"""Display-free, orthographic POSCAR-to-PNG rendering with Cairo."""
import argparse
import itertools
import math
import os
from pathlib import Path
import re
import sys
import tempfile
import xml.etree.ElementTree as ET


def rotations(text):
    result = []
    for token in text.split(','):
        match = re.fullmatch(r'\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+))\s*([xyzXYZ])\s*', token)
        if not match:
            raise argparse.ArgumentTypeError('rotation must look like 30x,-20y,10z (degrees)')
        angle = float(match[1])
        if not math.isfinite(angle):
            raise argparse.ArgumentTypeError('rotation must be finite')
        result.append((match[2].lower(), math.radians(angle)))
    return result


def image_size(text):
    try:
        w, h = map(int, text.lower().split('x'))
    except ValueError:
        raise argparse.ArgumentTypeError('size must be WIDTHxHEIGHT, e.g. 1200x900')
    if min(w, h) < 32 or max(w, h) > 8192 or w*h > 32000000:
        raise argparse.ArgumentTypeError('dimensions must be 32..8192, at most 32 million pixels')
    return w, h


def positive(text):
    value = float(text)
    if not math.isfinite(value) or value <= 0:
        raise argparse.ArgumentTypeError('value must be positive and finite')
    return value


def transform(point, turns):
    x, y, z = point
    for axis, angle in turns:
        c, s = math.cos(angle), math.sin(angle)
        if axis == 'x': y, z = c*y-s*z, s*y+c*z
        elif axis == 'y': x, z = c*x+s*z, -s*x+c*z
        else: x, y = c*x-s*y, s*x+c*y
    return x, y, z


def load_structure(path):
    from p4vasp.Structure import Structure
    structure = Structure(str(path))
    if not len(structure):
        raise ValueError('structure has no atoms')
    basis = [list(v) for v in structure.basis]
    scales = list(structure.scaling)
    if len(scales) == 1:
        scale = scales[0]
        if scale < 0:
            a, b, c = basis
            volume = abs(a[0]*(b[1]*c[2]-b[2]*c[1]) - a[1]*(b[0]*c[2]-b[2]*c[0]) + a[2]*(b[0]*c[1]-b[1]*c[0]))
            if volume == 0: raise ValueError('cell volume is zero')
            scale = (abs(scale)/volume)**(1/3)
        scales = [scale]*3
    if len(scales) != 3 or any(not math.isfinite(v) or v <= 0 for v in scales):
        raise ValueError('invalid POSCAR scale factors')
    basis = [[v[j]*scales[j] for j in range(3)] for v in basis]
    positions = []
    for pos in structure:
        if structure.isDirect():
            positions.append(tuple(sum(pos[i]*basis[i][j] for i in range(3)) for j in range(3)))
        else:
            positions.append(tuple(pos[j]*scales[j] for j in range(3)))
    if not all(math.isfinite(x) for v in basis + positions for x in v):
        raise ValueError('structure contains non-finite coordinates')
    elements = [str(structure.info.getRecordForAtom(i).element).strip() for i in range(len(structure))]
    return basis, positions, elements


def atom_styles():
    from p4vasp import p4vasp_home
    root = ET.parse(Path(p4vasp_home)/'data/atomtypes.xml').getroot()
    styles = {}
    for row in root.findall('.//r'):
        values = row.text.split()
        radius = float(values[2]) or float(values[3]) or .7
        styles[values[0]] = (radius, tuple(map(float, values[4:7])), float(values[3]))
    return styles


def bond_pairs(positions, radii, factor):
    """Distance-based bonds within the supplied atoms, without periodic images."""
    for i, p in enumerate(positions):
        for j in range(i+1, len(positions)):
            if radii[i] <= 0 or radii[j] <= 0:
                continue
            distance = sum((p[k]-positions[j][k])**2 for k in range(3))
            if 1e-12 < distance <= (factor*(radii[i]+radii[j]))**2:
                yield i, j


def camera_point(point, camera):
    """OpenGL M * scale * position; getRotMatElement returns row,column."""
    matrix = camera['matrix']
    return tuple(sum(matrix[i][j]*point[j]*camera['zoom'] for j in range(3))+matrix[i][3]
                 for i in range(3))


def perspective_factor(point, camera):
    return 10/(20-point[2]) if camera.get('perspective') else 1.0


def camera_visible(point, camera):
    return -30 < point[2] < 10 if camera.get('perspective') else -30 < point[2] < 30


def render(source, output, *, view='top', turns=(), size=(1000, 1000),
           radius_scale=.5, cell=True, transparent=True, force=True,
           model="spheres", brightness=1.0, bond_radius=.10, bond_factor=1.15, quality=2, material="matte", scene=None, camera=None):
    import cairo
    source = Path(source).resolve() if source is not None else None
    output = Path(output).absolute()
    if output.suffix.lower() != '.png': raise ValueError('output must have a .png extension')
    if source == output.resolve(): raise ValueError('output must not replace the input structure')
    if output.exists() and not force: raise ValueError('output exists; use --force to replace it')
    basis, positions, elements = load_structure(source) if scene is None else scene[:3]
    if not positions:
        raise ValueError("No visible atoms to export")
    project = (lambda p: camera_point(p, camera)) if camera else (lambda p: transform(p, turns))
    styles = atom_styles()
    presets = {'top': [], 'front': [('x', -math.pi/2)], 'side': [('x', -math.pi/2)]}
    turns = presets[view] + list(turns)
    atoms = []
    covalent = []
    for pos, element in zip(positions, elements):
        radius, color, cov = styles.get(element, (.7, (.6, .6, .6), 0))
        covalent.append(cov)
        radius *= radius_scale
        if model == "ball-stick": radius *= .45
        if model == "stick": radius = bond_radius
        if model == "space-filling": radius *= 2
        atoms.append((project(pos), radius*(camera["zoom"] if camera else 1), color))
    corners = {bits: project(tuple(sum(bits[i]*basis[i][j] for i in range(3)) for j in range(3)))
               for bits in itertools.product((0, 1), repeat=3)}
    cell_edges = []
    origins = scene[3] if scene is not None and len(scene) > 3 else [(0, 0, 0)]
    for origin in origins:
        points = {bits: project(tuple(origin[j]+sum(bits[i]*basis[i][j] for i in range(3)) for j in range(3)))
                  for bits in itertools.product((0, 1), repeat=3)}
        for bits, point in points.items():
            for axis in range(3):
                if bits[axis]: continue
                other = list(bits); other[axis] = 1
                cell_edges.append((point, points[tuple(other)]))
    bounds = [(p[0]-r, p[1]-r, p[0]+r, p[1]+r) for p, r, _ in atoms]
    if cell: bounds += [(p[0], p[1], p[0], p[1]) for p in corners.values()]
    xmin, ymin = min(b[0] for b in bounds), min(b[1] for b in bounds)
    xmax, ymax = max(b[2] for b in bounds), max(b[3] for b in bounds)
    width, height = size
    margin = .06*min(size)
    scale = min((width-2*margin)/max(xmax-xmin, 1e-9), (height-2*margin)/max(ymax-ymin, 1e-9))
    def screen(p):
        return width/2+(p[0]-(xmin+xmax)/2)*scale, height/2-(p[1]-(ymin+ymax)/2)*scale
    if camera:
        # Match VisNavDrawer's projection and retain the window's framing.
        scale = min(width/camera['width'], height/camera['height']) / .04
        def screen(p):
            factor = perspective_factor(p, camera)
            return width/2+p[0]*factor*scale, height/2-p[1]*factor*scale
    if width*height*quality*quality > 64000000:
        raise ValueError("quality and size exceed 64 million working pixels; reduce --quality or --size")
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width*quality, height*quality)
    ctx = cairo.Context(surface)
    ctx.scale(quality, quality)
    ctx.set_antialias(cairo.ANTIALIAS_BEST)
    if not transparent:
        ctx.set_source_rgb(1, 1, 1); ctx.paint()
    if cell:
        ctx.set_source_rgb(.18, .18, .18); ctx.set_line_width(max(1, min(size)/700))
        for a, b in cell_edges:
            if camera and (not camera_visible(a, camera) or not camera_visible(b, camera)):
                continue
            ctx.move_to(*screen(a)); ctx.line_to(*screen(b))
        ctx.stroke()
    materials = {
        'classic': (((0, 1.18), (.35, 1.05), (.72, .78), (1, .30)), .35, .40, (.4, 1.15, .45)),
        'matte': (((0, 1.02), (.35, .96), (.72, .82), (1, .55)), .45, .10, (.65, 1.0, .65)),
        'glossy': (((0, 1.10), (.35, 1.0), (.72, .70), (1, .28)), .20, .65, (.35, 1.18, .40)),
    }
    stops, highlight_size, highlight_alpha, bond_light = materials[material]

    def lit(color, factor):
        return tuple(min(1, max(0, v*factor*brightness)) for v in color)

    # Split bonds into short depth-sorted pieces to improve crossings with atoms.
    primitives = [(p[2], 'atom', (p, r, color)) for p, r, color in atoms]
    if model in ('ball-stick', 'stick'):
        for i, j in bond_pairs(positions, covalent, bond_factor):
            p, q = atoms[i][0], atoms[j][0]
            for part in range(16):
                a = tuple(p[k]+(q[k]-p[k])*part/16 for k in range(3))
                b = tuple(p[k]+(q[k]-p[k])*(part+1)/16 for k in range(3))
                color = atoms[i if part < 8 else j][2]
                primitives.append(((a[2]+b[2])/2, 'bond', (a, b, color)))
    for _, kind, data in sorted(primitives, key=lambda item: (item[0], item[1] == 'atom')):
        if camera and not camera_visible(data[0], camera):
            continue
        if kind == 'bond':
            a, b, color = data
            if camera and not camera_visible(b, camera): continue
            x, y = screen(a); u, v = screen(b)
            length = math.hypot(u-x, v-y)
            if length < 1e-8: continue
            r = bond_radius*scale
            if camera: r *= camera["zoom"]*perspective_factor(a, camera)
            nx, ny = -(v-y)/length*r, (u-x)/length*r
            gradient = cairo.LinearGradient(x-nx, y-ny, x+nx, y+ny)
            for offset, strength in zip((0, .35, 1), bond_light):
                gradient.add_color_stop_rgb(offset, *lit(color, strength))
            ctx.set_source(gradient); ctx.set_line_width(2*r)
            ctx.set_line_cap(cairo.LINE_CAP_ROUND)
            ctx.move_to(x, y); ctx.line_to(u, v); ctx.stroke()
            continue
        p, radius, color = data
        x, y = screen(p); radius *= scale
        if camera: radius *= perspective_factor(p, camera)
        gradient = cairo.RadialGradient(x-.28*radius, y-.32*radius, 0, x, y, radius)
        for offset, strength in stops:
            gradient.add_color_stop_rgb(offset, *lit(color, strength))
        ctx.arc(x, y, radius, 0, 2*math.pi); ctx.set_source(gradient); ctx.fill()
        highlight = cairo.RadialGradient(x-.3*radius, y-.35*radius, 0,
                                         x-.3*radius, y-.35*radius, highlight_size*radius)
        highlight.add_color_stop_rgba(0, 1, 1, 1, highlight_alpha)
        highlight.add_color_stop_rgba(1, 1, 1, 1, 0)
        ctx.arc(x, y, radius, 0, 2*math.pi); ctx.set_source(highlight); ctx.fill()
    if quality > 1:
        reduced = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        down = cairo.Context(reduced)
        down.scale(1/quality, 1/quality)
        down.set_source_surface(surface)
        down.get_source().set_filter(cairo.FILTER_BEST)
        down.get_source().set_extend(cairo.EXTEND_PAD)
        down.paint()
        surface = reduced
    # Render completely before publishing the output. Existing files are replaced unless explicitly protected.
    fd, tmp = tempfile.mkstemp(prefix='.p4v-render-', suffix='.png', dir=str(output.parent))
    os.close(fd)
    try:
        surface.write_to_png(tmp)
        if force: os.replace(tmp, output)
        else: os.link(tmp, output)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)


def main(argv=None):
    parser = argparse.ArgumentParser(description='Render POSCAR/CONTCAR to PNG without opening a GUI or requiring a display.')
    parser.add_argument('structure', help='POSCAR or CONTCAR file')
    parser.add_argument('-o', '--output', required=True, help='output PNG path')
    parser.add_argument('--view', choices=('top', 'front', 'side'), default='top', help='top: look from +z; front: +y; side: +y (rotate -90 degrees about x, z up)')
    parser.add_argument('--rotate', '--rotation', type=rotations, default=[], help='right-handed rotations in order, degrees, e.g. 30x,-20y,10z; use --rotate=-30x for negative first angles')
    parser.add_argument('--size', type=image_size, default=(1000, 1000), help='WIDTHxHEIGHT (default 1000x1000)')
    parser.add_argument('--radius-scale', type=positive, default=.5)
    parser.add_argument('--model', choices=('spheres', 'ball-stick', 'stick', 'space-filling'), default='spheres')
    parser.add_argument('--material', choices=('classic', 'matte', 'glossy'), default='matte', help='surface finish (default matte)')
    parser.add_argument('--brightness', type=positive, default=1.0)
    parser.add_argument('--bond-radius', type=positive, default=.10, help='bond radius in angstroms')
    parser.add_argument('--bond-factor', type=positive, default=1.15, help='covalent-radius sum multiplier')
    parser.add_argument('--quality', type=int, choices=(1, 2, 3, 4), default=2, help='supersampling factor (default 2)')
    parser.add_argument('--no-cell', action='store_true', help='hide cell and fit atoms only')
    background = parser.add_mutually_exclusive_group()
    background.add_argument('--transparent', dest='transparent', action='store_true', default=True,
                            help='transparent background (default)')
    background.add_argument('--white-background', dest='transparent', action='store_false',
                            help='opaque white background')
    overwrite = parser.add_mutually_exclusive_group()
    overwrite.add_argument('--force', dest='force', action='store_true', default=True,
                           help='replace an existing output PNG (default)')
    overwrite.add_argument('--no-clobber', dest='force', action='store_false',
                           help='fail if the output already exists')
    args = parser.parse_args(argv)
    try:
        render(args.structure, args.output, view=args.view, turns=args.rotate, size=args.size,
               radius_scale=args.radius_scale, cell=not args.no_cell,
               transparent=args.transparent, force=args.force, model=args.model,
               brightness=args.brightness, bond_radius=args.bond_radius,
               bond_factor=args.bond_factor, quality=args.quality, material=args.material)
    except ImportError as error:
        parser.exit(1, 'Rendering dependency missing (Python Cairo is required): %s\n' % error)
    except Exception as error:
        parser.exit(1, 'Could not render structure: %s\n' % error)
    print('Saved PNG: %s' % Path(args.output).absolute())
    return 0


if __name__ == '__main__':
    sys.exit(main())

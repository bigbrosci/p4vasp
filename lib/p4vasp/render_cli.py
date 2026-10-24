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
        styles[values[0]] = (radius, tuple(map(float, values[4:7])))
    return styles


def render(source, output, *, view='top', turns=(), size=(1000, 1000),
           radius_scale=.5, cell=True, transparent=False, force=False):
    import cairo
    source, output = Path(source).resolve(), Path(output).absolute()
    if output.suffix.lower() != '.png': raise ValueError('output must have a .png extension')
    if source == output.resolve(): raise ValueError('output must not replace the input structure')
    if output.exists() and not force: raise ValueError('output exists; use --force to replace it')
    basis, positions, elements = load_structure(source)
    styles = atom_styles()
    presets = {'top': [], 'front': [('x', -math.pi/2)], 'side': [('y', -math.pi/2)]}
    turns = presets[view] + list(turns)
    atoms = []
    for pos, element in zip(positions, elements):
        radius, color = styles.get(element, (.7, (.6, .6, .6)))
        atoms.append((transform(pos, turns), radius*radius_scale, color))
    corners = {bits: transform(tuple(sum(bits[i]*basis[i][j] for i in range(3)) for j in range(3)), turns)
               for bits in itertools.product((0, 1), repeat=3)}
    bounds = [(p[0]-r, p[1]-r, p[0]+r, p[1]+r) for p, r, _ in atoms]
    if cell: bounds += [(p[0], p[1], p[0], p[1]) for p in corners.values()]
    xmin, ymin = min(b[0] for b in bounds), min(b[1] for b in bounds)
    xmax, ymax = max(b[2] for b in bounds), max(b[3] for b in bounds)
    width, height = size
    margin = .06*min(size)
    scale = min((width-2*margin)/max(xmax-xmin, 1e-9), (height-2*margin)/max(ymax-ymin, 1e-9))
    def screen(p):
        return width/2+(p[0]-(xmin+xmax)/2)*scale, height/2-(p[1]-(ymin+ymax)/2)*scale
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    ctx = cairo.Context(surface)
    if not transparent:
        ctx.set_source_rgb(1, 1, 1); ctx.paint()
    if cell:
        ctx.set_source_rgb(.18, .18, .18); ctx.set_line_width(max(1, min(size)/700))
        for bits, p in corners.items():
            for axis in range(3):
                if bits[axis]: continue
                other = list(bits); other[axis] = 1
                ctx.move_to(*screen(p)); ctx.line_to(*screen(corners[tuple(other)]))
        ctx.stroke()
    # Painter's algorithm: nearer atom centers are drawn last.
    for p, radius, color in sorted(atoms, key=lambda a: a[0][2]):
        x, y = screen(p); radius *= scale
        gradient = cairo.RadialGradient(x-.3*radius, y-.35*radius, .04*radius, x, y, radius)
        gradient.add_color_stop_rgb(0, *[.65+.35*v for v in color])
        gradient.add_color_stop_rgb(.6, *color)
        gradient.add_color_stop_rgb(1, *[.4*v for v in color])
        ctx.arc(x, y, radius, 0, 2*math.pi); ctx.set_source(gradient); ctx.fill_preserve()
        ctx.set_source_rgb(*[.25*v for v in color]); ctx.set_line_width(.7); ctx.stroke()
    # Render completely before publishing the output. Existing files need --force.
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
    parser.add_argument('--view', choices=('top', 'front', 'side'), default='top', help='top: look from +z; front: +y; side: +x')
    parser.add_argument('--rotate', '--rotation', type=rotations, default=[], help='right-handed rotations in order, degrees, e.g. 30x,-20y,10z; use --rotate=-30x for negative first angles')
    parser.add_argument('--size', type=image_size, default=(1000, 1000), help='WIDTHxHEIGHT (default 1000x1000)')
    parser.add_argument('--radius-scale', type=positive, default=.5)
    parser.add_argument('--no-cell', action='store_true', help='hide cell and fit atoms only')
    parser.add_argument('--transparent', action='store_true')
    parser.add_argument('--force', action='store_true', help='replace an existing output PNG')
    args = parser.parse_args(argv)
    try:
        render(args.structure, args.output, view=args.view, turns=args.rotate, size=args.size,
               radius_scale=args.radius_scale, cell=not args.no_cell,
               transparent=args.transparent, force=args.force)
    except ImportError as error:
        parser.exit(1, 'Rendering dependency missing (Python Cairo is required): %s\n' % error)
    except Exception as error:
        parser.exit(1, 'Could not render structure: %s\n' % error)
    print('Saved PNG: %s' % Path(args.output).absolute())
    return 0


if __name__ == '__main__':
    sys.exit(main())

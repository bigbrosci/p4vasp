"""Export-only analytic sphere/capsule renderer; no GUI or graphics context.

Tiles bound scratch memory. Each pixel chooses the closest actual surface,
then receives linear-space studio lighting. NumPy is loaded only on export.
This is direct lighting, not path tracing or ambient occlusion.
"""
import math

import numpy as np


def _dot(a, b):
    return np.sum(a*b, axis=-1)


def intersect(origins, rays, a, b, radius, near, far):
    """Return first visible ray distance to a sphere or round-ended cylinder.

    Rays are unit length. near/far are distances along each ray, matching
    native view-space clipping planes. A clipped surface is not a solid cap.
    """
    a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    axis = b-a
    length = float(np.linalg.norm(axis))
    result = np.full(rays.shape[:-1], np.inf)
    if length > 1e-12:
        axis /= length
        along = _dot(rays, axis)
        relative = origins-a
        offset = _dot(relative, axis)
        d = rays-along[..., None]*axis
        o = relative-offset[..., None]*axis
        aa, bb = _dot(d, d), _dot(d, o)
        cc = _dot(o, o)-radius*radius
        disc = bb*bb-aa*cc
        root = np.sqrt(np.maximum(disc, 0))
        denominator = np.where(aa > 1e-14, aa, 1)
        for t in ((-bb-root)/denominator, (-bb+root)/denominator):
            z = offset+t*along
            valid = (aa > 1e-14) & (disc >= 0) & (z >= 0) & (z <= length) & (t >= near) & (t <= far)
            result = np.minimum(result, np.where(valid, t, np.inf))
    for end, center in enumerate((a, b) if length > 1e-12 else (a,)):
        relative = origins-center
        projection = _dot(relative, rays)
        # Perpendicular-distance form avoids subtracting two large squared depths.
        cross = np.cross(relative, rays)
        disc = radius*radius-_dot(cross, cross)
        root = np.sqrt(np.maximum(disc, 0))
        for t in (-projection-root, -projection+root):
            valid = (disc >= 0) & (t >= near) & (t <= far)
            if length > 1e-12:
                z = _dot(relative, axis)+t*_dot(rays, axis)
                valid &= (z <= 0) if end == 0 else (z >= 0)
            result = np.minimum(result, np.where(valid, t, np.inf))
    return result


def shade(normals, colors, view, material, brightness, visibility=1.):
    """Soft upper-left key, broad fill and controlled dielectric highlights."""
    base = np.where(colors <= .04045, colors/12.92, ((colors+.055)/1.055)**2.4)
    key = np.array([-.38, .52, .76]); key /= np.linalg.norm(key)
    fill = np.array([.65, .25, .72]); fill /= np.linalg.norm(fill)
    key_amount = np.maximum(_dot(normals, key), 0)[..., None]
    fill_amount = np.maximum(_dot(normals, fill), 0)[..., None]
    # Keep matte colours recognizable while avoiding a white sticker highlight.
    lit = base*(.25+.68*key_amount+.16*fill_amount)
    half = view+key
    half /= np.maximum(np.linalg.norm(half, axis=-1, keepdims=True), 1e-12)
    exponent, strength = {'matte': (36, .025), 'classic': (48, .12), 'glossy': (100, .32)}[material]
    spec = np.maximum(_dot(normals, half), 0)[..., None]**exponent
    lit += spec*strength*(.8+.2*base)
    lit *= brightness*(.70+.30*np.asarray(visibility)[..., None])
    # A smooth highlight shoulder instead of hard channel clipping.
    lit = np.where(lit <= .8, lit, .8+.2*(1-np.exp(-(lit-.8)/.2)))
    return np.clip(np.where(lit <= .0031308, lit*12.92,
                           1.055*np.maximum(lit, 0)**(1/2.4)-.055), 0, 1)


def draw(atoms, bonds, cell_edges, *, size, quality, scale, center,
         camera, bond_radius, material, brightness, transparent, cancelled=None):
    """Return a Cairo image surface, using exact sphere/capsule intersections."""
    import cairo
    if cancelled and cancelled(): raise ValueError("Rendering cancelled")
    width, height = size
    w, h = width*quality, height*quality
    pixel_scale = scale*quality
    perspective = bool(camera and camera.get('perspective'))
    clip_front, clip_back = ((10., -30.) if perspective else (30., -30.)) if camera else (math.inf, -math.inf)
    zoom = camera['zoom'] if camera else 1.
    origin_z = 20. if perspective else (30. if camera else max(p[2]+r for p, r, _ in atoms)+1)
    cx, cy = (0., 0.) if camera else center
    # a, b, radius, color at each end. Spheres have identical endpoints.
    objects = [(np.array(p), np.array(p), r, np.array(color), np.array(color)) for p, r, color in atoms]
    for i, j in bonds:
        objects.append((np.array(atoms[i][0]), np.array(atoms[j][0]), bond_radius*zoom,
                        np.array(atoms[i][2]), np.array(atoms[j][2])))
    # Cell edges also participate in the depth buffer, instead of always hiding behind atoms.
    for a, b in cell_edges:
        objects.append((np.array(a), np.array(b), max(.5, min(size)/1400)/scale,
                        np.full(3, .2), np.full(3, .2)))
    tile_size = 96
    bins = {}
    for obj in objects:
        a, b, radius, _, _ = obj
        # Twice the radius bounds the finite-support contact-darkening term.
        lower, upper = np.minimum(a,b)-2*radius, np.maximum(a,b)+2*radius
        if upper[2] < clip_back or lower[2] > clip_front: continue
        x0, y0, z0 = lower; x1, y1, z1 = upper
        if perspective:
            z0, z1 = max(z0, clip_back), min(z1, clip_front)
            corners = [(width/2+x*10/(20-z)*scale, height/2-y*10/(20-z)*scale)
                       for x in (x0,x1) for y in (y0,y1) for z in (z0,z1)]
        else:
            corners = [(width/2+(x-cx)*scale, height/2-(y-cy)*scale)
                       for x in (x0,x1) for y in (y0,y1)]
        px0 = max(0, int(math.floor(min(p[0] for p in corners)*quality))-1)
        px1 = min(w, int(math.ceil(max(p[0] for p in corners)*quality))+1)
        py0 = max(0, int(math.floor(min(p[1] for p in corners)*quality))-1)
        py1 = min(h, int(math.ceil(max(p[1] for p in corners)*quality))+1)
        if px0 >= px1 or py0 >= py1: continue
        for ty in range(py0//tile_size, (py1-1)//tile_size+1):
            for tx in range(px0//tile_size, (px1-1)//tile_size+1):
                bins.setdefault((tx,ty), []).append(obj)
    pixels = np.full((h,w), 0 if transparent else 0xffffffff, dtype=np.uint32)
    for (tx,ty), candidates in bins.items():
        if cancelled and cancelled(): raise ValueError('Rendering cancelled')
        x0, y0 = tx*tile_size, ty*tile_size
        x1, y1 = min(w,x0+tile_size), min(h,y0+tile_size)
        yy, xx = np.mgrid[y0:y1, x0:x1]
        x = (xx+.5-w/2)/pixel_scale+cx
        y = -(yy+.5-h/2)/pixel_scale+cy
        rays = np.zeros((*x.shape,3)); rays[...,2] = -1
        origins = np.zeros_like(rays); origins[...,2] = origin_z
        if perspective:
            rays[...,0], rays[...,1], rays[...,2] = x, y, -10
            rays /= np.linalg.norm(rays, axis=-1, keepdims=True)
            near, far = 10/-rays[...,2], 50/-rays[...,2]
        else:
            origins[...,0], origins[...,1] = x, y
            near, far = 0., origin_z-clip_back
        depth = np.full(x.shape, np.inf)
        normals = np.zeros_like(rays); colors = np.zeros_like(rays)
        for a,b,radius,ca,cb in candidates:
            t = intersect(origins, rays, a, b, radius, near, far)
            mask = t < depth
            if not mask.any(): continue
            hit = origins[mask]+t[mask,None]*rays[mask]
            axis = b-a
            length2 = float(_dot(axis,axis))
            if length2 > 1e-20:
                fraction = np.clip(_dot(hit-a,axis)/length2,0,1)
                closest = a+fraction[:,None]*axis
                colors[mask] = np.where((fraction < .5)[:,None],ca,cb)
            else:
                closest = a
                colors[mask] = ca
            normal = (hit-closest)/radius
            normal /= np.maximum(np.linalg.norm(normal,axis=-1,keepdims=True),1e-12)
            normals[mask] = normal
            depth[mask] = t[mask]
        visible = np.isfinite(depth)
        if not visible.any(): continue
        hits = origins[visible]+depth[visible,None]*rays[visible]
        normal = normals[visible]
        contact = np.zeros(len(hits))
        for a,b,radius,_,_ in candidates:
            axis = b-a
            length2 = float(_dot(axis,axis))
            if length2 > 1e-20:
                fraction = np.clip(_dot(hits-a,axis)/length2,0,1)
                closest = a+fraction[:,None]*axis
            else:
                closest = a
            delta = closest-hits
            distance = np.maximum(np.linalg.norm(delta,axis=-1),1e-12)
            ratio = np.minimum(radius/distance,1)
            facing = np.clip((_dot(normal,delta)/distance+ratio)/(1+ratio),0,1)
            # Local, finite-support approximation; not physical AO or cast shadows.
            proximity = np.clip(1-(distance-radius)/radius,0,1)**2
            contact += facing*ratio*ratio*proximity
        visibility = np.exp(-1.4*contact)
        rgb = np.rint(shade(normal, colors[visible], -rays[visible], material, brightness, visibility)*255).astype(np.uint32)
        pixels[y0:y1,x0:x1][visible] = 0xff000000 | (rgb[:,0]<<16) | (rgb[:,1]<<8) | rgb[:,2]
    if cancelled and cancelled(): raise ValueError('Rendering cancelled')
    # uint32 ARGB is native-endian, matching Cairo on both little/big endian machines.
    stride = cairo.ImageSurface.format_stride_for_width(cairo.FORMAT_ARGB32,w)
    surface = cairo.ImageSurface.create_for_data(pixels, cairo.FORMAT_ARGB32,w,h,stride)
    surface.mark_dirty()
    if quality > 1:
        result = cairo.ImageSurface(cairo.FORMAT_ARGB32,width,height)
        ctx = cairo.Context(result); ctx.scale(1/quality,1/quality)
        ctx.set_source_surface(surface)
        ctx.get_source().set_filter(cairo.FILTER_BEST)
        ctx.get_source().set_extend(cairo.EXTEND_PAD)
        ctx.paint()
        return result
    return surface

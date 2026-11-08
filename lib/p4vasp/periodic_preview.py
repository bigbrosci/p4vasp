"""Pure display geometry for lattice replicas; no structure modification."""
import itertools
import math

MAX_DISPLAY_ATOMS=12000


def cross(a,b):return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def lattice_point(cell,indices):return [sum(indices[i]*cell[i][j] for i in range(3)) for j in range(3)]


def geometry(positions,cell,repeats):
    if len(repeats)!=3 or any(type(n)!=int or not 1<=n<=5 for n in repeats):
        raise ValueError('Display repetitions must be integers from 1 to 5.')
    if len(positions)*math.prod(repeats)>MAX_DISPLAY_ATOMS:
        raise ValueError('Display limit: %d atoms. Reduce X/Y/Z repetitions.'%MAX_DISPLAY_ATOMS)
    reciprocal=[cross(cell[1],cell[2]),cross(cell[2],cell[0]),cross(cell[0],cell[1])]
    volume=dot(cell[0],reciprocal[0])
    if not math.isfinite(volume) or abs(volume)<1e-10:raise ValueError('Invalid preview cell.')
    wraps=[lattice_point(cell,[-math.floor(dot(p,r)/volume+1e-9) for r in reciprocal]) for p in positions]
    indices=[];offsets=[]
    for image in itertools.product(*(range(n) for n in repeats)):
        shift=lattice_point(cell,image)
        for i,wrap in enumerate(wraps):
            indices.append(i);offsets.append([wrap[j]+shift[j] for j in range(3)])
    points=[[positions[i][j]+offset[j] for j in range(3)] for i,offset in zip(indices,offsets)]
    # Integer lattice endpoints deduplicate shared edges exactly, including skew cells.
    edges=set()
    for image in itertools.product(*(range(n) for n in repeats)):
        for corner in itertools.product((0,1),repeat=3):
            start=tuple(image[j]+corner[j] for j in range(3))
            for axis in range(3):
                if corner[axis]:continue
                end=tuple(start[j]+(j==axis) for j in range(3));edges.add((start,end))
    cell_edges=[(lattice_point(cell,a),lattice_point(cell,b)) for a,b in sorted(edges)]
    return indices,offsets,points,cell_edges


def bonds(points,radii,factor=1.2):
    result=[];bins={};step=max(1.,2*factor*max(radii,default=1.))
    for i,p in enumerate(points):
        key=tuple(math.floor(v/step) for v in p)
        for offset in itertools.product((-1,0,1),repeat=3):
            near=tuple(key[j]+offset[j] for j in range(3))
            for k in bins.get(near,()):
                distance=sum((p[j]-points[k][j])**2 for j in range(3))
                if .04<distance<(factor*(radii[i]+radii[k]))**2:result.append((i,k))
        bins.setdefault(key,[]).append(i)
    return result

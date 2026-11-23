"""ASE slab generation in a short-lived scientific worker, never in GTK."""
from io import StringIO
import json
import math
from pathlib import Path
import sys
if __name__=='__main__': sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from p4vasp.ase_bulk import BulkTask, MAX_ATOMS, worker_command as bulk_command

from p4vasp.surface_geometry import PRESETS, integer, position_offset, parameters, build_surface


def reposition_result(result,placement):
    """Translate an existing generated slab without rebuilding or importing ASE."""
    import copy
    from p4vasp.Structure import Structure
    atoms=Structure();atoms.read(StringIO(result['poscar']))
    atoms.correctScaling();direct=atoms.isDirect();atoms.setCartesian()
    if not len(atoms) or any(abs(atoms.basis[i][j])>1e-8 for i,j in ((0,2),(1,2),(2,0),(2,1))):
        raise ValueError('Positioning requires a generated slab with its normal along z.')
    height=atoms.basis[2][2];low=min(p[2] for p in atoms);high=max(p[2] for p in atoms)
    shift=position_offset(low,high,height,placement)
    for point in atoms:point[2]+=shift
    new=copy.deepcopy(result);new['request']['placement']=placement
    new.update(placement=placement,vacuum_bottom=low+shift,vacuum_top=height-high-shift,
               vacuum_each_side=(height-high+low)/2 if placement=='center' else None)
    if direct:atoms.setDirect()
    stream=StringIO();atoms.write(stream)
    # Keep the existing writer's species/counts/flags, but avoid its rounded
    # Vector formatting moving z=0.1 during a Direct-coordinate round trip.
    lines=stream.getvalue().splitlines()
    for i,row in enumerate(atoms.basis):lines[2+i]=' '.join(format(v,'.17g') for v in row)
    start=len(lines)-len(atoms)
    for i,point in enumerate(atoms):
        flags=lines[start+i].split()[3:]
        lines[start+i]=' '.join([format(v,'.17g') for v in point]+flags)
    new['poscar']='\n'.join(lines)+'\n'
    return new


def worker_command():
    command=bulk_command()
    if len(command)==2 and command[1]=='--bulk': return [command[0],'--surface']
    return [command[0],str(Path(__file__).resolve()),'--worker']


class SurfaceTask(BulkTask):
    def __init__(self,request,callback,timeout=60,command_factory=None):
        super().__init__(request,callback,timeout,command_factory or worker_command,'Surface generation')


if __name__=='__main__':
    try: print(json.dumps({'ok':True,'result':build_surface(json.load(sys.stdin))}))
    except Exception as error:
        print(json.dumps({'ok':False,'error':str(error)}));sys.exit(1)

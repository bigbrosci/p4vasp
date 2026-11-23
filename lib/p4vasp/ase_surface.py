"""ASE slab generation in a short-lived scientific worker, never in GTK."""
from io import StringIO
import json
import math
from pathlib import Path
import sys
if __name__=='__main__': sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from p4vasp.ase_bulk import BulkTask, MAX_ATOMS, worker_command as bulk_command

PRESETS = {'fcc111': (1,1,1), 'fcc100': (1,0,0), 'fcc110': (1,1,0),
           'bcc110': (1,1,0), 'bcc100': (1,0,0), 'bcc111': (1,1,1), 'hcp0001': (0,0,1)}


def integer(value, name, low, high):
    if isinstance(value, bool): raise ValueError(name+' must be an integer.')
    try: number = int(str(value).strip())
    except (ValueError, TypeError): raise ValueError(name+' must be an integer.')
    if str(number) != str(value).strip() or not low <= number <= high:
        raise ValueError('%s must be an integer from %d to %d.' % (name,low,high))
    return number


def position_offset(low,high,height,placement):
    if placement not in ('center','bottom'):raise ValueError('Choose Center or Bottom.')
    if not all(math.isfinite(v) for v in (low,high,height)) or high<low or height<=0:
        raise ValueError('Invalid slab bounds or cell height.')
    gap=height-(high-low)
    if gap<=0 or (placement=='bottom' and gap<=.1):
        raise ValueError('Bottom requires more than 0.1 angstrom of total vacuum; increase vacuum.')
    return (gap/2 if placement=='center' else .1)-low


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


def parameters(request):
    source = request.get('source', 'preset')
    if source not in ('preset', 'poscar', 'file'): raise ValueError('Choose a bulk source.')
    placement=request.get('placement','center')
    if placement not in ('center','bottom'):raise ValueError('Choose Center or Bottom.')
    result = {'source': source,'placement':placement}
    for key, default, low, high in (('layers',4,1,100), ('fixed_layers',2,0,100)):
        result[key] = integer(request.get(key,default),key,low,high)
    for key, default in (('vacuum',10.),('layer_tolerance',.3)):
        if isinstance(request.get(key,default),bool):raise ValueError(key+' must be numeric, not boolean.')
        try: value = float(request.get(key,default))
        except (ValueError, TypeError): raise ValueError(key+' must be numeric.')
        if not math.isfinite(value) or not 0 < value <= (1000 if key=='vacuum' else 2):
            raise ValueError(key+' must be positive and finite (maximum %s).' % (1000 if key=='vacuum' else 2))
        result[key] = value
    repeat = request.get('repeat',(2,2))
    if not isinstance(repeat,(list,tuple)) or len(repeat)!=2: raise ValueError('Enter two in-plane repetitions.')
    result['repeat'] = [integer(v,'Repeat',1,100) for v in repeat]
    if source=='preset':
        preset=request.get('preset','fcc111')
        if preset not in PRESETS: raise ValueError('Choose a supported metal surface.')
        result.update(preset=preset,symbol=str(request.get('symbol','Cu')).strip())
        for key in (('a','c') if preset=='hcp0001' else ('a',)):
            if isinstance(request.get(key,''),bool):raise ValueError('Lattice '+key+' must be numeric, not boolean.')
            try: value=float(request.get(key,''))
            except (ValueError,TypeError): raise ValueError('Enter lattice '+key+' in angstrom.')
            if not math.isfinite(value) or not 0 < value <= 1000: raise ValueError('Lattice '+key+' must be positive and finite.')
            result[key]=value
        result['indices']=list(PRESETS[preset])
    else:
        indices=request.get('indices',(1,1,1))
        if not isinstance(indices,(list,tuple)) or len(indices)!=3: raise ValueError('Enter three Miller indices.')
        indices=[integer(v,'Miller index',-10,10) for v in indices]
        divisor=math.gcd(*indices)
        if not divisor: raise ValueError('Miller indices cannot all be zero.')
        result['indices']=[v//divisor for v in indices]
        key='poscar' if source=='poscar' else 'path'
        value=request.get(key,'')
        if not isinstance(value,str) or not value.strip(): raise ValueError('Select a bulk structure first.')
        if len(value)>10_000_000: raise ValueError('Bulk input is too large.')
        result[key]=value
    if math.prod(result['repeat'])*result['layers']>MAX_ATOMS: raise ValueError('Surface exceeds the 10000 atom limit.')
    return result


def build_surface(request):
    settings=parameters(request)
    import ase
    import numpy as np
    from ase import build
    from ase.constraints import FixAtoms
    from ase.data import atomic_numbers
    from ase.geometry import get_layers
    from ase.io import read, write
    nx,ny=settings['repeat'];layers=settings['layers']
    source=settings['source'];portable=dict(settings)
    if source=='preset':
        symbol=settings['symbol']
        if symbol not in atomic_numbers or symbol=='X': raise ValueError('Enter one valid element symbol.')
        kwargs={'a':settings['a']}
        if settings['preset']=='hcp0001': kwargs['c']=settings['c']
        slab=getattr(build,settings['preset'])(symbol,size=(nx,ny,layers),**kwargs)
        label=symbol+' '+settings['preset']
    else:
        if source=='file':
            path=Path(settings['path']).expanduser().resolve()
            if path.stat().st_size>50_000_000: raise ValueError('Bulk file exceeds 50 MB.')
            bulk=read(str(path),format='cif' if path.suffix.lower()=='.cif' else 'vasp',index=-1,
                      do_not_split_by_at_sign=True)
            label=path.name
        else:
            bulk=read(StringIO(settings['poscar']),format='vasp');label='Bulk result'
        if not len(bulk) or len(bulk)*layers*nx*ny>MAX_ATOMS: raise ValueError('Surface requires 1 to 10000 atoms.')
        if (bulk.cell.rank!=3 or not np.isfinite(bulk.cell.array).all() or not np.isfinite(bulk.positions).all()
                or not math.isfinite(bulk.get_volume()) or abs(bulk.get_volume())<1e-8): raise ValueError('Input must be a finite, nondegenerate 3D bulk cell.')
        if np.any(bulk.numbers<1) or np.any(bulk.numbers>118): raise ValueError('Dummy elements are not supported.')
        # Surface constraints are explicit: replace inherited bulk constraints.
        bulk.set_constraint()
        stream=StringIO();write(stream,bulk,format='vasp',direct=True,sort=False,vasp5=True)
        portable.pop('path',None);portable.update(source='poscar',poscar=stream.getvalue())
        slab=build.surface(bulk,settings['indices'],layers,periodic=False).repeat((nx,ny,1))
    if not len(slab) or len(slab)>MAX_ATOMS: raise ValueError('Surface exceeds the 10000 atom limit.')
    slab.set_constraint();slab.center(vacuum=settings['vacuum'],axis=2)
    if (not np.isfinite(slab.positions).all() or not np.isfinite(slab.cell.array).all()
            or not math.isfinite(slab.get_volume()) or slab.get_volume()<1e-8):
        raise ValueError('Generated surface cell or coordinates are invalid.')
    shift=position_offset(float(slab.positions[:,2].min()),float(slab.positions[:,2].max()),
                          float(slab.cell[2,2]),settings['placement'])
    slab.positions[:,2]+=shift
    tags,levels=get_layers(slab,(0,0,1),tolerance=settings['layer_tolerance'])
    fixed=settings['fixed_layers']
    if fixed>=len(levels): raise ValueError('Fixed bottom layers must leave at least one free geometric layer.')
    slab.set_tags(tags+1)
    if fixed: slab.set_constraint(FixAtoms(mask=tags<fixed))
    # Group species explicitly so JSON indices and VASP constraints stay aligned.
    slab=slab[sorted(range(len(slab)),key=lambda i:slab[i].symbol)]
    layer_numbers=slab.get_tags().tolist()
    stream=StringIO();write(stream,slab,format='vasp',direct=True,sort=False,vasp5=True)
    return {'poscar':stream.getvalue(),'atoms':len(slab),'formula':slab.get_chemical_formula(),
            'cell':slab.cell.array.tolist(),'ase_version':ase.__version__,'source_label':label,
            'request':portable,'geometric_layers':len(levels),'layer_numbers':layer_numbers,
            'fixed_atoms':sum(v<=fixed for v in layer_numbers),
            'placement':settings['placement'],'vacuum_bottom':float(slab.positions[:,2].min()),
            'vacuum_top':float(slab.cell[2,2]-slab.positions[:,2].max()),
            'vacuum_each_side':settings['vacuum'] if settings['placement']=='center' else None,
            'layer_convention':'bottom-up geometric layers along the surface normal; source constraints replaced'}


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

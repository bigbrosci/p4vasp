"""VASP normal modes, signed displacement export and optional ASE thermochemistry.

ASE/NumPy imports live inside worker functions. The GTK process uses JSON and
the already isolated optional/bundled scientific interpreter.
"""
import json
import math
from pathlib import Path
import re
import sys

NUMBER = r'[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[EeDd][-+]?\d+)?'
MODE = re.compile(r'^\s*(\d+)\s+f\s*(/\s*i)?\s*=.*?('+NUMBER+r')\s+cm-1')


def number(text):
    value = float(text.replace('D','E').replace('d','e'))
    if not math.isfinite(value):raise ValueError('Non-finite vibration data.')
    return value


def read_outcar(path):
    import numpy as np
    from ase import Atoms
    from ase.data import atomic_numbers
    from ase.data import covalent_radii
    from ase.data.colors import jmol_colors
    from ase.io import read, write
    from io import StringIO
    path=Path(path).resolve()
    counts=[]; symbols=[]; potential_symbols=[]; masses=[]; cell=None; groups=[]; group=None
    with path.open(errors='replace') as source:
        for line in source:
            if 'ions per type' in line:
                counts=[int(n) for n in line.split('=')[-1].split()]
                if not counts or min(counts)<0 or not 0<sum(counts)<=10000:
                    raise ValueError('Invalid OUTCAR atom counts (maximum 10000 atoms).')
            match=re.search(r'VRHFIN\s*=\s*([A-Z][a-z]?)\s*:',line)
            if match:symbols.append(match[1])
            match=re.match(r'^\s*(?:POTCAR:|TITEL\s*=)\s+\S+\s+([A-Z][a-z]?)(?:_[^\s]+)?(?:\s|$)',line)
            if match:potential_symbols.append(match[1])
            match=re.search(r'POMASS\s*=\s*('+NUMBER+r'(?:\s+'+NUMBER+r')*)',line)
            if match:masses.extend(number(value) for value in match[1].split())
            elif re.search(r'POMASS\s*=',line):raise ValueError('Invalid OUTCAR POMASS.')
            if 'direct lattice vectors' in line.lower():
                cell=[[number(v) for v in next(source,'').split()[:3]] for _ in range(3)]
                if any(len(row)!=3 for row in cell):raise ValueError('Incomplete OUTCAR lattice.')
            lower=line.lower()
            if 'eigenvectors after division by sqrt(mass)' in lower:
                group={'physical':True,'modes':[]};groups.append(group)
            elif 'eigenvectors and eigenvalues of the dynamical matrix' in lower:
                group={'physical':False,'modes':[]};groups.append(group)
            match=MODE.match(line)
            if not match:
                if re.match(r'^\s*\d+\s+f\s*(?:/\s*i)?\s*=',line):
                    raise ValueError('Malformed or non-finite frequency header.')
                continue
            if group is None:raise ValueError('Missing OUTCAR normal-mode section header.')
            if not counts:raise ValueError('Missing OUTCAR ions per type.')
            index=int(match[1])
            if index==1 and group['modes']:
                group={'physical':group['physical'],'modes':[]};groups.append(group)
            rows=[]
            for _ in range(6):
                header=next(source,'')
                if 'dx' in header and 'dy' in header and 'dz' in header:break
            else:raise ValueError('Missing mode X Y Z dx dy dz columns.')
            for _ in range(sum(counts)):
                values=next(source,'').split()
                if len(values)!=6:raise ValueError('Incomplete mode displacement table.')
                rows.append([number(v) for v in values])
            imaginary=bool(match.group(2)) or number(match.group(3))<0
            frequency=abs(number(match.group(3)))
            group['modes'].append({'index':index,'cm1':frequency,'imaginary':imaginary,
                                   'positions':[r[:3] for r in rows], 'vectors':[r[3:] for r in rows]})
    if not groups or not groups[-1]['modes']:
        raise ValueError('No complete normal modes found. Use a frequency OUTCAR (IBRION=5/6); NWRITE=3 prints physical displacement vectors.')
    group=groups[-1]; modes=group['modes']; n=sum(counts)
    if [m['index'] for m in modes]!=list(range(1,len(modes)+1)) or len(modes)>3*n:
        raise ValueError('Incomplete or inconsistent mode numbering.')
    if len(symbols)<len(counts):symbols=potential_symbols
    if cell is None or len(symbols)<len(counts):raise ValueError('OUTCAR lattice or species (VRHFIN/POTCAR/TITEL) are missing.')
    species=[s for s,count in zip(symbols,counts) for _ in range(count)]
    if any(s not in atomic_numbers for s in species):raise ValueError('Unknown OUTCAR element.')
    positions=np.array(modes[0]['positions'])
    atoms=Atoms(species,positions=positions,cell=cell,pbc=True)
    volume=abs(float(np.linalg.det(atoms.cell)))
    if not math.isfinite(volume) or volume<1e-10:raise ValueError('Degenerate OUTCAR cell.')
    mass_source='OUTCAR POMASS' if len(masses)>=len(counts) else 'ASE standard masses'
    if len(masses)>=len(counts):
        if any(m<=0 for m in masses[:len(counts)]):raise ValueError('Invalid OUTCAR POMASS.')
        atoms.set_masses([m for m,count in zip(masses,counts) for _ in range(count)])
    elif not group['physical']:
        raise ValueError('Mass-weighted modes require OUTCAR POMASS or a physical-vector section (NWRITE=3).')
    warnings=[]
    if mass_source=='ASE standard masses':warnings.append('POMASS unavailable; ASE standard masses are used for thermochemistry.')
    constraints_source=None
    for filename in ('POSCAR','CONTCAR'):
        candidate=path.parent/filename
        if not candidate.is_file():continue
        try:
            reference=read(str(candidate),format='vasp')
            if (reference.get_chemical_symbols()==species and np.allclose(reference.cell,atoms.cell,atol=1e-5,rtol=0)
                    and np.allclose(reference.positions,positions,atol=1e-4,rtol=0)):
                atoms.set_constraint(reference.constraints);constraints_source=filename;break
        except Exception:pass
    if constraints_source is None:
        warnings.append('Selective-dynamics flags unavailable: no matching POSCAR/CONTCAR. Export uses unconstrained atoms.')
    elif len(modes) not in (3*n,atoms.get_number_of_degrees_of_freedom()):
        raise ValueError('Mode count does not match the full or constrained degrees of freedom.')
    for mode in modes:
        if not np.allclose(mode.pop('positions'),positions,atol=1e-5,rtol=0):
            raise ValueError('Mode tables do not share the same equilibrium coordinates.')
        vector=np.array(mode['vectors'])
        if not group['physical']:vector=vector/np.sqrt(atoms.get_masses())[:,None]
        mode['vectors']=vector.tolist()
        mode['max_displacement']=float(np.linalg.norm(vector,axis=1).max())
    if len(modes)<3*n:warnings.append('A reduced set of modes was printed; verify the active/fixed degrees of freedom before thermochemistry.')
    stream=StringIO();write(stream,atoms,format='vasp',direct=False,sort=False,vasp5=True)
    return {'path':str(path),'symbols':species,'positions':positions.tolist(),'cell':atoms.cell.array.tolist(),
            'masses':atoms.get_masses().tolist(),'modes':modes,'poscar':stream.getvalue(),
            'mass_source':mass_source,
            'radii':[float(covalent_radii[z]) for z in atoms.numbers],
            'colors':[jmol_colors[z].tolist() for z in atoms.numbers],
            'vector_convention':'physical OUTCAR vectors' if group['physical'] else 'OUTCAR eigenvectors / sqrt(POMASS)',
            'constraints_source':constraints_source,'warnings':warnings}


def displaced_structure(data, mode_index, scale):
    """Pure frontend operation. Never normalize vectors or accumulate offsets."""
    from io import StringIO
    from p4vasp.Structure import Structure
    scale=float(scale)
    if not math.isfinite(scale) or not -1<=scale<=1:raise ValueError('Scale must be between -1 and 1.')
    if type(mode_index)!=int or not 0<=mode_index<len(data['modes']):raise ValueError('Choose a valid mode.')
    mode=data['modes'][mode_index]
    structure=Structure();structure.read(StringIO(data['poscar']));structure.setCartesian()
    if len(structure)!=len(mode['vectors']):raise ValueError('Mode/structure atom count mismatch.')
    for i,(position,vector) in enumerate(zip(data['positions'],mode['vectors'])):
        structure[i]=[position[j]+scale*vector[j] for j in range(3)]
    structure.comment='Mode %d, %s%.6f cm^-1, scale=%+.1f (dimensionless)'%(mode['index'],'i ' if mode['imaginary'] else '',mode['cm1'],scale)
    return structure


def thermochemistry(request):
    import ase
    import numpy as np
    from ase import Atoms, units
    from ase.thermochemistry import HarmonicThermo, IdealGasThermo
    data=request['data']; modes=data['modes']
    selected=request['selected']
    if len(selected)!=len(set(selected)) or any(type(i)!=int or not 0<=i<len(modes) for i in selected):
        raise ValueError('Invalid thermochemistry mode selection.')
    tolerance=float(request.get('imaginary_tolerance',0))
    if not math.isfinite(tolerance) or tolerance<0:raise ValueError('Imaginary tolerance must be nonnegative and finite.')
    imaginary=sum(m['imaginary'] and m['cm1']>tolerance for m in modes)
    state=request.get('state','minimum')
    if state not in ('minimum','ts'):raise ValueError('Choose minimum or transition state.')
    if (state=='minimum' and imaginary) or (state=='ts' and imaginary!=1):
        raise ValueError('A minimum requires no imaginary modes; a first-order transition state requires exactly one (above the explicit imaginary tolerance).')
    if any(modes[i]['imaginary'] or modes[i]['cm1']<=0 for i in selected):
        raise ValueError('Only positive real frequencies may enter thermochemistry.')
    if len(selected)!=len(modes) and not request.get('confirm_exclusions'):
        raise ValueError('Confirm the excluded modes before calculation.')
    temperature=float(request['temperature'])
    pressure=float(request.get('pressure',101325)) if request['model']=='gas' else 101325.
    floor=float(request.get('floor',0));energy=request.get('energy')
    potential=0. if energy in (None,'') else float(energy)
    if not all(math.isfinite(v) for v in (temperature,pressure,floor,potential)) or temperature<=0 or pressure<=0 or floor<0:
        raise ValueError('Temperature/pressure must be positive and finite; the frequency floor must be nonnegative.')
    frequencies=[max(float(modes[i]['cm1']),floor) for i in selected]
    energies=[f*units.invcm for f in frequencies]
    model=request['model']
    if model=='harmonic':
        if not energies:raise ValueError('Select at least one real vibrational mode.')
        thermo=HarmonicThermo(energies,potentialenergy=potential)
        internal=thermo.get_internal_energy(temperature,verbose=False)
        entropy=thermo.get_entropy(temperature,verbose=False)
        free=thermo.get_helmholtz_energy(temperature,verbose=False)
        kind='F';enthalpy=None
    elif model=='gas':
        atoms=Atoms(data['symbols'],positions=data['positions'],masses=data['masses'])
        geometry=request['geometry'];spin=float(request['spin']);symmetry=int(request['symmetry'])
        if not math.isfinite(spin) or spin<0 or abs(2*spin-round(2*spin))>1e-8 or symmetry<1 or str(symmetry)!=str(request['symmetry']).strip():
            raise ValueError('Spin must be a nonnegative integer/half integer; symmetry number a positive integer.')
        inertias=atoms.get_moments_of_inertia()
        linear=len(atoms)>1 and inertias[0]/max(inertias[-1],1e-20)<1e-6
        actual='monatomic' if len(atoms)==1 else ('linear' if linear else 'nonlinear')
        if geometry!=actual:raise ValueError('Geometry choice does not match the imported molecule (%s).'%actual)
        expected={'monatomic':0,'linear':3*len(atoms)-5,'nonlinear':3*len(atoms)-6}[geometry]-(state=='ts')
        if len(selected)!=expected:raise ValueError('Select exactly %d molecular vibrational modes; exclude translations/rotations explicitly.'%expected)
        thermo=IdealGasThermo(energies,geometry,atoms=atoms,symmetrynumber=symmetry,spin=spin,
                             potentialenergy=potential,vib_selection='all')
        internal=thermo.get_internal_energy(temperature,verbose=False)
        enthalpy=thermo.get_enthalpy(temperature,verbose=False)
        entropy=thermo.get_entropy(temperature,pressure,verbose=False)
        free=thermo.get_gibbs_energy(temperature,pressure,verbose=False);kind='G'
    else:raise ValueError('Choose harmonic or ideal gas thermochemistry.')
    if not all(math.isfinite(v) for v in (internal,entropy,free,thermo.get_ZPE_correction())):
        raise ValueError('Thermochemistry produced non-finite values; check frequencies and settings.')
    return {'ase_version':ase.__version__,'kind':kind,'temperature_K':temperature,'pressure_Pa':pressure if model=='gas' else None,
            'ZPE_eV':float(thermo.get_ZPE_correction()),'U_eV':float(internal),
            'H_eV':None if enthalpy is None else float(enthalpy),'S_eV_per_K':float(entropy),
            'TS_eV':float(temperature*entropy),'free_energy_eV':float(free),
            'correction_eV':float(free-potential),'electronic_energy_eV':None if energy in (None,'') else potential,
            'selected_modes':[modes[i]['index'] for i in selected],
            'excluded_modes':[m['index'] for i,m in enumerate(modes) if i not in selected],
            'effective_cm1':frequencies,'request_settings':{k:v for k,v in request.items() if k!='data'}}


def run_request(request):
    try:
        if request['action']=='read':return read_outcar(request['path'])
        if request['action']=='thermo':return thermochemistry(request)
        raise ValueError('Unknown vibration operation.')
    except ImportError as error:
        raise RuntimeError('ASE vibration environment is unavailable. Run bash install/install-ase.sh in the p4vasp checkout.') from error


def worker_command():
    from p4vasp.ase_bulk import worker_command as ase_command
    command=ase_command()
    return [command[0],'--vibrations'] if command[-1]=='--bulk' else [command[0],str(Path(__file__).resolve()),'--worker']


def task(request, callback):
    from p4vasp.ase_bulk import BulkTask
    return BulkTask(request,callback,timeout=90,command_factory=worker_command,label='Vibration analysis')


def load(path):
    from p4vasp.model_worker import launch_options
    import subprocess
    command=worker_command()
    process=subprocess.run(command,input=json.dumps({'action':'read','path':str(Path(path).resolve())}),
                           capture_output=True,text=True,encoding='utf-8',timeout=90,**launch_options(command))
    try:response=json.loads(process.stdout)
    except ValueError:raise RuntimeError('Cannot start ASE vibration worker. Run bash install/install-ase.sh. '+process.stderr[-300:])
    if process.returncode or not response.get('ok'):raise ValueError(response.get('error','Vibration import failed.'))
    return response['result']


if __name__=='__main__':
    try:print(json.dumps({'ok':True,'result':run_request(json.load(sys.stdin))}))
    except Exception as error:
        print(json.dumps({'ok':False,'error':str(error)}));sys.exit(1)

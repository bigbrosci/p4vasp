"""Optional isolated RDKit worker for reproducible initial molecular geometry."""
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import threading
import p4vasp

SEED = 20261031
CONFORMERS = 8


def build_geometry(smiles):
    if not isinstance(smiles, str) or not smiles.strip() or len(smiles)>2048:
        raise ValueError('Enter a SMILES string (maximum 2048 characters).')
    try:
        import rdkit
        from rdkit import Chem
        from rdkit.Chem import AllChem
    except ImportError as error:
        raise RuntimeError('RDKit is unavailable. Run bash install/install-rdkit.sh in the p4vasp checkout, or set P4VASP_SMILES_PYTHON.') from error
    mol=Chem.MolFromSmiles(smiles.strip())
    if mol is None:raise ValueError('Invalid SMILES. Check atom symbols, brackets and ring closures.')
    if len(Chem.GetMolFrags(mol))!=1:
        raise ValueError('Multiple fragments / salts: use the local XYZ library to retain their relative geometry.')
    supported={1,5,6,7,8,9,14,15,16,17,34,35,53}
    if any(atom.GetAtomicNum() not in supported for atom in mol.GetAtoms()):
        raise ValueError('Metal or unsupported element: import a prepared XYZ geometry instead.')
    if mol.GetNumHeavyAtoms()>100:raise ValueError('This initial builder supports at most 100 heavy atoms; use XYZ for larger molecules.')
    canonical=Chem.MolToSmiles(mol,isomericSmiles=True)
    ambiguous=any(str(item.specified)=='Unspecified' for item in Chem.FindPotentialStereo(mol))
    charge=Chem.GetFormalCharge(mol)
    radicals=sum(atom.GetNumRadicalElectrons() for atom in mol.GetAtoms())
    multiplicity=None  # SMILES does not uniquely specify the spin state.
    mol=Chem.AddHs(mol)
    if mol.GetNumAtoms()>300:raise ValueError('This initial builder supports at most 300 atoms including H; use XYZ.')
    if AllChem.MMFFHasAllMoleculeParams(mol):forcefield='MMFF94s'
    elif AllChem.UFFHasAllMoleculeParams(mol):forcefield='UFF'
    else:raise ValueError('No complete MMFF/UFF parameters for this molecule. Use a prepared XYZ geometry.')
    params=AllChem.ETKDGv3();params.randomSeed=SEED;params.numThreads=1;params.pruneRmsThresh=.25;params.enforceChirality=True
    ids=list(AllChem.EmbedMultipleConfs(mol,numConfs=CONFORMERS,params=params))
    if not ids:raise ValueError('Could not generate a 3D conformer. Check SMILES or import XYZ.')
    if forcefield=='MMFF94s':
        results=AllChem.MMFFOptimizeMoleculeConfs(mol,numThreads=1,maxIters=1000,mmffVariant='MMFF94s')
    else:results=AllChem.UFFOptimizeMoleculeConfs(mol,numThreads=1,maxIters=1000)
    candidates=[(float(energy),conf_id) for conf_id,(status,energy) in zip(ids,results) if status==0 and math.isfinite(energy)]
    if not candidates:raise ValueError('Force-field optimization did not converge. Use a prepared XYZ geometry.')
    energy,conf_id=min(candidates)
    conformer=mol.GetConformer(conf_id)
    positions=[[float(value) for value in conformer.GetAtomPosition(i)] for i in range(mol.GetNumAtoms())]
    if not all(math.isfinite(value) for point in positions for value in point):raise ValueError('Generated non-finite coordinates.')
    warnings=[]
    if ambiguous:warnings.append('Unspecified stereochemistry: this is one possible geometry; verify it in preview.')
    if radicals:warnings.append('Radical spin is not inferred: confirm multiplicity before exporting.')
    return {'name':'SMILES '+(canonical if len(canonical)<=40 else canonical[:37]+'...'),
            'smiles':canonical,'symbols':[atom.GetSymbol() for atom in mol.GetAtoms()],
            'positions':positions,'charge':charge,'multiplicity':multiplicity,
            'forcefield':forcefield,'energy':energy,'converged':True,'conformers':len(ids),
            'converged_conformers':len(candidates),'seed':SEED,'rdkit_version':rdkit.__version__,
            'warning':' '.join(warnings)}


def molecule_from_result(result):
    from p4vasp.gas_phase_inputs import Molecule
    from p4vasp.element_data import SYMBOLS
    if not result.get('converged'):raise ValueError('The geometry was not optimized successfully.')
    symbols=tuple(result['symbols']);positions=tuple(tuple(point) for point in result['positions'])
    if not symbols or len(symbols)!=len(positions) or any(symbol not in SYMBOLS for symbol in symbols):
        raise ValueError('Invalid generated atom data.')
    if any(len(point)!=3 or not all(math.isfinite(value) for value in point) for point in positions):
        raise ValueError('Invalid generated coordinates.')
    provenance='SMILES=%s; ETKDGv3 seed=%d; RDKit=%s; %s converged; E=%.8g kcal/mol; initial geometry only'%(
        result['smiles'],result['seed'],result['rdkit_version'],result['forcefield'],result['energy'])
    if result.get('warning'):provenance+='; '+result['warning']
    return Molecule(None,result['name'],symbols,positions,result['charge'],result['multiplicity'],provenance)


def worker_command():
    configured=os.environ.get('P4VASP_SMILES_PYTHON')
    if configured:return [configured,'-m','p4vasp.smiles_builder']
    from p4vasp.model_worker import bundled_worker
    bundled=bundled_worker()
    if bundled is not None:return [str(bundled),'--smiles']
    root=Path(p4vasp.p4vasp_home)
    for relative in ('.venv-smiles/bin/python','.venv-smiles/Scripts/python.exe'):
        python=root/relative
        if python.is_file():return [str(python),'-m','p4vasp.smiles_builder']
    if getattr(sys,'frozen',False):
        raise RuntimeError('Set P4VASP_SMILES_PYTHON to a Python interpreter with RDKit installed.')
    return [sys.executable,'-m','p4vasp.smiles_builder']


class SmilesTask:
    """One bounded worker process; GUI callbacks are marshalled by the caller."""
    def __init__(self,smiles,callback,timeout=60):
        self.smiles=smiles;self.callback=callback;self.timeout=timeout
        self.cancelled=threading.Event();self.process=None;self.lock=threading.Lock()
        self.thread=threading.Thread(target=self.run,daemon=True)

    def start(self):self.thread.start()

    def cancel(self):
        self.cancelled.set()
        with self.lock:
            if self.process is not None and self.process.poll() is None:
                try:self.process.terminate()
                except ProcessLookupError:pass

    def run(self):
        result=None;error=None
        try:
            if self.cancelled.is_set():raise RuntimeError('SMILES generation cancelled.')
            env=os.environ.copy()
            env['PYTHONPATH']=str(Path(__file__).resolve().parents[1])+os.pathsep+env.get('PYTHONPATH','')
            from p4vasp.model_worker import launch_options
            command=worker_command()
            options=launch_options(command)
            if not getattr(sys,'frozen',False):options['env'].update(env)
            options['env']['OMP_NUM_THREADS']='1';options['env']['OPENBLAS_NUM_THREADS']='1'
            with self.lock:
                if self.cancelled.is_set():raise RuntimeError('SMILES generation cancelled.')
                self.process=subprocess.Popen(command,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                                              text=True,encoding='utf-8',**options)
            try:stdout,stderr=self.process.communicate(json.dumps({'smiles':self.smiles}),timeout=self.timeout)
            except subprocess.TimeoutExpired:
                self.process.kill();self.process.communicate()
                raise RuntimeError('SMILES generation timed out; try a smaller molecule or use XYZ.')
            if self.cancelled.is_set():raise RuntimeError('SMILES generation cancelled.')
            try:response=json.loads(stdout)
            except ValueError:raise RuntimeError('SMILES worker failed: '+stderr[-1000:])
            if self.process.returncode or 'error' in response:raise RuntimeError(response.get('error','SMILES worker failed.'))
            molecule_from_result(response)  # Validate before passing to the GUI.
            result=response
        except Exception as exc:error=str(exc)
        self.callback(result,error)


def main():
    try:
        request=json.load(sys.stdin)
        json.dump(build_geometry(request.get('smiles')),sys.stdout)
        return 0
    except Exception as error:
        json.dump({'error':str(error)},sys.stdout)
        return 2

if __name__=='__main__':sys.exit(main())

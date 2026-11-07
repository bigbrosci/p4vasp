"""ASE structure import in the optional scientific Python, never in GTK."""
from io import StringIO
import json
import math
from pathlib import Path
import subprocess
import sys

FORMATS = {'.xyz': 'extxyz', '.extxyz': 'extxyz', '.cif': 'cif',
           '.pdb': 'proteindatabank', '.mol': 'mol', '.sdf': 'sdf',
           '.xsf': 'xsf', '.traj': 'traj'}


def read_structure(request):
    try:
        import ase
        import numpy as np
        from ase.io import read, write
    except ImportError as error:
        raise RuntimeError('ASE is unavailable. Run bash install/install-ase.sh in the p4vasp checkout.') from error
    path = Path(request['path']).resolve()
    format = FORMATS.get(path.suffix.lower())
    if format is None:
        raise ValueError('Unsupported ASE import extension: '+path.suffix)
    atoms = read(str(path), format=format, index=-1, do_not_split_by_at_sign=True)
    if not len(atoms) or len(atoms) > 100000:
        raise ValueError('Import requires 1 to 100000 atoms.')
    if not np.isfinite(atoms.positions).all() or not np.isfinite(atoms.cell.array).all():
        raise ValueError('Coordinates and cell must be finite.')
    if any(number < 1 or number > 118 for number in atoms.numbers):
        raise ValueError('Unknown or dummy elements cannot be imported.')
    original_pbc = atoms.pbc.tolist()
    boxed = bool(atoms.cell.rank == 0)
    if boxed:
        # Cartesian axis spans, with exactly 10 Angstrom on either side.
        lengths = np.ptp(atoms.positions, axis=0) + 20.0
        atoms.set_cell(lengths)
        atoms.positions += 10.0 - atoms.positions.min(axis=0)
    elif atoms.cell.rank != 3:
        raise ValueError('Partial cells are not expanded automatically; provide a full 3D cell or no cell.')
    if not math.isfinite(atoms.get_volume()) or atoms.get_volume() <= 1e-10:
        raise ValueError('The imported cell is degenerate.')
    stream = StringIO()
    # Do not sort atoms: selections must retain the file's atom order.
    write(stream, atoms, format='vasp', direct=False, sort=False, vasp5=True)
    return {'poscar': stream.getvalue(), 'atoms': len(atoms), 'boxed': boxed,
            'cell': atoms.cell.array.tolist(), 'source_pbc': original_pbc,
            'ase_version': ase.__version__, 'frame': 'last'}


def load_structure(path, timeout=60):
    from p4vasp.ase_bulk import worker_command
    from p4vasp.model_worker import launch_options
    command = worker_command()
    if command[-1] == '--bulk':
        command[-1] = '--read-structure'
    else:
        command = [command[0], str(Path(__file__).resolve()), '--worker']
    try:
        process = subprocess.run(command, input=json.dumps({'path': str(Path(path).resolve())}),
                                 capture_output=True, text=True, encoding='utf-8',
                                 timeout=timeout, **launch_options(command))
    except subprocess.TimeoutExpired as error:
        raise RuntimeError('ASE structure import timed out after 60 seconds.') from error
    try:
        response = json.loads(process.stdout)
    except ValueError as error:
        raise RuntimeError('ASE import worker could not start. Run bash install/install-ase.sh '
                           'or check P4VASP_ASE_PYTHON. '+process.stderr[-400:]) from error
    if process.returncode or not response.get('ok'):
        raise RuntimeError(response.get('error', 'ASE structure import failed.'))
    return response['result']


if __name__ == '__main__':
    try:
        print(json.dumps({'ok': True, 'result': read_structure(json.load(sys.stdin))}))
    except Exception as error:
        print(json.dumps({'ok': False, 'error': str(error)}))
        sys.exit(1)

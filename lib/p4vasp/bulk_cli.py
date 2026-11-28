"""Generate a bulk POSCAR from explicit ASE crystal and lattice parameters."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

from p4vasp.ase_bulk import worker_command
from p4vasp.bulk_geometry import CRYSTALS, parameters, write_bulk_poscar
from p4vasp.model_worker import launch_options


def main(args=None):
    parser = argparse.ArgumentParser(prog='p4v bulk', description=__doc__)
    parser.add_argument('name', metavar='FORMULA', help='prototype formula, e.g. Cu or NaCl')
    parser.add_argument('crystal', choices=CRYSTALS, help='ASE crystal prototype')
    parser.add_argument('mode', choices=('primitive', 'orthorhombic', 'cubic'), help='cell type')
    parser.add_argument('--a', required=True, help='lattice parameter a in Å')
    parser.add_argument('--b', help='lattice parameter b in Å (orthorhombic prototype)')
    parser.add_argument('--c', help='lattice parameter c in Å (hcp, bct, wurtzite, orthorhombic)')
    parser.add_argument('--alpha', help='rhombohedral angle in degrees')
    parser.add_argument('--u', help='wurtzite internal coordinate')
    parser.add_argument('--repeat', nargs=3, default=(1, 1, 1), metavar=('N1', 'N2', 'N3'),
                        help='supercell repeats along the three cell vectors (default: 1 1 1)')
    parser.add_argument('-o', '--output', type=Path, required=True, help='new POSCAR path')
    parsed = parser.parse_args(args)
    request = vars(parsed).copy()
    output = request.pop('output').expanduser()
    for key in ('b', 'c', 'alpha', 'u'):
        if request[key] is None:
            del request[key]
        elif key not in CRYSTALS[parsed.crystal]:
            parser.error(f'--{key} is not used by {parsed.crystal}')
    try:
        parameters(request)
        if output.exists() or output.is_symlink():
            raise FileExistsError(f'Output already exists: {output}')
        command = worker_command()
        run = subprocess.run(command, input=json.dumps(request), text=True, encoding='utf-8',
                             capture_output=True, timeout=30, **launch_options(command))
        try:
            response = json.loads(run.stdout)
        except ValueError as error:
            raise RuntimeError('ASE worker could not start. '+run.stderr[-400:]) from error
        if run.returncode or not response.get('ok'):
            raise RuntimeError(response.get('error', 'ASE generation failed.'))
        write_bulk_poscar(output, response['result']['poscar'])
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as error:
        print(f'Bulk generation failed: {error}', file=sys.stderr)
        return 1
    print(f'Saved {output}')
    return 0

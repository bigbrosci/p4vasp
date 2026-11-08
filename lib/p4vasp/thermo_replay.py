"""Export a portable ASE calculation snapshot without importing ASE into GTK."""
import json
from pathlib import Path


REPLAY = '''#!/usr/bin/env python3
"""Reproduce this p4vasp thermochemistry result using Python, ASE and NumPy.
Install dependencies: python -m pip install ase=={ase_version} numpy
Run: python SCRIPT.py [--output NEW_RESULT.json]
The embedded equilibrium structure, masses and effective frequencies are used;
no p4vasp installation or original OUTCAR is required. This does not run DFT.
"""
import argparse
import json
import math
from pathlib import Path
import sys

SNAPSHOT = json.loads({snapshot})


def calculate():
    import ase
    from ase import Atoms, units
    from ase.thermochemistry import HarmonicThermo, IdealGasThermo
    saved = SNAPSHOT['result']
    settings = saved['request_settings']
    if ase.__version__ != saved['ase_version']:
        print('Warning: ASE version differs from the original calculation: ' + saved['ase_version'], file=sys.stderr)
    energies = [frequency * units.invcm for frequency in saved['effective_cm1']]
    potential = saved['electronic_energy_eV']
    potential = 0.0 if potential is None else potential
    temperature = saved['temperature_K']
    if settings['model'] == 'gas':
        data = SNAPSHOT['structure']
        atoms = Atoms(data['symbols'], positions=data['positions'], masses=data['masses'])
        thermo = IdealGasThermo(energies, settings['geometry'], atoms=atoms,
                               symmetrynumber=int(settings['symmetry']), spin=float(settings['spin']),
                               potentialenergy=potential, vib_selection='all')
        pressure = saved['pressure_Pa']
        entropy = thermo.get_entropy(temperature, pressure, verbose=False)
        free = thermo.get_gibbs_energy(temperature, pressure, verbose=False)
        enthalpy = float(thermo.get_enthalpy(temperature, verbose=False))
    else:
        thermo = HarmonicThermo(energies, potentialenergy=potential)
        entropy = thermo.get_entropy(temperature, verbose=False)
        free = thermo.get_helmholtz_energy(temperature, verbose=False)
        enthalpy = None
    result = dict(saved)
    result.update(ase_version=ase.__version__, ZPE_eV=float(thermo.get_ZPE_correction()),
                  U_eV=float(thermo.get_internal_energy(temperature, verbose=False)),
                  H_eV=enthalpy, S_eV_per_K=float(entropy), TS_eV=float(temperature * entropy),
                  free_energy_eV=float(free), correction_eV=float(free - potential),
                  source=SNAPSHOT['source'])
    for key in ('ZPE_eV', 'U_eV', 'S_eV_per_K', 'TS_eV', 'free_energy_eV', 'correction_eV'):
        if not math.isfinite(result[key]):
            raise ValueError('Non-finite thermochemistry result: ' + key)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path,
                        default=Path(__file__).with_name(Path(__file__).stem + '_rerun.json'))
    args = parser.parse_args()
    result = calculate()
    with args.output.open('x', encoding='utf-8') as output:
        json.dump(result, output, indent=2, allow_nan=False)
    print(json.dumps(result, indent=2, allow_nan=False))
    print('Saved ' + str(args.output))


if __name__ == '__main__':
    main()
'''


def replay_script(data, result):
    snapshot = dict(source=data['path'], result=result,
                    structure={key:data[key] for key in ('symbols','positions','masses')},
                    modes=[{key:mode[key] for key in ('index','cm1','imaginary')} for mode in data['modes']])
    # repr quotes JSON as inert Python string data, including quotes and paths.
    return REPLAY.replace('{ase_version}', result['ase_version']).replace(
        '{snapshot}', repr(json.dumps(snapshot, ensure_ascii=True, allow_nan=False)))


def save_thermochemistry(path, data, result):
    """Create a JSON report and sibling script; never clobber either file."""
    path=Path(path)
    if path.suffix.lower()!='.json':
        raise ValueError('Use a .json filename; a matching .py replay script is also saved.')
    script=path.with_suffix('.py')
    report=json.dumps(dict(result,source=data['path']),indent=2,allow_nan=False)
    code=replay_script(data,result)
    created=[]
    try:
        for destination,text in ((path,report),(script,code)):
            with destination.open('x',encoding='utf-8') as output:
                created.append(destination)
                output.write(text)
    except BaseException:
        for destination in created:destination.unlink()
        raise
    return path,script

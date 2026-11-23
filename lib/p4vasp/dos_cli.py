"""Headless positional DOS analysis, dispatched before any GTK/native imports."""
import argparse
import json
import math
import re
from pathlib import Path
import subprocess
import sys
from p4vasp.dos_selection import parse_atoms,parse_orbitals


def is_dos_command(args):
    if len(args)<2:return False
    source=Path(args[0])
    if source.name.upper()!='DOSCAR' and source.suffix.lower()!='.xml':return False
    return len(args)==7 or args[1].lower()=='all' or bool(re.fullmatch(r'[0-9,\s-]+',args[1]))


def limit(value):
    if value.lower() in ('full','auto'):return None
    number=float(value)
    if not math.isfinite(number):raise ValueError('Energy limits must be finite.')
    return number


def main(args=None):
    parser=argparse.ArgumentParser(description='Analyze projected DOS without opening the GUI.',
        usage='p4v DOSCAR selected_atoms orbital(s) both/up/down Emin Emax output.csv')
    parser.add_argument('source',help='DOSCAR or vasprun.xml')
    parser.add_argument('atoms',help='1-based numbers/ranges, e.g. 1-3,8; or all')
    parser.add_argument('orbitals',help='d or comma-separated individual orbitals, e.g. dxy,dyz')
    parser.add_argument('spin',type=str.lower,choices=('both','up','down'))
    parser.add_argument('emin',help='Energy relative to EF, or full')
    parser.add_argument('emax',help='Energy relative to EF, or full')
    parser.add_argument('output',type=Path)
    parsed=parser.parse_args(args)
    try:
        request=dict(path=str(Path(parsed.source).resolve()),atoms=parse_atoms(parsed.atoms),
                     orbital=','.join(parse_orbitals(parsed.orbitals)),spin=parsed.spin,
                     emin=limit(parsed.emin),emax=limit(parsed.emax))
        if parsed.output.exists():raise FileExistsError('Output exists; choose a new CSV filename.')
        from p4vasp.dos_analysis import worker_command,save_result
        from p4vasp.model_worker import launch_options
        command=worker_command()
        run=subprocess.run(command,input=json.dumps(request),text=True,encoding='utf-8',capture_output=True,
                           timeout=120,**launch_options(command))
        try:response=json.loads(run.stdout)
        except ValueError:raise RuntimeError('DOS worker failed to start. '+run.stderr[-400:])
        if run.returncode or not response.get('ok'):raise RuntimeError(response.get('error','DOS analysis failed.'))
        result=response['result'];save_result(parsed.output,result)
        for name,value,unit in result['rows']:
            print(name+': '+('Unavailable' if value is None else '%.10g'%value)+' '+unit)
        print('Saved '+str(parsed.output.resolve()))
        return 0
    except (OSError,ValueError,RuntimeError,subprocess.TimeoutExpired) as error:
        print('DOS analysis failed: '+str(error),file=sys.stderr)
        return 1

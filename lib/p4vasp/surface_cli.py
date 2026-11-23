"""Rebuild a saved portable surface recipe without GTK/native viewer imports."""
import argparse
import json
from pathlib import Path
import subprocess
import sys


def main(args=None):
    parser=argparse.ArgumentParser(description=__doc__,prog='p4v --surface-replay')
    parser.add_argument('recipe',type=Path,help='saved surface.json')
    parser.add_argument('output',type=Path,help='new output folder (parent must exist)')
    parsed=parser.parse_args(args)
    try:
        data=json.loads(parsed.recipe.read_text(encoding='utf-8'))
        if not isinstance(data,dict):raise ValueError('Surface recipe must be a JSON object.')
        request=data['request']
        if not isinstance(request,dict):raise ValueError('Surface request must be a JSON object.')
        if request.get('source') not in ('preset','poscar'):
            raise ValueError('The recipe must contain a preset or embedded bulk POSCAR.')
        if parsed.output.exists():raise FileExistsError('Output folder exists; choose a new folder.')
        from p4vasp.ase_surface import worker_command
        from p4vasp.model_worker import launch_options
        command=worker_command()
        run=subprocess.run(command,input=json.dumps(request),text=True,encoding='utf-8',capture_output=True,
                           timeout=60,**launch_options(command))
        try:response=json.loads(run.stdout)
        except ValueError:raise RuntimeError('Surface worker failed. '+run.stderr[-400:])
        if run.returncode or not response.get('ok'):raise RuntimeError(response.get('error','Surface rebuild failed.'))
        from p4vasp.surface_replay import surface_contents
        from p4vasp.single_atom_inputs import write_contents
        output=parsed.output.expanduser().absolute()
        write_contents(surface_contents(response['result']),output.parent,output.name)
        print('Saved '+str(output));return 0
    except (OSError,ValueError,KeyError,TypeError,RuntimeError,subprocess.TimeoutExpired) as error:
        print('Surface replay failed: '+str(error),file=sys.stderr);return 1

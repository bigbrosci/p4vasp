"""Portable surface recipes plus standalone Python and headless Bash replay."""
import json
from pathlib import Path

INDEX_CONVENTION='zero-based POSCAR atom order; layer_numbers are bottom-up starting at 1'


def metadata(result):
    data={key:value for key,value in result.items() if key!='poscar'}
    data['index_convention']=INDEX_CONVENTION
    return data


def bash_script():
    from p4vasp.model_worker import bash_launcher
    return ('#!/usr/bin/env bash\nset -euo pipefail\n'
            '# Rebuild from the adjacent portable surface.json, without a GUI.\n'
            '# Run: bash rebuild_surface.sh [NEW_OUTPUT_FOLDER]\n'
            'script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"\n'
            'if ! command -v p4v >/dev/null 2>&1; then\n'+
            bash_launcher()+
            'fi\n'
            'p4v --surface-replay "$script_dir/surface.json" "${1:-$script_dir/surface_rebuilt}"\n')


def python_script(result,shell):
    if result['request'].get('source') not in ('preset','poscar'):
        raise ValueError('Save a generated surface with embedded bulk data, not a live file reference.')
    from p4vasp.ase_bulk import MAX_ATOMS
    source=Path(__file__).with_name('surface_geometry.py').read_text(encoding='utf-8')
    source=source.replace('from p4vasp.ase_bulk import MAX_ATOMS','MAX_ATOMS = '+repr(MAX_ATOMS))
    header='''#!/usr/bin/env python3
"""Rebuild this surface from the saved parameters and embedded bulk input.
Install: python -m pip install ase==%s
Run: python rebuild_surface.py [--output NEW_OUTPUT_FOLDER]
No p4vasp, original POSCAR/CIF, GTK or display is required. No VASP job is run.
Produces POSCAR, surface.json and replay scripts in a new non-overwriting folder.
Camera/preview selections are not calculation parameters and are not recorded.
"""
'''%result['ase_version']
    tail='''
import argparse
import json
import sys

REQUEST=json.loads(%s)
EXPECTED_ASE=%r
BASH_SCRIPT=%r


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=Path(__file__).resolve().parent/'surface_rebuilt')
    args=parser.parse_args()
    target=args.output.expanduser().absolute()
    if target.exists():raise FileExistsError('Output folder exists; choose a new folder.')
    if not target.parent.is_dir():raise ValueError('Choose an existing parent folder.')
    result=build_surface(REQUEST)
    if result['ase_version']!=EXPECTED_ASE:
        print('Warning: ASE version differs from the saved construction.',file=sys.stderr)
    data={key:value for key,value in result.items() if key!='poscar'}
    data['index_convention']=%r
    files={'POSCAR':result['poscar'],'surface.json':json.dumps(data,indent=2)+'\\n',
           'rebuild_surface.py':Path(__file__).read_text(encoding='utf-8'),'rebuild_surface.sh':BASH_SCRIPT}
    target.mkdir()
    created=[]
    try:
        for name,text in files.items():
            path=target/name
            with path.open('x',encoding='utf-8',newline='\\n') as stream:
                created.append(path);stream.write(text)
    except Exception:
        for path in created:path.unlink(missing_ok=True)
        try:target.rmdir()
        except OSError:pass
        raise
    print('Saved '+str(target))


if __name__=='__main__':main()
'''%(repr(json.dumps(result['request'],ensure_ascii=False,allow_nan=False)),result['ase_version'],shell,INDEX_CONVENTION)
    text=header+'\n'+source+'\n'+tail
    compile(text,'rebuild_surface.py','exec')
    return text


def surface_contents(result):
    shell=bash_script()
    return {'POSCAR':result['poscar'],'surface.json':json.dumps(metadata(result),indent=2)+'\n',
            'rebuild_surface.py':python_script(result,shell),'rebuild_surface.sh':shell}

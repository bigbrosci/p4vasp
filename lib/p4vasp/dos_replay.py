"""Export the selected projected DOS snapshot and the shared calculation as plain Python."""
import json
import shlex
from pathlib import Path


def script_text(result):
    if not result or 'replay' not in result:
        raise ValueError('Analyze the current selection before exporting its Python script.')
    snapshot=json.dumps(result['replay'],ensure_ascii=False,allow_nan=False)
    version=result['pymatgen_version']
    header='''#!/usr/bin/env python3
"""Reproduce this projected DOS analysis without p4vasp or the original VASP files.
Install: python -m pip install pymatgen==%s
Run: python SCRIPT.py [--emin EMIN --emax EMAX] [--output NEW_RESULT.csv]
The embedded spectrum is already summed for the original atoms/orbital/spin.
Energy limits are relative to EF=0 eV. Changing the original selection requires
exporting a new script. The one-site structure is only an API container for
this numerical spectrum, not a new calculation geometry. No VASP job is run.
"""
'''%version
    core=Path(__file__).with_name('dos_metrics.py').read_text(encoding='utf-8')
    main='''
import argparse
import csv
import json
from pathlib import Path
import sys

SNAPSHOT=json.loads(%s)


def main():
    from pymatgen.core import Structure
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--emin',type=float,default=SNAPSHOT['metadata']['emin'])
    parser.add_argument('--emax',type=float,default=SNAPSHOT['metadata']['emax'])
    parser.add_argument('--output',type=Path,default=Path(__file__).with_name(Path(__file__).stem+'_results.csv'))
    args=parser.parse_args()
    result=dict(SNAPSHOT['metadata'])
    result.update(calculate_metrics(SNAPSHOT['energies'],SNAPSHOT['density'],
                                   Structure.from_dict(SNAPSHOT['structure']),args.emin,args.emax,
                                   SNAPSHOT['metadata'].get('band_label','d')))
    if result['pymatgen_version']!=SNAPSHOT['metadata']['pymatgen_version']:
        print('Warning: pymatgen version differs from the original analysis.',file=sys.stderr)
    with args.output.open('x',encoding='utf-8',newline='') as stream:
        writer=csv.writer(stream);writer.writerow(['Metadata','Value'])
        for key,value in result.items():
            if key!='rows':writer.writerow([key,json.dumps(value,ensure_ascii=False)])
        writer.writerow([]);writer.writerow(['Property','Value','Unit']);writer.writerows(result['rows'])
    for name,value,unit in result['rows']:
        print(name+': '+('Unavailable' if value is None else ('%%.10g'%%value))+' '+unit)
    print('Saved '+str(args.output))


if __name__=='__main__':main()
'''%repr(snapshot)
    text=header+'\n'+core+'\n'+main
    compile(text,'<d-band replay>','exec')
    return text


def save_script(path,result):
    text=script_text(result)
    with Path(path).open('x',encoding='utf-8',newline='') as stream:stream.write(text)
    return Path(path)


def bash_text(path,result):
    from p4vasp.model_worker import bash_launcher
    command=['p4v',result['path'],','.join(map(str,result['atoms'])),result['orbital'],result['spin'],
             '%.17g'%result['emin'],'%.17g'%result['emax']]
    output=Path(path).with_name(Path(path).stem+'_cli.csv').absolute()
    return ('#!/usr/bin/env bash\nset -euo pipefail\n'
            '# Re-read the original VASP source using the headless p4v command.\n'
            '# Run: bash THIS_SCRIPT.sh [NEW_OUTPUT.csv]\n'
            '# p4v must support positional DOS analysis. Bash does not load interactive aliases.\n'
            'if ! command -v p4v >/dev/null 2>&1; then\n'
            +bash_launcher()+
            'fi\n'
            'default_output='+shlex.quote(str(output))+'\n'
            'output="${1:-$default_output}"\n'+shlex.join(command)+' "$output"\n')


def save_scripts(path,result):
    """Create matching .py/.sh files exclusively; roll back on pair failure."""
    path=Path(path)
    if path.suffix.lower()!='.py':raise ValueError('Choose a .py filename; the matching .sh is exported alongside it.')
    shell=path.with_suffix('.sh')
    if path.exists() or shell.exists():raise FileExistsError('A script already exists; choose a new basename.')
    texts=((path,script_text(result)),(shell,bash_text(path,result)))
    created=[]
    try:
        for destination,text in texts:
            with destination.open('x',encoding='utf-8',newline='') as stream:
                created.append(destination);stream.write(text)
    except Exception:
        for destination in reversed(created):destination.unlink(missing_ok=True)
        raise
    return path,shell

"""Export the selected d-DOS snapshot and the shared calculation as plain Python."""
import json
from pathlib import Path


def save_script(path, result):
    if not result or 'replay' not in result:
        raise ValueError('Analyze the current selection before exporting its Python script.')
    snapshot=json.dumps(result['replay'],ensure_ascii=False,allow_nan=False)
    version=result['pymatgen_version']
    header='''#!/usr/bin/env python3
"""Reproduce this d-DOS analysis without p4vasp or the original VASP files.
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
                                   Structure.from_dict(SNAPSHOT['structure']),args.emin,args.emax))
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
    compile(text,str(path),'exec')
    with Path(path).open('x',encoding='utf-8',newline='') as stream:stream.write(text)
    return Path(path)

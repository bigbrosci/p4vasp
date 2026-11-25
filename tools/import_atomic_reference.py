"""Rebuild offline neutral-atom data from captured NIST ASD table rows."""
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'lib'))
from p4vasp.element_data import SYMBOLS
SOURCE_URL='https://physics.nist.gov/cgi-bin/ASD/ie.pl?at_num_out=on&biblio=on&e_out=0&el_name_out=on&level_out=on&shells_out=on&spectra=H-DS+i&unc_out=on&units=1'


def convert(path):
    records={}
    for line in path.read_text(encoding='utf-8').splitlines():
        parts=[part.strip() for part in line.split('|')]
        if len(parts)<4 or not parts[0].isdigit():continue
        number=int(parts[0])
        if not 1<=number<=len(SYMBOLS):raise ValueError('Invalid atomic number')
        symbol=SYMBOLS[number-1]
        if symbol in records:raise ValueError('Duplicate atomic number')
        config=parts[2].replace('{','').replace('}','')
        config=re.sub(r'(?<!^)(?=\d[spdfgh])',' ',config)
        term=parts[3].replace('{','').replace('}','').replace('^','').replace('/_','/')
        match=re.match(r'^(\d+)[A-Z]',term)
        multiplicity=int(match[1]) if match else None
        if term.startswith('_'):term='J='+term[1:]+' (term unassigned)'
        records[symbol]=dict(number=number,name=parts[1],configuration=config,term=term,
                             multiplicity=multiplicity,spin=None if multiplicity is None else (multiplicity-1)/2)
    if len(records)!=108:raise ValueError('Expected 108 captured neutral rows, H through Hs.')
    return dict(source=dict(name='NIST Atomic Spectra Database 5.12 (2024)',url=SOURCE_URL,
                            doi='10.18434/T4W30F',retrieved='2026-11-25',
                            capture_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                            scope='Neutral atoms only. Spin/multiplicity derived from assigned LS labels; not DFT predictions. Missing values are unknown.'),elements=records)


if __name__=='__main__':
    source=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'data/resources/atomic_states_source.txt'
    output=Path(sys.argv[2]) if len(sys.argv)>2 else ROOT/'data/resources/atomic_states.json'
    output.write_text(json.dumps(convert(source),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

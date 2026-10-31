"""Rebuild the bundled supplement from an ASE wheel; no ASE/NumPy installation.

Usage: python3 tools/import_element_reference.py /path/to/ase-3.29.0-py3-none-any.whl
Existing 36 XML element records take precedence. ASE placeholders remain null.
"""
import ast
import hashlib
import json
from pathlib import Path
import sys
from zipfile import ZipFile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'lib'))
from p4vasp.element_data import SYMBOLS


def value(node):
    if isinstance(node, ast.Constant): return node.value
    if isinstance(node, (ast.List, ast.Tuple)): return [value(item) for item in node.elts]
    # ASE's `missing=2.0` and dummy radius are placeholders, not measurements.
    if isinstance(node, ast.Name) and node.id in ('missing', '_R_DUMMY'): return None
    if isinstance(node, ast.Attribute) and node.attr == 'nan': return None
    raise ValueError('Unsupported source expression: '+ast.dump(node))


def array(source, name):
    for node in ast.parse(source).body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in node.targets):
            return value(node.value.args[0])
    raise ValueError(name)


def main(wheel):
    with ZipFile(wheel) as archive:
        masses = array(archive.read('ase/data/__init__.py'), 'atomic_masses_iupac2016')
        covalent = array(archive.read('ase/data/__init__.py'), 'covalent_radii')
        radii = array(archive.read('ase/data/vdw.py'), 'vdw_radii')
        colors = array(archive.read('ase/data/colors.py'), 'jmol_colors')
        license_name = next(name for name in archive.namelist() if name.endswith('/licenses/LICENSE'))
        (ROOT/'data/resources/ASE-LICENSE.txt').write_bytes(archive.read(license_name))
    xml = ET.parse(ROOT/'data/atomtypes.xml').getroot().find('./array')
    fields = [(f.text or '').strip() for f in xml.findall('field')]
    legacy = {dict(zip(fields, row.text.split()))['element']: dict(zip(fields, row.text.split())) for row in xml.findall('./set/r')}
    records = []
    for number, symbol in enumerate(SYMBOLS, 1):
        record = {'symbol':symbol, 'number':number, 'mass':masses[number],
                  'radius':radii[number] if number < len(radii) else None,
                  'covalent':covalent[number] if number < len(covalent) else None}
        rgb = colors[number] if number < len(colors) else [None]*3
        record.update(dict(zip(('red','green','blue'), rgb)))
        if symbol in legacy:
            for field in ('mass','radius','covalent','red','green','blue'):
                record[field] = float(legacy[symbol][field])
        records.append(record)
    data = {'source': {'archive':Path(wheel).name, 'sha256':hashlib.sha256(Path(wheel).read_bytes()).hexdigest(),
                       'url':'https://ase-lib.org/ase/data.html',
                       'colors':'ASE ase/data/colors.py jmol_colors; existing XML values retained',
                       'radii':'Existing display radii retained; new values from ASE vdw_radii (angstrom)',
                       'masses':'Existing values retained; ASE atomic_masses_iupac2016, including selected isotope masses',
                       'missing':'null; ASE covalent missing/dummy sentinels excluded'}, 'elements':records}
    (ROOT/'data/resources/elements.json').write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n')
    print({field:sum(row[field] is not None for row in records) for field in ('mass','radius','covalent','red')})

if __name__ == '__main__': main(sys.argv[1])

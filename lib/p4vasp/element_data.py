"""Join the existing element table with per-element INCAR defaults."""
import copy
import json
import math
import xml.etree.ElementTree as ET
from p4vasp.resource_data import validate

SYMBOLS = ('H He Li Be B C N O F Ne Na Mg Al Si P S Cl Ar K Ca Sc Ti V Cr Mn Fe Co Ni Cu Zn Ga Ge As Se Br Kr Rb Sr Y Zr Nb Mo Tc Ru Rh Pd Ag Cd In Sn Sb Te I Xe Cs Ba La Ce Pr Nd Pm Sm Eu Gd Tb Dy Ho Er Tm Yb Lu Hf Ta W Re Os Ir Pt Au Hg Tl Pb Bi Po At Rn Fr Ra Ac Th Pa U Np Pu Am Cm Bk Cf Es Fm Md No Lr Rf Db Sg Bh Hs Mt Ds Rg Cn Nh Fl Mc Lv Ts Og').split()
NUMBERS = {symbol: index+1 for index, symbol in enumerate(SYMBOLS)}
COLUMNS = ('Name', 'atomic number', 'mass', 'radii', 'R', 'G', 'B', 'Magmom', 'U', 'J')
XML_FIELDS = ('mass', 'radius', 'red', 'green', 'blue')
DEFAULT_FIELDS = ('mag_value', 'u_value', 'j_value')


def check_value(column, value):
    value = value.strip()
    if not value and column >= 7:
        return value
    number = float(value)
    if not math.isfinite(number):
        raise ValueError('Use a finite number.')
    if 2 <= column <= 6 and number < 0:
        raise ValueError('Mass, radius and RGB must be nonnegative.')
    if column == 2 and number <= 0:
        raise ValueError('Atomic mass must be positive.')
    if 4 <= column <= 6:
        if number > 255 or not number.is_integer():
            raise ValueError('RGB values must be integers between 0 and 255.')
        return str(int(number))
    return value


class ElementData:
    def __init__(self, store):
        self.store = store
        self.reload()

    def reload(self):
        self.sources = {key: self.store.read(key) for key in ('elements', 'incar')}
        self.xml = validate('elements', self.sources['elements'][0])
        self.config = validate('incar', self.sources['incar'][0])
        array = self.xml.find("./array[@name='atomtypes']")
        self.fields = [(field.text or '').strip() for field in array.findall('field')]
        self.rows = []
        for node in array.findall('./set/r'):
            record = dict(zip(self.fields, node.text.split()))
            symbol = record['element']
            if symbol not in NUMBERS: continue  # Preserve numeric fallback entries outside the editor.
            row = [symbol, str(NUMBERS[symbol])] + [record[field] for field in XML_FIELDS]
            row[4:7] = [str(round(float(value)*255)) for value in row[4:7]]
            row += [str(self.config['elements'][field][symbol]) if symbol in self.config['elements'][field] else ''
                    for field in DEFAULT_FIELDS]
            self.rows.append(row)
        self.rows.sort(key=lambda row: int(row[1]))

    def serialize(self, rows):
        rows = [list(row) for row in rows]
        if [row[:2] for row in rows] != [row[:2] for row in self.rows]:
            raise ValueError('Element identities and atomic numbers cannot be changed.')
        for row in rows:
            if len(row) != len(COLUMNS): raise ValueError('Incorrect column count.')
            for column in range(2, 10): row[column] = check_value(column, row[column])
        by_symbol = {row[0]: row for row in rows}
        original_rows = {row[0]: row for row in self.rows}
        root = copy.deepcopy(self.xml)
        array = root.find("./array[@name='atomtypes']")
        for node in array.findall('./set/r'):
            values = node.text.split(); symbol = values[self.fields.index('element')]
            if symbol in by_symbol:
                for column, field in enumerate(XML_FIELDS, 2):
                    value = by_symbol[symbol][column]
                    if value != original_rows[symbol][column]:
                        values[self.fields.index(field)] = format(int(value)/255, '.17g') if column >= 4 else value
                node.text = ' '.join(values)
        config = copy.deepcopy(self.config)
        for row in rows:
            for column, field in enumerate(DEFAULT_FIELDS, 7):
                if row[column] == '': config['elements'][field].pop(row[0], None)
                else: config['elements'][field][row[0]] = float(row[column])
        texts = {}
        if any(row[2:7] != original[2:7] for row, original in zip(rows, self.rows)):
            texts['elements'] = '<?xml version="1.0"?>\n'+ET.tostring(root, encoding='unicode')+'\n'
        if config != self.config:
            texts['incar'] = json.dumps(config, ensure_ascii=False, indent=2)+'\n'
        for key, text in texts.items(): validate(key, text)
        return texts

    def save(self, rows):
        texts = self.serialize(rows)
        # Check both inputs even when only one file needs writing.
        for key, (_, expected) in self.sources.items():
            if self.store.read(key)[1] != expected:
                raise ValueError('Source file changed outside the table. Reload and review.')
        written = []
        backups = []
        try:
            for key, text in texts.items():
                content, backup = self.store.save(key, text, self.sources[key][1])
                written.append((key, content)); backups.append(backup)
        except Exception as error:
            failures = []
            for key, content in reversed(written):
                try: self.store.save(key, self.sources[key][0], content)
                except Exception as rollback: failures.append(str(self.store.path(key))+': '+str(rollback))
            if failures:
                raise RuntimeError('Save incomplete; restore backups before continuing. Backups: '+
                                   ', '.join(str(path) for path in backups)+'; errors: '+ '; '.join(failures)) from error
            raise
        self.reload()
        return backups

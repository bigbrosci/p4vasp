"""Join the existing element table with per-element INCAR defaults."""
import copy
import json
import math
from p4vasp.resource_data import validate

SYMBOLS = ('H He Li Be B C N O F Ne Na Mg Al Si P S Cl Ar K Ca Sc Ti V Cr Mn Fe Co Ni Cu Zn Ga Ge As Se Br Kr Rb Sr Y Zr Nb Mo Tc Ru Rh Pd Ag Cd In Sn Sb Te I Xe Cs Ba La Ce Pr Nd Pm Sm Eu Gd Tb Dy Ho Er Tm Yb Lu Hf Ta W Re Os Ir Pt Au Hg Tl Pb Bi Po At Rn Fr Ra Ac Th Pa U Np Pu Am Cm Bk Cf Es Fm Md No Lr Rf Db Sg Bh Hs Mt Ds Rg Cn Nh Fl Mc Lv Ts Og').split()
NUMBERS = {symbol: index+1 for index, symbol in enumerate(SYMBOLS)}
COLUMNS = ('Name', 'atomic number', 'mass (u)', 'radii (Å)', 'R (0–255)', 'G (0–255)', 'B (0–255)', 'Magmom (μB)', 'U (eV)', 'J (eV)')
XML_FIELDS = ('mass', 'radius', 'red', 'green', 'blue')
DEFAULT_FIELDS = ('mag_value', 'u_value', 'j_value')


def check_value(column, value):
    value = value.strip()
    if not value:
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
        self.sources = {key: self.store.read(key) for key in ('periodic', 'incar')}
        self.catalog = validate('periodic', self.sources['periodic'][0])
        self.config = validate('incar', self.sources['incar'][0])
        self.rows = []
        for record in self.catalog['elements']:
            symbol = record['symbol']
            row = [symbol, str(record['number'])]
            for field in XML_FIELDS:
                value = record[field]
                row.append('' if value is None else str(round(value*255)) if field in ('red','green','blue') else str(value))
            row += [str(self.config['elements'][field][symbol]) if symbol in self.config['elements'][field] else ''
                    for field in DEFAULT_FIELDS]
            self.rows.append(row)

    def serialize(self, rows):
        rows = [list(row) for row in rows]
        if [row[:2] for row in rows] != [row[:2] for row in self.rows]:
            raise ValueError('Element identities and atomic numbers cannot be changed.')
        catalog = copy.deepcopy(self.catalog)
        config = copy.deepcopy(self.config)
        for row, original, record in zip(rows, self.rows, catalog['elements']):
            if len(row) != len(COLUMNS): raise ValueError('Incorrect column count.')
            for column in range(2, 10): row[column] = check_value(column, row[column])
            for column, field in enumerate(XML_FIELDS, 2):
                value = row[column]
                if value != original[column]:
                    record[field] = None if value == '' else int(value)/255 if column >= 4 else float(value)
            for column, field in enumerate(DEFAULT_FIELDS, 7):
                if row[column] == '': config['elements'][field].pop(row[0], None)
                else: config['elements'][field][row[0]] = float(row[column])
        texts = {}
        if catalog != self.catalog:
            texts['periodic'] = json.dumps(catalog, ensure_ascii=False, indent=2)+'\n'
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


def runtime_values(record):
    """Finite rendering fallbacks; these are never written as reference data."""
    defaults = {'mass':0.0, 'radius':1.0, 'covalent':0.0, 'red':1.0, 'green':1.0, 'blue':1.0}
    return {field:record[field] if record[field] is not None else default for field, default in defaults.items()}


def apply_catalog(atominfo, store=None):
    from p4vasp.resource_data import ResourceStore
    store = store or ResourceStore()
    catalog = validate('periodic', store.read('periodic')[0])
    # XML-backed arrays may be lazy read-only sequences; additions need a list.
    atominfo.atomtypes.data = [list(row) for row in atominfo.atomtypes.data]
    for record in catalog['elements']:
        target = atominfo.getRecordForElement(record['symbol'])
        if target is None:
            target = atominfo.appendEmpty()
            target.element = record['symbol']
        for field, value in runtime_values(record).items(): setattr(target, field, value)
    return atominfo

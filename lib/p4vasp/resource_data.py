"""Resource defaults and personal field overrides, with atomic saves and backups."""
from datetime import datetime
import json
import math
import os
from pathlib import Path
import re
import shutil
import tempfile
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET

import p4vasp

FILES = {'elements': 'atomtypes.xml', 'incar': 'incar/presets.json',
         'websites': 'resources/websites.json', 'periodic': 'resources/elements.json'}


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate JSON key: '+key)
        result[key] = value
    return result


def validate(key, text):
    if key == 'elements':
        root = ET.fromstring(text)
        array = root.find("./array[@name='atomtypes']")
        if root.tag != 'atominfo' or array is None:
            raise ValueError('Expected atominfo / array name="atomtypes".')
        fields = [(node.text or '').strip() for node in array.findall('field')]
        required = ('element', 'mass', 'radius', 'covalent', 'red', 'green', 'blue')
        if len(set(fields)) != len(fields) or not set(required).issubset(fields):
            raise ValueError('Keep unique element/mass/radius/covalent/red/green/blue fields.')
        seen = set()
        rows = array.findall('./set/r')
        if not rows:
            raise ValueError('The element table must not be empty.')
        for number, row in enumerate(rows, 1):
            values = (row.text or '').split()
            if len(values) != len(fields):
                raise ValueError('Element row %d: wrong number of fields.' % number)
            record = dict(zip(fields, values))
            if record['element'] in seen:
                raise ValueError('Duplicate element: '+record['element'])
            seen.add(record['element'])
            for field in required[1:]:
                value = float(record[field])
                if not math.isfinite(value) or value < 0 or (field in ('red','green','blue') and value > 1):
                    raise ValueError('Element row %d: invalid %s.' % (number, field))
        return root
    data = json.loads(text, object_pairs_hook=_pairs,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError('Invalid number: '+value)))
    if key == 'periodic':
        from p4vasp.element_data import SYMBOLS
        if not isinstance(data, dict) or not isinstance(data.get('elements'), list):
            raise ValueError('Expected an elements list.')
        if len(data['elements']) != 118 or not all(isinstance(row, dict) for row in data['elements']) or [row.get('symbol') for row in data['elements']] != SYMBOLS:
            raise ValueError('Keep all 118 element symbols in atomic-number order.')
        for number, row in enumerate(data['elements'], 1):
            if type(row.get('number')) is not int or row['number'] != number:
                raise ValueError('Incorrect atomic number.')
            for field in ('mass', 'radius', 'covalent', 'red', 'green', 'blue'):
                if field not in row: raise ValueError('Missing field: '+field)
                value = row[field]
                if value is None: continue
                if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
                    raise ValueError('Invalid '+field+' for '+row['symbol'])
                if field == 'mass' and value <= 0:
                    raise ValueError('Mass must be positive or null.')
                if field in ('red','green','blue') and value > 1:
                    raise ValueError('Stored RGB must be 0–1 or null.')
        return data
    if key == 'websites':
        if not isinstance(data, list):
            raise ValueError('Use a JSON list of websites.')
        names = set()
        for site in data:
            if not isinstance(site, dict) or not isinstance(site.get('name'), str) or not site['name'].strip():
                raise ValueError('Each website needs a name.')
            if site['name'] in names:
                raise ValueError('Duplicate website name: '+site['name'])
            names.add(site['name'])
            for field in ('url', 'description', 'badge', 'icon'):
                if field in site and not isinstance(site[field], str):
                    raise ValueError('Website '+field+' must be text.')
            url = urlsplit(site.get('url', ''))
            if url.scheme not in ('http', 'https') or not url.hostname or url.username or url.password:
                raise ValueError('Use an HTTP(S) website URL without embedded credentials.')
            if any(c.isspace() for c in site['url']):
                raise ValueError('Website URLs must not contain whitespace.')
            icon = site.get('icon', '')
            if icon and (Path(icon).name != icon or '/' in icon or '\\' in icon):
                raise ValueError('Icon must be a filename in database_logos.')
        return data
    if key != 'incar':
        raise ValueError('Unknown resource.')
    if not isinstance(data, dict) or not all(isinstance(data.get(k), dict) for k in ('categories','standard','elements')):
        raise ValueError('Keep categories, standard and elements JSON objects.')
    if not isinstance(data['categories'].get('Tasks'), dict):
        raise ValueError('Keep the Tasks category.')
    def parameters(params):
        if not isinstance(params, dict):
            raise ValueError('Preset parameters must be an object.')
        for tag,value in params.items():
            if not re.fullmatch('[A-Za-z][A-Za-z0-9_]*', tag) or not isinstance(value, (str,int,float,bool)):
                raise ValueError('Invalid INCAR parameter: '+str(tag))
            if isinstance(value, float) and not math.isfinite(value):
                raise ValueError('Non-finite INCAR value.')
    for category in data['categories'].values():
        if not isinstance(category, dict):
            raise ValueError('Categories must contain preset objects.')
        for preset in category.values():
            if not isinstance(preset, dict) or 'params' not in preset:
                raise ValueError('Each preset needs params.')
            parameters(preset['params'])
    for params in data['standard'].values():
        parameters(params)
    for field in ('mag_value', 'u_value', 'j_value'):
        if not isinstance(data['elements'].get(field), dict):
            raise ValueError('Keep elements.'+field)
        for value in data['elements'][field].values():
            if not math.isfinite(float(value)):
                raise ValueError('Element defaults must be finite numbers.')
    return data


class ResourceStore:
    def __init__(self, root=None, backups=None, user_root=None):
        self.root = Path(root or p4vasp.p4vasp_home)/'data'
        self.user_root = (Path(user_root) if user_root is not None else
                          Path.home()/'.p4vasp/resources' if root is None else None)
        self.backups = Path(backups) if backups is not None else Path.home()/'.p4vasp/backups'

    def path(self, key):
        if self.user_root is not None and key in ('periodic', 'incar'):
            return self.user_root/(key+'.json')
        return self.root/FILES[key]

    def _effective(self, key):
        data = json.loads((self.root/FILES[key]).read_text(encoding='utf-8'))
        path = self.path(key)
        if path.exists():
            overlay = json.loads(path.read_text(encoding='utf-8'))
            if overlay.get('version') != 1:
                raise ValueError('Unsupported personal data version: '+str(path))
            for change in overlay['changes']:
                target = data
                for part in change['path'][:-1]: target = target[part]
                last = change['path'][-1]
                if change.get('delete'): target.pop(last, None)
                else: target[last] = change['value']
        text = json.dumps(data, ensure_ascii=False, indent=2)+'\n'
        validate(key, text)
        return text.encode('utf-8')

    def _personal(self, key):
        return self.user_root is not None and key in ('periodic', 'incar')

    def read(self, key):
        content = self._effective(key) if self._personal(key) else self.path(key).read_bytes()
        return content.decode('utf-8'), content

    def save(self, key, text, expected):
        validate(key, text)
        path = self.path(key)
        original = self.read(key)[1]
        payload = text
        if self._personal(key):
            base = json.loads((self.root/FILES[key]).read_text(encoding='utf-8'))
            changes = []
            def diff(old, new, parts):
                if isinstance(old, dict) and isinstance(new, dict):
                    for name in old.keys() | new.keys():
                        if name not in new: changes.append(dict(path=parts+[name], delete=True))
                        elif name not in old: changes.append(dict(path=parts+[name], value=new[name]))
                        else: diff(old[name], new[name], parts+[name])
                elif isinstance(old, list) and isinstance(new, list) and len(old) == len(new):
                    for index, (a, b) in enumerate(zip(old, new)): diff(a, b, parts+[index])
                elif old != new: changes.append(dict(path=parts, value=new))
            diff(base, json.loads(text), [])
            payload = json.dumps(dict(version=1, changes=changes), ensure_ascii=False, indent=2)+'\n'
            path.parent.mkdir(parents=True, exist_ok=True)
        if original != expected:
            raise ValueError('File changed outside this editor. Reload and review before saving.')
        folder = self.backups/key
        folder.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(prefix=datetime.now().strftime('%Y%m%d-%H%M%S-'),
                                         suffix='.bak', dir=folder, delete=False) as backup:
            backup.write(original)
            backup_path = Path(backup.name)
        descriptor, temporary = tempfile.mkstemp(prefix='.p4vasp-resource-', dir=path.parent)
        try:
            with os.fdopen(descriptor, 'w', encoding='utf-8', newline='') as stream:
                stream.write(payload)
            if path.exists(): shutil.copymode(path, temporary)
            if self.read(key)[1] != original:
                raise ValueError('File changed during save. Reload and review.')
            os.replace(temporary, path)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)
        return text.encode('utf-8'), backup_path

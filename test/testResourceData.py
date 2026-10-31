"""Validate real schemas and exercise editing without changing bundled files."""
from pathlib import Path
import json
import shutil
import tempfile
import unittest
from unittest.mock import patch
from p4vasp.resource_data import ResourceStore, FILES, validate

ROOT = Path(__file__).resolve().parents[1]

class Resources(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        for relative in FILES.values():
            target = root/'data'/relative; target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT/'data'/relative, target)
        self.store = ResourceStore(root, root/'backups')

    def test_bundled_schemas_and_16_sites(self):
        for key in FILES: validate(key, self.store.read(key)[0])
        self.assertEqual(len(validate('websites', self.store.read('websites')[0])), 16)

    def test_save_backup_and_conflict(self):
        text, original = self.store.read('websites')
        changed = text.replace('Open Catalyst Project', 'Open Catalyst')
        saved, backup = self.store.save('websites', changed, original)
        self.assertEqual(backup.read_bytes(), original)
        self.assertEqual(saved, self.store.path('websites').read_bytes())
        with self.assertRaises(ValueError): self.store.save('websites', text, original)
        self.assertEqual(self.store.read('websites')[1], saved)

    def test_element_and_incar_edit_roundtrip(self):
        for key in ('elements', 'incar'):
            text, original = self.store.read(key)
            saved, backup = self.store.save(key, text+'\n', original)
            validate(key, saved.decode('utf-8'))
            self.assertEqual(backup.read_bytes(), original)
            self.assertEqual(self.store.read(key)[1], saved)

    def test_invalid_data_preserves_files(self):
        for key, invalid in [('elements','<atominfo/>'), ('incar','{}'), ('websites','[{"name":"x","url":"file:///tmp/a"}]')]:
            text, original = self.store.read(key)
            with self.assertRaises(ValueError): self.store.save(key, invalid, original)
            self.assertEqual(self.store.path(key).read_bytes(), original)
        sites=json.loads(self.store.read('websites')[0]); sites[0]['icon']='../bad.png'
        with self.assertRaises(ValueError): validate('websites',json.dumps(sites))
        with self.assertRaises(ValueError): validate('incar','{"categories":{},"categories":{}}')

    def test_failed_replace_preserves_original_and_cleans_temp(self):
        text, original = self.store.read('websites')
        with patch('p4vasp.resource_data.os.replace', side_effect=PermissionError('read only')):
            with self.assertRaises(PermissionError): self.store.save('websites',text+'\n',original)
        self.assertEqual(self.store.read('websites')[1], original)
        self.assertFalse(list(self.store.path('websites').parent.glob('.p4vasp-resource-*')))

if __name__ == '__main__': unittest.main()

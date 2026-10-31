"""Joined element edits preserve unrelated defaults and handle two-file failure."""
from pathlib import Path
import json
import shutil
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET
from p4vasp.element_data import ElementData, COLUMNS
from p4vasp.resource_data import ResourceStore, FILES

ROOT = Path(__file__).resolve().parents[1]

class Elements(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        for path in FILES.values():
            target=root/'data'/path; target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(ROOT/'data'/path,target)
        self.store=ResourceStore(root,root/'backups'); self.data=ElementData(self.store)

    def test_rows_numbers_missing_and_noop(self):
        self.assertEqual(len(COLUMNS),10)
        self.assertEqual(self.data.rows[0][:2],['H','1'])
        self.assertEqual(self.data.rows[0][8:10],['',''])
        self.assertEqual(len(self.data.rows),36)
        self.assertEqual(self.data.save(self.data.rows),[])

    def test_joined_save_preserves_covalent_placeholders_and_presets(self):
        original=ET.fromstring(self.store.read('elements')[0])
        config=json.loads(self.store.read('incar')[0])
        rows=[row[:] for row in self.data.rows]
        rows[0][2:]=['1.01','1.3','51','77','102','-1.5','2','0.5']
        self.assertEqual(len(self.data.save(rows)),2)
        self.assertEqual(self.data.rows[0][2:7],rows[0][2:7])
        self.assertEqual(self.data.rows[0][7:],['-1.5','2.0','0.5'])
        result=json.loads(self.store.read('incar')[0])
        self.assertEqual(result['categories'],config['categories'])
        self.assertEqual(result['elements']['mag_value']['Og'],config['elements']['mag_value']['Og'])
        new=ET.fromstring(self.store.read('elements')[0])
        for a,b in zip(original.findall('./array/set/r'),new.findall('./array/set/r')):
            self.assertEqual(a.text.split()[3],b.text.split()[3])
            if a.text.split()[0].isdigit():self.assertEqual(a.text,b.text)
        rows=[row[:] for row in self.data.rows]; rows[0][8]=''
        self.data.save(rows)
        self.assertNotIn('H',json.loads(self.store.read('incar')[0])['elements']['u_value'])

    def test_invalid_and_conflicting_edits_do_not_write(self):
        before={key:self.store.read(key)[1] for key in ('elements','incar')}
        for col,value in [(2,'0'),(4,'256'),(5,'1.5'),(6,'-1'),(7,'nan'),(8,'oops')]:
            rows=[row[:] for row in self.data.rows];rows[0][col]=value
            with self.assertRaises(ValueError):self.data.save(rows)
            for key in before:self.assertEqual(self.store.read(key)[1],before[key])
        self.store.path('incar').write_bytes(before['incar']+b'\n')
        with self.assertRaises(ValueError):self.data.save(self.data.rows)

    def test_rgb_conversion_preserves_unedited_precision(self):
        self.assertEqual(self.data.rows[0][4:7],['255','255','255'])
        before=ET.fromstring(self.store.read('elements')[0])
        rows=[row[:] for row in self.data.rows]; rows[0][2]='1.02'
        self.data.save(rows)
        after=ET.fromstring(self.store.read('elements')[0])
        for a,b in zip(before.findall('./array/set/r'),after.findall('./array/set/r')):
            self.assertEqual(a.text.split()[4:7],b.text.split()[4:7])
        rows=[row[:] for row in self.data.rows]; rows[0][4:7]=['0','128','255']
        self.data.save(rows)
        self.assertEqual(self.data.rows[0][4:7],['0','128','255'])
        root=ET.fromstring(self.store.read('elements')[0])
        h=next(node for node in root.findall('./array/set/r') if node.text.split()[0]=='H')
        self.assertEqual(float(h.text.split()[4]),0)
        self.assertAlmostEqual(float(h.text.split()[5]),128/255)
        self.assertEqual(float(h.text.split()[6]),1)

    def test_second_write_failure_rolls_back_first(self):
        before={key:self.store.read(key)[1] for key in ('elements','incar')}
        rows=[row[:] for row in self.data.rows];rows[0][2]='1.01';rows[0][7]='2'
        save=self.store.save
        def fail(key,*args):
            if key=='incar':raise PermissionError('read only')
            return save(key,*args)
        with patch.object(self.store,'save',side_effect=fail):
            with self.assertRaises(PermissionError):self.data.save(rows)
        for key in before:self.assertEqual(self.store.read(key)[1],before[key])

if __name__=='__main__':unittest.main()

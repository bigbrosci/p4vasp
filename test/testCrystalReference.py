"""Offline phase conditions and separation from isolated-atom generation."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from p4vasp.atomic_reference import crystal_reference, _crystals
from p4vasp.element_data import SYMBOLS
from p4vasp.single_atom_inputs import input_contents

class CrystalReference(unittest.TestCase):
    def test_reviewed_records(self):
        records={s:crystal_reference(s) for s in SYMBOLS}
        self.assertEqual(sum(bool(v) for v in records.values()),83)
        for symbol,record in records.items():
            if not record:continue
            self.assertIn(record['ambient_phase'],('Solid','Liquid','Gas'))
            for key in ('structure','conditions','url'):self.assertTrue(record[key],symbol)
            self.assertTrue(record['url'].startswith('https://'))
        self.assertIn('fcc',records['Cu']['structure'])
        self.assertIn('bcc',records['Fe']['structure'])
        self.assertIn('hcp',records['Mg']['structure'])
        self.assertIn('graphite',records['C']['structure'])
        self.assertIn('Diamond',records['Ge']['structure'])
        self.assertIn('cI58',records['Mn']['structure'])
        self.assertIn('Rhombohedral',records['Bi']['structure'])
        self.assertIn('double',records['La']['structure'])
        self.assertIn('35.6',records['N']['conditions'])
        self.assertIn('molecular',records['N']['structure'])
        self.assertIn('25 bar',records['He']['conditions'])
        self.assertIn('No ambient-pressure solid',records['He']['structure'])
        self.assertEqual(records['Br']['ambient_phase'],'Liquid')
        self.assertEqual(records['Og'],{})
        self.assertEqual(records['Rn']['structure'],'Unknown')
        records['Cu']['structure']='changed'
        self.assertIn('fcc',crystal_reference('Cu')['structure'])

    def test_missing_and_corrupt_data(self):
        with tempfile.TemporaryDirectory() as root:
            with patch('p4vasp.p4vasp_home',root):
                self.assertEqual(crystal_reference('Cu'),{})
                path=Path(root)/'data/resources/crystal_states.json';path.parent.mkdir(parents=True)
                for text in ('not json','[]',json.dumps({'elements':[]})):
                    path.write_text(text);_crystals.cache_clear()
                    self.assertEqual(crystal_reference('Cu'),{})
        _crystals.cache_clear()

    def test_reference_not_used_for_atomic_inputs(self):
        before=input_contents('Cu')
        with patch('p4vasp.atomic_reference._crystals',return_value={'Cu':{'structure':'bcc'}}):
            self.assertEqual(input_contents('Cu'),before)

if __name__=='__main__':unittest.main()

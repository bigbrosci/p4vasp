"""Generated scientific inputs, default precedence and filesystem protection."""
from io import StringIO
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from p4vasp.single_atom_inputs import input_contents, write_inputs, destination
from p4vasp.incar_generator import load_presets, parse_custom
from p4vasp.Structure import Structure

class SingleAtomInputs(unittest.TestCase):
    def test_all_elements_centered_in_physical_cell(self):
        from p4vasp.element_data import SYMBOLS
        for symbol in SYMBOLS:
            files=input_contents(symbol)
            self.assertEqual(set(files),{'INCAR','KPOINTS','POSCAR'})
            structure=Structure();structure.read(StringIO(files['POSCAR']))
            self.assertEqual(len(structure),1)
            self.assertEqual(structure.info.getRecord(0).element,symbol)
            self.assertEqual([list(row) for row in structure.basis],[[13,0,0],[0,14,0],[0,0,15]])
            self.assertEqual(list(structure[0]),[.5,.5,.5])
            structure.setCarthesian();self.assertEqual(list(structure[0]),[6.5,7,7.5])
            self.assertEqual(files['KPOINTS'].splitlines()[1:],['0','Gamma','1 1 1','0 0 0'])

    def test_incar_uses_internal_standards_and_required_overrides(self):
        config=load_presets();config['standard']['d_elec']['MAGMOM']='99'
        config['standard']['d_elec']['ENCUT']='555'
        params=parse_custom(input_contents('Fe',config)['INCAR'])
        self.assertEqual(params['ISPIN'],'2');self.assertEqual(params['ALGO'],'ALL');self.assertEqual(params['NELM'],'500')
        self.assertNotIn('MAGMOM',params)
        for group in config['standard'].values():
            for tag,value in group.items():
                if tag not in ('SYSTEM','ISPIN','ALGO','NELM','MAGMOM'):self.assertEqual(params[tag],str(value))
        self.assertEqual(config['standard']['d_elec']['MAGMOM'],'99')

    def test_explicit_spin_charge_and_cell(self):
        files=input_contents('Cu',settings=dict(ispin=2,charge=1,zval=11,nupdown=0,cell=[16,17,18]))
        params=parse_custom(files['INCAR'])
        self.assertEqual(params['NELECT'],'10');self.assertEqual(params['NUPDOWN'],'0');self.assertEqual(params['MAGMOM'],'0')
        structure=Structure();structure.read(StringIO(files['POSCAR']))
        self.assertEqual([list(row) for row in structure.basis],[[16,0,0],[0,17,0],[0,0,18]])
        self.assertEqual(list(structure[0]),[.5,.5,.5])
        self.assertEqual(parse_custom(input_contents('Cu',settings=dict(charge=-1,zval=11))['INCAR'])['NELECT'],'12')
        self.assertIn('NELECT = SET_AFTER_POTCAR',input_contents('O',settings={'charge':-1})['INCAR'])
        neutral=parse_custom(input_contents('O',settings=dict(ispin=1))['INCAR'])
        self.assertNotIn('MAGMOM',neutral);self.assertNotIn('NELECT',neutral);self.assertNotIn('NUPDOWN',neutral)
        config=load_presets();config['standard']['d_elec'].update(NELECT=99,NUPDOWN=10,LSORBIT='.TRUE.')
        params=parse_custom(input_contents('Cu',config)['INCAR'])
        self.assertNotIn('NELECT',params);self.assertNotIn('NUPDOWN',params);self.assertNotIn('LSORBIT',params)

    def test_invalid_atomic_settings(self):
        for settings in ({'charge':'1.5'},{'ispin':3},{'ispin':1,'magmom':1},{'cell':[1,0,3]},
                         {'magmom':'nan'},{'zval':30},{'zval':11,'nupdown':2},
                         {'nupdown':1,'magmom':2},{'nupdown':-1},{'cell':[1,2]}):
            with self.subTest(settings=settings),self.assertRaises(ValueError):input_contents('Cu',settings=settings)
        with self.assertRaises(ValueError):input_contents('H',settings={'charge':1})

    def test_offline_reference_provenance_and_missing_spin(self):
        import json,runpy
        from p4vasp.atomic_reference import reference
        root=Path(__file__).resolve().parents[1]
        importer=runpy.run_path(str(root/'tools/import_atomic_reference.py'))
        data=importer['convert'](root/'data/resources/atomic_states_source.txt')
        self.assertEqual(data,json.loads((root/'data/resources/atomic_states.json').read_text()))
        self.assertEqual(len(data['elements']),108)
        import re
        cores={'Ne':10,'Ar':18,'Kr':36,'Cd':48,'Xe':54,'Hg':80,'Rn':86}
        for symbol,record in data['elements'].items():
            configuration=record['configuration']
            core=re.match(r'\[([A-Za-z]+)\]',configuration)
            count=cores[core[1]] if core else 0
            for n,l,occupation in re.findall(r'(\d)([spdfgh])(?:\^(\d+))?',configuration):
                occupied=int(occupation or 1)
                self.assertLessEqual(occupied,2*(2*'spdfgh'.index(l)+1))
                count+=occupied
            self.assertEqual(count,record['number'],symbol)
            if record['multiplicity'] is not None:
                self.assertEqual((count-record['multiplicity']+1)%2,0,symbol)

        self.assertEqual(reference('Cu')['multiplicity'],2);self.assertEqual(reference('Cr')['spin'],3)
        self.assertEqual(reference('Fe')['multiplicity'],5)
        self.assertIsNone(reference('Pb')['spin']);self.assertIsNone(reference('Hs')['multiplicity'])
        self.assertNotIn('configuration',reference('Og'))

    def test_new_folder_and_existing_files_preserved(self):
        with tempfile.TemporaryDirectory() as root:
            path=write_inputs('O',root,'oxygen')
            before={file.name:file.read_bytes() for file in path.iterdir()}
            self.assertEqual(set(before),{'INCAR','KPOINTS','POSCAR'})
            with self.assertRaises(FileExistsError):write_inputs('H',root,'oxygen')
            self.assertEqual(before,{file.name:file.read_bytes() for file in path.iterdir()})

    def test_invalid_name_parent_and_symbol(self):
        with tempfile.TemporaryDirectory() as root:
            for name in ('','..','../bad','a/b','a\\b','CON','x?','end.'):
                with self.assertRaises(ValueError):destination(root,name)
            with self.assertRaises(ValueError):destination(Path(root)/'missing','a')
            with self.assertRaises(ValueError):write_inputs('Unknown',root,'a')
            self.assertEqual(list(Path(root).iterdir()),[])

    def test_mid_write_failure_cleans_new_output(self):
        with tempfile.TemporaryDirectory() as root:
            original=Path.open
            def fail(path,*args,**kwargs):
                if path.name=='KPOINTS':raise OSError('disk full')
                return original(path,*args,**kwargs)
            with patch.object(Path,'open',fail):
                with self.assertRaises(OSError):write_inputs('Fe',root,'failed')
            self.assertFalse((Path(root)/'failed').exists())

if __name__=='__main__':unittest.main()

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

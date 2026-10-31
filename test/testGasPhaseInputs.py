"""XYZ diagnostics, geometry retention, spin/charge and export safety."""
from io import StringIO
from pathlib import Path
import math
import tempfile
import unittest
from p4vasp.gas_phase_inputs import read_xyz, scan_library, suggested_cell, poscar, input_contents, write_inputs
from p4vasp.incar_generator import parse_custom
from p4vasp.Structure import Structure

class GasInputs(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.path=self.root/'complex.xyz'
        self.path.write_text('4\nname="Two fragments" charge=0 multiplicity=1 units=angstrom\nH 101 200 300\nO 102 201 300\nH 110 200 302\nCu 104 205 300\n')
        self.molecule=read_xyz(self.path)

    def test_metadata_missing_and_bundled_examples(self):
        self.assertEqual(self.molecule.name,'Two fragments')
        self.assertEqual(self.molecule.charge,0);self.assertEqual(self.molecule.multiplicity,1)
        self.path.write_text('1\nCustom comment\nFe 0 0 0\n')
        molecule=read_xyz(self.path)
        self.assertIsNone(molecule.charge);self.assertIsNone(molecule.multiplicity)
        with self.assertRaises(ValueError):input_contents(molecule,'','',suggested_cell(molecule))
        root=Path(__file__).resolve().parents[1]/'data/models/gas_phase'
        self.assertEqual(len(scan_library(root)),2)
        self.assertEqual(read_xyz(root/'oxygen_triplet.xyz').multiplicity,3)

    def test_line_diagnostics_and_partial_library_errors(self):
        cases=[('x\n\n',1),('2\n\nH 0 0 0',4),('1\nunits=bohr\nH 0 0 0',2),
               ('1\ncharge=0 charge=1\nH 0 0 0',2),('1\nmultiplicty=1\nH 0 0 0',2),
               ('1\n\nXx 0 0 0',3),('1\n\nH nan 0 0',3),('1\n\nH 0 0',3),
               ('1\n\nH 0 0 0\n1\n\nH 1 0 0',4)]
        bad=self.root/'bad.XYZ'
        for text,line in cases:
            bad.write_text(text)
            with self.assertRaisesRegex(ValueError,r'bad.XYZ:%d:'%line):read_xyz(bad)
        rows=scan_library(self.root)
        self.assertEqual(len(rows),2);self.assertIsNone(rows[0][1]);self.assertIsNotNone(rows[1][1])

    def test_grouping_translation_and_all_pair_distances(self):
        cell=suggested_cell(self.molecule)
        s=Structure();s.read(StringIO(poscar(self.molecule,cell)))
        self.assertEqual(s.info.atomspertype,[2,1,1]);self.assertEqual(len(s),4)
        original=[self.molecule.positions[i] for i in (0,2,1,3)]
        for i in range(4):
            for j in range(4):self.assertAlmostEqual(math.dist(original[i],original[j]),math.dist(s[i],s[j]))
        for axis in range(3):self.assertAlmostEqual((min(p[axis] for p in s)+max(p[axis] for p in s))/2,cell[axis]/2)
        with self.assertRaises(ValueError):poscar(self.molecule,(1,1,1))
        with self.assertRaises(ValueError):poscar(self.molecule,(float('nan'),14,15))
        self.assertEqual(self.molecule.positions[0],(101,200,300))

    def test_spin_charge_and_no_guessed_nelect(self):
        params=parse_custom(input_contents(self.molecule,0,3,suggested_cell(self.molecule))['INCAR'])
        self.assertEqual(params['NUPDOWN'],'2');self.assertEqual(params['ISPIN'],'2')
        self.assertNotIn('MAGMOM',params);self.assertNotIn('NELECT',params)
        self.assertEqual(params['SIGMA'],'0.01')
        for charge in (-1,1):
            text=input_contents(self.molecule,charge,2,suggested_cell(self.molecule))['INCAR']
            params=parse_custom(text)
            self.assertEqual(params['NELECT'],'SET_AFTER_POTCAR')
            self.assertEqual(params['NUPDOWN'],'1')
            self.assertIn('POTCAR ZVAL) - (%+d)'%charge,text)
            self.assertIn('before running VASP',text)

    def test_write_conflict_and_source_change(self):
        output=write_inputs(self.molecule,0,1,suggested_cell(self.molecule),self.root,'out')
        self.assertEqual({p.name for p in output.iterdir()},{'INCAR','KPOINTS','POSCAR'})
        self.assertEqual((output/'KPOINTS').read_text().splitlines()[3],'1 1 1')
        with self.assertRaises(FileExistsError):write_inputs(self.molecule,0,1,suggested_cell(self.molecule),self.root,'out')
        self.path.write_text(self.path.read_text().replace('101 200','102 200'))
        with self.assertRaisesRegex(ValueError,'changed'):write_inputs(self.molecule,0,1,(20,20,20),self.root,'new')
        self.assertFalse((self.root/'new').exists())

if __name__=='__main__':unittest.main()

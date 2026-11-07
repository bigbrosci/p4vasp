"""Real optional ASE worker: geometry, cell policy, errors and legacy dispatch."""
from pathlib import Path
import tempfile
import subprocess
import unittest
from unittest.mock import patch
from p4vasp.SystemPM import getSystem, ASESystemPM, PoscarSystemPM, XMLSystemPM, DoscarSystemPM


class AseImportTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='ASE import ')
        self.root = Path(self.temporary.name)
        self.addCleanup(self.temporary.cleanup)

    def write(self, name, text):
        path = self.root/name
        path.write_text(text)
        return path

    def test_xyz_box_atom_order_last_frame_and_no_overwrite(self):
        text = '1\nfirst\nHe 0 0 0\n3\nlast\nH -3 5 -1\nO 1 6 2\nH 0 4 0\n'
        path = self.write('molecule @test.XYZ', text)
        s = getSystem(path)
        self.assertIsInstance(s, ASESystemPM)
        structure = s.INITIAL_STRUCTURE
        structure.setCartesian()
        self.assertEqual(len(structure), 3)
        self.assertEqual([structure.getRecordForAtom(i).element.strip() for i in range(3)], ['H','O','H'])
        for axis, length in enumerate((24,22,23)):
            self.assertAlmostEqual(structure.basis[axis][axis], length)
            self.assertAlmostEqual(min(p[axis] for p in structure), 10)
            self.assertAlmostEqual(max(p[axis] for p in structure), length-10)
        self.assertTrue(s.ASE_IMPORT_INFO['boxed'])
        self.assertEqual(s.URL, str(path))
        self.assertEqual(path.read_text(), text)
        self.assertEqual({p.name for p in self.root.iterdir()}, {path.name})

    def test_extxyz_preserves_cell_and_positions(self):
        path = self.write('periodic.extxyz', '2\nLattice="4 0 0 1 5 0 0 0 6" Properties=species:S:1:pos:R:3 pbc="T T T"\nCu -1 2 3\nCu 2 3 4\n')
        s = getSystem(path); structure = s.INITIAL_STRUCTURE; structure.setCartesian()
        self.assertFalse(s.ASE_IMPORT_INFO['boxed'])
        self.assertEqual(s.ASE_IMPORT_INFO['cell'], [[4,0,0],[1,5,0],[0,0,6]])
        for actual, expected in zip(structure[0], [-1,2,3]):self.assertAlmostEqual(actual, expected)

    def test_single_atom_and_cif(self):
        s = getSystem(self.write('one.xyz','1\natom\nHe 100 -50 7\n'))
        self.assertEqual(s.ASE_IMPORT_INFO['cell'], [[20,0,0],[0,20,0],[0,0,20]])
        self.assertEqual(list(s.INITIAL_STRUCTURE[0]), [10,10,10])
        cif = 'data_test\n_cell_length_a 4\n_cell_length_b 5\n_cell_length_c 6\n_cell_angle_alpha 90\n_cell_angle_beta 90\n_cell_angle_gamma 90\nloop_\n_atom_site_label\n_atom_site_type_symbol\n_atom_site_fract_x\n_atom_site_fract_y\n_atom_site_fract_z\nCu1 Cu 0.25 0.5 0.5\n'
        s = getSystem(self.write('crystal.cif', cif))
        self.assertFalse(s.ASE_IMPORT_INFO['boxed'])
        self.assertEqual(len(s.INITIAL_STRUCTURE),1)

    def test_errors_and_legacy_dispatch(self):
        for name, text in [('bad.xyz','2\nbad\nH 0 0 0\n'),('nan.xyz','1\nbad\nH nan 0 0\n'),('empty.xyz','0\nempty\n'),
                           ('partial.extxyz','1\nLattice="4 0 0 0 0 0 0 0 0"\nH 0 0 0\n')]:
            with self.subTest(name=name), self.assertRaises(RuntimeError):getSystem(self.write(name,text))
        self.assertIsInstance(getSystem(self.root/'POSCAR'),PoscarSystemPM)
        self.assertIsInstance(getSystem(self.root/'vasprun.xml'),XMLSystemPM)
        self.assertIsInstance(getSystem(self.root/'DOSCAR'),DoscarSystemPM)
        from p4vasp.ase_import import load_structure
        with patch('p4vasp.ase_bulk.worker_command',return_value=['/bin/false','unused','--worker']):
            with self.assertRaisesRegex(RuntimeError,'install-ase.sh'):load_structure(self.root/'one.xyz')

    def test_other_advertised_formats(self):
        from p4vasp.ase_bulk import worker_command
        # Fixture writers run in the same optional ASE environment, not GTK.
        script = "from ase import Atoms; from ase.io import write; import sys; from pathlib import Path; a=Atoms('He',positions=[[1,2,3]],cell=[4,5,6],pbc=True); [(write(str(Path(sys.argv[1])/('test.'+ext)),a,format=fmt)) for ext,fmt in [('pdb','proteindatabank'),('xsf','xsf'),('traj','traj')]]"
        subprocess.run([worker_command()[0],'-c',script,str(self.root)],check=True)
        mol='Helium\n  synthetic\n\n  1  0  0  0  0  0            999 V2000\n    1.0000    2.0000    3.0000 He  0  0  0  0  0  0  0  0  0  0  0  0\nM  END\n'
        self.write('test.mol',mol);self.write('test.sdf',mol+'$$$$\n')
        for ext in ('pdb','xsf','traj','mol','sdf'):
            with self.subTest(extension=ext):
                s=getSystem(self.root/('test.'+ext))
                self.assertEqual(len(s.INITIAL_STRUCTURE),1)
                self.assertEqual(s.ASE_IMPORT_INFO['boxed'],ext in ('mol','sdf'))


if __name__ == '__main__':unittest.main()

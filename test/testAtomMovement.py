"""Physical step, coordinate preservation, flags and save-roundtrip checks."""
from io import StringIO
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'lib'))
from p4vasp.Structure import Structure
from p4vasp.atom_movement import move_selected


class Movement(unittest.TestCase):
    def structure(self, mode='Direct', scale='1'):
        s=Structure()
        s.read(StringIO('test\n'+scale+'\n3 0 0\n1 4 0\n0 1 5\nH\n2\nSelective dynamics\n'+mode+'\n0.1 0.2 0.3 F T F\n0.5 0.6 0.7 T F T\n'))
        return s

    def physical(self, source):
        s=Structure(source);s.setDirect();s.correctScaling();s.setCarthesian()
        return [list(v) for v in s]

    def test_step_and_poscar_flags_in_all_coordinate_scales(self):
        for mode in ['Direct','Cartesian']:
            for scale in ['1','2','-60','2 3 4']:
                with self.subTest(mode=mode,scale=scale):
                    s=self.structure(mode,scale)
                    before=self.physical(s)
                    basis=[list(v) for v in s.basis];scaling=s.scaling[:]
                    flags=[list(v) for v in s.selective]
                    self.assertTrue(move_selected(s,[0,0],(1,0,0)))
                    after=self.physical(s)
                    self.assertAlmostEqual(after[0][0]-before[0][0],.1)
                    for j in [1,2]:self.assertAlmostEqual(after[0][j],before[0][j])
                    for j in range(3):self.assertAlmostEqual(after[1][j],before[1][j])
                    self.assertEqual(s.isDirect(),mode=='Direct')
                    self.assertEqual([list(v) for v in s.basis],basis)
                    self.assertEqual(s.scaling,scaling)
                    output=StringIO();s.write(output)
                    restored=Structure();restored.read(StringIO(output.getvalue()))
                    self.assertEqual([list(v) for v in restored.selective],flags)

    def test_no_selection_or_stale_index_does_not_change_structure(self):
        s=self.structure();before=self.physical(s)
        self.assertFalse(move_selected(s,[],(1,0,0)))
        self.assertFalse(move_selected(s,[0,99],(1,0,0)))
        self.assertEqual(self.physical(s),before)

    def test_configured_step_and_rigid_group_translation(self):
        s=self.structure()
        before=self.physical(s)
        move_selected(s,[0,1],(1,2,2),.3)
        after=self.physical(s)
        for i in range(2):
            for j,delta in enumerate([.1,.2,.2]):self.assertAlmostEqual(after[i][j]-before[i][j],delta)


if __name__=='__main__':unittest.main()

"""Physical step, coordinate preservation, flags and save-roundtrip checks."""
from io import StringIO
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'lib'))
from p4vasp.Structure import Structure
from p4vasp.atom_movement import move_selected, rotate_selected
import math


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

    def mixed(self):
        s=Structure()
        s.read(StringIO('mixed\n1\n10 0 0\n0 10 0\n0 0 10\nH He C\n1 1 1\nSelective dynamics\nCartesian\n0 0 0 F T F\n2 0 0 T F T\n7 8 9 F F F\n'))
        for record,mass in zip(s.info,[1.,3.,12.]):record.mass=mass
        return s

    def test_true_mass_center_not_geometric_center(self):
        s=self.mixed()
        center=rotate_selected(s,[0,1,0],(0,0,1),90)
        for a,b in zip(center,(1.5,0,0)):self.assertAlmostEqual(a,b)
        expected=[(1.5,-1.5,0),(1.5,.5,0),(7,8,9)]
        for actual,target in zip(s,expected):
            for a,b in zip(actual,target):self.assertAlmostEqual(a,b)
        self.assertAlmostEqual((s[1]-s[0]).length(),2.)
        rotate_selected(s,[0,1],(0,0,-1),90)
        for a,b in zip(s[0],(0,0,0)):self.assertAlmostEqual(a,b)
        for a,b in zip(s[1],(2,0,0)):self.assertAlmostEqual(a,b)

    def test_five_degrees_preserves_mass_center_cell_and_flags(self):
        for mode in ['Direct','Cartesian']:
            for scale in ['1','2','-60','2 3 4']:
                s=self.structure(mode,scale)
                s.info[0].mass=2.
                before=self.physical(s)
                center=[(before[0][j]+before[1][j])/2 for j in range(3)]
                basis=[list(v) for v in s.basis];flags=[list(v) for v in s.selective]
                result=rotate_selected(s,[0,1],(0,0,1))
                after=self.physical(s)
                for j in range(3):
                    self.assertAlmostEqual(result[j],center[j])
                    self.assertAlmostEqual((after[0][j]+after[1][j])/2,center[j])
                radius=[before[0][j]-center[j] for j in range(3)]
                angle=math.radians(5)
                self.assertAlmostEqual(after[0][0]-center[0],math.cos(angle)*radius[0]-math.sin(angle)*radius[1])
                self.assertAlmostEqual(after[0][1]-center[1],math.sin(angle)*radius[0]+math.cos(angle)*radius[1])
                self.assertEqual([list(v) for v in s.basis],basis)
                self.assertEqual([list(v) for v in s.selective],flags)
                self.assertEqual(s.isDirect(),mode=='Direct')

    def test_missing_mass_aborts_without_changes(self):
        s=self.mixed();s.info[1].element='UnknownElement';s.info[1].mass=0.
        before=[list(v) for v in s]
        with self.assertRaisesRegex(ValueError,'mass'):rotate_selected(s,[0,1],(1,0,0))
        self.assertEqual([list(v) for v in s],before)

    def test_single_atom_and_table_mass_fallback(self):
        s=self.mixed();s.info[0].mass=0.
        before=list(s[0])
        self.assertEqual(rotate_selected(s,[0],(1,0,0)),tuple(before))
        self.assertEqual(list(s[0]),before)
        self.assertIsNone(rotate_selected(s,[],(1,0,0)))


if __name__=='__main__':unittest.main()

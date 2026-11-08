"""Replica geometry and bonds, independent of GTK and user calculation files."""
import copy
import unittest
from p4vasp.periodic_preview import geometry,bonds,MAX_DISPLAY_ATOMS


class PeriodicPreviewTest(unittest.TestCase):
    def test_boundary_bond_and_replica_offsets(self):
        positions=[[.1,1,1],[9.5,1,1]];original=copy.deepcopy(positions)
        cell=[[10,0,0],[0,8,0],[0,0,12]]
        indices,offsets,points,edges=geometry(positions,cell,(2,1,1))
        self.assertEqual(indices,[0,1,0,1]);self.assertEqual(points[2],[10.1,1,1])
        self.assertEqual(len(edges),20)
        self.assertIn((2,1),bonds(points,[.32]*4))
        self.assertEqual(bonds(points[:2],[.32]*2),[])
        self.assertEqual(positions,original)
        moved=[[p[0]+.2,p[1]-.1,p[2]] for p in positions]
        display=[[moved[i][j]+offset[j] for j in range(3)] for i,offset in zip(indices,offsets)]
        for before,after in zip(points,display):self.assertAlmostEqual(after[0]-before[0],.2)

    def test_skew_cell_and_unwrapped_atoms(self):
        cell=[[4,0,0],[2,3,0],[1,1,5]]
        positions=[[-2.9,-.3,1], [7.1,-.3,1]]
        indices,offsets,points,edges=geometry(positions,cell,(1,2,3))
        self.assertEqual(len(points),12)
        self.assertEqual(len(geometry(positions,cell,(1,1,1))[3]),12)
        self.assertIn(([7,9,15],[11,9,15]),edges)
        # All changes are lattice translations, preserving each input atom.
        for index,offset,point in zip(indices,offsets,points):
            self.assertEqual(point,[positions[index][j]+offset[j] for j in range(3)])

    def test_display_limits(self):
        cell=[[1,0,0],[0,1,0],[0,0,1]]
        for repeat in ((0,1,1),(6,1,1),(1.5,1,1)):
            with self.assertRaises(ValueError):geometry([[0,0,0]],cell,repeat)
        with self.assertRaises(ValueError):geometry([[0,0,0]]*(MAX_DISPLAY_ATOMS//2+1),cell,(2,1,1))
        with self.assertRaises(ValueError):geometry([[0,0,0]],[[0,0,0]]*3,(1,1,1))

if __name__=='__main__':unittest.main()

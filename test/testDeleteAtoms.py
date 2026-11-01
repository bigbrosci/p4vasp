"""Delete deduplication, stale protection and POSCAR metadata preservation."""
from io import StringIO
import unittest
from p4vasp.Structure import Structure
from p4vasp.atom_movement import delete_selected

class Delete(unittest.TestCase):
    def structure(self):
        s=Structure();s.read(StringIO('delete\n2\n4 0 0\n0 5 0\n0 0 6\nCu C Cu H\n2 1 1 2\nSelective dynamics\nDirect\n0 0 0 T F T\n.1 0 0 F T F\n.2 0 0 T T F\n.3 0 0 F F T\n.4 0 0 T F F\n.5 0 0 F T T\n'))
        return s

    def test_deduplicated_remove_and_saved_species_flags(self):
        s=self.structure();basis=[list(v) for v in s.basis];scaling=s.scaling[:]
        positions=[list(v) for v in s];flags=[list(v) for v in s.selective]
        self.assertTrue(delete_selected(s,[1,1,4],6))
        self.assertEqual([list(v) for v in s],[positions[i] for i in (0,2,3,5)])
        self.assertEqual([list(v) for v in s.selective],[flags[i] for i in (0,2,3,5)])
        self.assertEqual([list(v) for v in s.basis],basis);self.assertEqual(s.scaling,scaling)
        self.assertTrue(s.isDirect());self.assertEqual(s.atomspertype,[1,1,1,1])
        text=StringIO();s.write(text);new=Structure();new.read(StringIO(text.getvalue()))
        self.assertEqual(len(new),4);self.assertEqual([list(v) for v in new.selective],[list(v) for v in s.selective])

    def test_stale_and_invalid_requests_are_atomic(self):
        s=self.structure();before=s.toString()
        for indices,count in [([],6),([0,99],6),([-1],6),([0],5)]:
            self.assertFalse(delete_selected(s,indices,count));self.assertEqual(s.toString(),before)
        self.assertTrue(delete_selected(s,[0],6));after=s.toString()
        self.assertFalse(delete_selected(s,[0],6));self.assertEqual(s.toString(),after)

    def test_delete_species_and_all_atoms(self):
        s=self.structure();self.assertTrue(delete_selected(s,[2]))
        self.assertEqual(s.atomspertype,[2,1,2])
        self.assertEqual([r.element.strip() for r in s.info],['Cu','Cu','H'])
        self.assertTrue(delete_selected(s,range(5),5))
        self.assertEqual(len(s),0);self.assertEqual(len(s.info),0);self.assertEqual(len(s.selective),0)

if __name__=='__main__':unittest.main()

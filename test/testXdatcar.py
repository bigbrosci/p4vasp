"""XDATCAR trajectory indexing, endpoints and malformed-input checks."""
from pathlib import Path
import tempfile
import unittest
from p4vasp.xdatcar import XdatcarSequence
from p4vasp.SystemPM import getSystem,XdatcarSystemPM

HEADER='trajectory\n1\n4 0 0\n1 5 0\n0 0 6\nC H\n1 1\n'
FRAMES=''.join('Direct configuration= %d\n%.3f 0 0\n0 .5 .5\n'%(i+1,i*.1) for i in range(3))

class XdatcarTest(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.path=Path(self.tmp.name)/'XDATCAR'
        self.path.write_text(HEADER+FRAMES)
    def test_frames_and_dispatch(self):
        s=getSystem(self.path);self.assertIsInstance(s,XdatcarSystemPM)
        q=s.STRUCTURE_SEQUENCE_L;self.assertEqual(len(q),3)
        self.assertAlmostEqual(q[1][0][0],.1)
        self.assertAlmostEqual(s.INITIAL_STRUCTURE[0][0],0)
        self.assertAlmostEqual(s.FINAL_STRUCTURE[0][0],.2)
        self.assertEqual(q[2].info[0].element.strip(),'C')
        self.assertAlmostEqual(q[0].basis[1][0],1)
        s.INITIAL_STRUCTURE[0][0]=.9
        self.assertEqual(q[0][0][0],0)
        with self.assertRaises(IndexError):q[3]
    def test_repeated_header_variable_cell(self):
        self.path.write_text(HEADER+FRAMES+HEADER.replace('4 0 0','8 0 0')+FRAMES)
        q=XdatcarSequence(self.path);self.assertEqual(len(q),6)
        self.assertEqual(q[3].basis[0][0],8)
    def test_vasp4_cartesian_and_errors(self):
        self.path.write_text(HEADER.replace('C H\n','')+FRAMES.replace('Direct','Cartesian'))
        q=XdatcarSequence(self.path);self.assertEqual(len(q),3)
        frame=q[1];frame.setDirect();self.assertAlmostEqual(frame[0][0],.025)
        for text in (HEADER,HEADER+FRAMES+'Direct configuration=4\n0 0 0\n',HEADER+FRAMES.replace('.5','nan',1)):
            self.path.write_text(text)
            with self.assertRaises(ValueError):XdatcarSequence(self.path)

if __name__=='__main__':unittest.main()

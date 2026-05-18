import unittest
from p4vasp.Structure import *
from io import *

class TestStructure(unittest.TestCase):
    def testParsingCell(self):
        f=StringIO("""test chgcar
1
1 2 3
4 5 6
7 8 9
1
cart
0 0 0
""")

        s=Structure()
        s.read(f)
        self.assertEqual(s.basis[0][0],1)
        self.assertEqual(s.basis[0][1],2)
        self.assertEqual(s.basis[0][2],3)
        self.assertEqual(s.basis[1][0],4)
        self.assertEqual(s.basis[1][1],5)
        self.assertEqual(s.basis[1][2],6)
        self.assertEqual(s.basis[2][0],7)
        self.assertEqual(s.basis[2][1],8)
        self.assertEqual(s.basis[2][2],9)
    def testReciprocalLattice(self):
        f=StringIO("""test chgcar
1
0 10 10
10 0 10
10 10 0
1
cart
0 0 0
""")

        s=Structure()
        s.read(f)
        s.updateRecipBasis()
        self.assertEqual(s.rbasis[0][0],-0.05)
        self.assertEqual(s.rbasis[0][1],0.05)
        self.assertEqual(s.rbasis[0][2],0.05)

        self.assertEqual(s.rbasis[1][0],0.05)
        self.assertEqual(s.rbasis[1][1],-0.05)
        self.assertEqual(s.rbasis[1][2],0.05)

        self.assertEqual(s.rbasis[2][0],0.05)
        self.assertEqual(s.rbasis[2][1],0.05)
        self.assertEqual(s.rbasis[2][2],-0.05)
    def testAppendAtom(self):
        s=Structure()
        self.assertEqual(len(s.info),0)
        self.assertEqual(len(s.positions),0)
        s.appendAtom(0,(1,2,3))
        self.assertEqual(len(s.info),1)
        self.assertEqual(len(s.positions),1)
        self.assertEqual(s[0][0],1)
        self.assertEqual(s[0][1],2)
        self.assertEqual(s[0][2],3)
        s.appendAtom(1,(4,5,6))
        self.assertEqual(len(s.info),2)
        self.assertEqual(len(s.positions),2)
        self.assertEqual(s[1][0],4)
        self.assertEqual(s[1][1],5)
        self.assertEqual(s[1][2],6)
        s.appendAtom(0,(7,8,9))
        self.assertEqual(len(s.info),2)
        self.assertEqual(len(s.positions),3)
        self.assertEqual(s[0][0],1)
        self.assertEqual(s[0][1],2)
        self.assertEqual(s[0][2],3)
        self.assertEqual(s[1][0],7)
        self.assertEqual(s[1][1],8)
        self.assertEqual(s[1][2],9)
        self.assertEqual(s[2][0],4)
        self.assertEqual(s[2][1],5)
        self.assertEqual(s[2][2],6)
    def testNewSpecie(self):
        s=Structure()
        self.assertEqual(len(s.info),0)
        self.assertEqual(len(s.positions),0)
        s.appendAtomOfNewSpecie((1,2,3))
        self.assertEqual(len(s.info),1)
        self.assertEqual(len(s.positions),1)
        self.assertEqual(s[0][0],1)
        self.assertEqual(s[0][1],2)
        self.assertEqual(s[0][2],3)
        s.appendAtomOfNewSpecie((4,5,6))
        self.assertEqual(len(s.info),2)
        self.assertEqual(len(s.positions),2)
        self.assertEqual(s[0][0],1)
        self.assertEqual(s[0][1],2)
        self.assertEqual(s[0][2],3)
        self.assertEqual(s[1][0],4)
        self.assertEqual(s[1][1],5)
        self.assertEqual(s[1][2],6)




if __name__ == '__main__':
    unittest.main()

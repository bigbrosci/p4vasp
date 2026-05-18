import unittest
from p4vasp.Selection import *

class TestSelection(unittest.TestCase):
    def testEncodeSimple(self):
        selection=Selection()
        self.assertEqual(selection.encodeSimple([(1,0,0,0)]),"2")

if __name__ == '__main__':
    unittest.main()

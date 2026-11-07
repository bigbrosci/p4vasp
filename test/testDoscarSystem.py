"""Standalone DOSCAR dispatch, Fermi energy and total spin-channel parsing."""
from io import StringIO
from pathlib import Path
import tempfile
import unittest
from p4vasp.SystemPM import readDOSCAR,getSystem,DoscarSystemPM,XMLSystemPM,PoscarSystemPM


def doscar(spin=False,scale=1,fermi=.5):
    rows=['-1 0 0','0 %g 1'% (4*scale),'1 %g 2'%scale]
    if spin:rows=['-1 1 2 3 4','0 4 5 6 7','1 8 9 10 11']
    return '1 1 1 0\n1 1 1 1 1\n300\nSynthetic\nDOSCAR test\n1 -1 3 %g 1\n'%fermi+'\n'.join(rows)+'\n'


class DoscarSystemTest(unittest.TestCase):
    def test_standalone_without_structure_or_incar(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'DOSCAR';path.write_text(doscar())
            system=getSystem(path)
            self.assertIsInstance(system,DoscarSystemPM)
            self.assertEqual(system.PATH,folder)
            self.assertEqual(system.URL,str(path))
            self.assertIn('DOSCAR',system.NAME)
            self.assertEqual(system.E_FERMI,.5)
            self.assertEqual(len(system.INITIAL_STRUCTURE),0)
            self.assertIsNotNone(system.INCAR)
            self.assertEqual(list(system.TOTAL_DOS[0][1]),[0.,4.,1.])
            path2=Path(folder)/'doscar';path2.write_text(doscar(scale=3))
            self.assertEqual(getSystem(path2).TOTAL_DOS[0][1][1],12.)
            self.assertIsInstance(getSystem(Path(folder)/'vasprun.xml'),XMLSystemPM)
            self.assertIsInstance(getSystem(Path(folder)/'POSCAR'),PoscarSystemPM)

    def test_spin_channels_and_projected_tail(self):
        stream=StringIO(doscar(spin=True)+'1 -1 3 .5\n0 100 200\n')
        data=readDOSCAR(stream)
        self.assertFalse(stream.closed)
        self.assertEqual(len(data),2)
        self.assertEqual(len(data[0]),3)
        self.assertEqual(list(data[0][1]),[0.,4.,6.])
        self.assertEqual(list(data[1][1]),[0.,5.,7.])
        readDOSCAR(StringIO(doscar()),closeflag=1)

    def test_reject_incomplete_inconsistent_or_invalid_rows(self):
        for text in ['', 'header\n',doscar().replace('1 -1 3 0.5','1 -1 0 0.5'),
                     doscar().rsplit('\n',2)[0]+'\n',doscar().replace('0 4 1','0 4 5 6 7')]:
            with self.subTest(text=text):
                with self.assertRaises(ValueError):readDOSCAR(StringIO(text))

if __name__=='__main__':unittest.main()

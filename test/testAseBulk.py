"""Actual ASE geometries and input validation, independent of GTK/native code."""
from io import StringIO
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from ase.io import read
from p4vasp.ase_bulk import build_bulk
from p4vasp.bulk_replay import bulk_contents
from p4vasp.single_atom_inputs import write_contents


def request(**kwargs):
    return dict(name='Cu', crystal='fcc', mode='primitive', a='3.6', repeat=[1,1,1], **kwargs)


class AseBulkTest(unittest.TestCase):
    def test_exported_bulk_replays_and_cli(self):
        root = Path(__file__).resolve().parents[1]
        env = dict(os.environ, P4VASP_HOME=str(root), P4VASP_ASE_PYTHON=sys.executable,
                   PYTHONPATH=str(root/'lib'), PYTHON=sys.executable, PATH=os.defpath)
        for key in ('DISPLAY', 'WAYLAND_DISPLAY'):
            env.pop(key, None)
        bulk_request = request()
        bulk_request.update(name='ZnS', crystal='wurtzite', a='3.82', c='6.26',
                            u='0.38', repeat=[2, 1, 3])
        result = build_bulk(bulk_request)
        with tempfile.TemporaryDirectory(prefix='bulk replay ') as temporary:
            directory = write_contents(bulk_contents(result), Path(temporary), 'exported bulk')
            for command, target in [
                ([sys.executable, '-I', str(directory/'rebuild_bulk.py'), '-o'], 'Python output'),
                (['bash', str(directory/'rebuild_bulk.sh')], 'Bash output'),
            ]:
                with self.subTest(target=target):
                    run = subprocess.run(command + [target], cwd=temporary, env=env,
                                         text=True, capture_output=True, timeout=40)
                    self.assertEqual(run.returncode, 0, run.stderr)
                    rebuilt = Path(temporary)/target
                    self.assertEqual(rebuilt.read_bytes(), (directory/'POSCAR').read_bytes())
                    run = subprocess.run(command + [target], cwd=temporary, env=env,
                                         text=True, capture_output=True, timeout=40)
                    self.assertNotEqual(run.returncode, 0)
                    self.assertEqual(rebuilt.read_bytes(), (directory/'POSCAR').read_bytes())
            cli = [sys.executable, str(root/'p4v.py'), 'bulk', 'Cu', 'fcc', 'cubic']
            run = subprocess.run(cli + ['--a', '3.615', '-o', 'POSCAR'], cwd=temporary,
                                 env=env, text=True, capture_output=True, timeout=40)
            self.assertEqual(run.returncode, 0, run.stderr)
            atoms = read(Path(temporary)/'POSCAR', format='vasp')
            self.assertEqual(len(atoms), 4)
            self.assertAlmostEqual(atoms.cell.lengths()[0], 3.615)
            run = subprocess.run(cli + ['--a', 'nan', '-o', 'invalid'], cwd=temporary,
                                 env=env, text=True, capture_output=True, timeout=40)
            self.assertNotEqual(run.returncode, 0)
            self.assertFalse((Path(temporary)/'invalid').exists())

    def test_fcc_cells_and_supercell_geometry(self):
        for mode, count in [('primitive',1),('orthorhombic',2),('cubic',4)]:
            q=request();q.update(mode=mode,repeat=[2,3,1])
            result=build_bulk(q)
            atoms=read(StringIO(result['poscar']),format='vasp')
            self.assertEqual(len(atoms),count*6)
            self.assertAlmostEqual(atoms.get_volume(),3.6**3*count/4*6)
            self.assertTrue(atoms.pbc.all())
            self.assertEqual(atoms.get_chemical_formula(),'Cu'+str(count*6))
            self.assertEqual(result['request'],q)

    def test_binary_stoichiometry_and_distance(self):
        q=request();q.update(name='NaCl',crystal='rocksalt',a='5.64',mode='cubic')
        atoms=read(StringIO(build_bulk(q)['poscar']),format='vasp')
        self.assertEqual(atoms.get_chemical_symbols().count('Na'),4)
        self.assertEqual(atoms.get_chemical_symbols().count('Cl'),4)
        na=atoms.get_chemical_symbols().index('Na');cl=atoms.get_chemical_symbols().index('Cl')
        distances=atoms.get_distances(na,[i for i,s in enumerate(atoms.symbols) if s=='Cl'],mic=True)
        self.assertAlmostEqual(min(distances),2.82)
        self.assertEqual(atoms.get_chemical_symbols(),sorted(atoms.get_chemical_symbols()))

    def test_hexagonal_and_rhombohedral_parameters(self):
        q=request();q.update(name='Ti',crystal='hcp',a='2.95',c='4.68')
        atoms=read(StringIO(build_bulk(q)['poscar']),format='vasp')
        self.assertEqual(len(atoms),2)
        self.assertAlmostEqual(atoms.cell.lengths()[2],4.68)
        self.assertAlmostEqual(atoms.cell.angles()[2],120)
        q.update(name='Bi',crystal='rhombohedral',alpha='75')
        atoms=read(StringIO(build_bulk(q)['poscar']),format='vasp')
        self.assertAlmostEqual(atoms.cell.angles()[0],75)

    def test_all_offered_prototypes(self):
        examples={'sc':'Cu','fcc':'Cu','bcc':'Fe','diamond':'Si','hcp':'Ti','bct':'Fe',
                  'rocksalt':'NaCl','zincblende':'ZnS','cesiumchloride':'CsCl',
                  'fluorite':'CaF2','wurtzite':'ZnS',
                  'orthorhombic':'Si','rhombohedral':'Bi'}
        for crystal,name in examples.items():
            with self.subTest(crystal=crystal):
                q=request();q.update(name=name,crystal=crystal,b='4',c='5',alpha='75',u='.375')
                result=build_bulk(q)
                atoms=read(StringIO(result['poscar']),format='vasp')
                self.assertGreater(len(atoms),0)
                self.assertGreater(atoms.get_volume(),0)

    def test_reject_invalid_scientific_inputs(self):
        for changes in [dict(a='nan'),dict(a='inf'),dict(a='0'),dict(a='-3'),dict(name='X'),
                dict(name='NoSuchElement'),dict(name='Cu999999999'),dict(name='Cu',crystal='rocksalt'),dict(crystal='hcp'),
                dict(crystal='hcp',c=4.6,mode='cubic'),dict(crystal='rhombohedral',alpha=120),
                dict(repeat=[0,1,1]),dict(repeat=[1.5,1,1]),dict(repeat=[True,1,1]),
                dict(repeat=[100,100,100]),dict(mode='bad'),dict(crystal='custom')]:
            with self.subTest(changes=changes):
                q=request();q.update(changes)
                with self.assertRaises((ValueError,RuntimeError)):build_bulk(q)
        q=request();q.update(mode='cubic',repeat=[20,20,20])
        with self.assertRaises(ValueError):build_bulk(q)


if __name__=='__main__':unittest.main()

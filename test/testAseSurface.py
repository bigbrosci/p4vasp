"""Scientific slab invariants with actual ASE; no user structures."""
from io import StringIO
import copy
import json
import math
from pathlib import Path
import subprocess
import tempfile
import unittest
import numpy as np
from ase.build import bulk
from ase.constraints import FixAtoms
from ase.io import read, write
from p4vasp.ase_surface import build_surface, parameters, PRESETS, reposition_result


class SurfaceTest(unittest.TestCase):
    def request(self,**changes):
        return dict(dict(source='preset',preset='fcc111',symbol='Cu',a=3.615,layers=4,
                         repeat=[2,2],vacuum=10,fixed_layers=2,layer_tolerance=.3),**changes)

    def check(self,result):
        atoms=read(StringIO(result['poscar']),format='vasp')
        self.assertEqual(len(atoms),result['atoms'])
        z=atoms.positions[:,2]
        self.assertAlmostEqual(z.min(),result['vacuum_bottom'],places=8)
        self.assertAlmostEqual(atoms.cell[2,2]-z.max(),result['vacuum_top'],places=8)
        self.assertTrue(np.allclose(np.cross(atoms.cell[0],atoms.cell[1])[:2],0,atol=1e-9))
        fixed={int(i) for con in atoms.constraints for i in con.get_indices()}
        expected={i for i,layer in enumerate(result['layer_numbers']) if layer<=result['request']['fixed_layers']}
        self.assertEqual(fixed,expected)
        self.assertEqual(len(fixed),result['fixed_atoms'])
        return atoms

    def test_fcc111_atomic_planes_spacing_vacuum_and_fixed_flags(self):
        request=self.request();original=copy.deepcopy(request)
        result=build_surface(request);atoms=self.check(result)
        self.assertEqual(result['atoms'],16);self.assertEqual(result['fixed_atoms'],8)
        self.assertEqual(result['geometric_layers'],4)
        levels=np.unique(np.round(atoms.positions[:,2],8))
        self.assertTrue(np.allclose(np.diff(levels),3.615/math.sqrt(3),atol=1e-7))
        self.assertEqual(request,original)

    def test_center_bottom_preserve_cell_distances_flags_and_source(self):
        centered=build_surface(self.request());original=copy.deepcopy(centered)
        atoms=self.check(centered)
        bottom=reposition_result(centered,'bottom');shifted=self.check(bottom)
        self.assertAlmostEqual(shifted.positions[:,2].min(),.1,places=12)
        self.assertAlmostEqual(bottom['vacuum_top'],19.9,places=10)
        self.assertIsNone(bottom['vacuum_each_side'])
        self.assertTrue(np.allclose(shifted.cell.array,atoms.cell.array,atol=1e-12))
        self.assertTrue(np.allclose(shifted.positions-atoms.positions,[0,0,-9.9],atol=1e-12))
        self.assertEqual(bottom['layer_numbers'],centered['layer_numbers'])
        self.assertEqual(centered,original)
        again=reposition_result(bottom,'bottom');self.check(again)
        self.assertTrue(np.allclose(read(StringIO(again['poscar']),format='vasp').positions,shifted.positions,atol=1e-12))
        # Independent ASE centering of the shifted slab is the Center oracle.
        shifted.center(axis=2)
        restored=self.check(reposition_result(bottom,'center'))
        self.assertTrue(np.allclose(restored.positions,shifted.positions,atol=1e-12))
        self.assertTrue(np.allclose(restored.positions,atoms.positions,atol=1e-12))
        generated=self.check(build_surface(self.request(placement='bottom')))
        self.assertTrue(np.allclose(generated.positions,read(StringIO(bottom['poscar']),format='vasp').positions,atol=1e-12))

    def test_bottom_rejects_insufficient_vacuum_without_modifying_result(self):
        result=build_surface(self.request(vacuum=.04));original=copy.deepcopy(result)
        with self.assertRaisesRegex(ValueError,'0.1'):reposition_result(result,'bottom')
        self.assertEqual(result,original)
        with self.assertRaises(ValueError):build_surface(self.request(placement='unknown'))

    def test_all_presets_and_zero_fixed_layers(self):
        for preset in PRESETS:
            with self.subTest(preset=preset):
                result=build_surface(self.request(preset=preset,c=5.9,fixed_layers=0))
                atoms=self.check(result)
                self.assertEqual(len(atoms),16)
                self.assertFalse(atoms.constraints)
                self.assertNotIn('Selective dynamics',result['poscar'])

    def test_bulk_input_negative_indices_and_normalization(self):
        atoms=bulk('Cu','fcc',a=3.615,cubic=True)
        atoms.set_constraint(FixAtoms(indices=list(range(len(atoms)))))
        stream=StringIO();write(stream,atoms,format='vasp',direct=True)
        source=stream.getvalue()
        result=build_surface(self.request(source='poscar',poscar=source,indices=[-2,2,2],repeat=[1,2],fixed_layers=1))
        self.check(result)
        self.assertEqual(result['atoms'],32)
        self.assertEqual(result['request']['indices'],[-1,1,1])
        self.assertEqual(source,stream.getvalue())
        # Original all-fixed bulk mask is replaced by the selected bottom rule.
        self.assertLess(result['fixed_atoms'],result['atoms'])

    def test_cif_import_mixed_species_and_portable_metadata(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'salt.cif'
            write(path,bulk('NaCl','rocksalt',a=5.64,cubic=True))
            before=path.read_bytes()
            result=build_surface(self.request(source='file',path=str(path),indices=[1,0,0],repeat=[1,1],layers=3,fixed_layers=1))
            atoms=self.check(result)
            self.assertEqual(set(atoms.get_chemical_symbols()),{'Na','Cl'})
            self.assertEqual(path.read_bytes(),before)
            self.assertNotIn('path',result['request'])
            replay=build_surface(result['request'])
            self.assertEqual(replay['poscar'],result['poscar'])

    def test_reject_invalid_or_excessive_models(self):
        for changes in ({'indices':[0,0,0],'source':'poscar','poscar':'x'}, {'layers':True},
                        {'repeat':[100,100]}, {'vacuum':0}, {'vacuum':float('nan')},
                        {'a':float('inf')}, {'vacuum':True}, {'a':True}, {'fixed_layers':4}):
            with self.subTest(changes=changes),self.assertRaises(ValueError):build_surface(self.request(**changes))
        molecule='H\n1\n1 0 0\n0 1 0\n0 0 1\nH\n1\nDirect\n0 0 0\n'
        with self.assertRaises(ValueError):build_surface(self.request(source='poscar',poscar=molecule,indices=[1,1,1],repeat=[100,100]))

    def test_worker_runs_without_gui_pythonpath(self):
        import os,sys
        env=dict(os.environ);env.pop('PYTHONPATH',None)
        script=Path(__file__).resolve().parents[1]/'lib/p4vasp/ase_surface.py'
        result=subprocess.run([sys.executable,str(script),'--worker'],input=json.dumps(self.request()),
                              env=env,capture_output=True,text=True,timeout=20)
        self.assertEqual(result.returncode,0,result.stderr+result.stdout)
        self.check(json.loads(result.stdout)['result'])
        # Exercise the same --surface JSON dispatcher used by future frozen workers.
        root=Path(__file__).resolve().parents[1]
        result=subprocess.run([sys.executable,str(root/'install/windows/model_worker.py'),'--surface'],
            input=json.dumps(self.request()),env=dict(env,PYTHONPATH=str(root/'lib')),
            capture_output=True,text=True,timeout=20)
        self.assertEqual(result.returncode,0,result.stderr+result.stdout)
        self.check(json.loads(result.stdout)['result'])


if __name__=='__main__':unittest.main()

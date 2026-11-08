"""Independent exported scripts reproduce ASE results without p4vasp or OUTCAR."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from vibration_fixtures import write_calculation
from p4vasp.vibrations import read_outcar,thermochemistry
from p4vasp.thermo_replay import save_thermochemistry


class ReplayTest(unittest.TestCase):
    def test_harmonic_and_gas_independent_replay(self):
        with tempfile.TemporaryDirectory(prefix="thermo ' 测试 ") as temporary:
            root=Path(temporary)
            for model in ('harmonic','gas'):
                path=write_calculation(root/model,imaginary=(1,2,3) if model=='harmonic' else ())
                data=read_outcar(path)
                data['modes'][3]['cm1']=20
                data['modes'][5]['cm1']=30
                request=dict(action='thermo',data=data,model=model,state='ts' if model=='harmonic' else 'minimum',
                             temperature='345',pressure='200000',geometry='linear',symmetry='2',spin='1',
                             selected=list(range(6)) if model=='harmonic' else [5],confirm_exclusions=True,
                             floor='250',energy='-15.2',imaginary_tolerance='0')
                result=thermochemistry(request)
                report,script=save_thermochemistry(root/(model+'.json'),data,result)
                self.assertEqual(json.loads(report.read_text())['source'],str(path))
                path.unlink();(path.parent/'POSCAR').unlink()
                env=dict(os.environ);env.pop('PYTHONPATH',None);env.pop('P4VASP_HOME',None)
                output=root/(model+' rerun.json')
                run=subprocess.run([sys.executable,'-I',str(script),'--output',str(output)],env=env,cwd=root,capture_output=True,text=True,timeout=30)
                self.assertEqual(run.returncode,0,run.stderr)
                actual=json.loads(output.read_text())
                for key in ('ZPE_eV','U_eV','S_eV_per_K','TS_eV','free_energy_eV','correction_eV'):
                    self.assertAlmostEqual(actual[key],result[key],places=12)
                self.assertEqual(actual['request_settings'],result['request_settings'])
                default=subprocess.run([sys.executable,'-I',str(script)],env=env,capture_output=True,text=True,timeout=30)
                self.assertEqual(default.returncode,0,default.stderr)
                self.assertTrue(script.with_name(script.stem+'_rerun.json').is_file())
                again=subprocess.run([sys.executable,'-I',str(script),'--output',str(output)],env=env,capture_output=True,text=True,timeout=30)
                self.assertNotEqual(again.returncode,0)

    def test_pair_collision_preserves_existing_files(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);data=read_outcar(write_calculation(root/'calc'))
            result=thermochemistry(dict(data=data,model='harmonic',state='ts',selected=[1,2,3,4,5],temperature=298.15,confirm_exclusions=True))
            script=root/'result.py';script.write_text('KEEP')
            with self.assertRaises(FileExistsError):save_thermochemistry(root/'result.json',data,result)
            self.assertFalse((root/'result.json').exists());self.assertEqual(script.read_text(),'KEEP')
            report=root/'exists.json';report.write_text('REPORT')
            with self.assertRaises(FileExistsError):save_thermochemistry(report,data,result)
            self.assertEqual(report.read_text(),'REPORT');self.assertFalse((root/'exists.py').exists())
            with self.assertRaises(ValueError):save_thermochemistry(root/'wrong.py',data,result)

if __name__=='__main__':unittest.main()

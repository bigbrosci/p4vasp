"""Actual p4v positional CLI and paired exports, with no display or GUI import."""
import csv
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from dos_projected_fixtures import projected_calculation
from p4vasp.dos_analysis import analyze
from p4vasp.dos_replay import save_scripts

ROOT=Path(__file__).resolve().parents[1]

class DosCliTest(unittest.TestCase):
    def env(self):
        env=dict(os.environ,DISPLAY='',WAYLAND_DISPLAY='',PYTHON='/usr/bin/python3',
                 P4VASP_HOME=str(ROOT),P4VASP_PYMATGEN_PYTHON=sys.executable,
                 P4VASP_SCIENCE_PYTHON=sys.executable,PYTHONPATH=str(ROOT/'lib'),PATH='/usr/bin:/bin')
        return env

    def test_headless_positional_command_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);source=projected_calculation(root/'source space',xml=True)
            output=root/'result.csv'
            args=[str(source/'DOSCAR'),'1-2','dxy,dyz','both','-6','0',str(output)]
            run=subprocess.run(['bash',str(ROOT/'p4v.sh'),*args],cwd=root,env=self.env(),capture_output=True,text=True,timeout=30)
            self.assertEqual(run.returncode,0,run.stderr)
            self.assertTrue(output.is_file())
            original=output.read_bytes()
            xml_args=[str(source/'vasprun.xml'),*args[1:-1],str(root/'xml.csv')]
            xml_run=subprocess.run(['bash',str(ROOT/'p4v.sh'),*xml_args],cwd=root,env=self.env(),capture_output=True,text=True,timeout=30)
            self.assertEqual(xml_run.returncode,0,xml_run.stderr)
            missing=subprocess.run(['bash',str(ROOT/'p4v.sh'),*args[:-1]],cwd=root,env=self.env(),capture_output=True,text=True,timeout=30)
            self.assertEqual(missing.returncode,2);self.assertIn('output',missing.stderr)
            again=subprocess.run(['bash',str(ROOT/'p4v.sh'),*args],cwd=root,env=self.env(),capture_output=True,text=True,timeout=30)
            self.assertNotEqual(again.returncode,0);self.assertEqual(output.read_bytes(),original)
            # Deny GTK imports entirely, not just display access.
            output2=root/'guard.csv'
            guarded='''import builtins,runpy,sys
original=builtins.__import__
def checked(name,*args,**kwargs):
    if name=='gi' or name.startswith('gi.'):raise RuntimeError('GUI imported in headless CLI')
    return original(name,*args,**kwargs)
builtins.__import__=checked
sys.argv=['p4v.py']+ARGS
runpy.run_path(P4V,run_name='__main__')
'''
            guarded=guarded.replace('ARGS',repr(args[:-1]+[str(output2)])).replace('P4V',repr(str(ROOT/'p4v.py')))
            probe=subprocess.run(['/usr/bin/python3','-c',guarded],cwd=root,env=self.env(),capture_output=True,text=True,timeout=30)
            self.assertEqual(probe.returncode,0,probe.stderr);self.assertTrue(output2.exists())

    def test_bash_pair_runs_cli_and_preserves_existing_pair(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);source=projected_calculation(root/'source space')
            result=analyze(dict(path=str(source/'DOSCAR'),atoms=[1],orbital='dxy,dyz',spin='up',emin=-6,emax=0))
            py,sh=save_scripts(root/'analysis space.py',result)
            check=subprocess.run(['bash','-n',str(sh)],capture_output=True,text=True)
            self.assertEqual(check.returncode,0,check.stderr)
            self.assertIn('p4v ',sh.read_text())
            run=subprocess.run(['bash',str(sh)],cwd=root,env=self.env(),capture_output=True,text=True,timeout=30)
            self.assertEqual(run.returncode,0,run.stderr)
            output=root/'analysis space_cli.csv'
            with output.open() as stream:rows=list(csv.reader(stream))
            index=rows.index(['Property','Value','Unit'])
            for actual,expected in zip(rows[index+1:],result['rows']):
                self.assertAlmostEqual(float(actual[1]),expected[1],places=9)
            before=sh.read_bytes()
            with self.assertRaises(FileExistsError):save_scripts(py,result)
            self.assertEqual(sh.read_bytes(),before)
            other=root/'other.py';other.with_suffix('.sh').write_text('KEEP')
            with self.assertRaises(FileExistsError):save_scripts(other,result)
            self.assertFalse(other.exists());self.assertEqual(other.with_suffix('.sh').read_text(),'KEEP')

if __name__=='__main__':unittest.main()

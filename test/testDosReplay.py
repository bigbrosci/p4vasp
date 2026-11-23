"""Exported scripts reproduce the selection without p4vasp/original VASP files."""
import csv
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from dos_projected_fixtures import projected_calculation
from p4vasp.dos_analysis import analyze
from p4vasp.dos_replay import save_script

class DosReplayTest(unittest.TestCase):
    def test_isolated_script_reproduces_and_adjusts_window(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);source=projected_calculation(root/'source')
            result=analyze(dict(path=str(source/'DOSCAR'),atoms=[1],spin='up',emin=-6,emax=0))
            script=save_script(root/'analysis.py',result)
            shutil.rmtree(source)
            env=dict(os.environ);env.pop('PYTHONPATH',None);env.pop('P4VASP_HOME',None)
            run=subprocess.run([sys.executable,'-I',str(script)],env=env,cwd=root,capture_output=True,text=True,timeout=30)
            self.assertEqual(run.returncode,0,run.stderr)
            output=root/'analysis_results.csv'
            with output.open() as stream:rows=list(csv.reader(stream))
            start=rows.index(['Property','Value','Unit'])
            for actual,expected in zip(rows[start+1:],result['rows']):
                self.assertEqual(actual[0],expected[0]);self.assertEqual(actual[2],expected[2])
                self.assertAlmostEqual(float(actual[1]),expected[1],places=9)
            metadata={row[0]:json.loads(row[1]) for row in rows[1:start-1]}
            self.assertEqual(metadata['atoms'],[1]);self.assertEqual(metadata['spin'],'up')
            second=root/'other-window.csv'
            rerun=subprocess.run([sys.executable,'-I',str(script),'--emin','-2','--emax','1','--output',str(second)],
                                 env=env,cwd=root,capture_output=True,text=True,timeout=30)
            self.assertEqual(rerun.returncode,0,rerun.stderr)
            self.assertIn('emin,-2.0',second.read_text())
            existing=output.read_bytes()
            again=subprocess.run([sys.executable,'-I',str(script)],env=env,cwd=root,capture_output=True,text=True,timeout=30)
            self.assertNotEqual(again.returncode,0);self.assertEqual(output.read_bytes(),existing)

    def test_exclusive_export_and_missing_result(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);source=projected_calculation(root/'source')
            result=analyze(dict(path=str(source/'DOSCAR')))
            script=root/'keep.py';script.write_text('KEEP')
            with self.assertRaises(FileExistsError):save_script(script,result)
            self.assertEqual(script.read_text(),'KEEP')
            with self.assertRaises(ValueError):save_script(root/'missing.py',{})

if __name__=='__main__':unittest.main()

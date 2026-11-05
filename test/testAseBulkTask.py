"""Real isolated worker round trip, missing dependency, cancellation and timeout."""
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import time
import unittest
from unittest.mock import patch
from p4vasp.ase_bulk import BulkTask

ROOT=Path(__file__).resolve().parents[1]
REQUEST={'name':'Cu','crystal':'fcc','a':'3.6','mode':'cubic','repeat':[2,2,2]}

class BulkTaskTest(unittest.TestCase):
    def run_task(self, task):
        task.start()
        self.assertTrue(self.done.wait(15),'worker did not finish')
        if task.process is not None:self.assertIsNotNone(task.process.poll())

    def setUp(self):
        self.done=threading.Event();self.response=None
    def callback(self,result,error):
        self.response=(result,error);self.done.set()

    def test_real_worker_and_p4vasp_poscar(self):
        task=BulkTask(REQUEST,self.callback)
        self.run_task(task)
        result,error=self.response;self.assertIsNone(error,error)
        self.assertEqual(result['atoms'],32)
        from io import StringIO
        from p4vasp.Structure import Structure
        structure=Structure();structure.read(StringIO(result['poscar']))
        self.assertEqual(len(structure),32)
        self.assertAlmostEqual(structure.basis[0][0],7.2)
        self.assertEqual(structure.info.getRecord(0).element,'Cu')

    def test_missing_ase_message(self):
        env=dict(os.environ);env['PYTHONPATH']=str(ROOT/'lib')
        result=subprocess.run(['/usr/bin/python3',str(ROOT/'lib/p4vasp/ase_bulk.py'),'--worker'],
            input=json.dumps(REQUEST),env=env,text=True,capture_output=True)
        self.assertNotEqual(result.returncode,0)
        self.assertIn('install/install-ase.sh',json.loads(result.stdout)['error'])

    def test_cancel_and_timeout_reap(self):
        command=[sys.executable,'-c','import time; time.sleep(30)']
        with patch('p4vasp.ase_bulk.worker_command',return_value=command):
            task=BulkTask(REQUEST,self.callback,timeout=.1);self.run_task(task)
            self.assertIn('timed out',self.response[1])
            self.done.clear();task=BulkTask(REQUEST,self.callback);task.start()
            deadline=time.monotonic()+5
            while task.process is None and time.monotonic()<deadline:time.sleep(.01)
            task.cancel();self.assertTrue(self.done.wait(5))
            self.assertIsNotNone(task.process.poll())
            self.assertIn('cancelled',self.response[1])

if __name__=='__main__':unittest.main()

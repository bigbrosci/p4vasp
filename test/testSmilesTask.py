"""Real optional worker, export handoff, timeout and cancellation cleanup."""
from io import StringIO
from pathlib import Path
import tempfile
import threading
import time
import sys
import unittest
from unittest.mock import patch
from p4vasp.smiles_builder import SmilesTask,molecule_from_result
from p4vasp.gas_phase_inputs import write_inputs,suggested_cell
from p4vasp.incar_generator import parse_custom
from p4vasp.Structure import Structure

class Task(unittest.TestCase):
    def result(self,smiles,timeout=20):
        completed=threading.Event();out={}
        task=SmilesTask(smiles,lambda result,error:(out.update(result=result,error=error),completed.set()))
        task.start()
        self.addCleanup(task.cancel)
        self.assertTrue(completed.wait(timeout));task.thread.join(1)
        return out

    def test_real_worker_to_poscar_and_charged_template(self):
        for smiles in ('CCO','[NH4+]'):
            out=self.result(smiles);self.assertIsNone(out['error'])
            molecule=molecule_from_result(out['result'])
            self.assertIsNone(molecule.path);self.assertIsNone(molecule.multiplicity)
            with tempfile.TemporaryDirectory() as root:
                folder=write_inputs(molecule,molecule.charge,1,suggested_cell(molecule),root,'inputs')
                s=Structure();s.read(StringIO((folder/'POSCAR').read_text()))
                self.assertEqual(len(s),len(molecule.symbols))
                incar=(folder/'INCAR').read_text();self.assertIn('SMILES=',incar)
                self.assertIn('ETKDGv3',incar)
                params=parse_custom(incar)
                if molecule.charge:self.assertEqual(params['NELECT'],'SET_AFTER_POTCAR')
                else:self.assertNotIn('NELECT',params)

    def test_invalid_worker_result_reported(self):
        self.assertIsNotNone(self.result('invalid smiles')['error'])

    def test_live_child_cancelled_and_reaped(self):
        completed=threading.Event();out={}
        with patch('p4vasp.smiles_builder.worker_command',return_value=[sys.executable,'-c','import time; time.sleep(20)']):
            task=SmilesTask('CC',lambda result,error:(out.update(error=error),completed.set()))
            task.start();self.addCleanup(task.cancel)
            deadline=time.monotonic()+3
            while task.process is None and time.monotonic()<deadline:time.sleep(.01)
            self.assertIsNotNone(task.process)
            task.cancel();self.assertTrue(completed.wait(3));task.thread.join(1)
            self.assertIn('cancelled',out['error']);self.assertIsNotNone(task.process.poll())

    def test_timeout_kills_and_reaps_child(self):
        completed=threading.Event();out={}
        with patch('p4vasp.smiles_builder.worker_command',return_value=[sys.executable,'-c','import time; time.sleep(20)']):
            task=SmilesTask('CC',lambda result,error:(out.update(error=error),completed.set()),timeout=.1)
            task.start();self.addCleanup(task.cancel)
            self.assertTrue(completed.wait(3));task.thread.join(1)
            self.assertIn('timed out',out['error']);self.assertIsNotNone(task.process.poll())

if __name__=='__main__':unittest.main()

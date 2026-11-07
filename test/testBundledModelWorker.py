"""Frozen worker selection, clean child environment and hidden-console launching."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from p4vasp.model_worker import bundled_worker,launch_options
from p4vasp.ase_bulk import worker_command as bulk_command
from p4vasp.smiles_builder import worker_command as smiles_command

class BundledWorkerTest(unittest.TestCase):
    def test_frozen_worker_routing_and_isolation(self):
        with tempfile.TemporaryDirectory(prefix='model worker ') as folder:
            root=Path(folder);exe=root/'p4vasp.exe';exe.touch()
            worker=root/'model-worker/p4vasp-model-worker.exe';worker.parent.mkdir();worker.touch()
            with patch.object(sys,'frozen',True,create=True),patch.object(sys,'executable',str(exe)),patch.dict(os.environ,{'P4VASP_ASE_PYTHON':'','P4VASP_SMILES_PYTHON':''}):
                self.assertEqual(bundled_worker(),worker)
                self.assertEqual(bulk_command(),[str(worker),'--bulk'])
                self.assertEqual(smiles_command(),[str(worker),'--smiles'])
                from p4vasp.ase_import import load_structure
                with patch('subprocess.run',return_value=subprocess.CompletedProcess([],0,'{"ok":true,"result":{"atoms":1}}','')) as run:
                    self.assertEqual(load_structure(root/'one.xyz'),{'atoms':1})
                    self.assertEqual(run.call_args.args[0],[str(worker),'--read-structure'])
                    self.assertEqual(run.call_args.kwargs['env']['PYINSTALLER_RESET_ENVIRONMENT'],'1')
                with patch.object(sys,'platform','win32'),patch.object(subprocess,'CREATE_NO_WINDOW',0x08000000,create=True):
                    options=launch_options([str(worker),'--bulk'])
                    self.assertEqual(options['creationflags'],0x08000000)
                self.assertNotIn('PYTHONPATH',options['env'])
                self.assertEqual(options['env']['PYINSTALLER_RESET_ENVIRONMENT'],'1')
                self.assertEqual(options['env']['OMP_NUM_THREADS'],'1')
                worker.unlink();self.assertIsNone(bundled_worker())

    def test_source_environment_not_sanitized(self):
        with patch.object(sys,'frozen',False,create=True),patch.dict(os.environ,{'PYTHONPATH':'source-path'}):
            self.assertIsNone(bundled_worker())
            self.assertEqual(launch_options(['python','worker.py'])['env']['PYTHONPATH'],'source-path')

if __name__=='__main__':unittest.main()

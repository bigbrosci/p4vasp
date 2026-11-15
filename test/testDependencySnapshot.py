"""Maintenance catalog checks and metadata-only snapshots without installation."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/'tools/dependency_snapshot.py'
spec=importlib.util.spec_from_file_location('dependency_snapshot',SCRIPT)
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)


class DependencySnapshotTest(unittest.TestCase):
    def setUp(self):self.catalog=json.loads(module.CATALOG.read_text())

    def test_catalog_and_bad_sources(self):
        module.validate(self.catalog)
        bad=copy.deepcopy(self.catalog);bad['python'][0]['sources']=['../outside.py']
        with self.assertRaises(ValueError):module.validate(bad)
        bad=copy.deepcopy(self.catalog);bad['native'][0]['id']=bad['python'][0]['id']
        with self.assertRaises(ValueError):module.validate(bad)
        bad=copy.deepcopy(self.catalog);bad['python'][0]['profiles']=['unknown']
        with self.assertRaises(ValueError):module.validate(bad)

    def test_missing_metadata_transitive_and_raw_markers(self):
        dist=SimpleNamespace(metadata={'Name':'Typing.Extensions'},version='1.2',
                             requires=['example>=1; extra == "docs"'])
        with patch.object(module.metadata,'distributions',return_value=[dist]):
            data=module.collect(self.catalog,'ase')
        declared={d['id']:d for d in data['declared']}
        self.assertEqual(declared['typing-extensions']['version'],'1.2')
        self.assertEqual(declared['ase']['status'],'metadata-not-found')
        self.assertEqual(data['distributions'][0]['requires_dist'],dist.requires)
        self.assertNotIn('executable',data['python'])
        with self.assertRaises(ValueError):module.collect(self.catalog,'unknown')

    def test_cli_snapshot_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'nested'/'snapshot.json'
            args=[sys.executable,str(SCRIPT),'--profile','gui','--output',str(path)]
            result=subprocess.run(args,text=True,capture_output=True)
            self.assertEqual(result.returncode,0,result.stderr)
            original=path.read_bytes();data=json.loads(original)
            self.assertEqual(data['profile'],'gui')
            self.assertEqual(len(data['catalog_sha256']),64)
            self.assertTrue(data['limits'])
            again=subprocess.run(args,text=True,capture_output=True)
            self.assertNotEqual(again.returncode,0)
            self.assertEqual(path.read_bytes(),original)
            self.assertEqual(subprocess.run([sys.executable,str(SCRIPT),'--check'],capture_output=True).returncode,0)


if __name__=='__main__':unittest.main()

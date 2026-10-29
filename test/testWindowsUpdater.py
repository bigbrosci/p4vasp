"""Validate update safeguards using temporary real Git repositories; no network/build."""
import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import json

spec = importlib.util.spec_from_file_location('windows_update_build',
    Path(__file__).resolve().parents[1]/'install/windows/update_build.py')
updater = importlib.util.module_from_spec(spec)
spec.loader.exec_module(updater)


class CheckoutGuards(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.git('init', '-q', '-b', updater.BRANCH)
        self.git('remote', 'add', 'origin', updater.REMOTE)
        self.git('-c', 'user.name=Updater test', '-c', 'user.email=test@example.invalid',
                 '-c', 'commit.gpgsign=false', 'commit', '-q', '--allow-empty', '-m', 'fixture')

    def git(self, *args):
        return subprocess.check_output(['git', *args], cwd=self.root, text=True).strip()

    def test_clean_authorized_checkout(self):
        self.assertEqual(updater.validate_checkout(self.root), self.git('rev-parse', 'HEAD'))

    def test_untracked_changes_preserved(self):
        (self.root/'notes.txt').write_text('keep')
        with self.assertRaisesRegex(RuntimeError, 'local changes'):
            updater.validate_checkout(self.root)
        self.assertEqual((self.root/'notes.txt').read_text(), 'keep')

    def test_wrong_branch_preserved(self):
        self.git('checkout', '-q', '-b', 'other')
        with self.assertRaisesRegex(RuntimeError, 'Required branch'):
            updater.validate_checkout(self.root)
        self.assertEqual(self.git('branch', '--show-current'), 'other')

    def test_wrong_remote_preserved(self):
        self.git('remote', 'set-url', 'origin', 'https://example.invalid/other.git')
        with self.assertRaisesRegex(RuntimeError, 'Required origin'):
            updater.validate_checkout(self.root)
        self.assertEqual(self.git('remote', 'get-url', 'origin'), 'https://example.invalid/other.git')

    def test_nested_directory_rejected(self):
        nested = self.root/'nested'
        nested.mkdir()
        with self.assertRaisesRegex(RuntimeError, 'subdirectory'):
            updater.validate_checkout(nested)

    def test_verifier_uses_gui_exe_and_clean_environment(self):
        calls = []
        def simulate(command, cwd, log, env, timeout):
            calls.append((command, env))
            output = Path(command[2])
            output.mkdir()
            (output/'report.json').write_text(json.dumps(dict(ok=True, frozen=True)))
        reports = self.root/'reports'
        with patch.object(updater, 'logged', side_effect=simulate):
            updater.verify(self.root/'release', reports)
        self.assertEqual(calls[0][0][0].name, 'p4vasp-console.exe')
        self.assertEqual(calls[1][0][0].name, 'p4vasp.exe')
        self.assertNotIn('PYTHONPATH', calls[1][1])
        self.assertNotIn('MSYSTEM', calls[1][1])

    def test_missing_completion_report_is_failure(self):
        with patch.object(updater, 'logged'), self.assertRaisesRegex(RuntimeError, 'without a completion report'):
            updater.verify(self.root/'release', self.root/'reports')


if __name__ == '__main__':
    unittest.main()

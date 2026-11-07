"""Installer completion: alias quoting, headless behavior and failure propagation."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class FinishTest(unittest.TestCase):
    def run_finish(self, directory, code=0, display=':0', launch=1, mac=False):
        directory.joinpath('p4v.sh').write_text('exit '+str(code)+'\n')
        env = dict(os.environ, DISPLAY=display, WAYLAND_DISPLAY='', TEST_ROOT=str(directory),
                   FINISH_SCRIPT=str(ROOT/'install/finish-install.sh'), TEST_LAUNCH=str(launch))
        prefix='uname() { echo Darwin; }; ' if mac else ''
        return subprocess.run(['bash', '-c', prefix+'set -euo pipefail; ROOT="$TEST_ROOT"; LAUNCH="$TEST_LAUNCH"; APP_ARGS=(); source "$FINISH_SCRIPT"; finish_install'],
                              env=env, text=True, capture_output=True)

    def test_success_alias_and_failure(self):
        with tempfile.TemporaryDirectory(prefix="p4vasp quote ' $ ") as folder:
            root = Path(folder)
            result = self.run_finish(root)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('GUI startup check: PASSED', result.stdout)
            self.assertIn('NEXT STEP:',result.stdout)
            self.assertIn('============================================================',result.stdout)
            alias = next(line for line in result.stdout.splitlines() if line.startswith('alias p4v='))
            root.joinpath('p4v.sh').write_text('printf "%s\\n" "$0"\n')
            # Check the alias as shell syntax, then invoke it with expansion enabled.
            check = subprocess.run(['bash', '-O', 'expand_aliases', '-c', alias+'\np4v'], capture_output=True, text=True)
            self.assertEqual(check.returncode, 0, check.stderr)
            self.assertEqual(check.stdout.strip(), str(root/'p4v.sh'))
            # Execute the exact printed four-line block against a disposable rc file.
            lines=result.stdout.splitlines()
            start=lines.index("cat >> ~/.bashrc <<'P4VASP_ALIAS'")
            rc=root/'test.bashrc'
            block='\n'.join(lines[start:start+4]).replace('~/.bashrc',"'"+str(rc).replace("'","'\\''")+"'")
            check=subprocess.run(['bash','-O','expand_aliases','-c',block+'\np4v'],capture_output=True,text=True)
            self.assertEqual(check.returncode,0,check.stderr)
            self.assertEqual(rc.read_text(),alias+'\n')
            self.assertEqual(check.stdout.strip(),str(root/'p4v.sh'))
            result = self.run_finish(root, code=7)
            self.assertEqual(result.returncode, 7)
            self.assertNotIn('installation steps completed', result.stdout)
            for display, launch in [('', 1), (':0', 0)]:
                result = self.run_finish(root, code=7, display=display, launch=launch)
                self.assertEqual(result.returncode, 0)
                self.assertNotIn('GUI startup check: PASSED', result.stdout)
                self.assertIn('GUI startup check: SKIPPED', result.stdout)
                self.assertIn('alias p4v=', result.stdout)

    def test_macos_zsh_instructions(self):
        with tempfile.TemporaryDirectory() as folder:
            result=self.run_finish(Path(folder),launch=0,mac=True)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertIn('run this block INSTEAD',result.stdout)
            lines=result.stdout.splitlines()
            start=lines.index("cat >> ~/.zshrc <<'P4VASP_ALIAS'")
            self.assertEqual(lines[start+2:start+4],['P4VASP_ALIAS','source ~/.zshrc'])
            # Validate emitted shell syntax only; this is not a macOS/zsh run.
            check=subprocess.run(['bash','-n'],input='\n'.join(lines[start:start+4]),text=True,capture_output=True)
            self.assertEqual(check.returncode,0,check.stderr)


if __name__ == '__main__':
    unittest.main()

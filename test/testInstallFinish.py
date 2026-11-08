"""Automatic alias setup uses disposable rc files, never the developer's HOME."""
import os
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
BEGIN='# >>> p4vasp command >>>'


class FinishTest(unittest.TestCase):
    def run_finish(self,directory,code=0,display=':0',launch=1,rc=None,shell='bash',configure=1,zdotdir=None,receipt=None):
        directory.mkdir(parents=True,exist_ok=True)
        (directory/'p4v.sh').write_text('exit '+str(code)+'\n')
        env=dict(os.environ,DISPLAY=display,WAYLAND_DISPLAY='',TEST_ROOT=str(directory),
                 FINISH_SCRIPT=str(ROOT/'install/finish-install.sh'),TEST_LAUNCH=str(launch),
                 TEST_CONFIGURE=str(configure),SHELL='/bin/'+shell,PYTHON=sys.executable,
                 P4VASP_SHELL_RC=str(rc or directory/'.bashrc'),
                 P4VASP_RELOAD_RECEIPT=str(receipt) if receipt else '',P4VASP_CALLER_SHELL='bash' if receipt else '')
        if zdotdir is not None:
            env.update(ZDOTDIR=str(zdotdir),P4VASP_SHELL_RC='')
        return subprocess.run(['bash','-c','set -euo pipefail; ROOT="$TEST_ROOT"; LAUNCH="$TEST_LAUNCH"; CONFIGURE_SHELL="$TEST_CONFIGURE"; APP_ARGS=(); source "$FINISH_SCRIPT"; finish_install'],
                              env=env,text=True,capture_output=True)

    def test_success_quoted_alias_and_repeat_install(self):
        with tempfile.TemporaryDirectory(prefix="p4vasp quote ' $ ` ") as folder:
            root=Path(folder);rc=root/'.bashrc'
            result=self.run_finish(root)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertIn('GUI startup check: PASSED',result.stdout)
            self.assertIn('Command setup: CONFIGURED',result.stdout)
            self.assertIn('source ~/.bashrc',result.stdout)
            for command in ('p4v POSCAR','p4v test.xyz','p4v OUTCAR','p4v POSCAR -o top.png --view top','p4v POSCAR -o side.png --view side'):
                self.assertNotIn(command,result.stdout)
            self.assertIn('usage_commands.md',result.stdout)
            original=rc.read_bytes();mtime=rc.stat().st_mtime_ns
            (root/'p4v.sh').write_text('printf "%s\\n" "$0"\n')
            check=subprocess.run(['bash','-O','expand_aliases','-c','source '+shlex.quote(str(rc))+'\np4v'],capture_output=True,text=True)
            self.assertEqual(check.returncode,0,check.stderr)
            self.assertEqual(check.stdout.strip(),str(root/'p4v.sh'))
            self.assertEqual(self.run_finish(root).returncode,0)
            self.assertEqual(rc.read_bytes(),original)
            self.assertEqual(rc.stat().st_mtime_ns,mtime)
            self.assertFalse(list(root.glob('.bashrc.p4vasp-backup-*')))

    def test_preserve_existing_config_backup_and_update_checkout(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);rc=root/'.bashrc'
            original=b'# custom\nexport KEEP_ME=yes\n# non-UTF8: \xff\nalias other=true'
            rc.write_bytes(original);rc.chmod(0o640)
            self.assertEqual(self.run_finish(root/'first',rc=rc).returncode,0)
            first=rc.read_bytes()
            self.assertTrue(first.startswith(original+b'\n'))
            self.assertEqual(rc.stat().st_mode&0o777,0o640)
            backups=list(root.glob('.bashrc.p4vasp-backup-*'))
            self.assertEqual(len(backups),1);self.assertEqual(backups[0].read_bytes(),original)
            result=self.run_finish(root/'second',rc=rc)
            self.assertEqual(result.returncode,0,result.stderr)
            data=rc.read_bytes()
            self.assertEqual(data.count(BEGIN.encode()),1)
            self.assertIn(str(root/'second/p4v.sh').encode(),data)
            self.assertNotIn(str(root/'first/p4v.sh').encode(),data)
            self.assertTrue(any(p.read_bytes()==first for p in root.glob('.bashrc.p4vasp-backup-*')))

    def test_failure_skip_gui_and_dependency_only(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            failed=root/'failed';result=self.run_finish(failed,code=7)
            self.assertEqual(result.returncode,7)
            self.assertNotIn('installation steps completed',result.stdout)
            self.assertFalse((failed/'.bashrc').exists())
            for name,display,launch in [('headless','',1),('no-launch',':0',0)]:
                directory=root/name;result=self.run_finish(directory,code=7,display=display,launch=launch)
                self.assertEqual(result.returncode,0,result.stderr)
                self.assertIn('GUI startup check: SKIPPED',result.stdout)
                self.assertTrue((directory/'.bashrc').is_file())
            directory=root/'dependencies';result=self.run_finish(directory,launch=0,configure=0)
            self.assertEqual(result.returncode,0)
            self.assertIn('Command setup: SKIPPED (--deps-only)',result.stdout)
            self.assertFalse((directory/'.bashrc').exists())

    def test_zsh_destination_and_malformed_block(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            result=self.run_finish(root,launch=0,shell='zsh')
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertFalse((root/'.zshrc').exists())
            self.assertIn('source ~/.bashrc',result.stdout)
            rc=root/'.bashrc';original=BEGIN+'\n# incomplete block\n';rc.write_text(original)
            result=self.run_finish(root,launch=0)
            self.assertEqual(result.returncode,0)
            self.assertIn('Command setup: NOT CONFIGURED',result.stdout)
            self.assertIn('Incomplete/duplicate',result.stderr)
            self.assertEqual(rc.read_text(),original)

    def test_symlink_config_keeps_link(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);target=root/'real-rc';target.write_text('# keep\n')
            rc=root/'.bashrc';rc.symlink_to(target.name)
            result=self.run_finish(root,launch=0)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertTrue(rc.is_symlink())
            self.assertIn(BEGIN,target.read_text())


if __name__=='__main__':unittest.main()

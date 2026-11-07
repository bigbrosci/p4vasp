"""Route installers without installing packages, compiling, or opening windows."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class UnifiedInstallerTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='p4vasp installer ')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        shutil.copy(ROOT / 'install.sh', self.root)
        (self.root / 'bin').mkdir()
        (self.root / 'install').mkdir()
        for backend in ('ubuntu', 'macos'):
            (self.root / 'install' / (backend + '-bootstrap.sh')).write_text(
                "printf 'BACKEND:%s\\n' " + backend + "\nprintf '<%s>\\n' \"$@\"\nexit \"${BACKEND_EXIT:-0}\"\n")
        uname = self.root / 'bin/uname'
        uname.write_text('#!/bin/sh\nprintf "%s\\n" "$TEST_KERNEL"\n')
        uname.chmod(0o755)

    def run_installer(self, kernel='Linux', release='ID=ubuntu\n', args=(), exitcode=0):
        release_file = self.root / 'os-release'
        if release is not None:
            release_file.write_text(release)
        env = dict(os.environ, PATH=str(self.root / 'bin') + ':' + os.environ['PATH'],
                   TEST_KERNEL=kernel, P4VASP_OS_RELEASE=str(release_file),
                   BACKEND_EXIT=str(exitcode))
        return subprocess.run(['bash', str(self.root / 'install.sh'), *args],
                              env=env, cwd='/tmp', capture_output=True, text=True)

    def test_debian_family(self):
        for release in ('ID=ubuntu\n', 'ID=debian\n', 'ID=linuxmint\nID_LIKE="ubuntu debian"\n'):
            with self.subTest(release=release):
                result = self.run_installer(release=release)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn('BACKEND:ubuntu', result.stdout)
                self.assertNotIn('--skip-apt', result.stdout)

    def test_other_linux(self):
        for release in ('ID=fedora\n', 'ID=arch\n', 'ID=opensuse-tumbleweed\n', None):
            with self.subTest(release=release):
                if release is None:
                    (self.root / 'os-release').unlink(missing_ok=True)
                result = self.run_installer(release=release)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn('<--skip-apt>', result.stdout)

    def test_macos(self):
        result = self.run_installer(kernel='Darwin', args=('--skip-deps', '--no-launch'))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('BACKEND:macos', result.stdout)
        self.assertIn('<--skip-brew>', result.stdout)
        self.assertIn('<--no-launch>', result.stdout)

    def test_arguments(self):
        result = self.run_installer(args=('--build-only', '--', 'a path/POSCAR', '--help', '$(false)'))
        self.assertIn('<--skip-apt>\n<--build-only>\n<-->\n<a path/POSCAR>\n<--help>\n<$(false)>', result.stdout)

    def test_dry_run_and_help(self):
        for args in (('--dry-run',), ('--help',)):
            result = self.run_installer(args=args)
            self.assertEqual(result.returncode, 0)
            self.assertNotIn('BACKEND:', result.stdout)

    def test_errors(self):
        for kwargs in (dict(kernel='FreeBSD'), dict(args=('--typo',)),
                       dict(args=('--deps-only', '--skip-deps')),
                       dict(args=('--deps-only', '--build-only')),
                       dict(release='ID=fedora\n', args=('--deps-only',))):
            with self.subTest(kwargs=kwargs):
                result = self.run_installer(**kwargs)
                self.assertNotEqual(result.returncode, 0)
                self.assertNotIn('BACKEND:', result.stdout)

    def test_dependency_aliases(self):
        for option in ('--skip-apt', '--skip-brew', '--skip-deps'):
            result = self.run_installer(args=(option,))
            self.assertIn('<--skip-apt>', result.stdout)

    def test_exit_status(self):
        self.assertEqual(self.run_installer(exitcode=23).returncode, 23)

    def test_release_is_not_executed(self):
        marker = self.root / 'should-not-exist'
        self.run_installer(release=f'ID=$(touch "{marker}")\n')
        self.assertFalse(marker.exists())

    def source_installer(self,args=(),exitcode=0,no_receipt=False,interactive=False):
        (self.root/'os-release').write_text('ID=ubuntu\n')
        receipt_dir=self.root/'receipts';receipt_dir.mkdir(exist_ok=True)
        rc=self.root/'test rc'
        rc.write_text(('case $- in *i*) ;; *) return;; esac\n' if interactive else '')+"alias p4v='printf READY\\n'\n")
        (self.root/'install/ubuntu-bootstrap.sh').write_text('''
if [ "${BACKEND_EXIT:-0}" -ne 0 ]; then exit "$BACKEND_EXIT"; fi
for arg in "$@"; do if [ "$arg" = --deps-only ]; then exit 0; fi; done
if [ "${TEST_NO_RECEIPT:-0}" -eq 0 ]; then
    printf '%s\\0' "$P4VASP_SHELL_RC" > "$P4VASP_RELOAD_RECEIPT"
fi
''')
        env=dict(os.environ,PATH=str(self.root/'bin')+':'+os.environ['PATH'],TEST_KERNEL='Linux',
                 P4VASP_OS_RELEASE=str(self.root/'os-release'),TEST_ENTRY=str(self.root/'install.sh'),
                 BACKEND_EXIT=str(exitcode),TEST_NO_RECEIPT=str(int(no_receipt)),
                 P4VASP_SHELL_RC=str(rc),TMPDIR=str(receipt_dir))
        script='''ROOT=preserve-parent
p4v_options=$-
p4v_directory=$PWD
if source "$TEST_ENTRY" "$@"; then p4v_status=0; else p4v_status=$?; fi
printf 'SOURCE_STATUS:%s\\n' "$p4v_status"
[[ "$ROOT" == preserve-parent && "$-" == "$p4v_options" && "$PWD" == "$p4v_directory" ]] || exit 99
if declare -F _p4vasp_install_and_reload >/dev/null; then exit 98; fi
if alias p4v >/dev/null 2>&1; then p4v; else echo NO_ALIAS; fi
'''
        command=['bash','--noprofile','--norc']+(['-i'] if interactive else [])
        result=subprocess.run([*command,'-O','expand_aliases','-c',script,'source-test',*args],
                              env=env,cwd='/tmp',capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertFalse(list(receipt_dir.iterdir()))
        return result

    def test_source_reloads_parent_without_changing_options_or_directory(self):
        result=self.source_installer(args=('--skip-deps','--no-launch'))
        self.assertIn('SOURCE_STATUS:0',result.stdout)
        self.assertIn('READY',result.stdout)
        self.assertIn('p4v is ready in this terminal',result.stdout)

    def test_source_interactive_bash_rc_guard(self):
        result=self.source_installer(interactive=True)
        self.assertIn('SOURCE_STATUS:0',result.stdout)
        self.assertIn('READY',result.stdout)

    def test_source_failure_does_not_reload_or_exit_parent(self):
        result=self.source_installer(exitcode=23)
        self.assertIn('SOURCE_STATUS:23',result.stdout)
        self.assertIn('NO_ALIAS',result.stdout)
        result=self.source_installer(no_receipt=True)
        self.assertIn('SOURCE_STATUS:1',result.stdout)
        self.assertIn('NO_ALIAS',result.stdout)

    def test_source_dry_run_help_and_dependencies_do_not_reload(self):
        for option in ('--dry-run','--help','--deps-only'):
            result=self.source_installer(args=(option,))
            self.assertIn('SOURCE_STATUS:0',result.stdout)
            self.assertIn('NO_ALIAS',result.stdout)


if __name__ == '__main__':
    unittest.main()

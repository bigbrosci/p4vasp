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
        shutil.copy(ROOT / 'ubuntu_install.sh', self.root)
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
        return subprocess.run(['bash', str(self.root / 'ubuntu_install.sh'), *args],
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


if __name__ == '__main__':
    unittest.main()

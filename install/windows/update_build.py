"""Update an authorized Windows checkout; build/test an isolated source snapshot."""
import argparse
from datetime import datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile

BRANCH = 'p4vasp-py3'
REMOTE = 'https://github.com/bigbrosci/p4vasp.git'


def git(root, *args):
    return subprocess.check_output(['git', *args], cwd=root, text=True).strip()


def validate_checkout(root):
    if git(root, 'rev-parse', '--show-prefix'):
        raise RuntimeError('Run from a dedicated p4vasp Git checkout, not a subdirectory of another repository.')
    if git(root, 'branch', '--show-current') != BRANCH:
        raise RuntimeError(f'Required branch: {BRANCH}; checkout was not changed.')
    if git(root, 'remote', 'get-url', 'origin') != REMOTE:
        raise RuntimeError(f'Required origin: {REMOTE}; remote was not changed.')
    if git(root, 'status', '--porcelain', '--untracked-files=normal'):
        raise RuntimeError('Working tree has local changes. Preserve/review them before updating; nothing was reset.')
    return git(root, 'rev-parse', 'HEAD')


def logged(command, cwd, log, env=None, timeout=None):
    with log.open('w', encoding='utf-8') as output:
        subprocess.run([str(x) for x in command], cwd=cwd, env=env, stdout=output,
                       stderr=subprocess.STDOUT, timeout=timeout, check=True)


def verify(release, reports):
    env = dict(os.environ)
    for name in ('PYTHONPATH', 'PYTHONHOME', 'P4VASP_HOME', 'GI_TYPELIB_PATH',
                 'GTK_PATH', 'GTK_DATA_PREFIX', 'GTK_EXE_PREFIX', 'GIO_MODULE_DIR',
                 'MSYSTEM', 'MINGW_PREFIX'):
        env.pop(name, None)
    windows = Path(env.get('SystemRoot', r'C:\Windows'))
    env['PATH'] = str(windows/'System32') + os.pathsep + str(windows)
    reports.mkdir()
    for option, name in (('--check-runtime', 'runtime'), ('--check-gui', 'gui')):
        executable = 'p4vasp.exe' if name == 'gui' else 'p4vasp-console.exe'
        logged([release/executable, option, reports/name],
               tempfile.gettempdir(), reports/(name+'.log'), env=env, timeout=60)
        report_path = reports/name/'report.json'
        if not report_path.is_file():
            raise RuntimeError(f'{name} process exited without a completion report; see {reports}')
        report = json.loads(report_path.read_text(encoding='utf-8'))
        if not report.get('ok') or not report.get('frozen'):
            raise RuntimeError(f'Packaged {name} check did not pass; see {reports}')


def main(args=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Read-only checkout validation; no pull or build')
    parser.add_argument('--build-current', action='store_true', help='Build the current commit without pulling')
    options = parser.parse_args(args)
    root = Path(__file__).resolve().parents[2]
    revision = validate_checkout(root)
    if options.check:
        print(f'CHECK PASS: {root}\n{BRANCH} @ {revision}\norigin: {REMOTE}')
        return
    if sys.platform != 'win32' or os.environ.get('MSYSTEM') != 'UCRT64':
        raise RuntimeError('Build requires Windows and MSYS2 UCRT64.')
    if not options.build_current:
        subprocess.run(['git', 'pull', '--ff-only', 'origin', BRANCH], cwd=root, check=True)
        # Re-enter the newly pulled implementation instead of continuing an old updater.
        subprocess.run([sys.executable, str(root/'install/windows/update_build.py'), '--build-current'], check=True)
        return
    if importlib.util.find_spec('PyInstaller') is None:
        raise RuntimeError('Install mingw-w64-ucrt-x86_64-pyinstaller in UCRT64 first.')
    work_parent = root/'build/windows-update'
    work_parent.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix=revision[:8]+'-', dir=work_parent))
    print(f'Source commit: {revision}\nBuild logs: {work}', flush=True)
    release = None
    try:
        archive = work/'source.tar'
        subprocess.run(['git', 'archive', '--format=tar', '--output', str(archive), revision], cwd=root, check=True)
        source = work/'source'
        source.mkdir()
        with tarfile.open(archive) as tar:
            tar.extractall(source, filter='data')
        bash = Path(sys.prefix).parent/'usr/bin/bash.exe'
        print('Building Windows native extension...', flush=True)
        logged([bash, 'install/build-windows-py3.sh'], source, work/'native-build.log')
        print('Packaging portable folder...', flush=True)
        logged([bash, 'install/package-windows.sh'], source, work/'package.log')
        destination = root/'dist/windows-releases'
        destination.mkdir(parents=True, exist_ok=True)
        prefix = f'p4vasp-{datetime.now():%Y%m%d-%H%M%S}-{revision[:8]}-'
        release = Path(tempfile.mkdtemp(prefix=prefix, dir=destination))
        shutil.copytree(source/'dist/windows/p4vasp', release, dirs_exist_ok=True)
        (release/'SOURCE-COMMIT.txt').write_text(revision+'\n', encoding='utf-8')
        (release/'BUILD-STATUS.txt').write_text('Verification pending\n')
        print('Checking portable runtime and GUI (test windows will open briefly)...', flush=True)
        verify(release, release.with_name(release.name+'-checks'))
        (release/'BUILD-STATUS.txt').write_text('Synthetic runtime and GUI checks passed; clean-machine acceptance pending.\n')
        bundle = Path(shutil.make_archive(str(release), 'zip', root_dir=release.parent, base_dir=release.name))
        with bundle.open('rb') as handle:
            digest = hashlib.file_digest(handle, 'sha256').hexdigest()
        bundle.with_suffix('.zip.sha256').write_text(digest+'  '+bundle.name+'\n', encoding='utf-8')
        print(f'SUCCESS\nEXE: {release / "p4vasp.exe"}\nZIP: {bundle}\nSHA256: {digest}', flush=True)
    except BaseException:
        if release is not None:
            (release/'BUILD-STATUS.txt').write_text('FAILED or interrupted; inspect build/check logs before using.\n')
        print(f'Build stopped. Previous releases were preserved. Logs: {work}', file=sys.stderr)
        raise


if __name__ == '__main__':
    main()

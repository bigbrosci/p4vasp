"""Prepare a project-build-only CPython environment for Windows wheel packages."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import urllib.request
import zipfile

PYTHON_VERSION='3.13.17'
PACKAGES=['ase==3.29.0','rdkit==2026.9.1','pyinstaller==6.22.3']


def environment_path():
    return Path(os.environ.get('P4VASP_MODEL_CACHE',Path(os.environ['LOCALAPPDATA'])/'p4vasp-build'))/('python-'+PYTHON_VERSION)


def prepare():
    if sys.platform!='win32':raise RuntimeError('This build environment is for Windows only.')
    folder=environment_path();folder.mkdir(parents=True,exist_ok=True)
    python=folder/'python.exe'
    if not all((folder/name).is_file() for name in ('python.exe','python313.dll','python313.zip','LICENSE.txt')):
        url=f'https://www.python.org/ftp/python/{PYTHON_VERSION}/python-{PYTHON_VERSION}-embed-amd64.zip'
        print('Downloading official CPython embeddable runtime:',url,flush=True)
        with urllib.request.urlopen(url,timeout=90) as response:data=response.read()
        archive=folder/'python-embed.zip';archive.write_bytes(data)
        with zipfile.ZipFile(archive) as z:
            if z.testzip():raise RuntimeError('Invalid CPython archive')
            for name in z.namelist():
                if Path(name).is_absolute() or '..' in Path(name).parts:raise RuntimeError('Unsafe archive path')
            z.extractall(folder)
        (folder/'PYTHON-SOURCE.json').write_text(json.dumps({'url':url,'sha256':hashlib.sha256(data).hexdigest()},indent=2))
    (folder/'python313._pth').write_text('python313.zip\n.\nLib/site-packages\nimport site\n')
    site=folder/'Lib/site-packages';site.mkdir(parents=True,exist_ok=True)
    if not (site/'pip').is_dir():
        with urllib.request.urlopen('https://pypi.org/pypi/pip/26.1.2/json',timeout=60) as response:metadata=json.load(response)
        wheel=next(file for file in metadata['urls'] if file['filename'].endswith('.whl'))
        with urllib.request.urlopen(wheel['url'],timeout=60) as response:data=response.read()
        if hashlib.sha256(data).hexdigest()!=wheel['digests']['sha256']:raise RuntimeError('pip wheel checksum mismatch')
        from io import BytesIO
        with zipfile.ZipFile(BytesIO(data)) as z:z.extractall(site)
    env=dict(os.environ)
    for name in ('PYTHONHOME','PYTHONPATH'):env.pop(name,None)
    subprocess.run([str(python),'-m','pip','--isolated','install','--only-binary=:all:',
                    '--disable-pip-version-check','--no-warn-script-location','--index-url','https://pypi.org/simple',*PACKAGES],env=env,check=True)
    subprocess.run([str(python),'-c','import ase,rdkit,PyInstaller; print("Model build environment:",ase.__version__,rdkit.__version__,PyInstaller.__version__)'],env=env,check=True)
    with (folder/'PACKAGES.json').open('w') as handle:
        subprocess.run([str(python),'-m','pip','list','--format=json'],stdout=handle,env=env,check=True)
    return python


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--print-path',action='store_true');args=parser.parse_args()
    if args.print_path:print((environment_path()/'python.exe').as_posix())
    else:prepare()

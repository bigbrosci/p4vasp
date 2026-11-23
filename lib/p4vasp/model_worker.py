"""Locate the optional bundled model worker and isolate its runtime environment."""
import os
from pathlib import Path
import subprocess
import sys


def bash_launcher():
    """Alias-free replay fallback for source checkouts and portable Windows apps."""
    import shlex
    if getattr(sys,'frozen',False):
        launcher=Path(sys.executable).resolve().with_name('p4vasp-console.exe')
        command=shlex.quote(launcher.as_posix())
    else:
        import p4vasp
        launcher=Path(p4vasp.p4vasp_home).resolve()/'p4v.sh'
        command='bash '+shlex.quote(str(launcher))
    if not launcher.is_file():raise ValueError('Replay launcher is missing: '+str(launcher))
    return '  p4v() { '+command+' "$@"; }\n'


def bundled_worker():
    if not getattr(sys,'frozen',False):return None
    path=Path(sys.executable).resolve().parent/'model-worker/p4vasp-model-worker.exe'
    return path if path.is_file() else None


def launch_options(command):
    env=dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1')
    bundled=bundled_worker()
    if bundled is not None and Path(command[0]).resolve()==bundled:
        for name in ('PYTHONHOME','PYTHONPATH','P4VASP_HOME','GI_TYPELIB_PATH','GTK_PATH',
                     'GTK_DATA_PREFIX','GTK_EXE_PREFIX','GIO_MODULE_DIR','MSYSTEM','MINGW_PREFIX'):
            env.pop(name,None)
        env['PYINSTALLER_RESET_ENVIRONMENT']='1'
        system=Path(env.get('SystemRoot',r'C:\Windows'))
        env['PATH']=str(system/'System32')+os.pathsep+str(system)
    options={'env':env}
    if sys.platform=='win32':options['creationflags']=subprocess.CREATE_NO_WINDOW
    return options


def scientific_python(feature):
    """Explicit feature override, shared override, shared venv, then legacy venv."""
    import p4vasp
    variable, legacy = {
        'ase': ('P4VASP_ASE_PYTHON', '.venv-ase'),
        'smiles': ('P4VASP_SMILES_PYTHON', '.venv-smiles'),
        'pymatgen': ('P4VASP_PYMATGEN_PYTHON', '.venv-pymatgen'),
    }[feature]
    configured = os.environ.get(variable) or os.environ.get('P4VASP_SCIENCE_PYTHON')
    if configured: return configured
    root = Path(p4vasp.p4vasp_home)
    for folder in ('.venv-science', legacy):
        for executable in ('bin/python', 'Scripts/python.exe'):
            path = root/folder/executable
            if path.is_file(): return str(path)
    return None

"""Locate the optional bundled model worker and isolate its runtime environment."""
import os
from pathlib import Path
import subprocess
import sys


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

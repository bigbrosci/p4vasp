"""Build/run the native box-selection regression after the Python 3 build.

Requires g++, fltk-config, Python development libraries, and a working display.
Run from any directory: /usr/bin/python3 test/run_box_selection.py
"""
from pathlib import Path
import shlex
import subprocess
import sysconfig
import tempfile

root = Path(__file__).resolve().parents[1]
# Only the production objects named by the build script, not viewer/test mains.
import re
build = (root / 'install/build-unix-py3.sh').read_text()
sources = re.search(r'P4VASP_SOURCES=\((.*?)\)', build, re.S).group(1).split()
objects = [root / 'src' / (Path(s).stem + '.o') for s in sources if s != 'cp4vasp_wrap.cpp']
sources = re.search(r'ODP_SOURCES=\((.*?)\)', build, re.S).group(1).split()
objects += [root / 'odpdom' / (Path(s).stem + '.o') for s in sources]
assert all(p.exists() for p in objects), 'Run install/build-ubuntu-py3.sh first'
fltk = shlex.split(subprocess.check_output(['fltk-config', '--use-gl', '--cxxflags', '--ldflags'], text=True))
python_lib = sysconfig.get_config_var('LDLIBRARY')
python_name = python_lib.removeprefix('lib').split('.so')[0].split('.dylib')[0]
with tempfile.TemporaryDirectory(prefix='p4vasp-box-') as tmp:
    exe = str(Path(tmp) / 'testBoxSelection')
    command = ['g++', '-std=gnu++11', '-DNO_THREADS', '-DNO_GL_LISTS_S', '-DCHECK=1',
               '-I' + str(root / 'src/include'), '-I' + str(root / 'odpdom/include'),
               '-I' + sysconfig.get_path('include'), str(root / 'test/testBoxSelection.cpp'),
               *map(str, objects), *fltk, '-lGLU', '-lGL',
               '-L' + sysconfig.get_config_var('LIBDIR'), '-l' + python_name, '-o', exe]
    subprocess.run(command, check=True)
    subprocess.run([exe, '/tmp/p4vasp-box-drag.ppm', '/tmp/p4vasp-box-selected.ppm'], check=True, timeout=30)

from pathlib import Path
import runpy
import sys

root = Path(SPECPATH).parents[1]
applets = runpy.run_path(str(root / 'lib/p4vasp/applet/appletlist.py'))['appletlist']()
hidden = [name.rsplit('.', 1)[0] for name in applets]
hidden += ['numpy', 'cairo', 'gi.repository.PangoCairo', 'gi.repository.GdkPixbuf',
           'p4vasp.render_studio', 'p4vasp.render_recipe']
a = Analysis(
    [str(root / 'p4v.py')], pathex=[str(root / 'lib')],
    binaries=[], datas=[(str(root / 'data'), 'data'), (str(root / 'LICENSE'), '.'),
                       (str(Path(sys.prefix)/'share/licenses'), 'dependency-licenses')],
    hiddenimports=hidden, hookspath=[],
    runtime_hooks=[str(root / 'install/windows/runtime_hook.py')],
    hooksconfig={'gi': {'versions': {'Gtk': '3.0', 'Gdk': '3.0'},
                        'icons': ['Adwaita', 'hicolor'], 'themes': ['Adwaita'],
                        'languages': ['en', 'zh_CN']}},
    excludes=['tkinter', 'matplotlib', 'scipy'], noarchive=False,
)
pyz = PYZ(a.pure)
gui = EXE(pyz, a.scripts, [], exclude_binaries=True, name='p4vasp',
          debug=False, strip=False, upx=False, console=False)
console = EXE(pyz, a.scripts, [], exclude_binaries=True, name='p4vasp-console',
              debug=False, strip=False, upx=False, console=True)
coll = COLLECT(gui, console, a.binaries, a.datas, strip=False, upx=False, name='p4vasp')

from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs, copy_metadata, collect_delvewheel_libs_directory

root=Path(SPECPATH).parents[1]
datas=collect_data_files('ase')+collect_data_files('rdkit')
binaries=collect_dynamic_libs('rdkit')
datas,binaries=collect_delvewheel_libs_directory('rdkit',datas=datas,binaries=binaries)
for package in ('ase','rdkit','numpy','scipy'):
    datas+=copy_metadata(package)
datas += [(str(root/'LICENSE'),'.')]
python_license=Path(__import__('sys').base_prefix)/'LICENSE.txt'
if python_license.is_file():datas += [(str(python_license),'dependency-licenses/python')]
a=Analysis([str(root/'install/windows/model_worker.py')],pathex=[str(root/'lib')],
    datas=datas,binaries=binaries,hiddenimports=['ase.build','ase.io.vasp','ase.io.extxyz',
        'ase.io.cif','ase.io.proteindatabank','ase.io.mol','ase.io.sdf','ase.io.xsf',
        'ase.io.trajectory','ase.thermochemistry','rdkit.Chem.AllChem'],
    excludes=['gi','cairo','cp4vasp','_cp4vasp','tkinter','matplotlib','PyQt5','PyQt6','PySide6'],noarchive=False)
pyz=PYZ(a.pure)
exe=EXE(pyz,a.scripts,[],exclude_binaries=True,name='p4vasp-model-worker',console=True,strip=False,upx=False)
coll=COLLECT(exe,a.binaries,a.datas,name='p4vasp-model-worker',strip=False,upx=False)

"""Actual ASE replay from artificial structures, with no original input or GUI."""
from io import StringIO
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import numpy as np
from ase.build import bulk
from ase.io import read, write
from p4vasp.ase_surface import build_surface, reposition_result
from p4vasp.surface_replay import surface_contents

ROOT=Path(__file__).resolve().parents[1]
FILES={'POSCAR','surface.json','rebuild_surface.py','rebuild_surface.sh'}


class ReplayTest(unittest.TestCase):
    def test_preset_standalone(self):
        result=build_surface(dict(source='preset',preset='fcc111',symbol='Cu',a=3.61,
                                  layers=4,repeat=[2,2],vacuum=10,fixed_layers=2,layer_tolerance=.3))
        with tempfile.TemporaryDirectory() as name:
            parent=Path(name);script=parent/'rebuild_surface.py'
            script.write_text(surface_contents(result)['rebuild_surface.py'])
            output=parent/'rebuilt'
            subprocess.run([sys.executable,'-I',str(script),'--output',str(output)],check=True,
                           capture_output=True,timeout=60)
            self.same(result,output)

    def same(self,result,folder):
        self.assertEqual({p.name for p in folder.iterdir()},FILES)
        first=read(StringIO(result['poscar']),format='vasp');second=read(folder/'POSCAR')
        self.assertEqual(first.get_chemical_symbols(),second.get_chemical_symbols())
        np.testing.assert_allclose(first.cell.array,second.cell.array,atol=1e-10)
        np.testing.assert_allclose(first.positions,second.positions,atol=1e-10)
        fixed=lambda atoms:sorted(int(i) for c in atoms.constraints for i in c.get_indices())
        self.assertEqual(fixed(first),fixed(second))
        data=json.loads((folder/'surface.json').read_text())
        self.assertEqual(data['layer_numbers'],result['layer_numbers'])
        self.assertEqual(data['request'],result['request'])

    def test_python_and_bash_portable_center_bottom(self):
        env=dict(os.environ)
        for key in ('DISPLAY','WAYLAND_DISPLAY','PYTHONPATH','P4VASP_HOME'):env.pop(key,None)
        env.update(PATH='/usr/bin:/bin',PYTHON='/usr/bin/python3',
                   P4VASP_ASE_PYTHON=sys.executable,P4VASP_SCIENCE_PYTHON=sys.executable)
        with tempfile.TemporaryDirectory(prefix='surface replay ') as name:
            parent=Path(name)
            for placement in ('center','bottom'):
                source=parent/'bulk.cif';write(source,bulk('Cu','fcc',a=3.61,cubic=True))
                result=build_surface(dict(source='file',path=str(source),hkl=[1,1,1],layers=3,
                                          repeat=[2,1],vacuum=8,fixed_layers=1,layer_tolerance=.3))
                result=reposition_result(result,placement);source.unlink()
                saved=parent/placement;saved.mkdir()
                for filename,content in surface_contents(result).items():(saved/filename).write_text(content)
                output=parent/(placement+' python')
                command=[sys.executable,'-I',str(saved/'rebuild_surface.py'),'--output',str(output)]
                run=subprocess.run(command,env=env,capture_output=True,text=True,timeout=60)
                self.assertEqual(run.returncode,0,run.stderr);self.same(result,output)
                self.assertNotEqual(subprocess.run(command,env=env,capture_output=True,timeout=60).returncode,0)
                subprocess.run(['bash','-n',str(saved/'rebuild_surface.sh')],check=True)
                output=parent/(placement+' bash')
                run=subprocess.run(['bash',str(saved/'rebuild_surface.sh'),str(output)],env=env,
                                   capture_output=True,text=True,timeout=90)
                self.assertEqual(run.returncode,0,run.stderr);self.same(result,output)

    def test_invalid_recipe_is_headless_and_does_not_overwrite(self):
        from p4vasp.surface_cli import main
        with tempfile.TemporaryDirectory() as name:
            parent=Path(name);recipe=parent/'surface.json';output=parent/'output';output.mkdir()
            for data in ([],{'request':[]},{'request':{'source':'file'}}):
                recipe.write_text(json.dumps(data));self.assertEqual(main([str(recipe),str(output)]),1)
            self.assertEqual(list(output.iterdir()),[])


if __name__=='__main__':unittest.main()

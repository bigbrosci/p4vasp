"""Data-only recipe validation, shell-safe command generation and headless replay."""
import json
import os
from pathlib import Path
import shlex
import subprocess
import tempfile
import unittest
from p4vasp.render_cli import render, transform
from p4vasp.render_recipe import DEFAULTS, make, save_bundle, bundle_paths, scene_from_source, load

ROOT = Path(__file__).resolve().parents[1]


class RecipeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.output = Path(self.temp.name)/'image with spaces.png'
        self.base = ([[5,0,0],[0,5,0],[0,0,5]],[[0,0,0],[1,0,0],[0,1,1]],['O','H','H'])
        turns = [('x',.37),('y',-.61),('z',.23)]
        columns = [transform(tuple(1 if i == j else 0 for i in range(3)),turns) for j in range(3)]
        matrix = [[columns[j][i] for j in range(3)]+[value] for i,value in enumerate((.3,-.2,.1))]
        matrix.append([0,0,0,1])
        self.camera = dict(matrix=matrix,
                           zoom=1.5,width=320,height=240,perspective=False)
        self.settings = dict(DEFAULTS,size=(320,240),quality=1,cell=False,model='ball-stick')
        self.data = make(self.camera,self.settings,dict(repeat=[2,1,1],hidden=[1]))

    def run_command(self, command):
        env = dict(os.environ,PYTHON='/usr/bin/python3',PYTHONDONTWRITEBYTECODE='1')
        env.pop('DISPLAY',None); env.pop('WAYLAND_DISPLAY',None)
        return subprocess.run(shlex.split(command),env=env,capture_output=True,text=True,timeout=20)

    def test_exact_replay_and_batch_input(self):
        paths = bundle_paths(self.output)
        command = save_bundle(paths,self.output,self.base,self.data)
        scene = scene_from_source(paths[0],self.data['display'])
        self.assertEqual(len(scene[1]),4)
        render(paths[0],self.output,scene=scene,camera=self.camera,
               **{k:v for k,v in self.settings.items() if k not in ('view','turns')})
        expected = self.output.read_bytes()
        result = self.run_command(command)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(expected,self.output.read_bytes())
        other = Path(self.temp.name)/'other POSCAR'
        other.write_text(paths[0].read_text().replace('0 1 1','0 1 2'))
        argv = shlex.split(command); argv[2] = str(other)
        result = self.run_command(shlex.join(argv))
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertTrue(expected != self.output.read_bytes(), 'Changed batch input should change the image')

    def test_explicit_size_overrides_preset(self):
        paths = bundle_paths(self.output)
        command = save_bundle(paths,self.output,self.base,self.data)+' --size 160x120'
        result = self.run_command(command)
        self.assertEqual(result.returncode,0,result.stderr)
        import cairo
        surface = cairo.ImageSurface.create_from_png(str(self.output))
        self.assertEqual((surface.get_width(),surface.get_height()),(160,120))

    def test_validation_and_hidden_index(self):
        path = Path(self.temp.name)/'bad.json'
        for mutation in ('version','matrix','size','quality'):
            data = json.loads(json.dumps(self.data))
            if mutation == 'version': data['version'] = 99
            if mutation == 'matrix': data['camera']['matrix'][0][0] = float('nan')
            if mutation == 'size': data['render']['size'] = [0,240]
            if mutation == 'quality': data['render']['quality'] = 20
            path.write_text(json.dumps(data))
            with self.assertRaises(ValueError): load(path)
        paths = bundle_paths(self.output)
        save_bundle(paths,self.output,self.base,self.data)
        with self.assertRaisesRegex(ValueError,'hidden atom index'):
            scene_from_source(paths[0],dict(repeat=[1,1,1],hidden=[99]))

    def test_bad_preset_or_conflicting_view_keeps_old_image(self):
        paths = bundle_paths(self.output)
        command = save_bundle(paths,self.output,self.base,self.data)
        self.output.write_bytes(b'keep output')
        result = self.run_command(command+' --view side')
        self.assertNotEqual(result.returncode,0)
        self.assertEqual(self.output.read_bytes(),b'keep output')
        paths[1].write_text('{invalid json')
        result = self.run_command(command)
        self.assertNotEqual(result.returncode,0)
        self.assertEqual(self.output.read_bytes(),b'keep output')

    def test_existing_companions_are_preserved(self):
        paths = bundle_paths(self.output)
        paths[0].write_text('unrelated original')
        new_paths = bundle_paths(self.output)
        self.assertNotEqual(paths,new_paths)
        save_bundle(new_paths,self.output,self.base,self.data)
        self.assertEqual(paths[0].read_text(),'unrelated original')
        with self.assertRaises(FileExistsError):
            save_bundle(new_paths,self.output,self.base,self.data)


if __name__ == '__main__': unittest.main()

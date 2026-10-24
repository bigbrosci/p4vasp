"""Headless CLI regression checks; run with PYTHONPATH=lib python3 this_file."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
import cairo
from p4vasp.render_cli import load_structure, rotations, transform, bond_pairs

ROOT = Path(__file__).resolve().parents[1]
POSCAR = 'Water\n1\n6 0 0\n0 6 0\n0 0 6\nO H\n1 2\nCartesian\n3 3 3\n3.76 3.59 3\n2.24 3.59 3\n'


class RenderTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.source = self.folder / 'input POSCAR'
        self.source.write_text(POSCAR)
        self.output = self.folder / 'output image.png'

    def run_cli(self, *args, success=True):
        env = dict(os.environ, PYTHON='/usr/bin/python3', PYTHONDONTWRITEBYTECODE='1')
        env.pop('DISPLAY', None)
        env.pop('WAYLAND_DISPLAY', None)
        result = subprocess.run(['bash', str(ROOT/'p4v.sh'), str(self.source), '-o', str(self.output), *args],
                                env=env, capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode == 0, success, result.stdout + result.stderr)
        self.assertEqual(self.source.read_text(), POSCAR)
        return result

    def test_headless_size_and_background(self):
        self.run_cli('--size', '320x240')
        surface = cairo.ImageSurface.create_from_png(str(self.output))
        self.assertEqual((surface.get_width(), surface.get_height()), (320, 240))
        self.assertEqual(bytes(surface.get_data()[:4]), b'\0'*4)

    def test_white_background(self):
        self.run_cli('--white-background')
        surface = cairo.ImageSurface.create_from_png(str(self.output))
        self.assertEqual(bytes(surface.get_data()[:4]), b'\xff'*4)

    def test_transparent_rotated_view(self):
        self.run_cli('--transparent', '--view', 'side', '--rotate=-30x,20z', '--no-cell')
        surface = cairo.ImageSurface.create_from_png(str(self.output))
        self.assertEqual(bytes(surface.get_data()[:4]), b'\0'*4)
        self.assertGreater(len(set(bytes(surface.get_data()))), 20)

    def test_default_overwrite_and_no_clobber(self):
        self.output.write_bytes(b'keep me')
        self.run_cli('--no-clobber', success=False)
        self.assertEqual(self.output.read_bytes(), b'keep me')
        self.run_cli()
        self.assertTrue(self.output.read_bytes().startswith(b'\x89PNG'))

    def test_invalid_arguments(self):
        for args in [('--rotate', 'bad'), ('--size', '0x20'), ('--radius-scale', '-1')]:
            self.run_cli(*args, success=False)
            self.assertFalse(self.output.exists())

    def test_views_differ(self):
        self.run_cli('--view', 'top')
        first = self.output.read_bytes()
        self.run_cli('--view', 'front', '--force')
        self.assertNotEqual(first, self.output.read_bytes())

    def test_scaling(self):
        for scale, expected in [('2', (6, 6, 6)), ('-1728', (6, 6, 6)), ('2 3 4', (6, 9, 12))]:
            self.source.write_text(POSCAR.replace('\n1\n', '\n'+scale+'\n', 1))
            self.assertEqual(load_structure(self.source)[1][0], expected)
        self.source.write_text(POSCAR.replace('Cartesian', 'Direct').replace('3 3 3', '.5 .5 .5'))
        self.assertEqual(load_structure(self.source)[1][0], (3, 3, 3))

    def test_bond_detection(self):
        self.assertEqual(list(bond_pairs([(0, 0, 0), (1, 0, 0), (5, 0, 0)], [.6]*3, 1.15)), [(0, 1)])
        self.assertEqual(list(bond_pairs([(0, 0, 0), (0, 0, 0)], [.6]*2, 1.15)), [])

    def test_models_and_quality(self):
        outputs = []
        for model in ('spheres', 'ball-stick', 'stick', 'space-filling'):
            self.run_cli('--model', model, '--size', '320x240', '--quality', '3', '--force')
            outputs.append(self.output.read_bytes())
        self.assertEqual(len(set(outputs)), 4)
        self.run_cli('--brightness', '0.7', '--force')
        self.run_cli('--quality', '4', '--size', '8192x1000', '--force', success=False)

    def test_rotation_convention(self):
        p = transform((1, 0, 0), rotations('90z,90x'))
        for actual, expected in zip(p, (0, 0, 1)):
            self.assertAlmostEqual(actual, expected)

    def test_no_ui_imports(self):
        code = '''import sys, runpy
class BlockUI:
    def find_spec(self, fullname, *args):
        if fullname.split('.')[0] in ('gi', 'cp4vasp', '_cp4vasp', 'OpenGL'):
            raise RuntimeError('Unexpected GUI import: '+fullname)
sys.meta_path.insert(0, BlockUI())
sys.argv = ['p4v.py', sys.argv[1], '-o', sys.argv[2]]
runpy.run_path('p4v.py', run_name='__main__')
'''
        result = subprocess.run(['/usr/bin/python3', '-c', code, str(self.source), str(self.output)],
                                cwd=ROOT, capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == '__main__':
    unittest.main()

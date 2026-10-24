"""Surface correctness and export regressions independent of a GUI/display."""
import tempfile
import unittest
from pathlib import Path
import cairo
import numpy as np
from p4vasp.render_studio import intersect, shade
from p4vasp.render_cli import render


class StudioTests(unittest.TestCase):
    def test_surface_depth_and_clipping(self):
        origins = np.array([[0.,0.,5.],[.5,0,5],[2,0,5]])
        rays = np.tile([0.,0.,-1.],(3,1))
        t = intersect(origins,rays,[0,0,0],[0,0,0],1,0,100)
        np.testing.assert_allclose(t[:2],[4,5-np.sqrt(.75)])
        self.assertTrue(np.isinf(t[2]))
        # Front surface clipped; back surface remains, no artificial clipping cap.
        self.assertEqual(intersect(origins[:1],rays[:1],[0,0,0],[0,0,0],1,4.5,100)[0],6)
        self.assertTrue(np.isinf(intersect(origins[:1],rays[:1],[0,0,0],[0,0,0],1,0,3)[0]))

    def test_off_axis_perspective_ray(self):
        origin = np.array([[0.,0.,20.]])
        center = np.array([2.,1.,0.])
        ray = center-origin
        distance = np.linalg.norm(ray)
        ray /= distance
        hit = intersect(origin,ray,center,center,.6,0,100)[0]
        self.assertAlmostEqual(hit,distance-.6)

    def test_capsule_sides_caps_and_parallel_rays(self):
        o = np.array([[0.,0.,5.],[0.,0.,5.],[0.,0.,5.]])
        d = np.tile([0.,0.,-1.],(3,1))
        self.assertEqual(intersect(o[:1],d[:1],[-1,0,0],[1,0,0],.25,0,100)[0],4.75)
        self.assertEqual(intersect(o[:1],d[:1],[0,0,-1],[0,0,1],.25,0,100)[0],3.75)
        self.assertTrue(np.isinf(intersect(o[:1]+[2,0,0],d[:1],[0,0,-1],[0,0,1],.25,0,100)[0]))

    def test_shading_uses_normal_and_finite_highlights(self):
        normals = np.array([[0,0,1.],[0,-1.,0.]])
        colors = np.full((2,3),.5)
        view = np.array([[0,0,1.]]*2)
        rgb = shade(normals,colors,view,'matte',1)
        self.assertGreater(rgb[0,0],rgb[1,0])
        for material in ('matte','classic','glossy'):
            rgb = shade(normals,colors,view,material,10)
            self.assertTrue(np.isfinite(rgb).all())
            self.assertTrue(((rgb>=0)&(rgb<=1)).all())

    def test_large_sphere_hides_nearer_center_and_order_invariance(self):
        # The large red front surface is at z=2, ahead of the small blue sphere.
        from p4vasp import render_cli
        original = render_cli.atom_styles
        render_cli.atom_styles = lambda: {'R':(2,(1,0,0),0),'B':(.5,(0,0,1),0)}
        self.addCleanup(setattr,render_cli,'atom_styles',original)
        with tempfile.TemporaryDirectory() as folder:
            a,b = Path(folder)/'a.png',Path(folder)/'b.png'
            basis = [[5,0,0],[0,5,0],[0,0,5]]
            scene = (basis,[(0,0,0),(0,0,1)],['R','B'])
            render(None,a,scene=scene,radius_scale=1,cell=False,size=(128,128),quality=1)
            surface = cairo.ImageSurface.create_from_png(str(a))
            pixels = np.frombuffer(surface.get_data(),dtype=np.uint32).reshape((128,128))
            color = int(pixels[64,64])
            self.assertGreater((color>>16)&255,color&255)
            render(None,b,scene=(basis,list(reversed(scene[1])),list(reversed(scene[2]))),
                   radius_scale=1,cell=False,size=(128,128),quality=1)
            self.assertEqual(a.read_bytes(),b.read_bytes())

    def test_oblique_perspective_and_cancel_preserve_output(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder)/'out.png'
            output.write_bytes(b'previous image')
            basis = [[5,0,0],[0,5,0],[0,0,5]]
            scene = (basis,[(0,0,0)],['O'])
            camera = dict(matrix=[[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]],zoom=1,
                          width=128,height=128,perspective=True)
            with self.assertRaisesRegex(ValueError,'cancelled'):
                render(None,output,scene=scene,camera=camera,size=(128,128),quality=1,cancelled=lambda:True)
            self.assertEqual(output.read_bytes(),b'previous image')
            render(None,output,scene=scene,camera=camera,size=(128,128),quality=1)
            surface = cairo.ImageSurface.create_from_png(str(output))
            self.assertEqual(bytes(surface.get_data()[:4]),bytes(4))
            self.assertGreater(len(set(bytes(surface.get_data()))),20)


if __name__ == '__main__': unittest.main()

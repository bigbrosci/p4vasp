import unittest
from p4vasp.paint3d.data import *
from p4vasp.paint3d.Paint3DInterface import *

class TestPaint3DInterface(unittest.TestCase):
    def testColorMaterial(self):
        p=Paint3DRecorder()
        p.colorMaterial(Vector(0.5,0.5,0.5))
        self.assertEqual(1,len(p.commands))
        self.assertTrue("ColorMaterial" in str(p.commands[0]))
        self.assertEqual("1",p.commands[0].name)
    def testFrame(self):
        p=Paint3DRecorder()
        p.frame()
        self.assertEqual(1,len(p.commands))
        self.assertTrue("Frame" in str(p.commands[0]))
        self.assertEqual("1",p.commands[0].name)
    def testAmbientLight(self):
        p=Paint3DRecorder()
        p.ambientLight(Vector(0.3,0.3,0.3))
        self.assertEqual(1,len(p.commands))
        self.assertTrue("AmbientLight" in str(p.commands[0]))
        self.assertEqual("1",p.commands[0].name)
    def testBackground(self):
        p=Paint3DRecorder()
        p.background(Vector(0,0,0))
        self.assertEqual(1,len(p.commands))
        self.assertTrue("Background" in str(p.commands[0]))
        self.assertEqual("1",p.commands[0].name)
    def testPointLight(self):
        p=Paint3DRecorder()
        p.pointLight(Vector(0,0,0), Vector(1,1,1))
        self.assertEqual(1,len(p.commands))
        self.assertTrue("PointLight" in str(p.commands[0]))
        self.assertEqual("1",p.commands[0].name)
    def testOrthographicCamera(self):
        p=Paint3DRecorder()
        p.orthographicCamera(Vector(0,0,0), Vector(0,0,1), Vector(1.33,0,0), Vector(0,1,0))
        self.assertEqual(1,len(p.commands))
        self.assertTrue("OrthographicCamera" in str(p.commands[0]))
        self.assertEqual("1",p.commands[0].name)
    def testPerspectiveCamera(self):
        p=Paint3DRecorder()
        p.perspectiveCamera(Vector(0,0,0), Vector(0,0,1), Vector(1.33,0,0), Vector(0,1,0))
        self.assertEqual(1,len(p.commands))
        self.assertTrue("PerspectiveCamera" in str(p.commands[0]))
        self.assertEqual("1",p.commands[0].name)
    def testSphere(self):
        p=Paint3DRecorder()
        p.sphere(Vector(0,0,0), 1.0, None)
        self.assertEqual(1,len(p.commands))
        self.assertTrue("Sphere" in str(p.commands[0]))
        self.assertEqual("1",p.commands[0].name)
    def testCylinder(self):
        p=Paint3DRecorder()
        p.cylinder(Vector(0,0,0), Vector(1,0,0), 1.0, None)
        self.assertEqual(1,len(p.commands))
        self.assertTrue("Cylinder" in str(p.commands[0]))
        self.assertEqual("1",p.commands[0].name)
    def testLine(self):
        p=Paint3DRecorder()
        p.line(Vector(0,0,0), Vector(1,0,0), 1.0, None)
        self.assertEqual(1,len(p.commands))
        self.assertTrue("Line" in str(p.commands[0]))
        self.assertEqual("1",p.commands[0].name)
    def testCone(self):
        p=Paint3DRecorder()
        p.cone(Vector(0,0,0), Vector(10,0,0), 1.0, None)
        self.assertEqual(1,len(p.commands))
        self.assertTrue("Cone" in str(p.commands[0]))
        self.assertEqual("1",p.commands[0].name)
    def testArrow(self):
        p=Paint3DRecorder()
        p.arrow(Vector(0,0,0), Vector(10,0,0), 0.5, 1.0, 2.0, None)
        self.assertEqual(1,len(p.commands))
        self.assertTrue("Arrow" in str(p.commands[0]))
        self.assertEqual("1",p.commands[0].name)
    def testMesh(self):
        p=Paint3DRecorder()
        p.mesh(None, None, None, None)
        self.assertEqual(1,len(p.commands))
        self.assertTrue("Mesh" in str(p.commands[0]))
        self.assertEqual("1",p.commands[0].name)


if __name__ == '__main__':
    unittest.main()

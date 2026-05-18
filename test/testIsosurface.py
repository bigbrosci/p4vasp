#!/usr/bin/python3
import unittest
from p4vasp.isosurface import *
from cp4vasp import *
from tempfile import mkstemp
from os import remove, close
import p4vasp.cStructure
import p4vasp.cmatrix

class TestIsosurface(unittest.TestCase):
    def setUp(self):
        self.paths=[]
    def tearDown(self):
        for p in self.paths:
            remove(p)
    def makeChgcar(self):
        f,path=mkstemp(prefix="CHGCAR",suffix="")
        self.paths.append(path)
        close(f)
        f=open(path,"w+")
        f.write("""test chgcar
1
10 0 0
0 10 0
0 0 10
1
cart
0 0 0

 4 4 4
 0 0 0 0
 0 0 0 0
 0 0 0 0
 0 0 0 0
 0 0 0 0
 0 0.1 0.1 0
 0 0.1 0.1 0
 0 0 0 0
 0 0 0 0
 0 0.1 0.1 0
 0 0.1 0.1 0
 0 0 0 0
 0 0 0 0
 0 0 0 0
 0 0 0 0
 0 0 0 0
""")
        f.close()
        chgcar=Chgcar()
        chgcar.read(path)
        return chgcar

    def testChgcar(self):
        chgcar = self.makeChgcar()
        structure=p4vasp.cStructure.Structure(pointer=chgcar.structure)
        self.assertEqual(chgcar.nx,4)
        self.assertEqual(chgcar.ny,4)
        self.assertEqual(chgcar.nz,4)
        self.assertEqual(len(structure),1)
        self.assertEqual(structure.basis[0][0],10)
        v=p4vasp.cmatrix.Vector()
        chgcar.getGrad(v.pointer,1,1,1)
        self.assertTrue(v[0]+1<0.01)

    def testIsosurface(self):
        chgcar = self.makeChgcar()

        mesh=[]
        for step,total,meshpart in partialIsosurface(chgcar,0.05):
            self.assertEqual(total,chgcar.nx)
            mesh.extend(meshpart)
        self.assertEqual(len(mesh),len(completeIsosurface(chgcar,0.05)))
        for x in mesh:
            self.assertEqual(len(x),6)

    def testMeshFormatConversion1(self):
        mesh=[((1,2,3),(4,5,6),(7,8,9),(10,11,12),(13,14,15),(16,17,18))]
        coordinates,normals,triangles=convertMeshFormat(mesh)
        self.assertEqual(len(mesh),len(triangles))
        self.assertEqual(triangles,[(0,1,2)])
        for i in range(len(mesh)):
            for j in 0,1,2:
                for k in 0,1,2:
                    self.assertEqual(normals[triangles[i][j]][k],mesh[i][j][k])
                    self.assertEqual(coordinates[triangles[i][j]][k],mesh[i][3+j][k])

    def testMeshFormatConversion2(self):
        chgcar = self.makeChgcar()
        mesh=completeIsosurface(chgcar,0.05)
        coordinates,normals,triangles=convertMeshFormat(mesh)
        self.assertEqual(len(mesh),len(triangles))
        for i in range(len(mesh)):
            for j in 0,1,2:
                for k in 0,1,2:
                    self.assertEqual(normals[triangles[i][j]][k],mesh[i][j][k])
                    self.assertEqual(coordinates[triangles[i][j]][k],mesh[i][3+j][k])

if __name__ == '__main__':
    unittest.main()

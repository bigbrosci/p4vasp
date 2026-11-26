#!/usr/bin/python3

#  p4vasp is a GUI-program and a library for processing outputs of the
#  Vienna Ab-inition Simulation Package (VASP)
#  (see http://cms.mpi.univie.ac.at/vasp/Welcome.html)
#
#  Copyright (C) 2003  Orest Dubay <odubay@users.sourceforge.net>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA


from p4vasp.store import *
from p4vasp import *
from p4vasp.applet.Applet import *
from p4vasp.paint3d.OpenGLPaint3D import *
from p4vasp.ConvexShape import *
import p4vasp.Structure
import p4vasp.cStructure
from OpenGL.GLUT import *
from OpenGL.raw.GLUT import glutDestroyWindow as destroy_glut_window
from OpenGL import contextdata
from p4vasp.Dyna import DynaListener,dynaPublisher
from p4vasp.gtk3 import GLib

class KpointsViewerApplet(Applet,DynaListener):
    menupath=["Electronic","View k-points"]
    showmode=Applet.EXTERNAL_ONLY_MODE
    paint=None
    SUPERCELL=1
    PRIMITIVE_CELL=2

    def __init__(self):
        Applet.__init__(self)
        self.celltype=self.PRIMITIVE_CELL
        self.dyna=None
        self._event_source=None
        self._destroyed=False
        self._context=None
        self._menu=None
        dynaPublisher().addListener(self)
    def dynaUpdated(self,dyna):
        self.dyna=dyna
        self.updateSystem()

    def dmenu(self,x):
        print(("MENU",x))
        self.celltype = x
        self.updateSystem()
        return 0

    def createPanel(self):
        return None

    def setExternalMode(self):
        pass
    def setEmbeddedMode(self):
        raise RuntimeError("KpointsViewerApplet.setEmbeddedMode() not supported.")

    def getPaint(self):
        if self.paint is None:
            paint = GLUTPaint3D()
            paint.zoom=0.1
            try:
                paint.glutinit('p4vasp — K-points')
            except Exception:
                if paint.window:
                    destroy_glut_window(paint.window)
                    glutMainLoopEvent()
                raise

            self._menu=glutCreateMenu(self.dmenu)
            glutAddMenuEntry("Supercell", self.SUPERCELL)
            glutAddMenuEntry("Primitive cell", self.PRIMITIVE_CELL)
            glutAttachMenu(GLUT_RIGHT_BUTTON)

            self.paint=paint
            self._context=contextdata.getContext()
            paint.on_close=self.destroyApplet
            glutCloseFunc(self.glutclose)
            self._event_source=GLib.timeout_add(16,self.mainloop)
        glutSetWindow(self.paint.window)
        self.paint.reset()
        return self.paint

    def mainloop(self):
        if self.paint is None:return False
        self.paint.mainloopevent()
        return self.paint is not None

    def glutclose(self):
        # freeglut owns destruction after a window-manager close callback.
        # Never re-enter its event loop or hide/destroy that same window here.
        if self.paint is not None:self.paint.window=None
        self.paint=None
        self.destroyApplet()

    def destroy(self):
        if self._destroyed:return
        self._destroyed=True
        if self._event_source is not None:
            GLib.source_remove(self._event_source);self._event_source=None
        if self._menu is not None:
            glutDestroyMenu(self._menu);self._menu=None
        paint=self.paint;self.paint=None
        if paint is not None and paint.window:
            window=paint.window;paint.window=None
            # The PyOpenGL convenience wrapper drops callback references before
            # freeglut's deferred close callback has run. Keep them alive until
            # the native destruction pass below to avoid a dangling C callback.
            destroy_glut_window(window)
        # freeglut defers native destruction. Drain it on the next GTK turn,
        # outside any GLUT callback; stopping the pump immediately leaves an
        # unresponsive native window until another viewer is opened.
        GLib.idle_add(self._finish_close,self._context)
        if self in dynaPublisher().listeners:dynaPublisher().removeListener(self)

    @staticmethod
    def _finish_close(context,remaining=1):
        glutMainLoopEvent()
        # Explicit destruction queues the close notification first, then native
        # release. Use separate GTK turns for both, never recursive GLUT calls.
        if remaining:GLib.idle_add(KpointsViewerApplet._finish_close,context,remaining-1)
        elif context:contextdata.cleanupContext(context)
        return False

    def updateSystem(self,x=None):
        if self.celltype == self.SUPERCELL:
            msg().message("Show supercell")
            structure=self.system.INITIAL_STRUCTURE
        elif self.celltype == self.PRIMITIVE_CELL:
            msg().message("Show primitive cell")
            structure=self.system.PRIMITIVE_STRUCTURE
            if structure is None:
                msg().error("Primitive cell not available, showing supercell")
                structure=self.system.INITIAL_STRUCTURE
                self.celltype = self.SUPERCELL

        structure.updateRecipBasis()

        BrillouinZone=ConvexShape()
        b=structure.rbasis
        b[0]=10*b[0]
        b[1]=10*b[1]
        b[2]=10*b[2]

        BrillouinZone.cell(b)

        paint=self.getPaint()
        paint.colorMaterial(Vector(1,0,0),"Red")
        paint.colorMaterial(Vector(0,1,0),"Green")
        paint.colorMaterial(Vector(0,0,1),"Blue")
        paint.colorMaterial(Vector(1,0.5,0),"Orange")
        paint.background(Vector(0.4,0.4,0.7))
        paint.ambientLight(Vector(.5,.5,.5))
        paint.pointLight(Vector(-80,0,10),Vector(1,1,1))
        factor=40
        paint.orthographicCamera(Vector(-80,80,0),Vector(0,0,-20),Vector(3.2,0,0)*factor,Vector(0,0,2)*factor)

        if self.celltype == self.SUPERCELL:
            for i in (-2,-1,0,1,2):
                for j in (-2,-1,0,1,2):
                    for k in (-2,-1,0,1,2):
                        v=b[0]*float(i)+b[1]*float(j)+b[2]*float(k)
                        paint.sphere(v,0.05,"Blue")

            for u in self.system.KPOINT_LIST:
                v=b[0]*u[0]+b[1]*u[1]+b[2]*u[2]
                paint.sphere(v,0.1,"Green")

        if self.dyna is not None:
            for u1,u2 in self.dyna.segments:
                v1=b[0]*u1[0]+b[1]*u1[1]+b[2]*u1[2]
                v2=b[0]*u2[0]+b[1]*u2[1]+b[2]*u2[2]
                paint.line(v1,v2,material="Orange")

        GN=0
        for i,j,k in self.indices():
            v=(b[0]*float(i)+b[1]*float(j)+b[2]*float(k))*0.5
            BrillouinZone.clip(v,v)
        BrillouinZone.paint(paint,0.05,"Red")
        glutPostRedisplay()

    def indices(self):
        for i in (-1,0,1):
            for j in (-1,0,1):
                for k in (-1,0,1):
                    if i==0 and j==0 and k==0:
                        continue
                    yield i,j,k


KpointsViewerApplet.store_profile=AppletProfile(KpointsViewerApplet,tagname="KpoinsViewer",
attr_setup="""
""")

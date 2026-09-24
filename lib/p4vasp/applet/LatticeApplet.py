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


from p4vasp.util import ParseException
from p4vasp import *
from p4vasp.matrix import *
from p4vasp.store import *
from p4vasp.applet.Applet import *
from p4vasp.SystemPM import *
from p4vasp import gtk3 as gtk
from p4vasp.gtk3 import gobject
from p4vasp.gtk3 import pango
from math import *

class LatticeApplet(Applet):
    menupath=["Structure","Lattice"]
    showmode=Applet.EXTERNAL_MODE

    def __init__(self):
        Applet.__init__(self)
        self.gladefile="lattice.glade"
        self.gladename="applet_frame"
        self.allow_parameters_update=True
        self.allow_cell_update=True
        self.in_apply=False

    def updateSystem(self,x=None):
        pass

    def on_triclinic_radiobutton_toggled_handler(self,w,*arg):
        if w.get_active():
            self.widgets.a_entry.set_sensitive(True)
            self.widgets.b_entry.set_sensitive(True)
            self.widgets.c_entry.set_sensitive(True)
            self.widgets.alpha_entry.set_sensitive(True)
            self.widgets.beta_entry.set_sensitive(True)
            self.widgets.gamma_entry.set_sensitive(True)
    def on_monoclinic_radiobutton_toggled_handler(self,w,*arg):
        if w.get_active():
            self.toMonoclinic()
    def on_orthorhombic_radiobutton_toggled_handler(self,w,*arg):
        if w.get_active():
            self.toOrthorhombic()
    def on_tetragonal_radiobutton_toggled_handler(self,w,*arg):
        if w.get_active():
            self.toTetragonal()
    def on_rhombohedral_radiobutton_toggled_handler(self,w,*arg):
        if w.get_active():
            self.toRhombohedral()
    def on_hexagonal_radiobutton_toggled_handler(self,w,*arg):
        if w.get_active():
            self.toHexagonal()
    def on_cubic_radiobutton_toggled_handler(self,w,*arg):
        if w.get_active():
            self.toCubic()

    def on_parameter_updated_handler(self,*arg):
        if self.allow_parameters_update:
            self.allow_parameters_update=False
            try:
                self.fixParameters()
                self.updateCell()
            finally:
                self.allow_parameters_update=True

    def on_cell_updated_handler(self,*arg):
        if self.allow_cell_update:
            self.allow_cell_update=False
            try:
                self.updateParameters()
            finally:
                self.allow_cell_update=True

    def on_apply_button_clicked_handler(self,*arg):
        b1,b2,b3 = self.getCell()
        s=self.getCurrentStructure()
        s.basis[0]=b1
        s.basis[1]=b2
        s.basis[2]=b3
        self.in_apply=True
        systemlist().notifySystemChanged()
        self.in_apply=False

    def fixParameters(self):
        if self.widgets.monoclinic_radiobutton.get_active():
            self.toMonoclinic()
        if self.widgets.orthorhombic_radiobutton.get_active():
            self.toOrthorhombic()
        if self.widgets.tetragonal_radiobutton.get_active():
            self.toTetragonal()
        if self.widgets.rhombohedral_radiobutton.get_active():
            self.toRhombohedral()
        if self.widgets.hexagonal_radiobutton.get_active():
            self.toHexagonal()
        if self.widgets.cubic_radiobutton.get_active():
            self.toCubic()
    def toMonoclinic(self):
        self.widgets.a_entry.set_sensitive(True)
        self.widgets.b_entry.set_sensitive(True)
        self.widgets.c_entry.set_sensitive(True)
        self.widgets.alpha_entry.set_sensitive(False)
        self.widgets.beta_entry.set_sensitive(True)
        self.widgets.gamma_entry.set_sensitive(False)
        a=self.widgets.a_entry.get_text()
        self.widgets.b_entry.set_text(a)
        self.widgets.c_entry.set_text(a)
        self.widgets.alpha_entry.set_text("90")
        self.widgets.gamma_entry.set_text("90")
        self.updateCell()
    def toOrthorhombic(self):
        self.widgets.a_entry.set_sensitive(True)
        self.widgets.b_entry.set_sensitive(True)
        self.widgets.c_entry.set_sensitive(True)
        self.widgets.alpha_entry.set_sensitive(False)
        self.widgets.beta_entry.set_sensitive(False)
        self.widgets.gamma_entry.set_sensitive(False)
        self.widgets.alpha_entry.set_text("90")
        self.widgets.beta_entry.set_text("90")
        self.widgets.gamma_entry.set_text("90")
        self.updateCell()
    def toTetragonal(self):
        self.widgets.a_entry.set_sensitive(True)
        self.widgets.b_entry.set_sensitive(False)
        self.widgets.c_entry.set_sensitive(True)
        self.widgets.alpha_entry.set_sensitive(False)
        self.widgets.beta_entry.set_sensitive(False)
        self.widgets.gamma_entry.set_sensitive(False)
        a=self.widgets.a_entry.get_text()
        self.widgets.b_entry.set_text(a)
        self.widgets.alpha_entry.set_text("90")
        self.widgets.beta_entry.set_text("90")
        self.widgets.gamma_entry.set_text("90")
        self.updateCell()
    def toRhombohedral(self):
        self.widgets.a_entry.set_sensitive(True)
        self.widgets.b_entry.set_sensitive(False)
        self.widgets.c_entry.set_sensitive(False)
        self.widgets.alpha_entry.set_sensitive(True)
        self.widgets.beta_entry.set_sensitive(True)
        self.widgets.gamma_entry.set_sensitive(True)
        a=self.widgets.a_entry.get_text()
        self.widgets.b_entry.set_text(a)
        self.widgets.c_entry.set_text(a)
        self.updateCell()
    def toHexagonal(self):
        self.widgets.a_entry.set_sensitive(True)
        self.widgets.b_entry.set_sensitive(False)
        self.widgets.c_entry.set_sensitive(True)
        self.widgets.alpha_entry.set_sensitive(False)
        self.widgets.beta_entry.set_sensitive(False)
        self.widgets.gamma_entry.set_sensitive(False)
        a=self.widgets.a_entry.get_text()
        self.widgets.b_entry.set_text(a)
        self.widgets.alpha_entry.set_text("90")
        self.widgets.beta_entry.set_text("90")
        self.widgets.gamma_entry.set_text("120")
        self.updateCell()
    def toCubic(self):
        self.widgets.a_entry.set_sensitive(True)
        self.widgets.b_entry.set_sensitive(False)
        self.widgets.c_entry.set_sensitive(False)
        self.widgets.alpha_entry.set_sensitive(False)
        self.widgets.beta_entry.set_sensitive(False)
        self.widgets.gamma_entry.set_sensitive(False)
        a=self.widgets.a_entry.get_text()
        self.widgets.b_entry.set_text(a)
        self.widgets.c_entry.set_text(a)
        self.widgets.alpha_entry.set_text("90")
        self.widgets.beta_entry.set_text("90")
        self.widgets.gamma_entry.set_text("90")
        self.updateCell()

    def getParameter(self,name):
        return self.getValue(name+"_entry")
    def getValue(self,name):
        txt=self.xml.get_widget(name).get_text()
        try:
            return float(eval(txt))
        except:
            return 0.0
    def updateCell(self):
        a=self.getParameter("a")
        b=self.getParameter("b")
        c=self.getParameter("c")
        alpha=self.getParameter("alpha")*pi/180
        beta=self.getParameter("beta")*pi/180
        gamma=self.getParameter("gamma")*pi/180

        cosA=cos(alpha)
        cosB=cos(beta)
        cosC=cos(gamma)
        sinC=sin(gamma)

        b1=Vector(a,0.0,0.0)
        b2=Vector(cosC,sinC,0.0)*b
        try:
            x=cosB
            y=(cosA-cosB*cosC)/sinC
            z=sqrt(1.0-x*x-y*y)
            b3=Vector(x,y,z)*c
        except:
            b3=Vector(0.0,0.0,0.0)
        self.setBasis((b1,b2,b3))

    def updateSystem(self,x=None):
        if not self.in_apply:
            s=self.getCurrentStructure()
            if s is not None and self.xml is not None:
                self.setBasis(s.basis)
                self.updateParameters()

    def setBasis(self,basis):
        previous=self.allow_cell_update
        self.allow_cell_update=False
        try:
            for i in range(3):
                for j in range(3):
                    self.xml.get_widget("a%d%d"%(i+1,j+1)).set_text("%17.15f"%basis[i][j])
        finally:
            self.allow_cell_update=previous

    def getCurrentStructure(self):
        s=getCurrentSystemPM()
        if s is not None:
            return s.INITIAL_STRUCTURE
    def getCell(self):
        b1=Vector(self.getValue("a11"),self.getValue("a12"),self.getValue("a13"))
        b2=Vector(self.getValue("a21"),self.getValue("a22"),self.getValue("a23"))
        b3=Vector(self.getValue("a31"),self.getValue("a32"),self.getValue("a33"))
        return (b1,b2,b3)
    def updateParameters(self):
        b1,b2,b3 = self.getCell()
        a,b,c = b1.length(),b2.length(),b3.length()
        if min(a,b,c) == 0:
            return  # A cell entry can be temporarily empty while typing.
        previous=self.allow_parameters_update
        self.allow_parameters_update=False
        try:
            self.widgets.triclinic_radiobutton.set_active(True)
            values=(a,b,c,b2.angle(b3)*180/pi,b3.angle(b1)*180/pi,b1.angle(b2)*180/pi)
            for name,value in zip(("a","b","c","alpha","beta","gamma"),values):
                self.xml.get_widget(name+"_entry").set_text(str(value))
        finally:
            self.allow_parameters_update=previous

    def initUI(self):
        pass

#BuilderApplet.store_profile=AppletProfile(BuilderApplet,tagname="Builder")

"""Cairo Show window with the existing Control/sequence interface.

The native backend is created lazily only for volumetric isosurfaces/perspective.
"""
import math
import struct
from pathlib import Path
from types import SimpleNamespace
import cairo
from p4vasp.gtk3 import Gtk
from p4vasp.applet.StructurePreviewApplet import StructurePreviewApplet
from p4vasp.gtk3.mode_view import _show_rotation
from p4vasp.Selection import selection
from p4vasp.matrix import Matrix
from p4vasp.viewer_style import RADIUS_FACTOR,BOND_FACTOR,BOND_COLOR,BOND_RADIUS


class ShowController(StructurePreviewApplet):
    def __init__(self,window):
        super().__init__();self.window_adapter=window
    def display_source(self):return self.window_adapter.structure
    def updateSystem(self,*args):
        super().updateSystem(*args)
        if self.summary.get_text().startswith('Preview unavailable:'):
            self.summary.set_text(self.summary.get_text().replace('Use Show to inspect the structure.','Use Control → Perspective for the dedicated renderer.'))
    def editable_source(self):
        owner=self.window_adapter.owner
        if owner.sequencetype!=owner.INITIAL_SEQUENCE:
            from p4vasp import msg
            msg().status('Keyboard editing is available for the initial structure only.')
            return None
        return owner.system.INITIAL_STRUCTURE if owner.system is not None else None


class Records:
    def __init__(self,records=()):self.records=list(records)
    def len(self):return len(self.records)
    def getRecord(self,i):return self.records[i]


class Drawer:
    def __init__(self,window):
        self.window=window;self.info=Records();self.showcellflag=True
        self.cell_red=self.cell_green=self.cell_blue=0.;self.cell_line_width=1
        self.bond_factor=BOND_FACTOR;self.bond_color=BOND_COLOR;self.bond_radius=BOND_RADIUS
    def setBondFactor(self,value):self.bond_factor=value;self.window.updateStructure()
    def getBondFactor(self):return self.bond_factor
    def setBondColor(self,*color):self.bond_color=color;self.window.updateStructure()
    def setBondRadius(self,value):self.bond_radius=value;self.window.updateStructure()
    def getRadiusFactor(self):return self.window.getRadiusFactor()
    def setRadiusFactor(self,value):self.window.setRadiusFactor(value)
    def getWidth(self):return self.window.win.w
    def getHeight(self):return self.window.win.h


class Navigator:
    def __init__(self,window):self.window=window
    def rotation(self,x=0,y=0,z=0):
        self.window.view.rotation=_show_rotation(x,y,z);self.window.redraw()
    def setFrontView(self):self.rotation()
    def setBackView(self):self.rotation(y=math.pi)
    def setLeftView(self):self.rotation(y=math.pi/2)
    def setRightView(self):self.rotation(y=-math.pi/2)
    def setTopView(self):self.rotation(x=-math.pi/2)
    def setBottomView(self):self.rotation(x=math.pi/2)
    def setHome(self):self.rotation();self.window.fitToStructure()
    def setZoom(self,value):self.window.view.zoom=float(value);self.window.redraw()
    def mulZoom(self,value):self.setZoom(self.window.view.zoom*value)
    def getZoom(self):
        return self.window.view.projection_scale()*.04 if self.window.view.data else 1.
    def getPerspective(self):return bool(self.window._legacy and self.window._perspective)
    def setPerspective(self,value):
        self.window._perspective=bool(value)
        if value:self.window.advanced().navigator.setPerspective(1)
        elif self.window._legacy:
            self.window._legacy.navigator.setPerspective(0)
            if self.window.chgcar is None:self.window.return_to_cairo()
    def getRotMatElement(self,i,j):return self.window.getRotmat()[i][j]


class WindowHandle:
    """Small window API retained by Control's screenshot/resize actions."""
    def __init__(self,owner):self.owner=owner
    @property
    def this(self):
        return self.owner._legacy.win.this if self.owner._legacy_visible else None
    @property
    def x(self):return self.owner.widget.get_position()[0]
    @property
    def y(self):return self.owner.widget.get_position()[1]
    @property
    def w(self):return self.owner.view.get_allocated_width()
    @property
    def h(self):return self.owner.view.get_allocated_height()
    def redraw(self):self.owner.redraw()
    def hide(self):self.owner.hide()
    def show(self):self.owner.show()
    def resize(self,x,y,w,h):self.owner.widget.resize(w,h)
    def saveScreenshot(self,path):
        view=self.owner.view;w,h=max(1,self.w),max(1,self.h)
        surface=cairo.ImageSurface(cairo.FORMAT_ARGB32,w,h);view.draw(cairo.Context(surface));surface.flush()
        if str(path).lower().endswith('.tga'):
            data=bytes(surface.get_data());stride=surface.get_stride()
            pixels=b''.join(data[y*stride:y*stride+w*4] for y in range(h))
            Path(path).write_bytes(struct.pack('<BBBHHBHHHHBB',0,0,2,0,0,0,0,0,w,h,32,0x28)+pixels)
        else:surface.write_to_png(str(path))


class CairoStructureWindow:
    def __init__(self,owner,x=0,y=0,w=500,h=400,title='p4vasp Structure',atomtypes=None):
        self.owner=owner;self.atomtypes=atomtypes;self.structure=None;self.visible=True
        self._legacy=None;self._legacy_visible=False;self._perspective=False
        self._needs_initial_fit=True;self._radius_factor=RADIUS_FACTOR;self.multiple=(1,1,1)
        self._last_multiple=(1,1,1)
        self.chgcar=None;self.dsx=self.dsy=self.dsz=2;self._arrows=None;self._arrow_scale=1.
        self.structure_drawer=Drawer(self);self.navigator=Navigator(self)
        self.arrows_drawer=SimpleNamespace(red=.5,green=1.,blue=.5,arrow_radius=.1,arrowhead_radius=.2,arrowhead_length=.2)
        self.controller=ShowController(self);self.widget=Gtk.Window(title=title)
        self.widget.set_default_size(w,h);self.widget.add(self.controller.createPanel())
        self.view=self.controller.view;self.view.repeat_limit=10;self.view.centered_images=True;self.view.wrap_positions=False;self.win=WindowHandle(self)
        self.widget.connect('delete-event',self.closed)
        self.widget.connect('focus-in-event',self.activated)
        self.view.connect_after('draw',self.draw_arrows)
        self.widget.show_all()
    def activated(self,*_):
        from p4vasp.applet import applets,getAppletFrame
        frame=getAppletFrame()
        # Focus restoration after File/Save is not an explicit Show action.
        # Do not destroy the embedded editor when the WM restores this window.
        if frame and getattr(frame.embedded_applet,'startup_preview',False):return False
        if self.owner in applets():applets().activate(self.owner)
        return False
    def closed(self,*_):
        self.owner.destroyApplet();return True
    def destroy(self):
        if self._legacy:self._legacy.hide()
        self.widget.destroy();self.visible=False
    def show(self):
        self.visible=True
        if self._legacy_visible:self._legacy.show()
        else:self.widget.show_all();self.widget.present()
    def hide(self):
        self.widget.hide();self.visible=False
        if self._legacy:self._legacy.hide()
    def setStructure(self,structure):
        if structure is not None and len(structure):
            from p4vasp.cStructure import Structure as NativeStructure
            from p4vasp.Structure import Structure
            from p4vasp.Array import VArray
            from p4vasp.matrix import Vector
            physical=Structure(structure)
            native=NativeStructure(structure);native.correctScaling()
            physical.basis=VArray([Vector(list(v)) for v in native.basis])
            physical.positions=VArray([Vector(list(p)) for p in native])
            physical.scaling=[1.];physical.coordinates='Direct' if native.isDirect() else 'Cartesian';physical.updateRecipBasis()
            if self.owner.cell_centering!=self.owner.CELL_CENTERING_ZERO:physical.toUnitCell()
            structure=physical
        self.structure=structure
        records=[]
        if structure is not None:
            hidden=set(self.getHiddenAtoms())
            for i in range(len(structure)):
                records.append(SimpleNamespace(hidden=int(i in hidden)))
        self.structure_drawer.info=Records(records)
        self.controller.system=self.owner.system
        self.controller._source=structure
        self.controller.updateSystem()
        if self._needs_initial_fit and self.view.data:self.view.fit()
        self._needs_initial_fit=False
        self.updateStructure()
        if self._legacy_visible:self._legacy.setStructure(structure)
    def updateStructure(self):
        if not hasattr(self,'view') or not self.view.data:return
        self.view.radius_factor=self._radius_factor
        self.view.bond_factor=self.structure_drawer.bond_factor
        self.view.bond_color=self.structure_drawer.bond_color;self.view.bond_radius=self.structure_drawer.bond_radius
        from p4vasp.periodic_preview import bonds
        if self.view.repeats!=self.multiple:
            camera=(self.view.rotation,self.view.pan,self.view.zoom,self.view.center,self.view.extent)
            self.view.set_repeats(self.multiple)
            if self._last_multiple==self.multiple:
                self.view.rotation,self.view.pan,self.view.zoom,self.view.center,self.view.extent=camera
        self._last_multiple=self.multiple
        self.view.bonds=bonds(self.view.display_positions(),[self.view.radii[i] for i in self.view.indices],self.view.bond_factor)
        self.view.hidden=set(self.getHiddenAtoms());self.redraw()
    def redraw(self):
        if hasattr(self,'view'):self.view.queue_draw()
        if self._legacy_visible:self._legacy.redraw()
    def fitToStructure(self,include_cell=False):
        if self.view.data:self.view.fit();self.redraw();return True
        return False
    def setMultiple(self,a,b,c):
        multiple=(int(a),int(b),int(c))
        if self.view.data:
            try:
                from p4vasp.periodic_preview import geometry
                geometry(self.view.positions,self.view.data['cell'],multiple,max_repeat=10)
            except ValueError as error:
                from p4vasp import msg
                msg().status(str(error));return
        self.multiple=multiple;self.updateStructure()
        if self._legacy_visible:self._legacy.setMultiple(*self.multiple)
    def getMultiple(self):return self.multiple
    def setRadiusFactor(self,value):self._radius_factor=float(value);self.updateStructure()
    def getRadiusFactor(self):return self._radius_factor
    def showCell(self,value):
        self.structure_drawer.showcellflag=bool(value);self.view.set_cell_visible(value)
        if self._legacy_visible:self._legacy.showCell(value)
    def setCellColor(self,r,g,b):
        self.structure_drawer.cell_red,self.structure_drawer.cell_green,self.structure_drawer.cell_blue=r,g,b
        self.view.cell_color=(r,g,b);self.redraw()
    def setBackground(self,r,g,b):self.view.background=(r,g,b);self.redraw()
    def getBackground(self):return getattr(self.view,'background',(1.,1.,1.))
    def getHiddenAtoms(self):return [i for i,r in enumerate(self.structure_drawer.info.records) if r.hidden]
    def setHiddenAtoms(self,indices):
        indices=set(indices)
        for i,r in enumerate(self.structure_drawer.info.records):r.hidden=int(i in indices)
        self.updateStructure()
    def removeSelectedAll(self):self.view.queue_draw()
    def selectAtom(self,*_):self.view.queue_draw()
    def deselectAtom(self,*_):self.view.queue_draw()
    def getSelectedCount(self):return len(selection())
    def getSelected(self,i):
        atom,nx,ny,nz=selection()[i];return SimpleNamespace(atom=atom,nx=nx,ny=ny,nz=nz)
    def setArrows(self,arrows=None):self._arrows=arrows;self.redraw()
    def setArrowsScale(self,value):self._arrow_scale=float(value);self.redraw()
    def getArrowsScale(self):return self._arrow_scale
    def draw_arrows(self,widget,cr):
        if not self.view.data or self._arrows is None:return False
        cr.set_source_rgb(self.arrows_drawer.red,self.arrows_drawer.green,self.arrows_drawer.blue);cr.set_line_width(2.)
        for i,p in zip(self.view.indices,self.view.display_positions()):
            if i>=len(self._arrows) or i in self.view.hidden:continue
            q=[p[j]+self._arrow_scale*self._arrows[i][j] for j in range(3)]
            x,y,_=self.view.project(p);a,b,_=self.view.project(q)
            if math.hypot(a-x,b-y)<1e-6:continue
            angle=math.atan2(b-y,a-x)
            cr.new_path();cr.move_to(x,y);cr.line_to(a,b)
            for side in (-1,1):
                cr.move_to(a,b);cr.line_to(a-7*math.cos(angle+side*.4),b-7*math.sin(angle+side*.4))
            cr.stroke()
        return False
    def getRotmat(self):
        if not self.view.data:return Matrix([[int(i==j) for j in range(4)] for i in range(4)])
        r=self.view.rotation;zoom=self.navigator.getZoom()
        translation=[-zoom*sum(r[i][j]*self.view.center[j] for j in range(3)) for i in range(3)]
        translation[0]+=self.view.pan[0]*.04;translation[1]+=self.view.pan[1]*.04
        return Matrix([list(r[i])+[translation[i]] for i in range(3)]+[[0.,0.,0.,1.]])
    def advanced(self):
        if self._legacy is None:
            from p4vasp.StructureWindow import StructureWindow
            adapter=self
            class VolumeWindow(StructureWindow):
                def setChgcar(native,value,update_structure=0):
                    super().setChgcar(value,update_structure)
                    adapter.chgcar=native.chgcar
                    if value is None and not native.navigator.getPerspective():adapter.return_to_cairo()
            class VolumeNavigator:
                def __init__(proxy,nav):proxy.nav=nav
                def __getattr__(proxy,name):return getattr(proxy.nav,name)
                def setPerspective(proxy,value):
                    proxy.nav.setPerspective(value)
                    if not value and adapter._legacy.chgcar is None:adapter.return_to_cairo()
            self._legacy=VolumeWindow(title='p4vasp — volume/perspective',atomtypes=self.atomtypes)
            self._legacy.navigator=VolumeNavigator(self._legacy.navigator)
        self._legacy.setStructure(self.structure);self._legacy.setMultiple(*self.multiple)
        self._legacy.setRadiusFactor(self._radius_factor);self._legacy.win.show()
        self._legacy.setHiddenAtoms(self.getHiddenAtoms());self._legacy.setArrows(self._arrows)
        self._legacy.setArrowsScale(self._arrow_scale);self._legacy.showCell(self.view.show_cell)
        self._legacy.setBackground(*self.getBackground())
        drawer=self.structure_drawer;self._legacy.setCellColor(drawer.cell_red,drawer.cell_green,drawer.cell_blue)
        self.widget.hide();self._legacy_visible=True;self.owner.swin=self._legacy
        from p4vasp import msg
        msg().status('Volume/perspective uses the dedicated OpenGL renderer; ordinary Show uses Cairo.')
        return self._legacy
    def return_to_cairo(self):
        legacy=self._legacy;camera=None
        if legacy:
            self._radius_factor=legacy.getRadiusFactor();self.multiple=legacy.getMultiple()
            self._arrow_scale=legacy.getArrowsScale()
            self.setHiddenAtoms([i for i in range(legacy.structure_drawer.info.len()) if legacy.structure_drawer.info.getRecord(i).hidden])
            self.showCell(legacy.structure_drawer.showcellflag)
            self.setBackground(*legacy.getBackground())
            drawer=legacy.structure_drawer;self.setCellColor(drawer.cell_red,drawer.cell_green,drawer.cell_blue)
            camera=([[legacy.navigator.getRotMatElement(i,j) for j in range(4)] for i in range(4)],legacy.navigator.getZoom())
            legacy.win.hide()
        self._legacy_visible=False;self._perspective=False;self.owner.swin=self
        self.widget.show_all();self.owner.updateSeq()
        if camera and self.view.data:
            matrix,zoom=camera
            scale=self.view.projection_scale()/self.view.zoom
            self.view.rotation=tuple(tuple(row[:3]) for row in matrix[:3])
            self.view.zoom=zoom/(scale*.04)
            self.view.pan=tuple(25*(matrix[i][3]+zoom*sum(matrix[i][j]*self.view.center[j] for j in range(3))) if i<2 else 0. for i in range(3))
            self.redraw()
    def setChgcar(self,value,update_structure=0):
        if value is not None:
            legacy=self.advanced();legacy.dsx,legacy.dsy,legacy.dsz=self.dsx,self.dsy,self.dsz
            legacy.setChgcar(value,update_structure);self.chgcar=legacy.chgcar
        else:
            self.chgcar=None
            if self._legacy:self._legacy.setChgcar(None)
            if not self._perspective:self.return_to_cairo()
    def setIsosurfaceLevel(self,value):self.advanced().setIsosurfaceLevel(value)
    def getIsosurfaceLevel(self):return self._legacy.getIsosurfaceLevel() if self._legacy else 0.
    def setDrawIsosurfaceAsPoints(self,value):self.advanced().setDrawIsosurfaceAsPoints(value)
    def getDrawIsosurfaceAsPoints(self):return self._legacy.getDrawIsosurfaceAsPoints() if self._legacy else False

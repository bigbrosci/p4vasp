"""Embedded initial-structure viewer sharing selection and scientific edit helpers."""
from collections import Counter
from p4vasp.applet.Applet import Applet
from p4vasp.gtk3 import Gtk
from p4vasp.gtk3.structure_view import StructureView, structure_data
from p4vasp.Selection import SelectionListener,selection


class StructurePreviewApplet(Applet,SelectionListener):
    menupath=None
    showmode=Applet.EMBEDDED_ONLY_MODE
    startup_preview=True

    def __init__(self):
        super().__init__()
        self.required=['INITIAL_STRUCTURE']
        self._source=None

    def createPanel(self):
        self.panel=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=5)
        self.view=StructureView(self);self.view.set_hexpand(True);self.view.set_vexpand(True)
        self.panel.pack_start(self.view,True,True,0)
        self.summary=Gtk.Label(xalign=0);self.summary.set_margin_start(8)
        self.summary.set_margin_bottom(5);self.summary.set_line_wrap(True)
        self.panel.pack_start(self.summary,False,False,0)
        self.panel.show_all()
        return self.panel

    def notifyAtomSelection(self,sel,origin):
        if self.panel is None:return
        self.view.queue_draw()
        if self.view.data:
            symbols=self.view.data['symbols']
            selected={}
            for index in sorted(set(sel.getAtoms())):
                if 0<=index<len(symbols):
                    selected.setdefault(symbols[index],[]).append(str(index))
            indices=' | '.join(f"{symbol}: {', '.join(atoms)}" for symbol,atoms in selected.items())
            self.summary.set_text('  '.join('%s: %d'%item for item in Counter(symbols).items())+
                                 '     Selected: '+(indices or '0'))

    def edit(self,operation,direction=None):
        from p4vasp.atom_movement import delete_selected,move_selected,rotate_selected
        from p4vasp.applet import applets
        from p4vasp import msg
        if self.panel is None or self.system is None or self.view.data is None:return
        source=self.editable_source()
        if source is None:return
        indices=selection().getAtoms()
        try:
            if operation=='delete':changed=delete_selected(source,indices,len(source))
            elif operation=='move':changed=move_selected(source,indices,direction)
            else:changed=rotate_selected(source,indices,direction) is not None
        except ValueError as error:
            msg().status(str(error));return
        if not changed:return
        if operation=='delete':selection().setSelection([]);selection().notify(self)
        for applet in list(applets()):
            if getattr(applet,'system',None) is self.system:applet.updateSystem()
        self.notifyAtomSelection(selection(),self)
        msg().status('Structure edited. Use File → Save to save the current structure.')

    def editable_source(self):
        source=self.system.INITIAL_STRUCTURE
        return source if source is self._source else None

    def display_source(self):
        return self.system.INITIAL_STRUCTURE

    def updateSystem(self,*_):
        if self.panel is None:return
        self.view.data=None;self.view.queue_draw()
        self.summary.set_text('Open a structure to preview it here.')
        if self.system is None:return
        try:
            source=self.display_source()
            same=source is self._source
            camera=(self.view.rotation,self.view.pan,self.view.zoom,getattr(self.view,'center',None),getattr(self.view,'extent',None))
            if not same:
                selection().setSelection([]);selection().notify(self)
            self._source=source
            self.view.box=None;self.view.drag=None
            if source is None or not len(source):return
            self.view.set_data(structure_data(source))
            if same and camera[3] is not None:
                self.view.rotation,self.view.pan,self.view.zoom,self.view.center,self.view.extent=camera
            self.notifyAtomSelection(selection(),self)
        except (ValueError,TypeError,AttributeError,IndexError,ZeroDivisionError,OverflowError) as error:
            self.view.data=None;self.view.queue_draw()
            self.summary.set_text('Preview unavailable: '+str(error)+'. Use Show to inspect the structure.')

"""Local XYZ library, unchanged-geometry preview and gas input export."""
from io import StringIO
from pathlib import Path
import re
from p4vasp.gtk3 import Gtk
from p4vasp.gtk3.file_dialogs import entry
from p4vasp.gtk3.single_atom import InputFolderDialog
from p4vasp.gas_phase_inputs import library_path, scan_library, suggested_cell, poscar, input_contents, write_inputs


# One session-owned auxiliary window avoids dangling asynchronous FLTK events.
_shared_preview = None


def handle_preview_event(event):
    """Keep auxiliary preview close/selection events out of the active system."""
    if _shared_preview is None: return False
    import cp4vasp
    if event.type in (cp4vasp.BE_SELECTED, cp4vasp.BE_DESELECTED):
        drawer=event.getStructureDrawer()
        return drawer is not None and drawer.this==_shared_preview.structure_drawer.this
    if event.type not in (cp4vasp.BE_WIN_CLOSE, cp4vasp.BE_WIN_ACTIVATE, cp4vasp.BE_WIN_DEACTIVATE,
                           cp4vasp.BE_WIN_SHOW, cp4vasp.BE_WIN_HIDE, cp4vasp.BE_ATOM_MOVE): return False
    window=event.getWindow()
    if window is None or window.this!=_shared_preview.win.this:return False
    if event.type==cp4vasp.BE_WIN_CLOSE:
        window.hide();cp4vasp.VisSync()
    elif event.type==cp4vasp.BE_WIN_ACTIVATE:window.redraw()
    return True


class GasPhasePage(Gtk.Box):
    def __init__(self, folder=None):
        super().__init__(orientation=Gtk.Orientation.VERTICAL,spacing=6)
        self.set_border_width(8)
        self.folder=Path(folder) if folder is not None else library_path()
        self.molecule=None;self.directory=None;self.preview_window=None;self.refreshing=False
        actions=Gtk.Box(spacing=6)
        self.refresh_button=Gtk.Button(label='Refresh');self.refresh_button.connect('clicked',self.refresh)
        self.open_button=Gtk.Button(label='Open library folder');self.open_button.connect('clicked',self.open_folder)
        self.preview_button=Gtk.Button(label='Preview 3D');self.preview_button.connect('clicked',self.preview)
        self.generate_button=Gtk.Button(label='Generate inputs');self.generate_button.connect('clicked',self.generate)
        for button in (self.refresh_button,self.open_button,self.preview_button,self.generate_button):actions.pack_start(button,False,False,0)
        self.pack_start(actions,False,False,0)
        path=entry(self.folder);path.set_editable(False);self.pack_start(path,False,False,0)
        self.model=Gtk.ListStore(str,str,int,str,object)
        self.tree=Gtk.TreeView(model=self.model)
        from gi.repository import Pango
        for index,title in enumerate(('File','Name','Atoms','Status')):
            renderer=Gtk.CellRendererText();renderer.set_property('ellipsize',Pango.EllipsizeMode.END)
            column=Gtk.TreeViewColumn(title,renderer,text=index);column.set_resizable(True)
            if index in (0,1,3):column.set_expand(True);column.set_max_width(260)
            self.tree.append_column(column)
        self.tree.get_selection().connect('changed',self.selected)
        scroll=Gtk.ScrolledWindow();scroll.set_policy(Gtk.PolicyType.AUTOMATIC,Gtk.PolicyType.AUTOMATIC)
        scroll.add(self.tree);self.pack_start(scroll,True,True,0)
        fields=Gtk.Grid(column_spacing=6,row_spacing=6)
        self.charge=entry('');self.multiplicity=entry('');self.nelect=entry('')
        self.charge.set_placeholder_text('Required');self.multiplicity.set_placeholder_text('Required')
        self.nelect.set_placeholder_text('Charged only')
        self.nelect.set_tooltip_text('For charged systems: sum of chosen POTCAR valence electrons minus total charge. Neutral: leave blank.')
        self.cell=[entry('') for _ in range(3)]
        for row,items in enumerate((list(zip(('Charge','Multiplicity','NELECT'),(self.charge,self.multiplicity,self.nelect))),list(zip(('Lx (Å)','Ly (Å)','Lz (Å)'),self.cell)))):
            for index,(title,widget) in enumerate(items):
                fields.attach(Gtk.Label(label=title,xalign=0),index*2,row,1,1)
                fields.attach(widget,index*2+1,row,1,1)
        self.pack_start(fields,False,False,0)
        self.status=Gtk.Label(xalign=0);self.status.set_line_wrap(True)
        self.status.set_max_width_chars(80)
        self.pack_start(self.status,False,False,0)
        self.connect('destroy',self.close_preview)
        self.refresh()

    def refresh(self,*args):
        old=self.molecule
        self.refreshing=True;self.model.clear();restore=None
        try:
            rows=scan_library(self.folder)
            for path,molecule,error in rows:
                status=error or ('Ready' if molecule.charge is not None and molecule.multiplicity is not None else 'Confirm charge / multiplicity')
                iterator=self.model.append([path.name,molecule.name if molecule else '',len(molecule.symbols) if molecule else 0,status,molecule])
                if old and path==old.path:restore=iterator
            self.status.set_text('Select a molecule. One XYZ frame per file; coordinates in Å.' if rows else 'No XYZ files found. Add files to the library folder, then Refresh.')
        except OSError as error:self.status.set_text(str(error))
        if restore is not None:
            current=self.model[restore][4]
            self.tree.get_selection().select_iter(restore)
        else:
            current=None;self.molecule=None
        self.refreshing=False
        if restore is not None and current==old:return
        self.load_selection()

    def selected(self,*args):
        if not self.refreshing:self.load_selection()

    def load_selection(self):
        model,iterator=self.tree.get_selection().get_selected()
        molecule=model[iterator][4] if iterator is not None else None
        self.molecule=molecule
        self.preview_button.set_sensitive(molecule is not None)
        self.generate_button.set_sensitive(molecule is not None)
        if molecule is None:
            for field in (self.charge,self.multiplicity,self.nelect,*self.cell):field.set_text('')
            if iterator is not None:self.status.set_text(model[iterator][3])
            return
        self.charge.set_text('' if molecule.charge is None else str(molecule.charge))
        self.multiplicity.set_text('' if molecule.multiplicity is None else str(molecule.multiplicity))
        self.nelect.set_text('')
        for widget,length in zip(self.cell,suggested_cell(molecule)):widget.set_text(str(length))
        self.status.set_text(molecule.name+' — geometry retained; no added atoms or fragment rearrangement. Confirm charge, multiplicity and cell before generating.')

    def lengths(self):
        try:return tuple(float(field.get_text()) for field in self.cell)
        except ValueError:raise ValueError('Enter three numeric cell lengths in angstrom.')

    def parent_window(self):
        parent=self.get_toplevel()
        return parent if isinstance(parent,Gtk.Window) else None

    def open_folder(self,*args):
        try:
            from gi.repository import Gio
            Gio.AppInfo.launch_default_for_uri(self.folder.absolute().as_uri(),None)
        except Exception as error:self.status.set_text('Cannot open library folder: '+str(error))

    def preview(self,*args):
        if self.molecule is None:return
        try:
            from p4vasp.Structure import Structure
            from p4vasp.StructureWindow import StructureWindow
            from p4vasp.util import getAtomtypes
            structure=Structure();structure.read(StringIO(poscar(self.molecule,self.lengths())))
            global _shared_preview
            if _shared_preview is None:
                _shared_preview=StructureWindow(w=600,h=500,title='Gas phase preview',atomtypes=getAtomtypes())
            self.preview_window=_shared_preview
            self.preview_window.setStructure(None)
            self.preview_window.setStructure(structure)
            self.preview_window.win.show()
            self.status.set_text('3D preview: '+self.molecule.name+'. Source XYZ coordinates are unchanged.')
        except Exception as error:self.status.set_text(str(error))

    def close_preview(self,*args):
        if self.preview_window is not None:
            # Drain the queued FLTK hide while its drawer objects are alive.
            # StructureWindow.hide frees drawers before its asynchronous hide.
            import cp4vasp
            preview=self.preview_window
            preview.win.hide();cp4vasp.VisSync()
            # The session-owned window keeps queued back-events safe and is reused.
            self.preview_window=None

    def generate(self,*args):
        if self.molecule is None:return
        try:
            molecule=self.molecule;charge=self.charge.get_text();multiplicity=self.multiplicity.get_text()
            cell=self.lengths();nelect=self.nelect.get_text()
            input_contents(molecule,charge,multiplicity,cell,nelect)
            stem=re.sub(r'[^A-Za-z0-9_-]+','_',molecule.path.stem).strip('_') or 'molecule'
            writer=lambda parent,name:write_inputs(molecule,charge,multiplicity,cell,parent,name,nelect)
            output=InputFolderDialog(self.parent_window(),molecule.name,self.directory,
                title='Generate gas phase inputs',folder_name=stem+'_gas_phase',
                summary='Creates INCAR, KPOINTS and POSCAR.\nCell (Å): '+ ' × '.join(map(str,cell))+'. Molecular geometry is retained.',writer=writer).run()
            if output is not None:
                self.directory=output.parent;self.status.set_text('Created INCAR, KPOINTS and POSCAR in: '+str(output))
        except Exception as error:self.status.set_text(str(error))

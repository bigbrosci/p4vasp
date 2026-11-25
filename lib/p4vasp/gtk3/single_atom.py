"""Periodic selection and a compact new-folder dialog for isolated atoms."""
from pathlib import Path
from p4vasp.gtk3 import Gtk
from gi.repository import Pango
from p4vasp.gtk3.periodic_grid import FittedPeriodicGrid
from p4vasp.gtk3.file_dialogs import FolderDialog, fit_dialog, entry, error_label
from p4vasp.element_data import SYMBOLS, PERIODS
from p4vasp.single_atom_inputs import write_inputs



class InputFolderDialog:
    def __init__(self, parent, symbol, directory=None, *, title=None, folder_name=None, summary=None, writer=None, action_label='Generate inputs'):
        self.symbol = symbol
        self.writer = writer
        self.dialog = Gtk.Dialog(title=title or 'Generate single atom inputs — '+symbol,
                                 transient_for=parent, modal=True, use_header_bar=False)
        self.dialog.add_buttons('Cancel', Gtk.ResponseType.CANCEL, action_label, Gtk.ResponseType.OK)
        fit_dialog(self.dialog, parent, 540, 250)
        grid = Gtk.Grid(column_spacing=8, row_spacing=8); grid.set_border_width(12)
        self.name = entry(folder_name or symbol+'_single_atom')
        self.folder = entry(directory or Path.cwd())
        browse = Gtk.Button(label='Browse…'); browse.connect('clicked',self.browse)
        grid.attach(Gtk.Label(label='Folder name:',xalign=0),0,0,1,1); grid.attach(self.name,1,0,2,1)
        grid.attach(Gtk.Label(label='Save in:',xalign=0),0,1,1,1); grid.attach(self.folder,1,1,1,1); grid.attach(browse,2,1,1,1)
        label=Gtk.Label(label=summary or 'Creates a new folder containing INCAR, KPOINTS and POSCAR.\nCell: 13 × 14 × 15 Å; atom at the center.',xalign=0)
        label.set_line_wrap(True);grid.attach(label,0,2,3,1)
        self.error=error_label();grid.attach(self.error,0,3,3,1)
        self.dialog.get_content_area().add(grid)

    def browse(self,*args):
        directory=self.folder.get_text().strip()
        if not Path(directory).expanduser().is_dir():directory=str(Path.home())
        chosen=FolderDialog(self.dialog,directory).run()
        if chosen:self.folder.set_text(chosen)

    def create(self):
        if self.writer:
            return self.writer(self.folder.get_text().strip(), self.name.get_text())
        return write_inputs(self.symbol,self.folder.get_text().strip(),self.name.get_text())

    def run(self):
        self.dialog.show_all();self.name.grab_focus();self.name.select_region(0,-1)
        try:
            while self.dialog.run()==Gtk.ResponseType.OK:
                try:return self.create()
                except Exception as error:self.error.set_text(str(error))
            return None
        finally:self.dialog.destroy()


class SingleAtomPage(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL,spacing=8)
        self.set_border_width(8)
        self.symbol=None;self.directory=None;self.buttons={}
        actions=Gtk.Box(spacing=12)
        self.selection=Gtk.Label(label='Choose an element.',xalign=0)
        self.generate=Gtk.Button(label='Generate inputs');self.generate.set_sensitive(False)
        self.generate.connect('clicked',self.generate_inputs)
        actions.pack_start(self.selection,True,True,0);actions.pack_start(self.generate,False,False,0)
        self.pack_start(actions,False,False,0)
        self.grid=grid=FittedPeriodicGrid(columns=18,rows=9)
        for row,period in enumerate(PERIODS):
            for symbol,column in period:
                number=SYMBOLS.index(symbol)+1
                button=Gtk.Button(label=str(number)+'\n'+symbol)
                button.get_style_context().add_class('single-atom-element')
                button.get_style_context().add_class('element-tile')
                grid.track(button);grid.track(button.get_child())
                button.set_tooltip_text(symbol+' — atomic number '+str(number))
                button.connect('clicked',self.choose,symbol)
                grid.attach(button,column,row,1,1);self.buttons[symbol]=button
        self.pack_start(grid,True,True,0)
        self.status=Gtk.Label(xalign=0)
        self.status.set_no_show_all(True)
        self.status.set_line_wrap(True);self.status.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
        self.status.set_width_chars(1);self.status.set_max_width_chars(70)
        self.pack_start(self.status,False,False,0)

    def choose(self,button,symbol):
        if self.symbol:self.buttons[self.symbol].get_style_context().remove_class('suggested-action')
        self.symbol=symbol;button.get_style_context().add_class('suggested-action')
        self.selection.set_text('Selected: '+symbol);self.generate.set_sensitive(True)

    def generate_inputs(self,*args):
        if self.symbol is None:return
        parent=self.get_toplevel();parent=parent if isinstance(parent,Gtk.Window) else None
        output=InputFolderDialog(parent,self.symbol,self.directory).run()
        if output is not None:
            self.directory=output.parent
            self.status.set_text('Created INCAR, KPOINTS and POSCAR in: '+str(output))
            self.status.show()

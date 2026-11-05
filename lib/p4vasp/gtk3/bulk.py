"""ASE-backed bulk settings inside Models; output is POSCAR only."""
from io import StringIO
import re
from p4vasp.gtk3 import Gtk, GLib
from p4vasp.gtk3.file_dialogs import entry
from p4vasp.gtk3.single_atom import InputFolderDialog
from p4vasp.ase_bulk import CRYSTALS, BulkTask, parameters


class BulkPage(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.set_border_width(8)
        self.result = None
        self.task = None
        self.alive = True
        self.directory = None
        self.preview_window = None
        grid = Gtk.Grid(column_spacing=10, row_spacing=8)
        self.name = entry('Cu')
        self.name.set_placeholder_text('Element / formula: Cu, Si, NaCl')
        self.crystal = Gtk.ComboBoxText()
        for name in CRYSTALS: self.crystal.append_text(name)
        self.crystal.set_active(1)
        self.mode = Gtk.ComboBoxText()
        for name in ('primitive', 'orthorhombic', 'cubic'): self.mode.append_text(name)
        self.mode.set_active(0)
        for row, (title, widget) in enumerate((('Element / formula', self.name),
                ('Crystal structure', self.crystal), ('Cell type', self.mode))):
            grid.attach(Gtk.Label(label=title, xalign=0), 0, row, 1, 1)
            grid.attach(widget, 1, row, 3, 1)
        self.fields = {}
        for index, (key, label, value) in enumerate((('a','a (Å)','3.615'), ('b','b (Å)',''),
                ('c','c (Å)',''), ('alpha','alpha (°)',''), ('u','u (fraction)','0.375'))):
            widget = entry(value)
            self.fields[key] = widget
            grid.attach(Gtk.Label(label=label, xalign=0), (index%2)*2, 3+index//2, 1, 1)
            grid.attach(widget, (index%2)*2+1, 3+index//2, 1, 1)
        repeats = Gtk.Box(spacing=6)
        self.repeat = [entry('1') for _ in range(3)]
        for title, widget in zip(('n1', 'n2', 'n3'), self.repeat):
            repeats.pack_start(Gtk.Label(label=title), False, False, 0)
            repeats.pack_start(widget, True, True, 0)
        grid.attach(Gtk.Label(label='Supercell', xalign=0), 0, 6, 1, 1)
        grid.attach(repeats, 1, 6, 3, 1)
        self.settings = grid
        self.pack_start(grid, False, False, 0)
        actions = Gtk.Box(spacing=8)
        self.build_button = Gtk.Button(label='Build bulk')
        self.cancel_button = Gtk.Button(label='Cancel')
        self.preview_button = Gtk.Button(label='Preview 3D')
        self.save_button = Gtk.Button(label='Save POSCAR')
        for button in (self.build_button, self.cancel_button, self.preview_button, self.save_button):
            actions.pack_start(button, False, False, 0)
        self.pack_start(actions, False, False, 0)
        self.summary = Gtk.Label(xalign=0)
        self.summary.set_line_wrap(True)
        self.summary.set_selectable(True)
        self.summary.set_max_width_chars(70)
        self.pack_start(self.summary, False, False, 0)
        self.status = Gtk.Label(label='Build a periodic crystal with ASE. Lattice values are user inputs, not optimized results.', xalign=0)
        self.status.set_line_wrap(True)
        self.status.set_max_width_chars(70)
        self.pack_start(self.status, False, False, 0)
        self.build_button.connect('clicked', self.build)
        self.cancel_button.connect('clicked', self.cancel)
        self.preview_button.connect('clicked', self.preview)
        self.save_button.connect('clicked', self.save)
        for widget in (self.name, self.crystal, self.mode, *self.fields.values(), *self.repeat):
            widget.connect('changed', self.changed)
        self.connect('destroy', self.destroyed)
        self.update_fields()
        self.set_busy(False)

    def update_fields(self):
        active = CRYSTALS[self.crystal.get_active_text()]
        for key, widget in self.fields.items(): widget.set_sensitive(key in active)

    def changed(self, *_):
        self.update_fields()
        self.result = None
        self.summary.set_text('')
        self.preview_button.set_sensitive(False)
        self.save_button.set_sensitive(False)
        self.status.set_text('Settings changed. Click Build bulk to generate the new structure.')
        self.close_preview()

    def request(self):
        result = {'name': self.name.get_text().strip(), 'crystal': self.crystal.get_active_text(),
                  'mode': self.mode.get_active_text(), 'repeat': [w.get_text().strip() for w in self.repeat]}
        result.update({key: widget.get_text().strip() for key, widget in self.fields.items()})
        parameters(result)
        return result

    def set_busy(self, busy):
        self.settings.set_sensitive(not busy)
        self.build_button.set_sensitive(not busy)
        self.cancel_button.set_sensitive(busy)
        self.preview_button.set_sensitive(not busy and self.result is not None)
        self.save_button.set_sensitive(not busy and self.result is not None)

    def build(self, *_):
        if self.task is not None: return
        try: request = self.request()
        except ValueError as error:
            self.status.set_text(str(error)); return
        self.result = None
        self.summary.set_text('')
        self.close_preview()
        task = BulkTask(request, lambda result, error: GLib.idle_add(self.finished, task, result, error))
        self.task = task
        self.set_busy(True)
        self.status.set_text('Building bulk with ASE…')
        task.start()

    def finished(self, task, result, error):
        if not self.alive or self.task is not task: return False
        self.task = None
        if task.cancelled.is_set(): error = 'Bulk generation cancelled.'
        if error:
            self.result = None
            self.status.set_text(error)
        else:
            self.result = result
            rows = '\n'.join('  '+'  '.join('%.6g'%v for v in row) for row in result['cell'])
            self.summary.set_text('%s · %d atoms · ASE %s\nCell vectors (Å):\n%s\nVolume: %.6g Å³' %
                                  (result['formula'], result['atoms'], result['ase_version'], rows, result['volume']))
            self.status.set_text('Bulk generated. Preview or save POSCAR to a new folder. Open the saved file in p4vasp for editing.')
        self.set_busy(False)
        return False

    def cancel(self, *_):
        if self.task is not None:
            self.task.cancel()
            self.cancel_button.set_sensitive(False)
            self.status.set_text('Cancelling bulk generation…')

    def preview(self, *_):
        if self.result is None: return
        try:
            from p4vasp.Structure import Structure
            from p4vasp.gtk3.gas_phase import show_model_preview
            structure = Structure()
            structure.read(StringIO(self.result['poscar']))
            self.preview_window = show_model_preview(structure, 'Bulk preview — '+self.result['formula'])
        except Exception as error: self.status.set_text(str(error))

    def parent_window(self):
        window = self.get_toplevel()
        return window if isinstance(window, Gtk.Window) else None

    def save(self, *_):
        if self.result is None: return
        from p4vasp.single_atom_inputs import write_contents
        result = self.result
        name = re.sub('[^A-Za-z0-9_-]', '_', result['formula'])+'_bulk'
        output = InputFolderDialog(self.parent_window(), result['formula'], self.directory,
            title='Save bulk POSCAR', folder_name=name,
            summary='Creates a new folder containing POSCAR only. Existing folders are not overwritten.',
            writer=lambda parent, name: write_contents({'POSCAR': result['poscar']}, parent, name),
            action_label='Save POSCAR').run()
        if output is not None:
            self.directory = output.parent
            self.status.set_text('Saved '+str(output/'POSCAR'))

    def close_preview(self):
        if self.preview_window is not None:
            if self.preview_window.win.getTitle().startswith('Bulk preview'):
                import cp4vasp
                self.preview_window.win.hide(); cp4vasp.VisSync()
            self.preview_window = None

    def destroyed(self, *_):
        self.alive = False
        if self.task is not None: self.task.cancel()
        self.close_preview()

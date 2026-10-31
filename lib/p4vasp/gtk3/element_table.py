"""Editable per-element resource table."""
from p4vasp.gtk3 import Gtk
from p4vasp.element_data import ElementData, COLUMNS, check_value


class ElementTable(Gtk.Box):
    def __init__(self, store, parent_window, show_error):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.set_border_width(6)
        self.store, self.parent_window, self.show_error = store, parent_window, show_error
        self.dirty = False
        self.status = Gtk.Label(xalign=0)
        self.status.set_line_wrap(True)
        self.pack_start(self.status, False, False, 0)
        actions = Gtk.Box(spacing=6)
        self.save_button = Gtk.Button(label='Save'); self.save_button.connect('clicked', self.save)
        self.reload_button = Gtk.Button(label='Reload'); self.reload_button.connect('clicked', self.reload_clicked)
        actions.pack_start(self.save_button, False, False, 0); actions.pack_start(self.reload_button, False, False, 0)
        self.pack_start(actions, False, False, 0)
        self.units = Gtk.Label(label='Units: Name = element symbol; atomic number = dimensionless; mass = u; radii = Å;\nR / G / B = dimensionless (0–1); Magmom = μB; U / J = eV.', xalign=0)
        self.units.set_line_wrap(True)
        self.pack_start(self.units, False, False, 0)
        self.model = Gtk.ListStore(*([str]*len(COLUMNS)))
        self.view = Gtk.TreeView(model=self.model)
        self.view.set_grid_lines(Gtk.TreeViewGridLines.BOTH)
        for index, title in enumerate(COLUMNS):
            renderer = Gtk.CellRendererText(); renderer.set_property('editable', index >= 2)
            if index >= 2: renderer.connect('edited', self.edited, index)
            column = Gtk.TreeViewColumn(title, renderer, text=index)
            column.set_resizable(True); column.set_min_width(60)
            self.view.append_column(column)
        scroll = Gtk.ScrolledWindow(); scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll.add(self.view); self.pack_start(scroll, True, True, 0)
        self.data = None
        self.load()

    def load(self):
        try:
            data = ElementData(self.store)
            self.model.clear()
            for row in data.rows: self.model.append(row)
            self.data = data; self.dirty = False
            self.save_button.set_sensitive(True)
            self.status.set_text('Existing elements only. Blank = unset. radii = display radius; RGB: 0–1.\nDouble-click a value to edit; press Enter, then Save. Restart p4vasp after saving.')
        except Exception as error:
            self.save_button.set_sensitive(False)
            self.status.set_text('Cannot load element data: '+str(error))

    def edited(self, renderer, path, value, column):
        try:
            value = check_value(column, value)
            if self.model[path][column] != value:
                self.model[path][column] = value; self.dirty = True
                self.status.set_text('Unsaved changes. Press Save to write the program files.')
        except Exception as error: self.show_error(self.parent_window(), str(error))

    def save(self, *args):
        try:
            backups = self.data.save([list(row) for row in self.model])
            self.load()
            self.status.set_text('Saved. Restart p4vasp to apply defaults.\n'+ '\n'.join(str(path) for path in backups) if backups else 'No changes to save.')
        except Exception as error: self.show_error(self.parent_window(), str(error))

    def reload_clicked(self, *args):
        if self.dirty:
            dialog = Gtk.MessageDialog(transient_for=self.parent_window(), modal=True,
                message_type=Gtk.MessageType.QUESTION, buttons=Gtk.ButtonsType.YES_NO,
                text='Discard unsaved table edits?')
            response = dialog.run(); dialog.destroy()
            if response != Gtk.ResponseType.YES: return
        self.load()

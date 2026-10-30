"""Transparent PNG export from a snapshot of the active native structure view."""
import itertools
import tempfile
from pathlib import Path
from threading import Event, Thread


def snapshot(window, with_recipe=False):
    """Copy native state on the GUI thread; workers receive Python values only."""
    if window is None or window.structure is None:
        raise ValueError('Open a structure window first.')
    from p4vasp.cStructure import Structure
    structure = Structure(window.structure)
    structure.setCarthesian()
    basis = [list(v) for v in structure.basis]
    drawer = window.structure_drawer
    hidden = set(window.getHiddenAtoms())
    counts = window.getMultiple()
    origins = [tuple(sum((n[i]-counts[i]//2)*basis[i][j] for i in range(3)) for j in range(3))
               for n in itertools.product(*(range(c) for c in counts))]
    positions, elements = [], []
    for origin in origins:
        for i, pos in enumerate(structure):
            if i in hidden or drawer.info.getRecord(i).hidden:
                continue
            positions.append(tuple(pos[j]+origin[j] for j in range(3)))
            elements.append(str(structure.info.getRecordForAtom(i).getElement()).strip())
    if not positions:
        raise ValueError('No visible atoms to export.')
    nav = window.navigator
    camera = dict(matrix=[[nav.getRotMatElement(i,j) for j in range(4)] for i in range(4)],
                  zoom=nav.getZoom(), width=max(1, window.win.w), height=max(1, window.win.h),
                  perspective=bool(nav.getPerspective()))
    state = dict(scene=(basis, positions, elements, origins), camera=camera,
                radius_scale=window.getRadiusFactor(), cell=bool(drawer.showcellflag))
    if with_recipe:
        hidden = sorted(i for i in range(len(structure)) if i in hidden or drawer.info.getRecord(i).hidden)
        base = (basis, [list(p) for p in structure],
                [str(structure.info.getRecordForAtom(i).getElement()).strip() for i in range(len(structure))])
        return state, base, dict(repeat=list(counts),hidden=hidden)
    return state


class ExportImageDialog:
    def __init__(self, get_window, parent=None):
        from p4vasp.gtk3 import Gtk, GdkPixbuf, GLib
        self.Gtk, self.GdkPixbuf, self.GLib = Gtk, GdkPixbuf, GLib
        self.get_window = get_window
        self.alive, self.busy = True, False
        self.cancel = Event()
        self.temp = tempfile.TemporaryDirectory(prefix='p4v-preview-')
        self.dialog = Gtk.Dialog(title='Export structure image', transient_for=parent)
        self.dialog.set_default_size(620, 600)
        self.dialog.add_button('Close', Gtk.ResponseType.CLOSE)
        self.dialog.connect('response', lambda *args: self.dialog.destroy())
        self.dialog.connect('destroy', self.on_destroy)
        outer = self.dialog.get_content_area()
        outer.set_spacing(8)
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        outer.pack_start(scroll, True, True, 0)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        box.set_border_width(12)
        scroll.add(box)
        intro = Gtk.Label(label='Studio export • current view • transparent PNG')
        box.pack_start(intro, False, False, 0)
        grid = Gtk.Grid(column_spacing=12, row_spacing=8)
        box.pack_start(grid, False, False, 0)
        self.model = Gtk.ComboBoxText()
        for value in ('spheres', 'ball-stick', 'stick', 'space-filling'): self.model.append_text(value)
        self.model.set_active(0)
        self.material = Gtk.ComboBoxText()
        for value in ('matte', 'classic', 'glossy'): self.material.append_text(value)
        self.material.set_active(0)
        self.width = Gtk.SpinButton.new_with_range(64, 4096, 100); self.width.set_value(1600)
        self.quality = Gtk.SpinButton.new_with_range(1, 4, 1); self.quality.set_value(2)
        self.brightness = Gtk.SpinButton.new_with_range(.1, 2, .05)
        self.brightness.set_digits(2); self.brightness.set_value(1)
        for row, (label, widget) in enumerate((('Model', self.model), ('Material', self.material),
                      ('Width (px)', self.width), ('Quality', self.quality), ('Brightness', self.brightness))):
            col, line = 2*(row % 2), row//2
            grid.attach(Gtk.Label(label=label, xalign=0), col, line, 1, 1)
            grid.attach(widget, col+1, line, 1, 1)
        self.width.set_tooltip_text('Image height follows the structure window aspect ratio')
        self.preview = Gtk.Image()
        box.pack_start(self.preview, True, True, 0)
        self.status = Gtk.Label(label=''); self.status.set_line_wrap(True)
        box.pack_start(self.status, False, False, 0)
        actions = Gtk.Box(spacing=8)
        self.save_recipe = Gtk.CheckButton(label='Save reusable command, view preset and structure snapshot')
        self.save_recipe.set_active(True)
        box.pack_start(self.save_recipe, False, False, 0)
        self.command_entry = Gtk.Entry()
        self.command_entry.set_editable(False)
        self.command_entry.set_placeholder_text('Export PNG to generate a reusable command')
        self.command_entry.set_tooltip_text('Last successful export command uses the structure snapshot and view preset; replace its input for batch export.')
        command_row = Gtk.Box(spacing=8)
        command_row.pack_start(self.command_entry, True, True, 0)
        box.pack_start(command_row, False, False, 0)
        self.copy_command = Gtk.Button(label='Copy command')
        self.copy_command.set_sensitive(False)
        self.copy_command.connect('clicked', self.on_copy_command)
        command_row.pack_start(self.copy_command, False, False, 0)
        self.refresh = Gtk.Button(label='Refresh preview')
        self.save = Gtk.Button(label='Export PNG…')
        actions.pack_start(self.refresh, True, True, 0); actions.pack_start(self.save, True, True, 0)
        outer.pack_start(actions, False, False, 0)
        self.refresh.connect('clicked', lambda *args: self.start())
        self.save.connect('clicked', self.choose_file)
        for widget in (self.model, self.material): widget.connect('changed', lambda *args: self.start())
        self.dialog.show_all()
        self.start()

    def on_copy_command(self, *args):
        from p4vasp.gtk3 import Gdk
        self.Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD).set_text(self.command_entry.get_text(),-1)

    def on_destroy(self, *args):
        self.alive = False
        self.cancel.set()
        if not self.busy: self.temp.cleanup()

    def choose_file(self, *args):
        from p4vasp.gtk3.file_dialogs import PngSaveDialog
        path = PngSaveDialog(self.dialog, getattr(self, 'export_folder', None)).run()
        if path:
            self.export_folder = str(Path(path).parent)
            self.start(path)

    def start(self, output=None):
        if self.busy or not self.alive: return
        try:
            capture_recipe = bool(output) and self.save_recipe.get_active()
            captured = snapshot(self.get_window(), with_recipe=capture_recipe)
            if capture_recipe:
                state, base, display = captured
            else:
                state, base, display = captured, None, None
            width = self.width.get_value_as_int() if output else 520
            height = max(32, round(width*state['camera']['height']/state['camera']['width']))
            if height > 8192: raise ValueError('Image is too tall; reduce width or resize the structure window.')
            options = dict(state, model=self.model.get_active_text(), material=self.material.get_active_text(),
                           size=(width, height), quality=self.quality.get_value_as_int() if output else 1,
                           brightness=self.brightness.get_value(), transparent=True,
                           renderer="studio", cancelled=self.cancel.is_set)
            recipe = paths = None
            if capture_recipe:
                from p4vasp.render_recipe import make, bundle_paths
                recipe = make(state['camera'], options, display)
                paths = bundle_paths(output)
        except Exception as error:
            self.status.set_text(str(error)); return
        self.busy = True
        for widget in (self.refresh, self.save, self.model, self.material): widget.set_sensitive(False)
        self.status.set_text('Rendering studio image… (model interaction remains available)')
        target = output or str(Path(self.temp.name)/'preview.png')
        def work():
            error, cmd = None, None
            try:
                from p4vasp.render_cli import render
                render(None, target, **options)
                if paths and not self.cancel.is_set():
                    from p4vasp.render_recipe import save_bundle
                    try:
                        cmd = save_bundle(paths, Path(output).absolute(), base, recipe)
                    except Exception as exc:
                        raise ValueError('PNG saved, but replay files failed: '+str(exc)) from exc
            except Exception as exc:
                error = str(exc)
            self.GLib.idle_add(self.finished, target, output is not None, error, cmd)
        Thread(target=work, daemon=True).start()

    def finished(self, target, saved, error, cmd=None):
        self.busy = False
        if not self.alive:
            self.temp.cleanup(); return False
        for widget in (self.refresh, self.save, self.model, self.material): widget.set_sensitive(True)
        if error:
            self.status.set_text('Export failed: '+error)
        elif saved:
            self.status.set_text('Saved: '+target+('\nView preset, structure snapshot and command saved alongside PNG.' if cmd else ''))
            self.command_entry.set_text(cmd or '')
            self.copy_command.set_sensitive(bool(cmd))
        else:
            self.preview.set_from_pixbuf(self.GdkPixbuf.Pixbuf.new_from_file_at_scale(target, 520, 160, True))
            self.status.set_text('Preview uses current view. Refresh after rotating.\nExport captures the latest view; arrows and isosurfaces are not included.')
        return False


def show_export_dialog(get_window, parent=None):
    return ExportImageDialog(get_window, parent)

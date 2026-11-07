"""Compact file/folder dialogs, independent of desktop chooser saved sizes."""
from pathlib import Path

from p4vasp.gtk3 import Gtk, Gdk
from gi.repository import Pango


def workarea(parent):
    display = Gdk.Display.get_default()
    monitor = display.get_monitor_at_window(parent.get_window()) if parent and parent.get_window() else None
    monitor = monitor or display.get_primary_monitor() or display.get_monitor(0)
    return monitor.get_workarea()


def fit_dialog(dialog, parent, width, height):
    area = workarea(parent)
    dialog.set_default_size(min(width, max(240, area.width-48)),
                            min(height, max(160, area.height-80)))
    dialog.set_position(Gtk.WindowPosition.CENTER_ON_PARENT if parent else Gtk.WindowPosition.CENTER)


def entry(text):
    widget = Gtk.Entry()
    widget.set_width_chars(1)
    widget.set_hexpand(True)
    widget.set_text(str(text))
    return widget


def error_label():
    label = Gtk.Label(xalign=0)
    label.set_line_wrap(True)
    label.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
    label.set_max_width_chars(42)
    return label


class FolderDialog:
    def __init__(self, parent, directory):
        self.dialog = Gtk.Dialog(title='Choose export folder', transient_for=parent,
                                 modal=True, use_header_bar=False)
        self.dialog.add_buttons('Cancel', Gtk.ResponseType.CANCEL, 'Select folder', Gtk.ResponseType.OK)
        fit_dialog(self.dialog, parent, 540, 360)
        box = self.dialog.get_content_area()
        box.set_border_width(12)
        box.set_spacing(8)
        navigation = Gtk.Box(spacing=6)
        self.up = Gtk.Button(label='Up')
        self.home = Gtk.Button(label='Home')
        self.location = entry(directory)
        navigation.pack_start(self.up, False, False, 0)
        navigation.pack_start(self.home, False, False, 0)
        navigation.pack_start(self.location, True, True, 0)
        box.pack_start(navigation, False, False, 0)
        self.model = Gtk.ListStore(str, str)
        self.tree = Gtk.TreeView(model=self.model)
        renderer = Gtk.CellRendererText()
        renderer.set_property('ellipsize', Pango.EllipsizeMode.END)
        self.tree.append_column(Gtk.TreeViewColumn('Folders (double-click to open)', renderer, text=0))
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll.add(self.tree)
        box.pack_start(scroll, True, True, 0)
        self.error = error_label()
        box.pack_start(self.error, False, False, 0)
        self.current = Path.cwd()
        self.up.connect('clicked', lambda *_: self.navigate(self.current.parent))
        self.home.connect('clicked', lambda *_: self.navigate(Path.home()))
        self.location.connect('activate', lambda *_: self.navigate(self.location.get_text()))
        self.tree.connect('row-activated', lambda view, path, column: self.navigate(self.model[path][1]))
        self.navigate(directory)

    def navigate(self, directory):
        try:
            path = Path(directory).expanduser().absolute()
            folders = sorted((p for p in path.iterdir() if p.is_dir()), key=lambda p: p.name.casefold())
        except (OSError, ValueError) as exc:
            self.error.set_text('Could not open folder: '+str(exc))
            return False
        self.current = path
        self.location.set_text(str(path))
        self.model.clear()
        for folder in folders:
            self.model.append([folder.name, str(folder)])
        self.up.set_sensitive(path.parent != path)
        self.error.set_text('')
        return True

    def run(self):
        self.dialog.show_all()
        try:
            while self.dialog.run() == Gtk.ResponseType.OK:
                text = self.location.get_text().strip()
                if not text:
                    self.error.set_text('Enter a folder path.')
                    continue
                if Path(text).expanduser().absolute() != self.current:
                    if not self.navigate(text):
                        continue
                model, selected = self.tree.get_selection().get_selected()
                path = Path(model[selected][1]) if selected is not None else self.current
                if path.is_dir():
                    return str(path)
                self.error.set_text('This folder is no longer available.')
            return None
        finally:
            self.dialog.destroy()


class CompactFileDialog(FolderDialog):
    """File navigation using the bounded folder browser, without GtkFileChooser.

    Open accepts existing files; save exclusively selects a new destination.
    Short entry requests and an expanding scroll area keep actions on screen.
    """
    def __init__(self, parent, directory, title, save_name=None):
        self.saving=save_name is not None
        super().__init__(parent,directory)
        self.dialog.set_title(title)
        self.dialog.get_widget_for_response(Gtk.ResponseType.OK).set_label('Save' if self.saving else 'Open')
        self.dialog.set_default_response(Gtk.ResponseType.OK)
        fit_dialog(self.dialog,parent,580,390)
        self.tree.get_column(0).set_title('Folders and files (double-click to open)')
        self.filename=entry(save_name or '')
        self.filename.set_activates_default(True)
        row=Gtk.Box(spacing=8)
        row.pack_start(Gtk.Label(label='Filename:'),False,False,0)
        row.pack_start(self.filename,True,True,0)
        box=self.dialog.get_content_area()
        box.pack_start(row,False,False,0);box.reorder_child(row,1)
        self.tree.get_selection().connect('changed',self.selected)
        self.error.set_lines(3)
        self.error.set_ellipsize(Pango.EllipsizeMode.END)

    def navigate(self,directory):
        try:
            path=Path(directory).expanduser().absolute()
            if path.is_file() and hasattr(self,'filename'):
                self.navigate(path.parent)
                self.filename.set_text(path.name)
                self.dialog.response(Gtk.ResponseType.OK)
                return True
            children=sorted(path.iterdir(),key=lambda p:(not p.is_dir(),p.name.casefold()))
        except (OSError,ValueError) as error:
            self.error.set_text('Could not open folder: '+str(error))
            return False
        self.current=path;self.location.set_text(str(path));self.model.clear()
        if hasattr(self,'filename') and not self.saving:self.filename.set_text('')
        for child in children:
            self.model.append([child.name+('/' if child.is_dir() else ''),str(child)])
        self.up.set_sensitive(path.parent!=path);self.error.set_text('')
        return True

    def selected(self,selection):
        model,iterator=selection.get_selected()
        if iterator is None:return
        path=Path(model[iterator][1])
        if path.is_file():self.filename.set_text(path.name)
        elif not self.saving:self.filename.set_text('')

    def select_file(self,path):
        path=Path(path).expanduser().absolute()
        if self.navigate(path.parent):self.filename.set_text(path.name)

    def destination(self):
        location=self.location.get_text()
        if not location:raise ValueError('Enter a folder path.')
        directory=Path(location).expanduser().absolute()
        if not directory.is_dir():raise ValueError('Choose an existing folder, or paste a file path and press Enter.')
        name=self.filename.get_text()
        if not name:
            model,iterator=self.tree.get_selection().get_selected()
            if iterator is not None:
                path=Path(model[iterator][1])
                if path.is_dir():self.navigate(path);return None
            raise ValueError('Select a file or enter its filename.')
        path=(directory/Path(name).expanduser()).absolute()
        if path.is_dir():self.navigate(path);return None
        if self.saving:
            if not path.parent.is_dir():raise ValueError('Choose an existing destination folder.')
            if path.exists():raise ValueError('Choose a new filename; existing files are not overwritten.')
        elif not path.is_file():raise ValueError('The selected file does not exist.')
        return path

    def run(self):
        self.dialog.show_all()
        (self.filename if self.saving else self.tree).grab_focus()
        try:
            while self.dialog.run()==Gtk.ResponseType.OK:
                try:path=self.destination()
                except (ValueError,OSError) as error:
                    self.error.set_text(str(error));continue
                if path is not None:return str(path)
            return None
        finally:self.dialog.destroy()


class PngSaveDialog:
    def __init__(self, parent, directory=None):
        self.dialog = Gtk.Dialog(title='Export PNG', transient_for=parent,
                                 modal=True, use_header_bar=False)
        self.dialog.add_buttons('Cancel', Gtk.ResponseType.CANCEL, 'Export', Gtk.ResponseType.OK)
        self.dialog.set_default_response(Gtk.ResponseType.OK)
        fit_dialog(self.dialog, parent, 520, 210)
        grid = Gtk.Grid(column_spacing=10, row_spacing=10)
        grid.set_border_width(12)
        self.filename = entry('structure.png')
        self.folder = entry(directory or Path.cwd())
        self.filename.set_activates_default(True)
        self.folder.set_activates_default(True)
        self.browse = Gtk.Button(label='Browse…')
        self.browse.connect('clicked', self.on_browse)
        grid.attach(Gtk.Label(label='Filename:', xalign=0), 0, 0, 1, 1)
        grid.attach(self.filename, 1, 0, 2, 1)
        grid.attach(Gtk.Label(label='Folder:', xalign=0), 0, 1, 1, 1)
        grid.attach(self.folder, 1, 1, 1, 1)
        grid.attach(self.browse, 2, 1, 1, 1)
        self.error = error_label()
        grid.attach(self.error, 0, 2, 3, 1)
        self.dialog.get_content_area().add(grid)

    def on_browse(self, *_):
        directory = self.folder.get_text().strip()
        if not Path(directory).expanduser().is_dir():
            directory = str(Path.home())
        chosen = FolderDialog(self.dialog, directory).run()
        if chosen:
            self.folder.set_text(chosen)

    def destination(self):
        name = self.filename.get_text().strip()
        if not name or name in ('.', '..') or Path(name).name != name or '/' in name or '\\' in name:
            raise ValueError('Enter a filename. Put the directory in Folder.')
        suffix = Path(name).suffix
        if not suffix:
            name += '.png'
        elif suffix.lower() != '.png':
            raise ValueError('Use a PNG filename ending in .png.')
        directory = self.folder.get_text().strip()
        if not directory or not Path(directory).expanduser().is_dir():
            raise ValueError('Choose an existing folder.')
        path = Path(directory).expanduser().absolute()/name
        if path.is_dir():
            raise ValueError('The destination is a folder. Choose another filename.')
        return path

    def confirm_replace(self):
        confirm = Gtk.MessageDialog(transient_for=self.dialog, modal=True, use_header_bar=False,
                                    message_type=Gtk.MessageType.QUESTION, buttons=Gtk.ButtonsType.NONE,
                                    text='Replace the existing PNG?')
        confirm.add_buttons('Cancel', Gtk.ResponseType.CANCEL, 'Replace', Gtk.ResponseType.OK)
        try:
            return confirm.run() == Gtk.ResponseType.OK
        finally:
            confirm.destroy()

    def run(self):
        self.dialog.show_all()
        self.filename.grab_focus()
        self.filename.select_region(0, -1)
        try:
            while self.dialog.run() == Gtk.ResponseType.OK:
                try:
                    path = self.destination()
                except (ValueError, OSError) as exc:
                    self.error.set_text(str(exc))
                    continue
                if path.exists() and not self.confirm_replace():
                    continue
                return str(path)
            return None
        finally:
            self.dialog.destroy()

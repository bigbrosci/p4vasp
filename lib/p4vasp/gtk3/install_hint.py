"""Copyable, path-safe optional-dependency installation hints; never execute them."""
from pathlib import Path
import shlex
import sys
import p4vasp
from p4vasp.gtk3 import Gtk, Gdk


class InstallHint(Gtk.Box):
    def __init__(self, dependency, script):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self.caption = Gtk.Label(label=dependency+' missing? Copy this command and run it in your Linux/macOS terminal:', xalign=0)
        self.caption.set_line_wrap(True)
        self.caption.set_max_width_chars(70)
        self.pack_start(self.caption, False, False, 0)
        row = Gtk.Box(spacing=6)
        self.command = Gtk.Entry()
        self.command.set_editable(False)
        self.command.set_width_chars(1)
        self.command.set_hexpand(True)
        self.copy_button = Gtk.Button(label='Copy command')
        from p4vasp.model_worker import bundled_worker
        if bundled_worker() is not None:
            self.caption.set_text(dependency+' is included. No installation or PATH setup is required.')
            self.command.set_no_show_all(True)
            self.copy_button.set_no_show_all(True)
            self.copy_button.set_sensitive(False)
            return
        path = Path(p4vasp.p4vasp_home).resolve()/'install'/script
        available = sys.platform != 'win32' and not getattr(sys, 'frozen', False) and path.is_file()
        if available:
            self.command.set_text('bash '+shlex.quote(str(path)))
            self.command.set_tooltip_text(self.command.get_text())
        else:
            self.caption.set_text(dependency+' installation command requires a Linux/macOS source checkout; this build does not include that installer.')
            self.copy_button.set_sensitive(False)
        self.copy_button.connect('clicked', self.copy)
        row.pack_start(self.command, True, True, 0)
        row.pack_start(self.copy_button, False, False, 0)
        self.pack_start(row, False, False, 0)

    def copy(self, *_):
        self.command.select_region(0, -1)
        try:
            clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
            clipboard.set_text(self.command.get_text(), -1)
            clipboard.store()
            self.copy_button.set_label('Copied')
        except Exception:
            self.copy_button.set_label('Use Ctrl+C')

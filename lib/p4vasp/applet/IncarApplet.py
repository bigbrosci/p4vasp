"""Native INCAR panel based on the Q-robot INCAR generator."""

import os

from p4vasp import gtk3 as gtk
from p4vasp import msg
from p4vasp.applet.Applet import Applet, AppletProfile
from p4vasp.incar_generator import generate_incar, load_presets, species_from_structure


class IncarApplet(Applet):
    menupath = ["Edit", "INCAR generator"]
    showmode = Applet.EMBEDDED_ONLY_MODE
    exclusive_groups = (
        {"PBE", "RPBE", "R2SCAN", "HSE06"},
        {"Gas", "Bulk", "Slab"},
        {"D3-0", "D3-BJ", "D4"},
        {"Opt", "Single", "TSopt", "NEB", "Dimer", "MD", "Frequency"},
    )

    def __init__(self):
        super().__init__()
        self.config = load_presets()
        self.buttons = {}
        self.sections = {}
        self.updating = False

    @staticmethod
    def label(text):
        label = gtk.Label(label=text)
        label.set_xalign(0)
        label.set_line_wrap(True)
        return label

    @staticmethod
    def scrolled(child):
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll.add(child)
        return scroll

    def createPanel(self):
        self.panel = gtk.Box(orientation=gtk.Orientation.VERTICAL, spacing=8)
        self.panel.set_border_width(10)
        self.panel.pack_start(self.label("INCAR generator — Q-robot presets"), False, False, 0)
        columns = gtk.Paned(orientation=gtk.Orientation.HORIZONTAL)
        choices = gtk.Box(orientation=gtk.Orientation.VERTICAL, spacing=8)
        choices.set_border_width(4)
        defaults = set()
        for category, tasks in self.config["categories"].items():
            frame = gtk.Frame(label=category)
            grid = gtk.Grid(column_spacing=4, row_spacing=4)
            grid.set_border_width(6)
            column_count = 2 if category == "Tasks" else 3
            for index, (name, task) in enumerate(tasks.items()):
                button = gtk.ToggleButton(label=name)
                button.set_tooltip_text("\n".join("%s = %s" % item for item in task["params"].items()))
                button.set_active(name in defaults)
                button.connect("toggled", self.on_preset, name)
                self.buttons[name] = button
                grid.attach(button, index % column_count, index // column_count, 1, 1)
            frame.add(grid)
            choices.pack_start(frame, False, False, 0)
        frame = gtk.Frame(label="Standard sections")
        sections = gtk.Box(orientation=gtk.Orientation.VERTICAL)
        sections.set_border_width(6)
        for name in self.config["standard"]:
            if name in ("d_system", "d_lapack", "d_ncore", "d_write"):
                continue
            check = gtk.CheckButton(label=name[2:].title())
            check.set_active(False)
            check.connect("toggled", self.refresh)
            self.sections[name] = check
            sections.pack_start(check, False, False, 0)
        frame.add(sections)
        choices.pack_start(frame, False, False, 0)
        choices.pack_start(self.label("Reads the open POSCAR; MAGMOM/UJ values use data/incar/presets.json."), False, False, 0)
        columns.pack1(self.scrolled(choices), resize=False, shrink=False)

        editor = gtk.Box(orientation=gtk.Orientation.VERTICAL, spacing=6)
        editor.set_border_width(4)
        editor.pack_start(self.label("Custom parameters (override presets): TAG = value"), False, False, 0)
        self.custom = gtk.TextView()
        self.custom.set_monospace(True)
        self.custom.set_tooltip_text("One TAG = value per line. For example: ENCUT = 520")
        custom_scroll = self.scrolled(self.custom)
        custom_scroll.set_size_request(-1, 110)
        editor.pack_start(custom_scroll, False, True, 0)
        editor.pack_start(self.label("INCAR preview"), False, False, 0)
        self.preview = gtk.TextView()
        self.preview.set_monospace(True)
        self.preview.set_editable(False)
        self.preview.set_left_margin(8)
        self.preview.set_right_margin(8)
        editor.pack_start(self.scrolled(self.preview), True, True, 0)
        columns.pack2(editor, resize=True, shrink=False)
        columns.set_position(290)
        self.panel.pack_start(columns, True, True, 0)
        self.status = self.label("")
        self.panel.pack_start(self.status, False, False, 0)
        actions = gtk.Box(spacing=8)
        refresh = gtk.Button(label="Refresh")
        refresh.connect("clicked", self.reset)
        actions.pack_start(refresh, False, False, 0)
        self.save_button = gtk.Button(label="Save INCAR…")
        self.save_button.connect("clicked", self.on_save)
        actions.pack_end(self.save_button, False, False, 0)
        self.panel.pack_start(actions, False, False, 0)
        self.custom.get_buffer().connect("changed", self.refresh)
        self.panel.show_all()
        return self.panel

    def initUI(self):
        self.refresh()

    def updateSystem(self, *args):
        if self.panel is not None:
            self.refresh()

    def reset(self, *args):
        self.updating = True
        try:
            for button in list(self.buttons.values()) + list(self.sections.values()):
                button.set_active(False)
            self.custom.get_buffer().set_text("")
        finally:
            self.updating = False
        self.refresh()

    def on_preset(self, button, name):
        if self.updating:
            return
        self.updating = True
        if button.get_active():
            for group in self.exclusive_groups:
                if name in group:
                    for other in group - {name}:
                        self.buttons[other].set_active(False)
            # Match Q-robot's frequency/NCORE exclusion.
            if name == "Frequency":
                self.buttons["NCORE"].set_active(False)
            elif name == "NCORE":
                self.buttons["Frequency"].set_active(False)
        self.updating = False
        self.refresh()

    @staticmethod
    def buffer_text(view):
        buffer = view.get_buffer()
        return buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), True)

    def refresh(self, *args):
        if self.updating or not hasattr(self, "preview"):
            return False
        try:
            structure = None
            if self.system is not None:
                structure = getattr(self.system, "INITIAL_STRUCTURE", None)
            species = species_from_structure(structure)
            name = getattr(structure, "comment", "") if structure is not None else ""
            content = generate_incar(
                self.config,
                [name for name, button in self.buttons.items() if button.get_active()],
                [name for name, check in self.sections.items() if check.get_active()],
                self.buffer_text(self.custom), species, name)
            self.preview.get_buffer().set_text(content)
            self.save_button.set_sensitive(True)
            self.status.set_text("Ready to save. Custom parameters take precedence over task and standard presets.")
            return True
        except (ValueError, TypeError, AttributeError) as error:
            self.preview.get_buffer().set_text("")
            self.save_button.set_sensitive(False)
            self.status.set_text(str(error))
            return False

    def on_save(self, *args):
        if not self.refresh():
            return
        parent = self.panel.get_toplevel()
        dialog = gtk.Dialog(
            title="Save INCAR", transient_for=parent if isinstance(parent, gtk.Window) else None,
            use_header_bar=False, modal=True)
        dialog.set_decorated(True)
        dialog.set_deletable(True)
        dialog.set_resizable(False)
        dialog.add_buttons("Cancel", gtk.RESPONSE_CANCEL, "Save", gtk.RESPONSE_OK)
        dialog.set_default_response(gtk.RESPONSE_OK)
        grid = gtk.Grid(column_spacing=12, row_spacing=10)
        grid.set_border_width(16)
        filename = gtk.Entry()
        filename.set_text("INCAR")
        filename.set_width_chars(36)
        filename.set_activates_default(True)
        folder = gtk.Entry()
        directory = getattr(self.system, "PATH", None) if self.system is not None else None
        folder.set_text(os.path.abspath(directory) if directory and os.path.isdir(directory) else os.getcwd())
        folder.set_activates_default(True)
        grid.attach(self.label("Filename:"), 0, 0, 1, 1)
        grid.attach(filename, 1, 0, 1, 1)
        grid.attach(self.label("Folder:"), 0, 1, 1, 1)
        grid.attach(folder, 1, 1, 1, 1)
        browse = gtk.Button(label="Browse…")
        browse.connect("clicked", lambda button: self.browse_folder(dialog, folder))
        grid.attach(browse, 2, 1, 1, 1)
        error_label = self.label("")
        error_label.set_max_width_chars(50)
        grid.attach(error_label, 0, 2, 2, 1)
        dialog.get_content_area().add(grid)
        dialog.show_all()
        filename.grab_focus()
        filename.select_region(0, -1)
        try:
            while dialog.run() == gtk.RESPONSE_OK:
                name = filename.get_text().strip()
                if not name or name in (".", "..") or os.path.basename(name) != name:
                    error_label.set_text("Enter a filename such as INCAR_test. Set the directory in Folder.")
                    continue
                directory = os.path.abspath(os.path.expanduser(folder.get_text().strip()))
                path = os.path.join(directory, name)
                if os.path.exists(path):
                    confirm = gtk.MessageDialog(
                        transient_for=dialog, modal=True,
                        message_type=gtk.MessageType.QUESTION,
                        buttons=gtk.ButtonsType.NONE,
                        text="Replace the existing file?", use_header_bar=False)
                    confirm.format_secondary_text(path)
                    confirm.add_buttons("Cancel", gtk.RESPONSE_CANCEL, "Replace", gtk.RESPONSE_OK)
                    try:
                        replace = confirm.run() == gtk.RESPONSE_OK
                    finally:
                        confirm.destroy()
                    if not replace:
                        continue
                try:
                    with open(path, "w", encoding="utf-8") as stream:
                        stream.write(self.buffer_text(self.preview))
                except OSError as error:
                    error_label.set_text("Could not save INCAR: " + str(error))
                    continue
                self.status.set_text("Saved " + path)
                msg().status("Saved INCAR to " + path)
                break
        finally:
            dialog.destroy()

    def browse_folder(self, parent, folder_entry):
        """Browse directories without the desktop's oversized file chooser."""
        dialog = gtk.Dialog(title="Choose folder", transient_for=parent,
                            modal=True, use_header_bar=False)
        dialog.set_default_size(600, 400)
        dialog.add_buttons("Cancel", gtk.RESPONSE_CANCEL, "Select folder", gtk.RESPONSE_OK)
        box = gtk.Box(orientation=gtk.Orientation.VERTICAL, spacing=8)
        box.set_border_width(12)
        navigation = gtk.Box(spacing=6)
        up = gtk.Button(label="Up")
        home = gtk.Button(label="Home")
        location = gtk.Entry()
        navigation.pack_start(up, False, False, 0)
        navigation.pack_start(home, False, False, 0)
        navigation.pack_start(location, True, True, 0)
        box.pack_start(navigation, False, False, 0)
        box.pack_start(self.label("Double-click a folder to open it, or select it and click Select folder."), False, False, 0)
        model = gtk.ListStore(str, str)
        tree = gtk.TreeView(model=model)
        tree.append_column(gtk.TreeViewColumn("Folders", gtk.CellRendererText(), text=0))
        box.pack_start(self.scrolled(tree), True, True, 0)
        error = self.label("")
        box.pack_start(error, False, False, 0)
        current = [os.getcwd()]

        def navigate(path):
            path = os.path.abspath(os.path.expanduser(path))
            try:
                with os.scandir(path) as entries:
                    folders = sorted((entry.name, entry.path) for entry in entries if entry.is_dir())
            except OSError as exc:
                error.set_text(str(exc))
                return False
            current[0] = path
            location.set_text(path)
            model.clear()
            for item in folders:
                model.append(item)
            up.set_sensitive(os.path.dirname(path) != path)
            error.set_text("")
            return True

        up.connect("clicked", lambda button: navigate(os.path.dirname(current[0])))
        home.connect("clicked", lambda button: navigate(os.path.expanduser("~")))
        location.connect("activate", lambda entry: navigate(entry.get_text()))
        tree.connect("row-activated", lambda view, path, column: navigate(model[path][1]))
        dialog.get_content_area().add(box)
        initial = os.path.expanduser(folder_entry.get_text().strip())
        navigate(initial if os.path.isdir(initial) else os.getcwd())
        dialog.show_all()
        try:
            while dialog.run() == gtk.RESPONSE_OK:
                if os.path.abspath(os.path.expanduser(location.get_text())) != current[0]:
                    if not navigate(location.get_text()):
                        continue
                selected_model, iterator = tree.get_selection().get_selected()
                path = selected_model[iterator][1] if iterator is not None else current[0]
                if not os.path.isdir(path):
                    error.set_text("This folder is no longer available. Choose another folder.")
                    continue
                folder_entry.set_text(path)
                break
        finally:
            dialog.destroy()


IncarApplet.store_profile = AppletProfile(IncarApplet, tagname="IncarApplet")

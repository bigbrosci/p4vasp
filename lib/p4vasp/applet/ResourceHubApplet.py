"""Offline resource cards and a validated editor for the actual bundled files."""
from p4vasp.gtk3 import Gtk, Gdk
from p4vasp.applet.Applet import Applet
from p4vasp.resource_data import ResourceStore, validate
from p4vasp.gtk3.element_table import ElementTable


def message(parent, text, kind=Gtk.MessageType.ERROR):
    dialog = Gtk.MessageDialog(transient_for=parent, modal=True,
                              message_type=kind, buttons=Gtk.ButtonsType.OK, text=text)
    dialog.run()
    dialog.destroy()


class ResourceEditor(Gtk.Dialog):
    def __init__(self, parent, store, key, title, focus='', on_saved=None):
        super().__init__(title=title, transient_for=parent, destroy_with_parent=True)
        self.store, self.key, self.on_saved = store, key, on_saved
        self.set_default_size(680, 440)
        self.add_button('Close', Gtk.ResponseType.CLOSE)
        self.add_button('Reload', Gtk.ResponseType.REJECT)
        self.add_button('Save', Gtk.ResponseType.APPLY)
        box = self.get_content_area()
        path = Gtk.Label(label=str(store.path(key)), xalign=0)
        path.set_selectable(True); path.set_line_wrap(True); box.pack_start(path, False, False, 6)
        self.status = Gtk.Label(label='Edits change the program file. Restart p4vasp to apply cached defaults.', xalign=0)
        self.status.set_line_wrap(True); box.pack_start(self.status, False, False, 6)
        self.search = Gtk.SearchEntry(); self.search.set_placeholder_text('Find text')
        self.search.connect('activate', self.find); box.pack_start(self.search, False, False, 4)
        scroll = Gtk.ScrolledWindow(); scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.text = Gtk.TextView(); self.text.set_monospace(True)
        self.buffer = self.text.get_buffer(); scroll.add(self.text); box.pack_start(scroll, True, True, 0)
        self.reload()
        self.connect('response', self.response)
        self.connect('delete-event', self.close_requested)
        self.show_all(); self.search.set_text(focus)
        if focus: self.find(self.search)

    def contents(self):
        return self.buffer.get_text(self.buffer.get_start_iter(), self.buffer.get_end_iter(), True)

    def reload(self):
        text, self.expected = self.store.read(self.key)
        self.buffer.set_text(text); self.buffer.set_modified(False)

    def discard(self):
        if not self.buffer.get_modified(): return True
        dialog = Gtk.MessageDialog(transient_for=self, modal=True, message_type=Gtk.MessageType.QUESTION,
                                   buttons=Gtk.ButtonsType.YES_NO, text='Discard unsaved edits?')
        result = dialog.run(); dialog.destroy()
        return result == Gtk.ResponseType.YES

    def close_requested(self, *args):
        if self.discard(): self.destroy()
        return True

    def response(self, dialog, response):
        if response == Gtk.ResponseType.APPLY:
            try:
                self.expected, backup = self.store.save(self.key, self.contents(), self.expected)
                self.buffer.set_modified(False)
                self.status.set_text('Saved. Backup: %s\nRestart p4vasp to apply cached defaults.' % backup)
                if self.on_saved: self.on_saved(self.key)
            except Exception as error: message(self, str(error))
        elif response == Gtk.ResponseType.REJECT:
            if self.discard():
                try: self.reload()
                except Exception as error: message(self, str(error))
        else: self.close_requested()

    def find(self, entry):
        needle = entry.get_text()
        if not needle: return
        start = self.buffer.get_iter_at_mark(self.buffer.get_insert())
        match = start.forward_search(needle, Gtk.TextSearchFlags.CASE_INSENSITIVE, None)
        if match is None:
            match = self.buffer.get_start_iter().forward_search(needle, Gtk.TextSearchFlags.CASE_INSENSITIVE, None)
        if match:
            self.buffer.select_range(*match); self.text.scroll_to_iter(match[0], 0.1, False, 0, 0)


class ResourceHubApplet(Applet):
    show_system_selection = False
    def __init__(self):
        super().__init__()
        self.name = 'Database resources'; self.gladefile = 'resources.glade'; self.gladename = 'applet_frame'
        self.store = ResourceStore(); self.online_buttons = []

    def initUI(self):
        notebook = Gtk.Notebook()
        self.online = Gtk.Grid(column_spacing=8, row_spacing=8, column_homogeneous=True)
        self.online.set_border_width(8)
        online_page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll.add(self.online); online_page.pack_start(scroll, True, True, 0)
        footer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        footer.set_border_width(8)
        self.link_status = Gtk.Label(label='Click a database to show and copy its URL.', xalign=0)
        self.link_status.set_line_wrap(True)
        self.link_entry = Gtk.Entry(); self.link_entry.set_editable(False)
        self.link_entry.set_placeholder_text('Database URL')
        footer.pack_start(self.link_status, False, False, 0)
        footer.pack_start(self.link_entry, False, False, 0)
        online_page.pack_start(footer, False, False, 0)
        notebook.append_page(online_page, Gtk.Label(label='Online databases'))
        self.element_table = ElementTable(self.store, self.parent_window, message)
        notebook.append_page(self.element_table, Gtk.Label(label='p4vasp data'))
        self.useful_tools = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        notebook.append_page(self.useful_tools, Gtk.Label(label='Useful tools'))
        self.xml.get_widget('resource_host').pack_start(notebook, True, True, 0)
        self.refresh(); self.panel.show_all()

    def card(self, title, description):
        button = Gtk.Button()
        label = Gtk.Label(label=title)
        label.set_line_wrap(True); label.set_max_width_chars(18)
        label.set_margin_top(12); label.set_margin_bottom(12)
        label.set_margin_start(8); label.set_margin_end(8)
        button.add(label)
        button.set_tooltip_text(description)
        return button

    def refresh(self):
        for child in self.online.get_children(): self.online.remove(child)
        self.online_buttons = []
        try:
            sites = validate('websites', self.store.read('websites')[0])
            for index, site in enumerate(sites):
                button = self.card(site['name'], site.get('description', '')+'\n'+site['url'])
                button.connect('clicked', self.select_site, site['name'], site['url'])
                self.online.attach(button, index % 4, index // 4, 1, 1); self.online_buttons.append(button)
        except Exception as error:
            self.online.attach(Gtk.Label(label='Cannot read website catalog: '+str(error)), 0, 0, 4, 1)
        self.online.show_all()

    def parent_window(self):
        parent = self.panel.get_toplevel()
        return parent if isinstance(parent, Gtk.Window) else None

    def select_site(self, button, name, url):
        self.link_entry.set_text(url)
        self.link_entry.select_region(0, -1)
        try:
            clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
            clipboard.set_text(url, -1)
            clipboard.store()
            self.link_status.set_text(name+' — URL copied to clipboard.')
        except Exception:
            self.link_status.set_text(name+' — Select the URL below and press Ctrl+C to copy.')

    def edit(self, button, key, title, focus):
        try:
            return ResourceEditor(self.parent_window(), self.store, key, title, focus,
                                  lambda saved: self.refresh() if saved == 'websites' else None)
        except Exception as error: message(self.parent_window(), str(error))

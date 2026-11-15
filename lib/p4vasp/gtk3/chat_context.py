"""Preview and copy context locally; no chat service or automatic upload."""
from p4vasp.gtk3 import Gtk, Gdk
from p4vasp.gtk3.file_dialogs import fit_dialog
from p4vasp.chat_context import format_context


class ChatContextDialog(Gtk.Dialog):
    def __init__(self, parent, structure, source, incar_loader=None):
        super().__init__(title='Copy for ChatGPT', transient_for=parent, modal=False,
                         destroy_with_parent=True, use_header_bar=False)
        self.structure, self.source, self.incar_loader = structure, source, incar_loader
        self._incar = None
        self.add_button('Close', Gtk.ResponseType.CLOSE)
        self.copy_button = self.add_button('Copy', Gtk.ResponseType.APPLY)
        fit_dialog(self, parent, 680, 500)
        box = self.get_content_area(); box.set_border_width(10); box.set_spacing(8)
        label = Gtk.Label(label='Default: compact summary without atomic coordinates.\nFull POSCAR uses more tokens. Nothing is uploaded; paste the text into your chat.', xalign=0)
        label.set_line_wrap(True); label.set_max_width_chars(70); box.pack_start(label, False, False, 0)
        options = Gtk.Box(spacing=12)
        self.full = Gtk.CheckButton(label='Include full POSCAR')
        self.full.set_sensitive(structure is not None)
        self.incar = Gtk.CheckButton(label='Include INCAR')
        self.incar.set_sensitive(incar_loader is not None)
        for widget in (self.full, self.incar):
            options.pack_start(widget, False, False, 0)
            widget.connect('toggled', self.refresh)
        box.pack_start(options, False, False, 0)
        scroll = Gtk.ScrolledWindow(); scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.preview = Gtk.TextView(); self.preview.set_editable(False); self.preview.set_monospace(True)
        self.preview.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        scroll.add(self.preview); box.pack_start(scroll, True, True, 0)
        self.status = Gtk.Label(xalign=0); self.status.set_line_wrap(True)
        box.pack_start(self.status, False, False, 0)
        self.connect('response', self.response)
        self.refresh(); self.show_all()

    def refresh(self, *args):
        try:
            if self.incar.get_active() and self._incar is None:
                self._incar = str(self.incar_loader())
            self.text = format_context(self.structure, self.source, self.full.get_active(),
                                       self._incar if self.incar.get_active() else None)
            self.preview.get_buffer().set_text(self.text)
            self.copy_button.set_sensitive(True)
            self.status.set_text('%d characters. Token count depends on the model.' % len(self.text))
        except Exception as error:
            self.text = ''
            self.preview.get_buffer().set_text('')
            self.copy_button.set_sensitive(False)
            self.status.set_text('Cannot prepare context: %s' % error)

    def response(self, dialog, response):
        if response == Gtk.ResponseType.APPLY:
            if self.text:
                clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
                clipboard.set_text(self.text, -1); clipboard.store()
                self.status.set_text('Copied. Paste into ChatGPT and add your question.')
        else:
            self.destroy()

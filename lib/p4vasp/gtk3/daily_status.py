"""Idle daily quote with task/error text taking priority in the same footer."""
import sys
from p4vasp.gtk3 import GLib
from gi.repository import Pango
from p4vasp.daily_quotes import load_quotes, quote_for_day


class DailyStatus:
    def __init__(self, label):
        # Quartz is not a Fontconfig backend; do not use its known-unsafe Fc path.
        if sys.platform != 'darwin':
            from p4vasp.gtk3.community import load_chinese_font
            load_chinese_font()
        self.label = label
        self.records = load_quotes()
        self.idle = True
        label.set_line_wrap(True)
        label.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
        label.set_selectable(True)
        label.set_width_chars(1)
        label.set_xalign(0)
        label.set_margin_start(8); label.set_margin_end(8)
        label.set_margin_top(4); label.set_margin_bottom(4)
        self.refresh()
        self.timer = GLib.timeout_add_seconds(60, self.refresh)
        label.connect('destroy', self.destroyed)

    def refresh(self, today=None):
        if self.idle:
            quote = quote_for_day(self.records, today)
            text = quote['text']+' ——《'+quote['source']+'》'
            self.label.set_text(text)
            self.label.set_tooltip_text(text+'\n'+quote['url'])
        return True

    def status(self, text):
        self.idle = text.strip().upper() in ('', 'OK')
        if self.idle: self.refresh()
        else:
            self.label.set_text(text)
            self.label.set_tooltip_text(text)
        self.label.show()

    def error(self, text):
        self.status('ERROR: '+text)

    def destroyed(self, *_):
        if self.timer:
            GLib.source_remove(self.timer)
            self.timer = None

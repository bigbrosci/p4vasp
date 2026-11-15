"""Actual Edit menu, preview options, lazy INCAR and native clipboard."""
from pathlib import Path
from unittest.mock import patch
from p4vasp.gtk3 import Gtk, Gdk
from p4vasp.gtk3.chat_context import ChatContextDialog
from testChatContext import structure

assert Gtk.init_check()[0]
ns = {'__name__': 'chat_context_frame_test'}
exec(compile(Path('p4v.py').read_text().split('\nschedule(init())')[0], 'p4v.py', 'exec'), ns)
errors = []
import sys
old = sys.excepthook
sys.excepthook = lambda *args: errors.append(args)
frame = ns['Frame'](); frame.quitNow = lambda *_: None; frame.createFrame()
calls = []
class System:
    INITIAL_STRUCTURE = structure()
    @property
    def INCAR(self):
        calls.append(1); return 'ISPIN = 2\nNELM = 500'
system = System()
before = system.INITIAL_STRUCTURE.toString()
ns['getCurrentSystemPM'] = lambda: system
try:
    edit = [item for item in frame.menubar.get_children() if item.get_name() == 'Edit']
    assert len(edit) == 1
    items = [item for item in edit[0].get_submenu().get_children() if item.get_name() == 'Copy for ChatGPT...']
    assert len(items) == 1
    items[0].activate()
    dialog = next(w for w in Gtk.Window.list_toplevels() if isinstance(w, ChatContextDialog))
    assert not calls and not dialog.full.get_active() and not dialog.incar.get_active()
    assert 'Atoms: 3' in dialog.text and '0.123456789' not in dialog.text
    dialog.incar.set_active(True)
    assert calls == [1] and 'ISPIN = 2' in dialog.text
    dialog.full.set_active(True)
    assert 'Selective' in dialog.text and 'F F F' in dialog.text
    dialog.incar.set_active(False); dialog.incar.set_active(True)
    assert calls == [1]
    dialog.copy_button.clicked()
    assert Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD).wait_for_text() == dialog.text
    assert system.INITIAL_STRUCTURE.toString() == before
    # WSL screen captures can be black. Render the real content offscreen.
    dialog.full.set_active(False); dialog.incar.set_active(False)
    content = dialog.get_content_area()
    content.get_parent().remove(content)
    capture = Gtk.OffscreenWindow(); capture.get_style_context().add_class('background'); capture.set_size_request(680, 460); capture.add(content); capture.show_all()
    def background(widget, cr):
        cr.set_source_rgb(1, 1, 1); cr.paint(); return False
    capture.connect('draw', background)
    capture.queue_draw()
    while Gtk.events_pending(): Gtk.main_iteration_do(False)
    import time
    for _ in range(20):
        while Gtk.events_pending(): Gtk.main_iteration_do(False)
        time.sleep(.01)
    capture.get_pixbuf().savev('/tmp/p4vasp-chat-context.png', 'png', [], [])
    assert not errors, errors
    capture.destroy(); dialog.destroy()
finally:
    sys.excepthook = old
    frame.root_window.destroy()
print('PASS Edit menu, summary/full options, lazy INCAR, native clipboard and unchanged source')

"""Actual About dialog: credits, bounded layout, scrolling and both headers."""
from contextlib import ExitStack
import time
from unittest.mock import patch
import p4vasp
from p4vasp.gtk3 import Gtk,Gdk

namespace={'__name__':'about_gui_test'}
exec(compile(open('p4v.py').read().split('\nschedule(init())')[0],'p4v.py','exec'),namespace)
assert Gtk.init_check()[0]
frame=namespace['Frame']()

def descendants(widget):
    yield widget
    if isinstance(widget,Gtk.Container):
        for child in widget.get_children():yield from descendants(child)

for versioned in (False,True):
    with ExitStack() as stack:
        for key,value in dict(name='p4vasp',version='3-test',release='1',build_date='2026-11-01').items():
            stack.enter_context(patch.object(p4vasp,key,value if versioned else None,create=True))
        frame.show_about_dialog()
    dialog=next(window for window in Gtk.Window.list_toplevels() if window.get_title()=='About p4vasp' and window.get_visible())
    for _ in range(20):
        while Gtk.events_pending():Gtk.main_iteration()
        time.sleep(.01)
    widgets=list(descendants(dialog))
    label=next(widget for widget in widgets if isinstance(widget,Gtk.Label) and 'Whitehare2023' in widget.get_text())
    assert 'Maintained and further developed by Bigbrosci' in label.get_text()
    assert 'Orest Dubay' in label.get_text() and 'ABSOLUTELY NO WARRANTY' in label.get_text()
    assert ('v3-testr1' in label.get_text())==versioned
    assert any(isinstance(widget,Gtk.ScrolledWindow) for widget in widgets)
    from p4vasp.gtk3.file_dialogs import workarea
    area=workarea(None);allocation=dialog.get_allocation()
    assert allocation.width<=area.width and allocation.height<=area.height
    buttons=[widget for widget in widgets if isinstance(widget,Gtk.Button)]
    assert any(button.get_visible() and button.get_allocation().height>10 for button in buttons)
    if not versioned:
        image=Gdk.pixbuf_get_from_window(dialog.get_window(),0,0,allocation.width,allocation.height)
        image.savev('/tmp/p4vasp-about-credits.png','png',[],[])
    dialog.destroy()
print('PASS: real About credits, both headers, scrollable content and visible action button')

# A long installation path on a small work area must not hide the OK button.
from types import SimpleNamespace
with patch.object(p4vasp,'p4vasp_home','/tmp/'+'long_path_'*50), patch('p4vasp.gtk3.file_dialogs.workarea',return_value=SimpleNamespace(width=480,height=400)):
    frame.show_about_dialog()
dialog=next(window for window in Gtk.Window.list_toplevels() if window.get_title()=='About p4vasp' and window.get_visible())
for _ in range(20):
    while Gtk.events_pending():Gtk.main_iteration()
    time.sleep(.01)
assert dialog.get_allocation().width<=480 and dialog.get_allocation().height<=400
scroll=next(widget for widget in descendants(dialog) if isinstance(widget,Gtk.ScrolledWindow))
assert scroll.get_vadjustment().get_upper()>scroll.get_vadjustment().get_page_size()
dialog.destroy()
print('PASS: long path / small work area scrolls within screen bounds')

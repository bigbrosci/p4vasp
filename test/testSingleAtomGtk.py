"""Periodic selection, output-folder dialog and actual generated files."""
from pathlib import Path
import tempfile
import time
from unittest.mock import patch
from p4vasp.gtk3 import Gtk, Gdk, GLib
from p4vasp.gtk3.single_atom import SingleAtomPage, InputFolderDialog, PERIODS
from p4vasp.element_data import SYMBOLS

assert Gtk.init_check()[0]
assert sorted(symbol for period in PERIODS for symbol,_ in period)==sorted(SYMBOLS)
window=Gtk.OffscreenWindow();window.set_size_request(1100,600)
page=SingleAtomPage();window.add(page);window.show_all()
assert page.symbol is None and not page.generate.get_sensitive()
assert not page.status.get_visible()
page.buttons['Fe'].clicked()
assert page.symbol=='Fe' and page.generate.get_sensitive()
page.buttons['Og'].clicked();assert page.symbol=='Og'
page.buttons['Fe'].clicked()
with tempfile.TemporaryDirectory() as root:
    root=Path(root)
    dialog=InputFolderDialog(None,'Fe',root)
    dialog.name.set_text('iron atom')
    dialog.dialog.show_all()
    for _ in range(20):
        while Gtk.events_pending():Gtk.main_iteration()
        time.sleep(.01)
    allocation=dialog.dialog.get_allocation()
    assert allocation.width<=600 and allocation.height<=350
    pixbuf=Gdk.pixbuf_get_from_window(dialog.dialog.get_window(),0,0,allocation.width,allocation.height)
    pixbuf.savev('/tmp/p4vasp-single-atom-folder.png','png',[],[])
    GLib.idle_add(lambda: (dialog.dialog.response(Gtk.ResponseType.OK),False)[1])
    output=dialog.run()
    assert output==root/'iron atom'
    assert {p.name for p in output.iterdir()}=={'INCAR','KPOINTS','POSCAR'}
    cancelled=InputFolderDialog(None,'H',root)
    GLib.idle_add(lambda: (cancelled.dialog.response(Gtk.ResponseType.CANCEL),False)[1])
    assert cancelled.run() is None
    assert not (root/'H_single_atom').exists()
    with patch('p4vasp.gtk3.single_atom.InputFolderDialog') as factory:
        factory.return_value.run.return_value=output
        page.generate.clicked()
        assert factory.call_args.args[1]=='Fe'
        assert 'iron atom' in page.status.get_text()
for _ in range(20):
    while Gtk.events_pending():Gtk.main_iteration()
    time.sleep(.01)
window.get_pixbuf().savev('/tmp/p4vasp-single-atom-page.png','png',[],[])
window.destroy()
print('PASS: periodic selection, compact folder dialog, create/cancel, Generate inputs wiring')

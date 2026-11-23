"""Actual GTK personal-table save/reopen with a temporary user profile."""
from pathlib import Path
import tempfile
from p4vasp.gtk3 import Gtk
from p4vasp.gtk3.element_table import ElementTable
from p4vasp.resource_data import ResourceStore

assert Gtk.init_check()[0], 'Display required'
root = Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as temporary:
    folder = Path(temporary)
    store = ResourceStore(root, folder/'backups', user_root=folder/'profile')
    window = Gtk.Window()
    errors = []
    table = ElementTable(store, lambda:window, lambda *args:errors.append(args))
    window.add(table); window.show_all()
    while Gtk.events_pending(): Gtk.main_iteration()
    table.edited(None, '5', '0.95', 3)
    table.save_button.clicked()
    assert not errors, errors
    assert 'Saved personal settings' in table.status.get_text()
    assert store.path('periodic').exists()
    reopened = ElementTable(store, lambda:window, lambda *args:errors.append(args))
    assert reopened.model[5][3] == '0.95'
    assert 'survive Git updates' in reopened.status.get_text()
    reopened.destroy(); window.destroy()
print('PASS: GTK edit/save/reopen personal radius and status')

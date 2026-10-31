"""Displayed GTK hub, browser dispatch and temporary-file editor integration."""
from pathlib import Path
import shutil
import tempfile
from unittest.mock import patch
from p4vasp.gtk3 import Gtk
from p4vasp.applet.DBApplet import DBApplet
from p4vasp.resource_data import ResourceStore, FILES
from p4vasp.applet.ResourceHubApplet import ResourceEditor

root = Path(__file__).resolve().parents[1]
assert Gtk.init_check()[0], 'A display is required'
with tempfile.TemporaryDirectory() as temporary:
    folder = Path(temporary)
    for relative in FILES.values():
        path = folder/'data'/relative; path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(root/'data'/relative, path)
    applet = DBApplet(); applet.store = ResourceStore(folder, folder/'backups')
    window = Gtk.OffscreenWindow(); window.set_size_request(640, 480)
    window.add(applet.createPanel()); applet.initUI(); window.show_all()
    for _ in range(10):
        while Gtk.events_pending(): Gtk.main_iteration()
    assert len(applet.online_buttons) == 16
    assert len(applet.internal_buttons) == 6
    for i, button in enumerate(applet.online_buttons):
        assert applet.online.child_get_property(button, 'left-attach') == i % 4
        assert applet.online.child_get_property(button, 'top-attach') == i // 4
        assert button.get_allocation().width > 40
    with patch('p4vasp.applet.ResourceHubApplet.webbrowser.open', return_value=True) as browser:
        applet.online_buttons[0].clicked()
        browser.assert_called_once_with('https://opencatalystproject.org/')
    window.get_pixbuf().savev('/tmp/p4vasp-resource-hub.png', 'png', [], [])
    editor = ResourceEditor(None, applet.store, 'websites', 'Website catalog', 'name', lambda key: applet.refresh())
    for key in ('elements', 'incar'):
        check = ResourceEditor(None, applet.store, key, key, 'mass' if key == 'elements' else 'categories')
        assert check.contents() == applet.store.read(key)[0]
        check.buffer.set_text(check.contents()+'\n')
        with patch.object(check, 'discard', return_value=False):
            check.close_requested()
            assert check.get_visible()
        check.destroy()
    old = applet.store.read('websites')[1]
    editor.buffer.set_text(editor.contents().replace('Open Catalyst Project', 'Changed title'))
    editor.response(editor, Gtk.ResponseType.APPLY)
    assert applet.store.read('websites')[1] != old
    assert not editor.buffer.get_modified()
    assert list((folder/'backups/websites').glob('*.bak'))
    editor.buffer.set_text('invalid json')
    with patch('p4vasp.applet.ResourceHubApplet.message') as error:
        editor.response(editor, Gtk.ResponseType.APPLY)
        assert error.called
    assert applet.store.read('websites')[1] != b'invalid json'
    editor.destroy(); window.destroy()
print('PASS: 4x4 displayed grid, six internal cards, mocked browser, editor save/validation/backup')

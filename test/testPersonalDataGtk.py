"""Actual colored periodic table and property-dialog saves in a temporary profile."""
import hashlib
from pathlib import Path
import tempfile
import time
from p4vasp.gtk3 import Gtk, Gdk
from p4vasp.gtk3.element_table import ElementTable, tile_color
from p4vasp.element_data import ElementData
from p4vasp.resource_data import ResourceStore, FILES

assert Gtk.init_check()[0], 'Display required'
Gtk.Settings.get_default().set_property('gtk-enable-animations',False)
root=Path(__file__).resolve().parents[1]
originals={name:hashlib.sha256((root/'data'/FILES[name]).read_bytes()).hexdigest() for name in ('periodic','incar','elements')}

def pump():
    for _ in range(12):
        while Gtk.events_pending():Gtk.main_iteration_do(False)
        time.sleep(.01)

with tempfile.TemporaryDirectory() as temporary:
    folder=Path(temporary);store=ResourceStore(root,folder/'backups',user_root=folder/'profile')
    window=Gtk.Window();window.set_default_size(1060,680)
    errors=[];table=ElementTable(store,lambda:window,lambda *args:errors.append(args))
    window.add(table);window.show_all();pump()
    import cairo
    initial=cairo.ImageSurface(cairo.FORMAT_ARGB32,window.get_allocated_width(),window.get_allocated_height())
    window.draw(cairo.Context(initial));initial.write_to_png('/tmp/p4vasp-data-periodic-default.png')
    assert len(table.buttons)==118 and table.buttons['Og'].get_mapped()
    assert table.grid.child_get_property(table.buttons['H'],'left-attach')==1
    assert table.grid.child_get_property(table.buttons['He'],'left-attach')==18
    assert table.grid.child_get_property(table.buttons['Ce'],'top-attach')>7
    record=table.data.catalog['elements'][28]
    assert table.colors['Cu']==tile_color(record)
    shown=table.buttons['Cu'].get_style_context().get_background_color(Gtk.StateFlags.NORMAL)
    assert max(abs(a-b) for a,b in zip((shown.red,shown.green,shown.blue),table.colors['Cu']))<=1/255
    table.buttons['Cu'].clicked();editor=table.editor
    assert editor is not None and editor.get_modal() and editor.get_transient_for() is window
    assert editor.symbol=='Cu' and set(editor.fields)==set(range(2,10))
    editor.fields[4].set_text('256');editor.save_button.clicked()
    assert table.editor is editor and '255' in editor.error.get_text()
    assert not store.path('periodic').exists()
    editor.fields[4].set_text('30');editor.fields[5].set_text('90');editor.fields[6].set_text('150')
    editor.fields[3].set_text('0.95');editor.fields[7].set_text('-1.5')
    editor.fields[8].set_text('4');editor.fields[9].set_text('0.6')
    editor.check_resize();pump()
    import cairo
    shot=cairo.ImageSurface(cairo.FORMAT_ARGB32,editor.get_allocated_width(),editor.get_allocated_height())
    editor.draw(cairo.Context(shot));shot.write_to_png('/tmp/p4vasp-element-properties.png')
    assert editor.save_button.get_mapped()
    editor.save_button.clicked();pump()
    assert table.editor is None and not errors
    assert 'Saved personal settings' in table.status.get_text()
    assert table.data.rows[28][3:]==['0.95','30','90','150','-1.5','4.0','0.6']
    assert table.colors['Cu']==(30/255,90/255,150/255)
    reopened=ElementTable(store,lambda:window,lambda *args:errors.append(args))
    assert reopened.data.rows[28][3:]==table.data.rows[28][3:]
    assert reopened.colors['Cu']==table.colors['Cu']
    reopened.destroy()
    # Cancelled edits do not leak into tiles or storage.
    before=store.read('periodic')[1]
    editor=table.open_element('Cu');editor.fields[3].set_text('8');editor.response(Gtk.ResponseType.CANCEL)
    assert store.read('periodic')[1]==before and table.data.rows[28][3]=='0.95'
    # Real color chooser event updates integer RGB fields and persists.
    editor=table.open_element('H');rgba=Gdk.RGBA();rgba.red=.2;rgba.green=.4;rgba.blue=.6;rgba.alpha=1
    editor.color.set_rgba(rgba);editor.color.emit('color-set')
    assert [editor.fields[i].get_text() for i in (4,5,6)]==['51','102','153']
    editor.save_button.clicked();assert table.colors['H']==(.2,.4,.6)
    # Blank reference colors stay blank; display fallback is not saved.
    editor=table.open_element('Og');assert all(editor.fields[i].get_text()=='' for i in (3,4,5,6))
    before=store.read('periodic')[1];editor.save_button.clicked();assert store.read('periodic')[1]==before
    # An external save while the editor is open is detected, not overwritten.
    editor=table.open_element('C');other=ElementData(store);rows=[row[:] for row in other.rows]
    rows[5][2]='12.1';other.save(rows);before=store.read('periodic')[1]
    editor.fields[3].set_text('9');editor.save_button.clicked()
    assert table.editor is editor and 'changed' in editor.error.get_text()
    assert store.read('periodic')[1]==before
    editor.response(Gtk.ResponseType.CANCEL);table.reload_button.clicked();pump()
    shot=cairo.ImageSurface(cairo.FORMAT_ARGB32,window.get_allocated_width(),window.get_allocated_height())
    window.draw(cairo.Context(shot));shot.write_to_png('/tmp/p4vasp-data-periodic.png')
    assert all(hashlib.sha256((root/'data'/FILES[name]).read_bytes()).hexdigest()==digest for name,digest in originals.items())
    assert not errors
    window.destroy()
print('PASS: 118 colored tiles, property dialog, validation, RGB picker, personal save/reopen, cancel, unknowns and conflict protection')

"""Actual GTK/ASE/native preview and real POSCAR folder-dialog integration."""
from io import StringIO
from pathlib import Path
import tempfile
import time
from unittest.mock import patch
import numpy as np
import cairo
import cp4vasp
from p4vasp.gtk3 import Gtk, Gdk, GLib
from p4vasp.applet.ModelsApplet import ModelsApplet
from p4vasp.gtk3.bulk import BulkPage
from p4vasp.gtk3.single_atom import InputFolderDialog
from p4vasp.Structure import Structure

assert Gtk.init_check()[0]
cp4vasp.VisInit()
window=Gtk.Window();window.set_default_size(700,540)
applet=ModelsApplet();window.add(applet.createPanel());applet.initUI();window.show_all()
applet.notebook.set_current_page(2)
page=applet.bulk_page

def spin(seconds=.1,until=None):
    limit=time.monotonic()+seconds
    while time.monotonic()<limit:
        cp4vasp.VisCheck()
        while Gtk.events_pending():Gtk.main_iteration()
        if until is not None and until():return
        time.sleep(.005)
    if until is not None:assert until(),'timed out'

assert page.result is None and not page.save_button.get_sensitive()
assert not page.fields['c'].get_sensitive()
page.mode.set_active(2)
for field in page.repeat:field.set_text('2')
ticks=[]
timer=GLib.timeout_add(10,lambda:(ticks.append(1),True)[1])
page.build_button.clicked()
assert not page.settings.get_sensitive()
spin(10,lambda:page.task is None)
GLib.source_remove(timer)
assert page.result is not None,page.status.get_text()
assert page.result['atoms']==32 and len(ticks)>=2
assert page.save_button.get_sensitive()
page.preview_button.clicked();spin(.3)
assert page.preview_window is not None,page.status.get_text()
assert 'Bulk preview' in page.preview_window.win.getTitle()
assert len(page.preview_window.structure)==32
from p4vasp.gtk3.gas_phase import handle_preview_event
from types import SimpleNamespace
assert handle_preview_event(SimpleNamespace(type=cp4vasp.BE_ATOM_MOVE,getWindow=lambda:page.preview_window.win))
page.preview_window.win.saveScreenshot('/tmp/p4vasp-bulk-native.tga')
raw=Path('/tmp/p4vasp-bulk-native.tga').read_bytes()
w,h=int.from_bytes(raw[12:14],'little'),int.from_bytes(raw[14:16],'little')
rgb=np.frombuffer(raw[18:],dtype=np.uint8).reshape(h,w,3)[::-1,:,::-1]
pixels=np.ascontiguousarray(0xff000000 | rgb[:,:,0].astype(np.uint32)<<16 | rgb[:,:,1].astype(np.uint32)<<8 | rgb[:,:,2].astype(np.uint32))
cairo.ImageSurface.create_for_data(pixels,cairo.FORMAT_ARGB32,w,h,w*4).write_to_png('/tmp/p4vasp-bulk-native.png')
with tempfile.TemporaryDirectory() as temporary:
    def actual_dialog(*args,**kwargs):
        kwargs['folder_name']='copper-test'
        dialog=InputFolderDialog(*args,**kwargs)
        dialog.folder.set_text(temporary)
        assert dialog.dialog.get_widget_for_response(Gtk.ResponseType.OK).get_label()=='Save POSCAR'
        GLib.timeout_add(80,lambda:(dialog.dialog.response(Gtk.ResponseType.OK),False)[1])
        return dialog
    with patch('p4vasp.gtk3.bulk.InputFolderDialog',side_effect=actual_dialog):page.save_button.clicked()
    saved=Path(temporary)/'copper-test/POSCAR'
    assert saved.read_text()==page.result['poscar']
    assert [p.name for p in saved.parent.iterdir()]==['POSCAR']
    structure=Structure();structure.read(StringIO(saved.read_text()));assert len(structure)==32
    # Existing-folder protection and cancellation use the same real dialog writer.
    before=saved.read_bytes()
    dialog=InputFolderDialog(window,'Cu',temporary,folder_name='copper-test',
        writer=lambda parent,name: __import__('p4vasp.single_atom_inputs',fromlist=['write_contents']).write_contents({'POSCAR':'bad'},parent,name))
    try:
        try:dialog.create();raise AssertionError('existing folder overwritten')
        except FileExistsError:pass
    finally:dialog.dialog.destroy()
    assert saved.read_bytes()==before
    def cancel_dialog(*args,**kwargs):
        dialog=InputFolderDialog(*args,**kwargs)
        GLib.timeout_add(50,lambda:(dialog.dialog.response(Gtk.ResponseType.CANCEL),False)[1])
        return dialog
    with patch('p4vasp.gtk3.bulk.InputFolderDialog',side_effect=cancel_dialog):page.save_button.clicked()
spin(.1)
Gdk.pixbuf_get_from_window(window.get_window(),0,0,window.get_allocated_width(),window.get_allocated_height()).savev('/tmp/p4vasp-bulk-page.png','png',[],[])
page.fields['a'].set_text('3.7')
assert page.result is None and not page.save_button.get_sensitive() and not page.preview_button.get_sensitive()
assert page.preview_window is None
page.crystal.set_active(list(__import__('p4vasp.ase_bulk',fromlist=['CRYSTALS']).CRYSTALS).index('hcp'))
assert page.fields['c'].get_sensitive() and not page.fields['b'].get_sensitive()
page.fields['c'].set_text('')
page.build_button.clicked();assert page.task is None and 'numeric c' in page.status.get_text()
# Small window: the notebook bulk page scrolls rather than forcing an oversized window.
scrolled=applet.notebook.get_nth_page(2)
applet.notebook.remove_page(2)
small=Gtk.Window();small.set_default_size(480,320);small.add(scrolled);small.show_all();spin(.3)
assert small.get_allocated_width()<=480 and small.get_allocated_height()<=320
small.destroy();window.destroy();spin(.1)
print('PASS: real ASE worker/UI responsiveness, 32-atom native read-only preview, real POSCAR save/cancel/no-overwrite, stale result invalidation and compact layout',flush=True)
import os;os._exit(0)

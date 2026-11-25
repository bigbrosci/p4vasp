"""Actual atomic-reference popup, preview and configured three-file export."""
from pathlib import Path
import tempfile
import time
from unittest.mock import patch
from p4vasp.gtk3 import Gtk, GLib
from p4vasp.gtk3.single_atom import SingleAtomPage, InputFolderDialog
from p4vasp.incar_generator import parse_custom

assert Gtk.init_check()[0]
Gtk.Settings.get_default().set_property('gtk-enable-animations',False)
window=Gtk.Window();window.set_default_size(800,650);page=SingleAtomPage();window.add(page);window.show_all()
def pump():
    for _ in range(30):
        while Gtk.events_pending():Gtk.main_iteration_do(False)
        time.sleep(.01)
def preview(dialog):
    buffer=dialog.preview.get_buffer();return buffer.get_text(buffer.get_start_iter(),buffer.get_end_iter(),False)
with tempfile.TemporaryDirectory() as name:
    parent=Path(name)
    page.buttons['Cu'].clicked();dialog=page.atom_dialog;pump()
    assert dialog.reference['multiplicity']==2 and '3d^10' in dialog.reference['configuration']
    assert dialog.ispin.get_active()==1 and dialog.magmom.get_text()==''
    assert 'MAGMOM' not in parse_custom(preview(dialog)) and not dialog.constrain.get_active()
    assert dialog.generate.get_mapped()
    dialog.use_reference.clicked();assert dialog.magmom.get_text()=='1'
    dialog.charge.set_text('1');assert not dialog.use_reference.get_sensitive()
    assert 'SET_AFTER_POTCAR' in preview(dialog)
    dialog.zval.set_text('11');assert parse_custom(preview(dialog))['NELECT']=='10'
    dialog.constrain.set_active(True);assert not dialog.generate.get_sensitive()
    dialog.nupdown.set_text('0');assert not dialog.generate.get_sensitive() # Initial moment mismatch.
    dialog.magmom.set_text('');assert dialog.generate.get_sensitive()
    assert parse_custom(preview(dialog))['MAGMOM']=='0'
    dialog.ispin.set_active(0);assert not dialog.constrain.get_active()
    assert 'NUPDOWN' not in parse_custom(preview(dialog))
    for entry,value in zip(dialog.cell,('16','17','18')):entry.set_text(value)
    pump()
    import cairo
    shot=cairo.ImageSurface(cairo.FORMAT_ARGB32,dialog.get_allocated_width(),dialog.get_allocated_height())
    dialog.draw(cairo.Context(shot));shot.write_to_png('/tmp/p4vasp-atomic-reference-settings.png')
    expected=preview(dialog)
    def auto(*args,**kwargs):
        kwargs['folder_name']='Cu_atom';d=InputFolderDialog(*args,**kwargs);d.folder.set_text(str(parent))
        GLib.timeout_add(50,lambda:(d.dialog.response(Gtk.ResponseType.OK),False)[1]);return d
    with patch('p4vasp.gtk3.single_atom.InputFolderDialog',side_effect=auto):dialog.generate.clicked()
    assert page.atom_dialog is None
    assert (parent/'Cu_atom/INCAR').read_text()==expected
    assert set(path.name for path in (parent/'Cu_atom').iterdir())=={'INCAR','POSCAR','KPOINTS'}
    assert (parent/'Cu_atom/POSCAR').read_text().splitlines()[2:5]==['16 0 0','0 17 0','0 0 18']
    page.generate.clicked();dialog=page.atom_dialog
    assert dialog.charge.get_text()=='1' and dialog.cell[0].get_text()=='16.0'
    dialog.response(Gtk.ResponseType.CANCEL)
    page.buttons['Og'].clicked();dialog=page.atom_dialog
    assert dialog.reference_labels['Neutral ground configuration'].get_text()=='Unknown'
    assert not dialog.use_reference.get_sensitive() and dialog.generate.get_sensitive()
    dialog.response(Gtk.ResponseType.CANCEL)
    page.buttons['O'].clicked();dialog=page.atom_dialog
    dialog.constrain.set_active(True);assert dialog.nupdown.get_text()=='2'
    assert parse_custom(preview(dialog))['MAGMOM']=='2'
    dialog.response(Gtk.ResponseType.CANCEL)
window.destroy()
print('PASS atomic reference/settings, explicit spin/charge, exact preview/export, reopen, missing data and cancellation')

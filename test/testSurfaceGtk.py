"""Actual Models tabs, ASE subprocess, Cairo slab preview and save dialogs."""
from io import StringIO
import json
import os
from pathlib import Path
import sys
import tempfile
import time
import traceback
import cairo
from unittest.mock import patch
from p4vasp.gtk3 import Gtk, GLib
from p4vasp.applet.ModelsApplet import ModelsApplet
from p4vasp.gtk3.single_atom import InputFolderDialog
from p4vasp.Structure import Structure
import cp4vasp


def main():
    assert Gtk.init_check()[0]
    assert 'ase' not in sys.modules,'ASE must stay out of the GTK interpreter'
    cp4vasp.VisInit()
    window=Gtk.Window();window.set_default_size(780,760)
    models=ModelsApplet();window.add(models.createPanel());models.initUI();window.show_all()
    assert not hasattr(models,'surface_page')
    models.notebook.set_current_page(3);page=models.surface_page
    assert page.result is None and not page.save_button.get_sensitive()
    assert not hasattr(page,'source')
    assert [button.get_label() for button in page.source_buttons]==['Metal preset','Use bulk result','Open POSCAR / CIF']
    assert page.preset_button.get_active() and page.source_mode==0
    page.preset.set_active(1)
    assert [w.get_text() for w in page.indices]==['1','0','0']
    page.preset.set_active(0)
    errors=[];old=sys.excepthook;sys.excepthook=lambda *args:errors.append(args)
    def screenshot(view, name):
        view.get_toplevel().check_resize()
        image=cairo.ImageSurface(cairo.FORMAT_ARGB32,view.get_allocated_width(),view.get_allocated_height())
        view.draw(cairo.Context(image));image.write_to_png('/tmp/p4vasp-surface-'+name+'.png')
    def pump(until=lambda:True,timeout=30):
        end=time.monotonic()+timeout
        while time.monotonic()<end:
            cp4vasp.VisCheck()
            for _ in range(30):
                if not Gtk.events_pending():break
                Gtk.main_iteration_do(False)
            if until():return
            time.sleep(.01)
        raise AssertionError('Timed out waiting for Surface UI')
    try:
        # Unavailable bulk and cancelled file selection preserve current source/result.
        page.use_bulk.clicked()
        assert page.source_mode==0 and page.preset_button.get_active()
        with patch('p4vasp.gtk3.surface.CompactFileDialog') as chooser:
            chooser.return_value.run.return_value=None
            page.open_button.clicked()
        assert page.source_mode==0 and page.preset_button.get_active()
        ticks=[];timer=GLib.timeout_add(10,lambda:(ticks.append(1),True)[1])
        page.build_button.clicked();assert page.task is not None
        assert not page.settings.get_sensitive() and page.cancel_button.get_sensitive()
        pump(lambda:page.task is None);GLib.source_remove(timer)
        assert ticks and page.result is not None,page.status.get_text()
        assert page.result['atoms']==16 and page.result['fixed_atoms']==8
        assert 'ase' not in sys.modules
        result=page.result;source=result['poscar']
        page.preview_button.clicked();pump()
        preview=page.preview_window
        assert preview is not None and preview.get_visible()
        view=preview.get_child()
        assert len(view.positions)==16 and view.show_cell
        assert view.constrained=={i for i,layer in enumerate(result['layer_numbers']) if layer<=2}
        assert 'X marks' in page.status.get_text()
        for _ in range(15):pump();time.sleep(.01)
        screenshot(view,'constraints')
        assert page.result['poscar']==source
        cell=page.result['cell']
        page.bottom_button.set_active(True);pump()
        assert page.result['request']['placement']=='bottom' and page.task is None
        assert 'Half total' in page.vacuum_title.get_text()
        assert page.result['cell']==cell and page.result['fixed_atoms']==8
        shifted=Structure();shifted.read(StringIO(page.result['poscar']));shifted.setCartesian()
        assert abs(min(p[2] for p in shifted)-.1)<1e-10
        assert abs(page.result['vacuum_top']-19.9)<1e-10
        assert page.preview_window is preview and len(view.constrained)==8
        for _ in range(15):pump();time.sleep(.01)
        screenshot(view,'bottom')
        page.center_button.set_active(True);pump()
        assert abs(page.result['vacuum_bottom']-10)<1e-10
        assert 'EACH side' in page.vacuum_title.get_text()
        for _ in range(15):pump();time.sleep(.01)
        screenshot(view,'center')
        preview.close()
        pump(lambda: page.preview_window is None)
        page.preview_button.clicked();pump()
        assert page.preview_window is not preview
        assert len(page.preview_window.get_child().constrained)==8
        page.bottom_button.set_active(True);source=page.result['poscar']

        with tempfile.TemporaryDirectory(prefix='surface UI ') as temporary:
            parent=Path(temporary)
            def dialog(*args,**kwargs):
                kwargs['folder_name']='Cu_111'
                d=InputFolderDialog(*args,**kwargs);d.folder.set_text(str(parent))
                GLib.timeout_add(50,lambda:(d.dialog.response(Gtk.ResponseType.OK),False)[1]);return d
            with patch('p4vasp.gtk3.surface.InputFolderDialog',side_effect=dialog):page.save_button.clicked()
            out=parent/'Cu_111'
            assert {f.name for f in out.iterdir()}=={'POSCAR','surface.json','rebuild_surface.py','rebuild_surface.sh'}
            atoms=Structure(str(out/'POSCAR'))
            assert len(atoms)==16 and sum(not all(flag) for flag in atoms.selective)==8
            meta=json.loads((out/'surface.json').read_text());assert meta['fixed_atoms']==8
            assert len(meta['layer_numbers'])==16 and meta['placement']=='bottom'
            atoms.setCartesian();assert abs(min(p[2] for p in atoms)-.1)<1e-10
            assert (out/'POSCAR').read_text()==source
            from p4vasp.single_atom_inputs import write_contents
            before=(out/'POSCAR').read_bytes()
            try:write_contents({'POSCAR':'bad'},parent,'Cu_111');raise AssertionError('overwrite allowed')
            except FileExistsError:pass
            assert (out/'POSCAR').read_bytes()==before
            # Bulk -> Surface takes an explicit snapshot and retains bulk output.
            models.notebook.set_current_page(2);bulk=models.bulk_page
            bulk.mode.set_active(2);bulk.fields['a'].set_text('3.6345');bulk.build_button.clicked();pump(lambda:bulk.task is None)
            assert bulk.result is not None,bulk.status.get_text()
            original=bulk.result['poscar']
            models.notebook.set_current_page(3);page.use_bulk.clicked()
            assert page.source_poscar==original and page.result is None
            assert page.a.get_text()=='3.6345' and page.symbol.get_text()=='Cu'
            assert not page.a.get_sensitive()
            assert 'a' not in page.request() and page.request()['poscar']==original
            window.check_resize();pump()
            shot=cairo.ImageSurface(cairo.FORMAT_ARGB32,window.get_allocated_width(),window.get_allocated_height())
            window.draw(cairo.Context(shot));shot.write_to_png('/tmp/p4vasp-surface-bulk-lattice.png')
            page.repeat[0].set_text('1');page.repeat[1].set_text('1')
            page.build_button.clicked();pump(lambda:page.task is None)
            assert page.result is not None,page.status.get_text()
            assert bulk.result['poscar']==original
            assert page.result['request']['source']=='poscar'
            # Explicit compact-file selection and the actual ASE file reader.
            path=parent/'bulk.POSCAR';path.write_text(original)
            def answer():
                browser=getattr(page,'file_dialog',None)
                if browser and browser.dialog.get_visible():
                    browser.select_file(path);browser.dialog.response(Gtk.ResponseType.OK);return False
                return True
            GLib.timeout_add(30,answer);page.open_button.clicked()
            assert page.source_path==str(path) and page.source_mode==2
            page.build_button.clicked();pump(lambda:page.task is None)
            assert page.result is not None,page.status.get_text()
            assert 'path' not in page.result['request']
            old_result=page.result
            with patch('p4vasp.gtk3.surface.CompactFileDialog') as chooser:
                chooser.return_value.run.return_value=None
                page.open_button.clicked()
            assert page.result is old_result and page.source_mode==2
            assert page.open_button.get_active() and sum(b.get_active() for b in page.source_buttons)==1
            # Changing input invalidates saves and hides the old surface preview.
            page.fixed.set_text('0')
            assert page.result is None and not page.save_button.get_sensitive() and page.preview_window is None
            page.layers.set_text('0');page.build_button.clicked()
            assert page.task is None and 'layers' in page.status.get_text()
            # Cancel/destroy must reject a late completion, even after inputs change.
            from types import SimpleNamespace
            import threading
            cancelled=threading.Event();fake=SimpleNamespace(cancelled=cancelled,cancel=cancelled.set)
            page.task=fake;page.set_busy(True);page.cancel_button.clicked()
            assert cancelled.is_set()
            page.finished(fake,result,None)
            assert page.result is None and 'cancelled' in page.status.get_text().lower()
        # Screenshot is the actual scrolled Surface content after a clean preset build.
        page.preset_button.clicked();assert page.a.get_text()=='3.615' and page.a.get_sensitive()
        page.layers.set_text('4');page.fixed.set_text('2');page.center_button.set_active(True)
        for field in page.repeat:field.set_text('2')
        page.build_button.clicked();pump(lambda:page.task is None)
        assert page.result is not None,page.status.get_text()
        for _ in range(15):pump();time.sleep(.01)
        window.check_resize()
        image=cairo.ImageSurface(cairo.FORMAT_ARGB32,window.get_allocated_width(),window.get_allocated_height())
        window.draw(cairo.Context(image));image.write_to_png('/tmp/p4vasp-surface-page.png')
        assert not errors,errors
        page.destroy();assert not page.alive
        window.destroy()
        print('PASS real lazy Surface/ASE responsiveness, preset/bulk/file sources, constraint-marked Cairo preview, POSCAR/metadata save, invalidation/cancel/destroy',flush=True)
    finally:
        sys.excepthook=old


if __name__=='__main__':
    try:main()
    except BaseException:traceback.print_exc();os._exit(1)
    os._exit(0)

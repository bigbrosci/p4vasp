"""Displayed local library, native preview, metadata and generated files."""
import os
from pathlib import Path
import tempfile
import time
from unittest.mock import patch
from p4vasp.gtk3 import Gtk, GLib
from p4vasp.gtk3.gas_phase import GasPhasePage
from p4vasp.incar_generator import parse_custom
import cp4vasp


def draw():
    for _ in range(20):
        while Gtk.events_pending():Gtk.main_iteration()
        time.sleep(.01)


def main():
    assert Gtk.init_check()[0];cp4vasp.VisInit()
    with tempfile.TemporaryDirectory() as temporary:
        root=Path(temporary)
        (root/'water.xyz').write_text('3\nname="Water" charge=0 multiplicity=1 units=angstrom\nO 0 0 0\nH .76 0 .50\nH -.76 0 .50\n')
        (root/'unknown.xyz').write_text('1\nNo metadata\nHe 0 0 0\n')
        (root/'bad.xyz').write_text('1\n\nWrong 0 0 0\n')
        page=GasPhasePage(root)
        window=Gtk.OffscreenWindow();window.set_size_request(780,500);window.add(page);window.show_all();draw()
        assert len(page.model)==3 and not page.generate_button.get_sensitive()
        def select(filename):
            index=next(i for i,row in enumerate(page.model) if row[0]==filename)
            page.tree.get_selection().select_path(str(index));draw()
        select('bad.xyz');assert not page.generate_button.get_sensitive() and 'bad.xyz:3' in page.status.get_text()
        select('unknown.xyz');assert page.charge.get_text()=='' and page.multiplicity.get_text()==''
        page.generate_button.clicked();assert 'integer' in page.status.get_text()
        select('water.xyz');assert page.charge.get_text()=='0' and page.multiplicity.get_text()=='1'
        page.multiplicity.set_text('3');page.refresh();assert page.multiplicity.get_text()=='3'
        page.multiplicity.set_text('1');before=page.molecule.positions
        from p4vasp.util import getAtomtypes
        baseline_radius=getAtomtypes().getRecordForElement('O').radius
        page.preview_button.clicked()
        assert page.preview_window is not None,page.status.get_text()
        assert len(page.preview_window.structure)==3
        from p4vasp.util import getAtomtypes
        original=getAtomtypes().getRecordForElement('O')
        assert abs(page.preview_window.structure_drawer.info.getRecord(0).radius-original.covalent)<1e-6
        assert abs(page.preview_window.getRadiusFactor()-.5)<1e-6
        assert abs(page.preview_window.atomtypes.getRecordForElement('Og').radius-.7)<1e-8
        assert abs(getAtomtypes().getRecordForElement('O').radius-baseline_radius)<1e-8
        for _ in range(12):cp4vasp.VisCheck();time.sleep(.02)
        page.preview_window.win.saveScreenshot('/tmp/p4vasp-gas-covalent.tga')
        from p4vasp.gtk3.gas_phase import handle_preview_event
        from types import SimpleNamespace
        event=SimpleNamespace(type=cp4vasp.BE_SELECTED,getStructureDrawer=lambda:page.preview_window.structure_drawer)
        assert handle_preview_event(event)
        close=SimpleNamespace(type=cp4vasp.BE_WIN_CLOSE,getWindow=lambda:page.preview_window.win)
        assert handle_preview_event(close)
        namespace={'__name__':'gas_preview_event_test'}
        app_root=Path(__file__).resolve().parents[1]
        exec(compile((app_root/'p4v.py').read_text().split('\nschedule(init())')[0],'p4v.py','exec'),namespace)
        class Queue:
            def __init__(self):self.events=[event,close]
            def current(self):return self.events[0] if self.events else None
            def pop(self):self.events.pop(0)
        queue=Queue();namespace['vbequeue']=queue
        namespace['scheduler']=lambda:iter([None])
        with patch.dict(namespace,{'getSelectionFromVisStructureDrawer':lambda drawer:(_ for _ in ()).throw(AssertionError('Preview changed global selection')),
                                  'applets':lambda:(_ for _ in ()).throw(AssertionError('Preview touched applet repository'))}):
            assert namespace['idle_func']() and not queue.events
        page.preview_button.clicked()
        assert page.molecule.positions==before
        page.charge.set_text('1');page.multiplicity.set_text('2')
        assert not hasattr(page,'nelect')
        from p4vasp.gtk3.single_atom import InputFolderDialog
        def destination_dialog(*args,**kwargs):
            dialog=InputFolderDialog(None,*args[1:],**kwargs)
            dialog.folder.set_text(str(root));dialog.name.set_text('created')
            GLib.idle_add(lambda:(dialog.dialog.response(Gtk.ResponseType.OK),False)[1])
            return dialog
        with patch('p4vasp.gtk3.gas_phase.InputFolderDialog',side_effect=destination_dialog) as factory:
            page.generate_button.clicked()
            assert factory.call_args.kwargs['folder_name']=='water_gas_phase'
        params=parse_custom((root/'created/INCAR').read_text())
        assert params['NELECT']=='SET_AFTER_POTCAR' and params['NUPDOWN']=='1'
        assert 'created' in page.status.get_text() and 'Fill NELECT' in page.status.get_text()
        with patch('p4vasp.gtk3.gas_phase.InputFolderDialog') as factory:
            factory.return_value.run.return_value=None
            page.generate_button.clicked()
        from gi.repository import Gio
        with patch.object(Gio.AppInfo,'launch_default_for_uri') as opener:
            page.open_button.clicked();opener.assert_called_once_with(root.as_uri(),None)
        page.close_preview()
        select('water.xyz')
        draw();window.get_pixbuf().savev('/tmp/p4vasp-gas-phase.png','png',[],[])
        page.preview_button.clicked()
        assert page.preview_window is not None
        window.destroy()
        assert page.preview_window is None
    print('PASS: XYZ library, invalid rows, metadata, refresh preservation, native preview and charged export/cancel',flush=True)

if __name__=='__main__':
    try:main()
    except BaseException:
        import traceback
        traceback.print_exc();os._exit(1)
    os._exit(0)

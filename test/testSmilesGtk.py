"""Real asynchronous SMILES build, GUI heartbeat and existing gas export path."""
import os
from pathlib import Path
import tempfile
import time
from unittest.mock import patch
from p4vasp.gtk3 import Gtk,GLib
from p4vasp.gtk3.gas_phase import GasPhasePage
from p4vasp.gtk3.single_atom import InputFolderDialog
import cp4vasp


def pump_until(predicate,timeout=20):
    deadline=time.monotonic()+timeout
    while not predicate() and time.monotonic()<deadline:
        while Gtk.events_pending():Gtk.main_iteration()
        cp4vasp.VisCheck();time.sleep(.01)
    assert predicate(),'GUI task timed out'


def main():
    assert Gtk.init_check()[0];cp4vasp.VisInit()
    with tempfile.TemporaryDirectory() as temporary:
        root=Path(temporary)
        page=GasPhasePage(root);window=Gtk.OffscreenWindow();window.set_size_request(900,600)
        window.add(page);window.show_all()
        assert page.task is None
        ticks=[];timer=GLib.timeout_add(10,lambda:(ticks.append(1),True)[1])
        page.smiles_entry.set_text('CCO');page.build_button.clicked()
        assert page.task is not None and not page.generate_button.get_sensitive()
        pump_until(lambda:page.task is None)
        assert ticks,'GUI stopped servicing timers'
        assert page.molecule is page.generated and page.molecule.path is None,page.status.get_text()
        assert len(page.molecule.symbols)==9 and page.charge.get_text()=='0'
        assert page.multiplicity.get_text()==''
        assert page.preview_window is not None and len(page.preview_window.structure)==9
        page.generate_button.clicked();assert 'integer' in page.status.get_text()
        page.multiplicity.set_text('1')
        def choose_folder(*args,**kwargs):
            dialog=InputFolderDialog(None,*args[1:],**kwargs)
            dialog.folder.set_text(str(root));dialog.name.set_text('ethanol')
            GLib.idle_add(lambda:(dialog.dialog.response(Gtk.ResponseType.OK),False)[1])
            return dialog
        with patch('p4vasp.gtk3.gas_phase.InputFolderDialog',side_effect=choose_folder):page.generate_button.clicked()
        assert (root/'ethanol/POSCAR').exists(),page.status.get_text()
        assert 'SMILES=CCO' in (root/'ethanol/INCAR').read_text()
        page.build_button.clicked();pump_until(lambda:page.task is None)
        assert page.molecule is page.generated and page.multiplicity.get_text()==''
        page.multiplicity.set_text('1')
        selected=page.molecule;page.refresh()
        assert page.molecule is selected and page.multiplicity.get_text()=='1'
        for _ in range(20):
            while Gtk.events_pending():Gtk.main_iteration()
            time.sleep(.01)
        window.get_pixbuf().savev('/tmp/p4vasp-smiles-gas.png','png',[],[])
        page.smiles_entry.set_text('invalid smiles');page.build_button.clicked()
        pump_until(lambda:page.task is None)
        assert page.molecule is selected and 'Invalid SMILES' in page.status.get_text()
        page.smiles_entry.set_text('C.C');page.build_button.clicked()
        pump_until(lambda:page.task is None)
        assert 'XYZ' in page.status.get_text() and page.molecule is selected
        page.smiles_entry.set_text('CCCC');page.build_button.clicked();page.cancel_button.clicked()
        pump_until(lambda:page.task is None)
        assert 'cancelled' in page.status.get_text() and page.molecule is selected
        with patch('p4vasp.smiles_builder.worker_command',return_value=[os.sys.executable,'-c','import time; time.sleep(20)']):
            page.build_button.clicked();task=page.task
            pump_until(lambda:task.process is not None)
            window.destroy();task.thread.join(3)
            assert not task.thread.is_alive() and task.process.poll() is not None
            assert not page.alive
        GLib.source_remove(timer)
        while Gtk.events_pending():Gtk.main_iteration()
    print('PASS: real SMILES build/optimization, responsive GTK, preview, gas export, errors, cancel and destroy cleanup',flush=True)

if __name__=='__main__':
    try:main()
    except BaseException:
        import traceback
        traceback.print_exc();os._exit(1)
    os._exit(0)

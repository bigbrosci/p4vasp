"""Frozen GUI-to-model-worker diagnostics using only temporary synthetic inputs."""
import json
import os
from pathlib import Path
import sys
import time
import traceback


def main(args):
    if len(args)!=1:raise SystemExit('Usage: --check-models NEW_OUTPUT_DIR')
    out=Path(args[0]).resolve()
    if out.exists() and any(out.iterdir()):raise SystemExit('Model check requires a new or empty output directory')
    out.mkdir(parents=True,exist_ok=True)
    report={'frozen':bool(getattr(sys,'frozen',False)),'checks':[]}
    status=1
    try:
        from io import StringIO
        from unittest.mock import patch
        from p4vasp.gtk3 import Gtk,Gdk,GLib
        from p4vasp.model_worker import bundled_worker,launch_options
        from p4vasp.applet.ModelsApplet import ModelsApplet
        from p4vasp.Structure import Structure
        import p4vasp.gtk3.bulk as bulk_module
        import p4vasp.gtk3.gas_phase as gas_module
        import cp4vasp
        import subprocess
        assert Gtk.init_check()[0]
        worker=bundled_worker();assert worker is not None,'Bundled model worker missing'
        versions=subprocess.run([str(worker),'--versions'],capture_output=True,text=True,timeout=30,check=True,
                                **launch_options([str(worker),'--versions']))
        report['versions']=json.loads(versions.stdout)
        report['checks'].append('bundled ASE/RDKit version query with isolated child environment')
        cp4vasp.VisInit()
        window=Gtk.Window();window.set_default_size(1000,700)
        models=ModelsApplet();window.add(models.createPanel());models.initUI();window.show_all()
        def pump(until=lambda:True,timeout=30):
            end=time.monotonic()+timeout
            while time.monotonic()<end:
                cp4vasp.VisCheck()
                for _ in range(15):
                    if not Gtk.events_pending():break
                    Gtk.main_iteration()
                if until():return
                time.sleep(.01)
            raise RuntimeError('Timed out waiting for the model GUI worker')
        def screenshot(name):
            for _ in range(10):pump();time.sleep(.02)
            Gdk.pixbuf_get_from_window(window.get_window(),0,0,window.get_allocated_width(),window.get_allocated_height()).savev(str(out/name),'png',[],[])
        def auto_dialog(original,name):
            def create(*args,**kwargs):
                kwargs['folder_name']=name
                dialog=original(*args,**kwargs);dialog.folder.set_text(str(out))
                GLib.timeout_add(100,lambda:(dialog.dialog.response(Gtk.ResponseType.OK),False)[1])
                return dialog
            return create
        models.notebook.set_current_page(2);bulk=models.bulk_page
        assert 'included' in bulk.install_hint.caption.get_text() and not bulk.install_hint.copy_button.get_sensitive()
        bulk.mode.set_active(2)
        for field in bulk.repeat:field.set_text('2')
        ticks=[];timer=GLib.timeout_add(20,lambda:(ticks.append(1),True)[1])
        bulk.build_button.clicked();pump(lambda:bulk.task is None,60);GLib.source_remove(timer)
        assert bulk.result is not None,bulk.status.get_text()
        assert bulk.result['atoms']==32 and ticks,'Bulk worker failed or GUI blocked'
        bulk.preview_button.clicked();pump()
        assert bulk.preview_window is not None and len(bulk.preview_window.structure)==32
        with patch.object(bulk_module,'InputFolderDialog',side_effect=auto_dialog(bulk_module.InputFolderDialog,'Cu_bulk')):
            bulk.save_button.clicked()
        structure=Structure();structure.read(str(out/'Cu_bulk/POSCAR'));assert len(structure)==32
        assert (out/'Cu_bulk/POSCAR').read_text()==bulk.result['poscar']
        screenshot('bulk.png');bulk.close_preview()
        report['checks'].append('actual bulk GUI -> bundled ASE -> 32 Cu atoms -> native preview -> real POSCAR save dialog')
        models.notebook.set_current_page(1);gas=models.notebook.get_nth_page(1)
        assert 'included' in gas.install_hint.caption.get_text()
        gas.smiles_entry.set_text('CCO');gas.build_button.clicked();pump(lambda:gas.task is None,90)
        assert gas.generated is not None,gas.status.get_text()
        assert len(gas.generated.symbols)==9 and gas.charge.get_text()=='0'
        assert gas.multiplicity.get_text()=='','Multiplicity must remain a user confirmation'
        gas.multiplicity.set_text('1');gas.preview_button.clicked();pump()
        assert gas.preview_window is not None and len(gas.preview_window.structure)==9
        with patch.object(gas_module,'InputFolderDialog',side_effect=auto_dialog(gas_module.InputFolderDialog,'ethanol_gas')):
            gas.generate_button.clicked()
        structure=Structure();structure.read(str(out/'ethanol_gas/POSCAR'));assert len(structure)==9
        assert {p.name for p in (out/'ethanol_gas').iterdir()}=={'INCAR','KPOINTS','POSCAR'}
        screenshot('smiles.png');gas.close_preview()
        report['checks'].append('actual SMILES GUI -> bundled RDKit ethanol optimization -> native preview -> three-file export')
        bad=subprocess.run([str(worker),'--smiles'],input=json.dumps({'smiles':'[Na+].[Cl-]'}),capture_output=True,
                           text=True,timeout=30,**launch_options([str(worker),'--smiles']))
        assert bad.returncode and 'fragments' in json.loads(bad.stdout)['error'].lower()
        report['checks'].append('unsupported multi-fragment SMILES rejected without fake geometry')
        from p4vasp.smiles_builder import SmilesTask
        finished=[]
        task=SmilesTask('C'*60,lambda result,error:finished.append((result,error)))
        task.start()
        pump(lambda:task.process is not None,10)
        task.cancel();pump(lambda:bool(finished),15)
        assert finished[0][0] is None and task.process.poll() is not None
        report['checks'].append('frozen caller cancellation terminates and reaps bundled worker')
        report['ok']=True;status=0
    except BaseException:
        report['ok']=False;report['error']=traceback.format_exc()
    (out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=True),flush=True)
    os._exit(status)

"""Actual CLI XDATCAR, Control trajectory navigation and GLib playback."""
import os
from pathlib import Path
import sys
import tempfile
import time
import traceback
from testXdatcar import HEADER,FRAMES


def main():
    from p4vasp.gtk3 import Gtk
    from p4vasp import scheduler
    from p4vasp.SystemPM import systemlist,XdatcarSystemPM
    from p4vasp.applet import applets,getAppletFrame
    import cp4vasp
    import cairo
    root=Path(__file__).resolve().parents[1]
    with tempfile.TemporaryDirectory() as folder:
        path=Path(folder)/'XDATCAR';path.write_text(HEADER+FRAMES)
        os.chdir(folder);sys.argv=['p4v.py',str(path)]
        ns={'__name__':'xdatcar_gui'}
        exec(compile((root/'p4v.py').read_text().split('\nschedule(init())')[0],str(root/'p4v.py'),'exec'),ns)
        errors=[];original=ns['FrameMessageDriver'].error
        def error(self,text):errors.append(text);original(self,text)
        ns['FrameMessageDriver'].error=error
        ns['schedule'](ns['init']())
        def drain(seconds=.35):
            end=time.monotonic()+seconds
            while time.monotonic()<end:
                next(scheduler());cp4vasp.VisCheck()
                for _ in range(15):
                    if not Gtk.events_pending():break
                    Gtk.main_iteration_do(False)
                time.sleep(.003)
        drain();frame=getAppletFrame()
        assert isinstance(systemlist()[0],XdatcarSystemPM)
        frame.xml.get_widget('astart p4vasp.applet.StructureWindowControlApplet.StructureWindowControlApplet').emit('clicked');drain()
        from p4vasp.applet.StructureWindowApplet import StructureWindowApplet
        from p4vasp.applet.StructureWindowControlApplet import StructureWindowControlApplet
        owner=next(a for a in applets() if isinstance(a,StructureWindowApplet))
        control=next(a for a in applets() if isinstance(a,StructureWindowControlApplet))
        def check(index):
            drain(.06);assert owner.index==index,(owner.index,index)
            actual=owner.swin.structure
            actual.setDirect()
            assert abs(actual[0][0]-index*.1)<1e-7,(index,actual[0][0])
        assert owner.sequencetype==owner.UNDEFINED_SEQUENCE
        check(0)
        control.on_seq_forward_clicked_handler(None);check(1)
        owner.swin.win.saveScreenshot('/tmp/p4vasp-xdatcar-frame1.tga');cp4vasp.VisSync()
        control.on_seq_last_clicked_handler(None);check(2)
        owner.swin.win.saveScreenshot('/tmp/p4vasp-xdatcar-frame2.tga');cp4vasp.VisSync()
        control.on_seq_back_clicked_handler(None);check(1)
        control.on_structureitem_clicked_handler(None,owner.FINAL_SEQUENCE)
        assert abs(owner.swin.structure[0][0]-.2)<1e-7
        control.on_play_clicked_handler(None);check(0)
        drain(.24);assert owner.index>=1
        control.on_stop_clicked_handler(None);index=owner.index;drain(.3);assert owner.index==index
        control.on_seq_first_clicked_handler(None);check(0)
        control.on_play_clicked_handler(None);control.on_play_clicked_handler(None)
        drain(.8);check(2);assert not control.play_flag
        control.on_structureitem_clicked_handler(None,owner.INITIAL_SEQUENCE)
        assert abs(owner.swin.structure[0][0])<1e-7
        control.on_seq_first_clicked_handler(None);check(0)
        widget=frame.root_window;widget.check_resize();drain(.1)
        surface=cairo.ImageSurface(cairo.FORMAT_ARGB32,widget.get_allocated_width(),widget.get_allocated_height())
        widget.draw(cairo.Context(surface));surface.write_to_png('/tmp/p4vasp-xdatcar-control.png')
        # User trajectory is read only: verify actual first/middle/last in the native viewer.
        real=root/'XDATCAR'
        if real.is_file():
            from p4vasp.SystemPM import getSystem
            frame.show_load_system_fileselection();chooser=frame.load_system_fileselection
            chooser.set_filename(str(real));drain();chooser.ok_button.clicked();drain()
            s=owner.system;assert isinstance(s,XdatcarSystemPM)
            assert len(s.STRUCTURE_SEQUENCE_L)==1000
            for i in (0,499,999):
                control.setSeqIndex(i);drain(.04)
                expected=s.STRUCTURE_SEQUENCE_L[i];actual=owner.swin.structure;actual.setDirect()
                assert len(actual)==71
                assert all(abs(actual[-1][k]-expected[-1][k])<1e-7 for k in range(3))
            control.setSeqIndex(499);control.on_play_clicked_handler(None);drain(.25)
            assert owner.index>499
            control.on_stop_clicked_handler(None)
        # Switching to a regular POSCAR restores its normal initial-structure view.
        poscar=Path(folder)/'POSCAR';systemlist()[0].INITIAL_STRUCTURE.write(str(poscar))
        (Path(folder)/'CONTCAR').write_bytes(poscar.read_bytes())
        from p4vasp.SystemPM import getSystem
        owner.setSystem(getSystem(poscar));control.setSystem(owner.system)
        assert owner.sequencetype==owner.INITIAL_SEQUENCE
        assert not errors,errors
        print('PASS CLI XDATCAR / native Control first-last-step / timed playback-stop-restart / actual trajectory samples',flush=True)

if __name__=='__main__':
    try:main()
    except BaseException:traceback.print_exc();os._exit(1)
    os._exit(0)

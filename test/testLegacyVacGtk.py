"""Actual VAC page button, scheduler, calculation and visible graph."""
import os
from pathlib import Path
import sys
import tempfile
import time
import traceback


def main():
    from p4vasp.gtk3 import Gtk
    from p4vasp import scheduler
    from p4vasp.Structure import Structure
    from p4vasp.SystemPM import systemlist
    from p4vasp.applet import appletfactory,getAppletFrame
    import cp4vasp
    import numpy as np
    import cairo
    root=Path(__file__).resolve().parents[1]
    with tempfile.TemporaryDirectory(prefix='VAC GUI ') as folder:
        frames=[]
        for i in range(6):
            frame=Structure();frame.basis[0][0]=frame.basis[1][1]=frame.basis[2][2]=10
            frame.setCarthesian();frame.appendAtom(0,[i*i*.05,i*.05,0]);frame.appendAtom(0,[2+i*.02,2,2]);frames.append(frame)
        path=Path(folder)/'POSCAR';frames[0].write(str(path));frames[-1].write(str(Path(folder)/'CONTCAR'))
        os.chdir(folder);sys.argv=['p4v.py',str(path)]
        ns={'__name__':'legacy_vac_gui'}
        exec(compile((root/'p4v.py').read_text().split('\nschedule(init())')[0],str(root/'p4v.py'),'exec'),ns)
        errors=[];original=ns['FrameMessageDriver'].error
        def error(self,text):errors.append(text);original(self,text)
        ns['FrameMessageDriver'].error=error
        ns['schedule'](ns['init']())
        def drain():
            for _ in range(100):
                next(scheduler());cp4vasp.VisCheck()
                for _ in range(10):
                    if not Gtk.events_pending():break
                    Gtk.main_iteration_do(False)
                time.sleep(.002)
            assert not len(scheduler())
        drain();frame=getAppletFrame();systemlist()[0].add('CSTRUCTURE_SEQUENCE_L',frames)
        applet=appletfactory().create('p4vasp.applet.VACApplet.VACApplet');frame.showApplet(applet);drain()
        applet.xml.get_widget('multi').set_active(False)
        applet.xml.get_widget('init_entry').set_text('0')
        applet.xml.get_widget('vac_button').clicked();drain()
        assert len(applet.vac)==4 and np.isfinite(applet.vac).all()
        assert abs(applet.vac[0]-1)<1e-12
        assert applet.xml.get_widget('fft_button').get_sensitive()
        assert applet.canvas is not None and len(applet.graphdata[0][0])==4
        widget=frame.root_window;widget.resize(1200,850);drain();widget.check_resize();drain()
        surface=cairo.ImageSurface(cairo.FORMAT_ARGB32,widget.get_allocated_width(),widget.get_allocated_height())
        widget.draw(cairo.Context(surface));surface.write_to_png('/tmp/p4vasp-legacy-vac.png')
        assert not errors,errors
        print('PASS actual VAC page / Calculate button / scheduler / finite numerical result / visible graph',flush=True)

if __name__=='__main__':
    try:main()
    except BaseException:traceback.print_exc();os._exit(1)
    os._exit(0)

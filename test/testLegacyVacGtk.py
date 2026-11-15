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
        systemlist()[0].add('PARAMETERS',{'POTIM':2})
        callback_errors=[];sys.excepthook=lambda *args:callback_errors.append(args)
        applet=appletfactory().create('p4vasp.applet.VACApplet.VACApplet');frame.showApplet(applet);drain()
        applet.xml.get_widget('multi').set_active(False)
        applet.xml.get_widget('init_entry').set_text('0')
        applet.xml.get_widget('vac_button').clicked();drain()
        assert len(applet.vac)==4 and np.isfinite(applet.vac).all()
        assert abs(applet.vac[0]-1)<1e-12
        assert applet.xml.get_widget('fft_button').get_sensitive()
        assert applet.canvas is not None and len(applet.graphdata[0][0])==4
        original_vac=applet.vac.copy()
        applet.xml.get_widget('optionmenu1').set_active(1);drain()
        assert applet.showtype==1
        for count in (4,5):
            for filtered in (False,True):
                applet.vac=original_vac.copy() if count==4 else np.r_[original_vac,original_vac[-1]*.9]
                applet.xml.get_widget('filter_button').set_active(filtered)
                assert applet.xml.get_widget('wleft_entry').get_sensitive()==filtered
                applet.xml.get_widget('wleft_entry').set_text('7')
                applet.xml.get_widget('wright_entry').set_text('7')
                applet.xml.get_widget('wpolyn_entry').set_text('3')
                applet.xml.get_widget('fft_button').clicked();drain()
                assert len(applet.freq)==count and np.isfinite(applet.freq).all()
                assert len(applet.graphdata[0][0])==count//2
                if not filtered:np.testing.assert_allclose(applet.freq,np.abs(np.fft.fft(applet.vac)),rtol=1e-12)
        for index in range(4):
            applet.xml.get_widget('winopt').set_active(index)
            applet.xml.get_widget('fft_button').clicked();drain()
            assert applet.windowfunction==index and np.isfinite(applet.freq).all()
        applet.xml.get_widget('optionmenu1').set_active(2);drain()
        assert applet.showtype==2
        assert len(applet.graphdata)==2
        widget=frame.root_window;widget.resize(1200,850);drain();widget.check_resize();drain()
        surface=cairo.ImageSurface(cairo.FORMAT_ARGB32,widget.get_allocated_width(),widget.get_allocated_height())
        widget.draw(cairo.Context(surface));surface.write_to_png('/tmp/p4vasp-legacy-fft.png')
        assert not errors,errors
        assert not callback_errors,callback_errors
        print('PASS actual VAC page / Read VAC / FFT button / odd-even / filter toggle / VAC+FFT graphs',flush=True)

if __name__=='__main__':
    try:main()
    except BaseException:traceback.print_exc();os._exit(1)
    os._exit(0)

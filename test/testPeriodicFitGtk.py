"""Actual full p4vasp frame: periodic tiles fit initially, on resize and maximize."""
import os
from pathlib import Path
import sys
import tempfile
import time
import traceback

ROOT=Path(__file__).resolve().parents[1]

def main():
    from p4vasp import scheduler
    from p4vasp.gtk3 import Gtk,Gdk
    from p4vasp.applet import getAppletFrame
    from p4vasp.resource_data import ResourceStore
    import cairo
    assert Gtk.init_check()[0]
    Gtk.Settings.get_default().set_property('gtk-enable-animations',False)
    sys.excepthook=lambda *args:(traceback.print_exception(*args),os._exit(3))
    with tempfile.TemporaryDirectory() as name:
        folder=Path(name);os.chdir(folder);sys.argv=['p4v.py']
        ns={'__name__':'periodic_fit_regression'}
        exec(compile((ROOT/'p4v.py').read_text().split('\nschedule(init())')[0],str(ROOT/'p4v.py'),'exec'),ns)
        ns['schedule'](ns['init']())
        def pump(seconds=.4):
            end=time.monotonic()+seconds
            while time.monotonic()<end:
                next(scheduler())
                for _ in range(30):
                    if not Gtk.events_pending():break
                    Gtk.main_iteration_do(False)
                time.sleep(.005)
        pump(1)
        frame=getAppletFrame();assert frame is not None
        window=frame.root_window
        window.resize(640,480);pump()
        ns['startApplet'](None,'p4vasp.applet.ModelsApplet.ModelsApplet',frame);pump()
        models=frame.embedded_applet
        models.store=ResourceStore(ROOT,folder/'backups',user_root=folder/'profile')
        models.notebook.set_current_page(4);pump()
        page=models.element_table
        def check():
            assert len(page.buttons)==118
            width,height=page.grid.get_allocated_width(),page.grid.get_allocated_height()
            gx,gy=page.grid.translate_coordinates(page,0,0)
            assert gx>=0 and gy>=0 and gx+width<=page.get_allocated_width() and gy+height<=page.get_allocated_height()
            for symbol,button in page.buttons.items():
                x,y=button.translate_coordinates(page.grid,0,0)
                assert button.get_mapped() and button.get_allocated_width()>1 and button.get_allocated_height()>1
                assert x>=0 and y>=0 and x+button.get_allocated_width()<=width and y+button.get_allocated_height()<=height,(symbol,x,y,width,height)
            print('FIT',window.get_allocated_width(),window.get_allocated_height(),width,height,page.grid.font_size,flush=True)
        check()
        sizes=[]
        for width,height in ((800,600),(1100,740),(600,400),(680,500)):
            window.resize(width,height);pump(.6);window.check_resize();pump(.2);check()
            sizes.append(page.grid.font_size)
            page.buttons['Og'].clicked();assert page.editor.symbol=='Og'
            page.editor.response(Gtk.ResponseType.CANCEL)
            pump(.1)
        assert sizes[1]>sizes[2]
        def capture(path):
            window.check_resize();pump()
            shot=cairo.ImageSurface(cairo.FORMAT_ARGB32,window.get_allocated_width(),window.get_allocated_height())
            window.draw(cairo.Context(shot));shot.write_to_png(path)
        capture('/tmp/p4vasp-periodic-fit-compact.png')
        window.maximize();pump(.8);check()
        assert window.get_window().get_state() & Gdk.WindowState.MAXIMIZED
        capture('/tmp/p4vasp-periodic-fit-maximized.png')
        window.unmaximize();window.resize(640,480);pump(.8);check()
        # Single atom uses the same fitter with its original 18-column/9-row layout.
        models.notebook.set_current_page(0);pump()
        page=models._page_contents[0]
        assert page.symbol is None and not page.generate.get_sensitive()
        for width,height in ((640,480),(1100,740),(600,400)):
            window.resize(width,height);pump(.6);check()
            page.buttons['Og'].clicked()
            assert page.symbol=='Og' and page.generate.get_sensitive()
        capture('/tmp/p4vasp-single-atom-fit-compact.png')
        window.maximize();pump(.8);check()
        capture('/tmp/p4vasp-single-atom-fit-maximized.png')
        window.unmaximize();window.resize(640,480);pump(.8);check()
        page.buttons['H'].clicked();assert page.symbol=='H'
        models.notebook.set_current_page(4);pump();page=models.element_table;check()
        assert not (folder/'profile').exists(),'Layout checks must not save user settings'
        print('PASS full-frame initial/resize/maximize/restore: both periodic pages fit all 118 tiles; editing/selection preserved',flush=True)

if __name__=='__main__':
    main();os._exit(0)

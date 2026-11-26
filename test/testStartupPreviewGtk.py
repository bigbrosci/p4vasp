"""Real CLI startup preview, system changes and native Show/Control handoff."""
import os
from pathlib import Path
import sys
import tempfile
import time
import cairo

ROOT=Path(__file__).resolve().parents[1]
from p4vasp import scheduler
from p4vasp.gtk3 import Gtk
from p4vasp.applet import getAppletFrame,applets
from p4vasp.applet.StructurePreviewApplet import StructurePreviewApplet
from p4vasp.applet.StructureWindowApplet import StructureWindowApplet
from p4vasp.applet.StructureWindowControlApplet import StructureWindowControlApplet
from p4vasp.applet.InfoApplet import InfoApplet

assert Gtk.init_check()[0]
Gtk.Settings.get_default().set_property('gtk-enable-animations',False)
with tempfile.TemporaryDirectory() as name:
    folder=Path(name);os.chdir(folder)
    poscar=folder/'POSCAR'
    poscar.write_text('Water synthetic\n1\n7 0 0\n0 7 0\n0 0 7\nO H\n1 2\nCartesian\n3.5 3.5 3.5\n4.46 3.5 3.5\n3.26 4.43 3.5\n')
    original=poscar.read_bytes();sys.argv=['p4v.py',str(poscar)]
    ns={'__name__':'startup_preview_regression'}
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
    frame=getAppletFrame();preview=frame.embedded_applet
    assert isinstance(preview,StructurePreviewApplet)
    assert preview.view.get_mapped() and preview.view.data['symbols']==['O','H','H']
    assert 'O: 1' in preview.summary.get_text() and 'H: 2' in preview.summary.get_text()
    assert not any(isinstance(a,StructureWindowApplet) for a in applets())
    source=preview.system.INITIAL_STRUCTURE
    before=source.toxml();preview.view.zoom=1.5;preview.view.queue_draw();pump()
    assert source.toxml()==before and poscar.read_bytes()==original
    original_scale=list(source.scaling)
    for scales,expected in (([2.],[14.,14.,14.]),([-2744.],[14.,14.,14.]),([2.,3.,4.],[14.,21.,28.])):
        source.scaling=scales;preview.updateSystem()
        assert all(abs(preview.view.data['cell'][i][i]-expected[i])<1e-8 for i in range(3))
        assert all(abs(preview.view.data['positions'][0][i]-expected[i]/2)<1e-8 for i in range(3))
        assert source.scaling==scales
    source.scaling=original_scale;preview.updateSystem()
    preview.view.zoom=1;preview.view.queue_draw();pump()
    win=frame.root_window;win.resize(780,650);pump()
    surface=cairo.ImageSurface(cairo.FORMAT_ARGB32,win.get_allocated_width(),win.get_allocated_height())
    win.draw(cairo.Context(surface));surface.write_to_png('/tmp/p4vasp-startup-preview.png')
    # Show's actual toolbar action opens the native window and replaces preview.
    frame.xml.get_widget('astart p4vasp.applet.StructureWindowApplet.StructureWindowApplet').emit('clicked');pump()
    assert isinstance(frame.embedded_applet,StructureWindowControlApplet)
    assert preview.panel is None
    natives=[a for a in applets() if isinstance(a,StructureWindowApplet)]
    assert len(natives)==1 and natives[0].swin is not None
    # Explicit Info remains available and Show does not replace another panel.
    ns['startApplet'](None,'p4vasp.applet.InfoApplet.InfoApplet',frame);pump()
    assert isinstance(frame.embedded_applet,InfoApplet)
    frame.xml.get_widget('astart p4vasp.applet.StructureWindowApplet.StructureWindowApplet').emit('clicked');pump()
    assert isinstance(frame.embedded_applet,InfoApplet)
    # Recreate the startup panel, then activate Control directly.
    natives[0].destroyApplet();pump()
    ns['startApplet'](None,'p4vasp.applet.StructurePreviewApplet.StructurePreviewApplet',frame);pump()
    preview=frame.embedded_applet
    frame.xml.get_widget('astart p4vasp.applet.StructureWindowControlApplet.StructureWindowControlApplet').emit('clicked');pump()
    assert isinstance(frame.embedded_applet,StructureWindowControlApplet) and preview.panel is None
    assert len([a for a in applets() if isinstance(a,StructureWindowApplet)])==1
    # Empty sessions and later Open/system activation update the preview safely.
    ns['startApplet'](None,'p4vasp.applet.StructurePreviewApplet.StructurePreviewApplet',frame);pump()
    preview=frame.embedded_applet
    from p4vasp.SystemPM import SetupPM,systemlist
    empty=SetupPM();systemlist().activate(empty);pump()
    assert preview.view.data is None and 'Open a structure' in preview.summary.get_text()
    systemlist().activate(natives[0].system if natives[0].system is not empty else ns['getSystem'](str(poscar)));pump()
    assert preview.view.data and len(preview.view.data['positions'])==3
    assert poscar.read_bytes()==original
    from testEmbeddedStructureEditing import exercise
    exercise(frame,preview,folder,pump)
    print('PASS CLI embedded preview, unchanged inputs, Show/Control native handoff, Info preservation and empty/system refresh',flush=True)
os._exit(0)

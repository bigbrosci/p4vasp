"""Actual DOS graph export dialog -> PS/EPS/PDF files."""
import os
from pathlib import Path
import sys
import tempfile
import time
import traceback
from dos_fixtures import write_calculation
from testVectorExport import check_pdf


def main():
    from p4vasp import scheduler
    from p4vasp.gtk3 import Gtk
    from p4vasp.SystemPM import getSystem,systemlist
    from p4vasp.applet import applets,appletfactory,setAppletFrame
    import unittest
    import cairo
    root=Path(__file__).resolve().parents[1]
    ns={'__name__':'vector_export_gui'}
    exec(compile((root/'p4v.py').read_text().split('\nschedule(init())')[0],str(root/'p4v.py'),'exec'),ns)
    frame=ns['Frame']();frame.quitNow=lambda *_:None;frame.createFrame();frame.root_window.resize(1000,800)
    setAppletFrame(frame);appletfactory().registerApplets()
    applets().notify_on_append.append(lambda _,applet:frame.showApplet(applet))
    errors=[];sys.excepthook=lambda *args:errors.append(args)
    def drain():
        for _ in range(70):
            next(scheduler())
            for _ in range(10):
                if not Gtk.events_pending():break
                Gtk.main_iteration_do(False)
            time.sleep(.002)
    with tempfile.TemporaryDirectory(prefix='vector GUI ') as folder:
        source=write_calculation(folder,scale=.2,with_xml=False)
        systemlist().activate(getSystem(source/'DOSCAR'))
        ns['startApplet'](None,'p4vasp.applet.ElectronicApplet.ElectronicApplet',frame);drain()
        applet=frame.embedded_applet;original=[list(row) for row in applet.total_dos]
        applet.show_export_handler();drain()
        export=applet.export
        for suffix in ('ps','eps','pdf'):
            path=Path(folder)/("DOS 图 ' & %."+suffix)
            export.file_entry.set_text(str(path));drain()
            assert export.type=={'ps':2,'eps':3,'pdf':4}[suffix]
            export.xml.get_widget('export_button').clicked();drain()
            data=path.read_bytes();assert len(data)>1000
            if suffix=='pdf':check_pdf(unittest.TestCase(),data)
            else:assert data.startswith(b'%!PS') and b'%%EOF' in data
        assert applet.total_dos==original
        assert not errors,errors
        widget=export.window;widget.check_resize();drain()
        surface=cairo.ImageSurface(cairo.FORMAT_ARGB32,widget.get_allocated_width(),widget.get_allocated_height())
        widget.draw(cairo.Context(surface));surface.write_to_png('/tmp/p4vasp-vector-export-dialog.png')
        print('PASS DOS dialog export buttons -> Unicode PS/EPS/PDF files; PDF byte offsets/streams; unchanged DOS',flush=True)

if __name__=='__main__':
    try:main()
    except BaseException:traceback.print_exc();os._exit(1)
    os._exit(0)

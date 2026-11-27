"""Actual DOS graph export dialog -> DATA/AGR/FIG/SVG/PS/EPS/PDF files."""
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
        assert export.options[7]=='Portable Network Graphics (.png)'
        for suffix in ('dat','agr','fig','svg','ps','eps','pdf','png','PNG'):
            path=Path(folder)/("DOS 图 ' & %."+suffix)
            export.file_entry.set_text(str(path));drain()
            assert export.type=={'dat':0,'agr':1,'ps':2,'eps':3,'pdf':4,'fig':5,'svg':6,'png':7}[suffix.lower()]
            export.xml.get_widget('export_button').clicked();drain()

            if not path.exists():
                for error in errors:traceback.print_exception(*error)
            data=path.read_bytes();assert len(data)>50
            if suffix.lower()=='png':
                assert data.startswith(b'\x89PNG\r\n\x1a\n')
                image=cairo.ImageSurface.create_from_png(str(path))
                assert (image.get_width(),image.get_height())==(824,644)
                import numpy as np
                pixels=np.frombuffer(image.get_data(),dtype=np.uint8).reshape(image.get_height(),image.get_stride())[:,:image.get_width()*4].reshape(image.get_height(),image.get_width(),4)
                assert (pixels[:,:,:3].min(axis=2)<200).sum()>100
                image.write_to_png('/tmp/p4vasp-exported-dos-png.png')
            elif suffix=='pdf':check_pdf(unittest.TestCase(),data)
            elif suffix in ('ps','eps'):assert data.startswith(b'%!PS') and b'%%EOF' in data
            elif suffix=='fig':assert data.startswith(b'#FIG 3.2')
            elif suffix=='svg':
                from xml.etree import ElementTree
                svg=ElementTree.fromstring(data)
                assert svg.tag=='{http://www.w3.org/2000/svg}svg'
                from p4vasp.gtk3 import GdkPixbuf
                if any('svg' in format.get_name() for format in GdkPixbuf.Pixbuf.get_formats()):
                    pixbuf=GdkPixbuf.Pixbuf.new_from_file(str(path))
                    assert pixbuf.get_width()>0
                    pixbuf.savev('/tmp/p4vasp-exported-dos-svg.png','png',[],[])
                    print('SVG independently loaded by GdkPixbuf',flush=True)
            elif suffix=='agr':
                from p4vasp.graph import World
                restored=World();assert not restored.parseGrace(str(path))
                assert len(restored)>0 and len(restored[0][0])>0
            else:
                import numpy as np
                rows=[list(map(float,line.split())) for line in data.decode().splitlines() if line.strip()]
                source_data=export.world if export.data is None else export.data
                expected=[list(row) for graph in source_data for dataset in graph for row in dataset]
                np.testing.assert_allclose(rows,expected,rtol=5e-6,atol=1e-12)
        assert applet.total_dos==original
        assert not errors,errors
        widget=export.window;widget.check_resize();drain()
        surface=cairo.ImageSurface(cairo.FORMAT_ARGB32,widget.get_allocated_width(),widget.get_allocated_height())
        widget.draw(cairo.Context(surface));surface.write_to_png('/tmp/p4vasp-vector-export-dialog.png')
        print('PASS DOS dialog export buttons -> Unicode eight formats and uppercase PNG; decoded PNG/SVG/AGR, numeric DATA, PDF offsets; unchanged DOS',flush=True)

if __name__=='__main__':
    try:main()
    except BaseException:traceback.print_exc();os._exit(1)
    os._exit(0)

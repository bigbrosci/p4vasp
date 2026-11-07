"""Real DOSCAR graph zoom/render: readable numeric tick strings on both axes."""
import os
from pathlib import Path
import re
import tempfile
import time
from unittest.mock import patch
from dos_fixtures import write_calculation
from p4vasp import scheduler
from p4vasp.gtk3 import Gtk,Gdk
from p4vasp.SystemPM import getSystem,systemlist
from p4vasp.applet import applets,appletfactory,setAppletFrame

ROOT=Path(__file__).resolve().parents[1]
ns={'__name__':'tick_regression'}
exec(compile((ROOT/'p4v.py').read_text().split('\nschedule(init())')[0],str(ROOT/'p4v.py'),'exec'),ns)
frame=ns['Frame']();frame.quitNow=lambda *_:None;frame.createFrame();frame.root_window.resize(1000,800)
setAppletFrame(frame);appletfactory().registerApplets()
applets().notify_on_append.append(lambda _,applet:frame.showApplet(applet))

def drain():
    for _ in range(80):
        next(scheduler())
        for _ in range(10):
            if not Gtk.events_pending():break
            Gtk.main_iteration()
        time.sleep(.002)

with tempfile.TemporaryDirectory() as folder:
    path=write_calculation(folder,scale=.2,with_xml=False)
    systemlist().activate(getSystem(path/'DOSCAR'))
    ns['startApplet'](None,'p4vasp.applet.ElectronicApplet.ElectronicApplet',frame);drain()
    applet=frame.embedded_applet
    before=[list(row) for row in applet.total_dos]
    for factor in (.7,.5,1.6):
        applet.zoomFactor(factor);drain()
        graph=applet.world[0]
        graph.world_ymin=-.7;graph.world_ymax=1.3
        graph.world_xmin=-1.6;graph.world_xmax=.6
        with patch.object(applet.canvas,'drawString',wraps=applet.canvas.drawString) as draw:
            applet.canvas.updateGraph()
        labels=[call.args[0] for call in draw.call_args_list if re.fullmatch(r'[+-]?[0-9][0-9.eE+-]*',call.args[0])]
        assert len(labels)>10
        assert all(len(label)<=12 for label in labels),labels
        assert not any('000000000000' in label or '999999999999' in label for label in labels),labels
    assert applet.total_dos==before
    drain();window=frame.root_window
    Gdk.pixbuf_get_from_window(window.get_window(),0,0,window.get_allocated_width(),window.get_allocated_height()).savev('/tmp/p4vasp-dos-ticks.png','png',[],[])
print('PASS: DOSCAR plot zooms, both rendered tick-label sets, readable precision and unchanged DOS samples',flush=True)
os._exit(0)

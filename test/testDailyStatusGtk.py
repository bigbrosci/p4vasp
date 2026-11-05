"""Displayed footer alignment, offline day rotation and task/error priority."""
from datetime import date,timedelta
from pathlib import Path
import time
from p4vasp.gtk3 import Gtk,Gdk
from p4vasp.daily_quotes import load_quotes,quote_for_day

ROOT=Path(__file__).resolve().parents[1]
namespace={'__name__':'daily_status_regression'}
exec(compile((ROOT/'p4v.py').read_text().split('\nschedule(init())')[0],str(ROOT/'p4v.py'),'exec'),namespace)
namespace['Frame'].quitNow=lambda *_: None
frame=namespace['Frame']();frame.createFrame()
from p4vasp import msg
window=frame.root_window
window.resize(900,650)

def drain():
    for _ in range(20):
        while Gtk.events_pending():Gtk.main_iteration()
        time.sleep(.01)

driver=msg();label=driver.statusbar;progress=driver.progressbar
records=load_quotes();day=date(2026,11,4)
assert len(records)==12
assert quote_for_day(records,day)==quote_for_day(records,day)
assert quote_for_day(records,day)!=quote_for_day(records,day+timedelta(days=1))
assert quote_for_day(records,day)==quote_for_day(records,day+timedelta(days=len(records)))
driver.status('OK');driver.daily_status.refresh(day);drain()
assert label.get_text().startswith(quote_for_day(records,day)['text'])
assert '每日一句：' not in label.get_text()
assert label.create_pango_layout(label.get_text()).get_unknown_glyphs_count()==0
assert label.get_selectable() and not progress.get_visible()
footer=frame.xml.get_widget('status_frame');content=frame.xml.get_widget('applet_box')
for width in (900,700):
    window.resize(width,650);drain()
    fx,fy=footer.translate_coordinates(window,0,0)
    cx,cy=content.translate_coordinates(window,0,0)
    assert fx==cx,(fx,cx)
    assert footer.get_allocated_width()==content.get_allocated_width()
    assert fx>=frame.xml.get_widget('toolbar').get_allocated_width()
window.resize(900,650);drain()
Gdk.pixbuf_get_from_window(window.get_window(),0,0,window.get_allocated_width(),window.get_allocated_height()).savev('/tmp/p4vasp-daily-quote.png','png',[],[])
driver.status('Parsing synthetic file');driver.step(1,3);drain()
assert label.get_text()=='Parsing synthetic file' and progress.get_visible()
driver.daily_status.refresh(day+timedelta(days=1))
assert label.get_text()=='Parsing synthetic file'
assert progress.translate_coordinates(window,0,0)[1] < footer.translate_coordinates(window,0,0)[1]
driver.error('Synthetic error: missing structure')
driver.daily_status.refresh(day+timedelta(days=1))
assert label.get_text()=='ERROR: Synthetic error: missing structure'
driver.step(0,1);driver.status('OK');drain()
assert not progress.get_visible() and label.get_text().startswith(quote_for_day(records)['text'])
driver.daily_status.refresh(day+timedelta(days=1))
assert quote_for_day(records,day+timedelta(days=1))['text'] in label.get_text()
window.destroy();assert driver.daily_status.timer is None
print('PASS: daily selection/rotation, Chinese glyphs, full content-column alignment, task/error priority, progress row and timer cleanup',flush=True)
import os;os._exit(0)

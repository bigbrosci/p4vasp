"""Isolated applet startup check; uses an empty database and a synthetic structure.

Run: python3 test/gtk3_applet_smoke.py p4vasp.applet.BuilderApplet.BuilderApplet
Requires GTK3/Cairo, a display, and the compiled cp4vasp extension.
"""
import os,sys,traceback,json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
os.chdir(root);sys.path[:0]=[str(root/'lib'),str(root/'src')];os.environ['P4VASP_HOME']=str(root)
from p4vasp import gtk3 as gtk
from p4vasp.gtk3.glade import XML
import p4vasp.db
class EmptyDatabase(list):
 def connect(self):pass
 def query(self,*args):return []
p4vasp.db.getDatabase=lambda:EmptyDatabase()
namespace={'__name__':'p4v_smoke'}
exec(compile(open('p4v.py').read().split('\nschedule(init())')[0],'p4v.py','exec'),namespace)
from p4vasp.applet import appletfactory,applets,setAppletFrame
from p4vasp.SystemPM import SetupPM,systemlist
system=SetupPM();system.INCAR['SYSTEM']='GTK3 smoke'
for key,value in {'PATH':'/tmp','URL':'/tmp/POSCAR','DESCRIPTION':'','KEYWORDS':'','DATE':(2026,1,1,0,0,0,0,1,-1),'FINAL_STRUCTURE':system.INITIAL_STRUCTURE,'STRUCTURE_SEQUENCE_L':[]}.items():system.add(key,value)
from io import StringIO
system.INITIAL_STRUCTURE.read(StringIO('H test\n1\n1 0 0\n0 1 0\n0 0 1\nH\n1\nDirect\n0 0 0\n'))
system.add('KPOINT_LIST',[])
systemlist().activate(system)
frame=namespace['Frame']();xml=XML('data/glade2/frame.glade','frame_box')
frame.xml=xml;frame.applet_box=xml.get_widget('applet_box');frame.toolbar=xml.get_widget('toolbar')
window=gtk.OffscreenWindow();window.add(xml.get_widget('frame_box'));window.show_all()
setAppletFrame(frame);appletfactory().registerApplets()
applets().notify_on_append.append(lambda repository,applet:frame.showApplet(applet))
import cp4vasp
cp4vasp.VisInit()
errors=[]
sys.excepthook=lambda *args:errors.append(''.join(traceback.format_exception(*args)))
name=sys.argv[1]
try:
 if name.endswith('SelectionApplet'):
  from p4vasp.applet.SelectionApplet import SelectionApplet
  applet=SelectionApplet(xml.get_widget('selection_entry'),xml.get_widget('selection_set'),xml.get_widget('selection_none'))
  applet.initUI()
 else:
  applet=appletfactory().create(name)
  applets().activate(applet)
  assert applet.applet_ready, "Applet did not finish initializing"
  if applet.showmode in (applet.EMBEDDED_MODE, applet.EMBEDDED_ONLY_MODE):
   assert applet.panel is not None and applet.panel.get_parent() is frame.applet_box
 for _ in range(10):
  while gtk.events_pending():gtk.main_iteration()
 if errors:raise RuntimeError('\n'.join(errors))
 print('RESULT PASS',name,flush=True)
 result=0
except BaseException:
 traceback.print_exc();print('RESULT FAIL',name,flush=True)
 result=1
# Native FLTK thread cleanup is outside this isolated GTK panel smoke test.
os._exit(result)

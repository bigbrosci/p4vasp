"""Isolated UI startup without SQL, plus legacy path/session opt-in compatibility."""
import os
from pathlib import Path
import subprocess
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
COMMON='''
from p4vasp.gtk3 import Gtk
assert Gtk.init_check()[0]
'''

class DatabaseIsolationTest(unittest.TestCase):
    def run_probe(self,script):
        env=dict(os.environ);env['PYTHONPATH']=str(ROOT/'lib')+os.pathsep+str(ROOT/'src');env['P4VASP_HOME']=str(ROOT)
        result=subprocess.run([sys.executable,'-c',COMMON+script],cwd=ROOT,env=env,capture_output=True,text=True,timeout=45)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)

    def test_full_factory_resources_without_sql(self):
        self.run_probe('''
import sys,importlib.abc
blocked=[]
class NoSQL(importlib.abc.MetaPathFinder):
 def find_spec(self,fullname,path=None,target=None):
  if fullname in ('p4vasp.db','p4vasp.SQLSystemPM','pysqlite2','MySQLdb'):
   blocked.append(fullname);raise ImportError('SQL must not load for Resources')
sys.meta_path.insert(0,NoSQL())
from pathlib import Path
ns={'__name__':'database_import_probe'}
exec(compile(Path('p4v.py').read_text().split('\\nschedule(init())')[0],'p4v.py','exec'),ns)
from p4vasp.applet import appletfactory,setAppletFrame
from p4vasp.applet.appletlist import appletlist
frame=ns['Frame']();frame.quitNow=lambda *_:None;frame.createFrame();setAppletFrame(frame)
appletfactory().registerApplets()
classes=[f.Class for f in appletfactory().values()]
assert len(classes)>=len(appletlist())
assert any(c.__name__=='CommitApplet' and c.menupath is None for c in classes)
from p4vasp.setupstore import SetupProfile
SetupProfile()
from p4vasp.applet.DBApplet import DBApplet
page=DBApplet();frame.showApplet(page)
for _ in range(30):
 while Gtk.events_pending():Gtk.main_iteration_do(False)
assert not blocked,blocked
assert 'p4vasp.db' not in sys.modules and 'p4vasp.SQLSystemPM' not in sys.modules
''')

    def test_legacy_constructors_and_xml_class_names(self):
        self.run_probe('''
import sys,types
from xml.dom.minidom import parseString
calls=[]
class FakeDatabase(list):
 def connect(self):calls.append('connect')
fake=types.ModuleType('p4vasp.db')
def getDatabase():calls.append('get');return FakeDatabase()
fake.getDatabase=getDatabase;sys.modules['p4vasp.db']=fake
from p4vasp.applet.CommitApplet import CommitApplet
from p4vasp.applet.DBApplet import LegacyDBApplet,QueryTreeModel,DBApplet
assert calls==[]
DBApplet();assert calls==[]
from p4vasp.applet.Applet import AppletProfile
for name,cls in [('p4vasp.applet.CommitApplet.CommitApplet',CommitApplet),('p4vasp.applet.DBApplet.LegacyDBApplet',LegacyDBApplet)]:
 obj=AppletProfile().retrieveObj(parseString('<applet name="'+name+'"/>').documentElement)
 assert isinstance(obj,cls) and obj.gladefile in ('commit.glade','db.glade')
 assert cls.__module__+'.'+cls.__name__==name
assert calls==['get','connect','get','connect'],calls
''')

    def test_legacy_selection_loads_sql_only_on_selection(self):
        self.run_probe('''
import sys,types,importlib
from types import SimpleNamespace
module=importlib.import_module('p4vasp.applet.DBApplet')
assert 'p4vasp.SQLSystemPM' not in sys.modules
calls=[];fake=types.ModuleType('p4vasp.SQLSystemPM')
fake.SQLSystemPM=lambda db,identity:('legacy-sql',identity)
sys.modules['p4vasp.SQLSystemPM']=fake
module.systemlist=lambda:SimpleNamespace(setTemporaryActive=calls.append)
page=module.LegacyDBApplet.__new__(module.LegacyDBApplet)
db=SimpleNamespace(name='synthetic')
page.model=SimpleNamespace(query=SimpleNamespace(get=lambda i:(0,[123]),container=[db]))
page.canDeleteSelected=lambda:False
page.xml=SimpleNamespace(get_widget=lambda name:SimpleNamespace(set_sensitive=lambda value:None))
selection=SimpleNamespace(selected_foreach=lambda callback,data:callback(None,None,None,data))
# Selection callbacks supply row paths; do not query or connect a database.
selection.selected_foreach=lambda callback,data:callback(None,(0,),None,data)
page.treeselect_h(selection)
assert calls==[('legacy-sql',123)] and page.selected_dbi is db
''')

if __name__=='__main__':unittest.main()

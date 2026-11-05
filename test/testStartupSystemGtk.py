"""Real init() in isolated processes: blank sessions, explicit files, real XML errors."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import traceback

ROOT=Path(__file__).resolve().parents[1]


def child(mode):
    from p4vasp.gtk3 import Gtk,Gdk,GLib
    from p4vasp.SystemPM import systemlist,SetupPM,PoscarSystemPM,XMLSystemPM
    from p4vasp.applet import getAppletFrame
    assert Gtk.init_check()[0]
    with tempfile.TemporaryDirectory() as temporary:
        os.chdir(temporary)
        poscar='Synthetic hydrogen\n1\n4 0 0\n0 4 0\n0 0 4\nH\n1\nDirect\n0 0 0\n'
        args=[]
        if mode in ('poscar','poscar-with-xml'):
            Path('POSCAR').write_text(poscar);args=['POSCAR']
        if mode in ('bad-xml','poscar-with-xml'):Path('vasprun.xml').write_text('<modeling/>')
        sys.argv=['p4v.py',*args]
        namespace={'__name__':'startup_regression'}
        exec(compile((ROOT/'p4v.py').read_text().split('\nschedule(init())')[0],str(ROOT/'p4v.py'),'exec'),namespace)
        errors=[];driver=namespace['FrameMessageDriver'];original=driver.error
        def error(self,text):errors.append(text);original(self,text)
        driver.error=error
        done=[]
        def initialize():
            yield from namespace['init']()
            done.append(True)
        def verify():
            if not done:return True
            try:
                assert len(systemlist())==1
                system=systemlist()[0]
                if mode=='empty':assert isinstance(system,SetupPM) and len(system.INITIAL_STRUCTURE)==0
                elif mode.startswith('poscar'):
                    assert isinstance(system,PoscarSystemPM) and len(system.INITIAL_STRUCTURE)==1
                else:
                    assert isinstance(system,XMLSystemPM)
                    assert len(system.INITIAL_STRUCTURE)==0
                if mode=='bad-xml':assert any('no initial structure' in e for e in errors),errors
                else:assert not errors,errors
                if mode=='empty':
                    frame=getAppletFrame();label=frame.xml.get_widget('statusbar')
                    assert not label.get_text().startswith('ERROR'),label.get_text()
                    window=frame.root_window
                    Gdk.pixbuf_get_from_window(window.get_window(),0,0,window.get_allocated_width(),window.get_allocated_height()).savev('/tmp/p4vasp-empty-startup.png','png',[],[])
                print('PASS startup:',mode,flush=True)
                os._exit(0)
            except BaseException:
                traceback.print_exc();os._exit(1)
        namespace['schedule'](initialize())
        GLib.idle_add(namespace['idle_func'])
        GLib.timeout_add(100,verify)
        GLib.timeout_add(15000,lambda:os._exit(2))
        Gtk.main()


if __name__=='__main__':
    if len(sys.argv)>1:child(sys.argv[1])
    else:
        for mode in ('empty','poscar','poscar-with-xml','bad-xml'):
            subprocess.run([sys.executable,str(Path(__file__).resolve()),mode],cwd=ROOT,check=True,timeout=25)

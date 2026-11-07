"""Real startup, repeated DOS toolbar switches and File/Open with actual files."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import traceback
from dos_fixtures import write_calculation

ROOT=Path(__file__).resolve().parents[1]


def main(mode):
    from p4vasp import scheduler
    from p4vasp.gtk3 import Gtk,Gdk
    from p4vasp.applet import applets,getAppletFrame
    from p4vasp.SystemPM import systemlist,DoscarSystemPM
    assert Gtk.init_check()[0]
    with tempfile.TemporaryDirectory() as temporary:
        folder=write_calculation(Path(temporary)/'initial',with_xml=mode!='directory-dos')
        if mode=='directory-dos':
            folder.joinpath('POSCAR').unlink();folder.joinpath('INCAR').unlink()
        other=write_calculation(Path(temporary)/'another space',scale=3)
        os.chdir(folder)
        argument={'directory':[],'doscar':['DOSCAR'],'xml':['vasprun.xml'],'directory-dos':[]}[mode]
        sys.argv=['p4v.py',*argument]
        ns={'__name__':'dos_regression'}
        exec(compile((ROOT/'p4v.py').read_text().split('\nschedule(init())')[0],str(ROOT/'p4v.py'),'exec'),ns)
        callback_errors=[]
        def callback_error(*args):
            traceback.print_exception(*args)
            os._exit(3)
        sys.excepthook=callback_error
        ns['schedule'](ns['init']())
        def drain():
            for _ in range(120):
                next(scheduler())
                for _event in range(30):
                    if not Gtk.events_pending():break
                    Gtk.main_iteration()
                time.sleep(.002)
            assert not callback_errors,callback_errors
            assert not len(scheduler()),'scheduled graph work did not complete'
        drain();frame=getAppletFrame();frame.root_window.resize(1000,750)
        def select(name):
            ns['startApplet'](None,'p4vasp.applet.'+name+'.'+name,frame)
            drain()
            return frame.embedded_applet
        def expect_dos(scale=1):
            electronic=frame.embedded_applet
            assert electronic.system is systemlist()[0]
            assert electronic.total_dos is not None,'DOS data missing'
            assert electronic.total_dos[0]==[(-1.5,0.),(-.5,4.*scale),(.5,1.*scale)],electronic.total_dos
            assert electronic.canvas is not None and electronic.area.get_mapped()
            assert len(electronic.world[0])==1
            assert len(electronic.world[0][0].data)==3
            assert electronic.canvas.world is electronic.world
            return electronic
        select('ElectronicApplet');expect_dos()
        for name in ['InfoApplet','ModelsApplet','BuilderApplet','ElectronicControlApplet']:
            select(name);select('ElectronicApplet');expect_dos()
        # Actual file chooser/OK callback: both files, including a directory with spaces.
        for filename,scale in [('vasprun.xml',3),('DOSCAR',1),('DOSCAR',3),('vasprun.xml',1)]:
            path=(other if scale==3 else folder)/filename
            if not path.exists():continue
            select('InfoApplet')
            frame.show_load_system_fileselection()
            chooser=frame.load_system_fileselection
            chooser.set_filename(str(path));drain()
            assert Path(chooser.get_filename())==path
            chooser.ok_button.clicked();drain()
            assert not chooser.get_visible()
            select('ElectronicApplet');expect_dos(scale)
            if filename=='DOSCAR':assert isinstance(systemlist()[0],DoscarSystemPM)
            select('ModelsApplet');select('ElectronicApplet');expect_dos(scale)
        # Load a different XML while the DOS panel itself is still active.
        frame.show_load_system_fileselection();chooser=frame.load_system_fileselection
        chooser.set_filename(str(other/'vasprun.xml'));drain();chooser.ok_button.clicked();drain()
        electronic=expect_dos(3)
        electronic.setShowType(electronic.SHOW_DOS_BANDS);drain()
        assert len(electronic.eigenval)==2
        assert len(electronic.world)==2 and len(electronic.world[0])==2 and len(electronic.world[1])==1
        electronic.setShowType(electronic.SHOW_DOS_Y);drain();expect_dos(3)
        electronic.canvas.updateSize();drain()
        assert electronic.world.page_size_x==electronic.area.get_allocated_width()
        frame.root_window.resize(1100,800);drain();electronic.canvas.updateSize();drain()
        assert electronic.world.page_size_y==electronic.area.get_allocated_height()
        window=frame.root_window
        Gdk.pixbuf_get_from_window(window.get_window(),0,0,window.get_allocated_width(),window.get_allocated_height()).savev('/tmp/p4vasp-dos-'+mode+'.png','png',[],[])
        if mode=='directory':
            spin=write_calculation(Path(temporary)/'spin',with_xml=False)
            spin.joinpath('DOSCAR').write_text('1 1 1 0\n1 1 1 1 1\n300\nSynthetic\nSpin DOS\n1 -1 3 0.5 1\n-1 1 2 0 0\n0 4 5 1 2\n1 2 3 2 3\n')
            frame.show_load_system_fileselection();chooser=frame.load_system_fileselection
            chooser.set_filename(str(spin/'DOSCAR'));drain();chooser.ok_button.clicked();drain()
            electronic=frame.embedded_applet
            assert electronic.total_dos==[[(-1.5,1.),(-.5,4.),(.5,2.)],[(-1.5,-2.),(-.5,-5.),(.5,-3.)]]
            assert len(electronic.world[0])==2
            select('InfoApplet');select('ElectronicApplet')
            assert len(frame.embedded_applet.world[0])==2
        print('PASS:',mode,'startup/DOS reentry/real Open/XML refresh/bands/resize',flush=True)


if __name__=='__main__':
    if len(sys.argv)>1:
        try:main(sys.argv[1])
        except BaseException:traceback.print_exc();os._exit(1)
        os._exit(0)
    for mode in ['directory','doscar','xml','directory-dos']:
        subprocess.run([sys.executable,str(Path(__file__).resolve()),mode],check=True,timeout=60)

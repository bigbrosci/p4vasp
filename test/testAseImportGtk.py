"""Real CLI initialization, Show toolbar and File/Open with imported structures."""
import os
from pathlib import Path
import sys
import tempfile
import time
import traceback


def main():
    from p4vasp.gtk3 import Gtk
    from p4vasp import scheduler
    from p4vasp.SystemPM import systemlist, ASESystemPM
    from p4vasp.applet import applets, getAppletFrame
    import cp4vasp
    root=Path(__file__).resolve().parents[1]
    assert Gtk.init_check()[0]
    with tempfile.TemporaryDirectory(prefix='ASE GUI ') as temporary:
        os.chdir(temporary)
        path=Path('water.xyz').resolve()
        path.write_text('3\nwater\nO 0 0 0\nH 0.96 0 0\nH -0.24 0.93 0\n')
        sys.argv=['p4v.py',str(path)]
        ns={'__name__':'ase_import_regression'}
        exec(compile((root/'p4v.py').read_text().split('\nschedule(init())')[0],str(root/'p4v.py'),'exec'),ns)
        errors=[]
        original=ns['FrameMessageDriver'].error
        def error(self,text):errors.append(text);original(self,text)
        ns['FrameMessageDriver'].error=error
        ns['schedule'](ns['init']())
        def drain():
            for _ in range(100):
                next(scheduler());cp4vasp.VisCheck()
                for _ in range(15):
                    if not Gtk.events_pending():break
                    Gtk.main_iteration()
                time.sleep(.003)
            assert not len(scheduler())
        drain();frame=getAppletFrame()
        assert isinstance(systemlist()[0],ASESystemPM)
        frame.xml.get_widget('astart p4vasp.applet.StructureWindowApplet.StructureWindowApplet').emit('clicked')
        drain()
        from p4vasp.applet.StructureWindowApplet import StructureWindowApplet
        owner=next(a for a in applets() if isinstance(a,StructureWindowApplet))
        assert len(owner.swin.structure)==3
        from p4vasp.util import getAtomtypes
        from p4vasp.viewer_style import display_values
        table=getAtomtypes();record=owner.swin.structure_drawer.info.getRecord(0)
        radii,colors=display_values(['O'],[.66],[[1,0,0]])
        assert abs(record.radius-radii[0])<1e-6
        assert abs(record.red-colors[0][0])<1e-6
        assert abs(owner.swin.getRadiusFactor()-.5)<1e-8
        assert abs(owner.swin.structure_drawer.getBondFactor()-1.2)<1e-8
        assert cp4vasp.getDefaultPrimitivesResolution()==32
        assert owner.swin.structure_drawer.getCellLineWidth()==1
        assert abs(owner.swin.structure.basis[0][0]-21.2)<1e-10
        owner.swin.win.saveScreenshot('/tmp/p4vasp-ase-import-water.tga');cp4vasp.VisSync()
        crystal=Path('crystal.extxyz').resolve()
        crystal.write_text('1\nLattice="4 0 0 1 5 0 0 0 6" Properties=species:S:1:pos:R:3 pbc="T T T"\nCu 1 2 3\n')
        frame.show_load_system_fileselection();chooser=frame.load_system_fileselection
        chooser.set_filename(str(crystal));drain();chooser.ok_button.clicked();drain()
        assert not chooser.get_visible()
        assert owner.system is systemlist()[0] and len(owner.swin.structure)==1
        assert owner.system.ASE_IMPORT_INFO['boxed'] is False
        assert abs(owner.swin.structure.basis[1][0]-1)<1e-10
        owner.swin.win.saveScreenshot('/tmp/p4vasp-ase-import-crystal.tga');cp4vasp.VisSync()
        assert not errors,errors
        old=systemlist()[0]
        bad=Path('broken.xyz').resolve();bad.write_text('2\nbroken\nH 0 0 0\n')
        frame.show_load_system_fileselection();chooser=frame.load_system_fileselection
        chooser.set_filename(str(bad));drain()
        assert Path(chooser.get_filename())==bad
        chooser.ok_button.clicked();drain()
        assert errors and 'Can not load selected system' in errors[-1]
        assert systemlist()[0] is old and owner.system is old
        print('PASS actual CLI XYZ -> Show/native; Open extxyz -> same viewer; bad-file error preserves active system',flush=True)


if __name__=='__main__':
    try:main()
    except BaseException:traceback.print_exc();os._exit(1)
    os._exit(0)

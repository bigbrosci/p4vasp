"""Real Show controls, Cairo equivalence, frame editing and backend handoff."""
import os
from pathlib import Path
import sys
import tempfile
import time
import cairo
from p4vasp.gtk3 import Gtk,Gdk
from p4vasp import scheduler
from p4vasp.applet import getAppletFrame,applets
from p4vasp.Selection import selection
from p4vasp.Structure import Structure
from p4vasp.gtk3.structure_window import CairoStructureWindow
ROOT=Path(__file__).resolve().parents[1]
assert Gtk.init_check()[0]
Gtk.Settings.get_default().set_property('gtk-enable-animations',False)
with tempfile.TemporaryDirectory() as directory:
    folder=Path(directory);os.chdir(folder)
    geometry='Water\n1\n7 0 0\n0 7 0\n0 0 7\nO H\n1 2\nCartesian\n3.5 3.5 3.5\n4.46 3.5 3.5\n3.26 4.43 3.5\n'
    path=folder/'POSCAR'
    path.write_text(geometry.replace('Cartesian\n','Selective dynamics\nCartesian\n')
                    .replace('3.5 3.5 3.5\n','3.5 3.5 3.5 F F F\n')
                    .replace('4.46 3.5 3.5\n','4.46 3.5 3.5 F T F\n')
                    .replace('3.26 4.43 3.5\n','3.26 4.43 3.5 T T T\n'))
    (folder/'CONTCAR').write_bytes(path.read_bytes())
    sys.argv=['p4v.py',str(path)];namespace={'__name__':'cairo_show_regression'}
    exec(compile((ROOT/'p4v.py').read_text().split('\nschedule(init())')[0],str(ROOT/'p4v.py'),'exec'),namespace)
    namespace['schedule'](namespace['init']())
    def pump(seconds=.3):
        end=time.monotonic()+seconds
        while time.monotonic()<end:
            next(scheduler())
            for _ in range(25):
                if not Gtk.events_pending():break
                Gtk.main_iteration_do(False)
            time.sleep(.004)
    deadline=time.monotonic()+10
    while time.monotonic()<deadline:
        pump(.15)
        frame=getAppletFrame()
        if frame is not None and frame.embedded_applet is not None and frame.embedded_applet.view.data:
            break
    assert frame is not None and frame.embedded_applet is not None, 'startup preview did not open'
    initial=frame.embedded_applet
    expected=initial.view.data.copy();expected_radii=initial.view.ball_radii[:]
    frame.xml.get_widget('astart p4vasp.applet.StructureWindowApplet.StructureWindowApplet').emit('clicked');pump()
    from p4vasp.applet.StructureWindowApplet import StructureWindowApplet
    owner=next(a for a in applets() if isinstance(a,StructureWindowApplet))
    window=owner.swin;control=frame.embedded_applet
    assert isinstance(window,CairoStructureWindow) and window._legacy is None
    assert window.view.data is not None,window.controller.summary.get_text()
    assert initial.view.constrained==window.view.constrained=={0,1}
    assert window.view.ball_radii==expected_radii
    for field in ('symbols','radii','colors','cell'):assert window.view.data[field]==expected[field]
    for a,b in zip(window.view.data['positions'],expected['positions']):assert all(abs(x-y)<1e-12 for x,y in zip(a,b))
    assert window.getRadiusFactor()==.5 and window.view.radius_factor==.5
    source=owner.system.INITIAL_STRUCTURE
    for scales,expected_cell in (([2.],[14.,14.,14.]),([-2744.],[14.,14.,14.]),([2.,3.,4.],[14.,21.,28.])):
        source.scaling=scales;owner.updateSeq()
        assert all(abs(window.view.data['cell'][i][i]-expected_cell[i])<1e-8 for i in range(3))
        assert source.scaling==scales
    source.scaling=[1.];owner.updateSeq()
    # Existing Control actions now drive Cairo.
    import cp4vasp
    oracle=cp4vasp.VisNavDrawer()
    for name in ('setFrontView','setBackView','setLeftView','setRightView','setTopView','setBottomView'):
        getattr(oracle,name)();getattr(window.navigator,name)()
        assert all(abs(window.view.rotation[i][j]-oracle.getRotMatElement(i,j))<1e-12 for i in range(3) for j in range(3)),name
    control.on_top_button_clicked_handler(None);control.on_home_button_clicked_handler(None)
    control.csadj1.set_value(2);pump();assert window.view.repeats==(2,1,1)
    control.csadj1.set_value(1);control.sss_adj.set_value(1.5);pump()
    assert window.view.radius_factor==.75
    control.sss_adj.set_value(1)
    selection().setSelection([1]);selection().notify(None)
    control.on_hide_button_clicked_handler(None);assert 1 in window.view.hidden
    control.on_show_button_clicked_handler(None);assert 1 not in window.view.hidden
    control.on_hidecell_button_clicked_handler(None);assert not window.view.show_cell
    control.on_showcell_button_clicked_handler(None);assert window.view.show_cell
    window.setArrows([[.1,0,0],[0,.2,0],[0,0,.3]]);window.setArrowsScale(2);pump()
    assert window.getArrowsScale()==2
    window.win.saveScreenshot(str(folder/'shot.tga'));assert (folder/'shot.tga').read_bytes()[2]==2
    from p4vasp.export_image import snapshot
    state=snapshot(window);assert len(state['scene'][1])==3 and state['camera']['zoom']>0
    from p4vasp.render_cli import camera_point
    window.view.pan=(13.,-7.,0.);window.view.zoom=1.6
    state=snapshot(window)
    for point in window.view.display_positions():
        x,y,_=window.view.project(point);a,b,_=camera_point(point,state['camera'])
        assert abs(x-(window.win.w/2+25*a))<1e-9
        assert abs(y-(window.win.h/2-25*b))<1e-9
    control.csadj1.set_value(2);pump();state=snapshot(window)
    assert all(abs(a-b)<1e-10 for p,q in zip(state['scene'][1],window.view.display_positions()) for a,b in zip(p,q))
    zoom=window.view.zoom;owner.updateSeq();assert window.view.zoom==zoom
    control.csadj1.set_value(1);pump()
    # Shared selected edit changes canonical structure, not just a display copy.
    source=owner.system.INITIAL_STRUCTURE;before=list(source[1])
    event=Gdk.Event.new(Gdk.EventType.KEY_PRESS);event.keyval=Gdk.KEY_Right;event.state=0
    window.view.emit('key-press-event',event);pump()
    assert list(source[1])!=before and len(window.view.positions)==3
    owner.setSequenceType(owner.FINAL_SEQUENCE);pump()
    if owner.swin.view.data:
        before=source.toxml();selection().setSelection([0]);window.controller.edit('delete');assert source.toxml()==before
    owner.setSequenceType(owner.INITIAL_SEQUENCE);pump()
    selection().setSelection([0]);selection().notify(None)
    pump();shot=cairo.ImageSurface(cairo.FORMAT_ARGB32,window.widget.get_allocated_width(),window.widget.get_allocated_height())
    window.widget.draw(cairo.Context(shot));shot.write_to_png('/tmp/p4vasp-cairo-show.png')
    # Perspective hands the full existing interface to the dedicated renderer.
    window.navigator.setPerspective(1);pump()
    assert owner.swin is window._legacy and window._legacy_visible
    owner.swin.navigator.setFrontView();owner.swin.navigator.setPerspective(0);pump()
    assert owner.swin is window and not window._legacy_visible and window.widget.get_visible()
    volume=folder/'CHGCAR';volume.write_text(geometry+'\n2 2 2\n0 0.2 0.4 0.6 0.8 1.0 1.2 1.4\n')
    window.setChgcar(str(volume));pump()
    assert owner.swin is window._legacy and owner.swin.chgcar is not None
    owner.swin.setIsosurfaceLevel(.3);owner.swin.win.redraw();pump()
    owner.swin.setChgcar(None);pump()
    assert owner.swin is window and window.chgcar is None and window.widget.get_visible()
    # Closing/reopening removes the GTK window and preserves the main application.
    owner.system.add('STRUCTURE_SEQUENCE_L',[Structure(source),Structure(source)])
    owner.setSequenceType(owner.UNDEFINED_SEQUENCE);control.on_play_clicked_handler(None)
    assert control.play_flag
    window.widget.close();pump();assert owner.swin is None and owner not in applets()
    assert not control.play_flag
    frame.xml.get_widget('astart p4vasp.applet.StructureWindowApplet.StructureWindowApplet').emit('clicked');pump()
    assert any(isinstance(a,StructureWindowApplet) and isinstance(a.swin,CairoStructureWindow) for a in applets())
    print('PASS Cairo Show/common appearance, Control/nav/repeat/radius/hide/cell/arrows, screenshot/snapshot, editing, perspective return and close/reopen',flush=True)
os._exit(0)

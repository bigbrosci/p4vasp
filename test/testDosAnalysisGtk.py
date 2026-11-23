"""Actual DOS applet plus asynchronous pymatgen, source switching and clipboard."""
import os
from pathlib import Path
import sys
import tempfile
import time
import traceback
from dos_projected_fixtures import projected_calculation

ROOT=Path(__file__).resolve().parents[1]

def main():
    from p4vasp import scheduler
    from p4vasp.gtk3 import Gtk,GLib,Gdk
    from p4vasp.applet import getAppletFrame
    assert Gtk.init_check()[0]
    sys.excepthook=lambda *args:(traceback.print_exception(*args),os._exit(3))
    with tempfile.TemporaryDirectory() as tmp:
        folder=projected_calculation(tmp,xml=True)
        os.chdir(folder);sys.argv=['p4v.py',str(folder/'DOSCAR')]
        ns={'__name__':'dos_analysis_regression'}
        exec(compile((ROOT/'p4v.py').read_text().split('\nschedule(init())')[0],str(ROOT/'p4v.py'),'exec'),ns)
        ns['schedule'](ns['init']())
        def spin(seconds=.3,until=None):
            end=time.monotonic()+seconds
            while time.monotonic()<end:
                next(scheduler())
                for _ in range(30):
                    if not Gtk.events_pending():break
                    Gtk.main_iteration()
                if until and until():return
                time.sleep(.005)
            if until:assert until(),'Timed out'
        spin(10,lambda:getAppletFrame() is not None);spin(.8)
        frame=getAppletFrame();frame.root_window.resize(1100,850)
        ns['startApplet'](None,'p4vasp.applet.ElectronicApplet.ElectronicApplet',frame);spin(.8)
        electronic=frame.embedded_applet;panel=electronic.dos_analysis
        assert isinstance(panel,Gtk.Frame)
        assert electronic.dos_split.get_orientation()==Gtk.Orientation.HORIZONTAL
        assert electronic.dos_split.get_child1() is electronic.dos_plot_scroll
        assert electronic.dos_plot_scroll.get_child().get_child() is electronic.xml.get_widget('vbox2')
        assert electronic.dos_split.get_child2() is panel
        assert electronic.total_dos is not None
        original=[channel[:] for channel in electronic.total_dos]
        from p4vasp.applet.ElectronicApplet import Line
        from types import SimpleNamespace
        line=Line(selection='1',orbital=['dxy','dyz','dz2','dxz','dx2'],spin=2,scale=-1)
        list(line.updateDosGen(SimpleNamespace(system=electronic.system,struct=electronic.system.INITIAL_STRUCTURE,e_fermi=2.)))
        assert len(line.dos)==401 and abs(line.dos[200][1]+15)<1e-8

        spin()
        left=electronic.dos_split.get_child1()
        assert panel.translate_coordinates(electronic.dos_split,0,0)[0]>left.translate_coordinates(electronic.dos_split,0,0)[0]
        assert panel.calculate.get_mapped() and panel.export.get_mapped()
        assert not panel.hint.get_visible()
        electronic.lines.append(line);panel.use_line()
        assert panel.request()['atoms']==[1] and panel.request()['spin']=='down'
        electronic.lines.remove(line)
        from p4vasp.Selection import selection
        old_selection=selection().data[:]
        try:
            selection().data=[(1,0,0,0)];panel.use_selection()
            assert panel.request()['atoms']==[2]
        finally:selection().data=old_selection

        panel.mode.set_active(2);panel.selection.set_text('1');panel.spin.set_active(1)
        ticks=[];timer=GLib.timeout_add(10,lambda:(ticks.append(1),True)[1])
        panel.calculate.clicked();assert panel.job is not None
        spin(30,lambda:panel.job is None);GLib.source_remove(timer)
        assert panel.result is not None,panel.status.get_text()
        assert len(ticks)>2
        assert abs(panel.result['rows'][0][1]+1)<1e-8
        assert len(panel.model)==5 and panel.export.get_sensitive()
        assert electronic.total_dos==original,'Analysis changed original plotting densities'
        assert not any(name=='pymatgen' or name.startswith('pymatgen.') for name in sys.modules)
        panel.copy.clicked();assert 'd-band center' in Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD).wait_for_text()
        from p4vasp.dos_analysis import save_result
        output=folder/'analysis.csv';save_result(output,panel.result);assert 'emin' in output.read_text()
        from unittest.mock import patch
        from p4vasp.gtk3.file_dialogs import CompactFileDialog
        def actual_export_dialog(*args,**kwargs):
            dialog=CompactFileDialog(*args,**kwargs)
            GLib.timeout_add(100,lambda:(dialog.dialog.response(Gtk.ResponseType.OK),False)[1])
            return dialog
        with patch('p4vasp.gtk3.file_dialogs.CompactFileDialog',side_effect=actual_export_dialog):
            panel.export.clicked()
        assert (folder/'d-band-analysis.csv').exists(),panel.status.get_text()

        panel.emin.set_text('-2');assert panel.result is None and not panel.export.get_sensitive()
        panel.emax.set_text('1');panel.calculate.clicked()
        panel.cancel.clicked();assert panel.job is None
        spin(.5);assert panel.result is None,'Cancelled callback restored stale result'
        # Existing real File/Open refresh must invalidate result and analyze XML source.
        frame.show_load_system_fileselection();chooser=frame.load_system_fileselection
        chooser.set_filename(str(folder/'vasprun.xml'));spin();chooser.ok_button.clicked();spin(.8)
        panel=electronic.dos_analysis
        assert panel.result is None
        panel.mode.set_active(2);panel.selection.set_text('1');panel.spin.set_active(1)
        panel.emin.set_text('');panel.emax.set_text('')
        panel.calculate.clicked();spin(30,lambda:panel.job is None)
        assert panel.result is not None,panel.status.get_text()
        assert Path(panel.result['path']).name=='vasprun.xml'
        assert abs(panel.result['rows'][0][1]+1)<1e-8
        spin(1.)
        window=frame.root_window
        window.check_resize();spin(.3)
        # Draw GTK widgets to Cairo instead of capturing WSL compositor pixels.
        import cairo
        surface=cairo.ImageSurface(cairo.FORMAT_ARGB32,window.get_allocated_width(),window.get_allocated_height())
        window.draw(cairo.Context(surface));surface.write_to_png('/tmp/p4vasp-dos-analysis-side.png')
        # Missing environment fails gracefully and does not remove the old DOS plot.
        from unittest.mock import patch
        with patch('p4vasp.dos_analysis.worker_command',side_effect=RuntimeError('pymatgen is unavailable. Run bash install/install-science.sh.')):
            panel.calculate.clicked();spin(10,lambda:panel.job is None)
        assert panel.result is None and electronic.total_dos is not None
        assert panel.hint.get_visible(),panel.status.get_text()
        split=electronic.dos_split
        position=split.get_position()-35
        split.set_position(position);spin(.3)
        assert split.get_position()==position,'Divider reset after a user adjustment'
        window.resize(900,650);spin(.8);window.check_resize();spin(.3)
        assert panel.get_mapped() and electronic.area.get_mapped()
        assert split.get_child1().get_allocated_width()>100 and panel.get_allocated_width()>100
        assert panel.calculate.get_mapped() and panel.export.get_mapped()
        print('Compact allocation:',window.get_allocated_width(),window.get_allocated_height(),flush=True)
        compact=cairo.ImageSurface(cairo.FORMAT_ARGB32,window.get_allocated_width(),window.get_allocated_height())
        window.draw(cairo.Context(compact));compact.write_to_png('/tmp/p4vasp-dos-analysis-side-compact.png')

        print('PASS: actual DOSCAR/XML analysis, responsive GTK, raw plot preserved, copy/export, cancellation/source invalidation and missing-library hint',flush=True)

if __name__=='__main__':
    main();os._exit(0)

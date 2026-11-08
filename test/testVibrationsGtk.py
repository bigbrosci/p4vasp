"""Actual Frame toolbar/CLI, embedded preview, animation, Scale/export and ASE UI."""
from io import StringIO
import json
import os
from pathlib import Path
import sys
import tempfile
import time
import traceback
from vibration_fixtures import write_calculation


def main():
    from p4vasp.gtk3 import Gtk,GLib
    from p4vasp import scheduler
    from p4vasp.SystemPM import systemlist,VibrationSystemPM
    from p4vasp.applet import getAppletFrame
    from p4vasp.Structure import Structure
    import cairo
    root=Path(__file__).resolve().parents[1]
    assert Gtk.init_check()[0]
    with tempfile.TemporaryDirectory(prefix='vibration GUI ') as temporary:
        folder=Path(temporary);path=write_calculation(folder/'calculation')
        original=path.read_bytes();original_poscar=(path.parent/'POSCAR').read_bytes()
        os.chdir(folder);sys.argv=['p4v.py',str(path)]
        namespace={'__name__':'vibrations_regression'}
        exec(compile((root/'p4v.py').read_text().split('\nschedule(init())')[0],str(root/'p4v.py'),'exec'),namespace)
        errors=[];old=namespace['FrameMessageDriver'].error
        def error(self,text):errors.append(text);old(self,text)
        namespace['FrameMessageDriver'].error=error
        namespace['schedule'](namespace['init']())
        def pump(until=lambda:True,timeout=10):
            end=time.monotonic()+timeout
            while time.monotonic()<end:
                for _ in range(40):
                    next(scheduler())
                    if Gtk.events_pending():Gtk.main_iteration()
                if until():return
                time.sleep(.01)
            raise AssertionError('GUI wait timed out')
        pump(lambda:not len(scheduler()))
        frame=getAppletFrame();frame.root_window.resize(1050,800)
        assert isinstance(systemlist()[0],VibrationSystemPM)
        button=frame.xml.get_widget('astart p4vasp.applet.VibrationsApplet.VibrationsApplet')
        button.emit('clicked');pump()
        page=frame.embedded_applet.page
        assert page.view.get_mapped() and len(page.store)==6
        assert page.thermo.get_expanded()
        assert [column.get_title() for column in page.tree.get_columns()]==['Mode','cm⁻¹','Type']
        for width in (700,900,1200):
            frame.root_window.resize(width,750)
            for _ in range(15):pump();time.sleep(.02)
            rect=page.tree.get_visible_rect()
            assert sum(column.get_width() for column in page.tree.get_columns())<=rect.width, (width,rect.width)
            x,y=page.mode_scroll.translate_coordinates(frame.root_window,0,0)
            assert x>=0 and x+page.mode_scroll.get_allocated_width()<=frame.root_window.get_allocated_width(),width
            if width==700:
                widget=frame.root_window
                surface=cairo.ImageSurface(cairo.FORMAT_ARGB32,widget.get_allocated_width(),widget.get_allocated_height())
                widget.check_resize();widget.draw(cairo.Context(surface));surface.write_to_png('/tmp/p4vasp-vibrations-compact.png')
        frame.root_window.resize(1050,800)
        for _ in range(15):pump();time.sleep(.02)
        assert page.tools.get_orientation()==Gtk.Orientation.HORIZONTAL
        x,y=page.displacement.translate_coordinates(page.tools,0,0)
        assert x>=page.periodic_controls.get_allocated_width()

        assert page.play.get_active() and page.timer is not None
        initial=json.dumps(page.view.positions)
        pump(lambda:json.dumps(page.view.positions)!=initial)
        page.tree.get_selection().select_path(2);pump()
        assert page.mode==2 and page.play.get_active()
        assert not page.scale.get_sensitive() and not page.save_button.get_sensitive()
        page.tree.get_selection().select_path(0);pump()
        page.zero();assert page.timer is None and page.view.positions==page.data['positions']
        for scale in (.1,.2,-.1,0,.2):
            page.scale.set_value(scale);pump()
            assert not page.play.get_active() and page.timer is None
            assert abs(page.view.positions[0][0]-(4+scale*.4))<1e-12
        snapshot=json.dumps(page.data,sort_keys=True)
        page.repeat[0].set_value(2);page.repeat[1].set_value(2);pump()
        assert page.view.repeats==(2,2,1) and len(page.view.indices)==8
        assert len(page.view.cell_edges)>12
        display=page.view.display_positions()
        for index,offset,position in zip(page.view.indices,page.view.offsets,display):
            for axis in range(3):assert abs(position[axis]-page.view.positions[index][axis]-offset[axis])<1e-12
        page.cell_visible.set_active(False);assert not page.view.show_cell
        page.cell_visible.set_active(True);assert page.view.show_cell
        assert json.dumps(page.data,sort_keys=True)==snapshot
        with tempfile.TemporaryDirectory() as expanded:
            target=Path(expanded)/'POSCAR';page.export_poscar(target)
            assert len(Structure(str(target)))==2
            assert page.view.repeats==(2,2,1)
        for _ in range(10):pump();time.sleep(.02)
        widget=frame.root_window
        surface=cairo.ImageSurface(cairo.FORMAT_ARGB32,widget.get_allocated_width(),widget.get_allocated_height())
        widget.check_resize();widget.draw(cairo.Context(surface));surface.write_to_png('/tmp/p4vasp-vibrations-periodic.png')
        for widget in page.repeat:widget.set_value(1)
        pump()
        adj=page.scale.get_adjustment()
        assert adj.get_lower()==-1 and adj.get_upper()==1 and adj.get_step_increment()==.1
        def answer_save(name='POSCAR_displaced'):
            browser=getattr(page,'file_dialog',None)
            if browser and browser.saving and browser.dialog.get_visible():
                browser.navigate(folder);browser.filename.set_text(name)
                browser.dialog.response(Gtk.ResponseType.OK);return False
            return True
        GLib.timeout_add(50,answer_save);page.save_button.clicked();pump()
        output=folder/'POSCAR_displaced'
        assert output.exists(),page.status.get_text()
        structure=Structure(str(output));structure.setCartesian()
        assert abs(structure[0][0]-4.08)<1e-12
        assert [bool(v) for v in structure.selective[1]]==[True,False,True]
        try:page.export_poscar(output)
        except FileExistsError:pass
        else:raise AssertionError('Existing output was overwritten')
        assert path.read_bytes()==original and (path.parent/'POSCAR').read_bytes()==original_poscar
        expander=next(child for child in page.get_children() if isinstance(child,Gtk.Expander))
        expander.set_expanded(True);page.state.set_active(1)
        ticks=[];timer=GLib.timeout_add(10,lambda:(ticks.append(1),True)[1])
        page.calculate.clicked();pump(lambda:page.job is None,30);GLib.source_remove(timer)
        assert ticks and page.thermo_result is not None,page.status.get_text()
        assert page.thermo_result['kind']=='F' and page.thermo_result['excluded_modes']==[1]
        assert page.result_panel.stack.get_visible_child_name()=='result'
        assert page.calculate.is_sensitive() and page.save_thermo.is_sensitive()
        assert page.result_panel.names['free_energy_eV'].get_text()=='Total F'
        assert 'ΔF' in page.result_panel.summary.get_text()
        assert abs(float(page.result_panel.values['ZPE_eV'].get_text())-page.thermo_result['ZPE_eV'])<1e-6
        x,y=page.result_panel.translate_coordinates(page.thermo_content,0,0)
        assert x>=page.thermo_box.get_allocated_width()

        page.fields['temperature'].set_text('310');assert page.thermo_result is None
        assert page.result_panel.stack.get_visible_child_name()=='empty'
        page.state.set_active(0);page.calculate.clicked();pump(lambda:page.job is None,30)
        assert page.thermo_result is not None and page.thermo_result['excluded_imaginary_modes']==[1]
        assert 'floor' not in page.fields and 'imaginary_tolerance' not in page.fields
        page.state.set_active(1);page.calculate.clicked();pump(lambda:page.job is None,30)
        assert page.thermo_result is not None
        pump()
        position=page.save_button.translate_coordinates(frame.root_window,0,0)
        assert position[0]+page.save_button.get_allocated_width()<=frame.root_window.get_allocated_width()
        def capture(name):
            frame.root_window.present()
            for _ in range(8):pump();time.sleep(.03)
            widget=frame.root_window
            surface=cairo.ImageSurface(cairo.FORMAT_ARGB32,widget.get_allocated_width(),widget.get_allocated_height())
            widget.check_resize();widget.draw(cairo.Context(surface));surface.write_to_png('/tmp/'+name+'.png')
        capture('p4vasp-vibrations-thermo')
        # Switch panels: animation/timers must stop, then returning must reload modes.
        page.play.set_active(True)
        namespace['startApplet'](None,'p4vasp.applet.InfoApplet.InfoApplet',frame);pump()
        assert page.timer is None
        button.emit('clicked');pump();page=frame.embedded_applet.page
        assert len(page.store)==6
        gas=write_calculation(folder/'gas',imaginary=())
        page.load_path(gas);pump(lambda:page.job is None,30)
        def cancel_gas():
            browser=getattr(page,'gas_dialog',None)
            if browser and browser.dialog.get_visible():
                assert browser.temperature.get_text()=='298.15' and browser.pressure.get_text()=='101325'
                browser.temperature.set_text('500');browser.pressure.set_text('200000')
                browser.dialog.response(Gtk.ResponseType.CANCEL);return False
            return True
        GLib.timeout_add(50,cancel_gas);page.model.set_active(1)
        assert page.job is None and page.thermo_result is None
        assert 'cancelled' in page.status.get_text()
        assert page.fields['temperature'].get_text()=='298.15' and page.fields['pressure'].get_text()=='101325'
        page.model.set_active(0)
        answers=[]
        def answer_gas():
            browser=getattr(page,'gas_dialog',None)
            if not browser or not browser.dialog.get_visible():return True
            if not answers:
                browser.geometry.set_active(1);browser.spin.set_text('0.3')
                browser.dialog.response(Gtk.ResponseType.OK);answers.append('invalid');return True
            if len(answers)==1:
                assert 'Spin must' in browser.error.get_text()
                browser.spin.set_text('1');browser.symmetry.set_text('2')
                browser.temperature.set_text('0');browser.pressure.set_text('nan')
                browser.dialog.response(Gtk.ResponseType.OK);answers.append('invalid conditions');return True
            assert 'positive and finite' in browser.error.get_text()
            browser.temperature.set_text('350');browser.pressure.set_text('200000')
            assert browser.chosen==[5]
            dialog=browser.dialog;button=dialog.get_widget_for_response(Gtk.ResponseType.OK)
            position=button.translate_coordinates(dialog,0,0)
            assert position[0]+button.get_allocated_width()<=dialog.get_allocated_width()
            assert position[1]+button.get_allocated_height()<=dialog.get_allocated_height()
            assert dialog.get_allocated_width()<=640 and dialog.get_allocated_height()<=480,(dialog.get_allocated_width(),dialog.get_allocated_height())
            surface=cairo.ImageSurface(cairo.FORMAT_ARGB32,dialog.get_allocated_width(),dialog.get_allocated_height())
            dialog.check_resize();dialog.draw(cairo.Context(surface));surface.write_to_png('/tmp/p4vasp-gas-thermo-dialog.png')
            browser.dialog.response(Gtk.ResponseType.OK);answers.append('valid');return False
        from unittest.mock import patch
        from types import SimpleNamespace
        import p4vasp.gtk3.file_dialogs as dialogs
        GLib.timeout_add(80,answer_gas)
        with patch.object(dialogs,'workarea',return_value=SimpleNamespace(width=640,height=480)):
            page.model.set_active(1)
        pump(lambda:page.job is None,30)
        assert answers==['invalid','invalid conditions','valid']
        assert page.thermo_result is not None and page.thermo_result['kind']=='G',page.status.get_text()
        assert page.thermo_result['temperature_K']==350 and page.thermo_result['pressure_Pa']==200000
        assert 'ΔG' in page.result_panel.summary.get_text()
        assert '350 K' in page.result_panel.conditions.get_text() and '200000 Pa' in page.result_panel.conditions.get_text()
        capture('p4vasp-thermochemistry-gas-result')
        assert page.fields['temperature'].get_text()=='350' and page.fields['pressure'].get_text()=='200000'
        assert page.thermo_result['request_settings']['spin']=='1.0'
        assert page.thermo_result['request_settings']['symmetry']=='2'
        GLib.timeout_add(50,answer_save,'thermochemistry.json');page.save_thermo.clicked();pump()
        report=json.loads((folder/'thermochemistry.json').read_text())
        assert report['kind']=='G' and report['selected_modes']==[6] and report['source']==str(gas)
        assert report['temperature_K']==350 and report['pressure_Pa']==200000
        assert (folder/'thermochemistry.py').is_file()
        assert '350.0' in (folder/'thermochemistry.py').read_text() and '200000.0' in (folder/'thermochemistry.py').read_text()
        assert 'Saved' in page.status.get_text() and 'thermochemistry.py' in page.status.get_text()
        # Hidden gas choices must never restrict a later harmonic calculation.
        page.model.set_active(0);page.calculate.clicked();pump(lambda:page.job is None,30)
        assert page.thermo_result['selected_modes']==list(range(1,7))
        # Asynchronous source loading, absent constraints and explicit export confirmation.
        no_flags=write_calculation(folder/'without flags',flags=False)
        def answer_open():
            browser=getattr(page,'file_dialog',None)
            if browser and not browser.saving and browser.dialog.get_visible():
                browser.select_file(no_flags);browser.dialog.response(Gtk.ResponseType.OK);return False
            return True
        GLib.timeout_add(50,answer_open);page.open_button.clicked();pump(lambda:page.job is None,30)
        assert page.data['constraints_source'] is None
        page.scale.set_value(.1);assert not page.save_button.get_sensitive()
        page.accept_flags.set_active(True);assert page.save_button.get_sensitive()
        page.export_poscar(folder/'unconstrained.POSCAR')
        # A cancelled worker must not replace the active snapshot with a late callback.
        active=page.data;page.load_path(path);job=page.job;page.cancel()
        pump(lambda:job.process is None or job.process.poll() is not None,10)
        assert page.data is active
        capture('p4vasp-vibrations-preview')
        assert not errors,errors
        page.destroy();assert page.timer is None and page.job is None
        print('PASS real CLI OUTCAR/toolbar, mode animation, signed dimensionless slider, real POSCAR save, flags, thermo/error, panel return, async load/cancel/destroy',flush=True)


if __name__=='__main__':
    try:main()
    except BaseException:traceback.print_exc();os._exit(1)
    os._exit(0)

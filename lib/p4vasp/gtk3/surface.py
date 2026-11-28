"""Lazy ASE surface builder using the existing model worker/preview/save flows."""
from io import StringIO
from pathlib import Path
import re
from p4vasp.gtk3 import Gtk, GLib
from p4vasp.gtk3.file_dialogs import entry, CompactFileDialog
from p4vasp.gtk3.single_atom import InputFolderDialog
from p4vasp.ase_surface import PRESETS, SurfaceTask, parameters, reposition_result


class SurfacePage(Gtk.Box):
    def __init__(self, bulk_result):
        super().__init__(orientation=Gtk.Orientation.VERTICAL,spacing=8)
        self.set_border_width(8)
        self.bulk_result=bulk_result
        self.result=None;self.task=None;self.alive=True;self.directory=None;self.preview_window=None
        self.source_poscar=None;self.source_path=None;self.placement='center';self._positioning=False
        self.bulk_parameters={};self._showing_preset=True
        grid=Gtk.Grid(column_spacing=8,row_spacing=8)
        self.source_mode=0
        self.preset_button=Gtk.ToggleButton(label='Metal preset')
        self.use_bulk=Gtk.ToggleButton(label='Use bulk result')
        self.open_button=Gtk.ToggleButton(label='Open POSCAR / CIF')
        self.source_buttons=(self.preset_button,self.use_bulk,self.open_button)
        sources=Gtk.Box(spacing=8,homogeneous=True)
        for button in self.source_buttons:sources.pack_start(button,True,True,0)
        self.sync_source_buttons()
        grid.attach(sources,0,0,4,1)
        self.source_label=Gtk.Label(label='Metal preset uses standard ASE surface cells.',xalign=0)
        self.source_label.set_line_wrap(True);self.source_label.set_max_width_chars(60)
        grid.attach(self.source_label,0,1,4,1)
        self.preset=Gtk.ComboBoxText()
        for name in PRESETS:self.preset.append_text(name)
        self.preset.set_active(0)
        self.symbol=entry('Cu');self.a=entry('3.615');self.c=entry('')
        self.indices=[entry(v) for v in (1,1,1)]
        self.layers=entry('4');self.repeat=[entry('2'),entry('2')]
        self.vacuum=entry('10');self.fixed=entry('2');self.tolerance=entry('0.3')
        def row(index,label,widgets):
            title=Gtk.Label(label=label,xalign=0)
            grid.attach(title,0,index,1,1)
            box=Gtk.Box(spacing=6)
            for widget in widgets:box.pack_start(widget,True,True,0)
            grid.attach(box,1,index,3,1)
            return title
        row(2,'Metal surface',[self.preset]);row(3,'Element / a (Å) / c (Å)',[self.symbol,self.a,self.c])
        row(4,'Miller indices (h k l)',self.indices)
        self.layer_title=Gtk.Label(label='Atomic layers',xalign=0)
        grid.attach(self.layer_title,0,5,1,1);grid.attach(self.layers,1,5,3,1)
        row(6,'In-plane repeat (nx ny)',self.repeat)
        self.vacuum_title=row(7,'Vacuum EACH side (Å)',[self.vacuum])
        self.vacuum.set_tooltip_text('Total empty space is twice this value. Bottom keeps 0.1 Å below the slab and the remainder above.')
        row(8,'Fix bottom geometric layers',[self.fixed]);row(9,'Layer tolerance (Å)',[self.tolerance])
        self.center_button=Gtk.RadioButton.new_with_label_from_widget(None,'Center')
        self.bottom_button=Gtk.RadioButton.new_with_label_from_widget(self.center_button,'Bottom')
        for button,placement in ((self.center_button,'center'),(self.bottom_button,'bottom')):
            button.set_mode(False);button.connect('toggled',self.position_changed,placement)
        row(10,'Slab position',[self.center_button,self.bottom_button])
        self.settings=grid;self.pack_start(grid,False,False,0)
        actions=Gtk.FlowBox();actions.set_selection_mode(Gtk.SelectionMode.NONE)
        self.build_button=Gtk.Button(label='Build surface');self.cancel_button=Gtk.Button(label='Cancel')
        self.preview_button=Gtk.Button(label='Preview 3D');self.save_button=Gtk.Button(label='Save POSCAR')
        for button in (self.build_button,self.cancel_button,self.preview_button,self.save_button):actions.add(button)
        self.pack_start(actions,False,False,0)
        self.summary=Gtk.Label(xalign=0);self.status=Gtk.Label(xalign=0)
        for label in (self.summary,self.status):
            label.set_line_wrap(True);label.set_max_width_chars(65);label.set_selectable(True)
            self.pack_start(label,False,False,0)
        self.status.set_text('')
        from p4vasp.gtk3.install_hint import InstallHint
        self.install_hint=InstallHint('ASE','install-science.sh');self.pack_end(self.install_hint,False,False,0)
        self.preset_button.connect('clicked',lambda *_:None if self._source_sync else self.set_source(0))
        self.use_bulk.connect('clicked',self.from_bulk);self.open_button.connect('clicked',self.open)
        for widget in (self.preset,self.symbol,self.a,self.c,*self.indices,self.layers,*self.repeat,self.vacuum,self.fixed,self.tolerance):
            widget.connect('changed',self.changed)
        self.build_button.connect('clicked',self.build);self.cancel_button.connect('clicked',self.cancel)
        self.preview_button.connect('clicked',self.preview);self.save_button.connect('clicked',self.save)
        self.connect('destroy',self.destroyed)
        self.update_fields();self.set_busy(False)

    def sync_source_buttons(self):
        self._source_sync=True
        try:
            for index,button in enumerate(self.source_buttons):button.set_active(index==self.source_mode)
        finally:self._source_sync=False

    def set_source(self,index,refresh=False):
        previous=self.source_mode;self.source_mode=index;self.sync_source_buttons()
        if previous!=index or refresh:self.changed()

    def update_fields(self):
        preset=self.source_mode==0
        for widget in (self.preset,self.symbol,self.a):widget.set_sensitive(preset)
        self.c.set_sensitive(preset and self.preset.get_active_text()=='hcp0001')
        self._updating_fields=True
        try:
            fields=(self.symbol,self.a,self.c)
            if not preset:
                if self._showing_preset:self._preset_values=[widget.get_text() for widget in fields]
                values=[self.bulk_parameters.get(key,'') for key in ('name','a','c')] if self.source_mode==1 else ['','','']
                for widget,value in zip(fields,values):widget.set_text(str(value))
            elif not self._showing_preset:
                for widget,value in zip(fields,self._preset_values):widget.set_text(value)
            self._showing_preset=preset
            for widget,value in zip(self.indices,PRESETS[self.preset.get_active_text()]):
                widget.set_sensitive(not preset)
                if preset and widget.get_text()!=str(value):widget.set_text(str(value))
        finally:self._updating_fields=False
        self.layer_title.set_text('Atomic layers' if preset else 'ASE equivalent layers')
        if preset:self.source_label.set_text('Metal preset uses standard ASE surface cells.')
        elif self.source_mode==1:
            self.source_label.set_text('Bulk snapshot loaded. Lattice fields show its build inputs (read only); cutting uses the full cell, including repeats.' if self.source_poscar else 'Click Use bulk result after building a crystal.')
        else:self.source_label.set_text(self.source_path or 'Choose a periodic bulk POSCAR / CIF.')

    def changed(self,*_):
        if getattr(self,'_updating_fields',False):return
        self.update_fields();self.result=None;self.summary.set_text('');self.close_preview()
        self.preview_button.set_sensitive(False);self.save_button.set_sensitive(False)
        self.status.set_text('Settings changed. Build again; Miller indices refer to the chosen input cell.')

    def from_bulk(self,*_):
        if self._source_sync:return
        result=self.bulk_result()
        if not result:
            self.sync_source_buttons()
            self.status.set_text('Build a bulk structure in the Bulk tab first, then click Use bulk result.');return
        self.source_poscar=result['poscar'];self.bulk_parameters=dict(result.get('request',{}));self.set_source(1,refresh=True)
        self.source_label.set_text('Snapshot of bulk result: '+result['formula']+'; lattice fields are read only. Cutting uses this full input cell.')

    def open(self,*_):
        if self._source_sync:return
        self.file_dialog=CompactFileDialog(self.parent_window(),self.directory or '.', 'Open bulk POSCAR / CIF')
        path=self.file_dialog.run()
        if path:
            self.source_path=str(path);self.directory=Path(path).parent;self.set_source(2,refresh=True)
            self.source_label.set_text(str(path))
        else:self.sync_source_buttons()

    def request(self):
        source=('preset','poscar','file')[self.source_mode]
        request=dict(source=source,placement=self.placement,preset=self.preset.get_active_text(),symbol=self.symbol.get_text(),
            a=self.a.get_text(),c=self.c.get_text(),indices=[w.get_text() for w in self.indices],
            layers=self.layers.get_text(),repeat=[w.get_text() for w in self.repeat],vacuum=self.vacuum.get_text(),
            fixed_layers=self.fixed.get_text(),layer_tolerance=self.tolerance.get_text(),
            poscar=self.source_poscar or '',path=self.source_path or '')
        return parameters(request)

    def set_busy(self,busy):
        self.settings.set_sensitive(not busy);self.build_button.set_sensitive(not busy);self.cancel_button.set_sensitive(busy)
        for button in (self.preview_button,self.save_button):button.set_sensitive(not busy and self.result is not None)

    def build(self,*_):
        if self.task is not None:return
        try:request=self.request()
        except ValueError as error:self.status.set_text(str(error));return
        self.result=None;self.summary.set_text('');self.close_preview()
        task=SurfaceTask(request,lambda result,error:GLib.idle_add(self.finished,task,result,error))
        self.task=task;self.set_busy(True);self.status.set_text('Building surface with ASE…');task.start()

    def finished(self,task,result,error):
        if not self.alive or self.task is not task:return False
        self.task=None
        if task.cancelled.is_set():error='Surface generation cancelled.'
        if error:self.result=None;self.status.set_text(error)
        else:
            self.result=result
            self.update_summary()
            self.status.set_text('Preview or save POSCAR + surface.json. Generated slab is an initial model, not an optimized or stability-validated surface.')
        self.set_busy(False);return False

    def update_summary(self):
        result=self.result
        self.summary.set_text('%s · %d atoms · ASE %s\n%d geometric layers; %d fixed atoms. %s: vacuum bottom %.6g Å / top %.6g Å.' %
            (result['formula'],result['atoms'],result['ase_version'],result['geometric_layers'],
             result['fixed_atoms'],result['placement'].title(),result['vacuum_bottom'],result['vacuum_top']))

    def position_changed(self,button,placement):
        if self._positioning or not button.get_active():return
        previous=self.placement;preview_open=False
        try:
            if self.result is not None:
                positioned=reposition_result(self.result,placement)
                preview_open=self.preview_window is not None
                self.result=positioned;self.update_summary()
            self.placement=placement
            self.vacuum_title.set_text('Vacuum EACH side (Å)' if placement=='center' else 'Half total vacuum (Å)')
            self.status.set_text('Center: vacuum on both sides.' if placement=='center' else 'Bottom: lowest atom z = 0.1 Å; cell and total vacuum unchanged.')
            if preview_open:self.preview()
        except Exception as error:
            self._positioning=True
            (self.center_button if previous=='center' else self.bottom_button).set_active(True)
            self._positioning=False;self.status.set_text(str(error))

    def cancel(self,*_):
        if self.task:self.task.cancel();self.cancel_button.set_sensitive(False);self.status.set_text('Cancelling surface generation…')

    def preview(self,*_):
        if self.result is None:return
        try:
            from math import pi
            from p4vasp.Structure import Structure
            from p4vasp.gtk3.mode_view import ModeView, _show_rotation
            from p4vasp.gtk3.structure_view import structure_data
            structure=Structure();structure.read(StringIO(self.result['poscar']))
            data=structure_data(structure)
            if self.preview_window is None:
                window=Gtk.Window(transient_for=self.parent_window(), destroy_with_parent=True)
                window.set_default_size(600,500)
                window.connect('destroy',self.preview_closed)
                view=ModeView()
                view.wrap_positions=False
                view.radius_factor=.5
                window.add(view)
                self.preview_window=window
            window=self.preview_window
            window.set_title('Surface preview — '+self.result['formula'])
            view=window.get_child()
            # View along -Y so +Z is upward; ModeView fits the full cell.
            view.rotation=_show_rotation(pi/2,0)
            view.set_data(data)
            window.show_all()
            window.present()
            self.status.set_text('X marks atoms with one or more fixed coordinates.')
        except Exception as error:self.status.set_text(str(error))

    def preview_closed(self,*_):
        self.preview_window=None

    def parent_window(self):
        window=self.get_toplevel();return window if isinstance(window,Gtk.Window) else None

    def save(self,*_):
        if self.result is None:return
        from p4vasp.single_atom_inputs import write_contents
        from p4vasp.surface_replay import surface_contents
        result=self.result;files=surface_contents(result)
        output=InputFolderDialog(self.parent_window(),result['formula'],self.directory,title='Save surface POSCAR',
            folder_name=re.sub('[^A-Za-z0-9_-]','_',result['formula'])+'_surface',
            summary='Creates POSCAR, surface.json and replay scripts:\nrebuild_surface.py / rebuild_surface.sh\nExisting folders are not overwritten.',
            writer=lambda parent,name:write_contents(files,parent,name),action_label='Save POSCAR').run()
        if output:self.directory=output.parent;self.status.set_text('Saved structure and replay scripts to '+str(output))

    def close_preview(self):
        if self.preview_window is not None:
            self.preview_window.destroy()

    def destroyed(self,*_):
        self.alive=False
        if self.task:self.task.cancel()
        self.close_preview()

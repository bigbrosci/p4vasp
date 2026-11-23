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
        grid=Gtk.Grid(column_spacing=8,row_spacing=8)
        self.source=Gtk.ComboBoxText()
        for name in ('Metal preset','Bulk result','Structure file'): self.source.append_text(name)
        self.source.set_active(0)
        self.use_bulk=Gtk.Button(label='Use bulk result');self.open_button=Gtk.Button(label='Open POSCAR / CIF')
        sources=Gtk.Box(spacing=8);sources.pack_start(self.use_bulk,False,False,0);sources.pack_start(self.open_button,False,False,0)
        grid.attach(Gtk.Label(label='Source',xalign=0),0,0,1,1);grid.attach(self.source,1,0,3,1)
        grid.attach(sources,0,1,4,1)
        self.source_label=Gtk.Label(label='Metal preset uses standard ASE surface cells.',xalign=0)
        self.source_label.set_line_wrap(True);self.source_label.set_max_width_chars(60)
        grid.attach(self.source_label,0,2,4,1)
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
        row(3,'Metal surface',[self.preset]);row(4,'Element / a (Å) / c (Å)',[self.symbol,self.a,self.c])
        row(5,'Miller indices (h k l)',self.indices)
        self.layer_title=Gtk.Label(label='Atomic layers',xalign=0)
        grid.attach(self.layer_title,0,6,1,1);grid.attach(self.layers,1,6,3,1)
        row(7,'In-plane repeat (nx ny)',self.repeat)
        self.vacuum_title=row(8,'Vacuum EACH side (Å)',[self.vacuum])
        self.vacuum.set_tooltip_text('Total empty space is twice this value. Bottom keeps 0.1 Å below the slab and the remainder above.')
        row(9,'Fix bottom geometric layers',[self.fixed]);row(10,'Layer tolerance (Å)',[self.tolerance])
        self.center_button=Gtk.RadioButton.new_with_label_from_widget(None,'Center')
        self.bottom_button=Gtk.RadioButton.new_with_label_from_widget(self.center_button,'Bottom')
        for button,placement in ((self.center_button,'center'),(self.bottom_button,'bottom')):
            button.set_mode(False);button.connect('toggled',self.position_changed,placement)
        row(11,'Slab position',[self.center_button,self.bottom_button])
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
        self.status.set_text('Choose a source. Miller indices refer to the INPUT cell; use a conventional bulk cell for conventional indices. Bottom-layer rule replaces input constraints.')
        from p4vasp.gtk3.install_hint import InstallHint
        self.install_hint=InstallHint('ASE','install-science.sh');self.pack_end(self.install_hint,False,False,0)
        self.use_bulk.connect('clicked',self.from_bulk);self.open_button.connect('clicked',self.open)
        for widget in (self.source,self.preset,self.symbol,self.a,self.c,*self.indices,self.layers,*self.repeat,self.vacuum,self.fixed,self.tolerance):
            widget.connect('changed',self.changed)
        self.build_button.connect('clicked',self.build);self.cancel_button.connect('clicked',self.cancel)
        self.preview_button.connect('clicked',self.preview);self.save_button.connect('clicked',self.save)
        self.connect('destroy',self.destroyed)
        self.update_fields();self.set_busy(False)

    def update_fields(self):
        preset=self.source.get_active()==0
        for widget in (self.preset,self.symbol,self.a):widget.set_sensitive(preset)
        self.c.set_sensitive(preset and self.preset.get_active_text()=='hcp0001')
        self._updating_fields=True
        try:
            for widget,value in zip(self.indices,PRESETS[self.preset.get_active_text()]):
                widget.set_sensitive(not preset)
                if preset and widget.get_text()!=str(value):widget.set_text(str(value))
        finally:self._updating_fields=False
        self.layer_title.set_text('Atomic layers' if preset else 'ASE equivalent layers')
        if preset:self.source_label.set_text('Metal preset uses standard ASE surface cells.')
        elif self.source.get_active()==1:
            self.source_label.set_text('Bulk snapshot loaded; indices refer to its cell, not an automatically standardized cell.' if self.source_poscar else 'Click Use bulk result after building a crystal.')
        else:self.source_label.set_text(self.source_path or 'Choose a periodic bulk POSCAR / CIF.')

    def changed(self,*_):
        if getattr(self,'_updating_fields',False):return
        self.update_fields();self.result=None;self.summary.set_text('');self.close_preview()
        self.preview_button.set_sensitive(False);self.save_button.set_sensitive(False)
        self.status.set_text('Settings changed. Build again; Miller indices refer to the chosen input cell.')

    def from_bulk(self,*_):
        result=self.bulk_result()
        if not result:
            self.status.set_text('Build a bulk structure in the Bulk tab first, then click Use bulk result.');return
        self.source_poscar=result['poscar'];self.source.set_active(1);self.changed()
        self.source_label.set_text('Snapshot of bulk result: '+result['formula']+'; indices refer to this cell, with no automatic conventional-cell conversion.')

    def open(self,*_):
        self.file_dialog=CompactFileDialog(self.parent_window(),self.directory or '.', 'Open bulk POSCAR / CIF')
        path=self.file_dialog.run()
        if path:
            self.source_path=str(path);self.directory=Path(path).parent;self.source.set_active(2);self.changed()
            self.source_label.set_text(str(path))

    def request(self):
        source=('preset','poscar','file')[self.source.get_active()]
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
            from p4vasp.Structure import Structure
            from p4vasp.gtk3.gas_phase import show_model_preview
            structure=Structure();structure.read(StringIO(self.result['poscar']))
            self.preview_window=show_model_preview(structure,'Surface preview — '+self.result['formula'],show_cell=True)
            # View along -Y so +Z is upward; fit the cell to expose vacuum.
            self.preview_window.navigator.setBottomView()
            self.preview_window.fitToStructure(include_cell=True)
            for index,layer in enumerate(self.result['layer_numbers']):
                if layer<=self.result['request']['fixed_layers']:self.preview_window.selectAtom(index)
            self.preview_window.redraw()
            self.status.set_text('Preview rings mark fixed bottom atoms. Source geometry and saved flags are unchanged.')
        except Exception as error:self.status.set_text(str(error))

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
            if self.preview_window.win.getTitle().startswith('Surface preview'):
                import cp4vasp
                self.preview_window.win.hide();cp4vasp.VisSync()
            self.preview_window=None

    def destroyed(self,*_):
        self.alive=False
        if self.task:self.task.cancel()
        self.close_preview()

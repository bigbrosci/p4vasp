"""Frequency selection, display-only animation, signed displacement and ASE UI."""
import math
from pathlib import Path
import time
from p4vasp.gtk3 import Gtk, GLib
from p4vasp.gtk3.mode_view import ModeView
from p4vasp.gtk3.thermo_result import ThermoResult
from p4vasp.gtk3.install_hint import InstallHint
from p4vasp.gtk3.file_dialogs import CompactFileDialog, fit_dialog
from p4vasp.thermo_replay import save_thermochemistry
from p4vasp.vibrations import task, displaced_structure, gas_mode_count


def entry(value=''):
    widget=Gtk.Entry();widget.set_text(str(value));widget.set_width_chars(9);return widget


class GasThermoDialog:
    """Review gas parameters and the exact proposed modes before automatic work."""
    def __init__(self,page):
        self.page=page
        self.dialog=Gtk.Dialog(title='Gas molecule thermochemistry',transient_for=page.parent(),modal=True,use_header_bar=False)
        self.dialog.add_buttons('Cancel',Gtk.ResponseType.CANCEL,'Calculate',Gtk.ResponseType.OK)
        fit_dialog(self.dialog,page.parent(),500,300)
        content=self.dialog.get_content_area();content.set_border_width(10)
        scroll=Gtk.ScrolledWindow();scroll.set_policy(Gtk.PolicyType.AUTOMATIC,Gtk.PolicyType.AUTOMATIC)
        box=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=9);scroll.add(box);content.pack_start(scroll,True,True,0)
        grid=Gtk.Grid(column_spacing=10,row_spacing=8)
        self.geometry=Gtk.ComboBoxText()
        for label in ('nonlinear','linear','monatomic'):self.geometry.append_text(label)
        self.geometry.set_active(page.geometry.get_active())
        self.spin=entry(page.fields['spin'].get_text());self.symmetry=entry(page.fields['symmetry'].get_text())
        self.temperature=entry(page.fields['temperature'].get_text())
        self.pressure=entry(page.fields['pressure'].get_text())
        for i,(label,widget) in enumerate((('Geometry',self.geometry),('Spin S (not multiplicity)',self.spin),('Symmetry number',self.symmetry),('Temperature (K)',self.temperature),('Pressure (Pa)',self.pressure))):
            grid.attach(Gtk.Label(label=label,xalign=0),0,i,1,1);grid.attach(widget,1,i,1,1)
        box.pack_start(grid,False,False,0)
        conditions=Gtk.Label(label=page.state.get_active_text(),xalign=0)
        conditions.set_line_wrap(True);conditions.set_max_width_chars(50);box.pack_start(conditions,False,False,0)
        self.summary=Gtk.Label(xalign=0);self.summary.set_line_wrap(True);self.summary.set_max_width_chars(50);self.summary.set_selectable(True)
        box.pack_start(self.summary,False,False,0)
        self.error=Gtk.Label(xalign=0);self.error.set_line_wrap(True);self.error.set_max_width_chars(50);box.pack_start(self.error,False,False,0)
        self.geometry.connect('changed',lambda *_:self.update_modes())
        self.update_modes(preserve=True)

    def update_modes(self,preserve=False):
        page=self.page;n=len(page.data['symbols'])
        count=gas_mode_count(page.data,self.geometry.get_active_text())
        candidates=sorted((i for i,m in enumerate(page.data['modes']) if not m['imaginary'] and m['cm1']>0),key=lambda i:page.data['modes'][i]['cm1'],reverse=True)
        current=[i for i,row in enumerate(page.store) if row[0]]
        self.chosen=current if preserve and len(current)==count else sorted(candidates[:max(0,count)])
        valid=count>=0 and len(self.chosen)==count
        self.dialog.set_response_sensitive(Gtk.ResponseType.OK,valid)
        included=[page.data['modes'][i]['index'] for i in self.chosen]
        excluded=[m['index'] for i,m in enumerate(page.data['modes']) if i not in self.chosen]
        self.summary.set_text('Selected modes: %s\nExcluded modes: %s\n%s'%(included,excluded,
            'Calculate confirms these molecular modes. Highest real modes are proposed if the current count differs. Cancel to review mode animations.' if valid else 'Insufficient real modes for this geometry / stationary point.'))

    def run(self):
        self.dialog.show_all()
        try:
            while self.dialog.run()==Gtk.ResponseType.OK:
                try:
                    spin=float(self.spin.get_text());symmetry=int(self.symmetry.get_text())
                    if not math.isfinite(spin) or spin<0 or abs(2*spin-round(2*spin))>1e-8 or symmetry<1:
                        raise ValueError('Spin must be nonnegative integer/half-integer; symmetry must be a positive integer.')
                except ValueError as error:
                    self.error.set_text(str(error));continue
                try:
                    temperature=float(self.temperature.get_text());pressure=float(self.pressure.get_text())
                    if not all(math.isfinite(value) and value>0 for value in (temperature,pressure)):
                        raise ValueError('Temperature and pressure must be positive and finite.')
                except ValueError as error:
                    self.error.set_text(str(error));continue
                return self.geometry.get_active(),str(spin),str(symmetry),self.chosen,self.temperature.get_text().strip(),self.pressure.get_text().strip()
            return None
        finally:self.dialog.destroy()


class VibrationsPage(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL,spacing=7)
        self.set_border_width(8)
        self.data=None;self.mode=0;self.job=None;self.timer=None;self.alive=True;self.thermo_result=None
        self.request_id=0;self.pending_path=None;self.energy_source=None
        top=Gtk.Box(spacing=7)
        self.open_button=Gtk.Button(label='Open frequency OUTCAR')
        self.cancel_button=Gtk.Button(label='Cancel');self.cancel_button.set_sensitive(False)
        self.source=Gtk.Label(label='No frequency data loaded',xalign=0)
        self.source.set_ellipsize(3);self.source.set_hexpand(True)
        for widget in (self.open_button,self.cancel_button,self.source):top.pack_start(widget,widget is self.source,True,0)
        self.pack_start(top,False,False,0)
        self.layout_grid=Gtk.Grid(column_spacing=12,row_spacing=7)
        self.layout_grid.set_column_homogeneous(True)
        self.cells=[]
        compact_css=Gtk.CssProvider()
        compact_css.load_from_data(b'spinbutton button {min-width: 14px; padding: 1px;} spinbutton entry {min-width: 22px; padding: 2px;} flowboxchild {padding: 0;}')
        def add_flow(flow,widget):
            flow.add(widget);widget.get_parent().get_style_context().add_provider(compact_css,Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        def cell(widget,title=None,expand=False):
            box=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=6);box.set_border_width(6)
            box.set_hexpand(True);box.set_vexpand(expand)
            if title:
                label=Gtk.Label(xalign=0);label.set_markup('<b>'+title+'</b>');box.pack_start(label,False,False,0)
            box.pack_start(widget,True,True,0);self.cells.append(box)
            return box
        left=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=5)
        self.view=ModeView();self.view.set_size_request(200,200)
        self.preview_overlay=Gtk.Overlay();self.preview_overlay.add(self.view)
        left.pack_start(self.preview_overlay,True,True,0)
        playback=Gtk.FlowBox();playback.set_selection_mode(Gtk.SelectionMode.NONE)
        playback.set_min_children_per_line(1);playback.set_max_children_per_line(3)
        playback.set_column_spacing(3);playback.set_row_spacing(3)
        self.play=Gtk.ToggleButton(label='Play / Pause')
        self.amplitude=Gtk.SpinButton.new_with_range(.1,10,.1);self.amplitude.set_value(1)
        self.period=Gtk.SpinButton.new_with_range(.2,10,.1);self.period.set_value(1.5)
        self.amplitude.set_width_chars(2);self.period.set_width_chars(2)
        for widget in (self.amplitude,self.period):widget.get_style_context().add_provider(compact_css,Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        for label,widget in (('',self.play),('Amp. ×',self.amplitude),('Period (s)',self.period)):
            group=Gtk.Box(spacing=3)
            if label:group.pack_start(Gtk.Label(label=label),False,False,0)
            group.pack_start(widget,False,False,0);add_flow(playback,group)
        self.mode_info=Gtk.Label(xalign=0);self.mode_info.set_line_wrap(True);self.mode_info.set_max_width_chars(28)
        self.mode_info.set_halign(Gtk.Align.START);self.mode_info.set_valign(Gtk.Align.START)
        self.mode_info.set_margin_start(8);self.mode_info.set_margin_top(8)
        css=Gtk.CssProvider();css.load_from_data(b'.mode-caption {background-color: rgba(255,255,255,0.88); padding: 4px 6px; border-radius: 4px;}')
        self.mode_info.get_style_context().add_class('mode-caption')
        self.mode_info.get_style_context().add_provider(css,Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self.preview_overlay.add_overlay(self.mode_info);self.preview_overlay.set_overlay_pass_through(self.mode_info,True)
        self.layout_grid.attach(cell(left,'Structure',True),0,0,1,1)
        self.store=Gtk.ListStore(bool,int,str,str)
        self.tree=Gtk.TreeView(model=self.store)
        for label,column,width in (('Mode',1,48),('cm⁻¹',2,100),('Type',3,90)):
            renderer=Gtk.CellRendererText()
            tree_column=Gtk.TreeViewColumn(label,renderer,text=column)
            tree_column.set_sizing(Gtk.TreeViewColumnSizing.FIXED);tree_column.set_fixed_width(width)
            self.tree.append_column(tree_column)
        self.tree.get_selection().connect('changed',self.select_mode)
        scroll=Gtk.ScrolledWindow();scroll.set_policy(Gtk.PolicyType.AUTOMATIC,Gtk.PolicyType.AUTOMATIC)
        scroll.set_size_request(240,245);scroll.add(self.tree);self.mode_scroll=scroll
        self.layout_grid.attach(cell(scroll,'Vibrational modes',True),1,0,1,1)
        self.periodic_controls=Gtk.FlowBox();self.periodic_controls.set_selection_mode(Gtk.SelectionMode.NONE)
        self.periodic_controls.set_min_children_per_line(1);self.periodic_controls.set_max_children_per_line(4)
        self.periodic_controls.set_column_spacing(3);self.periodic_controls.set_row_spacing(3)
        self.cell_visible=Gtk.CheckButton(label='Cell');self.cell_visible.set_active(True)
        add_flow(self.periodic_controls,self.cell_visible)
        self.repeat=[];self.repeat_updating=False
        for axis in ('X','Y','Z'):
            group=Gtk.Box(spacing=3);group.pack_start(Gtk.Label(label=axis),False,False,0)
            value=Gtk.SpinButton.new_with_range(1,5,1);value.set_value(1);value.set_width_chars(1)
            value.get_style_context().add_provider(compact_css,Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
            value.set_tooltip_text('Display repetitions along lattice '+axis+' (does not change the structure)')
            self.repeat.append(value);group.pack_start(value,False,False,0);add_flow(self.periodic_controls,group)
            value.connect('value-changed',self.repeat_changed)
        self.cell_visible.connect('toggled',lambda widget:self.view.set_cell_visible(widget.get_active()))
        tool_left=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=5)
        tool_left.pack_start(self.periodic_controls,False,False,0)
        tool_left.pack_start(playback,False,False,0)
        self.layout_grid.attach(cell(tool_left,'Cell and playback'),0,2,1,1)
        displacement=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=3);self.displacement=displacement
        scale_label=Gtk.Label(label='Scale × mode vector',xalign=0)
        displacement.pack_start(scale_label,False,False,0)
        self.scale=Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL,-1,1,.1)
        self.scale.set_digits(1);self.scale.set_round_digits(1);self.scale.set_value(0);self.scale.set_hexpand(True)
        for v in (-1,0,1):self.scale.add_mark(v,Gtk.PositionType.BOTTOM,None)
        displacement.pack_start(self.scale,False,False,0)
        scale_actions=Gtk.Box(spacing=5)
        reset=Gtk.Button(label='Zero');reset.connect('clicked',self.zero)
        self.save_button=Gtk.Button(label='Save new POSCAR')
        scale_actions.pack_start(reset,False,False,0);scale_actions.pack_start(self.save_button,False,False,0)
        displacement.pack_start(scale_actions,False,False,0)
        self.layout_grid.attach(cell(displacement,'Mode displacement'),1,2,1,1)
        box=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=5);self.thermo_box=box
        grid=Gtk.Grid(column_spacing=10,row_spacing=5)
        self.model=Gtk.ComboBoxText()
        for label in ('Harmonic','Ideal gas'):self.model.append_text(label)
        self.model.set_active(0)
        self.model.set_tooltip_text('Harmonic: surface / local vibrational modes. Ideal gas: isolated molecule.')
        self.state=Gtk.ComboBoxText()
        for label in ('Minimum','Transition state'):self.state.append_text(label)
        self.state.set_active(0)
        self.geometry=Gtk.ComboBoxText()
        for label in ('nonlinear','linear','monatomic'):self.geometry.append_text(label)
        self.geometry.set_active(0)
        self.fields={k:entry(v) for k,v in (('temperature','298.15'),('pressure','101325'),('symmetry','1'),('spin','0'),('energy',''))}
        self.energy_open=Gtk.Button(label='Open OUTCAR')
        self.energy_open.set_tooltip_text('Read the LAST ionic-step energy from a different OUTCAR; keep the frequency structure and modes.')
        self.fields['energy'].set_width_chars(6)
        energy_row=Gtk.Box(spacing=5);energy_row.pack_start(self.fields['energy'],True,True,0);energy_row.pack_start(self.energy_open,False,False,0)
        items=[('Model',self.model),('State',self.state),('T (K)',self.fields['temperature']),
               ('P (Pa)',self.fields['pressure']),('E (eV)',energy_row)]
        self.state.set_tooltip_text('Stationary-point label only; all imaginary modes are excluded.')
        self.fields['energy'].set_tooltip_text('First ionic-step OUTCAR energy is filled automatically when available; editable, empty for correction only.')
        for combo in (self.model,self.state):
            for renderer in combo.get_cells():
                renderer.set_property('ellipsize',3);renderer.set_property('width-chars',12);renderer.set_property('max-width-chars',16)
        for i,(label,widget) in enumerate(items):
            grid.attach(Gtk.Label(label=label,xalign=0),0,i,1,1);grid.attach(widget,1,i,1,1)
        box.pack_start(grid,False,False,0)
        policy=Gtk.Label(label='Real modes below 50 cm⁻¹ use 50 cm⁻¹; all imaginary modes are excluded.',xalign=0)
        policy.set_line_wrap(True);policy.set_max_width_chars(28);box.pack_start(policy,False,False,0)
        actions=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=5)
        self.calculate=Gtk.Button(label='Get Thermochemistry')
        self.save_thermo=Gtk.Button(label='Save result + Python script')
        for widget in (self.calculate,self.save_thermo):actions.pack_start(widget,False,False,0)
        box.pack_start(actions,False,False,0)
        self.result_panel=ThermoResult()
        self.result_panel.get_style_context().remove_class('thermo-card')
        self.result_panel.set_shadow_type(Gtk.ShadowType.NONE)
        self.result_panel.get_child().set_border_width(0)
        box.set_valign(Gtk.Align.FILL);self.result_panel.set_valign(Gtk.Align.FILL)
        self.thermo=cell(box,'Thermochemistry parameters')
        self.layout_grid.attach(self.thermo,0,4,1,1)
        self.layout_grid.attach(cell(self.result_panel),1,4,1,1)
        self.thermo_content=self.layout_grid
        self.row_separators=[]
        for row in (1,3):
            line=Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
            self.layout_grid.attach(line,0,row,2,1);self.row_separators.append(line)
        table=Gtk.Overlay();table.add(self.layout_grid)
        self.column_separator=Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
        self.column_separator.set_halign(Gtk.Align.CENTER);self.column_separator.set_valign(Gtk.Align.FILL)
        table.add_overlay(self.column_separator);table.set_overlay_pass_through(self.column_separator,True)
        frame=Gtk.Frame();frame.set_shadow_type(Gtk.ShadowType.IN);frame.add(table)
        self.pack_start(frame,True,True,0)
        self.status=Gtk.Label(label='Load a VASP frequency OUTCAR. Animation is schematic; Scale is dimensionless.',xalign=0)
        self.status.set_line_wrap(True);self.status.set_max_width_chars(90);self.status.set_selectable(True)
        self.pack_start(self.status,False,False,0)
        self.install_hint=InstallHint('ASE','install-ase.sh');self.install_hint.set_no_show_all(True)
        self.pack_start(self.install_hint,False,False,0)
        self.open_button.connect('clicked',self.open)
        self.cancel_button.connect('clicked',lambda *_:self.cancel())
        self.play.connect('toggled',self.play_toggled)
        self.scale.connect('value-changed',self.scale_changed)
        self.save_button.connect('clicked',self.save)
        self.energy_open.connect('clicked',self.open_energy)
        self.calculate.connect('clicked',self.compute)
        self.save_thermo.connect('clicked',self.export_thermo)
        for widget in (self.model,self.state,self.geometry,*self.fields.values()):widget.connect('changed',self.invalidate)
        self.model.connect('changed',self.model_changed)
        self.connect('unmap',lambda *_:self.pause())
        self.connect('destroy',self.destroyed)
        self.controls()

    def reveal_result(self):
        if not self.alive or self.thermo_result is None:return False
        parent=self.get_parent()
        while parent is not None and not isinstance(parent,Gtk.ScrolledWindow):parent=parent.get_parent()
        if parent is not None:
            adjustment=parent.get_vadjustment()
            location=self.result_panel.translate_coordinates(self,0,0)
            if location:
                bottom=location[1]+self.result_panel.get_allocated_height()
                adjustment.set_value(max(adjustment.get_value(),min(adjustment.get_upper()-adjustment.get_page_size(),bottom-adjustment.get_page_size())))
        return False

    def repeat_changed(self,*_):
        if self.repeat_updating or not self.data:return
        try:
            self.view.set_repeats(tuple(widget.get_value_as_int() for widget in self.repeat))
        except ValueError as error:
            self.status.set_text(str(error));self.repeat_updating=True
            for widget,value in zip(self.repeat,self.view.repeats):widget.set_value(value)
            self.repeat_updating=False

    def parent(self):
        window=self.get_toplevel();return window if isinstance(window,Gtk.Window) else None

    def controls(self):
        ready=self.data is not None and self.job is None
        imaginary=ready and self.data['modes'][self.mode]['imaginary']
        self.scale.set_sensitive(imaginary);self.play.set_sensitive(ready)
        self.save_button.set_sensitive(bool(imaginary))
        self.calculate.set_sensitive(ready)
        self.tree.set_sensitive(ready)
        self.periodic_controls.set_sensitive(ready)
        self.thermo_box.set_sensitive(ready)
        self.save_thermo.set_sensitive(self.thermo_result is not None and self.job is None)
        self.cancel_button.set_sensitive(self.job is not None)
        self.install_hint.set_visible(self.data is None)

    def pause(self):
        if self.timer:GLib.source_remove(self.timer);self.timer=None
        if self.play.get_active():self.play.set_active(False)

    def invalidate(self,*_):
        self.thermo_result=None;self.result_panel.clear();self.controls()

    def set_data(self,data):
        self.pause();self.data=data;self.mode=0;self.scale.set_value(0)
        self.source.set_text(data['path']);self.source.set_tooltip_text(data['path'])
        self.apply_energy(data.get('electronic_energy_source'))
        self.store.clear()
        for mode in data['modes']:
            self.store.append([not mode['imaginary'] and mode['cm1']>0,mode['index'],
                               ('%.4f'%mode['cm1'])+(' i' if mode['imaginary'] else ''),'Imaginary' if mode['imaginary'] else 'Real'])
        self.invalidate();self.view.set_data(data)
        self.repeat_updating=True
        for widget in self.repeat:widget.set_value(1)
        self.repeat_updating=False
        self.tree.get_selection().select_path(0)
        self.status.set_text('%d modes | %s. %s'%(len(data['modes']),data['vector_convention'],' '.join(data['warnings'])))
        self.controls()

    def apply_energy(self,record):
        self.energy_source=record
        self.fields['energy'].set_text('' if record is None else repr(float(record['value_eV'])))
        if record is None:
            tip='No first-step OUTCAR energy found. Enter manually or choose another OUTCAR.'
        else:
            step='ionic step 1' if record['ionic_step']==1 else 'last ionic step'
            tip='Read from %s: %s (%s).\n%s\nEditable.'%(step,record['quantity'],record['reader'],record['path'])
        self.fields['energy'].set_tooltip_text(tip)

    def open_energy(self,*_):
        if self.data is None or self.job:return
        directory=Path(self.energy_source['path']).parent if self.energy_source else Path(self.data['path']).parent
        self.energy_dialog=CompactFileDialog(self.parent(),directory,'Open energy OUTCAR (last ionic step)')
        path=self.energy_dialog.run()
        if path:self.start({'action':'energy','path':path,'step':'last'},'energy')

    def start(self,request,kind):
        self.cancel();self.request_id+=1;token=self.request_id
        def callback(result,error):GLib.idle_add(self.finished,token,kind,result,error)
        self.job=task(request,callback);self.status.set_text({'read':'Reading modes…','energy':'Reading last ionic-step energy…','thermo':'Calculating thermochemistry…'}[kind])
        if kind=='thermo':self.result_panel.clear('Calculating…')
        self.controls();self.job.start()

    def finished(self,token,kind,result,error):
        if not self.alive or token!=self.request_id:return False
        self.job=None
        if error:
            self.status.set_text(error)
            if kind=='thermo':self.result_panel.clear(error)
        elif kind=='read':self.set_data(result)
        elif kind=='energy':
            self.apply_energy(result)
            self.status.set_text('E updated from the selected OUTCAR, last ionic step. Frequency data unchanged.')
        else:
            self.thermo_result=result;self.result_panel.show_result(result)
            self.status.set_text('Correction calculated. Save the result and standalone Python script.')
            GLib.timeout_add(80,self.reveal_result)
        self.controls();return False

    def cancel(self):
        if self.job:self.job.cancel();self.job=None;self.request_id+=1;self.status.set_text('Calculation cancelled.')
        self.controls()

    def load_path(self,path):
        self.pause();self.pending_path=str(Path(path).resolve())
        self.start({'action':'read','path':self.pending_path},'read')

    def open(self,*_):
        directory=Path(self.data['path']).parent if self.data else Path.cwd()
        self.file_dialog=CompactFileDialog(self.parent(),directory,'Open frequency OUTCAR')
        path=self.file_dialog.run()
        if path:self.load_path(path)

    def select_mode(self,selection):
        model,iterator=selection.get_selected()
        if iterator is None or self.data is None:return
        self.pause();self.mode=model.get_path(iterator).get_indices()[0];self.scale.set_value(0)
        mode=self.data['modes'][self.mode]
        self.mode_info.set_text('Mode %d | %.4f%s cm⁻¹'%(mode['index'],mode['cm1'],' i' if mode['imaginary'] else ''))
        self.mode_info.set_tooltip_text('Maximum source-vector displacement: %.6g'%mode['max_displacement'])
        self.static_preview();self.controls()
        # A frequency click starts its mode; slider movement switches to static preview.
        self.play.set_active(True)

    def play_toggled(self,*_):
        if self.play.get_active() and self.data:
            self.started=time.monotonic()
            if not self.timer:self.timer=GLib.timeout_add(33,self.tick)
        else:
            if self.timer:GLib.source_remove(self.timer);self.timer=None
            self.static_preview()

    def tick(self):
        if not self.alive or self.data is None:return False
        factor=self.amplitude.get_value()*math.sin(2*math.pi*(time.monotonic()-self.started)/self.period.get_value())
        self.show_offset(factor);return True

    def show_offset(self,factor):
        mode=self.data['modes'][self.mode]
        self.view.set_positions([[p[j]+factor*v[j] for j in range(3)] for p,v in zip(self.data['positions'],mode['vectors'])])

    def static_preview(self):
        if self.data:self.show_offset(round(self.scale.get_value(),1) if self.data['modes'][self.mode]['imaginary'] else 0.)

    def scale_changed(self,*_):
        self.pause();self.static_preview()

    def zero(self,*_):
        self.pause();self.scale.set_value(0);self.static_preview()

    def destination(self,title,name):
        directory=Path(self.data['path']).parent if self.data else Path.cwd()
        self.file_dialog=CompactFileDialog(self.parent(),directory,title,save_name=name)
        return self.file_dialog.run()

    def export_poscar(self,path):
        if not self.data or not self.data['modes'][self.mode]['imaginary']:raise ValueError('Select an imaginary mode first.')
        self.pause();structure=displaced_structure(self.data,self.mode,round(self.scale.get_value(),1))
        with open(path,'x',encoding='utf-8') as output:structure.write(output)

    def save(self,*_):
        self.pause()
        path=self.destination('Save displaced POSCAR','POSCAR_mode%03d_s%+.1f'%(self.mode+1,round(self.scale.get_value(),1)))
        if path:
            try:self.export_poscar(path);self.status.set_text('Saved '+path)
            except Exception as error:self.status.set_text(str(error))

    def model_changed(self,*_):
        if self.model.get_active()==1 and self.data is not None and self.job is None:
            self.gas_parameters()

    def gas_parameters(self):
        if not self.data or self.job:return
        self.pause();self.invalidate()
        self.gas_dialog=GasThermoDialog(self)
        answer=self.gas_dialog.run()
        if not self.alive:return
        if answer is None:
            self.status.set_text('Gas calculation cancelled; no calculation started.');return
        geometry,spin,symmetry,chosen,temperature,pressure=answer
        self.geometry.set_active(geometry);self.fields['spin'].set_text(spin);self.fields['symmetry'].set_text(symmetry)
        self.fields['temperature'].set_text(temperature);self.fields['pressure'].set_text(pressure)
        for i,row in enumerate(self.store):row[0]=i in chosen
        self.run_thermo()

    def compute(self,*_):
        if not self.data:return
        if self.model.get_active()==1:self.gas_parameters()
        else:self.run_thermo()

    def run_thermo(self):
        self.invalidate();self.pause()
        request={'action':'thermo','data':self.data,'selected':([i for i,row in enumerate(self.store) if row[0]] if self.model.get_active()==1 else
                             [i for i,mode in enumerate(self.data['modes']) if not mode['imaginary'] and mode['cm1']>0]),
                 'model':'gas' if self.model.get_active()==1 else 'harmonic',
                 'state':'ts' if self.state.get_active()==1 else 'minimum','geometry':self.geometry.get_active_text(),
                 'confirm_exclusions':self.model.get_active()==1}
        request.update({key:widget.get_text().strip() for key,widget in self.fields.items()})
        text=request['energy']
        provenance=None
        if text:
            provenance={'reader':'manual'}
            try:
                if self.energy_source and float(text)==self.energy_source['value_eV']:provenance=self.energy_source
            except ValueError:pass
        request['energy_source']=provenance
        self.start(request,'thermo')

    def export_thermo(self,*_):
        if not self.thermo_result:return
        path=self.destination('Save result and matching Python script','thermochemistry.json')
        if path:
            try:
                report,script=save_thermochemistry(path,self.data,self.thermo_result)
                self.status.set_text('Saved %s and %s. Re-run: python %s (requires ASE and NumPy).'%(report,script,script.name))
            except Exception as error:self.status.set_text(str(error))

    def destroyed(self,*_):
        self.alive=False;self.pause();self.cancel()
        dialog=getattr(self,'gas_dialog',None)
        if dialog and dialog.dialog.get_visible():dialog.dialog.response(Gtk.ResponseType.CANCEL)

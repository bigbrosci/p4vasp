"""Frequency selection, display-only animation, signed displacement and ASE UI."""
import json
import math
from pathlib import Path
import time
from p4vasp.gtk3 import Gtk, GLib
from p4vasp.gtk3.mode_view import ModeView
from p4vasp.gtk3.install_hint import InstallHint
from p4vasp.gtk3.file_dialogs import CompactFileDialog
from p4vasp.vibrations import task, displaced_structure


def entry(value=''):
    widget=Gtk.Entry();widget.set_text(str(value));widget.set_width_chars(9);return widget


class VibrationsPage(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL,spacing=7)
        self.set_border_width(8)
        self.data=None;self.mode=0;self.job=None;self.timer=None;self.alive=True;self.thermo_result=None
        self.request_id=0;self.pending_path=None
        top=Gtk.Box(spacing=7)
        self.open_button=Gtk.Button(label='Open frequency OUTCAR')
        self.cancel_button=Gtk.Button(label='Cancel');self.cancel_button.set_sensitive(False)
        self.source=Gtk.Label(label='No frequency data loaded',xalign=0)
        self.source.set_ellipsize(3);self.source.set_hexpand(True)
        for widget in (self.open_button,self.cancel_button,self.source):top.pack_start(widget,widget is self.source,True,0)
        self.pack_start(top,False,False,0)
        split=Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        left=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=5)
        self.view=ModeView();left.pack_start(self.view,True,True,0)
        playback=Gtk.Box(spacing=6)
        self.play=Gtk.ToggleButton(label='Play / Pause')
        self.amplitude=Gtk.SpinButton.new_with_range(.1,10,.1);self.amplitude.set_value(1)
        self.period=Gtk.SpinButton.new_with_range(.2,10,.1);self.period.set_value(1.5)
        self.amplitude.set_width_chars(4);self.period.set_width_chars(4)
        for label,widget in (('',self.play),('Amp. ×',self.amplitude),('Period (s)',self.period)):
            if label:playback.pack_start(Gtk.Label(label=label),False,False,0)
            playback.pack_start(widget,False,False,0)
        left.pack_start(playback,False,False,0)
        self.mode_info=Gtk.Label(xalign=0);self.mode_info.set_line_wrap(True);self.mode_info.set_max_width_chars(55)
        left.pack_start(self.mode_info,False,False,0)
        split.pack1(left,resize=True,shrink=False)
        self.store=Gtk.ListStore(bool,int,str,str)
        self.tree=Gtk.TreeView(model=self.store)
        toggle=Gtk.CellRendererToggle();toggle.connect('toggled',self.toggle_mode)
        self.tree.append_column(Gtk.TreeViewColumn('Thermo',toggle,active=0))
        for label,column in (('Mode',1),('cm⁻¹',2),('Type',3)):
            self.tree.append_column(Gtk.TreeViewColumn(label,Gtk.CellRendererText(),text=column))
        self.tree.get_selection().connect('changed',self.select_mode)
        scroll=Gtk.ScrolledWindow();scroll.set_policy(Gtk.PolicyType.AUTOMATIC,Gtk.PolicyType.AUTOMATIC)
        scroll.set_size_request(210,230);scroll.add(self.tree);split.pack2(scroll,resize=False,shrink=False)
        split.set_position(430);self.pack_start(split,True,True,0)
        displacement=Gtk.Box(spacing=7)
        displacement.pack_start(Gtk.Label(label='Scale × mode vector'),False,False,0)
        self.scale=Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL,-1,1,.1)
        self.scale.set_digits(1);self.scale.set_round_digits(1);self.scale.set_value(0);self.scale.set_hexpand(True)
        for v in (-1,0,1):self.scale.add_mark(v,Gtk.PositionType.BOTTOM,None)
        displacement.pack_start(self.scale,True,True,0)
        reset=Gtk.Button(label='Zero');reset.connect('clicked',self.zero)
        self.save_button=Gtk.Button(label='Save new POSCAR')
        displacement.pack_start(reset,False,False,0);displacement.pack_start(self.save_button,False,False,0)
        self.pack_start(displacement,False,False,0)
        self.accept_flags=Gtk.CheckButton(label='Confirm export without selective-dynamics flags')
        self.accept_flags.set_tooltip_text('Required only when no matching POSCAR/CONTCAR can supply the original flags.')
        self.pack_start(self.accept_flags,False,False,0)
        thermo=Gtk.Expander(label='Thermochemistry — ASE');thermo.set_expanded(False)
        box=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=5);self.thermo_box=box
        grid=Gtk.Grid(column_spacing=10,row_spacing=5)
        self.model=Gtk.ComboBoxText()
        for label in ('Harmonic (adsorbate / local modes)','Ideal gas (molecule)'):self.model.append_text(label)
        self.model.set_active(0)
        self.state=Gtk.ComboBoxText()
        for label in ('Minimum','Transition state (one imaginary mode)'):self.state.append_text(label)
        self.state.set_active(0)
        self.geometry=Gtk.ComboBoxText()
        for label in ('nonlinear','linear','monatomic'):self.geometry.append_text(label)
        self.geometry.set_active(0)
        self.fields={k:entry(v) for k,v in (('temperature','298.15'),('pressure','101325'),('symmetry','1'),('spin','0'),('floor','0'),('imaginary_tolerance','0'),('energy',''))}
        items=[('Model',self.model),('Stationary point',self.state),('T (K)',self.fields['temperature']),
               ('P (Pa, gas only)',self.fields['pressure']),('Gas geometry',self.geometry),('Symmetry number (gas)',self.fields['symmetry']),
               ('Spin S (gas)',self.fields['spin']),('Low-frequency floor (cm⁻¹)',self.fields['floor']),
               ('Imaginary tolerance (cm⁻¹)',self.fields['imaginary_tolerance']),('Electronic energy (eV, optional)',self.fields['energy'])]
        self.fields['imaginary_tolerance'].set_tooltip_text('Default 0: no imaginary modes ignored. Raise only for identified numerical/translation artifacts; exclusions still require confirmation.')
        for i,(label,widget) in enumerate(items):
            grid.attach(Gtk.Label(label=label,xalign=0),0,i,1,1);grid.attach(widget,1,i,1,1)
        box.pack_start(grid,False,False,0)
        self.confirm=Gtk.CheckButton(label='I confirm the selected / excluded modes shown in the frequency table')
        box.pack_start(self.confirm,False,False,0)
        actions=Gtk.Box(spacing=7)
        self.gas_select=Gtk.Button(label='Select highest gas vibrational modes')
        self.calculate=Gtk.Button(label='Calculate correction')
        self.save_thermo=Gtk.Button(label='Save thermochemistry')
        for widget in (self.gas_select,self.calculate,self.save_thermo):actions.pack_start(widget,False,False,0)
        box.pack_start(actions,False,False,0)
        self.result=Gtk.Label(xalign=0);self.result.set_selectable(True);self.result.set_line_wrap(True);self.result.set_max_width_chars(90)
        box.pack_start(self.result,False,False,0);thermo.add(box);self.pack_start(thermo,False,False,0)
        self.status=Gtk.Label(label='Load a VASP frequency OUTCAR. Animation is schematic; Scale is dimensionless.',xalign=0)
        self.status.set_line_wrap(True);self.status.set_max_width_chars(90);self.status.set_selectable(True)
        self.pack_start(self.status,False,False,0)
        self.pack_start(InstallHint('ASE','install-ase.sh'),False,False,0)
        self.open_button.connect('clicked',self.open)
        self.cancel_button.connect('clicked',lambda *_:self.cancel())
        self.play.connect('toggled',self.play_toggled)
        self.scale.connect('value-changed',self.scale_changed)
        self.save_button.connect('clicked',self.save)
        self.gas_select.connect('clicked',self.select_gas)
        self.calculate.connect('clicked',self.compute)
        self.save_thermo.connect('clicked',self.export_thermo)
        for widget in (self.model,self.state,self.geometry,*self.fields.values()):widget.connect('changed',self.invalidate)
        self.confirm.connect('toggled',self.invalidate)
        self.accept_flags.connect('toggled',lambda *_:self.controls())
        self.connect('unmap',lambda *_:self.pause())
        self.connect('destroy',self.destroyed)
        self.controls()

    def parent(self):
        window=self.get_toplevel();return window if isinstance(window,Gtk.Window) else None

    def controls(self):
        ready=self.data is not None and self.job is None
        imaginary=ready and self.data['modes'][self.mode]['imaginary']
        self.scale.set_sensitive(imaginary);self.play.set_sensitive(ready)
        self.save_button.set_sensitive(bool(imaginary and (self.data['constraints_source'] or self.accept_flags.get_active())))
        self.calculate.set_sensitive(ready);self.gas_select.set_sensitive(ready)
        self.tree.set_sensitive(ready)
        self.thermo_box.set_sensitive(ready)
        self.accept_flags.set_sensitive(bool(ready and not self.data['constraints_source']))
        self.save_thermo.set_sensitive(self.thermo_result is not None and self.job is None)
        self.cancel_button.set_sensitive(self.job is not None)

    def pause(self):
        if self.timer:GLib.source_remove(self.timer);self.timer=None
        if self.play.get_active():self.play.set_active(False)

    def invalidate(self,*_):
        self.thermo_result=None;self.result.set_text('');self.controls()

    def set_data(self,data):
        self.pause();self.data=data;self.mode=0;self.accept_flags.set_active(False);self.scale.set_value(0)
        self.source.set_text(data['path']);self.source.set_tooltip_text(data['path'])
        self.store.clear()
        for mode in data['modes']:
            self.store.append([not mode['imaginary'] and mode['cm1']>0,mode['index'],
                               ('%.4f'%mode['cm1'])+(' i' if mode['imaginary'] else ''),'Imaginary' if mode['imaginary'] else 'Real'])
        self.confirm.set_active(False);self.invalidate();self.view.set_data(data)
        self.tree.get_selection().select_path(0)
        self.status.set_text('%d modes | %s. %s'%(len(data['modes']),data['vector_convention'],' '.join(data['warnings'])))
        self.controls()

    def start(self,request,kind):
        self.cancel();self.request_id+=1;token=self.request_id
        def callback(result,error):GLib.idle_add(self.finished,token,kind,result,error)
        self.job=task(request,callback);self.status.set_text('Reading modes…' if kind=='read' else 'Calculating thermochemistry…')
        self.controls();self.job.start()

    def finished(self,token,kind,result,error):
        if not self.alive or token!=self.request_id:return False
        self.job=None
        if error:self.status.set_text(error)
        elif kind=='read':self.set_data(result)
        else:
            self.thermo_result=result
            lines=['ASE %s | %s correction = %.8f eV'%(result['ase_version'],result['kind'],result['correction_eV']),
                   'ZPE = %.8f eV | S = %.10f eV/K | T S = %.8f eV'%(result['ZPE_eV'],result['S_eV_per_K'],result['TS_eV']),
                   'U = %.8f eV'%result['U_eV']]
            if result['H_eV'] is not None:lines.append('H = %.8f eV'%result['H_eV'])
            if result['electronic_energy_eV'] is not None:lines.append('%s = %.8f eV'%(result['kind'],result['free_energy_eV']))
            lines.append('Selected modes: %s | Excluded: %s'%(result['selected_modes'],result['excluded_modes']))
            self.result.set_text('\n'.join(lines));self.status.set_text('Correction calculated. Settings and effective frequencies are included when saving.')
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
        self.mode_info.set_text('Mode %d | %.4f%s cm⁻¹ | max |Δr| = %.6g (source-vector magnitude)'%
                                (mode['index'],mode['cm1'],' i' if mode['imaginary'] else '',mode['max_displacement']))
        self.static_preview();self.controls()
        # A frequency click starts its mode; slider movement switches to static preview.
        self.play.set_active(True)

    def toggle_mode(self,renderer,path):
        index=int(path);mode=self.data['modes'][index]
        if mode['imaginary'] or mode['cm1']<=0:return
        self.store[path][0]=not self.store[path][0]
        self.confirm.set_active(False);self.invalidate()

    def select_gas(self,*_):
        if not self.data:return
        n=len(self.data['symbols']);geometry=self.geometry.get_active_text()
        count={'nonlinear':max(0,3*n-6),'linear':max(0,3*n-5),'monatomic':0}[geometry]-(self.state.get_active()==1)
        candidates=sorted((i for i,m in enumerate(self.data['modes']) if not m['imaginary'] and m['cm1']>0),
                          key=lambda i:self.data['modes'][i]['cm1'],reverse=True)
        if count<0 or len(candidates)<count:self.status.set_text('Insufficient real modes for the chosen gas geometry.');return
        chosen=set(candidates[:count])
        for i,row in enumerate(self.store):row[0]=i in chosen
        self.confirm.set_active(False);self.invalidate()
        self.status.set_text('Selected %d highest real modes. Inspect the table and confirm exclusions before calculating.'%count)

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
        if not self.data['constraints_source'] and not self.accept_flags.get_active():raise ValueError('Confirm export without selective-dynamics flags.')
        self.pause();structure=displaced_structure(self.data,self.mode,round(self.scale.get_value(),1))
        with open(path,'x',encoding='utf-8') as output:structure.write(output)

    def save(self,*_):
        self.pause()
        path=self.destination('Save displaced POSCAR','POSCAR_mode%03d_s%+.1f'%(self.mode+1,round(self.scale.get_value(),1)))
        if path:
            try:self.export_poscar(path);self.status.set_text('Saved '+path)
            except Exception as error:self.status.set_text(str(error))

    def compute(self,*_):
        if not self.data:return
        self.invalidate();self.pause()
        request={'action':'thermo','data':self.data,'selected':[i for i,row in enumerate(self.store) if row[0]],
                 'model':'gas' if self.model.get_active()==1 else 'harmonic',
                 'state':'ts' if self.state.get_active()==1 else 'minimum','geometry':self.geometry.get_active_text(),
                 'confirm_exclusions':self.confirm.get_active()}
        request.update({key:widget.get_text().strip() for key,widget in self.fields.items()})
        self.start(request,'thermo')

    def export_thermo(self,*_):
        if not self.thermo_result:return
        path=self.destination('Save thermochemistry report','thermochemistry.json')
        if path:
            try:
                result=dict(self.thermo_result,source=self.data['path'])
                with open(path,'x',encoding='utf-8') as output:json.dump(result,output,indent=2)
                self.status.set_text('Saved '+path)
            except Exception as error:self.status.set_text(str(error))

    def destroyed(self,*_):
        self.alive=False;self.pause();self.cancel()

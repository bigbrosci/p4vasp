"""Readable thermochemistry result card, independent of calculation inputs."""
from p4vasp.gtk3 import Gtk
from gi.repository import Pango


class ThermoResult(Gtk.Frame):
    def __init__(self):
        super().__init__()
        self.get_style_context().add_class('thermo-card')
        css=Gtk.CssProvider();css.load_from_data(b'.thermo-card {background-color: #f5f7fb; border: 1px solid #dce2eb; border-radius: 6px;}')
        self.get_style_context().add_provider(css,Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        box=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=10);box.set_border_width(12);self.add(box)
        title=Gtk.Label(xalign=0);title.set_markup('<b>Thermochemistry results</b>');box.pack_start(title,False,False,0)
        self.stack=Gtk.Stack();box.pack_start(self.stack,True,True,0)
        self.empty=Gtk.Label(label='Choose a model and calculate.',xalign=0,yalign=0)
        self.empty.set_line_wrap(True);self.empty.set_max_width_chars(28);self.stack.add_named(self.empty,'empty')
        content=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=10);self.stack.add_named(content,'result')
        self.summary=Gtk.Label(xalign=0);self.summary.set_selectable(True);self.summary.set_line_wrap(True)
        content.pack_start(self.summary,False,False,0)
        self.conditions=Gtk.Label(xalign=0);self.conditions.set_line_wrap(True);self.conditions.set_max_width_chars(30)
        content.pack_start(self.conditions,False,False,0)
        table=Gtk.Grid(column_spacing=12,row_spacing=7);content.pack_start(table,False,False,0)
        self.values={};self.names={}
        for i,(key,label,unit) in enumerate((('ZPE_eV','ZPE','eV'),('U_eV','U','eV'),('H_eV','H','eV'),
                                           ('S_eV_per_K','S','eV/K'),('TS_eV','T × S','eV'),('electronic_energy_eV','E electronic','eV'),
                                           ('free_energy_eV','Total F / G','eV'))):
            name=Gtk.Label(label=label,xalign=0);self.names[key]=name;table.attach(name,0,i,1,1)
            value=Gtk.Label(xalign=1);value.set_selectable(True);self.values[key]=value;table.attach(value,1,i,1,1)
            units=Gtk.Label(xalign=0);units.set_markup('<span foreground="#657385">'+unit+'</span>');table.attach(units,2,i,1,1)
        self.details=Gtk.Label(xalign=0);self.details.set_line_wrap(True);self.details.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
        self.details.set_max_width_chars(30);self.details.set_selectable(True);content.pack_start(self.details,False,False,0)
        self.clear()

    def clear(self,message='Choose a model and calculate.'):
        self.summary.set_text('');self.empty.set_text(message);self.stack.set_visible_child_name('empty')

    def show_result(self,result):
        self.summary.set_markup('<span size="large" foreground="#234b75"><b>Δ%s = %.6f eV</b></span>'%(result['kind'],result['correction_eV']))
        settings=result['request_settings']
        conditions='T = %g K'%result['temperature_K']
        if result['pressure_Pa'] is not None:
            conditions+='  |  P = %g Pa'%result['pressure_Pa']
            conditions+='\n%s  |  Spin S = %s  |  σ = %s'%(settings['geometry'],settings['spin'],settings['symmetry'])
        self.conditions.set_text(conditions)
        self.names['free_energy_eV'].set_text('Total '+result['kind'])
        for key,label in self.values.items():
            value=result[key]
            text='—' if value is None or key=='free_energy_eV' and result['electronic_energy_eV'] is None else (('%.8f' if key=='S_eV_per_K' else '%.6f')%value)
            label.set_markup('<span font_family="monospace">'+text+'</span>')
        details='ASE %s\nReal-frequency minimum: 50 cm⁻¹\nIncluded modes: %s\nExcluded imaginary modes: %s'%(result['ase_version'],result['selected_modes'],result['excluded_imaginary_modes'])
        if result['electronic_energy_eV'] is None:details+='\nElectronic energy not provided; correction only.'
        if result.get('warnings'):details+='\n'+'\n'.join(result['warnings'])
        self.details.set_text(details);self.stack.set_visible_child_name('result')

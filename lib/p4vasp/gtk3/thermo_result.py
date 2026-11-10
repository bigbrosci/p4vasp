"""Thermochemistry results with equations and per-particle/molar units."""
from p4vasp.gtk3 import Gtk, GLib

# Exact SI elementary charge and Avogadro constant; eV/particle -> kJ/mol.
EV_TO_KJ_MOL = 1.602176634e-19 * 6.02214076e23 / 1000


class ThermoResult(Gtk.Frame):
    def __init__(self):
        super().__init__()
        self.get_style_context().add_class('thermo-card')
        css=Gtk.CssProvider();css.load_from_data(b'.thermo-card {background-color: #f5f7fb; border: 1px solid #dce2eb; border-radius: 6px;}')
        self.get_style_context().add_provider(css,Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        box=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=8);box.set_border_width(10);self.add(box)
        self.title=Gtk.Label(xalign=0);self.title.set_line_wrap(True);self.title.set_max_width_chars(32)
        self.title.set_markup('<b>Thermochemistry Results</b>');box.pack_start(self.title,False,False,0)
        self.stack=Gtk.Stack();box.pack_start(self.stack,True,True,0)
        self.empty=Gtk.Label(label='Choose a model and calculate.',xalign=0,yalign=0)
        self.empty.set_line_wrap(True);self.empty.set_max_width_chars(28);self.stack.add_named(self.empty,'empty')
        content=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=8);self.stack.add_named(content,'result')
        self.conditions=Gtk.Label(xalign=0);self.conditions.set_line_wrap(True);self.conditions.set_max_width_chars(30)
        content.pack_start(self.conditions,False,False,0)
        self.store=Gtk.ListStore(str,str,str,str,str,str,int);self.row_index={}
        self.table=Gtk.TreeView(model=self.store);self.table.set_enable_search(False)
        self.table.set_grid_lines(Gtk.TreeViewGridLines.BOTH);self.table.set_tooltip_column(4)
        for index,(title,width) in enumerate((('Energy item',80),('Equation',110),('Value in eV',100),('Value in kJ/mol',115))):
            renderer=Gtk.CellRendererText();renderer.set_property('xalign',1. if index>=2 else 0.);renderer.set_property('size-points',9.)
            if index>=2:renderer.set_property('family','monospace')
            column=Gtk.TreeViewColumn(title,renderer,text=index,foreground=5,weight=6)
            column.set_sizing(Gtk.TreeViewColumnSizing.FIXED);column.set_fixed_width(width);column.set_resizable(True)
            column.set_expand(True)  # Share spare width instead of stretching only the final column.
            header=Gtk.Label(label=title.replace('Energy item','Energy\nitem').replace('Value in ','Value in\n'))
            header.set_justify(Gtk.Justification.CENTER);column.set_widget(header);header.show()
            self.table.append_column(column)
        scroll=Gtk.ScrolledWindow();scroll.set_policy(Gtk.PolicyType.AUTOMATIC,Gtk.PolicyType.AUTOMATIC)
        scroll.set_min_content_height(205);scroll.add(self.table);self.table_scroll=scroll
        content.pack_start(scroll,True,True,0)
        self.clear()

    def clear(self,message='Choose a model and calculate.'):
        self.title.set_markup('<b>Thermochemistry Results</b>')
        self.store.clear();self.row_index.clear();self.empty.set_text(message);self.stack.set_visible_child_name('empty')

    def cell(self,key,column):
        return self.store[self.row_index[key]][column]

    def show_result(self,result):
        self.title.set_markup('<b>Thermochemistry Results (ASE %s)</b>'%GLib.markup_escape_text(result['ase_version']))
        settings=result['request_settings'];gas=settings['model']=='gas';kind=result['kind']
        conditions='T = %g K'%result['temperature_K']
        if result['pressure_Pa'] is not None:
            conditions+='  |  P = %g Pa'%result['pressure_Pa']
            conditions+='\n%s  |  Spin S = %s  |  σ = %s'%(settings['geometry'],settings['spin'],settings['symmetry'])
        self.conditions.set_text(conditions)
        base='H' if gas else 'U'
        rows=(('electronic_energy_eV','E electronic','E_DFT'),
              ('ZPE_eV','ZPE','½ Σ hν'),
              ('U_eV','U','E + ZPE + U_th' if gas else 'E + ZPE + U_v'),
              ('H_eV','H','U + k_B T' if gas else '—'),
              ('S_eV_per_K','S (per K)','Σ S_i' if gas else 'S_v'),
              ('TS_eV','T × S','T × S'),
              ('correction_eV','Δ'+kind,base+' − E − TS'),
              ('free_energy_eV','Total '+kind,base+' − TS'))
        self.store.clear();self.row_index.clear()
        for index,(key,label,equation) in enumerate(rows):
            value=result[key]
            if key=='free_energy_eV' and result['electronic_energy_eV'] is None:value=None
            entropy=key=='S_eV_per_K'
            def formatted(number):
                return ('%.8f /K' if entropy else '%.6f')%number
            ev='—' if value is None else formatted(value)
            molar='—' if value is None else formatted(value*EV_TO_KJ_MOL)
            tip='E = electronic energy; U_v = thermal vibration energy; U_th includes vibration, translation and rotation. S_t/S_r/S_v/S_e = translation/rotation/vibration/electronic entropy.'
            if entropy:tip+=' This row uses eV/K and kJ/(mol K).'
            correction=key=='correction_eV'
            self.store.append([label,equation,ev,molar,tip,'#234b75' if correction else '#243040',700 if correction else 400])
            self.row_index[key]=index
        self.stack.set_visible_child_name('result')

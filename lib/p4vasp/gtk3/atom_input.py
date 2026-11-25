"""Neutral-atom reference and explicit single-atom VASP calculation settings."""
import html
import re
from p4vasp.gtk3 import Gtk
from gi.repository import Pango
from p4vasp.gtk3.file_dialogs import entry, fit_dialog, error_label
from p4vasp.atomic_reference import reference, crystal_reference
from p4vasp.element_data import ElementData, NUMBERS
from p4vasp.resource_data import ResourceStore
from p4vasp.incar_generator import load_presets
from p4vasp.single_atom_inputs import input_contents, settings_values, write_contents


class AtomInputDialog(Gtk.Dialog):
    def __init__(self,page):
        parent=page.get_toplevel();parent=parent if isinstance(parent,Gtk.Window) else None
        self.page=page;self.symbol=page.symbol;self.config=load_presets();self.reference=reference(self.symbol)
        super().__init__(title='Single atom — '+self.symbol,transient_for=parent,modal=True,destroy_with_parent=True,use_header_bar=False)
        self.add_button('Cancel',Gtk.ResponseType.CANCEL)
        self.generate=self.add_button('Generate inputs',Gtk.ResponseType.APPLY)
        self.set_default_response(Gtk.ResponseType.APPLY);fit_dialog(self,parent,560,650)
        notebook=Gtk.Notebook();self.get_content_area().pack_start(notebook,True,True,0)
        scroll=Gtk.ScrolledWindow();scroll.set_policy(Gtk.PolicyType.NEVER,Gtk.PolicyType.AUTOMATIC)
        box=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=8);box.set_border_width(12);scroll.add(box)
        notebook.append_page(scroll,Gtk.Label(label='Atom & settings'))
        info=Gtk.Grid(column_spacing=12,row_spacing=5)
        element_row=ElementData(ResourceStore()).rows[NUMBERS[self.symbol]-1]
        mass=element_row[2]
        ref=self.reference;mult=ref.get('multiplicity');spin=ref.get('spin')
        crystal=crystal_reference(self.symbol)
        self.reference_labels={}
        for row,(label,value) in enumerate((('Element',ref.get('name',self.symbol)),('Symbol / atomic number',self.symbol+' / '+str(NUMBERS[self.symbol])),
                ('Mass (u)',mass or 'Unknown'),('Neutral ground configuration',ref.get('configuration','Unknown')),
                ('Ground level',ref.get('term','Unknown')),('S from LS label','Unknown' if spin is None else '%g'%spin),
                ('Multiplicity (2S + 1)','Unknown' if mult is None else str(mult)),
                ('Phase (~298 K, ~1 bar)',crystal.get('ambient_phase','Unknown')),
                ('Solid structure',crystal.get('structure','Unknown')),
                ('Structure conditions',crystal.get('conditions','Not verified')))):
            info.attach(Gtk.Label(label=label,xalign=0),0,row,1,1)
            text=value
            value=Gtk.Label(label=text,xalign=0);value.set_selectable(True);value.set_line_wrap(True)
            if label=='Neutral ground configuration':
                value.set_markup(re.sub(r'\^(\d+)',r'<sup>\1</sup>',html.escape(text)))
            elif label=='Ground level':
                term=re.fullmatch(r'(\d+)([A-Z]°?)_(.+)',text)
                if term:value.set_markup('<sup>'+term[1]+'</sup>'+term[2]+'<sub>'+html.escape(term[3])+'</sub>')
            value.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR);value.set_width_chars(1);value.set_hexpand(True)
            info.attach(value,1,row,1,1);self.reference_labels[label]=value
        box.pack_start(info,False,False,0)
        link=Gtk.LinkButton.new_with_label(ref.get('source',{}).get('url','https://physics.nist.gov/asd'),'NIST ASD neutral-atom reference')
        link.set_halign(Gtk.Align.START);box.pack_start(link,False,False,0)
        note=Gtk.Label(label='Neutral free-atom reference, not imposed orbital occupations. Charged and DFT states may differ; LS labels can be approximate.',xalign=0)
        note.set_line_wrap(True);note.set_max_width_chars(60);box.pack_start(note,False,False,0)
        self.crystal_link=Gtk.LinkButton.new_with_label(crystal.get('url','https://aflow.org/p/struk_A.html'),'Crystal structure reference')
        self.crystal_link.set_halign(Gtk.Align.START);box.pack_start(self.crystal_link,False,False,0)
        crystal_note=Gtk.Label(label=crystal.get('note','') or 'Solid-phase reference only; isolated-atom inputs remain unchanged.',xalign=0)
        crystal_note.set_line_wrap(True);crystal_note.set_max_width_chars(60);box.pack_start(crystal_note,False,False,0)
        box.pack_start(Gtk.Separator(),False,False,0)
        saved=page.input_settings.get(self.symbol,{})
        grid=Gtk.Grid(column_spacing=10,row_spacing=5);box.pack_start(grid,False,False,0)
        def row(index,label,widget):
            grid.attach(Gtk.Label(label=label,xalign=0),0,index,1,1);grid.attach(widget,1,index,1,1)
        self.charge=entry(saved.get('charge',0));row(0,'Charge',self.charge)
        self.ispin=Gtk.ComboBoxText()
        for text in ('1 — non-spin-polarized','2 — spin-polarized'):self.ispin.append_text(text)
        self.ispin.set_active(int(saved.get('ispin',2))-1);row(1,'ISPIN',self.ispin)
        self.magmom=entry(saved.get('magmom') if saved.get('magmom') is not None else '')
        self.magmom.set_placeholder_text('Optional initial moment')
        magbox=Gtk.Box(spacing=5);magbox.pack_start(self.magmom,True,True,0)
        self.use_reference=Gtk.Button(label='Use atomic 2S');self.use_reference.connect('clicked',self.apply_reference)
        magbox.pack_start(self.use_reference,False,False,0);row(2,'MAGMOM (μB)',magbox)
        atomic_moment='Unknown' if spin is None else '%g μB'%(2*spin)
        saved_moment=(element_row[7]+' μB') if element_row[7] else 'Not set'
        self.moment_source=Gtk.Label(label='Use atomic 2S: NIST neutral free-atom LS spin, 2S = '+atomic_moment+'.\np4vasp data Magmom: '+saved_moment+' (editable initial-moment preset; separate source).\nNeither value guarantees the converged DFT magnetic moment.',xalign=0)
        self.moment_source.set_line_wrap(True);self.moment_source.set_max_width_chars(60)
        grid.attach(self.moment_source,0,7,2,1)
        self.constrain=Gtk.CheckButton(label='Constrain spin (NUPDOWN)')
        self.constrain.set_active(saved.get('nupdown') is not None);grid.attach(self.constrain,0,3,2,1)
        self.nupdown=entry(saved.get('nupdown') if saved.get('nupdown') is not None else '')
        self.nupdown.set_placeholder_text('N↑ − N↓');row(4,'NUPDOWN',self.nupdown)
        self.constrain.set_tooltip_text('Fix the spin-electron difference. Blank MAGMOM uses NUPDOWN for this one atom. Supply ZVAL to check electron parity.')
        self.magmom.set_tooltip_text('Initial moment, not the final moment. Optional; no MAGMOM is written when unconstrained and blank.')
        self.zval=entry(saved.get('zval') if saved.get('zval') is not None else '')
        self.zval.set_placeholder_text('Optional, from your POTCAR');row(5,'POTCAR ZVAL',self.zval)
        cellbox=Gtk.Box(spacing=5);self.cell=[]
        for axis,value in zip(('x','y','z'),saved.get('cell',(13,14,15))):
            cellbox.pack_start(Gtk.Label(label=axis),False,False,0)
            field=entry(value);field.set_width_chars(4);cellbox.pack_start(field,True,True,0);self.cell.append(field)
        row(6,'Cell lengths (Å)',cellbox)
        self.preview=Gtk.TextView();self.preview.set_editable(False);self.preview.set_monospace(True)
        preview_scroll=Gtk.ScrolledWindow();preview_scroll.add(self.preview)
        notebook.append_page(preview_scroll,Gtk.Label(label='INCAR preview'))
        self.status=error_label();self.status.set_no_show_all(True);self.status.set_margin_start(12);self.status.set_margin_end(12)
        self.get_content_area().pack_start(self.status,False,False,6)
        self._updating=False
        for widget in (self.charge,self.ispin,self.magmom,self.nupdown,self.zval,*self.cell):widget.connect('changed',self.updated)
        self.constrain.connect('toggled',self.constrain_changed)
        self.connect('response',self.respond);self.updated()

    def suggestion(self):
        try:neutral=int(self.charge.get_text())==0
        except ValueError:neutral=False
        return self.reference.get('multiplicity',0)-1 if neutral and self.reference.get('multiplicity') and NUMBERS[self.symbol]<=86 else None

    def apply_reference(self,*_):
        value=self.suggestion()
        if value is not None:
            self.magmom.set_text(str(value))
            if self.constrain.get_active():self.nupdown.set_text(str(value))

    def constrain_changed(self,*_):
        value=self.suggestion()
        if self.constrain.get_active() and not self.nupdown.get_text().strip() and value is not None:self.nupdown.set_text(str(value))
        self.updated()

    def request(self):
        spin=self.ispin.get_active()+1
        target=self.nupdown.get_text() if spin==2 and self.constrain.get_active() else None
        if spin==2 and self.constrain.get_active() and not target.strip():raise ValueError('Enter NUPDOWN to constrain the spin.')
        return dict(charge=self.charge.get_text(),ispin=spin,magmom=self.magmom.get_text() if spin==2 else None,
                    nupdown=target,zval=self.zval.get_text(),cell=[field.get_text() for field in self.cell])

    def updated(self,*_):
        if self._updating:return
        self._updating=True
        try:
            spin=self.ispin.get_active()==1
            self.magmom.set_sensitive(spin);self.constrain.set_sensitive(spin)
            if not spin:self.constrain.set_active(False)
            self.nupdown.set_sensitive(spin and self.constrain.get_active())
            suggestion=self.suggestion()
            self.use_reference.set_sensitive(spin and suggestion is not None)
            self.use_reference.set_tooltip_text(('NIST neutral free-atom LS spin: 2S = %g μB. Independent of the p4vasp data Magmom preset; check POTCAR valence and the DFT state.'%suggestion) if suggestion is not None else 'Enter spin manually for charged, unknown or heavy-atom states.')
            files=input_contents(self.symbol,self.config,self.request())
            self.preview.get_buffer().set_text(files['INCAR']);self.generate.set_sensitive(True)
            self.status.set_text('Charged template: complete NELECT using POTCAR before running.' if 'SET_AFTER_POTCAR' in files['INCAR'] else '')
        except (ValueError,TypeError,OverflowError) as error:
            self.preview.get_buffer().set_text('');self.status.set_text(str(error));self.generate.set_sensitive(False)
        finally:
            self.status.set_visible(bool(self.status.get_text()))
            self._updating=False

    def respond(self,dialog,response):
        if response!=Gtk.ResponseType.APPLY:self.destroy();return
        try:
            request=self.request();files=input_contents(self.symbol,self.config,request)
        except (ValueError,TypeError,OverflowError) as error:self.status.set_text(str(error));self.status.show();return
        from p4vasp.gtk3.single_atom import InputFolderDialog
        pending='SET_AFTER_POTCAR' in files['INCAR']
        output=InputFolderDialog(self,self.symbol,self.page.directory,
            summary='Creates INCAR, Gamma 1×1×1 KPOINTS and a centered one-atom POSCAR.'+('\nCharged template: finish NELECT after choosing POTCAR.' if pending else ''),
            writer=lambda parent,name:write_contents(files,parent,name)).run()
        if output is not None:
            self.page.input_settings[self.symbol]=settings_values(self.symbol,request)
            self.page.directory=output.parent
            self.page.status.set_text('Created INCAR, KPOINTS and POSCAR in: '+str(output)+('\nComplete NELECT before running VASP.' if pending else ''))
            self.page.status.show();self.destroy()

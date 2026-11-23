"""Optional d-band controls; existing graph and local-DOS controls stay intact."""
from pathlib import Path
import re
from urllib.parse import unquote, urlparse
from p4vasp.gtk3 import Gtk, GLib, Gdk
from gi.repository import Pango
from p4vasp.gtk3.install_hint import InstallHint


class DosAnalysis(Gtk.Frame):
    _versions = {}

    def __init__(self, applet):
        super().__init__(label='d-band analysis (pymatgen)')
        self.applet=applet;self.job=None;self.result=None;self.alive=True;self.system=None;self.version_job=None
        self.connect('destroy',self.closed)
        box=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=5);box.set_border_width(6)
        bounds=Gtk.ScrolledWindow();bounds.set_policy(Gtk.PolicyType.AUTOMATIC,Gtk.PolicyType.AUTOMATIC)
        bounds.set_min_content_height(180);bounds.set_min_content_width(280)
        bounds.set_max_content_width(420);bounds.set_propagate_natural_width(True)
        bounds.add(box);self.add(bounds)
        grid=Gtk.Grid(column_spacing=6,row_spacing=5);box.pack_start(grid,False,False,0)
        self.mode=Gtk.ComboBoxText()
        for text in ('All atoms','Elements','Atom numbers'):self.mode.append_text(text)
        self.mode.set_active(0)
        self.selection=Gtk.Entry();self.selection.set_width_chars(12)
        self.selection.set_placeholder_text('Fe, Ni or 1-4, 8')
        self.selection.set_hexpand(True)
        grid.attach(self.mode,0,0,1,1);grid.attach(self.selection,1,0,1,1)
        selected=Gtk.Button(label='Use selected atoms');selected.connect('clicked',self.use_selection)
        line=Gtk.Button(label='Use last DOS line');line.connect('clicked',self.use_line)
        grid.attach(selected,0,1,1,1);grid.attach(line,1,1,1,1)
        from p4vasp.dos_selection import P_ORBITALS,D_ORBITALS,F_ORBITALS
        self.orbital_box=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=3)
        self.orbital_rows=[];self.orbital_buttons={};self._orbital_sync=False
        button_style=Gtk.CssProvider()
        button_style.load_from_data(b"button { min-width: 0; padding: 4px 5px; }")
        for names in (('s','p',*P_ORBITALS),('d',*D_ORBITALS),('f',*F_ORBITALS)):
            row=Gtk.Box(spacing=2,homogeneous=True);self.orbital_rows.append(row)
            self.orbital_box.pack_start(row,False,False,0)
            for name in names:
                label=name.replace('f_','f−')
                button=Gtk.ToggleButton(label=label)
                button.set_tooltip_text(name)
                button.get_style_context().add_provider(button_style,Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
                self.orbital_buttons[name]=button;row.pack_start(button,True,True,0)
        self.orbital_buttons['d'].set_active(True)
        self.spin_box=Gtk.Box(spacing=2,homogeneous=True)
        self.spin_buttons={};group=None
        for name,label in (('both','Both'),('up','Up'),('down','Down')):
            button=Gtk.RadioButton.new_with_label_from_widget(group,label)
            if group is None:group=button
            button.set_mode(False)
            button.get_style_context().add_provider(button_style,Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
            self.spin_buttons[name]=button;self.spin_box.pack_start(button,True,True,0)
        self.spin_buttons['both'].set_active(True)
        self.emin=Gtk.Entry();self.emax=Gtk.Entry()
        for entry in (self.emin,self.emax):
            entry.set_width_chars(4);entry.set_max_width_chars(4);entry.set_placeholder_text('Full')
            entry.set_tooltip_text('Relative to EF=0 eV. Blank uses the source grid limit.')
        for index,(label,widget) in enumerate((('Orbital',self.orbital_box),('Spin',self.spin_box))):
            row=Gtk.Box(spacing=6)
            row.pack_start(Gtk.Label(label=label,xalign=0),False,False,0)
            row.pack_start(widget,True,True,0);grid.attach(row,0,2+index,2,1)
        limits=Gtk.Box(spacing=5)
        limits.pack_start(Gtk.Label(label='Energy Range (eV)',xalign=0),False,False,0)
        for label,widget in (('Emin',self.emin),('Emax',self.emax)):
            limits.pack_start(Gtk.Label(label=label),False,False,0)
            limits.pack_start(widget,False,False,0)
        grid.attach(limits,0,4,2,1)
        actions=Gtk.Grid(column_spacing=6,row_spacing=5,column_homogeneous=True)
        self.calculate=Gtk.Button(label='Analyze DOS');self.calculate.connect('clicked',self.start)
        self.script=Gtk.Button(label='Export scripts');self.script.connect('clicked',self.export_script)
        self.copy=Gtk.Button(label='Copy results');self.copy.connect('clicked',self.copy_results)
        self.export=Gtk.Button(label='Export CSV');self.export.connect('clicked',self.export_results)
        for index,widget in enumerate((self.calculate,self.script,self.copy,self.export)):
            widget.set_hexpand(True);actions.attach(widget,index%2,index//2,1,1)
        box.pack_start(actions,False,False,0)
        self.status=Gtk.Label(xalign=0);self.status.set_line_wrap(True);self.status.set_max_width_chars(42);self.status.set_width_chars(1)
        self.status.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
        self.status.set_selectable(True);box.pack_start(self.status,False,False,0)
        self.model=Gtk.ListStore(str,str,str)
        view=Gtk.TreeView(model=self.model);view.set_grid_lines(Gtk.TreeViewGridLines.BOTH)
        view.get_selection().set_mode(Gtk.SelectionMode.NONE)
        for i,title in enumerate(('Property','Value','Unit')):
            renderer=Gtk.CellRendererText();renderer.set_property('editable',True)
            # Editable renderer permits copying an individual value; edits are discarded.
            renderer.connect('edited',lambda *_:None)
            if i==0:
                renderer.set_property('wrap-width',170)
                renderer.set_property('wrap-mode',Pango.WrapMode.WORD_CHAR)
            column=Gtk.TreeViewColumn(title,renderer,text=i);column.set_resizable(True);column.set_expand(i==0)
            view.append_column(column)
        scroll=Gtk.ScrolledWindow();scroll.set_policy(Gtk.PolicyType.AUTOMATIC,Gtk.PolicyType.AUTOMATIC)
        scroll.set_min_content_height(180)
        scroll.add(view);box.pack_start(scroll,True,True,0)
        self.hint=InstallHint('pymatgen','install-science.sh');self.hint.set_no_show_all(True)
        box.pack_start(self.hint,False,False,0)
        self.mode.connect('changed',self.changed)
        for name,button in self.orbital_buttons.items():button.connect('toggled',self.orbital_toggled,name)
        for button in self.spin_buttons.values():button.connect('toggled',self.spin_toggled)
        for widget in (self.selection,self.emin,self.emax):widget.connect('changed',self.changed)
        self.set_system(applet.system)
        self.load_version()

    def set_version(self,version):
        from p4vasp.dos_selection import band_label,parse_orbitals
        self.analysis_version=version
        label=band_label(parse_orbitals(self.orbital_name()))
        self.set_label(label+'-band analysis (pymatgen-'+str(version).replace('.','-')+')')

    def load_version(self):
        from p4vasp.ase_bulk import BulkTask
        from p4vasp.dos_analysis import worker_command
        try:key=tuple(worker_command())
        except Exception:return
        if key in self._versions:
            self.set_version(self._versions[key]);return
        task=BulkTask({'action':'version'},lambda result,error:GLib.idle_add(self.version_ready,task,key,result,error),
                      timeout=10,command_factory=worker_command,label='pymatgen version')
        self.version_job=task;task.start()

    def version_ready(self,task,key,result,error):
        if not self.alive or self.version_job is not task:return False
        self.version_job=None
        if result and not error:
            self._versions[key]=result['pymatgen_version'];self.set_version(result['pymatgen_version'])
        return False

    def parent(self):
        window=self.get_toplevel()
        return window if isinstance(window,Gtk.Window) else None

    def path(self):
        if self.system is None:raise ValueError('Open a DOSCAR or vasprun.xml first.')
        url=str(self.system.URL or '')
        if url.startswith('file:'):url=unquote(urlparse(url).path)
        elif '://' in url:raise ValueError('d-band analysis requires a local DOSCAR/vasprun.xml file.')
        path=Path(url)
        if path.is_file() and (path.name.upper()=='DOSCAR' or path.suffix.lower()=='.xml'):return path
        folder=path if path.is_dir() else path.parent
        for name in ('vasprun.xml','DOSCAR'):
            if (folder/name).is_file():return folder/name
        raise ValueError('No local DOSCAR/vasprun.xml for this system.')

    def set_system(self, system):
        self.cancel_job();self.system=system;self.result=None;self.model.clear()
        self.status.set_text('Select atoms/elements and an analysis range. Blank limits use the full DOS grid; plot zoom does not change analysis.')
        channels=None
        if system is not None and 'TOTAL_DOS' in system:
            prop=system['TOTAL_DOS']
            if prop.status==prop.READY and prop.value is not None:channels=len(prop.value)
        self.set_spin_channels(channels)
        self.hint.hide();self.status.set_tooltip_text(None);self.sensitivity()

    def orbital_name(self):
        return ','.join(name for name,button in self.orbital_buttons.items() if button.get_active())

    def set_orbitals(self,names):
        from p4vasp.dos_selection import parse_orbitals
        names=parse_orbitals(names)
        self._orbital_sync=True
        try:
            for name,button in self.orbital_buttons.items():button.set_active(name in names)
        finally:self._orbital_sync=False
        self.changed()

    def orbital_toggled(self,button,name):
        if self._orbital_sync:return
        self._orbital_sync=True
        try:
            if button.get_active():
                from p4vasp.dos_selection import SHELLS,orbital_shell
                shell=orbital_shell(name)
                if name==shell:
                    for other in SHELLS[shell]:self.orbital_buttons[other].set_active(False)
                else:self.orbital_buttons[shell].set_active(False)
            if not any(item.get_active() for item in self.orbital_buttons.values()):
                self.orbital_buttons['d'].set_active(True)
        finally:self._orbital_sync=False
        self.changed()

    def spin_name(self):
        return next(name for name,button in self.spin_buttons.items() if button.get_active())

    def set_spin(self,name):
        button=self.spin_buttons[name]
        if not button.get_sensitive():button=self.spin_buttons['both']
        button.set_active(True)

    def spin_toggled(self,button):
        if button.get_active():self.changed()

    def set_spin_channels(self,channels):
        polarized=channels==2
        for name in ('up','down'):
            button=self.spin_buttons[name];button.set_sensitive(polarized)
            button.set_tooltip_text(None if polarized else
                'No separate spin channel in this DOS.' if channels==1 else 'Separate spin channels are not available yet.')
        if not polarized:self.spin_buttons['both'].set_active(True)

    def sensitivity(self):
        busy=self.job is not None
        self.calculate.set_sensitive(not busy);self.script.set_sensitive(self.result is not None and not busy)
        self.copy.set_sensitive(self.result is not None and not busy)
        self.export.set_sensitive(self.result is not None and not busy)

    def changed(self,*_):
        if hasattr(self,'analysis_version'):self.set_version(self.analysis_version)
        self.cancel_job();self.result=None;self.model.clear();self.sensitivity()
        self.status.set_text('Parameters changed. Click Analyze DOS to calculate.')
        self.status.set_tooltip_text(None)
        self.applet.queue_plot_redraw()

    def use_selection(self,*_):
        from p4vasp.Selection import selection
        atoms=sorted(set(selection().getAtoms()))
        if not atoms:self.status.set_text('No atoms selected in the structure.');return
        self.mode.set_active(2);self.selection.set_text(', '.join(str(i+1) for i in atoms))

    def use_line(self,*_):
        if not self.applet.lines:self.status.set_text('No projected DOS lines. Use Local DOS+bands control to add one.');return
        line=self.applet.lines[-1]
        try:
            atoms=sorted(set(line.getSelection(self.system.INITIAL_STRUCTURE)))
            if not atoms:raise ValueError('The last DOS line selects no atoms.')
            self.mode.set_active(2);self.selection.set_text(', '.join(str(i+1) for i in atoms))
            self.set_spin({1:'up',2:'down'}.get(line.spin,'both'))
            from p4vasp.dos_selection import SHELLS,F_ORBITALS
            # Legacy plot f1..f7 denote ordered VASP columns, not magnetic m labels.
            mapped=[F_ORBITALS[int(name[1:])-1] if name.startswith('f') and name[1:].isdigit()
                    and 1<=int(name[1:])<=7 else name for name in line.orbital]
            selected=[]
            for shell,components in SHELLS.items():
                choices=[name for name in components if name in mapped]
                selected.extend([shell] if shell in mapped or (components and len(choices)==len(components)) else choices)
            self.set_orbitals(selected or ['d'])
        except Exception as error:self.status.set_text(str(error))

    def request(self):
        text=self.selection.get_text().strip();mode=self.mode.get_active()
        request=dict(path=str(self.path()),orbital=self.orbital_name(),spin=self.spin_name())
        if mode==1:
            request['elements']=list(dict.fromkeys(re.split(r'[\s,]+',text))) if text else []
            if not request['elements']:raise ValueError('Enter at least one element symbol.')
        if mode==2:
            atoms=[]
            for part in re.split(r'[\s,]+',text):
                match=re.fullmatch(r'(\d+)(?:-(\d+))?',part)
                if not match:raise ValueError('Use 1-based atom numbers, e.g. 1-4, 8.')
                first=int(match[1]);last=int(match[2] or first)
                if first<1 or last<first or last-first>100000:raise ValueError('Invalid atom range.')
                atoms.extend(range(first,last+1))
            request['atoms']=sorted(set(atoms))
        for key,entry in (('emin',self.emin),('emax',self.emax)):
            request[key]=float(entry.get_text()) if entry.get_text().strip() else None
        return request

    def start(self,*_):
        from p4vasp.ase_bulk import BulkTask
        from p4vasp.dos_analysis import worker_command
        try:request=self.request()
        except Exception as error:self.status.set_text(str(error));return
        self.result=None;self.model.clear();self.hint.hide()
        task=BulkTask(request,lambda result,error:GLib.idle_add(self.finished,task,result,error),
                      timeout=120,command_factory=worker_command,label='d-band analysis')
        self.job=task;self.status.set_text('Reading projected DOS and analyzing…');self.sensitivity();task.start()

    def finished(self,task,result,error):
        if not self.alive or self.job is not task:return False
        self.job=None
        if error:
            self.status.set_text(error)
            if 'pymatgen' in error or 'No module named' in error:self.hint.show();self.hint.show_all()
        else:
            self.result=result
            for name,value,unit in result['rows']:
                self.model.append([name,'Unavailable' if value is None else '%.3f'%value,unit])
            self.set_version(result['pymatgen_version'])
            self.status.set_text('atoms %s | %s | %s | E−EF: %.6g to %.6g eV.'%(
                ','.join(map(str,result['atoms'])),result['orbital'],result['spin'],result['emin'],result['emax']))
            self.status.set_tooltip_text('\n'.join([str(result['path']),result['normalization']]+result['notes']))
        self.sensitivity();self.applet.queue_plot_redraw();return False

    def cancel_job(self,*_):
        if self.job is not None:
            self.job.cancel();self.job=None
            self.status.set_text('Analysis cancelled.')
        self.sensitivity()

    def closed(self,*_):
        self.alive=False;self.cancel_job()
        if self.version_job is not None:self.version_job.cancel();self.version_job=None

    def copy_results(self,*_):
        if not self.result:return
        text='\n'.join('\t'.join(row) for row in self.model)
        Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD).set_text(text,-1)

    def export_results(self,*_):
        if not self.result:return
        from p4vasp.gtk3.file_dialogs import CompactFileDialog
        from p4vasp.dos_analysis import save_result
        dialog=CompactFileDialog(self.parent(),Path(self.result['path']).parent,'Export d-band analysis',save_name='d-band-analysis.csv')
        path=dialog.run()
        if path:
            try:save_result(path,self.result);self.status.set_tooltip_text((self.status.get_tooltip_text() or '')+'\nSaved '+str(path))
            except Exception as error:self.status.set_text('Export failed: '+str(error))

    def export_script(self,*_):
        if not self.result:return
        from p4vasp.gtk3.file_dialogs import CompactFileDialog
        from p4vasp.dos_replay import save_scripts
        dialog=CompactFileDialog(self.parent(),Path(self.result['path']).parent,'Export Python and Bash analysis scripts',save_name='d-band-analysis.py')
        path=dialog.run()
        if path:
            try:
                paths=save_scripts(path,self.result)
                self.status.set_tooltip_text((self.status.get_tooltip_text() or '')+'\n'+'\n'.join('Saved '+str(item) for item in paths))
            except Exception as error:self.status.set_text('Script export failed: '+str(error))

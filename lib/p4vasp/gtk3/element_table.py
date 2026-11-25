"""Colored periodic element browser and per-element personal settings editor."""
from p4vasp.gtk3 import Gtk, Gdk
from p4vasp.element_data import ElementData, COLUMNS, NUMBERS, PERIODS, check_value
from p4vasp.gtk3.file_dialogs import fit_dialog, entry, error_label


def tile_color(record):
    """Neutral display fallback only; never populate missing reference colors."""
    values=[record[field] for field in ('red','green','blue')]
    return tuple(values) if all(value is not None for value in values) else (.9,.9,.9)


class ElementEditor(Gtk.Dialog):
    def __init__(self, owner, symbol):
        super().__init__(title='Element properties — '+symbol, transient_for=owner.parent_window(),
                         modal=True, destroy_with_parent=True, use_header_bar=False)
        self.owner=owner;self.symbol=symbol
        self.data=ElementData(owner.store)
        self.index=NUMBERS[symbol]-1;self.original=self.data.rows[self.index]
        self.add_button('Cancel',Gtk.ResponseType.CANCEL)
        self.save_button=self.add_button('Save',Gtk.ResponseType.APPLY)
        self.set_default_response(Gtk.ResponseType.APPLY)
        fit_dialog(self,owner.parent_window(),440,440)
        scroll=Gtk.ScrolledWindow();scroll.set_policy(Gtk.PolicyType.NEVER,Gtk.PolicyType.AUTOMATIC)
        box=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=8);box.set_border_width(12)
        identity=Gtk.Label(xalign=0)
        identity.set_markup('<b>'+symbol+'</b> · atomic number '+str(NUMBERS[symbol]))
        box.pack_start(identity,False,False,0)
        hint=Gtk.Label(label='Blank = unknown / unset. RGB: 0–255.',xalign=0)
        box.pack_start(hint,False,False,0)
        grid=Gtk.Grid(column_spacing=10,row_spacing=8)
        self.fields={column:entry(self.original[column]) for column in range(2,len(COLUMNS))}
        for field in self.fields.values():
            field.set_width_chars(8);field.set_activates_default(True);field.set_placeholder_text('Unset')
        for row,column in enumerate((2,3)):
            grid.attach(Gtk.Label(label=COLUMNS[column],xalign=0),0,row,1,1)
            grid.attach(self.fields[column],1,row,1,1)
        self.fields[3].set_tooltip_text('Display radius only; does not change covalent bond detection.')
        self.color=Gtk.ColorButton();self.color.set_use_alpha(False);self.color.set_title('Element color — '+symbol)
        grid.attach(Gtk.Label(label='Color',xalign=0),0,2,1,1);grid.attach(self.color,1,2,1,1)
        rgb=Gtk.Box(spacing=5)
        for column,name in zip((4,5,6),('R','G','B')):
            rgb.pack_start(Gtk.Label(label=name),False,False,0)
            self.fields[column].set_width_chars(3)
            self.fields[column].connect('changed',self.rgb_changed)
            rgb.pack_start(self.fields[column],True,True,0)
        grid.attach(Gtk.Label(label='RGB (0–255)',xalign=0),0,3,1,1);grid.attach(rgb,1,3,1,1)
        for row,column in enumerate((7,8,9),4):
            grid.attach(Gtk.Label(label=COLUMNS[column],xalign=0),0,row,1,1)
            grid.attach(self.fields[column],1,row,1,1)
        self._color_sync=False
        rgba=Gdk.RGBA();rgba.red,rgba.green,rgba.blue=tile_color(self.data.catalog['elements'][self.index]);rgba.alpha=1
        self.color.set_rgba(rgba);self.color.connect('color-set',self.color_changed)
        box.pack_start(grid,False,False,0)
        self.error=error_label();box.pack_start(self.error,False,False,0)
        for field in self.fields.values():field.connect('changed',lambda *_:self.error.set_text(''))
        scroll.add(box);self.get_content_area().pack_start(scroll,True,True,0)
        self.connect('response',self.respond)

    def rgb_changed(self,*_):
        if self._color_sync:return
        try:
            values=[check_value(column,self.fields[column].get_text()) for column in (4,5,6)]
            if not all(values):return
            rgba=Gdk.RGBA();rgba.red,rgba.green,rgba.blue=[int(value)/255 for value in values];rgba.alpha=1
            self.color.set_rgba(rgba)
        except (ValueError,OverflowError):pass  # Report invalid entries on Save, not each keystroke.

    def color_changed(self,*_):
        rgba=self.color.get_rgba();self._color_sync=True
        try:
            for column,value in zip((4,5,6),(rgba.red,rgba.green,rgba.blue)):
                self.fields[column].set_text(str(round(value*255)))
        finally:self._color_sync=False

    def respond(self,dialog,response):
        if response!=Gtk.ResponseType.APPLY:
            self.destroy();return
        try:
            rows=[row[:] for row in self.data.rows]
            for column,field in self.fields.items():rows[self.index][column]=check_value(column,field.get_text())
            backups=self.data.save(rows)
        except Exception as error:
            self.error.set_text(str(error));return
        self.owner.saved(backups);self.destroy()


class ElementTable(Gtk.Box):
    """Keep the Models entry point while replacing the former spreadsheet UI."""
    def __init__(self, store, parent_window, show_error):
        super().__init__(orientation=Gtk.Orientation.VERTICAL,spacing=6)
        self.set_border_width(6)
        self.store,self.parent_window,self.show_error=store,parent_window,show_error
        self.editor=None;self.data=None;self.buttons={};self.colors={};self._providers={}
        self.status=Gtk.Label(xalign=0);self.status.set_line_wrap(True);self.status.set_max_width_chars(90)
        self.pack_start(self.status,False,False,0)
        actions=Gtk.Box(spacing=6)
        self.reload_button=Gtk.Button(label='Reload');self.reload_button.connect('clicked',lambda *_:self.load())
        actions.pack_start(self.reload_button,False,False,0);self.pack_start(actions,False,False,0)
        self.grid=Gtk.Grid(column_spacing=3,row_spacing=4,column_homogeneous=True)
        for group in range(1,19):self.grid.attach(Gtk.Label(label=str(group)),group,0,1,1)
        for period,elements in enumerate(PERIODS):
            row=period+1 if period<7 else period+2
            if period<7:self.grid.attach(Gtk.Label(label=str(period+1)),0,row,1,1)
            else:self.grid.attach(Gtk.Label(label='Ce–Lu' if period==7 else 'Th–Lr'),0,row,4,1)
            for symbol,column in elements:
                button=Gtk.Button();label=Gtk.Label()
                label.set_markup('<small>'+str(NUMBERS[symbol])+'</small>\n<b>'+symbol+'</b>')
                button.add(label);button.set_size_request(40,44)
                button.get_style_context().add_class('element-tile')
                button.connect('clicked',self.open_element,symbol)
                self.grid.attach(button,column+1,row,1,1);self.buttons[symbol]=button
        self.scroll=Gtk.ScrolledWindow();self.scroll.set_policy(Gtk.PolicyType.AUTOMATIC,Gtk.PolicyType.AUTOMATIC)
        self.scroll.add(self.grid);self.pack_start(self.scroll,True,True,0)
        self.connect('destroy',self.closed)
        self.load()

    def load(self):
        try:
            data=ElementData(self.store)
            for record in data.catalog['elements']:
                symbol=record['symbol'];color=tile_color(record);self.colors[symbol]=color
                button=self.buttons[symbol];context=button.get_style_context()
                if symbol in self._providers:context.remove_provider(self._providers[symbol])
                provider=Gtk.CssProvider()
                rgb=','.join(str(round(value*255)) for value in color)
                brightness=sum(value*weight for value,weight in zip(color,(.2126,.7152,.0722)))
                foreground='#111111' if brightness>.45 else '#ffffff'
                provider.load_from_data(('.element-tile { background-image: none; background-color: rgb('+rgb+'); color: '+foreground+'; border: 1px solid rgba(0,0,0,0.3); border-radius: 4px; padding: 2px; min-width: 24px; }').encode())
                context.add_provider(provider,Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
                self._providers[symbol]=provider;button.set_sensitive(True)
                missing=any(record[field] is None for field in ('red','green','blue'))
                button.set_tooltip_text(symbol+' — atomic number '+str(record['number'])+('\nColor unset; neutral tile.' if missing else '\nRGB: '+rgb)+'\nClick to edit properties.')
            self.data=data
            self.status.set_text('118 elements. Click an element to edit its properties, then Save.\nPersonal settings survive Git updates. Restart p4vasp to apply saved defaults to structures.')
        except Exception as error:
            for button in self.buttons.values():button.set_sensitive(False)
            self.status.set_text('Cannot load element data: '+str(error))

    def open_element(self,button,symbol=None):
        symbol=symbol or button
        if self.editor is not None:
            self.editor.present();return self.editor
        try:
            self.editor=ElementEditor(self,symbol)
            self.editor.connect('destroy',self.editor_closed)
            self.editor.show_all()
            return self.editor
        except Exception as error:self.show_error(self.parent_window(),str(error))

    def editor_closed(self,*_):self.editor=None

    def saved(self,backups):
        self.load()
        target='personal settings' if self.store.user_root is not None else 'element settings'
        self.status.set_text(('Saved '+target+'. Restart p4vasp to apply defaults.' if backups else 'No changes to save.')+'\nClick an element to edit its properties.')

    def closed(self,*_):
        if self.editor is not None:self.editor.destroy()

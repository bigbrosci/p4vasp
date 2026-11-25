"""Shared responsive native GTK layout for periodic element buttons."""
from p4vasp.gtk3 import Gtk


class FittedPeriodicGrid(Gtk.Grid):
    """Keep all groups and periods visible instead of requesting a fixed canvas."""
    def __init__(self,columns=19,rows=11):
        super().__init__(column_spacing=2,row_spacing=2,column_homogeneous=True,row_homogeneous=True)
        self.columns=columns;self.rows=rows
        self.sizing=Gtk.CssProvider();self.font_size=None
        self.set_hexpand(True);self.set_vexpand(True)

    def do_get_preferred_width(self):return 1,850

    def do_get_preferred_height(self):return 1,460

    def do_get_request_mode(self):return Gtk.SizeRequestMode.CONSTANT_SIZE

    def do_size_allocate(self,allocation):
        self.fit(self,allocation)
        Gtk.Grid.do_size_allocate(self,allocation)

    def track(self,widget):
        context=widget.get_style_context();context.add_class('periodic-fit-text')
        context.add_provider(self.sizing,Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION+1)

    def fit(self,widget,allocation):
        width=max(1,(allocation.width-2*(self.columns-1))/self.columns)
        height=max(1,(allocation.height-2*(self.rows-1))/self.rows)
        size=max(1,min(14,width*.46,height*.36))
        size=int(size*4)/4
        if size==self.font_size:return
        self.font_size=size
        self.sizing.load_from_data(('.periodic-fit-text { font-size: %.2fpx; }\n'
                                   '.element-tile { padding: 0; min-width: 0; min-height: 0; }'%size).encode())

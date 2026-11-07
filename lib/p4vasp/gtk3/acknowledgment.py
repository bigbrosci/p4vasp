"""Read-only credits for user-reported donations and suggestions."""
import json
from pathlib import Path
import p4vasp
from p4vasp.gtk3 import Gtk
from p4vasp.gtk3.file_dialogs import fit_dialog


def show_acknowledgment(parent=None):
    rows=json.loads((Path(p4vasp.p4vasp_home)/'data/acknowledgments.json').read_text(encoding='utf-8'))
    dialog=Gtk.Dialog(title='Acknowledgment',transient_for=parent,modal=True,use_header_bar=False)
    dialog.add_button('Close',Gtk.ResponseType.CLOSE)
    fit_dialog(dialog,parent,780,280)
    box=dialog.get_content_area();box.set_border_width(12);box.set_spacing(10)
    label=Gtk.Label(label='感谢捐款支持和提出建议的朋友。\nThank you for your donations and suggestions.',xalign=0)
    label.set_line_wrap(True);box.pack_start(label,False,False,0)
    model=Gtk.ListStore(str,str,str,str,str)
    for row in rows:model.append([row.get(key,'') for key in ('who','qq','donate','suggestion','date')])
    table=Gtk.TreeView(model=model)
    for i,title in enumerate(('Who','QQ号','Donate','Suggestion','Date')):
        renderer=Gtk.CellRendererText()
        column=Gtk.TreeViewColumn(title,renderer,text=i)
        column.set_resizable(True)
        table.append_column(column)
    scroll=Gtk.ScrolledWindow();scroll.set_policy(Gtk.PolicyType.AUTOMATIC,Gtk.PolicyType.AUTOMATIC)
    scroll.add(table);box.pack_start(scroll,True,True,0)
    dialog.connect('response',lambda widget,*_:widget.destroy())
    dialog.show_all()
    return dialog

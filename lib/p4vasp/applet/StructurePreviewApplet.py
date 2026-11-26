"""Read-only startup structure preview; editing stays in the native Show window."""
from collections import Counter
import math
from p4vasp.applet.Applet import Applet
from p4vasp.gtk3 import Gtk
from p4vasp.gtk3.mode_view import ModeView
from p4vasp.util import getAtomtypes
from p4vasp.viewer_style import display_radius
from p4vasp.Structure import Structure


class StructurePreviewApplet(Applet):
    menupath=None
    showmode=Applet.EMBEDDED_ONLY_MODE
    startup_preview=True

    def __init__(self):
        super().__init__()
        self.required=['INITIAL_STRUCTURE']

    def createPanel(self):
        self.panel=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=5)
        self.view=ModeView();self.view.set_hexpand(True);self.view.set_vexpand(True)
        self.panel.pack_start(self.view,True,True,0)
        self.summary=Gtk.Label(xalign=0);self.summary.set_margin_start(8)
        self.summary.set_margin_bottom(5);self.summary.set_line_wrap(True)
        self.panel.pack_start(self.summary,False,False,0)
        self.panel.show_all()
        return self.panel

    def updateSystem(self,*_):
        if self.panel is None:return
        self.view.data=None;self.view.queue_draw()
        self.summary.set_text('Open a structure to preview it here.')
        if self.system is None:return
        try:
            source=self.system.INITIAL_STRUCTURE
            if source is None or not len(source):return
            structure=Structure();structure.setStructure(source);structure.setCarthesian()
            scale=list(structure.scaling)
            if len(scale)==1 and math.isfinite(scale[0]) and scale[0]!=0:
                factor=scale[0] if scale[0]>0 else (abs(scale[0])/structure.getCellVolume())**(1./3.)
                scale=[factor]*3
            if len(scale)!=3 or any(not math.isfinite(s) or s<=0 for s in scale):
                raise ValueError('Invalid POSCAR scale')
            positions=[[p[j]*scale[j] for j in range(3)] for p in structure]
            cell=[[v[j]*scale[j] for j in range(3)] for v in structure.basis]
            symbols=[str(structure.info.getRecordForAtom(i).element).strip() for i in range(len(structure))]
            table=getAtomtypes();radii=[];colors=[]
            for symbol in symbols:
                record=table.getRecordForElement(symbol)
                radii.append(display_radius(record) if record is not None else .7)
                colors.append([record.red,record.green,record.blue] if record is not None else [1.,1.,1.])
            self.view.set_data(dict(symbols=symbols,positions=positions,
                                    cell=cell,radii=radii,colors=colors))
            self.summary.set_text('  '.join('%s: %d'%item for item in Counter(symbols).items()))
        except (ValueError,TypeError,AttributeError,IndexError,ZeroDivisionError,OverflowError) as error:
            self.view.data=None;self.view.queue_draw()
            self.summary.set_text('Preview unavailable: '+str(error)+'. Use Show to inspect the structure.')

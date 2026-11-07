"""Vibrational modes, signed mode displacement and ASE thermochemistry."""
from pathlib import Path
from p4vasp.applet.Applet import Applet
from p4vasp.gtk3 import Gtk
from p4vasp.gtk3.vibrations import VibrationsPage


class VibrationsApplet(Applet):
    menupath=['Analysis','Vibrations']
    show_system_selection=False

    def __init__(self):
        super().__init__()
        self.name='Vibrations';self.gladefile='vibrations.glade';self.gladename='applet_frame'
        self.page=None;self.source_system=None

    def initUI(self):
        self.page=VibrationsPage()
        scroll=Gtk.ScrolledWindow();scroll.set_policy(Gtk.PolicyType.AUTOMATIC,Gtk.PolicyType.AUTOMATIC)
        scroll.add(self.page);self.xml.get_widget('vibrations_host').pack_start(scroll,True,True,0)
        self.panel.show_all();self.updateSystem()

    def updateSystem(self,*_):
        if self.page is None or self.system is None or self.source_system is self.system:return
        self.source_system=self.system
        self.page.cancel();self.page.pause()
        data=getattr(self.system,'VIBRATIONS',None)
        if data:self.page.set_data(data);return
        folder=getattr(self.system,'PATH',None)
        path=Path(folder)/'OUTCAR' if folder else None
        if path and path.is_file():self.page.load_path(path)
        else:
            self.page.data=None;self.page.view.data=None;self.page.view.queue_draw();self.page.store.clear()
            self.page.invalidate();self.page.source.set_text('No frequency data loaded')
            self.page.status.set_text('Open a frequency OUTCAR to begin. A POSCAR alone has no normal modes.')

    def hide(self):
        if self.page:self.page.pause()

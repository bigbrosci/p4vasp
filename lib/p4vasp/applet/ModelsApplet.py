"""Empty model-library categories, ready for later model content."""
from p4vasp.applet.Applet import Applet
from p4vasp.gtk3 import Gtk


class ModelsApplet(Applet):
    menupath = ['Database', 'Models']
    show_system_selection = False

    def __init__(self):
        super().__init__()
        self.name = 'Models'
        self.gladefile = 'models.glade'
        self.gladename = 'applet_frame'

    def initUI(self):
        self.notebook = Gtk.Notebook()
        for title in ('single atom', 'gas phase', 'bulk', 'surface'):
            page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            self.notebook.append_page(page, Gtk.Label(label=title))
        self.xml.get_widget('models_host').pack_start(self.notebook, True, True, 0)
        self.panel.show_all()

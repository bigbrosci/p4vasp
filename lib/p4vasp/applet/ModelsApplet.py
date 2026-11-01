"""Model-library tabs with single-atom and local XYZ gas inputs."""
from p4vasp.applet.Applet import Applet
from p4vasp.gtk3 import Gtk
from p4vasp.gtk3.single_atom import SingleAtomPage
from p4vasp.gtk3.gas_phase import GasPhasePage
from p4vasp.gtk3.element_table import ElementTable
from p4vasp.resource_data import ResourceStore
from p4vasp.applet.ResourceHubApplet import message


class ModelsApplet(Applet):
    menupath = None
    show_system_selection = False

    def __init__(self):
        super().__init__()
        self.name = 'Models'
        self.store = ResourceStore()
        self.gladefile = 'models.glade'
        self.gladename = 'applet_frame'

    def initUI(self):
        self.notebook = Gtk.Notebook()
        for title in ('single atom', 'gas phase', 'bulk', 'surface', 'p4vasp data'):
            if title == 'single atom': page = SingleAtomPage()
            elif title == 'gas phase': page = GasPhasePage()
            elif title == 'p4vasp data':
                page = ElementTable(self.store, self.parent_window, message)
                self.element_table = page
            else: page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            if title == 'single atom': self.single_atom_page = page
            self.notebook.append_page(page, Gtk.Label(label=title))
        self.xml.get_widget('models_host').pack_start(self.notebook, True, True, 0)
        self.notebook.connect('switch-page', self.switch_page)
        self.panel.show_all()

    def switch_page(self, notebook, page, index):
        if index == 1: page.refresh()

    def parent_window(self):
        parent=self.panel.get_toplevel()
        return parent if isinstance(parent,Gtk.Window) else None

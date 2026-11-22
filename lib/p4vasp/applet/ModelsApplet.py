"""Lazy single-atom, molecular, bulk, surface and element-data pages."""
from p4vasp.applet.Applet import Applet
from p4vasp.gtk3 import Gtk
from p4vasp.gtk3.single_atom import SingleAtomPage
from p4vasp.gtk3.gas_phase import GasPhasePage
from p4vasp.gtk3.bulk import BulkPage
from p4vasp.gtk3.surface import SurfacePage
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
        self._page_contents = {}
        self._page_hosts = {}
        for index, title in enumerate(('single atom', 'gas phase', 'bulk', 'surface', 'p4vasp data')):
            if index == 0:
                page = SingleAtomPage()
                self.single_atom_page = page
                self._page_contents[index] = page
            elif index in (2,3):
                page = Gtk.ScrolledWindow()
                page.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
            else:
                page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            self._page_hosts[index] = page
            self.notebook.append_page(page, Gtk.Label(label=title))
        self.xml.get_widget('models_host').pack_start(self.notebook, True, True, 0)
        self.notebook.connect('switch-page', self.switch_page)
        self.panel.show_all()

    def switch_page(self, notebook, page, index):
        if index in self._page_contents:
            if index == 1:
                self._page_contents[index].refresh()
            return
        # Keep every page for this applet's lifetime so edits and running jobs
        # survive tab switches. GasPhasePage already refreshes on construction.
        if index == 1:
            content = GasPhasePage()
            self.gas_phase_page = content
        elif index == 2:
            content = BulkPage()
            self.bulk_page = content
        elif index == 3:
            content = SurfacePage(lambda: getattr(self._page_contents.get(2), 'result', None))
            self.surface_page = content
        elif index == 4:
            content = ElementTable(self.store, self.parent_window, message)
            self.element_table = content
        else:
            return
        host = self._page_hosts[index]
        if index in (2,3):
            host.add(content)
        else:
            host.pack_start(content, True, True, 0)
        self._page_contents[index] = content
        host.show_all()

    def parent_window(self):
        parent=self.panel.get_toplevel()
        return parent if isinstance(parent,Gtk.Window) else None

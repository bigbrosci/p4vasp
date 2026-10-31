"""Empty model-library categories, ready for later model content."""
from p4vasp.applet.Applet import Applet


class ModelsApplet(Applet):
    menupath = ['Database', 'Models']
    show_system_selection = False

    def __init__(self):
        super().__init__()
        self.name = 'Models'
        self.gladefile = 'models.glade'
        self.gladename = 'applet_frame'

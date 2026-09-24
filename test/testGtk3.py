"""GTK3 regression checks. Run separately with a display (or xvfb-run).

PYTHONPATH=lib:src P4VASP_HOME=$PWD /usr/bin/python3 -m unittest discover -s test -p testGtk3.py
"""
import ast
import glob
import os
from pathlib import Path
import sys
import unittest
from types import SimpleNamespace

from p4vasp import gtk3 as gtk
from p4vasp.gtk3.glade import XML
from p4vasp.piddle.piddleGTK3.core import BasicCanvas, InteractiveCanvas
from p4vasp.piddle.piddle import red, blue, white, Font

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(gtk.init_check()[0], "GTK3 tests require a display")
class TestGtk3(unittest.TestCase):
    def setUp(self):
        self.callback_errors = []
        self.original_hook = sys.excepthook
        sys.excepthook = lambda *args: self.callback_errors.append(args)

    def tearDown(self):
        sys.excepthook = self.original_hook
        self.assertFalse(self.callback_errors, self.callback_errors)

    def test_all_resources(self):
        paths = sorted((ROOT / 'data/glade2').glob('*.glade'))
        self.assertGreater(len(paths), 30)
        for path in paths:
            with self.subTest(path=path.name):
                xml = XML(str(path))
                try:
                    self.assertEqual(xml.property_errors, [])
                    self.assertTrue(xml.widgets)
                finally:
                    for widget in xml.widgets.values():
                        if isinstance(widget, gtk.Window):
                            widget.destroy()

    def test_cairo_draw_and_background_restore(self):
        canvas = BasicCanvas()
        canvas.ensure_size(160, 120)
        canvas.clear(white)
        canvas.drawRect(10, 10, 60, 60, fillColor=red)
        canvas.drawString('A & <B>', 10, 90, font=Font(size=12, underline=1))
        canvas.drawString('rotated', 130, 100, angle=90)
        self.assertGreater(canvas.stringWidth('A & <B>'), 10)
        self.assertGreater(canvas.fontAscent(), 0)
        self.assertGreaterEqual(canvas.fontDescent(), 0)
        canvas.to_background_buffer()
        expected = bytes(canvas.drawable.get_data())
        canvas.drawLine(0, 0, 160, 120, blue, 3)
        self.assertNotEqual(bytes(canvas.drawable.get_data()), expected)
        canvas.from_background_buffer()
        self.assertEqual(bytes(canvas.drawable.get_data()), expected)
        canvas.ensure_size(240, 200)
        self.assertEqual(canvas.drawable.get_width(), 240)
        canvas.close()
        canvas.area.destroy()

    def test_plot_widget_draw_resize_and_keyboard(self):
        from p4vasp.GraphCanvas import GraphCanvas
        from p4vasp.GraphPM import createGraph
        world = createGraph('dos')
        window = gtk.OffscreenWindow()
        area = gtk.DrawingArea()
        window.add(area)
        canvas = GraphCanvas(drawing_area=area, top=window, world=world)
        canvas.setGraphData([[[(0, 0), (1, 2), (2, 1)]]])
        canvas.viewAll()
        canvas.updateGraph()
        window.show_all()
        while gtk.events_pending():
            gtk.main_iteration()
        self.assertIsNotNone(window.get_pixbuf())
        before = world[0].world_xmax - world[0].world_xmin
        canvas.onKeyCallback(canvas, '+', 0)
        self.assertLess(world[0].world_xmax - world[0].world_xmin, before)
        canvas.close()
        window.destroy()

    def test_phonon_model_notifications(self):
        from p4vasp.applet.PhononApplet import KPathTreeModel
        from p4vasp.Dyna import Dyna
        data = Dyna()
        model = KPathTreeModel(data)
        view = gtk.TreeView(model)
        self.assertEqual(len(view.get_model()), 0)
        data.addSegment(label1='Gamma', label2='X')
        model.row_inserted('0', model.get_iter('0'))
        self.assertEqual(len(view.get_model()), 1)
        self.assertEqual(view.get_model()[0][0], 'Gamma')
        data.labels[0] = ('L', data.labels[0][1])
        model.row_changed('0', model.get_iter('0'))
        self.assertEqual(view.get_model()[0][0], 'L')
        data.deleteSegment(0)
        model.row_deleted('0')
        self.assertEqual(len(view.get_model()), 0)
        view.destroy()

    def test_lattice_programmatic_updates(self):
        from p4vasp.applet.LatticeApplet import LatticeApplet
        from p4vasp.matrix import Vector
        applet = LatticeApplet()
        applet.createPanel()
        basis = (Vector(2, 0, 0), Vector(0, 3, 0), Vector(0, 0, 4))
        applet.setBasis(basis)
        applet.updateParameters()
        self.assertEqual(float(applet.widgets.a_entry.get_text()), 2)
        self.assertEqual(float(applet.widgets.b_entry.get_text()), 3)
        self.assertEqual(float(applet.widgets.c_entry.get_text()), 4)
        self.assertEqual(float(applet.widgets.alpha_entry.get_text()), 90)
        applet.widgets.a11.set_text('')
        self.assertTrue(applet.allow_cell_update)
        applet.panel.destroy()

    def test_legacy_imports_use_gtk3_backend(self):
        import gtk as legacy
        from p4vasp.piddle.piddleGTK2p4 import BasicCanvas as old_canvas
        self.assertIs(legacy.Window, gtk.Window)
        self.assertIs(old_canvas, BasicCanvas)

    def test_application_imports_do_not_require_pygtk(self):
        paths = list((ROOT / 'lib/p4vasp/applet').glob('*.py')) + [ROOT / 'p4v.py', ROOT / 'lib/p4vasp/GraphCanvas.py']
        for path in paths:
            with self.subTest(path=path.name):
                for node in ast.walk(ast.parse(path.read_text())):
                    if isinstance(node, ast.Import):
                        self.assertFalse(any(item.name.split('.')[0] in ('gtk', 'pygtk', 'gobject', 'pango') for item in node.names))
                    if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id == 'gtk':
                        self.assertTrue(hasattr(gtk, node.attr), node.attr)


if __name__ == '__main__':
    unittest.main()

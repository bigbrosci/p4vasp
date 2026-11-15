"""Displayed GTK3/Cairo behavior for cloned transparent colors and drawing values."""
import time
import unittest
from p4vasp.gtk3 import Gtk
from p4vasp.piddle.piddle import Color,Font,white
from p4vasp.piddle.piddleGTK3.core import BasicCanvas


@unittest.skipUnless(Gtk.init_check()[0],'GTK display required')
class DrawingValuesGtkTest(unittest.TestCase):
    def setUp(self):
        self.window=Gtk.Window();self.canvas=BasicCanvas()
        self.canvas.area.set_size_request(300,160);self.window.add(self.canvas.area);self.window.show_all()
        for _ in range(20):
            while Gtk.events_pending():Gtk.main_iteration_do(False)
            time.sleep(.003)
        self.assertTrue(self.canvas.area.get_mapped())

    def tearDown(self):self.canvas.close();self.window.destroy()

    def test_cloned_transparent_color(self):
        self.canvas.clear(white);before=bytes(self.canvas.drawable.get_data())
        self.canvas.drawRect(10,10,80,80,edgeColor=Color(-1,-1,-1),fillColor=Color(-1,-1,-1))
        self.assertEqual(bytes(self.canvas.drawable.get_data()),before)
        self.canvas.clear(Color(-1,-1,-1))
        self.assertEqual(set(bytes(self.canvas.drawable.get_data())),{0})

    def test_divided_color_and_font_draw(self):
        self.canvas.clear(white);before=bytes(self.canvas.drawable.get_data())
        self.canvas.drawLine(15,30,280,100,color=Color(.2,.4,.8)/2,width=3)
        self.canvas.drawString('Python 3 drawing values',15,130,font=Font(face='Helvetica',size=14))
        self.canvas.flush()
        while Gtk.events_pending():Gtk.main_iteration_do(False)
        self.assertNotEqual(bytes(self.canvas.drawable.get_data()),before)
        self.canvas.drawable.write_to_png('/tmp/p4vasp-drawing-values.png')


if __name__=='__main__':unittest.main()

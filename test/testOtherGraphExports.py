"""Remaining graph exports: numeric roundtrips and portable SVG/FIG content."""
from io import StringIO
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from xml.etree import ElementTree as ET
import numpy as np
from p4vasp.GraphCanvas import Export
from p4vasp.GraphPM import createGraph
from p4vasp.graph import World
from p4vasp.piddle.piddle import Color,Font
from p4vasp.piddle.piddleFIG import FIGCanvas
from p4vasp.piddle.piddleSVG.piddleSVG import SVGCanvas


class OtherExportsTest(unittest.TestCase):
    def test_data_and_grace_roundtrip(self):
        data=[[[(0.,.123456789),(1.,-2.)],[(2.,3.),(4.,5.)]]]
        world=createGraph('dos');size=(world.page_size_x,world.page_size_y)
        with tempfile.TemporaryDirectory() as folder:
            export=Export(world,data)
            for suffix,kind in [('dat',0),('agr',1)]:
                path=Path(folder)/('中文 & plot.'+suffix);export.file=str(path);export.type=kind;export.export()
                if kind==0:
                    rows=[list(map(float,line.split())) for line in path.read_text().splitlines() if line.strip()]
                    np.testing.assert_allclose(rows,[row for dataset in data[0] for row in dataset],rtol=5e-6)
                else:
                    restored=World();errors=restored.parseGrace(str(path));self.assertFalse(errors)
                    self.assertEqual(len(restored[0]),2)
                    for actual,expected in zip(restored[0],data[0]):np.testing.assert_allclose(actual,expected,rtol=5e-6)
        self.assertEqual(size,(world.page_size_x,world.page_size_y));self.assertEqual(data[0][0][0],(0.,.123456789))

    def test_svg_unicode_xml_default_font_and_namespace(self):
        canvas=SVGCanvas(size=(200,100));font=Font()
        text='A & B <C> café 中文'
        canvas.drawString(text,5,40,font=font,angle=15)
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'图.svg';canvas.save_(path)
            raw=path.read_bytes();root=ET.fromstring(raw)
        self.assertEqual(root.tag,'{http://www.w3.org/2000/svg}svg')
        self.assertEqual(''.join(root.itertext()).strip(),text)
        self.assertIn('UTF-8',raw[:70].decode('ascii'));self.assertNotIn(b'DOCTYPE',raw)
        self.assertIsNone(font.face)
        element=next(root.iter('{http://www.w3.org/2000/svg}text'))
        self.assertIn('font-family:sans-serif',element.attrib['style'].replace(' ',''))

    def test_svg_fallback_fonts_are_not_mutated(self):
        font=Font(face=['Helvetica','Times New Roman'])
        canvas=SVGCanvas();canvas.drawString('text',5,20,font=font)
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'font.svg';canvas.save_(path);root=ET.fromstring(path.read_bytes())
        element=next(root.iter('{http://www.w3.org/2000/svg}text'))
        self.assertIn('Helvetica',element.attrib['style']);self.assertIn('Times New Roman',element.attrib['style'])
        self.assertEqual(font.face,['Helvetica','Times New Roman'])

    def test_fig_custom_rgb_and_escaped_text(self):
        canvas=FIGCanvas();canvas.drawLine(5,5,40,40,color=Color(.2,.4,.6))
        canvas.drawString('A & café',10,60,font=Font(face='Helvetica'))
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'图.fig';canvas.save(path);data=path.read_text()
        self.assertTrue(data.startswith('#FIG 3.2'));self.assertIn('#336699',data)
        self.assertIn('\\351',data);self.assertIn('\\001',data)

    def test_fig_output_closed_on_write_failure(self):
        class BrokenFile(StringIO):
            def write(self,text):raise OSError('simulated write failure')
        stream=BrokenFile()
        with patch('builtins.open',return_value=stream):
            with self.assertRaises(OSError):FIGCanvas().save('unused.fig')
        self.assertTrue(stream.closed)


if __name__=='__main__':unittest.main()

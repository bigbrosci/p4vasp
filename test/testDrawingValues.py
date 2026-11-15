"""Drawing value equality, hashing, division and old pickle state compatibility."""
import pickle
import unittest
from p4vasp.piddle.piddle import Color,Font,transparent


class DrawingValueTest(unittest.TestCase):
    def test_color_value_and_hash(self):
        a=Color(.2,.4,.6);b=Color(.2,.4,.6)
        self.assertEqual(a,b);self.assertFalse(a!=b)
        self.assertEqual(hash(a),hash(b));self.assertEqual({a:'value'}[b],'value')
        self.assertEqual(Color(-1,-1,-1),transparent)
        # The old weighted comparator equated these distinct RGB triples.
        self.assertNotEqual(Color(.5,0,0),Color(0,1,0))
        self.assertNotEqual(a,None);self.assertNotEqual(a,(.2,.4,.6))
        with self.assertRaises(TypeError):sorted([a,Color(1,1,1)])

    def test_forward_division_preserves_old_method(self):
        color=Color(.2,.4,.6);result=color/2
        self.assertEqual((result.red,result.green,result.blue),(.1,.2,.3))
        self.assertEqual(result,color.__div__(2))
        self.assertEqual((color.red,color.green,color.blue),(.2,.4,.6))
        with self.assertRaises(ZeroDivisionError):color/0

    def test_font_attributes_and_hash(self):
        a=Font(14,1,0,1,'Helvetica');b=Font(14,1,0,1,'Helvetica')
        self.assertEqual(a,b);self.assertFalse(a!=b);self.assertEqual(hash(a),hash(b))
        self.assertEqual({a:'cached'}[b],'cached')
        self.assertNotEqual(a,Font(14,1,0,0,'Helvetica'));self.assertNotEqual(a,None)
        self.assertEqual(Font(face=['Helvetica','serif']),Font(face=['Helvetica','serif']))
        with self.assertRaises(TypeError):hash(Font(face=['Helvetica','serif']))
        with self.assertRaises(TypeError):sorted([a,b])

    def test_active_ps_pdf_text_streams(self):
        from io import StringIO
        from p4vasp.piddle.piddlePS import PSCanvas
        from p4vasp.piddle.piddlePDF import PDFCanvas
        for cls,signature in ((PSCanvas,'%!PS'),(PDFCanvas,'%PDF')):
            canvas=cls(size=(140,100));stream=StringIO()
            canvas.drawLine(5,5,120,50,color=Color(.2,.4,.6)/2)
            canvas.drawString('value check',5,75,font=Font(face='Helvetica'))
            canvas.drawString('same font',5,90,font=Font(face='Helvetica'))
            canvas.save(stream)
            output=stream.getvalue();self.assertTrue(output.startswith(signature))
            self.assertGreater(len(output),500)

    def test_pickle_existing_field_state_and_readonly(self):
        for value,fields in [(Color(.2,.4,.6),{'red','green','blue'}),
                             (Font(14,1,0,1,['Helvetica','serif']),{'size','bold','italic','underline','face'})]:
            for protocol in (2,pickle.HIGHEST_PROTOCOL):
                restored=pickle.loads(pickle.dumps(value,protocol=protocol))
                self.assertEqual(restored.__dict__,value.__dict__)
                self.assertEqual(restored,value);self.assertEqual(set(restored.__dict__),fields)
            with self.assertRaises(TypeError):setattr(value,next(iter(fields)),1)


if __name__=='__main__':unittest.main()

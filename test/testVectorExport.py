"""Real PS/PDF byte output, PDF offsets and compressed-stream decoding."""
import base64
from io import BytesIO,StringIO
from pathlib import Path
import re
import tempfile
import unittest
import zlib
from p4vasp.piddle.piddle import Color,Font
from p4vasp.piddle.piddlePS import PSCanvas
from p4vasp.piddle.piddlePDF import PDFCanvas


def check_pdf(test,data):
    test.assertIn(b'%PDF-1.2',data[:1024]);test.assertTrue(data.endswith(b'%%EOF'))
    match=re.search(rb'startxref\r\n(\d+)\r\n%%EOF$',data)
    test.assertIsNotNone(match);start=int(match[1]);test.assertEqual(data[start:start+6],b'xref\r\n')
    lines=data[start:].split(b'\r\n');count=int(lines[1].split()[1])
    for i in range(1,count):
        offset=int(lines[2+i].split()[0])
        test.assertTrue(data[offset:].startswith(('%d 0 obj\r\n'%i).encode('ascii')),(i,offset))
    streams=[]
    for match in re.finditer(rb'<< /Length (\d+)([^\r\n]*)>>\r\nstream\r\n',data):
        length=int(match[1]);payload=data[match.end():match.end()+length]
        test.assertTrue(data[match.end()+length:].startswith(b'endstream'))
        if b'ASCII85Decode' in match[2]:payload=zlib.decompress(base64.a85decode(payload.rstrip(b'\r\n'),adobe=True))
        streams.append(payload)
    test.assertTrue(streams);test.assertTrue(any(b'BT' in p for p in streams))


def drawing(cls):
    canvas=cls(size=(180,120));canvas.drawLine(10,10,150,75,color=Color(.2,.4,.6)/2)
    canvas.drawString('caf\u00e9 (plot) \\',10,100,font=Font(face='Helvetica'))
    return canvas


class VectorExportTest(unittest.TestCase):
    def test_unicode_paths_and_pdf_offsets(self):
        with tempfile.TemporaryDirectory() as folder:
            for cls,ext in ((PSCanvas,'ps'),(PDFCanvas,'pdf')):
                path=Path(folder)/("图 plot ' & %."+ext)
                drawing(cls).save(path)
                data=path.read_bytes();self.assertGreater(len(data),500)
                if ext=='pdf':check_pdf(self,data)
                else:self.assertTrue(data.startswith(b'%!PS'));self.assertIn(b'%%EOF',data)

    def test_binary_and_legacy_memory_streams(self):
        for cls in (PSCanvas,PDFCanvas):
            for stream in (BytesIO(),StringIO()):
                drawing(cls).save(stream);self.assertFalse(stream.closed)
                data=stream.getvalue();data=data.encode('latin-1') if isinstance(data,str) else data
                if cls==PDFCanvas:check_pdf(self,data)
                else:self.assertTrue(data.startswith(b'%!PS'))

    def test_compressed_pdf(self):
        canvas=drawing(PDFCanvas);canvas.pdf.setPageCompression(1)
        output=BytesIO();canvas.save(output);data=output.getvalue()
        self.assertIn(b'ASCII85Decode',data);check_pdf(self,data)

    def test_pdf_prefixed_binary_stream_offsets(self):
        output=BytesIO(b'%prefix\n');output.seek(0,2)
        drawing(PDFCanvas).save(output);check_pdf(self,output.getvalue())

    def test_mixed_compression_pages(self):
        canvas=drawing(PDFCanvas);canvas.pdf.showPage()
        canvas.pdf.setPageCompression(1);canvas.drawString('second page',10,30)
        output=BytesIO();canvas.save(output);data=output.getvalue()
        check_pdf(self,data);self.assertIn(b'/Count 2',data)
        self.assertEqual(data.count(b'endstream'),2)

    def test_text_file_stream_rejected_without_writing(self):
        with tempfile.TemporaryDirectory() as folder:
            for cls in (PSCanvas,PDFCanvas):
                path=Path(folder)/'text-target';path.write_bytes(b'keep')
                with path.open('r+',encoding='utf-8') as stream:
                    with self.assertRaises(TypeError):drawing(cls).save(stream)
                    self.assertFalse(stream.closed)
                self.assertEqual(path.read_bytes(),b'keep')

    def test_serialization_failure_preserves_file_and_ps_state(self):
        with tempfile.TemporaryDirectory() as folder:
            for cls in (PSCanvas,PDFCanvas):
                path=Path(folder)/'existing';path.write_bytes(b'keep')
                canvas=drawing(cls)
                if cls==PSCanvas:
                    canvas.code.append('%% unsupported 中文');old=list(canvas.code)
                else:canvas.pdf.setTitle('unsupported 中文')
                with self.assertRaises(UnicodeEncodeError):canvas.save(str(path))
                self.assertEqual(path.read_bytes(),b'keep')
                if cls==PSCanvas:self.assertEqual(canvas.code,old)


if __name__=='__main__':unittest.main()

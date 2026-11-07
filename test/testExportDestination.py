"""Displayed compact PNG destination checks; requires GTK3 and a display."""
from pathlib import Path
import os
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'lib'))
from p4vasp.gtk3 import Gtk, GLib
from p4vasp.gtk3.file_dialogs import PngSaveDialog, FolderDialog, CompactFileDialog


@unittest.skipUnless(Gtk.init_check()[0], 'GTK display required')
class DestinationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.errors = []

    def later(self, callback):
        def run():
            try:
                callback()
            except BaseException as error:
                self.errors.append(error)
                for window in Gtk.Window.list_toplevels():
                    if isinstance(window, Gtk.Dialog):
                        window.response(Gtk.ResponseType.CANCEL)
            return False
        GLib.timeout_add(100, run)

    def tearDown(self):
        if self.errors:
            raise self.errors[0]

    def assert_buttons_fit(self, dialog):
        width, height = dialog.get_allocated_width(), dialog.get_allocated_height()
        self.assertLessEqual(width, 640)
        self.assertLessEqual(height, 480)
        for response in (Gtk.ResponseType.CANCEL, Gtk.ResponseType.OK):
            button = dialog.get_widget_for_response(response)
            self.assertTrue(button.get_mapped())
            x, y = button.translate_coordinates(dialog, 0, 0)
            self.assertGreaterEqual(x, 0)
            self.assertGreaterEqual(y, 0)
            self.assertLessEqual(x+button.get_allocated_width(), width)
            self.assertLessEqual(y+button.get_allocated_height(), height)
        destination = os.environ.get('P4VASP_TEST_SCREENSHOTS')
        if destination:
            import cairo
            folder = Path(destination)
            folder.mkdir(parents=True, exist_ok=True)
            surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
            dialog.draw(cairo.Context(surface))
            title=dialog.get_title()
            filename=('frequency-open.png' if title=='Open frequency OUTCAR' else
                      'frequency-save.png' if title=='Save displaced POSCAR' else
                      'folder.png' if 'folder' in title else 'save.png')
            surface.write_to_png(str(folder/filename))

    def test_small_workarea_save_and_browse_buttons(self):
        (self.root/('long folder name '*10)).mkdir()
        with patch('p4vasp.gtk3.file_dialogs.workarea', return_value=SimpleNamespace(width=640, height=480)):
            save = PngSaveDialog(None, self.root)
            browser = FolderDialog(save.dialog, self.root)
        def inspect_browser():
            self.assert_buttons_fit(browser.dialog)
            browser.dialog.response(Gtk.ResponseType.CANCEL)
        def inspect_save():
            self.assert_buttons_fit(save.dialog)
            self.assertEqual(save.filename.get_text(), 'structure.png')
            self.later(inspect_browser)
            self.assertIsNone(browser.run())
            save.dialog.response(Gtk.ResponseType.CANCEL)
        self.later(inspect_save)
        self.assertIsNone(save.run())

    def test_compact_open_small_screen_file_navigation(self):
        child=self.root/('long directory '*9);child.mkdir()
        target=child/'OUTCAR with spaces 测试';target.write_text('synthetic')
        with patch('p4vasp.gtk3.file_dialogs.workarea',return_value=SimpleNamespace(width=640,height=480)):
            browser=CompactFileDialog(None,self.root,'Open frequency OUTCAR')
        def choose():
            self.assert_buttons_fit(browser.dialog)
            self.assertEqual(browser.dialog.get_widget_for_response(Gtk.ResponseType.OK).get_label(),'Open')
            browser.tree.emit('row-activated',Gtk.TreePath.new_from_string('0'),browser.tree.get_column(0))
            self.assertEqual(browser.current,child)
            browser.tree.get_selection().select_path('0')
            self.assertEqual(browser.filename.get_text(),target.name)
            browser.dialog.response(Gtk.ResponseType.OK)
        self.later(choose)
        self.assertEqual(browser.run(),str(target))

    def test_compact_save_buttons_and_existing_file_rejection(self):
        target=self.root/'POSCAR';target.write_text('keep original')
        with patch('p4vasp.gtk3.file_dialogs.workarea',return_value=SimpleNamespace(width=640,height=480)):
            browser=CompactFileDialog(None,self.root,'Save displaced POSCAR',save_name='POSCAR')
        def correct():
            self.assertIn('not overwritten',browser.error.get_text())
            browser.filename.set_text('POSCAR_new')
            browser.dialog.response(Gtk.ResponseType.OK)
        def inspect():
            self.assert_buttons_fit(browser.dialog)
            self.assertEqual(browser.dialog.get_widget_for_response(Gtk.ResponseType.OK).get_label(),'Save')
            self.later(correct);browser.dialog.response(Gtk.ResponseType.OK)
        self.later(inspect)
        self.assertEqual(browser.run(),str(self.root/'POSCAR_new'))
        self.assertEqual(target.read_text(),'keep original')

    def test_compact_missing_file_cancel_and_pasted_path(self):
        target=self.root/'OUTCAR';target.write_text('synthetic')
        browser=CompactFileDialog(None,self.root,'Open frequency OUTCAR')
        def correct():
            self.assertIn('does not exist',browser.error.get_text())
            browser.location.set_text(str(target));browser.location.emit('activate')
        def invalid():
            browser.filename.set_text('missing');self.later(correct)
            browser.dialog.response(Gtk.ResponseType.OK)
        self.later(invalid);self.assertEqual(browser.run(),str(target))
        browser=CompactFileDialog(None,self.root,'Open frequency OUTCAR')
        self.later(lambda:browser.dialog.response(Gtk.ResponseType.CANCEL))
        self.assertIsNone(browser.run())

    def test_export_callback_receives_png_path(self):
        from p4vasp.export_image import ExportImageDialog
        save = PngSaveDialog(None, self.root)
        save.filename.set_text('image 测试')
        exported = []
        export = ExportImageDialog.__new__(ExportImageDialog)
        export.dialog = None
        export.start = exported.append
        self.later(lambda: save.dialog.response(Gtk.ResponseType.OK))
        with patch('p4vasp.gtk3.file_dialogs.PngSaveDialog', return_value=save):
            export.choose_file()
        self.assertEqual(exported, [str(self.root/'image 测试.png')])
        self.assertFalse((self.root/'image 测试.png').exists())

    def test_invalid_folder_stays_open_then_corrects(self):
        save = PngSaveDialog(None, self.root/'missing')
        def correct():
            self.assertTrue(save.error.get_text())
            save.folder.set_text(str(self.root))
            save.dialog.response(Gtk.ResponseType.OK)
        def invalid():
            self.later(correct)
            save.dialog.response(Gtk.ResponseType.OK)
        self.later(invalid)
        self.assertEqual(save.run(), str(self.root/'structure.png'))

    def test_browse_navigation_preserves_filename(self):
        child = self.root/'child'
        child.mkdir()
        save = PngSaveDialog(None, self.root)
        save.filename.set_text('keep.png')
        browser = FolderDialog(save.dialog, self.root)
        def navigate():
            browser.location.set_text(str(child))
            browser.location.emit('activate')
            self.assertEqual(browser.current, child)
            browser.up.clicked()
            self.assertEqual(browser.current, self.root)
            browser.location.set_text(str(child))
            browser.location.emit('activate')
            browser.dialog.response(Gtk.ResponseType.OK)
        self.later(navigate)
        with patch('p4vasp.gtk3.file_dialogs.FolderDialog', return_value=browser):
            save.on_browse()
        self.assertEqual(save.folder.get_text(), str(child))
        self.assertEqual(save.filename.get_text(), 'keep.png')
        save.dialog.destroy()

    def test_existing_png_requires_confirmation(self):
        target = self.root/'structure.png'
        target.write_bytes(b'keep original')
        save = PngSaveDialog(None, self.root)
        def decline():
            confirm = next(w for w in Gtk.Window.list_toplevels() if isinstance(w, Gtk.MessageDialog))
            confirm.response(Gtk.ResponseType.CANCEL)
            self.later(lambda: save.dialog.response(Gtk.ResponseType.CANCEL))
        def request():
            self.later(decline)
            save.dialog.response(Gtk.ResponseType.OK)
        self.later(request)
        self.assertIsNone(save.run())
        self.assertEqual(target.read_bytes(), b'keep original')


if __name__ == '__main__':
    unittest.main()

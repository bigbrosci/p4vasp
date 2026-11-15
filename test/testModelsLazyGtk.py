"""Real GTK tabs: defer hidden work, preserve edits, refresh local XYZ library."""
import importlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from p4vasp.gtk3 import Gtk
from p4vasp.resource_data import ResourceStore

module = importlib.import_module('p4vasp.applet.ModelsApplet')
gas_module = importlib.import_module('p4vasp.gtk3.gas_phase')


@unittest.skipUnless(Gtk.init_check()[0], 'Requires a display')
class ModelsLazyTest(unittest.TestCase):
    def test_deferred_pages_keep_state_and_refresh_library(self):
        errors = []
        import sys
        original = sys.excepthook
        sys.excepthook = lambda *args: errors.append(args)
        try:
            with tempfile.TemporaryDirectory() as temporary:
                folder = Path(temporary)
                library = folder / 'xyz'
                library.mkdir()
                (library / 'H.xyz').write_text('1\nHydrogen\nH 0 0 0\n')
                import shutil
                from p4vasp.resource_data import FILES
                root = Path(__file__).resolve().parents[1]
                for relative in FILES.values():
                    dest = folder / 'data' / relative
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(root / 'data' / relative, dest)
                with patch('p4vasp.gtk3.gas_phase.library_path', return_value=library), \
                     patch.object(gas_module, 'scan_library', wraps=gas_module.scan_library) as scans, \
                     patch.object(module, 'GasPhasePage', wraps=module.GasPhasePage) as gas_factory, \
                     patch.object(module, 'BulkPage', wraps=module.BulkPage) as bulk_factory, \
                     patch.object(module, 'ElementTable', wraps=module.ElementTable) as table_factory:
                    applet = module.ModelsApplet()
                    applet.store = ResourceStore(folder, folder / 'backups')
                    window = Gtk.OffscreenWindow()
                    try:
                        window.add(applet.createPanel())
                        applet.initUI()
                        window.show_all()
                        self.assertEqual([gas_factory.call_count, bulk_factory.call_count, table_factory.call_count], [0, 0, 0])
                        self.assertEqual(scans.call_count, 0)
                        tabs = applet.notebook
                        tabs.set_current_page(1)
                        gas = applet._page_contents[1]
                        self.assertEqual(len(gas.model), 1)
                        self.assertEqual(scans.call_count, 1)
                        gas.tree.get_selection().select_iter(gas.model.get_iter_first())
                        self.assertIsNotNone(gas.molecule)
                        gas.charge.set_text('-1')
                        tabs.set_current_page(2)
                        bulk = applet.bulk_page
                        bulk.name.set_text('Si')
                        tabs.set_current_page(4)
                        table = applet.element_table
                        table.edited(None, '0', '1.02', 2)
                        self.assertTrue(table.dirty)
                        tabs.set_current_page(3)
                        self.assertFalse(tabs.get_nth_page(3).get_children())
                        (library / 'He.xyz').write_text('1\nHelium\nHe 0 0 0\n')
                        tabs.set_current_page(1)
                        self.assertIs(applet._page_contents[1], gas)
                        self.assertEqual(len(gas.model), 2)
                        self.assertEqual(scans.call_count, 2)
                        self.assertEqual(gas.charge.get_text(), '-1')
                        tabs.set_current_page(2)
                        self.assertIs(applet.bulk_page, bulk)
                        self.assertEqual(bulk.name.get_text(), 'Si')
                        self.assertTrue(bulk.get_parent().get_visible())
                        while Gtk.events_pending():
                            Gtk.main_iteration_do(False)
                        self.assertTrue(bulk.get_mapped())
                        window.get_pixbuf().savev('/tmp/p4vasp-models-lazy-bulk.png', 'png', [], [])
                        tabs.set_current_page(4)
                        self.assertIs(applet.element_table, table)
                        self.assertTrue(table.dirty)
                        self.assertEqual(table.model[0][2], '1.02')
                        self.assertEqual([gas_factory.call_count, bulk_factory.call_count, table_factory.call_count], [1, 1, 1])
                        while Gtk.events_pending():
                            Gtk.main_iteration_do(False)
                        self.assertFalse(errors, errors)
                    finally:
                        window.destroy()
        finally:
            sys.excepthook = original


if __name__ == '__main__':
    unittest.main()

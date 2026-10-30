"""Explicit packaging diagnostic: p4vasp-console.exe --check-runtime OUTPUT_DIR.

Uses only synthetic data. Native worker teardown is deliberately outside this check.
"""
import json
import os
from pathlib import Path
import sys
import time
import traceback


def main(args):
    if len(args) != 1:
        raise SystemExit('Usage: --check-runtime OUTPUT_DIR (new or empty directory)')
    out = Path(args[0]).resolve()
    if out.exists() and any(out.iterdir()):
        raise SystemExit('Runtime check requires a new or empty output directory')
    out.mkdir(parents=True, exist_ok=True)
    report = {'frozen': bool(getattr(sys, 'frozen', False)), 'python': sys.version,
              'executable': sys.executable, 'checks': []}
    result = 1
    try:
        import importlib
        from io import StringIO
        import cp4vasp
        import cairo
        import numpy as np
        from p4vasp.gtk3 import Gtk
        from p4vasp.gtk3.glade import XML
        from p4vasp.applet.appletlist import appletlist
        from p4vasp import p4vasp_home
        from p4vasp.Structure import Structure
        from p4vasp.StructureWindow import StructureWindow
        from p4vasp.util import getAtomtypes
        from p4vasp.export_image import snapshot
        from p4vasp.render_cli import render
        assert Gtk.init_check()[0], 'No GTK display available'
        for name in appletlist():
            importlib.import_module(name.rsplit('.', 1)[0])
        report['checks'].append('all registered applet modules import')
        resources = sorted((Path(p4vasp_home) / 'data/glade2').glob('*.glade'))
        assert len(resources) >= 40, 'Missing packaged Glade resources'
        property_errors = []
        for path in resources:
            xml = XML(str(path))
            property_errors.extend(str(e) for e in xml.property_errors)
            for widget in xml.widgets.values():
                if isinstance(widget, Gtk.Window):
                    widget.destroy()
        report['resource_count'] = len(resources)
        report['resource_property_errors'] = property_errors
        report['checks'].append('Glade resources load (property warnings recorded)')
        from p4vasp.gtk3.file_dialogs import PngSaveDialog, FolderDialog, workarea
        for destination in (PngSaveDialog(None, out), FolderDialog(None, out)):
            dialog = destination.dialog
            dialog.show_all()
            for _ in range(10):
                while Gtk.events_pending():
                    Gtk.main_iteration()
                time.sleep(.02)
            width, height = dialog.get_allocated_width(), dialog.get_allocated_height()
            area = workarea(None)
            assert width <= area.width and height <= area.height
            for response in (Gtk.ResponseType.CANCEL, Gtk.ResponseType.OK):
                button = dialog.get_widget_for_response(response)
                assert button.get_mapped()
                x, y = button.translate_coordinates(dialog, 0, 0)
                assert 0 <= x and x+button.get_allocated_width() <= width
                assert 0 <= y and y+button.get_allocated_height() <= height
            surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
            dialog.draw(cairo.Context(surface))
            surface.write_to_png(str(out/('save-destination.png' if isinstance(destination, PngSaveDialog) else 'folder-browser.png')))
            dialog.destroy()
        report['checks'].append('compact PNG destination/folder dialogs and visible action buttons')
        cp4vasp.VisInit()
        s = Structure()
        s.read(StringIO('Packaged synthetic water\n1\n6 0 0\n0 6 0\n0 0 6\n'
                        'O H\n1 2\nSelective dynamics\nCartesian\n'
                        '0 0 0 F F F\n1.2 0 0 T T T\n0 1.2 0 T T T\n'))
        window = StructureWindow(w=600, h=450, atomtypes=getAtomtypes())
        window.setStructure(s)
        for _ in range(30):
            cp4vasp.VisCheck()
            while Gtk.events_pending():
                Gtk.main_iteration()
            time.sleep(.02)
        window.win.saveScreenshot(str(out / 'native.tga'))
        raw = (out / 'native.tga').read_bytes()
        w, h = int.from_bytes(raw[12:14], 'little'), int.from_bytes(raw[14:16], 'little')
        rgb = np.frombuffer(raw[18:], dtype=np.uint8).reshape(h, w, 3)[::-1, :, ::-1]
        assert (np.max(rgb, axis=2) - np.min(rgb, axis=2) > 15).sum() > 100
        pixels = np.ascontiguousarray(0xff000000 | rgb[:, :, 0].astype(np.uint32) << 16 |
                                     rgb[:, :, 1].astype(np.uint32) << 8 |
                                     rgb[:, :, 2].astype(np.uint32))
        cairo.ImageSurface.create_for_data(pixels, cairo.FORMAT_ARGB32, w, h, w * 4).write_to_png(str(out / 'native.png'))
        render(None, out / 'export.png', **snapshot(window), size=(600, 450))
        from p4vasp.render_recipe import DEFAULTS, make, bundle_paths, save_bundle
        state = snapshot(window)
        recipe = make(state['camera'], dict(DEFAULTS, size=(600, 450)),
                      dict(repeat=[1, 1, 1], hidden=[]))
        paths = bundle_paths(out / "replay ' & % 测试.png")
        replay = save_bundle(paths, out / 'replay.png', state['scene'][:3], recipe)
        report['replay_command'] = replay
        report['replay_script'] = str(paths[2])
        s.write(str(out / 'POSCAR'))
        restored = Structure()
        restored.read(str(out / 'POSCAR'))
        assert len(restored) == 3 and list(restored.selective[0]) == [False] * 3
        window.hide()
        report['checks'].append('native drawing, camera PNG, POSCAR selective flags')
        report['ok'] = True
        result = 0
    except BaseException:
        report['ok'] = False
        report['error'] = traceback.format_exc()
    (out / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(report), flush=True)
    os._exit(result)


def prepare_gui_check(args):
    """Arm a bounded startup check, then let the real application initialize."""
    if len(args) != 1:
        raise SystemExit('Usage: --check-gui OUTPUT_DIR (new or empty directory)')
    out = Path(args[0]).resolve()
    if out.exists() and any(out.iterdir()):
        raise SystemExit('GUI check requires a new or empty output directory')
    out.mkdir(parents=True, exist_ok=True)
    (out / 'POSCAR').write_text('Packaged GUI check\n1\n6 0 0\n0 6 0\n0 0 6\nH\n1\nCartesian\n0 0 0\n')
    sys.argv[1:] = [str(out / 'POSCAR')]
    from p4vasp.gtk3 import Gtk, Gdk, GLib
    errors = []
    original_hook = sys.excepthook
    def capture(*exception):
        errors.append(''.join(traceback.format_exception(*exception)))
        original_hook(*exception)
    sys.excepthook = capture
    def done():
        result = {'frozen': bool(getattr(sys, 'frozen', False))}
        status = 1
        try:
            assert not errors, '\n'.join(errors)
            windows = [w for w in Gtk.Window.list_toplevels() if w.get_visible() and w.get_window()]
            assert windows, 'Main window did not become visible'
            window = max(windows, key=lambda w: w.get_allocated_width()*w.get_allocated_height())
            w, h = window.get_allocated_width(), window.get_allocated_height()
            assert w > 300 and h > 200
            Gdk.pixbuf_get_from_window(window.get_window(), 0, 0, w, h).savev(str(out/'main.png'), 'png', [], [])
            result.update(ok=True, width=w, height=h)
            status = 0
        except BaseException:
            result.update(ok=False, error=traceback.format_exc())
        (out/'report.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
        print(json.dumps(result), flush=True)
        os._exit(status)
    GLib.timeout_add_seconds(8, done)

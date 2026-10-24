"""Actual GTK/native window export check. Requires a display and compiled extension."""
import os
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'lib'), str(ROOT/'src')]
os.environ['P4VASP_HOME'] = str(ROOT)
from p4vasp.gtk3 import Gtk, Gdk, GLib
from p4vasp.Structure import Structure
from p4vasp.StructureWindow import StructureWindow
from p4vasp.export_image import snapshot, ExportImageDialog
from p4vasp.render_cli import camera_point, perspective_factor, render
import cairo
import cp4vasp
from io import StringIO


def pump_until(predicate):
    deadline = time.monotonic()+15
    while not predicate():
        while Gtk.events_pending(): Gtk.main_iteration()
        if time.monotonic() > deadline: raise AssertionError('GUI export timed out')
        time.sleep(.01)
    while Gtk.events_pending(): Gtk.main_iteration()


def main():
    cp4vasp.VisInit()
    structure = Structure()
    structure.read(StringIO('Asymmetric test\n1\n6 0 0\n0 6 0\n0 0 6\nO H\n1 2\nCartesian\n0 0 0\n1.5 0 1\n0 2 0\n'))
    window = StructureWindow(w=500, h=400)
    window.setStructure(structure)
    window.navigator.setFrontView()
    window.navigator.setZoom(2)
    window.setMultiple(2, 1, 1)
    window.setHiddenAtoms([2])
    assert "p4vasp.render_studio" not in sys.modules, "Studio renderer loaded during interactive setup"
    state = snapshot(window)
    assert len(state['scene'][1]) == 4
    assert state['camera']['zoom'] == 2
    expected = [[window.navigator.getRotMatElement(i,j) for j in range(4)] for i in range(4)]
    assert state['camera']['matrix'] == expected
    # Check a non-symmetric matrix, translation and zoom (guards transposition).
    camera = dict(matrix=[[0,-1,0,3],[0,0,1,4],[-1,0,0,5],[0,0,0,1]], zoom=2)
    assert camera_point((1,2,3), camera) == (-1,10,3)
    with tempfile.TemporaryDirectory() as folder:
        from p4vasp.applet.StructureWindowControlApplet import StructureWindowControlApplet
        from p4vasp.gtk3.glade import XML
        control = StructureWindowControlApplet()
        control.swin = lambda: window
        xml = XML(str(ROOT/'data/glade2/swincontrol.glade'), 'applet_frame')
        button = xml.get_widget('foto_button')
        assert button.get_label() == 'Export PNG'
        button.connect('clicked', control.on_foto_button_clicked_handler)
        button.emit('clicked')
        dialog = control.image_export_dialog
        pump_until(lambda: not dialog.busy)
        assert dialog.preview.get_pixbuf() is not None, dialog.status.get_text()
        assert dialog.material.get_active_text() == 'matte'
        assert dialog.save.get_allocation().width > 20
        assert dialog.preview.get_allocation().height > 20
        # Rotate after opening: export must capture the new view, not the preview snapshot.
        window.navigator.setTopView()
        output = str(Path(folder)/'export.png')
        dialog.width.set_value(500)
        dialog.start(output)
        pump_until(lambda: not dialog.busy)
        assert Path(output).exists(), dialog.status.get_text()
        surface = cairo.ImageSurface.create_from_png(output)
        assert (surface.get_width(), surface.get_height()) == (500,400)
        assert bytes(surface.get_data()[:4]) == bytes(4)
        expected_png = str(Path(folder)/'expected.png')
        render(None, expected_png, **snapshot(window), size=(500,400))
        assert Path(output).read_bytes() == Path(expected_png).read_bytes()
        # Perspective uses the native frustum and keeps the viewport aspect ratio.
        window.navigator.setPerspective(1)
        perspective = snapshot(window)
        assert perspective['camera']['perspective']
        assert perspective_factor((0,0,0), perspective['camera']) == .5
        assert perspective_factor((0,0,5), perspective['camera']) == 2/3
        dialog.start(output)
        pump_until(lambda: not dialog.busy)
        assert 'Saved:' in dialog.status.get_text()
        window.navigator.setPerspective(0)
        # A higher-quality export must leave the GTK event loop responsive.
        ticks = []
        timer = GLib.timeout_add(10, lambda: (ticks.append(time.monotonic()) or True))
        dialog.width.set_value(900); dialog.quality.set_value(3)
        dialog.start(output)
        pump_until(lambda: not dialog.busy)
        GLib.source_remove(timer)
        assert ticks, 'GTK did not service timers during export'
        assert 'Saved:' in dialog.status.get_text()
        dialog.width.set_value(500); dialog.quality.set_value(2)
        # Errors remain visible and leave the dialog usable.
        dialog.start(str(Path(folder)/'missing'/'file.png'))
        pump_until(lambda: not dialog.busy)
        assert 'failed' in dialog.status.get_text()
        assert dialog.save.get_sensitive()
        dialog.start()
        pump_until(lambda: not dialog.busy)
        settled = time.monotonic()+.3
        pump_until(lambda: time.monotonic() >= settled)
        # Render the allocated GTK widget tree (independent of compositor capture).
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, dialog.dialog.get_allocated_width(), dialog.dialog.get_allocated_height())
        dialog.dialog.draw(cairo.Context(surface))
        surface.write_to_png('/tmp/p4v-export-dialog.png')
        # Closing the panel cancels a pending render and preserves an old output.
        Path(output).write_bytes(b'keep previous output')
        dialog.width.set_value(1600); dialog.quality.set_value(3)
        dialog.start(output)
        dialog.dialog.destroy()
        pump_until(lambda: not dialog.busy)
        assert Path(output).read_bytes() == b'keep previous output'
    print('PASS: native camera, hidden/replicated atoms, GTK preview, latest-view export, alpha, error recovery; %d GTK timer ticks during export' % len(ticks), flush=True)


if __name__ == '__main__':
    try:
        main()
    except BaseException:
        import traceback
        traceback.print_exc()
        os._exit(1)
    # Native FLTK worker teardown is outside this isolated UI check.
    os._exit(0)

"""Real GTK rendering, font coverage, clipboard and QR viewer checks."""
from pathlib import Path
from p4vasp.gtk3 import Gtk, Gdk, GdkPixbuf
from p4vasp.gtk3.community import CommunityPage, QRViewer, CONTACTS

assert Gtk.init_check()[0]
def drain():
    while Gtk.events_pending():
        Gtk.main_iteration()

window = Gtk.Window()
window.set_default_size(800, 480)
page = CommunityPage(lambda: window)
window.add(page)
window.show_all()
drain()
assert len(page.buttons) == 3
assert page.create_pango_layout('交流与支持 微信 微信公众号 群号 关闭 适应窗口 查看原图').get_unknown_glyphs_count() == 0
page.copy_button.clicked()
assert Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD).wait_for_text() == '1131610080'
root = Path(__file__).resolve().parents[1]
for title, detail, filename, crop in CONTACTS:
    original = GdkPixbuf.Pixbuf.new_from_file(str(root/'data/community'/filename))
    if crop:
        x, y, w, h = crop
        assert x >= 0 and y >= 0 and x+w <= original.get_width() and y+h <= original.get_height()
    viewer = QRViewer(window, title, original, crop)
    drain()
    viewer.zoom(1)
    assert viewer.image.get_pixbuf().get_width() == (crop[2] if crop else original.get_width())
    viewer.full.set_active(True)
    viewer.zoom(1)
    assert viewer.image.get_pixbuf().get_height() == original.get_height()
    viewer.fit()
    drain()
    if filename == 'qq.jpg':
        win = viewer.get_window()
        Gdk.pixbuf_get_from_window(win, 0, 0, viewer.get_allocated_width(), viewer.get_allocated_height()).savev('/tmp/p4vasp-community-viewer.png', 'png', [], [])
    viewer.destroy()
drain()
win = window.get_window()
Gdk.pixbuf_get_from_window(win, 0, 0, window.get_allocated_width(), window.get_allocated_height()).savev('/tmp/p4vasp-community.png', 'png', [], [])
window.resize(420, 400)
from gi.repository import GLib
loop = GLib.MainLoop()
GLib.timeout_add(200, lambda: (loop.quit(), False)[1])
loop.run()
drain()
assert page.get_allocated_width() <= 420
window.destroy()
print('Community GTK: Chinese glyphs, three QR images, crop bounds, clipboard, zoom/original and narrow layout passed')

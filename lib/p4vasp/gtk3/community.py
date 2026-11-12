"""User-supplied community QR images; originals are never rewritten."""
import ctypes
import ctypes.util
import sys
from pathlib import Path

import p4vasp
from p4vasp.gtk3 import Gtk, Gdk, GdkPixbuf
from p4vasp.gtk3.file_dialogs import fit_dialog, workarea

_font_loaded = False


def load_chinese_font():
    """Register the bundled OFL font for this process, without installing it."""
    global _font_loaded
    if _font_loaded:
        return
    if sys.platform == 'darwin':
        # Quartz uses PangoCoreTextFontMap, not PangoFcFontMap. Passing it to
        # pango_fc_* can crash the process; use macOS's system CJK fonts.
        _font_loaded = True
        return
    path = Path(p4vasp.p4vasp_home)/'data/fonts/NotoSansSC-Regular.otf'
    try:
        if not path.is_file():
            return
        if sys.platform == 'win32':
            loaded = ctypes.windll.gdi32.AddFontResourceExW(str(path), 0x10, None)
        else:
            library = ctypes.util.find_library('fontconfig')
            if not library:
                return
            fc = ctypes.CDLL(library)
            fc.FcConfigGetCurrent.restype = ctypes.c_void_p
            fc.FcConfigAppFontAddFile.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
            fc.FcConfigAppFontAddFile.restype = ctypes.c_int
            fc.FcConfigBuildFonts.argtypes = [ctypes.c_void_p]
            config = fc.FcConfigGetCurrent()
            loaded = fc.FcConfigAppFontAddFile(config, bytes(path))
            if loaded:
                fc.FcConfigBuildFonts(config)
        if loaded:
            import gi
            gi.require_version('PangoCairo', '1.0')
            from gi.repository import PangoCairo
            font_map = PangoCairo.FontMap.get_default()
            if sys.platform != 'win32':
                # Pango may own a separate FcConfig once GTK has rendered text.
                # Register against that config too, then invalidate its font cache.
                cairo = ctypes.CDLL(ctypes.util.find_library('pangocairo-1.0'))
                cairo.pango_cairo_font_map_get_default.restype = ctypes.c_void_p
                native_map = cairo.pango_cairo_font_map_get_default()
                pango_fc = ctypes.CDLL(ctypes.util.find_library('pangoft2-1.0'))
                pango_fc.pango_fc_font_map_get_config.argtypes = [ctypes.c_void_p]
                pango_fc.pango_fc_font_map_get_config.restype = ctypes.c_void_p
                pango_fc.pango_fc_font_map_config_changed.argtypes = [ctypes.c_void_p]
                pango_config = pango_fc.pango_fc_font_map_get_config(native_map)
                if pango_config and pango_config != config:
                    fc.FcConfigAppFontAddFile(pango_config, bytes(path))
                    fc.FcConfigBuildFonts(pango_config)
                pango_fc.pango_fc_font_map_config_changed(native_map)
            else:
                font_map.changed()
            _font_loaded = True
    except (OSError, AttributeError):
        pass  # Existing system font fallback remains available.


CONTACTS = (
    ('QQ群', 'p4vasp · 群号 1131610080', 'qq.jpg', (215, 850, 855, 855)),
    ('微信', 'BigBroSci · 扫码添加微信', 'wechat.jpg', (120, 360, 870, 870)),
    ('微信公众号', '扫码关注公众号', 'public-account.jpg', None),
)


def qr_image(original, crop):
    return original.new_subpixbuf(*crop) if crop else original


def scaled(pixbuf, scale):
    return pixbuf.scale_simple(max(1, round(pixbuf.get_width()*scale)),
                              max(1, round(pixbuf.get_height()*scale)),
                              GdkPixbuf.InterpType.NEAREST)


class QRViewer(Gtk.Dialog):
    def __init__(self, parent, title, original, crop):
        super().__init__(title=title, transient_for=parent, destroy_with_parent=True)
        self.original, self.crop = original, crop
        self.scale = 1.0
        self.add_button('关闭', Gtk.ResponseType.CLOSE)
        self.connect('response', lambda *_: self.destroy())
        fit_dialog(self, parent, 620, 680)
        box = self.get_content_area()
        controls = Gtk.Box(spacing=6)
        for title, action in [('适应窗口', self.fit), ('100%', lambda: self.zoom(1)),
                              ('−', lambda: self.zoom(self.scale/1.25)),
                              ('+', lambda: self.zoom(self.scale*1.25))]:
            button = Gtk.Button(label=title)
            button.connect('clicked', lambda _, action=action: action())
            controls.pack_start(button, False, False, 0)
        self.full = Gtk.CheckButton(label='查看原图')
        self.full.connect('toggled', lambda *_: self.fit())
        controls.pack_start(self.full, False, False, 0)
        box.pack_start(controls, False, False, 6)
        self.image = Gtk.Image()
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll.add(self.image)
        box.pack_start(scroll, True, True, 0)
        self.fit()
        self.show_all()

    def source(self):
        return self.original if self.full.get_active() else qr_image(self.original, self.crop)

    def zoom(self, scale):
        self.scale = max(0.05, min(4.0, scale))
        self.image.set_from_pixbuf(scaled(self.source(), self.scale))

    def fit(self):
        area = workarea(None)
        source = self.source()
        self.zoom(min(1, min(560, max(160, area.width-100))/source.get_width(),
                      min(500, max(120, area.height-240))/source.get_height()))


class CommunityPage(Gtk.ScrolledWindow):
    def __init__(self, parent_window):
        super().__init__()
        load_chinese_font()
        self.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.buttons = []
        self.parent_window = parent_window
        flow = Gtk.FlowBox()
        flow.set_selection_mode(Gtk.SelectionMode.NONE)
        flow.set_min_children_per_line(1)
        flow.set_max_children_per_line(3)
        flow.set_column_spacing(12)
        flow.set_row_spacing(12)
        flow.set_border_width(12)
        for title, detail, filename, crop in CONTACTS:
            card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
            card.pack_start(Gtk.Label(label=title), False, False, 0)
            caption = Gtk.Label(label=detail)
            caption.set_selectable(True)
            caption.set_line_wrap(True)
            caption.set_max_width_chars(22)
            card.pack_start(caption, False, False, 0)
            try:
                original = GdkPixbuf.Pixbuf.new_from_file(str(Path(p4vasp.p4vasp_home)/'data/community'/filename))
                qr = qr_image(original, crop)
                button = Gtk.Button()
                button.add(Gtk.Image.new_from_pixbuf(scaled(qr, 200/qr.get_width())))
                button.set_tooltip_text('点击放大二维码；可查看原图')
                button.connect('clicked', lambda _, title=title, original=original, crop=crop:
                               QRViewer(self.parent_window(), title, original, crop))
                card.pack_start(button, False, False, 0)
                self.buttons.append(button)
            except Exception:
                card.pack_start(Gtk.Label(label='二维码图片无法读取'), False, False, 0)
            if filename == 'qq.jpg':
                copy = Gtk.Button(label='复制群号')
                copy.connect('clicked', self.copy_qq)
                self.copy_button = copy
                card.pack_start(copy, False, False, 0)
            flow.add(card)
        self.add(flow)

    def copy_qq(self, button):
        try:
            clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
            clipboard.set_text('1131610080', -1)
            clipboard.store()
            button.set_label('群号已复制')
        except Exception:
            button.set_label('请复制群号：1131610080')

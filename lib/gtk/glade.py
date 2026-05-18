"""Minimal libglade-compatible loader for p4vasp's Glade 2 XML files."""

import os
import xml.etree.ElementTree as ET

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gdk, Gtk

import gtk


_BOOLS = {"true": True, "false": False, "yes": True, "no": False}
_INT_PROPS = {
    "border_width",
    "column_spacing",
    "default_height",
    "default_width",
    "height_request",
    "left_attach",
    "max_length",
    "n_columns",
    "n_rows",
    "padding",
    "position",
    "right_attach",
    "row_spacing",
    "spacing",
    "top_attach",
    "width_chars",
    "width_request",
    "xpad",
    "x_padding",
    "ypad",
    "y_padding",
}
_FLOAT_PROPS = {"value", "lower", "upper", "step_increment", "page_increment", "xalign", "yalign"}


def _text(node):
    return node.text or ""


def _properties(elem):
    return {child.attrib.get("name"): _text(child) for child in elem if child.tag == "property"}


def _bool(value):
    return _BOOLS.get(value.strip().lower(), False)


def _enum(value):
    value = (value or "").strip()
    enums = {
        "GTK_BUTTONBOX_END": Gtk.ButtonBoxStyle.END,
        "GTK_BUTTONBOX_START": Gtk.ButtonBoxStyle.START,
        "GTK_BUTTONBOX_CENTER": Gtk.ButtonBoxStyle.CENTER,
        "GTK_BUTTONBOX_EDGE": Gtk.ButtonBoxStyle.EDGE,
        "GTK_FILE_CHOOSER_ACTION_OPEN": Gtk.FileChooserAction.OPEN,
        "GTK_JUSTIFY_CENTER": Gtk.Justification.CENTER,
        "GTK_JUSTIFY_FILL": Gtk.Justification.FILL,
        "GTK_JUSTIFY_LEFT": Gtk.Justification.LEFT,
        "GTK_JUSTIFY_RIGHT": Gtk.Justification.RIGHT,
        "GTK_ORIENTATION_HORIZONTAL": Gtk.Orientation.HORIZONTAL,
        "GTK_ORIENTATION_VERTICAL": Gtk.Orientation.VERTICAL,
        "GTK_PACK_END": Gtk.PackType.END,
        "GTK_PACK_START": Gtk.PackType.START,
        "GTK_POLICY_ALWAYS": Gtk.PolicyType.ALWAYS,
        "GTK_POLICY_AUTOMATIC": Gtk.PolicyType.AUTOMATIC,
        "GTK_POLICY_NEVER": Gtk.PolicyType.NEVER,
        "GTK_POS_BOTTOM": Gtk.PositionType.BOTTOM,
        "GTK_POS_LEFT": Gtk.PositionType.LEFT,
        "GTK_POS_RIGHT": Gtk.PositionType.RIGHT,
        "GTK_POS_TOP": Gtk.PositionType.TOP,
        "GTK_RELIEF_HALF": Gtk.ReliefStyle.HALF,
        "GTK_RELIEF_NONE": Gtk.ReliefStyle.NONE,
        "GTK_RELIEF_NORMAL": Gtk.ReliefStyle.NORMAL,
        "GTK_SHADOW_ETCHED_IN": Gtk.ShadowType.ETCHED_IN,
        "GTK_SHADOW_ETCHED_OUT": Gtk.ShadowType.ETCHED_OUT,
        "GTK_SHADOW_IN": Gtk.ShadowType.IN,
        "GTK_SHADOW_NONE": Gtk.ShadowType.NONE,
        "GTK_SHADOW_OUT": Gtk.ShadowType.OUT,
        "GTK_TOOLBAR_BOTH": Gtk.ToolbarStyle.BOTH,
        "GTK_TOOLBAR_BOTH_HORIZ": Gtk.ToolbarStyle.BOTH_HORIZ,
        "GTK_TOOLBAR_ICONS": Gtk.ToolbarStyle.ICONS,
        "GTK_TOOLBAR_TEXT": Gtk.ToolbarStyle.TEXT,
        "GTK_WINDOW_POPUP": Gtk.WindowType.POPUP,
        "GTK_WINDOW_TOPLEVEL": Gtk.WindowType.TOPLEVEL,
        "GTK_WIN_POS_CENTER": Gtk.WindowPosition.CENTER,
        "GTK_WIN_POS_NONE": Gtk.WindowPosition.NONE,
        "GTK_WRAP_NONE": Gtk.WrapMode.NONE,
        "GTK_WRAP_WORD": Gtk.WrapMode.WORD,
        "GTK_WRAP_CHAR": Gtk.WrapMode.CHAR,
        "GTK_WRAP_WORD_CHAR": Gtk.WrapMode.WORD_CHAR,
    }
    aliases = {
        "both": Gtk.ToolbarStyle.BOTH,
        "both-horiz": Gtk.ToolbarStyle.BOTH_HORIZ,
        "center": Gtk.ButtonBoxStyle.CENTER,
        "edge": Gtk.ButtonBoxStyle.EDGE,
        "end": Gtk.ButtonBoxStyle.END,
        "horizontal": Gtk.Orientation.HORIZONTAL,
        "icons": Gtk.ToolbarStyle.ICONS,
        "left": Gtk.PositionType.LEFT,
        "right": Gtk.PositionType.RIGHT,
        "start": Gtk.ButtonBoxStyle.START,
        "text": Gtk.ToolbarStyle.TEXT,
        "top": Gtk.PositionType.TOP,
        "bottom": Gtk.PositionType.BOTTOM,
        "vertical": Gtk.Orientation.VERTICAL,
    }
    if value.lower() in aliases:
        return aliases[value.lower()]
    return enums.get(value, value)


def _events(value):
    masks = {
        "GDK_BUTTON_PRESS_MASK": Gdk.EventMask.BUTTON_PRESS_MASK,
        "GDK_BUTTON_RELEASE_MASK": Gdk.EventMask.BUTTON_RELEASE_MASK,
        "GDK_KEY_PRESS_MASK": Gdk.EventMask.KEY_PRESS_MASK,
        "GDK_KEY_RELEASE_MASK": Gdk.EventMask.KEY_RELEASE_MASK,
        "GDK_POINTER_MOTION_MASK": Gdk.EventMask.POINTER_MOTION_MASK,
        "GDK_BUTTON_MOTION_MASK": Gdk.EventMask.BUTTON_MOTION_MASK,
        "GDK_BUTTON1_MOTION_MASK": Gdk.EventMask.BUTTON1_MOTION_MASK,
        "GDK_BUTTON2_MOTION_MASK": Gdk.EventMask.BUTTON2_MOTION_MASK,
        "GDK_BUTTON3_MOTION_MASK": Gdk.EventMask.BUTTON3_MOTION_MASK,
    }
    result = 0
    for part in value.split("|"):
        result |= int(masks.get(part.strip(), 0))
    return Gdk.EventMask(result)


def _attach_options(value):
    raw = (value or "").strip()
    if not raw:
        return Gtk.AttachOptions(0)
    result = Gtk.AttachOptions(0)
    for part in raw.replace("|", " ").split():
        token = part.strip().upper()
        if token in ("GTK_FILL", "FILL"):
            result |= Gtk.AttachOptions.FILL
        elif token in ("GTK_EXPAND", "EXPAND"):
            result |= Gtk.AttachOptions.EXPAND
        elif token in ("GTK_SHRINK", "SHRINK"):
            result |= Gtk.AttachOptions.SHRINK
    return result


def _value(name, value):
    if value is None:
        return None
    raw = value.strip()
    if raw.lower() in _BOOLS:
        return _bool(raw)
    if name in _INT_PROPS:
        try:
            return int(raw)
        except ValueError:
            return 0
    if name in _FLOAT_PROPS:
        try:
            return float(raw)
        except ValueError:
            return 0.0
    if raw.startswith("GTK_") or name in ("layout_style", "orientation", "toolbar_style"):
        return _enum(raw)
    if name == "events":
        return _events(raw)
    return value


def _image_path(glade_path, icon):
    if not icon:
        return None
    candidates = [
        os.path.join(os.path.dirname(glade_path), icon),
        os.path.join(os.path.dirname(os.path.dirname(glade_path)), icon),
        os.path.join(os.path.dirname(os.path.dirname(glade_path)), "pixmaps", icon),
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return None


class XML:
    def __init__(self, path, root=None):
        self.path = path
        self.root_name = root
        self.widgets = {}
        self._signals = []
        data = open(path, "rb").read()
        text = data.decode("utf-8", "replace")
        self.document = ET.fromstring(text)
        self._build(root)

    def get_widget(self, name):
        return self.widgets.get(name)

    def get_widget_prefix(self, prefix):
        return [widget for name, widget in self.widgets.items() if name.startswith(prefix)]

    def signal_connect(self, handler_name, callback):
        for widget, signal, handler, obj_name in self._signals:
            if handler == handler_name:
                self._connect(widget, signal, callback, obj_name)

    def signal_autoconnect(self, handlers):
        for widget, signal, handler, obj_name in self._signals:
            callback = handlers.get(handler) if hasattr(handlers, "get") else getattr(handlers, handler, None)
            if callback is not None:
                self._connect(widget, signal, callback, obj_name)

    def _connect(self, widget, signal, callback, obj_name):
        signal = signal.replace("_", "-")
        obj = self.widgets.get(obj_name) if obj_name else None
        if obj is None:
            wrapper = callback
        else:
            wrapper = lambda _widget, *args, _callback=callback, _obj=obj: _callback(_obj)
        try:
            widget.connect(signal, wrapper)
        except TypeError:
            widget.connect(signal.replace("-", "_"), wrapper)

    def _build(self, root_name):
        if root_name is None:
            elems = [child for child in self.document if child.tag == "widget"]
        else:
            target = self._find_widget_elem(root_name)
            elems = [target] if target is not None else []
        for elem in elems:
            self._build_widget(elem)

    def _find_widget_elem(self, name):
        for elem in self.document.iter("widget"):
            if elem.attrib.get("id") == name:
                return elem
        return None

    def _build_widget(self, elem, parent=None, internal_child=None):
        class_name = elem.attrib.get("class")
        widget_id = elem.attrib.get("id")
        widget = self._new_widget(class_name, elem, parent, internal_child)
        if widget is None:
            return None
        if widget_id:
            widget.set_name(widget_id)
            self.widgets[widget_id] = widget
        props = _properties(elem)
        self._apply_properties(widget, props)
        for signal in elem.findall("signal"):
            self._signals.append(
                (
                    widget,
                    signal.attrib.get("name", ""),
                    signal.attrib.get("handler", ""),
                    signal.attrib.get("object"),
                )
            )
        for child in elem.findall("child"):
            child_widget_elem = child.find("widget")
            if child_widget_elem is None:
                continue
            built_child = self._build_widget(
                child_widget_elem,
                parent=widget,
                internal_child=child.attrib.get("internal-child"),
            )
            if built_child is not None:
                self._add_child(widget, built_child, child)
        if props.get("visible", "False").strip().lower() == "true":
            widget.show()
        return widget

    def _new_widget(self, class_name, elem, parent=None, internal_child=None):
        props = _properties(elem)
        if isinstance(parent, gtk.FileSelection):
            if internal_child == "ok_button":
                return parent.ok_button
            if internal_child == "cancel_button":
                return parent.cancel_button
        if isinstance(parent, gtk.Combo) and internal_child == "entry":
            return parent.entry
        if isinstance(parent, gtk.Combo):
            return None
        if class_name in ("GtkWindow",):
            return Gtk.Window()
        if class_name == "GtkDialog":
            return Gtk.Dialog()
        if class_name == "GtkFileSelection":
            title = props.get("title", "")
            return gtk.FileSelection(title=title)
        if class_name in ("GtkVBox",):
            return Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        if class_name in ("GtkHBox",):
            return Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        if class_name == "GtkHButtonBox":
            return Gtk.ButtonBox(orientation=Gtk.Orientation.HORIZONTAL)
        if class_name == "GtkFrame":
            return Gtk.Frame()
        if class_name == "GtkAlignment":
            return Gtk.Alignment()
        if class_name == "GtkTable":
            rows = int(props.get("n_rows", "1") or 1)
            cols = int(props.get("n_columns", "1") or 1)
            return Gtk.Table(n_rows=rows, n_columns=cols)
        if class_name == "GtkHPaned":
            return Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        if class_name == "GtkVPaned":
            return Gtk.Paned(orientation=Gtk.Orientation.VERTICAL)
        if class_name == "GtkScrolledWindow":
            return Gtk.ScrolledWindow()
        if class_name == "GtkViewport":
            return Gtk.Viewport()
        if class_name in ("GtkText", "GtkTextView"):
            return gtk.Text()
        if class_name == "GtkEntry":
            return Gtk.Entry()
        if class_name == "GtkLabel":
            return Gtk.Label()
        if class_name == "GtkButton":
            return Gtk.Button()
        if class_name == "GtkCheckButton":
            return Gtk.CheckButton()
        if class_name == "GtkRadioButton":
            return Gtk.RadioButton()
        if class_name == "GtkHScale":
            return Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL)
        if class_name == "GtkSpinButton":
            return Gtk.SpinButton()
        if class_name == "GtkProgressBar":
            return Gtk.ProgressBar()
        if class_name == "GtkMenuBar":
            return Gtk.MenuBar()
        if class_name == "GtkMenu":
            return gtk.Menu()
        if class_name == "GtkMenuItem":
            return gtk.MenuItem()
        if class_name == "GtkImageMenuItem":
            return gtk.ImageMenuItem()
        if class_name == "GtkOptionMenu":
            return gtk.OptionMenu()
        if class_name == "GtkToolbar":
            return Gtk.Toolbar()
        if class_name in ("GtkToolButton", "button"):
            return Gtk.ToolButton()
        if class_name == "GtkImage":
            return Gtk.Image()
        if class_name == "GtkDrawingArea":
            return Gtk.DrawingArea()
        if class_name == "GtkNotebook":
            return Gtk.Notebook()
        if class_name == "GtkStatusbar":
            return Gtk.Statusbar()
        if class_name == "GtkTreeView":
            return Gtk.TreeView()
        if class_name == "GtkCombo":
            return gtk.Combo()
        if class_name == "GtkComboBox":
            return Gtk.ComboBoxText()
        if class_name == "GtkList":
            return Gtk.ListBox()
        return Gtk.Box()

    def _apply_properties(self, widget, props):
        icon = props.get("icon") or props.get("pixbuf") or props.get("filename")
        icon_path = _image_path(self.path, icon)
        for name, raw in props.items():
            value = _value(name, raw)
            try:
                if name == "title" and hasattr(widget, "set_title"):
                    widget.set_title(value)
                elif name == "label" and hasattr(widget, "set_label"):
                    widget.set_label(value)
                elif name == "text":
                    self._set_text(widget, value)
                elif name in ("editable", "visibility", "selectable", "wrap", "use_markup"):
                    setter = getattr(widget, "set_" + name, None)
                    if setter:
                        setter(value)
                elif name in ("xalign", "yalign") and isinstance(widget, Gtk.Label):
                    widget.set_alignment(float(props.get("xalign", 0.5)), float(props.get("yalign", 0.5)))
                elif name == "border_width":
                    widget.set_border_width(value)
                elif name == "row_spacing" and isinstance(widget, Gtk.Table):
                    widget.set_row_spacings(value)
                elif name == "column_spacing" and isinstance(widget, Gtk.Table):
                    widget.set_col_spacings(value)
                elif name == "default_width" and hasattr(widget, "set_default_size"):
                    widget.set_default_size(value, int(props.get("default_height", -1) or -1))
                elif name == "default_height":
                    pass
                elif name == "width_request":
                    widget.set_size_request(value, widget.get_allocated_height() or -1)
                elif name == "height_request":
                    widget.set_size_request(widget.get_allocated_width() or -1, value)
                elif name == "events":
                    widget.set_events(value)
                elif name == "tooltip":
                    widget.set_tooltip_text(value)
                elif name == "orientation" and hasattr(widget, "set_orientation"):
                    widget.set_orientation(value)
                elif name == "toolbar_style" and hasattr(widget, "set_style"):
                    widget.set_style(value)
                elif name == "show_arrow" and hasattr(widget, "set_show_arrow"):
                    widget.set_show_arrow(value)
                elif name == "group" and isinstance(widget, Gtk.RadioButton):
                    group_widget = self.widgets.get((raw or "").strip())
                    if isinstance(group_widget, Gtk.RadioButton):
                        widget.join_group(group_widget)
                elif name == "stock" and isinstance(widget, Gtk.Image):
                    widget.set_from_icon_name(value.replace("gtk-", ""), Gtk.IconSize.MENU)
                elif name == "stock_id" and hasattr(widget, "set_stock_id"):
                    widget.set_stock_id(value)
                elif name == "icon" and isinstance(widget, Gtk.ToolButton) and icon_path:
                    img = Gtk.Image.new_from_file(icon_path)
                    widget.set_icon_widget(img)
                    img.show()
                elif name == "history" and hasattr(widget, "set_history"):
                    widget.set_history(value)
                else:
                    setter = getattr(widget, "set_" + name, None)
                    if setter:
                        setter(value)
            except Exception:
                pass
        if isinstance(widget, Gtk.Image) and icon_path:
            widget.set_from_file(icon_path)

    def _set_text(self, widget, value):
        if isinstance(widget, Gtk.TextView):
            widget.get_buffer().set_text(value or "")
        elif hasattr(widget, "set_text"):
            widget.set_text(value or "")

    def _add_child(self, parent, child, child_elem):
        internal = child_elem.attrib.get("internal-child")
        packing = _properties(child_elem.find("packing") or ET.Element("packing"))
        if isinstance(parent, gtk.FileSelection):
            return
        if isinstance(parent, gtk.Combo) and child is parent.entry:
            return
        if isinstance(parent, Gtk.Frame) and (
            child_elem.attrib.get("type") == "label" or child_elem.attrib.get("internal-child") == "label"
        ):
            parent.set_label_widget(child)
            return
        if isinstance(parent, Gtk.Frame) and isinstance(child, Gtk.Label) and parent.get_child() is not None:
            parent.set_label_widget(child)
            return
        if isinstance(parent, gtk.OptionMenu) and isinstance(child, Gtk.Menu):
            parent.set_menu(child)
            return
        if isinstance(parent, Gtk.ImageMenuItem) and internal == "image":
            parent.set_image(child)
            return
        if isinstance(parent, Gtk.MenuItem) and isinstance(child, Gtk.Menu):
            parent.set_submenu(child)
            return
        if isinstance(parent, (Gtk.Menu, Gtk.MenuBar)):
            parent.append(child)
            return
        if isinstance(parent, Gtk.Toolbar):
            if isinstance(child, Gtk.ToolItem):
                parent.insert(child, -1)
            else:
                item = Gtk.ToolItem()
                item.add(child)
                parent.insert(item, -1)
            return
        if isinstance(parent, Gtk.Dialog):
            parent.get_content_area().pack_start(child, True, True, 0)
            return
        if isinstance(parent, Gtk.Box):
            expand = _bool(packing.get("expand", "True"))
            fill = _bool(packing.get("fill", "True"))
            padding = int(packing.get("padding", "0") or 0)
            pack_type = packing.get("pack_type", "GTK_PACK_START")
            if pack_type == "GTK_PACK_END":
                parent.pack_end(child, expand, fill, padding)
            else:
                parent.pack_start(child, expand, fill, padding)
            return
        if isinstance(parent, Gtk.Table):
            left = int(packing.get("left_attach", "0") or 0)
            right = int(packing.get("right_attach", str(left + 1)) or left + 1)
            top = int(packing.get("top_attach", "0") or 0)
            bottom = int(packing.get("bottom_attach", str(top + 1)) or top + 1)
            x_options = _attach_options(packing.get("x_options", "GTK_EXPAND|GTK_FILL"))
            y_options = _attach_options(packing.get("y_options", "GTK_EXPAND|GTK_FILL"))
            x_padding = int(packing.get("x_padding", "0") or 0)
            y_padding = int(packing.get("y_padding", "0") or 0)
            parent.attach(child, left, right, top, bottom, x_options, y_options, x_padding, y_padding)
            return
        if isinstance(parent, Gtk.Paned):
            if parent.get_child1() is None:
                parent.add1(child)
            else:
                parent.add2(child)
            return
        if isinstance(parent, Gtk.Notebook):
            if child_elem.find("widget").attrib.get("id", "").startswith("label"):
                return
            parent.append_page(child, Gtk.Label())
            return
        if isinstance(parent, Gtk.ScrolledWindow):
            parent.add(child)
            return
        if isinstance(parent, Gtk.Button) and isinstance(child, Gtk.Image):
            parent.set_image(child)
            return
        if isinstance(parent, Gtk.Bin):
            try:
                parent.add(child)
            except Exception:
                pass

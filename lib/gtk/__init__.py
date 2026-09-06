"""PyGTK-style facade backed by PyGObject/GTK3."""

import os
import sys

try:
    _self = sys.modules.get(__name__)
    sys.modules.pop(__name__, None)
    import gi

    gi.require_version("Gtk", "3.0")
    gi.require_version("Gdk", "3.0")
    gi.require_version("GdkPixbuf", "2.0")
    from gi.repository import Gdk as _Gdk
    from gi.repository import GdkPixbuf as _GdkPixbuf
    from gi.repository import GLib as _GLib
    from gi.repository import GObject as _GObject
    from gi.repository import Gtk as _Gtk
except ImportError as exc:  # pragma: no cover - depends on GUI runtime
    raise ImportError("PyGObject with GTK3 is required for the p4vasp GUI") from exc
finally:
    if "_self" in locals() and _self is not None:
        sys.modules[__name__] = _self
    if sys.modules.get("gobject", None).__class__.__name__ == "_DummyStaticModule":
        sys.modules.pop("gobject", None)
    if sys.modules.get(__name__ + ".gdk", None).__class__.__name__ == "_DummyStaticModule":
        sys.modules.pop(__name__ + ".gdk", None)


Gtk = _Gtk
Gdk = _Gdk
GLib = _GLib
GObject = _GObject
GdkPixbuf = _GdkPixbuf


def _copy_public_names(module):
    for name in dir(module):
        if not name.startswith("_") and name not in globals():
            globals()[name] = getattr(module, name)


_copy_public_names(_Gtk)


def _enum(enum_type, member, fallback=None):
    return getattr(enum_type, member, fallback)


DIALOG_DESTROY_WITH_PARENT = _enum(_Gtk.DialogFlags, "DESTROY_WITH_PARENT")
MESSAGE_INFO = _enum(_Gtk.MessageType, "INFO")
MESSAGE_ERROR = _enum(_Gtk.MessageType, "ERROR")
BUTTONS_OK = _enum(_Gtk.ButtonsType, "OK")
BUTTONS_CLOSE = _enum(_Gtk.ButtonsType, "CLOSE")
RESPONSE_OK = _enum(_Gtk.ResponseType, "OK")
RESPONSE_CANCEL = _enum(_Gtk.ResponseType, "CANCEL")
RESPONSE_CLOSE = _enum(_Gtk.ResponseType, "CLOSE")

POLICY_ALWAYS = _enum(_Gtk.PolicyType, "ALWAYS")
POLICY_AUTOMATIC = _enum(_Gtk.PolicyType, "AUTOMATIC")
POLICY_NEVER = _enum(_Gtk.PolicyType, "NEVER")

SHADOW_NONE = _enum(_Gtk.ShadowType, "NONE")
SHADOW_IN = _enum(_Gtk.ShadowType, "IN")
SHADOW_OUT = _enum(_Gtk.ShadowType, "OUT")
SHADOW_ETCHED_IN = _enum(_Gtk.ShadowType, "ETCHED_IN")
SHADOW_ETCHED_OUT = _enum(_Gtk.ShadowType, "ETCHED_OUT")

JUSTIFY_LEFT = _enum(_Gtk.Justification, "LEFT")
JUSTIFY_RIGHT = _enum(_Gtk.Justification, "RIGHT")
JUSTIFY_CENTER = _enum(_Gtk.Justification, "CENTER")
JUSTIFY_FILL = _enum(_Gtk.Justification, "FILL")

POS_LEFT = _enum(_Gtk.PositionType, "LEFT")
POS_RIGHT = _enum(_Gtk.PositionType, "RIGHT")
POS_TOP = _enum(_Gtk.PositionType, "TOP")
POS_BOTTOM = _enum(_Gtk.PositionType, "BOTTOM")

RELIEF_NORMAL = _enum(_Gtk.ReliefStyle, "NORMAL")
RELIEF_HALF = _enum(_Gtk.ReliefStyle, "HALF")
RELIEF_NONE = _enum(_Gtk.ReliefStyle, "NONE")

WINDOW_TOPLEVEL = _enum(_Gtk.WindowType, "TOPLEVEL")
WINDOW_POPUP = _enum(_Gtk.WindowType, "POPUP")
WIN_POS_NONE = _enum(_Gtk.WindowPosition, "NONE")
WIN_POS_CENTER = _enum(_Gtk.WindowPosition, "CENTER")

ORIENTATION_HORIZONTAL = _enum(_Gtk.Orientation, "HORIZONTAL")
ORIENTATION_VERTICAL = _enum(_Gtk.Orientation, "VERTICAL")

# PyGTK 2 selection-mode constants used by the legacy applets.
SELECTION_NONE = _enum(_Gtk.SelectionMode, "NONE")
SELECTION_SINGLE = _enum(_Gtk.SelectionMode, "SINGLE")
SELECTION_BROWSE = _enum(_Gtk.SelectionMode, "BROWSE")
SELECTION_MULTIPLE = _enum(_Gtk.SelectionMode, "MULTIPLE")

PACK_START = _enum(_Gtk.PackType, "START")
PACK_END = _enum(_Gtk.PackType, "END")

TYPE_BOOLEAN = bool
TYPE_DOUBLE = float
TYPE_FLOAT = float
TYPE_INT = int
TYPE_LONG = int
TYPE_OBJECT = object
TYPE_STRING = str

BUTTONBOX_DEFAULT_STYLE = _enum(_Gtk.ButtonBoxStyle, "DEFAULT_STYLE", _Gtk.ButtonBoxStyle.SPREAD)
BUTTONBOX_SPREAD = _enum(_Gtk.ButtonBoxStyle, "SPREAD")
BUTTONBOX_EDGE = _enum(_Gtk.ButtonBoxStyle, "EDGE")
BUTTONBOX_START = _enum(_Gtk.ButtonBoxStyle, "START")
BUTTONBOX_END = _enum(_Gtk.ButtonBoxStyle, "END")
BUTTONBOX_CENTER = _enum(_Gtk.ButtonBoxStyle, "CENTER")

TOOLBAR_ICONS = _enum(_Gtk.ToolbarStyle, "ICONS")
TOOLBAR_TEXT = _enum(_Gtk.ToolbarStyle, "TEXT")
TOOLBAR_BOTH = _enum(_Gtk.ToolbarStyle, "BOTH")
TOOLBAR_BOTH_HORIZ = _enum(_Gtk.ToolbarStyle, "BOTH_HORIZ")

TREE_MODEL_ITERS_PERSIST = _Gtk.TreeModelFlags.ITERS_PERSIST
TREE_MODEL_LIST_ONLY = _Gtk.TreeModelFlags.LIST_ONLY


main = _Gtk.main
main_quit = _Gtk.main_quit
mainquit = _Gtk.main_quit
mainloop = _Gtk.main
events_pending = _Gtk.events_pending
main_iteration = _Gtk.main_iteration
main_iteration_do = _Gtk.main_iteration_do


_box_pack_start = _Gtk.Box.pack_start
_box_pack_end = _Gtk.Box.pack_end


def _compat_box_pack_start(self, child, expand=True, fill=True, padding=0):
    return _box_pack_start(self, child, bool(expand), bool(fill), int(padding))


def _compat_box_pack_end(self, child, expand=True, fill=True, padding=0):
    return _box_pack_end(self, child, bool(expand), bool(fill), int(padding))


_Gtk.Box.pack_start = _compat_box_pack_start
_Gtk.Box.pack_end = _compat_box_pack_end


class MenuItem(_Gtk.MenuItem):
    def __init__(self, label=None, *args, **kwargs):
        if label is not None and "label" not in kwargs:
            kwargs["label"] = label
        super().__init__(*args, **kwargs)

    def set_right_justified(self, _right_justified):
        return None


class ImageMenuItem(_Gtk.ImageMenuItem if hasattr(_Gtk, "ImageMenuItem") else _Gtk.MenuItem):
    def __init__(self, label=None, *args, **kwargs):
        if label is not None and "label" not in kwargs:
            kwargs["label"] = label
        super().__init__(*args, **kwargs)


class Text(_Gtk.TextView):
    def set_text(self, text):
        self.get_buffer().set_text(text or "")

    def get_text(self):
        buf = self.get_buffer()
        return buf.get_text(buf.get_start_iter(), buf.get_end_iter(), True)


class Combo(_Gtk.ComboBoxText):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("has_entry", True)
        super().__init__(*args, **kwargs)
        self.entry = self.get_child()

    def set_popdown_strings(self, strings):
        active = self.get_active()
        self.remove_all()
        for item in strings:
            self.append_text(str(item))
        if active >= 0 and active < len(strings):
            self.set_active(active)
        elif strings and self.entry is not None and not self.entry.get_text():
            self.entry.set_text(str(strings[0]))


class OptionMenu(_Gtk.ComboBoxText):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._menu = Menu()
        self._suppress_changed = False
        self.connect("changed", self._on_changed)

    def set_menu(self, menu):
        self._menu = menu
        self._sync_from_menu()

    def get_menu(self):
        return self._menu

    def set_history(self, index):
        self._sync_from_menu()
        try:
            self._suppress_changed = True
            self.set_active(int(index))
        except (TypeError, ValueError):
            self.set_active(-1)
        finally:
            self._suppress_changed = False

    def get_history(self):
        return self.get_active()

    def _sync_from_menu(self):
        active = self.get_active()
        self._suppress_changed = True
        self.remove_all()
        for child in self._menu.get_children():
            label = child.get_label() if hasattr(child, "get_label") else child.get_name()
            self.append_text(label or "")
        if active >= 0:
            self.set_active(active)
        self._suppress_changed = False

    def _on_changed(self, *_args):
        if self._suppress_changed:
            return
        index = self.get_active()
        if index < 0:
            return
        items = self._menu.get_children()
        if index < len(items):
            items[index].activate()


class FileSelection(_Gtk.FileChooserDialog):
    def __init__(self, title=None, action=None, *args, **kwargs):
        action = action or _Gtk.FileChooserAction.OPEN
        super().__init__(title=title or "", action=action, *args, **kwargs)
        self._ok_clicked = False
        self.ok_button = self.add_button("_OK", RESPONSE_OK)
        self.cancel_button = self.add_button("_Cancel", RESPONSE_CANCEL)
        self.ok_button.connect("clicked", self._mark_ok_clicked)
        self.connect("response", self._on_response)

    def _mark_ok_clicked(self, *_args):
        self._ok_clicked = True

    def _on_response(self, _dialog, response_id):
        # GtkFileChooserDialog emits ``response`` for both buttons.  Keep
        # the dialog lifecycle independent from the application callback:
        # Cancel always closes it, and an exception in an OK callback cannot
        # leave a non-responsive chooser on screen.
        if response_id in (RESPONSE_CANCEL, RESPONSE_OK):
            self._ok_clicked = False
            self.hide()


class GenericTreeModel:
    def __init__(self, *args, **kwargs):
        pass

    def row_changed(self, *args, **kwargs):
        pass

    def row_inserted(self, *args, **kwargs):
        pass

    def row_deleted(self, *args, **kwargs):
        pass

    def foreach(self, callback, user_data=None):
        return None


def _model_column_types(model):
    result = []
    for i in range(model.on_get_n_columns()):
        typ = model.on_get_column_type(i)
        if typ in (str, TYPE_STRING):
            result.append(str)
        elif typ in (bool, TYPE_BOOLEAN):
            result.append(bool)
        elif typ in (int,):
            result.append(int)
        elif typ in (float, TYPE_FLOAT, TYPE_DOUBLE):
            result.append(float)
        else:
            result.append(object)
    return result


def _coerce_model_value(value, typ):
    if value is None:
        return "" if typ is str else False if typ is bool else 0 if typ is int else 0.0 if typ is float else None
    if typ is str:
        return str(value)
    if typ is bool:
        return bool(value)
    if typ is int:
        return int(value)
    if typ is float:
        return float(value)
    return value


def _generic_model_rows(model, parent=None):
    node = model.on_iter_children(parent)
    while node is not None:
        row = [
            _coerce_model_value(model.on_get_value(node, i), typ)
            for i, typ in enumerate(_model_column_types(model))
        ]
        yield node, row
        node = model.on_iter_next(node)


def _generic_to_tree_model(model):
    column_types = _model_column_types(model)
    try:
        flags = model.on_get_flags()
    except AttributeError:
        flags = TREE_MODEL_LIST_ONLY

    if flags == TREE_MODEL_LIST_ONLY:
        store = _Gtk.ListStore(*column_types)
        for _node, row in _generic_model_rows(model, None):
            store.append(row)
        return store

    store = _Gtk.TreeStore(*column_types)

    def append_children(parent_iter, parent_node):
        for node, row in _generic_model_rows(model, parent_node):
            child_iter = store.append(parent_iter, row)
            append_children(child_iter, node)

    append_children(None, None)
    return store


class TreeView(_Gtk.TreeView):
    def __init__(self, model=None, *args, **kwargs):
        if isinstance(model, GenericTreeModel):
            model = _generic_to_tree_model(model)
        super().__init__(*args, **kwargs)
        if model is not None:
            self.set_model(model)

    def set_model(self, model):
        if isinstance(model, GenericTreeModel):
            model = _generic_to_tree_model(model)
        return super().set_model(model)


def _set_right_justified(_item, _right_justified):
    return None


if not hasattr(_Gtk.MenuItem, "set_right_justified"):
    _Gtk.MenuItem.set_right_justified = _set_right_justified


Pixmap = Image
gtk = sys.modules[__name__]

sys.modules.pop(__name__ + ".gdk", None)
from . import gdk  # noqa: E402  (export gtk.gdk)

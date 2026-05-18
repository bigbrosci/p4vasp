"""Subset of the old ``gtk.gdk`` API used by p4vasp."""

import sys

try:
    _self = sys.modules.get(__name__)
    sys.modules.pop(__name__, None)
    import gi

    gi.require_version("Gtk", "3.0")
    gi.require_version("Gdk", "3.0")
    gi.require_version("GdkPixbuf", "2.0")
    from gi.repository import Gdk, GdkPixbuf
except ImportError as exc:  # pragma: no cover - depends on GUI runtime
    raise ImportError("PyGObject with GTK3 is required for the p4vasp GUI") from exc
finally:
    if "_self" in locals() and _self is not None:
        sys.modules[__name__] = _self


BUTTON_PRESS_MASK = Gdk.EventMask.BUTTON_PRESS_MASK
BUTTON_RELEASE_MASK = Gdk.EventMask.BUTTON_RELEASE_MASK
KEY_PRESS_MASK = Gdk.EventMask.KEY_PRESS_MASK
KEY_RELEASE_MASK = Gdk.EventMask.KEY_RELEASE_MASK
POINTER_MOTION_MASK = Gdk.EventMask.POINTER_MOTION_MASK
POINTER_MOTION_HINT_MASK = Gdk.EventMask.POINTER_MOTION_HINT_MASK
ALL_EVENTS_MASK = Gdk.EventMask.ALL_EVENTS_MASK

SHIFT_MASK = Gdk.ModifierType.SHIFT_MASK
CONTROL_MASK = Gdk.ModifierType.CONTROL_MASK

ENTER_NOTIFY = Gdk.EventType.ENTER_NOTIFY
MOTION_NOTIFY = Gdk.EventType.MOTION_NOTIFY
BUTTON_PRESS = Gdk.EventType.BUTTON_PRESS
BUTTON_RELEASE = Gdk.EventType.BUTTON_RELEASE
KEY_PRESS = Gdk.EventType.KEY_PRESS

DOTBOX = Gdk.CursorType.DOTBOX
BOTTOM_RIGHT_CORNER = Gdk.CursorType.BOTTOM_RIGHT_CORNER
FLEUR = Gdk.CursorType.FLEUR
SB_RIGHT_ARROW = Gdk.CursorType.SB_RIGHT_ARROW
CROSSHAIR = Gdk.CursorType.CROSSHAIR

Cursor = Gdk.Cursor
Pixbuf = GdkPixbuf.Pixbuf


def pixbuf_new_from_file(path):
    return GdkPixbuf.Pixbuf.new_from_file(path)


def keyval_from_name(name):
    return Gdk.keyval_from_name(name)


def keyval_name(keyval):
    return Gdk.keyval_name(keyval)


def screen_height():
    screen = Gdk.Screen.get_default()
    return screen.get_height() if screen is not None else 0


def screen_height_mm():
    screen = Gdk.Screen.get_default()
    return screen.get_height_mm() if screen is not None else 0

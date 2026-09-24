"""Subset of the old ``gtk.gdk`` API used by p4vasp."""

from gi.repository import Gdk, GdkPixbuf


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

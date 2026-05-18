"""Compatibility wrapper for the PyGTK-era ``gobject`` module."""

try:
    from gtk import GLib
    from gtk import GObject as _GObjectModule
except ImportError as exc:  # pragma: no cover - depends on GUI runtime
    raise ImportError("PyGObject with GTK3 is required for the p4vasp GUI") from exc


idle_add = GLib.idle_add
timeout_add = GLib.timeout_add
source_remove = GLib.source_remove

TYPE_BOOLEAN = bool
TYPE_DOUBLE = float
TYPE_FLOAT = float
TYPE_INT = int
TYPE_LONG = int
TYPE_OBJECT = object
TYPE_STRING = str

GObject = _GObjectModule.GObject

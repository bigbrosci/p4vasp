"""Compatibility wrapper for the old PyGTK ``pango`` module."""

import sys

try:
    _self = sys.modules.get(__name__)
    sys.modules.pop(__name__, None)
    import gi

    gi.require_version("Pango", "1.0")
    from gi.repository import Pango as _Pango
except ImportError as exc:  # pragma: no cover - depends on GUI runtime
    raise ImportError("PyGObject with Pango is required for the p4vasp GUI") from exc
finally:
    if "_self" in locals() and _self is not None:
        sys.modules[__name__] = _self


for _name in dir(_Pango):
    if not _name.startswith("_"):
        globals()[_name] = getattr(_Pango, _name)

STYLE_NORMAL = _Pango.Style.NORMAL
STYLE_ITALIC = _Pango.Style.ITALIC
STYLE_OBLIQUE = _Pango.Style.OBLIQUE
WEIGHT_NORMAL = _Pango.Weight.NORMAL
WEIGHT_BOLD = _Pango.Weight.BOLD


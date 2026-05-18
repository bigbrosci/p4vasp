"""Small compatibility shim for old PyGTK imports.

The original p4vasp GUI was written against PyGTK 2.x.  Modern Python
does not provide that package, so this module keeps ``import pygtk`` and
``pygtk.require("2.0")`` working while the real widgets are provided by
the local ``gtk`` compatibility package backed by PyGObject/GTK3.
"""


def require(version):
    return None


"""Bounded real-GUI preview used only by the Unix installer."""
import os
import sys

_errors = []
from p4vasp.gtk3 import Gtk, GLib


def start():
    original_hook = sys.excepthook
    def capture(*exception):
        _errors.append(exception[1])
        original_hook(*exception)
    sys.excepthook = capture
    def failed():
        print('p4vasp GUI preview failed: startup did not finish within 60 seconds.', flush=True)
        os._exit(1)
    GLib.timeout_add(60000, failed)


def ready():
    def visible():
        windows = [w for w in Gtk.Window.list_toplevels() if w.get_mapped() and w.get_window()]
        if not windows:
            return True
        def finished():
            if _errors or not any(w.get_mapped() for w in windows):
                print('p4vasp GUI preview failed or was closed before completion.', flush=True)
                os._exit(1)
            # Match the application's existing native-thread shutdown strategy.
            os._exit(0)
        GLib.timeout_add(2000, finished)
        return False
    GLib.idle_add(visible)

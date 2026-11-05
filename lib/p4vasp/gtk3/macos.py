"""Integration of GTK Quartz and the native FLTK windows on macOS."""
import ctypes
import sys
import os


def configure_event_loop():
    """Let Quartz dequeue Cocoa events; it forwards non-GTK events to AppKit.

    FLTK's independent Fl::check() otherwise consumes GTK key events before
    Quartz can translate them. Native VisCheck still handles p4vasp's window
    commands and flushes GL drawing. Standalone FLTK callers retain their loop.
    """
    if sys.platform != 'darwin':
        return
    from p4vasp.gtk3 import Gdk
    display = Gdk.Display.get_default()
    if display is not None and display.__gtype__.name == 'GdkQuartzDisplay':
        os.environ['P4VASP_GTK_QUARTZ_EVENT_LOOP'] = '1'


def present_startup(window):
    """Activate this terminal-launched application once, then present its frame."""
    if sys.platform != 'darwin':
        return
    from p4vasp.gtk3 import Gdk
    display = window.get_display()
    if display.__gtype__.name != 'GdkQuartzDisplay':
        return
    # AppKit is already loaded by GTK. Use typed runtime calls, without a
    # PyObjC dependency or AppleScript/System Events accessibility permission.
    objc = ctypes.CDLL('/usr/lib/libobjc.A.dylib')
    objc.objc_getClass.argtypes = [ctypes.c_char_p]
    objc.objc_getClass.restype = ctypes.c_void_p
    objc.sel_registerName.argtypes = [ctypes.c_char_p]
    objc.sel_registerName.restype = ctypes.c_void_p
    message = ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_void_p,
                               ctypes.c_void_p)(('objc_msgSend', objc))
    app = message(objc.objc_getClass(b'NSApplication'),
                  objc.sel_registerName(b'sharedApplication'))
    activate = ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_void_p,
                                ctypes.c_bool)(('objc_msgSend', objc))
    activate(app, objc.sel_registerName(b'activateIgnoringOtherApps:'), True)
    window.present()

"""Real Cocoa key delivery with GTK + FLTK; run on macOS with a desktop.

PYTHONPATH=lib P4VASP_HOME="$PWD" .venv-macos/bin/python3 test/testMacQuartzInput.py
--legacy reproduces the lost-key bug without configuring the Quartz bridge.
Events are posted only to this process; no Accessibility permission is needed.
"""
import ctypes as C
from io import StringIO
import os
from pathlib import Path
import sys
import time

if sys.platform != 'darwin':
    raise SystemExit('SKIP: requires macOS Quartz')

from p4vasp.gtk3 import Gtk, Gdk
from p4vasp.gtk3.gas_phase import GasPhasePage
from p4vasp.gtk3.macos import configure_event_loop, present_startup
import cp4vasp

objc = C.CDLL('/usr/lib/libobjc.A.dylib')
objc.objc_getClass.argtypes = [C.c_char_p]
objc.objc_getClass.restype = C.c_void_p
objc.sel_registerName.argtypes = [C.c_char_p]
objc.sel_registerName.restype = C.c_void_p


def call(obj, selector, result=C.c_void_p, types=(), args=()):
    function = C.CFUNCTYPE(result, C.c_void_p, C.c_void_p, *types)(('objc_msgSend', objc))
    return function(obj, objc.sel_registerName(selector.encode()), *args)


def text(value):
    return call(objc.objc_getClass(b'NSString'), 'stringWithUTF8String:',
                types=(C.c_char_p,), args=(value.encode(),))


app = call(objc.objc_getClass(b'NSApplication'), 'sharedApplication')


class Point(C.Structure):
    _fields_ = [('x', C.c_double), ('y', C.c_double)]


def key(window, characters, code=8, modifiers=0):
    if characters in ('C', 'O', 'N'):
        code = {'C': 8, 'O': 31, 'N': 45}[characters]
        modifiers |= 1 << 17  # NSEventModifierFlagShift
    chars = text(characters)
    for event_type in (10, 11):  # NSEventTypeKeyDown / KeyUp
        event = call(objc.objc_getClass(b'NSEvent'),
                     'keyEventWithType:location:modifierFlags:timestamp:windowNumber:context:'
                     'characters:charactersIgnoringModifiers:isARepeat:keyCode:',
                     types=(C.c_ulong, Point, C.c_ulong, C.c_double, C.c_long,
                            C.c_void_p, C.c_void_p, C.c_void_p, C.c_bool, C.c_ushort),
                     args=(event_type, Point(0, 0), modifiers, time.monotonic(),
                           call(window, 'windowNumber', C.c_long), None, chars, chars, False, code))
        call(app, 'postEvent:atStart:', None, (C.c_void_p, C.c_bool), (event, False))


def pump():
    for _ in range(30):
        # Deliberately poll native first: the old loop consumes the posted key.
        cp4vasp.VisCheck()
        while Gtk.events_pending():
            Gtk.main_iteration()
        time.sleep(.01)


def main():
    assert Gdk.Display.get_default().__gtype__.name == 'GdkQuartzDisplay'
    if '--legacy' not in sys.argv:
        configure_event_loop()
    else:
        os.environ.pop('P4VASP_GTK_QUARTZ_EVENT_LOOP', None)
    cp4vasp.VisInit()
    page = GasPhasePage()
    window = Gtk.Window(title='p4vasp Quartz input regression')
    window.set_default_size(900, 600)
    window.add(page)
    window.show_all()
    present_startup(window)
    page.smiles_entry.grab_focus()
    pump()
    assert call(app, 'isActive', C.c_bool), 'Startup did not activate application'
    gtk_window = call(app, 'keyWindow')
    assert page.smiles_entry.has_focus()
    for char in 'CCO':
        key(gtk_window, char)
        pump()
    assert page.smiles_entry.get_text() == 'CCO', repr(page.smiles_entry.get_text())
    key(gtk_window, '\x7f', 51)
    pump()
    assert page.smiles_entry.get_text() == 'CC'
    key(gtk_window, 'N', 45)
    pump()
    assert page.smiles_entry.get_text() == 'CCN'
    page.charge.grab_focus()
    key(gtk_window, '1', 18)
    pump()
    assert page.charge.get_text() == '1'

    from p4vasp.Structure import Structure
    from p4vasp.StructureWindow import StructureWindow
    structure = Structure()
    structure.read(StringIO('Quartz test\n1\n5 0 0\n0 5 0\n0 0 5\nH\n1\nCartesian\n0 0 0\n'))
    native = StructureWindow(w=400, h=300, title='Quartz native regression')
    native.setStructure(structure)
    native.structure_drawer.selectAtom(0, 0, 0, 0)
    native.show()
    pump()
    windows = call(app, 'windows')
    native_window = None
    for i in range(call(windows, 'count', C.c_ulong)):
        candidate = call(windows, 'objectAtIndex:', types=(C.c_ulong,), args=(i,))
        if call(call(candidate, 'title'), 'UTF8String', C.c_char_p) == b'Quartz native regression':
            native_window = candidate
            break
    assert native_window, 'Native window not created'
    call(native_window, 'makeKeyAndOrderFront:', None, (C.c_void_p,), (None,))
    pump()
    assert call(app, 'keyWindow') == native_window
    key(native_window, '\uf728', 117)  # Forward Delete reaches native event queue.
    pump()
    queue = cp4vasp.VisBackEventQueue.get()
    found = False
    while queue.current() is not None:
        event = queue.current()
        if event.type == cp4vasp.BE_ATOM_MOVE:
            found = True
        queue.pop()
    assert found, 'GTK did not forward native keyboard event to FLTK'
    native.hide()
    pump()
    window.present()
    page.smiles_entry.grab_focus()
    page.smiles_entry.set_position(-1)
    pump()
    key(gtk_window, 'O', 31)
    pump()
    assert page.smiles_entry.get_text() == 'CCNO', (page.smiles_entry.get_text(), page.smiles_entry.has_focus(), call(app, 'keyWindow') == gtk_window)
    import cairo
    output = Path('/tmp/p4vasp-mac-focus')
    output.mkdir(exist_ok=True)
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, window.get_allocated_width(), window.get_allocated_height())
    window.draw(cairo.Context(surface))
    surface.write_to_png(str(output/'gas-phase.png'))
    print('PASS: startup activation, SMILES Cocoa typing/deletion, charge input, native Delete delivery, return to GTK', flush=True)


if __name__ == '__main__':
    try:
        main()
    except BaseException:
        import traceback
        traceback.print_exc()
        os._exit(1)
    os._exit(0)  # Avoid unrelated mixed-toolkit interpreter teardown.

"""Real GLUT render/WM_DELETE, Escape, reopen and GTK responsiveness (X11)."""
import ctypes as C
from ctypes.util import find_library
from io import StringIO
import time
from p4vasp.gtk3 import Gtk, GLib
from gi.repository import GdkPixbuf
from p4vasp.SystemPM import SetupPM
from p4vasp.applet.KpointsViewerApplet import KpointsViewerApplet
from p4vasp.Dyna import dynaPublisher
from OpenGL.GL import glReadPixels, glReadBuffer, GL_FRONT, GL_RGBA, GL_UNSIGNED_BYTE
from OpenGL.GLUT import glutPostRedisplay

assert Gtk.init_check()[0]
window=Gtk.Window(title='p4vasp k-point lifecycle test');window.add(Gtk.Label(label='Main application remains responsive'));window.show_all()
def pump():
    for _ in range(40):
        while Gtk.events_pending():Gtk.main_iteration_do(False)
        time.sleep(.005)
def viewer():
    system=SetupPM()
    system.INITIAL_STRUCTURE.read(StringIO('Cu synthetic\n1\n3.6 0 0\n0 3.6 0\n0 0 3.6\nCu\n1\nDirect\n0 0 0\n'))
    system.add('KPOINT_LIST',[[0,0,0],[.5,0,0]])
    applet=KpointsViewerApplet();applet.celltype=applet.SUPERCELL;applet.setSystem(system);pump()
    assert applet.paint.window and applet._event_source
    return applet

# Send the same ICCCM WM_DELETE_WINDOW client message as a title-bar close.
x=C.CDLL(find_library('X11'))
x.XOpenDisplay.argtypes=[C.c_char_p];x.XOpenDisplay.restype=C.c_void_p
display=x.XOpenDisplay(None);assert display
x.XDefaultRootWindow.argtypes=[C.c_void_p];x.XDefaultRootWindow.restype=C.c_ulong
x.XQueryTree.argtypes=[C.c_void_p,C.c_ulong,C.POINTER(C.c_ulong),C.POINTER(C.c_ulong),C.POINTER(C.POINTER(C.c_ulong)),C.POINTER(C.c_uint)]
x.XFetchName.argtypes=[C.c_void_p,C.c_ulong,C.POINTER(C.c_char_p)]
x.XFree.argtypes=[C.c_void_p]
def find_window(parent):
    name=C.c_char_p()
    if x.XFetchName(display,parent,C.byref(name)):
        text=name.value.decode(errors='replace');x.XFree(name)
        if text=='p4vasp — K-points':return parent
    root=C.c_ulong();up=C.c_ulong();children=C.POINTER(C.c_ulong)();count=C.c_uint()
    if x.XQueryTree(display,parent,C.byref(root),C.byref(up),C.byref(children),C.byref(count)):
        ids=[children[i] for i in range(count.value)]
        if children:x.XFree(children)
        for child in ids:
            found=find_window(child)
            if found:return found
    return None
class Data(C.Union):_fields_=[('b',C.c_char*20),('s',C.c_short*10),('l',C.c_long*5)]
class Client(C.Structure):_fields_=[('type',C.c_int),('serial',C.c_ulong),('send_event',C.c_int),('display',C.c_void_p),('window',C.c_ulong),('message_type',C.c_ulong),('format',C.c_int),('data',Data)]
class Event(C.Union):_fields_=[('client',Client),('pad',C.c_long*24)]
x.XInternAtom.argtypes=[C.c_void_p,C.c_char_p,C.c_int];x.XInternAtom.restype=C.c_ulong
x.XSendEvent.argtypes=[C.c_void_p,C.c_ulong,C.c_int,C.c_long,C.POINTER(Event)]
x.XFlush.argtypes=[C.c_void_p];x.XCloseDisplay.argtypes=[C.c_void_p]

applet=viewer();paint=applet.paint
# Capture the actual OpenGL framebuffer, not a GTK substitute.
paint.zoom=1;glutPostRedisplay();pump();glReadBuffer(GL_FRONT)
w,h=paint.width,paint.height
pixels=bytes(glReadPixels(0,0,w,h,GL_RGBA,GL_UNSIGNED_BYTE))
pixels=b''.join(pixels[y*w*4:(y+1)*w*4] for y in reversed(range(h)))
GdkPixbuf.Pixbuf.new_from_bytes(GLib.Bytes.new(pixels),GdkPixbuf.Colorspace.RGB,True,8,w,h,w*4).savev('/tmp/p4vasp-kpoints-close.png','png',[],[])
xid=find_window(x.XDefaultRootWindow(display));assert xid
message=Event();message.client.type=33;message.client.display=display;message.client.window=xid
message.client.message_type=x.XInternAtom(display,b'WM_PROTOCOLS',False);message.client.format=32
message.client.data.l[0]=x.XInternAtom(display,b'WM_DELETE_WINDOW',False)
assert x.XSendEvent(display,xid,False,0,C.byref(message));x.XFlush(display);pump()
assert applet.paint is None and applet._event_source is None and applet._destroyed
assert applet not in dynaPublisher().listeners
assert find_window(x.XDefaultRootWindow(display)) is None
assert window.get_visible()
# Reopen and use the byte-valued keyboard callback supplied by PyOpenGL.
applet=viewer();applet.paint.keyPressed(b'\x1b',0,0);pump()
assert applet.paint is None and applet._event_source is None
assert applet not in dynaPublisher().listeners and window.get_visible()
# Explicit applet destruction is idempotent and leaves no orphan window.
applet=viewer();applet.destroyApplet();applet.destroyApplet();pump()
assert applet.paint is None and applet._event_source is None
assert find_window(x.XDefaultRootWindow(display)) is None
seen=[];GLib.idle_add(lambda:seen.append(True) and False);pump();assert seen
x.XCloseDisplay(display);window.destroy()
print('PASS actual k-point rendering, WM_DELETE close, Escape, reopen, repeated destruction and GTK responsiveness')

"""Native initial-framing and camera-pivot regression; requires a display."""
import os
import sys
import time
from pathlib import Path
from io import StringIO

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'lib'),str(ROOT/'src')]
os.environ['P4VASP_HOME'] = str(ROOT)
import cp4vasp
import cairo
import numpy as np
from p4vasp.Structure import Structure
from p4vasp.StructureWindow import StructureWindow
from p4vasp.util import getAtomtypes


def bounds(window):
    nav, drawer, structure = window.navigator, window.structure_drawer, window.structure
    counts = window.getMultiple()
    low, high = [float('inf')]*3, [-float('inf')]*3
    import itertools
    for n in itertools.product(*(range(c) for c in counts)):
        for atom, point in enumerate(structure):
            if drawer.info.getRecord(atom).hidden: continue
            radius = drawer.info.getRecord(atom).radius*drawer.getRadiusFactor()*nav.getZoom()
            p = [point[j]+sum((n[k]-counts[k]//2)*structure.basis[k][j] for k in range(3)) for j in range(3)]
            for i in range(3):
                value = sum(nav.getRotMatElement(i,j)*p[j]*nav.getZoom() for j in range(3))+nav.getRotMatElement(i,3)
                low[i], high[i] = min(low[i],value-radius),max(high[i],value+radius)
    return low,high


def centered(window):
    lo,hi = bounds(window)
    assert max(abs(lo[i]+hi[i]) for i in range(3)) < 1e-8,(lo,hi)


def main():
    cp4vasp.VisInit()
    source = Structure()
    source.read(StringIO('Offset slab with vacuum\n1\n12 0 0\n0 8 0\n0 0 50\nCu\n4\nCartesian\n103 205 41\n111 205 41\n103 211 41\n111 211 41\n'))
    original = [list(p) for p in source]
    for w,h,repeat in ((400,300,(1,1,1)),(800,600,(2,3,1)),(900,300,(1,1,1))):
        window = StructureWindow(w=w,h=h,atomtypes=getAtomtypes())
        window.setRadiusFactor(.5)
        window.setMultiple(*repeat)
        window.setStructure(None)
        window.setStructure(source)
        centered(window)
        lo,hi = bounds(window)
        assert hi[0]-lo[0] <= .04*w*.851
        assert hi[1]-lo[1] <= .04*h*.851
        assert hi[2]-lo[2] < 60
        nav = window.navigator
        for view in (nav.setTopView,nav.setRightView,nav.setFrontView):
            view(); centered(window)
            nav.mulZoom(1.1); centered(window)
        matrix = [[nav.getRotMatElement(i,j) for j in range(4)] for i in range(4)]
        zoom = nav.getZoom()
        window.setStructure(source)
        assert matrix == [[nav.getRotMatElement(i,j) for j in range(4)] for i in range(4)]
        assert zoom == nav.getZoom(), 'Frame refresh unexpectedly reset camera'
        from p4vasp.applet.StructureWindowControlApplet import StructureWindowControlApplet
        control = StructureWindowControlApplet()
        control.swin = lambda: window
        control.on_home_button_clicked_handler()
        centered(window)
        from p4vasp.applet.StructureWindowApplet import StructureWindowApplet
        applet = StructureWindowApplet()
        applet.swin = window
        shifted = Structure(source)
        for p in shifted.positions:
            p[0] -= 300; p[1] -= 500
        applet.updateSystem = lambda: window.setStructure(shifted)
        applet.setSystem(object())
        centered(window)
        applet.updateSystem = lambda: window.setStructure(source)
        applet.setSystem(object())
        centered(window)
        assert original == [list(p) for p in source]
        np.testing.assert_allclose(original,[list(p) for p in window.structure],rtol=0,atol=1e-10)
        window.hide(); window.show()
        centered(window)
        assert window.getMultiple() == repeat
        assert abs(window.getRadiusFactor()-.5) < 1e-8
        if w == 900:
            window.showCell(0)
            for _ in range(12):
                cp4vasp.VisCheck(); time.sleep(.02)
            window.win.saveScreenshot('/tmp/p4v-centered-window.tga')
            raw = Path('/tmp/p4v-centered-window.tga').read_bytes()
            sw,sh = int.from_bytes(raw[12:14],'little'),int.from_bytes(raw[14:16],'little')
            rgb = np.frombuffer(raw[18:],dtype=np.uint8).reshape(sh,sw,3)[::-1,:,::-1]
            colored = np.max(rgb,axis=2)-np.min(rgb,axis=2) > 15
            ys,xs = np.where(colored)
            assert len(xs) > 100,'No native atoms drawn in screenshot'
            assert abs((xs.min()+xs.max())/2-sw/2) < 3
            assert abs((ys.min()+ys.max())/2-sh/2) < 3
            pixels = (0xff000000 | rgb[:,:,0].astype(np.uint32)<<16 |
                      rgb[:,:,1].astype(np.uint32)<<8 | rgb[:,:,2].astype(np.uint32))
            surface = cairo.ImageSurface.create_for_data(pixels,cairo.FORMAT_ARGB32,sw,sh,sw*4)
            surface.write_to_png('/tmp/p4v-centered-window.png')
        window.hide()
    print('PASS: offset slab, vacuum, viewport sizes, replicas, pivot/view/zoom, frame preservation, reopening and native screenshot',flush=True)


if __name__ == '__main__':
    try: main()
    except BaseException:
        import traceback
        traceback.print_exc(); os._exit(1)
    os._exit(0)

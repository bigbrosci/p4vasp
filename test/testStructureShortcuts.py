"""Actual Show owner, Builder refresh, Delete guards and native HUD screenshots."""
import os
from io import StringIO
from pathlib import Path
from types import SimpleNamespace
import time
from p4vasp.gtk3 import Gtk
from p4vasp.SystemPM import SetupPM,systemlist
from p4vasp.Structure import Structure
from p4vasp.StructureWindow import StructureWindow
from p4vasp.applet.StructureWindowApplet import StructureWindowApplet
from p4vasp.applet.BuilderApplet import BuilderApplet
from p4vasp.Selection import selection
from p4vasp.atom_movement import handle_event
from p4vasp.util import getAtomtypes
import cp4vasp


def capture(window,path):
    for _ in range(15):
        while Gtk.events_pending():Gtk.main_iteration()
        cp4vasp.VisCheck();time.sleep(.02)
    window.win.saveScreenshot(path)


def main():
    assert Gtk.init_check()[0];cp4vasp.VisInit()
    system=SetupPM();system.INCAR['SYSTEM']='Delete/HUD regression'
    positions=['%.6f %.6f %.6f T F T'%((i%5)/8,((i//5)%5)/8,(i//25)/8) for i in range(96)]
    text='counts\n1\n13 0 0\n0 14 0\n0 0 15\nCu C Cu H O\n32 10 32 20 2\nSelective dynamics\nDirect\n'+'\n'.join(positions)+'\n'
    source=system.INITIAL_STRUCTURE;source.read(StringIO(text))
    final=Structure(source);system.add('FINAL_STRUCTURE',final)
    systemlist().activate(system)
    owner=StructureWindowApplet();owner.system=system
    window=StructureWindow(w=700,h=500,title='p4vasp count / Delete check',atomtypes=getAtomtypes())
    owner.swin=window;owner.updateSystem();window.setRadiusFactor(.5)
    builder=BuilderApplet();builder.system=system
    offscreen=Gtk.OffscreenWindow();offscreen.add(builder.createPanel());builder.initUI();offscreen.show_all()
    assert builder.treeview.get_model().iter_n_children(None)==96
    window.setMultiple(2,1,1)
    capture(window,'/tmp/p4vasp-counts-before.tga')
    window.setMultiple(1,1,1)
    nav=window.navigator;nav.setFrontView();nav.mulZoom(1.1)
    matrix=[[nav.getRotMatElement(i,j) for j in range(4)] for i in range(4)];zoom=nav.getZoom()
    chosen=[0,0,74]
    selection().setSelection([(0,0,0,0),(0,1,0,0),(74,0,0,0)])
    window.selectAtom(0,0,0,0);window.selectAtom(0,1,0,0);window.selectAtom(74,0,0,0)
    capture(window,'/tmp/p4vasp-counts-selected.tga')
    other=SimpleNamespace(system=object(),getWindowPtr=lambda:None,updateSystem=lambda:(_ for _ in ()).throw(AssertionError('Other system refreshed')))
    event=SimpleNamespace(index=2,dx=96,dy=0,dz=0,getWindow=lambda:window.win,
                          getMovedAtomCount=lambda:len(chosen),getMovedAtom=lambda i:chosen[i])
    handle_event(event,[other,owner,builder])
    assert len(source)==94 and len(final)==96
    assert not selection().getAtoms() and window.getSelectedCount()==0
    assert builder.treeview.get_model().iter_n_children(None)==94
    assert matrix==[[nav.getRotMatElement(i,j) for j in range(4)] for i in range(4)] and zoom==nav.getZoom()
    counts={}
    for record in source.info:counts[record.element.strip()]=counts.get(record.element.strip(),0)+record.atomspertype
    assert counts==dict(Cu=63,C=10,H=19,O=2),counts
    output=StringIO();source.write(output);saved=Structure();saved.read(StringIO(output.getvalue()))
    assert len(saved)==94 and all(list(flag)==[True,False,True] for flag in saved.selective)
    handle_event(event,[owner,builder]);assert len(source)==94  # stale repeated key
    capture(window,'/tmp/p4vasp-counts-after.tga')
    owner.setSequenceType(owner.FINAL_SEQUENCE)
    event.dx=96;handle_event(event,[owner,builder]);assert len(source)==94 and len(final)==96
    owner.setSequenceType(owner.INITIAL_SEQUENCE)
    chosen[:]=list(range(94));event.dx=94
    handle_event(event,[owner,builder]);assert len(source)==0 and builder.treeview.get_model().iter_n_children(None)==0
    capture(window,'/tmp/p4vasp-counts-empty.tga')
    # The old Build Delete action still follows its existing path.
    source.read(StringIO(text));selection().setSelection([0])
    builder.on_del_button_clicked_handler(None);assert len(source)==95
    print('PASS: Show/Delete owner, dedup/stale/read-only guards, Builder sync, camera, POSCAR flags and HUD captures',flush=True)
    # Native window teardown is outside this isolated render test.
    os._exit(0)

if __name__=='__main__':
    try:main()
    except BaseException:
        import traceback
        traceback.print_exc();os._exit(1)

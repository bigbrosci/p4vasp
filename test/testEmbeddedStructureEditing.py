"""GTK event and File/Save integration exercised by testStartupPreviewGtk.py."""
def exercise(frame,preview,folder,pump):
    import math
    import cairo
    from p4vasp.gtk3 import Gdk
    from p4vasp.Selection import selection
    from p4vasp.Structure import Structure
    view=preview.view;source=preview.system.INITIAL_STRUCTURE
    def key(name,state=0):
        event=Gdk.Event.new(Gdk.EventType.KEY_PRESS);event.keyval=Gdk.keyval_from_name(name);event.state=state
        return view.emit('key-press-event',event)
    def mouse(kind,x,y,state=0):
        event=Gdk.Event.new(kind);event.window=view.get_window();event.x=x;event.y=y;event.state=state
        if kind!=Gdk.EventType.MOTION_NOTIFY:event.button=1
        signal={Gdk.EventType.BUTTON_PRESS:'button-press-event',Gdk.EventType.BUTTON_RELEASE:'button-release-event',Gdk.EventType.MOTION_NOTIFY:'motion-notify-event'}[kind]
        return view.emit(signal,event)
    def box():
        w,h=view.get_allocated_width(),view.get_allocated_height()
        mouse(Gdk.EventType.BUTTON_PRESS,1,1,Gdk.ModifierType.SHIFT_MASK)
        mouse(Gdk.EventType.MOTION_NOTIFY,w-1,h-1,Gdk.ModifierType.SHIFT_MASK)
        mouse(Gdk.EventType.BUTTON_RELEASE,w-1,h-1,Gdk.ModifierType.SHIFT_MASK)
    view.zoom=3;view.queue_draw();pump()
    x,y,z=view.project(view.display_positions()[1])
    mouse(Gdk.EventType.MOTION_NOTIFY,x,y);key('space')
    assert selection().getAtoms()==[1]
    assert frame.selection_entry.get_text().strip()
    assert 'Selected: H: 1' in preview.summary.get_text()
    key('space');assert not selection()
    rotation=view.rotation
    box();assert set(selection().getAtoms())=={0,1,2} and view.rotation==rotation
    assert preview.summary.get_text().endswith('Selected: O: 0 | H: 1, 2')
    box();assert not selection()
    # Escape cancels an unfinished box without clearing the previous selection.
    selection().setSelection([0]);selection().notify(None)
    mouse(Gdk.EventType.BUTTON_PRESS,1,1,Gdk.ModifierType.SHIFT_MASK)
    key('Escape');assert selection().getAtoms()==[0]
    mouse(Gdk.EventType.BUTTON_PRESS,1,1,Gdk.ModifierType.SHIFT_MASK)
    focus=Gdk.Event.new(Gdk.EventType.FOCUS_CHANGE);focus.in_=False
    view.emit('focus-out-event',focus)
    assert view.box is None and selection().getAtoms()==[0]
    mouse(Gdk.EventType.BUTTON_PRESS,1,1,Gdk.ModifierType.SHIFT_MASK)
    window=frame.root_window;window.resize(window.get_allocated_width()+60,window.get_allocated_height()+40);pump()
    mouse(Gdk.EventType.BUTTON_RELEASE,view.get_allocated_width()-1,view.get_allocated_height()-1,Gdk.ModifierType.SHIFT_MASK)
    assert selection().getAtoms()==[0]
    key('Escape');assert not selection()
    selection().setSelection([0,1]);selection().notify(None)
    camera=(view.rotation,view.zoom,view.pan,list(view.center),view.extent)
    before=[list(p) for p in source]
    key('Right')
    delta=[source[0][j]-before[0][j] for j in range(3)]
    assert abs(math.sqrt(sum(v*v for v in delta))-.1)<1e-8
    assert list(source[2])==before[2]
    assert (view.rotation,view.zoom,view.pan,list(view.center),view.extent)==camera
    distance=lambda:sum((source[0][j]-source[1][j])**2 for j in range(3))
    before_distance=distance();key('Up',Gdk.ModifierType.SHIFT_MASK)
    assert abs(distance()-before_distance)<1e-8
    # Modified keys must not trigger destructive editing.
    assert not key('Delete',Gdk.ModifierType.CONTROL_MASK) and len(source)==3
    assert not key('Delete',Gdk.ModifierType.SHIFT_MASK) and len(source)==3
    view.queue_draw();pump()
    shot=cairo.ImageSurface(cairo.FORMAT_ARGB32,view.get_allocated_width(),view.get_allocated_height())
    view.draw(cairo.Context(shot));shot.write_to_png('/tmp/p4vasp-embedded-selection.png')
    selection().setSelection([1]);selection().notify(None)
    source.selective=[[True,False,True],[False,False,False],[True,True,False]]
    key('Delete');assert len(source)==2 and not selection()
    assert len(view.data['positions'])==2 and 'H: 1' in preview.summary.get_text()
    assert source.selective==[[True,False,True],[True,True,False]]
    # Exercise the actual File menu, chooser OK and Frame save callback.
    target=folder/'edited_POSCAR'
    frame.xml.get_widget('save_system').emit('activate');pump()
    chooser=frame.save_system_fileselection
    chooser.set_current_folder(str(folder));chooser.set_current_name(target.name);pump()
    chooser.ok_button.clicked();pump()
    saved=Structure(str(target))
    assert len(saved)==2 and saved.selective==source.selective
    for p,q in zip(saved,source):assert all(abs(a-b)<1e-8 for a,b in zip(p,q))
    assert [saved.getRecordForAtom(i).element.strip() for i in range(2)]==['O','H']
    chooser.destroy()
    key('Delete');assert len(source)==2
    selection().setSelection([0,1]);selection().notify(None);key('Delete')
    assert len(source)==0 and view.data is None and not selection(), (len(source),view.data is None,list(selection()),view.box,preview.editable_source() is source)
    print('PASS embedded Space/Shift-box/Escape, shared selection, arrows/rotation/Delete, camera/flags and real File/Save POSCAR',flush=True)

"""Editable startup canvas; frequency ModeView remains display-only."""
import math
from p4vasp.gtk3 import Gtk,Gdk
from p4vasp.gtk3.mode_view import ModeView
from p4vasp.viewer_style import RADIUS_FACTOR
from p4vasp.Selection import selection


class StructureView(ModeView):
    def __init__(self,owner):
        self.owner=owner;self.pointer=None;self.box=None
        super().__init__()
        self.set_can_focus(True)
        self.add_events(Gdk.EventMask.ENTER_NOTIFY_MASK|Gdk.EventMask.LEAVE_NOTIFY_MASK|Gdk.EventMask.KEY_PRESS_MASK)
        self.connect('enter-notify-event',self.enter)
        self.connect('leave-notify-event',self.leave)
        self.connect('key-press-event',self.key)
        self.connect('focus-out-event',self.cancel_drag)
        self.set_tooltip_text('Show controls: Space toggles the atom under the pointer; Shift + left drag toggles atoms in a box; Esc clears. Delete removes selected atoms. Arrows move; Shift + arrows rotate. Left drag rotates, Ctrl + left spins, middle pans, right drag/scroll zooms.')

    def enter(self,widget,event):
        self.grab_focus();self.pointer=(event.x,event.y);return False

    def leave(self,*_):
        self.pointer=None;return False

    def toggle(self,indices):
        current=list(selection())
        for i in dict.fromkeys(indices):
            atom=(i,0,0,0)
            if atom in current:current.remove(atom)
            else:current.append(atom)
        selection().setSelection(current);selection().notify(self.owner)
        self.owner.notifyAtomSelection(selection(),self.owner)

    def press(self,widget,event):
        self.grab_focus();self.pointer=(event.x,event.y)
        if self.data and event.button==1 and event.state&Gdk.ModifierType.SHIFT_MASK:
            self.box=[event.x,event.y,event.x,event.y,self.get_allocated_width(),self.get_allocated_height()]
            self.queue_draw();return True
        return super().press(widget,event)

    def motion(self,widget,event):
        self.pointer=(event.x,event.y)
        if self.box is not None:
            self.box[2:4]=[event.x,event.y];self.queue_draw();return True
        return super().motion(widget,event)

    def release(self,widget,event):
        if self.box is not None and event.button==1:
            self.box[2:4]=[event.x,event.y]
            x0,y0,x1,y1,w,h=self.box;self.box=None
            if self.data and (w,h)==(self.get_allocated_width(),self.get_allocated_height()) and abs(x1-x0)>=3 and abs(y1-y0)>=3:
                left,right=sorted((x0,x1));top,bottom=sorted((y0,y1))
                picked=[]
                for i,point in zip(self.indices,self.display_positions()):
                    x,y,z=self.project(point)
                    if 0<=x<=w and 0<=y<=h and left<=x<=right and top<=y<=bottom:picked.append(i)
                self.toggle(picked)
            self.queue_draw();return True
        return super().release(widget,event)

    def cancel_drag(self,*args):
        self.box=None
        self.queue_draw()
        return super().cancel_drag(*args)

    def key(self,widget,event):
        if event.state&(Gdk.ModifierType.CONTROL_MASK|Gdk.ModifierType.MOD1_MASK|Gdk.ModifierType.META_MASK):return False
        name=Gdk.keyval_name(event.keyval)
        if name=='Escape':
            if self.box is not None:self.box=None;self.queue_draw()
            else:
                selection().setSelection([]);selection().notify(self.owner)
                self.owner.notifyAtomSelection(selection(),self.owner)
            return True
        if self.box is not None:return True
        if not self.data:return False
        if name=='space' and self.pointer is not None:
            px,py=self.pointer;hits=[]
            for n,p in enumerate(self.display_positions()):
                x,y,z=self.project(p);i=self.indices[n]
                radius=max(2.,self.projection_scale()*max(.15,self.ball_radii[i]*RADIUS_FACTOR))
                if (px-x)**2+(py-y)**2<=radius**2:hits.append((z,i))
            if hits:self.toggle([max(hits)[1]])
            return True
        shift=bool(event.state&Gdk.ModifierType.SHIFT_MASK)
        if name=='Delete' and not shift:
            self.owner.edit('delete');return True
        if name in ('Left','Right','Up','Down'):
            horizontal=name in ('Left','Right')
            row=(1 if horizontal else 0) if shift else (0 if horizontal else 1)
            sign=-1 if name=='Left' or name==('Up' if shift else 'Down') else 1
            self.owner.edit('rotate' if shift else 'move',[sign*v for v in self.rotation[row]])
            return True
        return False

    def on_draw(self,widget,cr):
        if not self.data:
            cr.set_source_rgb(1,1,1);cr.paint();return False
        super().on_draw(widget,cr)
        chosen=set(selection().getAtoms())
        cr.set_source_rgb(.1,.65,1.);cr.set_line_width(2.)
        for i,p in zip(self.indices,self.display_positions()):
            if i in chosen:
                x,y,z=self.project(p)
                radius=max(2.,self.projection_scale()*max(.15,self.ball_radii[i]*RADIUS_FACTOR))+3
                cr.new_sub_path();cr.arc(x,y,radius,0,2*math.pi);cr.stroke()
        if self.box is not None:
            x,y,x1,y1,w,h=self.box
            if (w,h)==(self.get_allocated_width(),self.get_allocated_height()):
                cr.new_path();cr.rectangle(x,y,x1-x,y1-y);cr.stroke()
        return False

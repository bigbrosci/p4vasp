"""GTK/Cairo ball-and-stick mode preview, with interactive 3D projection.

This is a display copy, independent of the editable native structure window.
No calculation or mode normalization is performed by the renderer.
"""
import math
import cairo
from p4vasp.gtk3 import Gtk, Gdk
from p4vasp.periodic_preview import geometry, bonds
from p4vasp.viewer_style import display_values, RADIUS_FACTOR, BOND_FACTOR, BOND_COLOR, BOND_RADIUS, CELL_LINE_WIDTH


def _multiply(a, b):
    return tuple(tuple(sum(a[i][k]*b[k][j] for k in range(3)) for j in range(3)) for i in range(3))


def _show_rotation(x, y, z=0.):
    # VisNavDrawer uses makerotmat4 (vecutils.cpp), stored column-major for
    # OpenGL. Keep its Euler composition/signs rather than substituting a
    # trackball: combined drags must behave like the native Show window.
    cx, sx = math.cos(x), math.sin(x)
    cy, sy = math.cos(y), math.sin(y)
    cz, sz = math.cos(z), math.sin(z)
    return ((cy*cz, sx*sy*cz+cx*sz, sx*sz-cx*sy*cz),
            (-sz*cy, cx*cz-sx*sy*sz, cx*sy*sz+sx*cz),
            (sy, -sx*cy, cx*cy))


class ModeView(Gtk.DrawingArea):
    def __init__(self):
        super().__init__()
        self.set_size_request(250,230)
        self.data=None;self.positions=[];self.bonds=[]
        self.repeats=(1,1,1);self.show_cell=True;self.indices=[];self.offsets=[];self.cell_edges=[]
        self.rotation=_multiply(_show_rotation(.3,0),_show_rotation(0,-.4))
        self.pan=(0.,0.,0.);self.zoom=1.;self.drag=None
        self.set_tooltip_text('Show controls: left drag rotates; Ctrl + left drag spins; middle drag pans; right drag horizontally zooms. Scroll also zooms. Read-only preview.')
        self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK|Gdk.EventMask.BUTTON_RELEASE_MASK|
                        Gdk.EventMask.POINTER_MOTION_MASK|Gdk.EventMask.SCROLL_MASK|Gdk.EventMask.SMOOTH_SCROLL_MASK)
        self.connect('draw',self.on_draw)
        self.connect('button-press-event',self.press)
        self.connect('button-release-event',self.release)
        self.connect('grab-broken-event',self.cancel_drag)
        self.connect('motion-notify-event',self.motion)
        self.connect('scroll-event',self.scroll)

    def set_data(self,data):
        self.data=data;self.positions=data['positions'];self.zoom=1.
        self.radii,self.colors=display_values(data['symbols'],data['radii'],data['colors'])
        self.set_repeats((1,1,1))

    def set_repeats(self,repeats):
        indices,offsets,points,edges=geometry(self.data['positions'],self.data['cell'],repeats)
        self.repeats=tuple(repeats);self.indices=indices;self.offsets=offsets;self.cell_edges=edges
        self.bonds=bonds(points,[self.radii[i] for i in indices],BOND_FACTOR)
        self.fit(points);self.queue_draw()

    def fit(self,points=None):
        if points is None:points=self.display_positions()
        bounds=list(points)
        if self.show_cell:bounds.extend(point for edge in self.cell_edges for point in edge)
        low=[min(p[j] for p in bounds) for j in range(3)];high=[max(p[j] for p in bounds) for j in range(3)]
        self.center=[(a+b)/2 for a,b in zip(low,high)]
        self.extent=max(3.,math.sqrt(sum((b-a)**2 for a,b in zip(low,high)))+2.)
        self.zoom=1.;self.pan=(0.,0.,0.);self.drag=None

    def display_positions(self):
        return [[self.positions[i][j]+offset[j] for j in range(3)] for i,offset in zip(self.indices,self.offsets)]

    def set_cell_visible(self,visible):
        self.show_cell=bool(visible)
        if self.data:self.fit()
        self.queue_draw()

    def set_positions(self,positions):
        self.positions=positions;self.queue_draw()

    def press(self,widget,event):
        if not self.data or event.button not in (1,2,3):return False
        # Shift+left is selection in Show, never camera rotation. This preview
        # has no editing/selection tool, so leave that gesture unassigned.
        if event.button==1 and event.state&Gdk.ModifierType.SHIFT_MASK:return False
        mode='spin' if event.button==1 and event.state&Gdk.ModifierType.CONTROL_MASK else {1:'rotate',2:'pan',3:'zoom'}[event.button]
        self.drag=(event.x,event.y,event.button,mode,self.rotation,self.pan,self.zoom)
        return True

    def motion(self,widget,event):
        if self.drag is None:return False
        x,y,button,mode,rotation,pan,zoom=self.drag
        dx,dy=event.x-x,event.y-y
        if mode in ('rotate','spin'):
            if mode=='rotate':
                delta=_show_rotation(-dy/100.,-dx/100.)
            else:
                cx,cy=self.get_allocated_width()/2.,self.get_allocated_height()/2.
                angle=math.atan2(event.y-cy,event.x-cx)-math.atan2(y-cy,x-cx)
                delta=_show_rotation(0.,0.,angle)
            self.rotation=_multiply(delta,rotation)
            self.pan=tuple(sum(delta[i][j]*pan[j] for j in range(3)) for i in range(3))
        elif mode=='pan':
            # Show: translation += delta/width/0.04, orthographic pixel scale
            # is 1/0.04. Preserve its width-based sensitivity for both axes.
            factor=625./max(1,self.get_allocated_width())
            self.pan=(pan[0]+factor*dx,pan[1]-factor*dy,pan[2])
        else:
            self.zoom=math.exp(max(math.log(.1),min(math.log(10.),math.log(zoom)+.005*dx)))
        self.queue_draw();return True

    def release(self,widget,event):
        if self.drag is None or event.button!=self.drag[2]:return False
        self.motion(widget,event);self.drag=None
        return True

    def cancel_drag(self,*args):
        self.drag=None
        return False

    def scroll(self,widget,event):
        if event.direction==Gdk.ScrollDirection.UP:amount=-1.
        elif event.direction==Gdk.ScrollDirection.DOWN:amount=1.
        elif event.direction==Gdk.ScrollDirection.SMOOTH:
            success,dx,amount=event.get_scroll_deltas()
            if not success or not amount:return False
        else:return False
        self.zoom=math.exp(max(math.log(.1),min(math.log(10.),math.log(self.zoom)-amount*math.log(1.12))))
        self.queue_draw();return True

    def on_draw(self,widget,cr):
        w=self.get_allocated_width();h=self.get_allocated_height()
        cr.set_source_rgb(1,1,1);cr.paint()
        if not self.data:
            cr.set_source_rgb(.35,.35,.35);cr.move_to(18,35);cr.show_text('Open a frequency OUTCAR to preview modes.');return False
        factor=min(w,h)*.75/self.extent*self.zoom
        r=self.rotation
        def project(p):
            a,b,c=p[0]-self.center[0],p[1]-self.center[1],p[2]-self.center[2]
            x=r[0][0]*a+r[0][1]*b+r[0][2]*c
            y=r[1][0]*a+r[1][1]*b+r[1][2]*c
            z=r[2][0]*a+r[2][1]*b+r[2][2]*c
            return (w/2+self.pan[0]+factor*x,h/2-self.pan[1]-factor*y,z)
        points=[project(p) for p in self.display_positions()]
        # Draw the lattice behind atoms/bonds so the frame cannot hide a mode.
        if self.show_cell:
            cr.set_source_rgb(0,0,0);cr.set_line_width(CELL_LINE_WIDTH)
            for a,b in self.cell_edges:
                cr.move_to(*project(a)[:2]);cr.line_to(*project(b)[:2])
            cr.stroke()
        objects=[((points[i][2]+points[j][2])/2,'bond',(i,j)) for i,j in self.bonds]
        objects.extend((p[2],'atom',i) for i,p in enumerate(points))
        for _,kind,item in sorted(objects,key=lambda obj:obj[0]):
            if kind=='bond':
                i,j=item;cr.set_source_rgb(*BOND_COLOR);cr.set_line_width(max(2.,factor*2*BOND_RADIUS))
                cr.move_to(*points[i][:2]);cr.line_to(*points[j][:2]);cr.stroke()
            else:
                x,y,_=points[item];radius=max(2.,factor*max(.15,self.radii[self.indices[item]]*RADIUS_FACTOR))
                red,green,blue=self.colors[self.indices[item]]
                gradient=cairo.RadialGradient(x-radius*.3,y-radius*.3,radius*.05,x,y,radius)
                gradient.add_color_stop_rgb(0,min(1,red*.6+.4),min(1,green*.6+.4),min(1,blue*.6+.4))
                gradient.add_color_stop_rgb(.65,red,green,blue)
                gradient.add_color_stop_rgb(1,red*.45,green*.45,blue*.45)
                cr.set_source(gradient);cr.arc(x,y,radius,0,2*math.pi);cr.fill()
        cr.set_source_rgb(.3,.3,.3);cr.move_to(10,h-12)
        cr.show_text('%d atoms | %d displayed | %d x %d x %d'%(len(self.positions),len(points),*self.repeats))
        return False

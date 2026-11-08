"""GTK/Cairo ball-and-stick mode preview, with interactive 3D projection.

This is a display copy, independent of the editable native structure window.
No calculation or mode normalization is performed by the renderer.
"""
import math
import cairo
from p4vasp.gtk3 import Gtk, Gdk
from p4vasp.periodic_preview import geometry, bonds
from p4vasp.viewer_style import display_values, RADIUS_FACTOR, BOND_FACTOR, BOND_COLOR, BOND_RADIUS


class ModeView(Gtk.DrawingArea):
    def __init__(self):
        super().__init__()
        self.set_size_request(250,230)
        self.data=None;self.positions=[];self.bonds=[]
        self.repeats=(1,1,1);self.show_cell=True;self.indices=[];self.offsets=[];self.cell_edges=[]
        self.yaw=.4;self.pitch=-.3;self.zoom=1.;self.drag=None
        self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK|Gdk.EventMask.BUTTON_RELEASE_MASK|
                        Gdk.EventMask.POINTER_MOTION_MASK|Gdk.EventMask.SCROLL_MASK)
        self.connect('draw',self.on_draw)
        self.connect('button-press-event',self.press)
        self.connect('button-release-event',lambda *_:setattr(self,'drag',None))
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
        self.zoom=1.

    def display_positions(self):
        return [[self.positions[i][j]+offset[j] for j in range(3)] for i,offset in zip(self.indices,self.offsets)]

    def set_cell_visible(self,visible):
        self.show_cell=bool(visible)
        if self.data:self.fit()
        self.queue_draw()

    def set_positions(self,positions):
        self.positions=positions;self.queue_draw()

    def press(self,widget,event):
        if event.button==1:self.drag=(event.x,event.y)

    def motion(self,widget,event):
        if self.drag:
            self.yaw+=(event.x-self.drag[0])*.01;self.pitch+=(event.y-self.drag[1])*.01
            self.drag=(event.x,event.y);self.queue_draw()

    def scroll(self,widget,event):
        self.zoom=max(.1,min(10.,self.zoom*(1.12 if event.direction==Gdk.ScrollDirection.UP else 1/1.12)))
        self.queue_draw();return True

    def on_draw(self,widget,cr):
        w=self.get_allocated_width();h=self.get_allocated_height()
        cr.set_source_rgb(1,1,1);cr.paint()
        if not self.data:
            cr.set_source_rgb(.35,.35,.35);cr.move_to(18,35);cr.show_text('Open a frequency OUTCAR to preview modes.');return False
        factor=min(w,h)*.75/self.extent*self.zoom
        cy,sy=math.cos(self.yaw),math.sin(self.yaw);cx,sx=math.cos(self.pitch),math.sin(self.pitch)
        def project(p):
            x,y,z=[p[j]-self.center[j] for j in range(3)]
            x,z=cy*x+sy*z,-sy*x+cy*z
            y,z=cx*y-sx*z,sx*y+cx*z
            return (w/2+factor*x,h/2-factor*y,z)
        points=[project(p) for p in self.display_positions()]
        # Draw the lattice behind atoms/bonds so the frame cannot hide a mode.
        if self.show_cell:
            cr.set_source_rgb(0,0,0);cr.set_line_width(1.)
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

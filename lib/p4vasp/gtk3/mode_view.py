"""GTK/Cairo ball-and-stick mode preview, with interactive 3D projection.

This is a display copy, independent of the editable native structure window.
No calculation or mode normalization is performed by the renderer.
"""
import math
import cairo
from p4vasp.gtk3 import Gtk, Gdk


class ModeView(Gtk.DrawingArea):
    def __init__(self):
        super().__init__()
        self.set_size_request(250,230)
        self.data=None;self.positions=[];self.bonds=[]
        self.yaw=.4;self.pitch=-.3;self.zoom=1.;self.drag=None
        self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK|Gdk.EventMask.BUTTON_RELEASE_MASK|
                        Gdk.EventMask.POINTER_MOTION_MASK|Gdk.EventMask.SCROLL_MASK)
        self.connect('draw',self.on_draw)
        self.connect('button-press-event',self.press)
        self.connect('button-release-event',lambda *_:setattr(self,'drag',None))
        self.connect('motion-notify-event',self.motion)
        self.connect('scroll-event',self.scroll)

    def set_data(self,data):
        self.data=data;self.positions=data['positions'];self.zoom=1.;self.bonds=[]
        self.center=[(max(p[j] for p in self.positions)+min(p[j] for p in self.positions))/2 for j in range(3)]
        self.extent=max(3.,max(max(p[j] for p in self.positions)-min(p[j] for p in self.positions) for j in range(3))+2.)
        # Spatial bins keep bond discovery bounded for larger structures.
        bins={};step=4.
        for i,p in enumerate(self.positions):
            key=tuple(math.floor(v/step) for v in p)
            for dx in (-1,0,1):
                for dy in (-1,0,1):
                    for dz in (-1,0,1):
                        for k in bins.get((key[0]+dx,key[1]+dy,key[2]+dz),()):
                            distance=sum((p[j]-self.positions[k][j])**2 for j in range(3))
                            if .04<distance<(1.2*(data['radii'][i]+data['radii'][k]))**2:
                                self.bonds.append((i,k))
            bins.setdefault(key,[]).append(i)
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
        points=[]
        for p in self.positions:
            x,y,z=[p[j]-self.center[j] for j in range(3)]
            x,z=cy*x+sy*z,-sy*x+cy*z
            y,z=cx*y-sx*z,sx*y+cx*z
            points.append((w/2+factor*x,h/2-factor*y,z))
        objects=[((points[i][2]+points[j][2])/2,'bond',(i,j)) for i,j in self.bonds]
        objects.extend((p[2],'atom',i) for i,p in enumerate(points))
        for _,kind,item in sorted(objects,key=lambda obj:obj[0]):
            if kind=='bond':
                i,j=item;cr.set_source_rgb(.55,.55,.6);cr.set_line_width(max(2.,factor*.10))
                cr.move_to(*points[i][:2]);cr.line_to(*points[j][:2]);cr.stroke()
            else:
                x,y,_=points[item];radius=max(2.,factor*max(.15,self.data['radii'][item]*.4))
                red,green,blue=self.data['colors'][item]
                gradient=cairo.RadialGradient(x-radius*.3,y-radius*.3,radius*.05,x,y,radius)
                gradient.add_color_stop_rgb(0,min(1,red*.6+.4),min(1,green*.6+.4),min(1,blue*.6+.4))
                gradient.add_color_stop_rgb(.65,red,green,blue)
                gradient.add_color_stop_rgb(1,red*.45,green*.45,blue*.45)
                cr.set_source(gradient);cr.arc(x,y,radius,0,2*math.pi);cr.fill()
        cr.set_source_rgb(.3,.3,.3);cr.move_to(10,h-12)
        cr.show_text('%d atoms | drag: rotate | wheel: zoom'%len(points))
        return False

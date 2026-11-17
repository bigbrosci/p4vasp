"""Real GTK mouse signals and native Show rotation oracle; synthetic data only."""
import copy
import math
import sys
import unittest
import cp4vasp
from p4vasp.gtk3 import Gtk, Gdk
from p4vasp.gtk3.mode_view import ModeView

IDENTITY=((1.,0.,0.),(0.,1.,0.),(0.,0.,1.))


@unittest.skipUnless(Gtk.init_check()[0], 'Requires a display')
class NavigationTest(unittest.TestCase):
    def setUp(self):
        self.errors=[];self.old_hook=sys.excepthook
        sys.excepthook=lambda *args:self.errors.append(args)
        self.window=Gtk.OffscreenWindow();self.window.set_size_request(600,400)
        self.view=ModeView();self.window.add(self.view)
        self.data=dict(positions=[[4,5,6],[5.2,5,6]],cell=[[10,0,0],[0,11,0],[0,0,12]],
                       symbols=['C','O'],radii=[.76,.66],colors=[[.4,.4,.4],[1.,0.,0.]])
        self.before=copy.deepcopy(self.data)
        self.view.set_data(self.data);self.view.rotation=IDENTITY;self.window.show_all()
        while Gtk.events_pending():Gtk.main_iteration_do(False)

    def tearDown(self):
        self.assertEqual(self.data,self.before)
        self.window.destroy()
        sys.excepthook=self.old_hook
        self.assertFalse(self.errors,self.errors)

    def event(self,kind,x,y,button=1,state=0):
        event=Gdk.Event.new(kind);event.window=self.view.get_window()
        event.x=x;event.y=y;event.state=state
        if kind!=Gdk.EventType.MOTION_NOTIFY:event.button=button
        signal={Gdk.EventType.BUTTON_PRESS:'button-press-event',
                Gdk.EventType.BUTTON_RELEASE:'button-release-event',
                Gdk.EventType.MOTION_NOTIFY:'motion-notify-event'}[kind]
        return self.view.emit(signal,event)

    def drag(self,start,end,button=1,state=0):
        self.event(Gdk.EventType.BUTTON_PRESS,*start,button,state)
        self.event(Gdk.EventType.MOTION_NOTIFY,*end,button,state)
        self.event(Gdk.EventType.BUTTON_RELEASE,*end,button,state)

    def native_rotation(self,x,y,z=0.):
        pointer=cp4vasp.createrotmat3da(x,y,z,math.sqrt(x*x+y*y+z*z))
        try:
            # Native Show interprets makerotmat4's matching coefficients as
            # column-major OpenGL, hence transpose this row-major 3x3 oracle.
            return [[cp4vasp.getMatElement3d(pointer,j,i) for j in range(3)] for i in range(3)]
        finally:cp4vasp.deletemat3d(pointer)

    def assertMatrix(self,expected):
        for row,other in zip(self.view.rotation,expected):
            for a,b in zip(row,other):self.assertAlmostEqual(a,b,places=12)

    def test_left_combined_drag_matches_native_and_is_motion_count_independent(self):
        expected=self.native_rotation(-.3,-.6)
        self.event(Gdk.EventType.BUTTON_PRESS,100,100)
        self.event(Gdk.EventType.MOTION_NOTIFY,120,115)
        self.event(Gdk.EventType.MOTION_NOTIFY,160,130)
        self.event(Gdk.EventType.BUTTON_RELEASE,160,130)
        self.assertMatrix(expected)
        self.assertIsNone(self.view.drag)
        previous=self.view.rotation
        self.drag((100,100),(110,120))
        delta=self.native_rotation(-.2,-.1)
        combined=[[sum(delta[i][k]*previous[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
        self.assertMatrix(combined)

    def test_ctrl_left_screen_spin_and_shift_does_not_rotate(self):
        cx,cy=self.view.get_allocated_width()/2,self.view.get_allocated_height()/2
        self.drag((cx+80,cy),(cx,cy+80),state=Gdk.ModifierType.CONTROL_MASK)
        self.assertMatrix(self.native_rotation(0.,0.,math.pi/2))
        before=self.view.rotation
        self.drag((100,100),(150,180),state=Gdk.ModifierType.SHIFT_MASK)
        self.assertEqual(self.view.rotation,before)

    def test_middle_pan_and_release_outside_use_show_sensitivity(self):
        self.drag((20,30),(80,70),button=2)
        factor=625/self.view.get_allocated_width()
        self.assertAlmostEqual(self.view.pan[0],60*factor)
        self.assertAlmostEqual(self.view.pan[1],-40*factor)
        self.assertEqual(self.view.rotation,IDENTITY)
        self.view.set_positions([[4.1,5,6],[5.1,5,6]])
        self.assertAlmostEqual(self.view.pan[0],60*factor)
        self.event(Gdk.EventType.BUTTON_PRESS,10,10,2)
        self.event(Gdk.EventType.BUTTON_RELEASE,-10,-20,2)
        self.assertIsNone(self.view.drag)

    def test_right_horizontal_zoom_vertical_no_zoom_and_cancel(self):
        self.drag((100,100),(200,150),button=3)
        self.assertAlmostEqual(self.view.zoom,math.exp(.5))
        zoom=self.view.zoom
        self.drag((100,100),(100,200),button=3)
        self.assertAlmostEqual(self.view.zoom,zoom)
        self.event(Gdk.EventType.BUTTON_PRESS,10,10,3)
        self.view.emit('grab-broken-event',Gdk.Event.new(Gdk.EventType.GRAB_BROKEN))
        self.assertIsNone(self.view.drag)
        self.view.fit();self.assertEqual(self.view.pan,(0.,0.,0.));self.assertEqual(self.view.zoom,1.)

    def test_hydrogen_ball_size_does_not_change_bonds_or_element_data(self):
        from p4vasp.util import getAtomtypes
        from p4vasp.viewer_style import covalent_atomtypes, BOND_FACTOR
        table=getAtomtypes();h=table.getRecordForElement('H');c=table.getRecordForElement('C')
        before=(h.radius,h.covalent,c.radius,c.covalent)
        cutoff=BOND_FACTOR*(c.covalent+h.covalent)
        data=dict(positions=[[5,5,5],[5+.9*cutoff,5,5],[5-1.1*cutoff,5,5]],
                  cell=[[10,0,0],[0,10,0],[0,0,10]],symbols=['C','H','H'],
                  radii=[c.covalent,h.covalent,h.covalent],colors=[[.4,.4,.4],[1,1,1],[1,1,1]])
        original=copy.deepcopy(data)
        self.view.set_data(data)
        self.assertEqual(self.view.radii,[c.covalent,h.covalent,h.covalent])
        self.assertAlmostEqual(self.view.ball_radii[1],1.5*h.covalent)
        self.assertAlmostEqual(self.view.ball_radii[0],c.covalent)
        self.assertEqual({tuple(sorted(pair)) for pair in self.view.bonds},{(0,1)})
        native=covalent_atomtypes()
        self.assertAlmostEqual(native.getRecordForElement('H').radius,1.5*h.covalent)
        self.assertEqual(native.getRecordForElement('H').covalent,h.covalent)
        self.assertEqual((h.radius,h.covalent,c.radius,c.covalent),before)
        self.assertEqual(data,original)
        self.view.set_cell_visible(False)
        self.view.queue_draw()
        import time
        for _ in range(12):
            while Gtk.events_pending():Gtk.main_iteration_do(False)
            time.sleep(.01)
        self.window.get_pixbuf().savev('/tmp/p4vasp-hydrogen-radius.png','png',[],[])

    def test_scroll_directions_and_actual_panned_rotated_drawing(self):
        event=Gdk.Event.new(Gdk.EventType.SCROLL);event.window=self.view.get_window()
        event.direction=Gdk.ScrollDirection.UP
        self.view.emit('scroll-event',event);self.assertAlmostEqual(self.view.zoom,1.12)
        event.direction=Gdk.ScrollDirection.LEFT
        self.view.emit('scroll-event',event);self.assertAlmostEqual(self.view.zoom,1.12)
        event.direction=Gdk.ScrollDirection.SMOOTH;event.delta_x=0.;event.delta_y=2.
        self.view.emit('scroll-event',event);self.assertAlmostEqual(self.view.zoom,1/1.12)
        self.drag((100,100),(140,120));self.drag((100,100),(130,115),button=2)
        self.view.queue_draw()
        import time
        for _ in range(12):
            while Gtk.events_pending():Gtk.main_iteration_do(False)
            time.sleep(.01)
        self.window.get_pixbuf().savev('/tmp/p4vasp-mode-navigation.png','png',[],[])


if __name__=='__main__':unittest.main()

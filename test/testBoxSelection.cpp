// Native FLTK/OpenGL regression. Run with test/run_box_selection.py after building.
#include <p4vasp/VisMain.h>
#include <p4vasp/VisWindow.h>
#include <p4vasp/VisFLWindow.h>
#include <p4vasp/VisNavDrawer.h>
#include <p4vasp/VisStructureDrawer.h>
#include <p4vasp/VisBackEvent.h>
#include <FL/Fl.H>
#include <GL/glu.h>
#include <cassert>
#include <cstdio>
#include <vector>

static void render(VisWindow &w){
  for(int i=0;i<3;i++){ VisCheck(); Fl::wait(0.02); }
  w.win->make_current(); glDrawBuffer(GL_BACK); w.draw();
}
static void event(VisWindow &w,int type,int x,int y,int state=0,int key=0){
  Fl::e_x=x; Fl::e_y=y; Fl::e_state=state;
  Fl::e_keysym=(type==FL_PUSH || type==FL_RELEASE) ? FL_Button+FL_LEFT_MOUSE : key;
  int handled=w.win->handle(type);
  if(type==FL_PUSH || type==FL_DRAG || type==FL_RELEASE || type==FL_KEYBOARD)
    assert(handled==1);
}
static void box(VisWindow &w,int x0,int y0,int x1,int y1){
  event(w,FL_PUSH,x0,y0,FL_SHIFT|FL_BUTTON1);
  event(w,FL_DRAG,x1,y1,FL_BUTTON1); // Shift may be released during drag.
  render(w);
  event(w,FL_RELEASE,x1,y1);
  render(w);
}
static void screenshot(VisWindow &w,const char *path){
  render(w);
  std::vector<unsigned char> pixels(w.w*w.h*3);
  glPixelStorei(GL_PACK_ALIGNMENT,1); glReadBuffer(GL_BACK);
  glReadPixels(0,0,w.w,w.h,GL_RGB,GL_UNSIGNED_BYTE,&pixels[0]);
  FILE *f=fopen(path,"wb"); assert(f);
  fprintf(f,"P6\n%d %d\n255\n",w.w,w.h);
  for(int y=w.h-1;y>=0;y--) fwrite(&pixels[y*w.w*3],1,w.w*3,f);
  fclose(f);
}
int main(int argc,char **argv){
  VisInit();
  Structure s;
  FILE *f=tmpfile();
  fputs("Box selection test\n1\n8 0 0\n0 8 0\n0 0 8\nH\n5\nCartesian\n-4 0 0\n0 0 0\n0 0 -3\n4 0 0\n0 4 0\n",f);
  rewind(f); s.read(f); fclose(f);
  VisWindow w(50,50,600,500,"p4vasp box-selection regression");
  VisNavDrawer nav;
  VisStructureDrawer atoms;
  nav.bg_red=nav.bg_green=nav.bg_blue=1;
  nav.append(&atoms); w.setDrawer(&nav); atoms.setStructure(&s);
  for(int i=0;i<5;i++){
    atoms.info->getRecord(i)->radius=0.7;
    atoms.info->getRecord(i)->red=0.2;
    atoms.info->getRecord(i)->green=0.4;
    atoms.info->getRecord(i)->blue=0.8;
  }
  atoms.info->getRecord(4)->hidden=1;
  render(w);
  VisBackEventQueue *queue=VisBackEventQueue::get();
  while(queue->current()) queue->pop();
  // Select both front and back atoms at the same screen position.
  event(w,FL_PUSH,275,225,FL_SHIFT|FL_BUTTON1);
  event(w,FL_DRAG,325,275,FL_SHIFT|FL_BUTTON1);
  if(argc>1) screenshot(w,argv[1]);
  event(w,FL_RELEASE,325,275); render(w);
  assert(atoms.getSelectedCount()==2);
  int notifications=0;
  while(queue->current()){
    if(queue->current()->type==BE_SELECTED) notifications++;
    queue->pop();
  }
  assert(notifications==1); // One batch refresh, not one per atom.
  assert(nav.getRotMatElement(0,0)==1.0);
  assert(atoms.findSelectedAtom(1,0,0,0)>=0 && atoms.findSelectedAtom(2,0,0,0)>=0);
  box(w,325,275,275,225); assert(atoms.getSelectedCount()==2); // reversed, duplicate
  box(w,175,225,225,275); assert(atoms.getSelectedCount()==3); // additive
  box(w,0,0,600,500); assert(atoms.getSelectedCount()==4); // hidden excluded
  atoms.removeSelectedAll();
  event(w,FL_PUSH,0,0,FL_SHIFT|FL_BUTTON1);
  event(w,FL_DRAG,600,500,FL_SHIFT|FL_BUTTON1);
  event(w,FL_KEYBOARD,600,500,0,FL_Escape);
  event(w,FL_RELEASE,600,500); render(w);
  assert(atoms.getSelectedCount()==0);
  box(w,300,250,301,251); assert(atoms.getSelectedCount()==0); // click jitter
  box(w,10,10,30,30); assert(atoms.getSelectedCount()==0); // empty rectangle
  // FLTK may deliver Escape as a shortcut, even after the mouse is released.
  Fl::e_keysym=FL_Escape; Fl::e_state=0;
  int escape_handled=Fl::handle(FL_SHORTCUT,w.win);
  fprintf(stderr,"Idle Escape: handled=%d visible=%d\n",escape_handled,w.win->shown());
  assert(w.win->shown());
  assert(escape_handled==1);
  event(w,FL_KEYBOARD,300,250,0,FL_Escape);
  Fl::e_keysym=FL_Escape;
  assert(w.win->handle(FL_KEYUP)==1);
  assert(w.win->shown());
  while(queue->current()){
    assert(queue->current()->type!=BE_WIN_CLOSE);
    queue->pop();
  }
  // Shortcut delivery during a drag also cancels; repeated Escape stays safe.
  event(w,FL_PUSH,0,0,FL_SHIFT|FL_BUTTON1);
  event(w,FL_DRAG,600,500,FL_SHIFT|FL_BUTTON1);
  Fl::e_keysym=FL_Escape; Fl::e_state=FL_SHIFT;
  assert(Fl::handle(FL_SHORTCUT,w.win)==1);
  event(w,FL_RELEASE,600,500); render(w);
  assert(atoms.getSelectedCount()==0 && w.win->shown());
  for(int i=0;i<3;i++){
    Fl::e_keysym=FL_Escape; Fl::e_state=0;
    assert(Fl::handle(FL_KEYBOARD,w.win)==1);
    assert(w.win->shown());
  }
  box(w,275,225,325,275); assert(atoms.getSelectedCount()==2);
  atoms.removeSelectedAll();
  // Space still toggles one atom, and unmodified drag still rotates.
  event(w,FL_KEYBOARD,200,250,0,' '); assert(atoms.getSelectedCount()==1);
  event(w,FL_KEYBOARD,200,250,0,' '); assert(atoms.getSelectedCount()==0);
  event(w,FL_PUSH,100,100,FL_BUTTON1);
  event(w,FL_DRAG,160,120,FL_BUTTON1);
  event(w,FL_RELEASE,160,120); render(w);
  assert(nav.getRotMatElement(0,0)!=1.0);
  nav.setHome(); render(w);
  // Periodic image identity is retained, with no duplicate additions.
  atoms.setMultiple(2,1,1); render(w);
  box(w,0,0,600,500); assert(atoms.getSelectedCount()==7);
  box(w,0,0,600,500); assert(atoms.getSelectedCount()==7);
  bool image=false;
  for(int i=0;i<atoms.getSelectedCount();i++) if(atoms.getSelected(i)->nx==1) image=true;
  assert(image);
  atoms.removeSelectedAll(); atoms.setMultiple(1,1,1);
  w.resize(50,50,900,650); render(w);
  nav.setRightView(); render(w);
  box(w,0,0,900,650); assert(atoms.getSelectedCount()==4);
  if(argc>2) screenshot(w,argv[2]);
  atoms.removeSelectedAll();
  event(w,FL_PUSH,0,0,FL_SHIFT|FL_BUTTON1);
  w.resize(50,50,700,550); render(w);
  event(w,FL_RELEASE,700,550); assert(atoms.getSelectedCount()==0);
  // Perspective and zoom still produce matching screen projections.
  nav.setHome(); nav.setPerspective(1); nav.setZoom(1.4); render(w);
  box(w,0,0,700,550); assert(atoms.getSelectedCount()==4);
  atoms.removeSelectedAll();
  // Losing focus cancels the gesture without changing the selection.
  event(w,FL_PUSH,0,0,FL_SHIFT|FL_BUTTON1);
  event(w,FL_UNFOCUS,0,0);
  assert(atoms.getSelectedCount()==0);
  // Empty structures must not select or crash.
  atoms.setStructure(NULL); render(w); box(w,0,0,700,550);
  // Escape is safe before/after a structure drawer is attached too.
  w.setDrawer(NULL);
  Fl::e_keysym=FL_Escape; Fl::e_state=0;
  assert(Fl::handle(FL_SHORTCUT,w.win)==1 && w.win->shown());
  // The explicit window close callback still works.
  w.win->do_callback();
  assert(!w.win->shown());
  puts("PASS: box selection, additive/deduplication, hidden/depth/replicas, Esc, resize, Side view, Space and rotation");
  fflush(stdout);
  // Native drawer/window ownership is managed by the app in production.
  _Exit(0);
}

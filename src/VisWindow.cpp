/*
 *  p4vasp is a GUI-program and library for processing outputs of the
 *  Vienna Ab-inition Simulation Package (VASP)
 *  (see http://cms.mpi.univie.ac.at/vasp/Welcome.html)
 *  
 *  Copyright (C) 2003  Orest Dubay <odubay@users.sourceforge.net>
 *
 *  This program is free software; you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation; either version 2 of the License, or
 *  (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *   You should have received a copy of the GNU General Public License
 *  along with this program; if not, write to the Free Software
 *  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */

#include <p4vasp/VisStructureDrawer.h>
#include <stdio.h>
#include <FL/gl.h>
#include <FL/Fl.H>

#include <p4vasp/utils.h>
#include <p4vasp/VisWindow.h>
#include <p4vasp/VisEvent.h>
#include <p4vasp/VisDrawer.h>
#include <p4vasp/Exceptions.h>
#include <p4vasp/VisMain.h>
#include <p4vasp/VisNavDrawer.h>
#include <p4vasp/VisBackEvent.h>
#include <algorithm>
#include <cmath>
#include <map>
#include <set>
#include <sstream>
#include <string>

/* ***************************************************************** *
 *  This is a HACK to compensate that GL_BGR definition is missing   *
 *  in FL/gl.h on some systems (windows/MinGW in paricular).         *
 * ***************************************************************** */
#ifndef GL_BGR
#define GL_BGR                                  0x80E0 
#endif

MUTEX(VisWindow_mutex);


VisWindow *VisWindow::root = NULL;


const char *VisWindow::getClassName(){
  return "VisWindow";
}

VisWindow::VisWindow(int x, int y, int w, int h,const char *title){
#if VERBOSE>0
  printf("new VisWindow()\n");
#endif  
  MUTEX_INIT(local_mutex);
  local_lock();
  this->x=x;
  this->y=y;
  this->w=w;
  this->h=h;
  drawer=NULL;
  if (title==NULL){
    this->title=NULL;
  }
  else{
    this->title=clone(title);
  }
  
  global_lock();
  next=NULL;

  if (VisWindow::root == NULL){
    VisWindow::root=this;
  }
  else{
    next=NULL;
    VisWindow::getLastWindow_nolock()->next=this;
  }
  this->win=NULL;
  VisEvent::add(VE_CREATE_WINDOW,this);
  local_unlock();
  global_unlock();
  VisSync();
#if VERBOSE>0
  printf("new VisWindow() -\n");
#endif  
}

const char *VisWindow::getTitle(){
  return title;
}

void VisWindow::setTitle(const char *title){
#if VERBOSE>0
  printf("VisWindow::setTitle('%s');\n",title);
#endif
  local_lock();
  if (this->title != NULL){
    delete []this->title;
  }
  if (title==NULL){
    this->title=NULL;
    VisEvent::add(VE_SET_WINDOW_TITLE,this,NULL);
  }
  else{
    this->title=clone(title);
    VisEvent::add(VE_SET_WINDOW_TITLE,this,clone(title));
  }
  
  local_unlock();
}

VisWindow *VisWindow::getFirstWindow(){
#if CHECK>0
  if (VisWindow::root==NULL){
    NTHROW_NP_EXC("No first window in VisWindow::getFirstWindow().");
  }
#endif  
  return VisWindow::root;  
}

VisWindow *VisWindow::getFirstWindow_nolock(){
#if CHECK>0
  if (VisWindow::root==NULL){
    NTHROW_NP_EXC("No first window in VisWindow::getFirstWindow_nolock().");
  }
#endif  
  return VisWindow::root;  
}

VisWindow *VisWindow::getLastWindow(){
  global_lock();
  VisWindow *l=getLastWindow_nolock();
  global_unlock();
  return l;
}

VisWindow *VisWindow::getLastWindow_nolock(){
  VisWindow *last = VisWindow::root;
#if CHECK>0
  if (last==NULL){
    NTHROW_NP_EXC("No first window in VisWindow::getLastWindow().");
  }
#endif  
  while (last->next!=NULL){
    last=last->next;
  }
  return last;  
}


int VisWindow::windowsCount(){
  global_lock();
  int l=windowsCount_nolock();
  global_unlock();
  return l;  
}

int VisWindow::windowsCount_nolock(){
  VisWindow *last = VisWindow::root;
#if CHECK>0
  if (last==NULL){
    NTHROW_NP_EXC("No first window in VisWindow::windowsCount().");
  }
#endif  
  int c=0;
  
  while (last!=NULL){
    last=last->next;
    c++;
  }
  return c;  
}


VisWindow *VisWindow::getWindow(int n){
  global_lock();
  VisWindow *l=getWindow_nolock(n);
  global_unlock();
  return l;
}

VisWindow *VisWindow::getWindow_nolock(int n){
  int count = windowsCount_nolock();
  if (n<0){
    n+=count;
  }
#if CHECK>0  
  if ((n<0)||(n>=count)){
    NTHROW_R_EXC("Index out of range in VisWindow::getWindow().",0,count,n);
  }
#endif  
  VisWindow *last = VisWindow::root;
#if CHECK>1
  if (last==NULL){
    NTHROW_NP_EXC("No first window in VisWindow::getWindow().");
  }
#endif  
  int c=0;
  
  while (last!=NULL){
    if (c==n){
      return last;
    }
    last=last->next;
    c++;
  }
#if CHECK>0
  if (n<0){
    NTHROW_EXC("Invalid index in VisWindow::getWindow(). (window not found)");
  }
#endif  
  return NULL;
}


VisWindow *VisWindow::getWindowByOutput(VisFLWindow *w){
  global_lock();
  VisWindow *l=getWindowByOutput_nolock(w);
  global_unlock();
  return l;
}

VisWindow *VisWindow::getWindowByOutput_nolock(VisFLWindow *w){
#if CHECK>0
  if (w==NULL){
    NTHROW_NP_EXC("NULL argument in VisWindow::getWindowByOutput()");
  }
#endif  
  VisWindow *last = VisWindow::root;
  
  while (last!=NULL){
    if (last->win==w){
      return last;
    }
    last=last->next;
  }
#if CHECK>0  
  NTHROW_EXC("Window not found in VisWindow::getWindowByOutput().");
#endif  
  return NULL;
}


int VisWindow::getWindowIndex(VisWindow *w){
  global_lock();
  int l=getWindowIndex_nolock(w);
  global_unlock();
  return l;  
}

int VisWindow::getWindowIndex_nolock(VisWindow *w){
  if (w==NULL){
    return -1;
  }

  VisWindow *last = VisWindow::root;
#if CHECK>0
  if (last==NULL){
    NTHROW_NP_EXC("No first window in VisWindow::getWindowIndex().");
  }
#endif  
  int c=0;
  
  while (last!=NULL){
    if (last==w){
      return c;
    }
    last=last->next;
    c++;
  }
  
  return -1;
}

VisWindow *VisWindow::getNextWindow(){
  global_lock();
  VisWindow *l=getNextWindow_nolock();
  global_unlock();
  return l;
}

VisWindow *VisWindow::getNextWindow_nolock(){
  return next;
}

VisWindow *VisWindow::getPreviousWindow(){
  global_lock();
  VisWindow *l=getPreviousWindow_nolock();
  global_unlock();
  return l;
}

VisWindow *VisWindow::getPreviousWindow_nolock(){
  VisWindow *last = VisWindow::root;
  if (last==this){
    return NULL;
  }
  
  while (last!=NULL){
    if (last->next==this){
      return last;
    }
    last=last->next;
  }
  
  return NULL;
}



VisWindow::~VisWindow(){
#if VERBOSE>0
  printf("~VisWindow()\n");
#endif  
  global_lock();
  local_lock();
  if (drawer!=NULL){
    drawer->setWindow(NULL);
    drawer=NULL;
  }
  if (win!=NULL){
    VisEvent::add(VE_DESTROY_WINDOW,this);
  }
  win=NULL;
  VisWindow *prev = getPreviousWindow_nolock();
  if (prev==NULL){
#if CHECK>1
    if (this!=VisWindow::root){
      fprintf(stderr,
      "Warning: getPreviousWindow()!=NULL and this!=VisWindow::root"
      " in VisWindow::~VisWindow().\n");
    }
#endif
    VisWindow::root=next;
  }
  else{
    prev->next=next;
  }
  local_unlock();
  global_unlock();
#if VERBOSE>0
  printf("~VisWindow() -\n");
#endif  
}


void VisWindow::deleteWindow(int n){
  global_lock();
  deleteWindow_nolock(n);
  global_unlock();
}

void VisWindow::deleteWindow_nolock(int n){
  VisWindow *p = getWindow_nolock(n);
  if (p!=NULL){
    delete p;
  }
}

VisWindow **VisWindow::getAllWindows(){
  global_lock();
  VisWindow **l=getAllWindows_nolock();
  global_unlock();
  return l;  
}

VisWindow **VisWindow::getAllWindows_nolock(){
  VisWindow **buff = new VisWindow *[VisWindow::windowsCount_nolock()+1];
#if CHECK>0
  if (buff==NULL){
    NTHROW_MA_EXC("VisWindow::getAllWindows() failed.");
  }
#endif
  VisWindow *last = VisWindow::root;
  int c=0;
  
  while (last!=NULL){
    buff[c]=last;
    last=last->next;
    c++;
  }
  buff[c]=NULL;
  return buff;
}

void VisWindow::deleteAllWindows(){
  global_lock();
  VisWindow **buff = getAllWindows_nolock();
  if (buff==NULL){
    NTHROW_NP_EXC("getAllWindows() failed => VisWindow::deleteAllWindows() failed.");
  }
  else{
    for (int i=0; buff[i]!=NULL; i++){
      delete buff[i];
    }
  }
  delete buff;
  global_unlock();
}

void VisWindow::init(){
  local_lock();
#if VERBOSE>0
  printf("VisWindow::init()\n");
#endif    
  for (VisDrawer *d=drawer; d!=NULL; d=d->getNext()){
    d->init();
  }
#if VERBOSE>0
  printf("VisWindow::init() -\n");
#endif    
  local_unlock();
}

void VisWindow::assure_init(){
  local_lock();
#if VERBOSE>0
  printf("VisWindow::assure_init()\n");
#endif    
  for (VisDrawer *d=drawer; d!=NULL; d=d->getNext()){
    if (!d->is_init){
      d->init();
    }
  }
#if VERBOSE>0
  printf("VisWindow::assure_init() -\n");
#endif    
  local_unlock();
}

static std::string countElement(const char *name){
  std::string element=name;
  element.erase(0,element.find_first_not_of(" \t"));
  if (!element.empty()) element.erase(element.find_last_not_of(" \t")+1);
  return element.empty()?"?":element;
}

static void drawCountPanel(const std::vector<std::string> &order,const std::map<std::string,int> &counts,
                           const std::string &prefix,int viewportWidth,bool right){
  const double available=(viewportWidth-32)/2.;
  std::vector<std::string> lines;
  std::string line=prefix;
  bool first=true;
  for(size_t i=0;i<order.size();i++){
    std::map<std::string,int>::const_iterator value=counts.find(order[i]);
    if(value==counts.end() || value->second<=0) continue;
    std::ostringstream item;item<<value->first<<":"<<value->second;
    std::string next=line.empty()?item.str():line+(first?" ":", ")+item.str();
    if(!line.empty() && gl_width(next.c_str())>available){lines.push_back(line);line=item.str();}
    else line=next;
    first=false;
  }
  if(first) line=right?"Selected:0":"Atoms:0";
  if(!line.empty()) lines.push_back(line);
  double width=0;for(size_t i=0;i<lines.size();i++) width=std::max(width,gl_width(lines[i].c_str()));
  double left=right?viewportWidth-width-16:4;
  glColor4f(1,1,1,.9f);
  glBegin(GL_QUADS);glVertex2d(left,4);glVertex2d(left+width+16,4);
  glVertex2d(left+width+16,lines.size()*18+10);glVertex2d(left,lines.size()*18+10);glEnd();
  glColor3f(0,0,0);
  for(size_t i=0;i<lines.size();i++){
    const double x=right?viewportWidth-10-gl_width(lines[i].c_str()):10;
    glRasterPos2d(x,10+(lines.size()-1-i)*18);gl_draw(lines[i].c_str());
  }
}

// Screen-space counts: left is the base structure, right is unique selected atoms.
static void drawAtomCounts(VisStructureDrawer *atoms){
  Structure *source=atoms->getStructure();
  std::vector<std::string> order;
  std::map<std::string,int> counts,selected;
  if(source && source->info){
    for(int i=0;i<source->info->len();i++){
      AtomtypesRecord *record=source->info->getRecord(i);
      if(record->atomspertype<=0) continue;
      std::string element=countElement(record->element);
      if(!counts.count(element)) order.push_back(element);
      counts[element]+=record->atomspertype;
    }
    std::set<int> unique;
    for(int i=0;i<atoms->getSelectedCount();i++){
      int atom=atoms->getSelected(i)->atom;
      if(atom>=0 && atom<source->len() && unique.insert(atom).second){
        selected[countElement(source->info->getRecordForAtom(atom)->element)]++;
      }
    }
  }
  GLint viewport[4],mode;
  glGetIntegerv(GL_VIEWPORT,viewport);glGetIntegerv(GL_MATRIX_MODE,&mode);
  glPushAttrib(GL_ALL_ATTRIB_BITS);
  glDisable(GL_DEPTH_TEST);glDisable(GL_LIGHTING);glDisable(GL_TEXTURE_2D);glDisable(GL_FOG);
  glMatrixMode(GL_PROJECTION);glPushMatrix();glLoadIdentity();
  glOrtho(0,viewport[2],0,viewport[3],-1,1);
  glMatrixMode(GL_MODELVIEW);glPushMatrix();glLoadIdentity();
  gl_font(FL_HELVETICA,14);
  glEnable(GL_BLEND);glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA);
  drawCountPanel(order,counts,"",viewport[2],false);
  drawCountPanel(order,selected,"Selected:",viewport[2],true);
  glPopMatrix();glMatrixMode(GL_PROJECTION);glPopMatrix();glMatrixMode(mode);
  glPopAttrib();
}

void VisWindow::draw(){
#if VERBOSE>0
  printf("VisWindow::draw()\n");
#endif
  assure_init();
  local_lock();
  if (drawer!=NULL){
    for (VisDrawer *d=drawer; d!=NULL; d=d->getNext()){
#if VERBOSE>0
      printf("VisWindow::draw() drawer call\n");
#endif    
      d->draw();
#if VERBOSE>0
      printf("VisWindow::draw() drawer call -\n");
#endif    
    }
  }
  else{
#if VERBOSE>0
    printf("Warning: No drawer in VisWindow::draw().\n");
#endif    
    glClearColor(0.0, 0.0, 0.5, 0.0);
    glShadeModel(GL_SMOOTH);
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);  
  }
  // Draw the selection rectangle last, above atoms, arrows and isosurfaces.
  for (VisDrawer *d=drawer;d!=NULL;d=d->getNext()){
    VisStructureDrawer *structure=dynamic_cast<VisStructureDrawer *>(d);
    if (structure) structure->drawBoxSelection();
  }
  for (VisDrawer *d=drawer;d!=NULL;d=d->getNext()){
    VisStructureDrawer *structure=dynamic_cast<VisStructureDrawer *>(d);
    if (structure){drawAtomCounts(structure);break;}
  }
  glFinish();
  local_unlock();  
#if VERBOSE>0
  printf("VisWindow::draw() -\n");
#endif    
}

int VisWindow::handle(int event){
  local_lock();
  if (event==FL_KEYBOARD && !(Fl::event_state()&(FL_CTRL|FL_ALT|FL_META|FL_BUTTONS))){
    const int key=Fl::event_key();
    if (key==FL_Delete && !(Fl::event_state()&FL_SHIFT)){
      for (VisDrawer *d=drawer;d!=NULL;d=d->getNext()){
        VisStructureDrawer *atoms=dynamic_cast<VisStructureDrawer *>(d);
        if (!atoms || !atoms->getSelectedCount() || !atoms->getStructure()) continue;
        std::vector<int> selected;
        for(int i=0;i<atoms->getSelectedCount();i++) selected.push_back(atoms->getSelected(i)->atom);
        std::sort(selected.begin(),selected.end());
        selected.erase(std::unique(selected.begin(),selected.end()),selected.end());
        // Reuse the snapshotted edit event; index=2 deletes, dx guards stale queued keys.
        VisBackEvent *request=VisBackEvent::createAtomMove(this,atoms->getStructure()->len(),0,0,selected);
        request->index=2;VisBackEventQueue::get()->append(request);
        local_unlock();return 1;
      }
    }
    if (key==FL_Left || key==FL_Right || key==FL_Up || key==FL_Down){
      VisNavDrawer *nav=NULL;
      VisStructureDrawer *atoms=NULL;
      for (VisDrawer *d=drawer;d!=NULL;d=d->getNext()){
        if (!nav) nav=dynamic_cast<VisNavDrawer *>(d);
        if (!atoms) atoms=dynamic_cast<VisStructureDrawer *>(d);
      }
      if (nav && atoms && atoms->getSelectedCount()){
        std::vector<int> selected;
        for (int i=0;i<atoms->getSelectedCount();i++) selected.push_back(atoms->getSelected(i)->atom);
        std::sort(selected.begin(),selected.end());
        selected.erase(std::unique(selected.begin(),selected.end()),selected.end());
        const bool rotate=(Fl::event_state()&FL_SHIFT)!=0;
        const bool horizontal=(key==FL_Left || key==FL_Right);
        const int row=rotate ? (horizontal ? 1 : 0) : (horizontal ? 0 : 1);
        const double sign=(key==FL_Left || (rotate ? key==FL_Up : key==FL_Down)) ? -1. : 1.;
        double delta[3],length=0.;
        for (int j=0;j<3;j++){delta[j]=sign*nav->getRotMatElement(row,j);length+=delta[j]*delta[j];}
        length=sqrt(length);
        if (length>1e-12){
          VisBackEventQueue::get()->append(VisBackEvent::createAtomMove(this,
            delta[0]/length,delta[1]/length,delta[2]/length,selected,rotate));
          local_unlock();
          return 1;
        }
      }
    }
  }
  for (VisDrawer *d=drawer;d!=NULL;d=d->getNext()){
    VisStructureDrawer *structure=dynamic_cast<VisStructureDrawer *>(d);
    if (structure && structure->handleBoxSelection(event)){
      local_unlock();
      redraw();
      return 1;
    }
  }
  for (VisDrawer *d=drawer; d!=NULL; d=d->getNext()){
    int r = d->handle(event);
    if (r) {
      local_unlock();
      redraw();
      return r;
    }
  }
  local_unlock();  
  return 0;
}


void VisWindow::setOutputWindow(VisFLWindow *w){
  local_lock();
  win=w;
  local_unlock();
}

void init_mutexes(){
  MUTEX_INIT(VisWindow_mutex);
}

void destroy_mutexes(){
  MUTEX_DESTROY(VisWindow_mutex);
}

void VisWindow::global_lock(){
  MUTEX_LOCK(VisWindow_mutex);
}

void VisWindow::global_unlock(){
  MUTEX_UNLOCK(VisWindow_mutex);
}


void VisWindow::position(int x,int y){
  local_lock();
  this->x=x;
  this->y=y;
  VisEvent::add(VE_SET_WINDOW_POSITION,this);
  local_unlock();
}

void VisWindow::size(int w,int h){
  local_lock();
  this->w=w;
  this->h=h;
  VisEvent::add(VE_SET_WINDOW_SIZE,this);
  local_unlock();
}

void VisWindow::resize(int x,int y,int w,int h){
  local_lock();
  this->x=x;
  this->y=y;
  this->w=w;
  this->h=h;
  VisEvent::add(VE_RESIZE_WINDOW,this);
  local_unlock();
}

void VisWindow::resize(){
  local_lock();
  VisEvent::add(VE_RESIZE_WINDOW,this);
  local_unlock();
}

void VisWindow::show(){
  local_lock();
  VisEvent::add(VE_SHOW_WINDOW,this);
  local_unlock();
}

void VisWindow::hide(){
  local_lock();
  VisEvent::add(VE_HIDE_WINDOW,this);
  local_unlock();
}

void VisWindow::redraw(){
  local_lock();
  VisEvent::add(VE_REDRAW_WINDOW,this);
  local_unlock();
}

void VisWindow::setDrawer(VisDrawer *d){
#if VERBOSE>0
  printf("VisWindow(%s)::setDrawer(%p)\n",title,d);
#endif
  local_lock();
  if (drawer!=NULL){
    drawer->setWindow(NULL);
  }
#if CHECK>0
  if (d!=NULL){
    if (d->getPrevious()!=NULL){
      THROW_EXC("D is not the first drawer of drawers linked to D in VisWindow::setDrawer(D).");
    }
  }  
#endif

  drawer=d;

  if (d!=NULL){
    d->setWindow(this);
  }
#if VERBOSE>0
  printf("VisWindow(%s)::setDrawer(%p) -\n",title,d);
#endif

  local_unlock();  
}

VisDrawer *VisWindow::getDrawer(){
  return drawer;
}

int VisWindow::saveScreenshot(char *path){
  unsigned char *pixels;
  FILE * f;
  GLint viewport[4];
  draw();
  local_lock();
  glGetIntegerv(GL_VIEWPORT, viewport);
//  printf("x:%d y:%d Width:%d Height:%d\n",viewport[0],viewport[1],viewport[2],viewport[3]);

  int width =viewport[2];
  int height=viewport[3];
  
  pixels = new unsigned char[width*height*3];
  if (pixels==NULL){
    THROW_MA_EXC("Can not allocate pixels.");
  }

  glReadPixels(0,0, width, height, GL_BGR, GL_UNSIGNED_BYTE, pixels);

  f=fopen(path, "wb");
  if(f==NULL){
    THROW_NP_EXC("Error opening file in saveScreenshot.");
  }

  // uncompressed .tga headder
  unsigned char TGAheader[12]={0,0,2,0,0,0,0,0,0,0,0,0};
  if (fwrite(TGAheader, sizeof(unsigned char), 12, f)!=12){
    THROW_EXC("Error writing tga headder (part 1).");  
  }

  unsigned char header[6];
//  printf("Width:%d Height:%d\n",width,height);
  header[0]=(int)(width%256); //width
  header[1]=(int)(width/256);
  header[2]=(int)(height%256); //height
  header[3]=(int)(height/256);
  header[4]=24;                //bpp
  header[5]=0;                 //nothing

  if (fwrite(header, sizeof(unsigned char), 6, f)!=6){
    THROW_EXC("Error writing tga headder (part 2).");
  }
  if (fwrite(pixels, sizeof(unsigned char), 
                 width*height*3, f)!=(unsigned) width*height*3){
    THROW_EXC("Error writing pixels to the tga file.");
  }

  fclose(f);
  delete [] pixels;
  local_unlock();
  return 0;
}


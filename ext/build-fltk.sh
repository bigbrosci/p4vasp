#!/usr/bin/sh

EXT=$PWD
FLTK_VERSION=${FLTK_VERSION:-1.3.11}
export CFLAGS=-fPIC
export CXXFLAGS=-fPIC
cd fltk-$FLTK_VERSION
./configure --enable-gl --prefix $EXT
make
make install
make clean
cd ..


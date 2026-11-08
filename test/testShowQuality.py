"""Native cell stroke coverage and state isolation on a synthetic skew cell."""
from io import StringIO
import os
from pathlib import Path
import tempfile
import time
import traceback
import numpy as np
import cp4vasp
from p4vasp.Structure import Structure
from p4vasp.StructureWindow import StructureWindow
from p4vasp.viewer_style import covalent_atomtypes


def main():
    cp4vasp.VisInit()
    source=Structure();source.read(StringIO('quality\n1\n8 0 0\n2 7 0\n1 1 8\nCu\n8\nDirect\n0 0 0\n1 0 0\n0 1 0\n1 1 0\n0 0 1\n1 0 1\n0 1 1\n1 1 1\n'))
    window=StructureWindow(w=600,h=500,title='Cell antialias check',atomtypes=covalent_atomtypes())
    window.setRadiusFactor(.3);window.setStructure(source);window.navigator.setHome();window.fitToStructure()
    assert window.structure_drawer.getCellLineWidth()==1
    original=[list(p) for p in window.structure]
    matrix=[[window.navigator.getRotMatElement(i,j) for j in range(4)] for i in range(4)]
    with tempfile.TemporaryDirectory() as folder:
        counts=[]
        for enabled in (False,True):
            window.navigator.setAntialiasing(int(enabled))
            for _ in range(20):cp4vasp.VisCheck();time.sleep(.01)
            path=Path(folder)/('smooth.tga' if enabled else 'hard.tga');window.win.saveScreenshot(str(path))
            raw=path.read_bytes();width=int.from_bytes(raw[12:14],'little');height=int.from_bytes(raw[14:16],'little')
            rgb=np.frombuffer(raw[18:],dtype=np.uint8).reshape(height,width,3)[::-1,:,::-1]
            # Exclude HUD text; copper spheres are colored, leaving neutral cell coverage.
            rgb=rgb[:-35]
            neutral=(rgb[:,:,0]==rgb[:,:,1]) & (rgb[:,:,1]==rgb[:,:,2])
            gray=rgb[:,:,0][neutral];levels=np.unique(gray[(gray>0)&(gray<255)])
            counts.append(len(levels))
            if enabled:Path('/tmp/p4vasp-show-antialias.tga').write_bytes(raw)
        assert counts[1]>counts[0]+8,counts
        assert [list(p) for p in window.structure]==original
        assert [[window.navigator.getRotMatElement(i,j) for j in range(4)] for i in range(4)]==matrix
        assert window.structure_drawer.getBondFactor()==1
        window.hide();window.show()
        assert window.structure_drawer.getCellLineWidth()==1
        print('PASS native thin cell lines: hard/smooth intermediate-gray levels %s; camera/structure/bond state preserved; reopen width 1'%counts,flush=True)

if __name__=='__main__':
    try:main()
    except BaseException:traceback.print_exc();os._exit(1)
    os._exit(0)

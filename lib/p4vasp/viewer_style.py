"""Shared ball-and-stick appearance; never change scientific atom data."""
import math

RADIUS_FACTOR = .5
BOND_FACTOR = 1.2
BOND_COLOR = (.5,.5,.7)
BOND_RADIUS = .1


def covalent_atomtypes():
    from p4vasp.Structure import AtomInfo
    from p4vasp.util import getAtomtypes
    table=AtomInfo(getAtomtypes())
    for index in range(len(table)):
        record=table.getRecord(index)
        record.radius=record.covalent if math.isfinite(record.covalent) and record.covalent>0 else .7
    return table


def display_values(symbols,radii,colors):
    from p4vasp.util import getAtomtypes
    table=getAtomtypes();out_radii=[];out_colors=[]
    for symbol,radius,color in zip(symbols,radii,colors):
        record=table.getRecordForElement(symbol)
        if record is not None:
            radius=record.covalent if math.isfinite(record.covalent) and record.covalent>0 else .7
            color=[record.red,record.green,record.blue]
        out_radii.append(radius);out_colors.append(tuple(color))
    return out_radii,out_colors

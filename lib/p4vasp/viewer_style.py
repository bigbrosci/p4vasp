"""Shared ball-and-stick appearance; never change scientific atom data."""
import math

# Native interactive tessellation: ~70% of the former 32 segments.
# Independent image-export quality presets do not use this setting.
INTERACTIVE_PRIMITIVES_RESOLUTION = 22
CELL_LINE_WIDTH = 1
RADIUS_FACTOR = .5
BOND_FACTOR = 1.2
BOND_COLOR = (.5,.5,.7)
BOND_RADIUS = .1


def ball_radius(symbol, radius):
    """Visual ball size only: retain covalent radii for bond detection."""
    return radius * (1.5 if str(symbol).strip() == 'H' else 1.)


def covalent_atomtypes():
    from p4vasp.Structure import AtomInfo
    from p4vasp.util import getAtomtypes
    table=AtomInfo(getAtomtypes())
    for index in range(len(table)):
        record=table.getRecord(index)
        record.radius=record.covalent if math.isfinite(record.covalent) and record.covalent>0 else .7
        record.radius=ball_radius(record.element,record.radius)
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

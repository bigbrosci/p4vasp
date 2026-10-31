"""Editable-structure screen-relative movement, dispatched from native key events."""
import math
from p4vasp.matrix import Vector
from p4vasp.Structure import Structure

ARROW_STEP = 0.1


def set_arrow_step(value):
    global ARROW_STEP
    value = float(value)
    if not math.isfinite(value) or value <= 0:
        raise ValueError('Arrow-key step must be positive and finite.')
    ARROW_STEP = value


def move_selected(structure, indices, direction, step=None):
    step = ARROW_STEP if step is None else float(step)
    if not math.isfinite(step) or step <= 0 or len(direction) != 3:
        raise ValueError('Invalid arrow movement.')
    length = math.sqrt(sum(float(x)**2 for x in direction))
    if not math.isfinite(length) or length < 1e-12:
        raise ValueError('Invalid movement direction.')
    atoms = sorted(set(int(i) for i in indices))
    if not atoms or any(i < 0 or i >= len(structure) for i in atoms):
        return False
    delta = Vector(*(step*float(x)/length for x in direction))
    physical = Structure()
    physical.basis = [Vector(v) for v in structure.basis]
    physical.scaling = structure.scaling[:]
    physical.coordinates = 'Direct'
    physical.correctScaling()
    a,b,c = physical.basis
    volume = a*b.cross(c)
    if abs(volume) < 1e-15:
        raise ValueError('Cannot move atoms in a singular cell.')
    fractional = Vector(delta*b.cross(c)/volume, delta*c.cross(a)/volume, delta*a.cross(b)/volume)
    if structure.isDirect():
        stored_delta = fractional
    else:
        stored_delta = sum((fractional[i]*structure.basis[i] for i in range(3)), Vector(0,0,0))
    for i in atoms:
        structure[i] = structure[i]+stored_delta
    return True


def handle_event(event, repository):
    from p4vasp import msg
    owner = next((a for a in repository if a.getWindowPtr() == event.getWindow().this), None)
    if owner is None:
        return
    # Edit only initial/Build geometry, never a final/trajectory/STM view.
    from p4vasp.applet.StructureWindowApplet import StructureWindowApplet
    from p4vasp.applet.StructureApplet import StructureApplet
    if isinstance(owner, StructureWindowApplet):
        editable = owner.sequencetype == owner.INITIAL_SEQUENCE
    elif isinstance(owner, StructureApplet):
        editable = owner.structure is getattr(owner.system, 'INITIAL_STRUCTURE', None)
    else:
        return
    if not editable or owner.system is None:
        msg().status('Arrow movement is available for the initial/Build structure only.')
        return
    structure = owner.system.INITIAL_STRUCTURE
    if structure is None:
        return
    indices = [event.getMovedAtom(i) for i in range(event.getMovedAtomCount())]
    if move_selected(structure, indices, (event.dx, event.dy, event.dz)):
        for applet in list(repository):
            if getattr(applet, 'system', None) is owner.system:
                applet.updateSystem()
        msg().status('Moved selected atoms by %g angstrom (current view).' % ARROW_STEP)

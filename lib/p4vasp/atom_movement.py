"""Editable-structure screen-relative movement, dispatched from native key events."""
import math
from p4vasp.matrix import Vector
from p4vasp.Structure import Structure

ARROW_STEP = 0.1
ROTATION_DEGREES = 5.0


def set_arrow_step(value):
    global ARROW_STEP
    value = float(value)
    if not math.isfinite(value) or value <= 0:
        raise ValueError('Arrow-key step must be positive and finite.')
    ARROW_STEP = value


def _physical_basis(structure):
    physical = Structure()
    physical.basis = [Vector(v) for v in structure.basis]
    physical.scaling = structure.scaling[:]
    physical.coordinates = 'Direct'
    physical.correctScaling()
    return physical.basis


def _fractional(basis, vector):
    a,b,c = basis
    volume = a*b.cross(c)
    if not math.isfinite(volume) or abs(volume) < 1e-15:
        raise ValueError('Cannot edit atoms in a singular cell.')
    return Vector(vector*b.cross(c)/volume, vector*c.cross(a)/volume, vector*a.cross(b)/volume)


def _cartesian(basis, fractional):
    return sum((fractional[i]*basis[i] for i in range(3)), Vector(0,0,0))


def _stored_delta(structure, physical_basis, delta):
    fractional = _fractional(physical_basis, delta)
    return fractional if structure.isDirect() else _cartesian(structure.basis, fractional)


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
    stored_delta = _stored_delta(structure, _physical_basis(structure), delta)
    for i in atoms:
        structure[i] = structure[i]+stored_delta
    return True


def rotate_selected(structure, indices, direction, degrees=ROTATION_DEGREES):
    """Rigid rotation about the true mass center; return that center in angstrom."""
    atoms = sorted(set(int(i) for i in indices))
    if not atoms or any(i < 0 or i >= len(structure) for i in atoms):
        return None
    axis = Vector(*direction)
    length = axis.length()
    if not math.isfinite(length) or length < 1e-12 or not math.isfinite(degrees):
        raise ValueError('Invalid rotation axis or angle.')
    axis = (1./length)*axis
    from p4vasp.util import getAtomtypes
    table = None
    masses = []
    for i in atoms:
        record = structure.info.getRecordForAtom(i)
        try:
            mass = float(record.mass)
        except (ValueError, TypeError, AttributeError):
            mass = 0.
        if not math.isfinite(mass) or mass <= 0:
            if table is None:
                table = getAtomtypes()
            element = str(record.element).strip()
            fallback = table.getRecordForElement(element) if table is not None else None
            mass = float(fallback.mass) if fallback is not None else 0.
        if not math.isfinite(mass) or mass <= 0:
            raise ValueError('No positive atomic mass for atom %d (%s).' % (i+1, record.element))
        masses.append(mass)
    basis = _physical_basis(structure)
    points = [_cartesian(basis, structure[i] if structure.isDirect() else
                         _fractional(structure.basis, structure[i])) for i in atoms]
    if not all(math.isfinite(x) for point in points for x in point):
        raise ValueError('Selected atoms have invalid coordinates.')
    total_mass = sum(masses)
    if not math.isfinite(total_mass):
        raise ValueError('Selected atoms have invalid total mass.')
    center = (1./total_mass)*sum((m*p for m,p in zip(masses,points)), Vector(0,0,0))
    if not all(math.isfinite(x) for x in center):
        raise ValueError('Cannot calculate a finite mass center.')
    if len(atoms) == 1:
        return tuple(points[0])
    angle = math.radians(degrees)
    cosine, sine = math.cos(angle), math.sin(angle)
    changes = []
    for i,point in zip(atoms,points):
        radius = point-center
        rotated = cosine*radius+sine*axis.cross(radius)+(1-cosine)*(axis*radius)*axis
        changes.append((i, _stored_delta(structure, basis, center+rotated-point)))
    # Validate and compute everything before touching the source geometry.
    for i,delta in changes:
        structure[i] = structure[i]+delta
    return tuple(center)


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
        msg().status('Arrow editing is available for the initial/Build structure only.')
        return
    structure = owner.system.INITIAL_STRUCTURE
    if structure is None:
        return
    indices = [event.getMovedAtom(i) for i in range(event.getMovedAtomCount())]
    rotating = getattr(event, 'index', 0) == 1
    direction = (event.dx, event.dy, event.dz)
    try:
        center = rotate_selected(structure, indices, direction) if rotating else None
        changed = center is not None if rotating else move_selected(structure, indices, direction)
    except ValueError as error:
        msg().status(str(error))
        return
    if changed:
        for applet in list(repository):
            if getattr(applet, 'system', None) is owner.system:
                applet.updateSystem()
        if rotating:
            msg().status('Rotated 5 degrees about mass center (%.4f, %.4f, %.4f) angstrom.' % center)
        else:
            msg().status('Moved selected atoms by %g angstrom (current view).' % ARROW_STEP)

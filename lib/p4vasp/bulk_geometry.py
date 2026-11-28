"""Shared ASE construction for Bulk workers and standalone replay."""
from io import StringIO
import math

# Fields are explicit: no inferred lattice constants or crystal structures.
CRYSTALS = {
    'sc': ('a',), 'fcc': ('a',), 'bcc': ('a',), 'diamond': ('a',),
    'hcp': ('a', 'c'), 'bct': ('a', 'c'),
    'rocksalt': ('a',), 'zincblende': ('a',), 'cesiumchloride': ('a',),
    'fluorite': ('a',), 'wurtzite': ('a', 'c', 'u'),
    'orthorhombic': ('a', 'b', 'c'),
    'rhombohedral': ('a', 'alpha'),
}
MAX_ATOMS = 10000


def parameters(request):
    name = str(request.get('name', '')).strip()
    crystal = request.get('crystal')
    mode = request.get('mode', 'primitive')
    if not name or len(name) > 40:
        raise ValueError('Enter an element or formula, e.g. Cu or NaCl.')
    if crystal not in CRYSTALS or mode not in ('primitive', 'orthorhombic', 'cubic'):
        raise ValueError('Choose a supported crystal and cell type.')
    values = {}
    for key in CRYSTALS[crystal]:
        try: value = float(request.get(key, ''))
        except (ValueError, TypeError): raise ValueError('Enter a numeric '+key+'.')
        if not math.isfinite(value) or value <= 0:
            raise ValueError(key+' must be positive and finite.')
        if key == 'alpha' and value >= 120:
            raise ValueError('Rhombohedral alpha must be between 0 and 120 degrees.')
        if key == 'u' and value >= 1:
            raise ValueError('Wurtzite u must be between 0 and 1.')
        values[key] = value
    repeat = request.get('repeat', (1, 1, 1))
    if not isinstance(repeat, (list, tuple)) or len(repeat) != 3:
        raise ValueError('Enter three positive integer supercell repetitions.')
    counts = []
    for value in repeat:
        if isinstance(value, bool) or str(value).strip() not in tuple(str(i) for i in range(1, 101)):
            raise ValueError('Each repetition must be an integer from 1 to 100.')
        counts.append(int(value))
    if math.prod(counts) > MAX_ATOMS:
        raise ValueError('Supercell exceeds the 10000 atom limit.')
    return name, crystal, mode, values, tuple(counts)


def build_bulk(request):
    name, crystal, mode, values, repeat = parameters(request)
    try:
        import ase
        from ase.build import bulk
        from ase.io import write
        from ase.formula import Formula
        from ase.data import atomic_numbers
    except ImportError as error:
        raise RuntimeError('ASE is unavailable. Run bash install/install-science.sh in the p4vasp checkout.') from error
    composition = Formula(name).count()
    if not composition or any(symbol not in atomic_numbers or symbol == 'X' for symbol in composition):
        raise ValueError('Use valid element symbols in the chemical formula.')
    if sum(composition.values()) > 3:
        raise ValueError('Enter one prototype formula unit (e.g. Cu, NaCl or CaF2), not a supercell formula.')
    try:
        atoms = bulk(name, crystalstructure=crystal, orthorhombic=mode == 'orthorhombic',
                     cubic=mode == 'cubic', **values)
    except KeyError as error:
        raise ValueError('ASE has no basis for this formula and crystal. Choose another supported prototype.') from error
    if len(atoms)*math.prod(repeat) > MAX_ATOMS:
        raise ValueError('Supercell exceeds the 10000 atom limit.')
    atoms = atoms.repeat(repeat)
    if atoms.cell.rank != 3 or not math.isfinite(atoms.get_volume()) or atoms.get_volume() <= 1e-10:
        raise ValueError('The requested cell is degenerate.')
    stream = StringIO()
    write(stream, atoms, format='vasp', direct=True, sort=True, vasp5=True)
    return {'poscar': stream.getvalue(), 'atoms': len(atoms), 'formula': atoms.get_chemical_formula(),
            'cell': atoms.cell.array.tolist(), 'volume': atoms.get_volume(), 'ase_version': ase.__version__,
            'request': request}


def write_bulk_poscar(path, poscar):
    """Create the requested POSCAR exclusively and clean up on write failure."""
    stream = path.open('x', encoding='utf-8', newline='\n')
    try:
        with stream:
            stream.write(poscar)
    except BaseException:
        path.unlink(missing_ok=True)
        raise

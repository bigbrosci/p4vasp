"""Generate three isolated-atom inputs using the bundled INCAR generator."""
import copy
from pathlib import Path
from p4vasp.element_data import SYMBOLS
from p4vasp.incar_generator import generate_incar, load_presets


def input_contents(symbol, config=None):
    if symbol not in SYMBOLS:
        raise ValueError('Choose an element from the periodic table.')
    config = copy.deepcopy(config if config is not None else load_presets())
    # Initial moment is intentionally left to VASP, independent of element defaults.
    for params in config['standard'].values():
        for tag in list(params):
            if tag.upper() == 'MAGMOM': del params[tag]
    incar = generate_incar(config, [], list(config['standard']),
                           'ISPIN=2\nALGO=ALL\nNELM=500', system_name=symbol+' single atom')
    return {
        'INCAR': incar,
        'KPOINTS': 'Single atom Gamma mesh\n0\nGamma\n1 1 1\n0 0 0\n',
        'POSCAR': symbol+' single atom\n1.0\n13 0 0\n0 14 0\n0 0 15\n'+symbol+'\n1\nDirect\n0.5 0.5 0.5\n',
    }


def destination(parent, name):
    name = name.strip()
    if not name or name in ('.', '..') or '/' in name or '\\' in name or ':' in name or any(ord(char)<32 or char in '<>\"|?*' for char in name):
        raise ValueError('Enter a folder name without path separators.')
    if name.endswith(('.', ' ')) or name.split('.')[0].upper() in {'CON','PRN','AUX','NUL',*('COM%d'%i for i in range(1,10)),*('LPT%d'%i for i in range(1,10))}:
        raise ValueError('Choose a portable folder name (no reserved Windows names or trailing dot).')
    if not str(parent).strip(): raise ValueError('Choose a parent folder.')
    parent = Path(parent).expanduser().absolute()
    if not parent.is_dir():
        raise ValueError('Choose an existing parent folder.')
    return parent/name


def write_inputs(symbol, parent, name, config=None):
    contents = input_contents(symbol, config)
    target = destination(parent, name)
    target.mkdir()  # Require a new directory; never overwrite an existing calculation.
    written = []
    try:
        for filename, text in contents.items():
            path = target/filename
            with path.open('x', encoding='utf-8', newline='\n') as stream:
                written.append(path)
                stream.write(text)
    except Exception:
        for path in written: path.unlink(missing_ok=True)
        try: target.rmdir()
        except OSError: pass
        raise
    return target

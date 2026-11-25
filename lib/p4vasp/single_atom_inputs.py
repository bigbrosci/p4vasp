"""Generate three isolated-atom inputs using the bundled INCAR generator."""
import copy
import math
import re
from pathlib import Path
from p4vasp.element_data import SYMBOLS
from p4vasp.incar_generator import generate_incar, load_presets


def settings_values(symbol, settings=None):
    from p4vasp.element_data import NUMBERS
    if symbol not in SYMBOLS:raise ValueError('Choose an element from the periodic table.')
    settings=settings or {}
    def integer(value,name):
        if isinstance(value,bool) or not re.fullmatch(r'[+-]?\d+',str(value).strip()):raise ValueError(name+' must be an integer.')
        return int(value)
    def optional(value):return value is None or str(value).strip()==''
    spin=integer(settings.get('ispin',2),'ISPIN')
    if spin not in (1,2):raise ValueError('ISPIN must be 1 or 2.')
    charge=integer(settings.get('charge',0),'Charge')
    if NUMBERS[symbol]-charge<1:raise ValueError('The charged atom must retain at least one electron.')
    cell=[float(value) for value in settings.get('cell',(13,14,15))]
    if len(cell)!=3 or any(not math.isfinite(value) or not 0<value<=1000 for value in cell):raise ValueError('Use three positive cell lengths up to 1000 Å.')
    mag=settings.get('magmom');mag=None if optional(mag) else float(mag)
    if mag is not None and not math.isfinite(mag):raise ValueError('MAGMOM must be finite.')
    target=settings.get('nupdown');target=None if optional(target) else integer(target,'NUPDOWN')
    if target is not None and not 0<=target<=NUMBERS[symbol]-charge:raise ValueError('NUPDOWN is outside the physical electron-count range.')
    if spin==1 and (mag is not None or target is not None):raise ValueError('MAGMOM and NUPDOWN require ISPIN=2.')
    if target is not None:
        if mag is None:mag=float(target)
        elif abs(mag-target)>1e-8:raise ValueError('For one constrained atom, MAGMOM must match NUPDOWN, or be blank.')
    zval=settings.get('zval');zval=None if optional(zval) else float(zval)
    if zval is not None and (not math.isfinite(zval) or not zval.is_integer() or not 0<zval<=NUMBERS[symbol]):raise ValueError('Use the integer ZVAL from your selected POTCAR.')
    nelect=None if zval is None else int(zval)-charge
    if nelect is not None and nelect<=0:raise ValueError('NELECT must be positive for the selected POTCAR and charge.')
    if nelect is not None and target is not None and (target>nelect or (nelect-target)%2):raise ValueError('NELECT minus NUPDOWN must be nonnegative and even.')
    return dict(ispin=spin,charge=charge,cell=cell,magmom=mag,nupdown=target,zval=zval,nelect=nelect)


def input_contents(symbol, config=None, settings=None):
    values=settings_values(symbol,settings)
    config=copy.deepcopy(config if config is not None else load_presets())
    for params in config['standard'].values():
        for tag in list(params):
            if tag.upper() in ('MAGMOM','NELECT','NUPDOWN','LSORBIT','LNONCOLLINEAR'):del params[tag]
    custom='ISPIN=%d\nALGO=ALL\nNELM=500'%values['ispin']
    for tag,key in (('MAGMOM','magmom'),('NUPDOWN','nupdown')):
        if values[key] is not None:custom+='\n%s=%.12g'%(tag,values[key])
    if values['charge'] and values['nelect'] is not None:custom+='\nNELECT=%d'%values['nelect']
    incar=generate_incar(config,[],list(config['standard']),custom,system_name=symbol+' single atom')
    incar='# Single atom %s; charge=%+d\n'%(symbol,values['charge'])+incar
    if values['charge'] and values['nelect'] is None:
        incar+=('\n# Charged template: complete NELECT before running VASP.\n'
                '# NELECT = POTCAR ZVAL - (%+d)\nNELECT = SET_AFTER_POTCAR\n')%values['charge']
    cell=''.join(' '.join('%.12g'%(values['cell'][i] if i==j else 0) for j in range(3))+'\n' for i in range(3))
    return {'INCAR':incar,'KPOINTS':'Single atom Gamma mesh\n0\nGamma\n1 1 1\n0 0 0\n',
            'POSCAR':symbol+' single atom\n1.0\n'+cell+symbol+'\n1\nDirect\n0.5 0.5 0.5\n'}


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


def write_inputs(symbol, parent, name, config=None, settings=None):
    contents = input_contents(symbol, config, settings)
    return write_contents(contents, parent, name)


def write_contents(contents, parent, name):
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

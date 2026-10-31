"""Strict single-frame XYZ library and geometry-preserving gas inputs."""
from collections import Counter
import copy
from dataclasses import dataclass
import math
from pathlib import Path
import re
import shlex
import p4vasp
from p4vasp.element_data import SYMBOLS
from p4vasp.incar_generator import generate_incar, load_presets
from p4vasp.single_atom_inputs import write_contents


@dataclass(frozen=True)
class Molecule:
    path: Path
    name: str
    symbols: tuple
    positions: tuple
    charge: object = None
    multiplicity: object = None


def library_path():
    return Path(p4vasp.p4vasp_home)/'data/models/gas_phase'


def integer(value, title, minimum=None):
    if not re.fullmatch(r'[+-]?\d+', str(value).strip()):
        raise ValueError(title+' must be an integer.')
    result=int(value)
    if minimum is not None and result<minimum: raise ValueError(title+' must be at least '+str(minimum)+'.')
    return result


def read_xyz(path):
    path=Path(path)
    def fail(line, text): raise ValueError('%s:%d: %s'%(path.name,line,text))
    try: lines=path.read_text(encoding='utf-8-sig').splitlines()
    except (OSError,UnicodeError) as error: raise ValueError(path.name+': '+str(error)) from error
    if not lines: fail(1,'Missing atom count.')
    try: count=integer(lines[0],'Atom count',1)
    except ValueError as error: fail(1,str(error))
    if len(lines)<2: fail(2,'Missing comment line.')
    metadata={}
    if '=' in lines[1]:
        try:
            for token in shlex.split(lines[1]):
                key,sep,value=token.partition('=')
                if not sep or key not in ('name','charge','multiplicity','units') or key in metadata:
                    raise ValueError('Use unique name, charge, multiplicity, units key=value fields.')
                metadata[key]=value
        except ValueError as error: fail(2,str(error))
    if metadata.get('units','angstrom').lower()!='angstrom': fail(2,'Coordinates must use units=angstrom.')
    charge=multiplicity=None
    try:
        if 'charge' in metadata: charge=integer(metadata['charge'],'Charge')
        if 'multiplicity' in metadata: multiplicity=integer(metadata['multiplicity'],'Multiplicity',1)
    except ValueError as error: fail(2,str(error))
    if len(lines)<count+2: fail(len(lines)+1,'Expected %d atom lines.'%count)
    symbols=[];positions=[]
    for index,line in enumerate(lines[2:count+2],3):
        fields=line.split()
        if len(fields)!=4: fail(index,'Use: Element X Y Z (angstrom).')
        if fields[0] not in SYMBOLS: fail(index,'Unknown element symbol: '+fields[0])
        try: point=tuple(float(value) for value in fields[1:])
        except ValueError: fail(index,'Coordinates must be numbers.')
        if not all(math.isfinite(value) for value in point): fail(index,'Coordinates must be finite.')
        symbols.append(fields[0]);positions.append(point)
    for index,line in enumerate(lines[count+2:],count+3):
        if line.strip(): fail(index,'Only one XYZ frame per file is supported.')
    name=metadata.get('name') or (lines[1].strip() if not metadata else '') or path.stem
    return Molecule(path,name,tuple(symbols),tuple(positions),charge,multiplicity)


def scan_library(folder=None):
    folder=Path(folder) if folder is not None else library_path()
    results=[]
    for path in sorted(folder.iterdir(),key=lambda item:item.name.casefold()):
        if path.is_file() and path.suffix.lower()=='.xyz':
            try: results.append((path,read_xyz(path),''))
            except ValueError as error: results.append((path,None,str(error)))
    return results


def suggested_cell(molecule, vacuum=6):
    span=[max(p[i] for p in molecule.positions)-min(p[i] for p in molecule.positions) for i in range(3)]
    return tuple(max(base,math.ceil(size+2*vacuum)) for base,size in zip((13,14,15),span))


def poscar(molecule, cell):
    if len(cell)!=3 or not all(math.isfinite(value) and value>0 for value in cell):
        raise ValueError('Enter three positive finite cell lengths in angstrom.')
    lo=[min(p[i] for p in molecule.positions) for i in range(3)]
    hi=[max(p[i] for p in molecule.positions) for i in range(3)]
    if any(length<=hi[i]-lo[i] for i,length in enumerate(cell)):
        raise ValueError('Cell must be larger than the molecular span in every direction.')
    shift=[cell[i]/2-lo[i]/2-hi[i]/2 for i in range(3)]
    order=list(dict.fromkeys(molecule.symbols));counts=Counter(molecule.symbols)
    title=re.sub(r'[\r\n]', ' ',molecule.name)
    lines=[title,'1.0','%.12g 0 0'%cell[0],'0 %.12g 0'%cell[1],'0 0 %.12g'%cell[2],
           ' '.join(order),' '.join(str(counts[symbol]) for symbol in order),'Cartesian']
    for symbol in order:
        for element,point in zip(molecule.symbols,molecule.positions):
            if element==symbol: lines.append(' '.join('%.15g'%(point[i]+shift[i]) for i in range(3)))
    return '\n'.join(lines)+'\n'


def input_contents(molecule, charge, multiplicity, cell, config=None):
    charge=integer(charge,'Charge');multiplicity=integer(multiplicity,'Multiplicity',1)
    difference=multiplicity-1
    config=copy.deepcopy(config if config is not None else load_presets())
    for params in config['standard'].values():
        for tag in list(params):
            if tag.upper() in ('MAGMOM','NELECT','NUPDOWN','LSORBIT','LNONCOLLINEAR'):
                del params[tag]
    custom='ISPIN=2\nNUPDOWN=%d\nISMEAR=0\nSIGMA=0.01'%difference
    incar=generate_incar(config,[],list(config['standard']),custom,system_name=molecule.name+' gas phase')
    if charge != 0:
        incar += ('\n# Charged-system template: complete NELECT before running VASP.\n'
                  '# NELECT = sum(atom_count * POTCAR ZVAL) - (%+d)\n'
                  '# Negative charge adds electrons; positive charge removes electrons.\n'
                  '# Check NELECT - NUPDOWN is nonnegative and even.\n'
                  'NELECT = SET_AFTER_POTCAR\n') % charge
    source=molecule.path.name.replace('\n',' ').replace('\r',' ')
    incar='# XYZ: %s; charge=%d; multiplicity=%d\n'%(source,charge,multiplicity)+incar
    return {'INCAR':incar,'KPOINTS':'Gas phase Gamma mesh\n0\nGamma\n1 1 1\n0 0 0\n',
            'POSCAR':poscar(molecule,cell)}


def write_inputs(molecule, charge, multiplicity, cell, parent, name):
    # Do not silently export an obsolete preview after the source was edited.
    if read_xyz(molecule.path)!=molecule:
        raise ValueError('XYZ file changed. Refresh the library and review the molecule again.')
    return write_contents(input_contents(molecule,charge,multiplicity,cell),parent,name)

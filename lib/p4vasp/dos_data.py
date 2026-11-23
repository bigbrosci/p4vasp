"""Strict collinear DOSCAR projected-data reader, independent of scientific/GUI libs."""
import math
from pathlib import Path
import re

LM = ['s', 'py', 'pz', 'px', 'dxy', 'dyz', 'dz2', 'dxz', 'dx2',
      'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7']


def read_doscar(path):
    path = Path(path)
    incar = path.parent/'INCAR'
    settings = incar.read_text(errors='replace') if incar.exists() else ''
    settings = re.sub(r'[!#][^\n]*', '', settings)
    for tag in ('LSORBIT', 'LNONCOLLINEAR'):
        if re.search(r'\b'+tag+r'\s*=\s*\.?T', settings, re.I):
            raise ValueError('Projected DOS analysis supports collinear calculations only (no SOC/noncollinear).')
    def numbers(line):
        try: values = [float(x.replace('D','E')) for x in line.split()]
        except ValueError as error: raise ValueError('DOSCAR contains invalid numeric data.') from error
        if not values or not all(math.isfinite(x) for x in values):
            raise ValueError('DOSCAR contains empty/nonfinite data.')
        return values
    with path.open() as stream:
        first = numbers(stream.readline())
        atoms = int(first[0])
        if atoms <= 0 or atoms != first[0]: raise ValueError('Invalid DOSCAR atom count.')
        for _ in range(4):
            if not stream.readline(): raise ValueError('DOSCAR header is incomplete.')
        header = numbers(stream.readline())
        if len(header) < 4: raise ValueError('DOSCAR energy header is incomplete.')
        count = int(header[2]); fermi = header[3]
        if count < 2 or count != header[2]: raise ValueError('DOSCAR needs at least two energy samples.')
        total = [numbers(stream.readline()) for _ in range(count)]
        columns = len(total[0])
        if columns not in (3,5) or any(len(row) != columns for row in total):
            raise ValueError('Unsupported/inconsistent total DOS columns.')
        spins = 2 if columns == 5 else 1
        energies = [row[0] for row in total]
        if any(b <= a for a,b in zip(energies,energies[1:])):
            raise ValueError('DOSCAR energy grid must be strictly increasing.')
        projected = []; orbitals = None
        for atom in range(atoms):
            line = stream.readline()
            while line and not line.strip(): line = stream.readline()
            if not line:
                if atom == 0: break
                raise ValueError('DOSCAR projected atom blocks are incomplete.')
            block = numbers(line)
            if len(block) < 4 or block[2] != count or abs(block[3]-fermi) > 1e-5:
                raise ValueError('DOSCAR projected header/grid differs from total DOS.')
            rows = [numbers(stream.readline()) for _ in range(count)]
            width = len(rows[0])
            if (width-1) % spins: raise ValueError('Unsupported projected DOS columns.')
            n_orbitals = (width-1)//spins
            if n_orbitals not in (3,4,9,16):
                raise ValueError('Unsupported projected DOS layout; SOC/noncollinear data are not supported.')
            if spins == 1 and n_orbitals == 16 and not incar.exists():
                raise ValueError('17-column projected data are ambiguous. Supply INCAR to verify collinear LORBIT settings.')
            fields = ['s','p','d','f'][:n_orbitals] if n_orbitals <= 4 else LM[:n_orbitals]
            if orbitals is not None and fields != orbitals:
                raise ValueError('DOSCAR orbital columns differ between atoms.')
            orbitals = fields
            channels = [[] for _ in range(spins)]
            for i,row in enumerate(rows):
                if len(row) != width or abs(row[0]-energies[i]) > 1e-5:
                    raise ValueError('DOSCAR projected energy grid/columns differ from total DOS.')
                if any(value < -1e-8 for value in row[1:]):
                    raise ValueError('Negative projected DOS: expected raw positive collinear spin densities.')
                for spin in range(spins):
                    channels[spin].append([max(0., value) for value in row[1+spin::spins]])
            projected.append(channels)
        if stream.read().strip(): raise ValueError('Unexpected extra DOSCAR atom blocks/data.')
    return dict(energies=energies, efermi=fermi, natoms=atoms, spins=spins,
                orbitals=orbitals or [], projected=projected,
                total=[[row[1+spin] for row in total] for spin in range(spins)])

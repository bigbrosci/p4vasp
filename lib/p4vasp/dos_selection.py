"""Shared, GUI-free validation for DOS selections and positional CLI arguments."""
import re

P_ORBITALS=('py','pz','px')
D_ORBITALS=('dxy','dyz','dz2','dxz','dx2')
F_ORBITALS=('f_3','f_2','f_1','f0','f1','f2','f3')
SHELLS={'s':(), 'p':P_ORBITALS, 'd':D_ORBITALS, 'f':F_ORBITALS}
ORBITAL_ORDER=tuple(name for shell,components in SHELLS.items() for name in (shell,*components))


def orbital_shell(name):
    return next(shell for shell,components in SHELLS.items() if name==shell or name in components)


def band_label(names):
    shells={orbital_shell(name) for name in names}
    return next(iter(shells)) if len(shells)==1 else 'selected'


def parse_orbitals(value):
    values=re.split(r'[\s,]+',value.strip()) if isinstance(value,str) else list(value)
    values=[name.replace('dx2_y2','dx2') for name in values if name]
    if not values:raise ValueError('Select at least one s, p, d or f orbital.')
    unknown=set(values)-set(ORBITAL_ORDER)
    if unknown:raise ValueError('Unsupported orbital: '+', '.join(sorted(unknown)))
    for shell,components in SHELLS.items():
        if shell in values and set(values).intersection(components):
            raise ValueError(shell+' cannot be combined with individual '+shell+' orbitals.')
    return [name for name in ORBITAL_ORDER if name in values]


def parse_atoms(text):
    if text.strip().lower()=='all':return []
    atoms=set()
    for part in re.split(r'[\s,]+',text.strip()):
        match=re.fullmatch(r'(\d+)(?:-(\d+))?',part)
        if not match:raise ValueError('Use 1-based atoms, e.g. 1-3,8, or all.')
        first=int(match[1]);last=int(match[2] or first)
        if first<1 or last<first or last-first>100000:raise ValueError('Invalid atom range.')
        atoms.update(range(first,last+1))
    return sorted(atoms)

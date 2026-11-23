"""Shared, GUI-free validation for DOS selections and positional CLI arguments."""
import re

D_ORBITALS=('dxy','dyz','dz2','dxz','dx2')


def parse_orbitals(value):
    values=re.split(r'[\s,]+',value.strip()) if isinstance(value,str) else list(value)
    values=[name.replace('dx2_y2','dx2') for name in values if name]
    if not values:raise ValueError('Select d or at least one individual d orbital.')
    unknown=set(values)-{'d',*D_ORBITALS}
    if unknown:raise ValueError('Unsupported d orbital: '+', '.join(sorted(unknown)))
    if 'd' in values:
        if set(values)!={'d'}:raise ValueError('d cannot be combined with individual d orbitals.')
        return ['d']
    return [name for name in D_ORBITALS if name in values]


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

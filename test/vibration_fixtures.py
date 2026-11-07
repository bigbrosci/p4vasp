"""Synthetic OUTCAR tables for parser/UI tests; not calculated physical modes."""
from pathlib import Path


def write_calculation(folder, physical=True, imaginary=(1,), flags=True):
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    lines=['VRHFIN =C: s2p2','POMASS = 12.000;','VRHFIN =O: s2p4','POMASS = 16.000;',
           'ions per type = 1 1','direct lattice vectors reciprocal lattice vectors',
           '10 0 0 0 0 0','0 11 0 0 0 0','0 0 12 0 0 0']
    headers=['Eigenvectors and eigenvalues of the dynamical matrix']
    if physical:headers.append('Eigenvectors after division by SQRT(mass)')
    for header in headers:
        lines.append(header)
        for i in range(1,7):
            cm=100*i
            lines.extend(['%d %s %.6f THz 1.0 2PiTHz %.6f cm-1 %.6f meV'%
                          (i,'f/i=' if i in imaginary else 'f =',cm/33.35640952,cm,cm*.123984198),
                          'X Y Z dx dy dz',
                          '4 5 6 %.6f 0 0'%(.4*i),'5.2 5 6 %.6f 0 0'%(-.2*i)])
    (folder/'OUTCAR').write_text('\n'.join(lines)+'\n')
    if flags:
        (folder/'POSCAR').write_text('CO\n1\n10 0 0\n0 11 0\n0 0 12\nC O\n1 1\nSelective dynamics\nCartesian\n4 5 6 T T T\n5.2 5 6 T F T\n')
    return folder/'OUTCAR'

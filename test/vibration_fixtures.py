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


def write_energy_calculation(folder):
    """Minimal ASE-readable ionic frames followed by synthetic normal modes."""
    path=write_calculation(folder)
    modes=path.read_text()
    header=''.join(' POTCAR: PAW_PBE %s 01Jan2000\n'%symbol for symbol in ('C','O','C','O'))
    header+=' ions per type = 1 1\n ISPIN = 1\n Iteration 1(1)\n'
    frames=[]
    for x,free,zero in ((4,-10.5,-10.25),(4.02,-11.5,-11.25),(3.98,-12.5,-12.25)):
        frames.append(' direct lattice vectors reciprocal lattice vectors\n10 0 0 0 0 0\n0 11 0 0 0 0\n0 0 12 0 0 0\n'
                      ' POSITION          TOTAL-FORCE (eV/Angst)\n ----------------\n'
                      '%g 5 6 0 0 0\n5.2 5 6 0 0 0\n ----------------\n'%x+
                      ' FREE ENERGIE OF THE ION-ELECTRON SYSTEM (eV)\n ----------------\n'
                      ' free energy TOTEN = %g eV\n\n energy without entropy= %g energy(sigma->0) = %g\n'%(free,zero,zero))
    path.write_text(header+''.join(frames)+modes)
    return path

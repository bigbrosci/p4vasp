"""Analytic synthetic projected DOS; never user scientific data."""
import math
from pathlib import Path


def projected_calculation(folder, spin=True, aggregate=False, xml=False):
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    n=401; ef=2.
    energies=[-10.+i*.05 for i in range(n)]
    fields=['s','p','d'] if aggregate else ['s','py','pz','px','dxy','dyz','dz2','dxz','dx2']
    channels=[]
    for atom in range(2):
        atom_channels=[]
        for channel in range(2 if spin else 1):
            center=(-1. if atom==0 else 1.)+(1. if channel else 0.)
            rows=[]
            for energy in energies:
                d=math.exp(-.5*((energy-center)/.6)**2)
                rows.append([.1,.2,d*15] if aggregate else [.1,.2,.3,.4]+[d*(i+1) for i in range(5)])
            atom_channels.append(rows)
        channels.append(atom_channels)
    header='12 -8 %d %g 1\n'%(n,ef)
    total=[]
    for i,energy in enumerate(energies):
        densities=[sum(sum(atom[s][i]) for atom in channels) for s in range(len(channels[0]))]
        total.append([energy+ef]+densities+([0.,0.] if spin else [0.]))
    text='2 2 1 0\n1 1 1 1 1\n300\nSynthetic FeNi\nProjected test\n'+header
    text+=''.join(' '.join(map(str,row))+'\n' for row in total)
    for atom in channels:
        text+=header
        for i,energy in enumerate(energies):
            values=[energy+ef]+[atom[s][i][o] for o in range(len(fields)) for s in range(len(atom))]
            text+=' '.join(map(str,values))+'\n'
    (folder/'DOSCAR').write_text(text)
    (folder/'INCAR').write_text('ISPIN = %d\nLORBIT=11\nLSORBIT = .FALSE.\nLNONCOLLINEAR=.FALSE.\n'%(2 if spin else 1))
    (folder/'POSCAR').write_text('FeNi test\n1\n4 0 0\n0 4 0\n0 0 4\nFe Ni\n1 1\nDirect\n0 0 0\n.5 .5 .5\n')
    if xml:
        structure='<crystal><varray name="basis"><v>4 0 0</v><v>0 4 0</v><v>0 0 4</v></varray></crystal><varray name="positions"><v>0 0 0</v><v>.5 .5 .5</v></varray>'
        atominfo='''<atominfo><atoms>2</atoms><types>2</types><array name="atoms"><set><rc><c>Fe</c><c>1</c></rc><rc><c>Ni</c><c>2</c></rc></set></array><array name="atomtypes"><dimension dim="1">type</dimension><field type="int">atomspertype</field><field type="string">element</field><field>mass</field><field>valence</field><field type="string">pseudopotential</field><set><rc><c>1</c><c>Fe</c><c>55.8</c><c>8</c><c>PAW_PBE Fe</c></rc><rc><c>1</c><c>Ni</c><c>58.7</c><c>10</c><c>PAW_PBE Ni</c></rc></set></array></atominfo>'''
        tdos=''
        for s in range(len(channels[0])):
            tdos+='<set comment="spin %d">'%(s+1)+''.join('<r>%g %.15g 0</r>'%(row[0],row[1+s]) for row in total)+'</set>'
        pdos=''
        for a,atom in enumerate(channels):
            pdos+='<set comment="ion %d">'%(a+1)
            for s,channel in enumerate(atom):
                pdos+='<set comment="spin %d">'%(s+1)+''.join('<r>'+str(energy+ef)+' '+' '.join(map(str,row))+'</r>' for energy,row in zip(energies,channel))+'</set>'
            pdos+='</set>'
        dos='<dos><i name="efermi">2</i><total><array><dimension dim="1">gridpoints</dimension><dimension dim="2">spin</dimension><field>energy</field><field>total</field><field>integrated</field><set>'+tdos+'</set></array></total><partial><array><dimension dim="1">gridpoints</dimension><dimension dim="2">spin</dimension><dimension dim="3">ion</dimension>'+''.join('<field>'+f+'</field>' for f in ['energy']+fields)+'<set>'+pdos+'</set></array></partial></dos>'
        parameters='<parameters><i name="ISPIN" type="int">%d</i><i name="NELM" type="int">60</i><i name="NSW" type="int">0</i><i name="IBRION" type="int">-1</i></parameters>'%(2 if spin else 1)
        (folder/'vasprun.xml').write_text('<modeling><generator><i name="version" type="string">6.4</i></generator><incar><i name="SYSTEM" type="string">Synthetic projected DOS</i></incar>'+parameters+atominfo+'<structure name="initialpos">'+structure+'</structure><calculation>'+dos+'</calculation><structure name="finalpos">'+structure+'</structure></modeling>')
    return folder

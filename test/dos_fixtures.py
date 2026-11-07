"""Small synthetic DOS/band files; no user calculation data."""
from pathlib import Path


def write_calculation(folder, scale=1, spin=False, with_xml=True):
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    folder.joinpath('POSCAR').write_text('Synthetic H\n1\n4 0 0\n0 4 0\n0 0 4\nH\n1\nDirect\n0 0 0\n')
    folder.joinpath('INCAR').write_text('SYSTEM = Synthetic DOS '+str(scale)+'\n')
    rows=['-1 0 0','0 %g 1'%(4*scale),'1 %g 2'%scale]
    folder.joinpath('DOSCAR').write_text('1 1 1 0\n1 1 1 1 1\n300\nSynthetic\nDOS test\n1 -1 3 0.5 1\n'+'\n'.join(rows)+'\n')
    if not with_xml:return folder
    atominfo='''<atominfo><atoms>1</atoms><types>1</types><array name="atomtypes">
    <dimension dim="1">type</dimension><field type="int">atomspertype</field>
    <field type="string">element</field><field>mass</field><field>valence</field>
    <field type="string">pseudopotential</field><set><rc><c>1</c><c>H</c><c>1.0</c><c>1</c><c>PAW H</c></rc></set></array></atominfo>'''
    struct='''<structure name="initialpos"><crystal><varray name="basis"><v>4 0 0</v><v>0 4 0</v><v>0 0 4</v></varray></crystal><varray name="positions"><v>0 0 0</v></varray></structure>'''
    total=''.join('<r>'+row+'</r>' for row in rows)
    dos='<dos><i name="efermi">0.5</i><total><array><dimension dim="1">gridpoints</dimension><dimension dim="2">spin</dimension><field>energy</field><field>total</field><field>integrated</field><set><set comment="spin 1">'+total+'</set></set></array></total></dos>'
    kpoints='''<kpoints><generation param="listgenerated"><i name="divisions" type="int">2</i></generation><varray name="kpointlist"><v>0 0 0</v><v>0.5 0 0</v></varray></kpoints>'''
    bands='''<eigenvalues><array><dimension dim="1">band</dimension><dimension dim="2">kpoint</dimension><dimension dim="3">spin</dimension><field>energy</field><field>occ</field><set><set comment="spin 1"><set comment="kpoint 1"><r>-1 1</r><r>1 0</r></set><set comment="kpoint 2"><r>-0.5 1</r><r>1.5 0</r></set></set></set></array></eigenvalues>'''
    folder.joinpath('vasprun.xml').write_text('<modeling><incar><i name="SYSTEM" type="string">Synthetic XML '+str(scale)+'</i></incar>'+atominfo+struct+kpoints+dos+bands+'</modeling>')
    return folder

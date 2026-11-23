"""Optional pymatgen d-DOS analysis in a short-lived scientific worker."""
import csv
import json
from pathlib import Path
import sys

# Source execution must work without importing native p4vasp extensions.
if __package__ in (None, ''):
    source = Path(__file__).resolve()
    sys.path = [item for item in sys.path if Path(item).resolve() != source.parent]
    sys.path.insert(0, str(source.parents[1]))


def worker_command():
    from p4vasp.model_worker import scientific_python
    python = scientific_python('pymatgen')
    if python is None:
        raise RuntimeError('pymatgen is unavailable. Run bash install/install-science.sh.')
    script=Path(__file__).resolve()
    if not script.is_file():raise RuntimeError('This build lacks the pymatgen analysis worker source; use an updated source checkout.')
    return [python, str(script)]


def load_complete(path, structure_path=None):
    import numpy as np
    from pymatgen.electronic_structure.core import Spin, Orbital, OrbitalType
    from pymatgen.electronic_structure.dos import Dos, CompleteDos
    path = Path(path).resolve()
    if path.name.upper() != 'DOSCAR':
        from pymatgen.io.vasp.outputs import Vasprun
        run = Vasprun(path, parse_eigen=False, parse_projected_eigen=False, parse_potcar_file=False)
        if any(settings.get(tag) for settings in (run.parameters,run.incar) for tag in ('LNONCOLLINEAR','LSORBIT')):
            raise ValueError('SOC/noncollinear projected analysis is not supported.')
        if run.dos_has_errors or not run.pdos:
            raise ValueError('No valid orbital-projected DOS in vasprun.xml.')
        aggregated = any(isinstance(orbital, OrbitalType) for atom in run.pdos for orbital in atom)
        return run.complete_dos, aggregated, str(path)
    from p4vasp.dos_data import read_doscar, LM
    data = read_doscar(path)
    if not data['projected']:
        raise ValueError('DOSCAR has total DOS only. Orbital-projected d-DOS is required.')
    if structure_path:
        source = Path(structure_path).resolve()
    else:
        source = next((path.parent/name for name in ('POSCAR','CONTCAR') if (path.parent/name).is_file()), None)
    if source is None:
        raise ValueError('DOSCAR needs a matching POSCAR/CONTCAR to identify atoms and elements.')
    from pymatgen.io.vasp.inputs import Poscar
    poscar = Poscar.from_file(source, check_for_potcar=False)
    if not poscar.true_names:
        raise ValueError('A matching VASP5 POSCAR/CONTCAR with explicit element symbols is required.')
    structure = poscar.structure
    if len(structure) != data['natoms']:
        raise ValueError('Structure atom count differs from DOSCAR; supply a matching structure.')
    spins = [Spin.up, Spin.down][:data['spins']]
    total = Dos(data['efermi'], data['energies'], dict(zip(spins, data['total'])))
    aggregated = len(data['orbitals']) <= 4
    pdos = {}
    for site, atom in zip(structure, data['projected']):
        pdos[site] = {}
        for column, name in enumerate(data['orbitals']):
            # Aggregated l data are represented once, solely for summed-d analysis.
            orbital = {'s':Orbital.s, 'p':Orbital.py, 'd':Orbital.dxy, 'f':Orbital.f_3}.get(name)
            if orbital is None: orbital = Orbital(LM.index(name))
            pdos[site][orbital] = {spin:np.array([row[column] for row in channel])
                                  for spin,channel in zip(spins, atom)}
    return CompleteDos(structure,total,pdos), aggregated, str(source)


def analyze(request):
    try:
        import numpy as np
        from pymatgen.electronic_structure.core import Spin, OrbitalType
    except ImportError as error:
        raise RuntimeError('pymatgen is unavailable. Run bash install/install-science.sh. '+str(error)) from error
    complete, aggregated, structure_source = load_complete(request['path'], request.get('structure_path'))
    elements = request.get('elements') or []
    indices = request.get('atoms') or []
    if elements and indices: raise ValueError('Select elements OR atom numbers, not both.')
    if indices:
        if any(isinstance(i,bool) or not isinstance(i,int) or i<1 or i>len(complete.structure) for i in indices):
            raise ValueError('Atom numbers are 1-based and must belong to this structure.')
        indices = sorted(set(i-1 for i in indices))
    elif elements:
        unknown = set(elements)-{site.specie.symbol for site in complete.structure}
        if unknown: raise ValueError('Elements not present: '+', '.join(sorted(unknown)))
        indices = [i for i,site in enumerate(complete.structure) if site.specie.symbol in elements]
    else: indices = list(range(len(complete.structure)))
    from p4vasp.dos_selection import parse_orbitals
    orbitals=parse_orbitals(request.get('orbital','d'))
    orbital=','.join(orbitals)
    if aggregated and orbitals != ['d']: raise ValueError('This DOSCAR contains summed d only, not separate d orbitals.')
    spin_name = request.get('spin','both')
    if spin_name not in ('both','up','down'): raise ValueError('Invalid spin selection.')
    spins = list(complete.densities) if spin_name == 'both' else [Spin.up if spin_name == 'up' else Spin.down]
    if any(spin not in complete.densities for spin in spins):
        raise ValueError('Requested spin channel is absent from this calculation.')
    energies = np.asarray(complete.energies, dtype=float)-float(complete.efermi)
    if not np.all(np.isfinite(energies)) or np.any(np.diff(energies)<=0):
        raise ValueError('DOS energy grid must be finite and strictly increasing.')
    density = np.zeros_like(energies)
    found = False
    for i in indices:
        for key,channels in complete.pdos.get(complete.structure[i],{}).items():
            kind = key if isinstance(key, OrbitalType) else key.orbital_type
            if kind == OrbitalType.d and (orbitals==['d'] or key.name.replace('dx2_y2','dx2') in orbitals):
                found = True
                for spin in spins:
                    if spin not in channels: raise ValueError('Projected spin channel is missing.')
                    values=np.asarray(channels[spin],dtype=float)
                    if values.shape!=energies.shape or not np.all(np.isfinite(values)) or np.any(values < -1e-8):
                        raise ValueError('Expected finite nonnegative raw projected spin densities on the DOS grid.')
                    density += np.maximum(values,0.)
    if not found: raise ValueError('No selected d-orbital projection; total DOS cannot substitute for d-DOS.')
    if not np.all(np.isfinite(density)) or np.any(density < -1e-8):
        raise ValueError('Expected finite, nonnegative raw d-DOS densities.')
    density = np.maximum(density,0.)
    from pymatgen.core import Structure
    from p4vasp.dos_metrics import calculate_metrics
    representative=Structure.from_sites([complete.structure[indices[0]]])
    result=calculate_metrics(energies,density,representative,request.get('emin'),request.get('emax'))
    result.update(path=str(Path(request['path']).resolve()), structure_source=structure_source,
                  atoms=[i+1 for i in indices], elements=sorted({complete.structure[i].specie.symbol for i in indices}),
                  orbital=orbital, orbitals=orbitals, spin=spin_name, efermi=float(complete.efermi))
    result['replay']=dict(energies=energies.tolist(),density=density.tolist(),structure=representative.as_dict(),
                          metadata={key:value for key,value in result.items() if key!='rows'})
    return result



def save_result(path,result):
    """One exclusive CSV with metadata and results; no overwriting old exports."""
    with Path(path).open('x',encoding='utf-8',newline='') as stream:
        writer=csv.writer(stream)
        writer.writerow(['Metadata','Value'])
        for key,value in result.items():
            if key not in ('rows','replay'): writer.writerow([key,json.dumps(value,ensure_ascii=False)])
        writer.writerow([]);writer.writerow(['Property','Value','Unit'])
        writer.writerows(result['rows'])


if __name__ == '__main__':
    try:
        request=json.load(sys.stdin)
        if request.get('action')=='version':
            from importlib.metadata import version
            result=dict(pymatgen_version=version('pymatgen'))
        else:result=analyze(request)
        print(json.dumps(dict(ok=True,result=result),allow_nan=False))
    except Exception as error:
        print(json.dumps(dict(ok=False,error=str(error))))
        sys.exit(1)

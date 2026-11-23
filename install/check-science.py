"""Fail early if any scientific environment component cannot load or calculate."""
from importlib.metadata import version
import numpy as np
from ase.build import bulk
from rdkit import Chem
from rdkit.Chem import AllChem
from pymatgen.electronic_structure.dos import Dos, CompleteDos
from pymatgen.electronic_structure.core import Spin, Orbital
from pymatgen.core import Lattice, Structure
from pymatgen.io.vasp.outputs import Vasprun
assert len(bulk('Cu', 'fcc', a=3.615)) == 1
molecule = Chem.AddHs(Chem.MolFromSmiles('CO'))
assert AllChem.EmbedMolecule(molecule, randomSeed=42) == 0
assert AllChem.UFFOptimizeMolecule(molecule, maxIters=500) == 0
for name in ('get_band_center', 'get_band_width', 'get_band_filling', 'get_upper_band_edge'):
    assert callable(getattr(CompleteDos, name, None)), name
dos = Dos(0., np.linspace(-2., 2., 101), {Spin.up: np.ones(101)})
assert np.isfinite(dos.get_interpolated_value(0.)[Spin.up])
structure = Structure(Lattice.cubic(4.), ['Fe'], [[0., 0., 0.]])
energies = np.linspace(-3., 1., 401)
densities = {Spin.up: np.ones_like(energies)}
complete = CompleteDos(structure, Dos(0., energies, densities),
                       {structure[0]: {Orbital.dxy: densities}})
assert abs(complete.get_band_center() + 1.) < 1e-10
assert abs(complete.get_band_width() - np.sqrt(4./3.)) < 1e-4

for name in ('ase', 'rdkit', 'pymatgen'):
    print(name, version(name))
print('PASS: ASE bulk, RDKit embedding/optimization, pymatgen DOS/VASP imports')

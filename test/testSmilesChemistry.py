"""Run with the optional RDKit Python; verifies real chemistry and optimization."""
import math
import unittest
from unittest.mock import patch
from rdkit import Chem
from rdkit.Chem import AllChem
from p4vasp.smiles_builder import build_geometry

class Chemistry(unittest.TestCase):
    def test_explicit_hydrogens_convergence_and_reproducibility(self):
        first=build_geometry('CCO');second=build_geometry('CCO')
        self.assertEqual(len(first['symbols']),9)
        self.assertEqual(first['symbols'].count('H'),6)
        self.assertTrue(first['converged']);self.assertGreater(first['converged_conformers'],0)
        self.assertTrue(math.isfinite(first['energy']))
        self.assertEqual(first['positions'],second['positions'])
        self.assertIsNone(first['multiplicity'])
        self.assertTrue(1.2<math.dist(first['positions'][1],first['positions'][2])<1.6)

    def test_charges_and_radical_spin_not_guessed(self):
        for smiles,charge in [('[NH4+]',1),('[O-]C=O',-1),('[CH3]',0),('O=O',0)]:
            result=build_geometry(smiles)
            self.assertEqual(result['charge'],charge);self.assertIsNone(result['multiplicity'])
        self.assertIn('Radical',build_geometry('[CH3]')['warning'])

    def test_stereochemistry_preserved_in_actual_coordinates(self):
        for smiles in ('F[C@](Cl)(Br)I','F[C@@](Cl)(Br)I'):
            result=build_geometry(smiles)
            mol=Chem.AddHs(Chem.MolFromSmiles(smiles))
            expected=Chem.FindMolChiralCenters(mol)
            conf=Chem.Conformer(mol.GetNumAtoms())
            for i,point in enumerate(result['positions']):conf.SetAtomPosition(i,point)
            mol.AddConformer(conf)
            Chem.AssignAtomChiralTagsFromStructure(mol,replaceExistingTags=True)
            Chem.AssignStereochemistry(mol,cleanIt=True,force=True)
            self.assertEqual(Chem.FindMolChiralCenters(mol),expected)
        self.assertIn('Unspecified',build_geometry('CC(O)C(=O)O')['warning'])

    def test_uff_fallback(self):
        self.assertEqual(build_geometry('B')['forcefield'],'UFF')

    def test_invalid_fragment_metal_and_size_rejected(self):
        for smiles in ('','not smiles','C.C','[Fe+2]','C'*101):
            with self.subTest(smiles=smiles[:20]),self.assertRaises(ValueError):build_geometry(smiles)

    def test_failed_optimization_never_labelled_success(self):
        with patch.object(AllChem,'MMFFOptimizeMoleculeConfs',return_value=[(1,4.0)]):
            with self.assertRaisesRegex(ValueError,'did not converge'):build_geometry('CCO')
        with patch.object(AllChem,'MMFFHasAllMoleculeParams',return_value=False),patch.object(AllChem,'UFFHasAllMoleculeParams',return_value=False):
            with self.assertRaisesRegex(ValueError,'No complete'):build_geometry('CCO')

if __name__=='__main__':unittest.main()

"""Actual ASE/NumPy parser and thermochemistry, plus independent numerical checks."""
import copy
from io import StringIO
import math
from pathlib import Path
import tempfile
import unittest
from ase import units
from p4vasp.vibrations import read_outcar,thermochemistry,displaced_structure
from p4vasp.Structure import Structure
from vibration_fixtures import write_calculation


class VibrationsTest(unittest.TestCase):
    def setUp(self):
        self.temporary=tempfile.TemporaryDirectory();self.root=Path(self.temporary.name)
        self.addCleanup(self.temporary.cleanup)

    def data(self,**kwargs):return read_outcar(write_calculation(self.root/str(len(list(self.root.iterdir()))),**kwargs))

    def test_physical_vectors_scale_sign_and_selective_flags(self):
        data=self.data();self.assertEqual(len(data['modes']),6)
        self.assertEqual(data['vector_convention'],'physical OUTCAR vectors')
        self.assertEqual(data['constraints_source'],'POSCAR')
        self.assertAlmostEqual(data['modes'][0]['max_displacement'],.4)
        before=copy.deepcopy(data)
        for scale in (-1,-.1,0,.1,.2,1):
            structure=displaced_structure(data,0,scale)
            self.assertAlmostEqual(structure[0][0],4+scale*.4)
            self.assertAlmostEqual(structure[1][0],5.2-scale*.2)
            self.assertEqual([bool(v) for v in structure.selective[1]],[True,False,True])
            self.assertEqual(list(structure.basis[1]),[0,11,0])
        self.assertEqual(data,before)
        with self.assertRaises(ValueError):displaced_structure(data,0,1.1)
        stream=StringIO();displaced_structure(data,0,.2).write(stream)
        reread=Structure();reread.read(StringIO(stream.getvalue()));reread.setCartesian()
        self.assertAlmostEqual(reread[0][0],4.08)
        self.assertEqual(reread.info[0].element.strip(),'C')

    def test_low_nwrite_species_and_mass_summary(self):
        # Reduced-verbosity OUTCAR may omit VRHFIN/per-potential masses entirely.
        for marker in ('POTCAR:', 'TITEL ='):
            path=write_calculation(self.root/marker.replace(':','').replace('=',''),physical=False)
            text=path.read_text().replace('VRHFIN =C: s2p2',marker+' PAW_PBE C_sv 01Jan2000')
            text=text.replace('VRHFIN =O: s2p4',marker+' PAW_PBE O 01Jan2000')
            text=text.replace('POMASS = 12.000;','').replace('POMASS = 16.000;','')
            text=marker+' PAW_PBE C_sv 01Jan2000\n'+marker+' PAW_PBE O 01Jan2000\n'+text
            path.write_text(text+'\n Mass of Ions in am\n POMASS = 12.000 16.000\n')
            data=read_outcar(path)
            self.assertEqual(data['symbols'],['C','O'])
            self.assertEqual(data['masses'],[12,16])
            self.assertEqual(data['constraints_source'],'POSCAR')
            self.assertAlmostEqual(data['modes'][0]['vectors'][0][0],.4/math.sqrt(12))
            self.assertAlmostEqual(data['modes'][0]['vectors'][1][0],-.2/math.sqrt(16))

    def test_mass_weighted_conversion_and_missing_flags(self):
        data=self.data(physical=False,flags=False)
        self.assertAlmostEqual(data['modes'][0]['vectors'][0][0],.4/math.sqrt(12))
        self.assertAlmostEqual(data['modes'][0]['vectors'][1][0],-.2/math.sqrt(16))
        self.assertIsNone(data['constraints_source']);self.assertTrue(data['warnings'])

    def test_geometry_mismatch_and_incomplete_mode_count(self):
        path=write_calculation(self.root/'mismatch')
        reference=path.parent/'POSCAR'
        reference.write_text(reference.read_text().replace('5.2 5 6','7.2 5 6'))
        self.assertIsNone(read_outcar(path)['constraints_source'])
        path=write_calculation(self.root/'incomplete')
        text=path.read_text();path.write_text(text[:text.rfind('5 f =')])
        with self.assertRaises(ValueError):read_outcar(path)
        path=write_calculation(self.root/'masses',physical=False)
        path.write_text(path.read_text().replace('POMASS','MISSING'))
        with self.assertRaisesRegex(ValueError,'POMASS'):read_outcar(path)

    def test_truncated_inconsistent_and_missing_mode_data(self):
        path=write_calculation(self.root/'bad')
        original=path.read_text()
        for text in (original.rsplit('\n',3)[0],original.replace('6 f =','7 f ='),
                     original.replace('4 5 6 0.400000','4 5 6 nan'), 'no frequency calculation'):
            path.write_text(text)
            with self.assertRaises((ValueError,StopIteration)):read_outcar(path)
        # A final empty section must not silently reuse an older complete result.
        path.write_text(original+'\nEigenvectors after division by SQRT(mass)\n')
        with self.assertRaises(ValueError):read_outcar(path)

    def request(self,data,**kwargs):
        result=dict(data=data,selected=[1,2,3,4,5],state='ts',model='harmonic',temperature=298.15,
                    pressure=101325,confirm_exclusions=True,floor=0,energy='')
        result.update(kwargs);return result

    def test_harmonic_against_analytic_formula_and_energy_shift(self):
        data=self.data();request=self.request(data);r=thermochemistry(request)
        energies=[m['cm1']*units.invcm for m in data['modes'][1:]];kT=units.kB*298.15
        zpe=sum(energies)/2
        u=zpe+sum(e/math.expm1(e/kT) for e in energies)
        entropy=units.kB*sum(e/kT/math.expm1(e/kT)-math.log1p(-math.exp(-e/kT)) for e in energies)
        self.assertAlmostEqual(r['ZPE_eV'],zpe,12)
        self.assertAlmostEqual(r['correction_eV'],u-298.15*entropy,12)
        shifted=thermochemistry(dict(request,energy=-10))
        self.assertAlmostEqual(shifted['free_energy_eV'],r['free_energy_eV']-10,12)
        self.assertAlmostEqual(shifted['correction_eV'],r['correction_eV'],12)
        floor=thermochemistry(dict(request,floor=350))
        self.assertEqual(floor['effective_cm1'],[350,350,400,500,600])

    def test_gas_pressure_symmetry_spin_and_count_validation(self):
        data=self.data(imaginary=())
        request=self.request(data,selected=[5],state='minimum',model='gas',geometry='linear',symmetry='1',spin='0')
        r=thermochemistry(request);self.assertEqual(r['kind'],'G')
        for setting,value,sign in (('pressure',202650,1),('symmetry','2',1),('spin','0.5',-1)):
            other=thermochemistry(dict(request,**{setting:value}))
            self.assertAlmostEqual(other['free_energy_eV']-r['free_energy_eV'],sign*units.kB*298.15*math.log(2),11)
        for changes in ({'selected':[4,5]},{'geometry':'nonlinear'},{'spin':'0.2'},{'symmetry':'0'}):
            with self.assertRaises(ValueError):thermochemistry(dict(request,**changes))

    def test_imaginary_exclusion_and_low_frequency_policy(self):
        data=self.data()
        for changes in ({'state':'minimum'},{'confirm_exclusions':False},{'selected':[0,1]},
                        {'temperature':0},{'floor':-1},{'selected':[1,1]}):
            with self.assertRaises(ValueError):thermochemistry(self.request(data,**changes))
        data=self.data(imaginary=(1,2))
        with self.assertRaises(ValueError):thermochemistry(self.request(data,selected=[2,3,4,5]))
        r=thermochemistry(self.request(data,selected=[2,3,4,5],imaginary_tolerance=150))
        self.assertEqual(r['excluded_modes'],[1,2])
        self.assertEqual(r['request_settings']['imaginary_tolerance'],150)


if __name__=='__main__':unittest.main()

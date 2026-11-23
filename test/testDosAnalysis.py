"""Real pymatgen calculations against analytic spectra and both VASP readers."""
import csv
import json
import math
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from dos_projected_fixtures import projected_calculation
from p4vasp.dos_analysis import analyze,save_result
from p4vasp.dos_data import read_doscar

ROOT=Path(__file__).resolve().parents[1]

class DosAnalysisTest(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.folder=projected_calculation(self.tmp.name,xml=True)

    def run_analysis(self,**kwargs):
        return analyze(dict(path=str(self.folder/'DOSCAR'),**kwargs))

    def test_gaussian_moments_spin_and_site_selection(self):
        for selection,center in [({'atoms':[1],'spin':'up'},-1.),({'elements':['Ni'],'spin':'down'},2.),
                                 ({'atoms':[1],'spin':'both'},-.5)]:
            result=self.run_analysis(**selection)
            self.assertAlmostEqual(result['rows'][0][1],center,places=8)
            expected=math.sqrt(.6**2+.5**2) if selection.get('spin')=='both' else .6
            self.assertAlmostEqual(result['rows'][1][1],expected,places=8)
        result=self.run_analysis(atoms=[1],spin='up')
        # Independent Gaussian CDF and value at EF; finite-grid trapezoid tolerance.
        expected=.5*(1+math.erf(1/(.6*math.sqrt(2))))
        self.assertAlmostEqual(result['rows'][2][1],expected,delta=2e-4)
        self.assertAlmostEqual(result['rows'][4][1],15*math.exp(-.5*(1/.6)**2),places=8)
        # Gaussian Hilbert peak is approximately center + 1.307*sigma.
        self.assertAlmostEqual(result['rows'][3][1],-1.+1.307*.6,delta=.05)
        self.assertEqual(result['atoms'],[1]);self.assertEqual(result['energy_reference'],'E−EF')

    def test_xml_matches_doscar_and_d_orbitals(self):
        a=self.run_analysis(atoms=[1],spin='down',orbital='dx2')
        b=analyze(dict(path=str(self.folder/'vasprun.xml'),atoms=[1],spin='down',orbital='dx2'))
        for row1,row2 in zip(a['rows'],b['rows']):self.assertAlmostEqual(row1[1],row2[1],places=9)
        self.assertAlmostEqual(a['rows'][0][1],0.,places=9)
        whole=self.run_analysis(atoms=[1],spin='down')
        self.assertAlmostEqual(whole['rows'][4][1],a['rows'][4][1]*3,places=8)

    def test_window_interpolation_filling_and_invariance(self):
        before=(self.folder/'DOSCAR').read_bytes()
        result=self.run_analysis(atoms=[1],spin='up',emin=-2.013,emax=.117)
        self.assertEqual((result['emin'],result['emax']),(-2.013,.117))
        self.assertTrue(-2.013<result['rows'][0][1]<.117)
        self.assertGreaterEqual(result['rows'][2][1],0);self.assertLessEqual(result['rows'][2][1],1)
        self.assertEqual(self.run_analysis(atoms=[1],emin=1.,emax=3.)['rows'][2][1],0.)
        self.assertAlmostEqual(self.run_analysis(atoms=[1],emin=-3.,emax=-1.)['rows'][2][1],1.)
        self.assertEqual((self.folder/'DOSCAR').read_bytes(),before)

    def test_aggregated_and_nonspin_layouts(self):
        for spin in (False,True):
            with tempfile.TemporaryDirectory() as tmp:
                p=projected_calculation(tmp,spin=spin,aggregate=True,xml=True)
                result=analyze(dict(path=str(p/'DOSCAR'),atoms=[1],spin='up'))
                self.assertAlmostEqual(result['rows'][0][1],-1.,places=8)
                xml_result=analyze(dict(path=str(p/'vasprun.xml'),atoms=[1],spin='up'))
                self.assertAlmostEqual(xml_result['rows'][0][1],-1.,places=8)
                with self.assertRaisesRegex(ValueError,'summed d'):
                    analyze(dict(path=str(p/'DOSCAR'),orbital='dxy'))
                if not spin:
                    with self.assertRaisesRegex(ValueError,'absent'):
                        analyze(dict(path=str(p/'DOSCAR'),spin='down'))

    def test_reject_missing_mismatched_and_invalid_inputs(self):
        for args in ({'atoms':[0]},{'atoms':[3]},{'elements':['C']},{'atoms':[1],'elements':['Fe']},
                     {'emin':1,'emax':-1},{'emin':-11},{'emax':float('nan')},{'spin':'invalid'}):
            with self.subTest(args=args),self.assertRaises(ValueError):self.run_analysis(**args)
        poscar=self.folder/'POSCAR';poscar.unlink()
        with self.assertRaisesRegex(ValueError,'matching POSCAR'):self.run_analysis()
        (self.folder/'INCAR').write_text('LSORBIT = .TRUE.\n')
        with self.assertRaisesRegex(ValueError,'collinear'):read_doscar(self.folder/'DOSCAR')

    def test_strict_projected_reader(self):
        path=self.folder/'DOSCAR';original=path.read_text()
        data=read_doscar(path)
        self.assertEqual(data['orbitals'][8],'dx2');self.assertEqual(len(data['projected']),2)
        self.assertEqual(len(data['projected'][0]),2)
        for bad in (original.rsplit('\n',3)[0], original+'1 2 3 4\n',
                    original.replace('12 -8 401 2 1','12 -8 400 2 1',1)):
            path.write_text(bad)
            with self.assertRaises(ValueError):read_doscar(path)
        # Only total DOS remains readable by original reader, but cannot be analyzed.
        path.write_text('\n'.join(original.splitlines()[:407])+'\n')
        self.assertEqual(read_doscar(path)['projected'],[])
        with self.assertRaisesRegex(ValueError,'total DOS only'):self.run_analysis()

    def test_zero_negative_nonuniform_and_structure_mismatch(self):
        path=self.folder/'DOSCAR';original=path.read_text()
        lines=original.splitlines()
        fields=lines[408].split();fields[9]='-1';lines[408]=' '.join(fields)
        path.write_text('\n'.join(lines)+'\n')
        with self.assertRaisesRegex(ValueError,'Negative projected'):self.run_analysis()
        # Move one shared grid point in total and both projected blocks.
        lines=original.splitlines()
        for start in (6,408,810):
            fields=lines[start+150].split();fields[0]=str(float(fields[0])+.005)
            lines[start+150]=' '.join(fields)
        path.write_text('\n'.join(lines)+'\n')
        result=self.run_analysis(atoms=[1],spin='up')
        self.assertIsNone(result['rows'][3][1]);self.assertTrue(result['notes'])
        lines=original.splitlines()
        for start in (408,810):
            for index in range(start,start+401):
                fields=lines[index].split();fields[9:]=['0']*10;lines[index]=' '.join(fields)
        path.write_text('\n'.join(lines)+'\n')
        with self.assertRaisesRegex(ValueError,'zero weight'):self.run_analysis()
        path.write_text(original)
        poscar=self.folder/'POSCAR'
        poscar.write_text('One Fe\n1\n4 0 0\n0 4 0\n0 0 4\nFe\n1\nDirect\n0 0 0\n')
        with self.assertRaisesRegex(ValueError,'atom count differs'):self.run_analysis()

    def test_worker_protocol_and_exclusive_metadata_export(self):
        env=dict(os.environ);env.pop('PYTHONPATH',None)
        process=subprocess.run([str(ROOT/'.venv-science/bin/python'),str(ROOT/'lib/p4vasp/dos_analysis.py')],
            input=json.dumps(dict(path=str(self.folder/'DOSCAR'),atoms=[1],spin='up')),
            text=True,capture_output=True,env=env,timeout=30)
        self.assertEqual(process.returncode,0,process.stderr)
        result=json.loads(process.stdout)['result']
        path=self.folder/'result.csv';save_result(path,result)
        with path.open() as stream: rows=list(csv.reader(stream))
        self.assertIn(['Property','Value','Unit'],rows)
        self.assertTrue(any(row and row[0]=='atoms' and row[1]=='[1]' for row in rows))
        with self.assertRaises(FileExistsError):save_result(path,result)

if __name__=='__main__':unittest.main()

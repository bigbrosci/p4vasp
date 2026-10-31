"""Full periodic reference, nullable edits, precision and failure recovery."""
from pathlib import Path
import json
import shutil
import tempfile
import unittest
from unittest.mock import patch
from p4vasp.element_data import ElementData, COLUMNS, runtime_values, apply_catalog
from p4vasp.resource_data import ResourceStore, FILES, validate

ROOT = Path(__file__).resolve().parents[1]

class Elements(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        root=Path(self.temp.name)
        for path in FILES.values():
            target=root/'data'/path;target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(ROOT/'data'/path,target)
        self.store=ResourceStore(root,root/'backups');self.data=ElementData(self.store)

    def test_complete_reference_and_noop(self):
        self.assertEqual(len(COLUMNS),10)
        self.assertEqual(len(self.data.rows),118)
        self.assertEqual([row[1] for row in self.data.rows],list(map(str,range(1,119))))
        self.assertEqual(self.data.rows[0][:2],['H','1'])
        self.assertEqual(self.data.rows[-1][:2],['Og','118'])
        self.assertEqual(self.data.rows[-1][3:7],['']*4)
        self.assertEqual(self.data.rows[0][8:10],['',''])
        self.assertEqual(self.data.save(self.data.rows),[])
        self.assertEqual(sum(row[2]!='' for row in self.data.rows),118)
        self.assertEqual(sum(row[3]!='' for row in self.data.rows),62)
        self.assertEqual(sum(row[4]!='' for row in self.data.rows),109)
        self.assertIsNone(self.data.catalog['elements'][-1]['covalent'])

    def test_joined_save_preserves_legacy_and_unrelated_presets(self):
        xml=self.store.read('elements')[1]
        config=json.loads(self.store.read('incar')[0])
        covalent=[record['covalent'] for record in self.data.catalog['elements']]
        rows=[row[:] for row in self.data.rows]
        rows[0][2:]=['1.01','1.3','51','77','102','-1.5','2','0.5']
        self.assertEqual(len(self.data.save(rows)),2)
        self.assertEqual(self.data.rows[0][2:7],rows[0][2:7])
        result=json.loads(self.store.read('incar')[0])
        self.assertEqual(result['categories'],config['categories'])
        self.assertEqual(result['elements']['mag_value']['Og'],config['elements']['mag_value']['Og'])
        self.assertEqual(self.store.read('elements')[1],xml)
        self.assertEqual([r['covalent'] for r in self.data.catalog['elements']],covalent)
        rows=[row[:] for row in self.data.rows]; rows[0][8]=''
        self.data.save(rows)
        self.assertNotIn('H',json.loads(self.store.read('incar')[0])['elements']['u_value'])

    def test_invalid_and_conflicting_edits_do_not_write(self):
        before={key:self.store.read(key)[1] for key in ('periodic','incar')}
        for col,value in [(2,'0'),(4,'256'),(5,'1.5'),(6,'-1'),(7,'nan'),(8,'oops')]:
            rows=[row[:] for row in self.data.rows];rows[0][col]=value
            with self.assertRaises(ValueError):self.data.save(rows)
            for key in before:self.assertEqual(self.store.read(key)[1],before[key])
        self.store.path('incar').write_bytes(before['incar']+b'\n')
        with self.assertRaises(ValueError):self.data.save(self.data.rows)

    def test_nullable_edits_and_runtime_fallback(self):
        rows=[row[:] for row in self.data.rows]
        rows[-1][3:7]=['2.2','1','2','3']
        self.data.save(rows)
        self.assertEqual(self.data.rows[-1][3:7],['2.2','1','2','3'])
        rows=[row[:] for row in self.data.rows];rows[-1][2:7]=['']*5
        self.data.save(rows)
        self.assertEqual(self.data.rows[-1][2:7],['']*5)
        record=self.data.catalog['elements'][-1]
        self.assertIsNone(record['mass'])
        self.assertEqual(runtime_values(record),dict(mass=0,radius=1,covalent=0,red=1,green=1,blue=1))
        self.assertEqual(self.data.serialize(self.data.rows),{})

    def test_rgb_conversion_preserves_unedited_precision(self):
        before=self.data.catalog['elements']
        rows=[row[:] for row in self.data.rows];rows[0][2]='1.02'
        self.data.save(rows)
        for a,b in zip(before,self.data.catalog['elements']):
            self.assertEqual([a[k] for k in ('red','green','blue')],[b[k] for k in ('red','green','blue')])
        rows=[row[:] for row in self.data.rows]; rows[0][4:7]=['0','128','255']
        self.data.save(rows)
        self.assertEqual(self.data.rows[0][4:7],['0','128','255'])
        self.assertAlmostEqual(self.data.catalog['elements'][0]['green'],128/255)

    def test_second_write_failure_rolls_back_first(self):
        before={key:self.store.read(key)[1] for key in ('periodic','incar')}
        rows=[row[:] for row in self.data.rows];rows[0][2]='1.01';rows[0][7]='2'
        save=self.store.save
        def fail(key,*args):
            if key=='incar':raise PermissionError('read only')
            return save(key,*args)
        with patch.object(self.store,'save',side_effect=fail):
            with self.assertRaises(PermissionError):self.data.save(rows)
        for key in before:self.assertEqual(self.store.read(key)[1],before[key])

    def test_schema_rejects_wrong_identity_and_nonfinite(self):
        for field,value in [('number',0),('mass',float('nan')),('red',2)]:
            data=json.loads(self.store.read('periodic')[0]);data['elements'][0][field]=value
            with self.assertRaises(ValueError):validate('periodic',json.dumps(data))

    def test_gui_loader_preserves_personal_override_priority(self):
        import p4vasp.util as util
        user=Path(self.temp.name)/'personal';user.mkdir()
        xml=self.store.read('elements')[0].replace('1.0080','2.0080')
        (user/'atomtypes.xml').write_text(xml)
        with patch.object(util,'atomtypes_',None), patch.object(util,'getPathChain',return_value=[str(self.store.root),str(user)]), patch('p4vasp.resource_data.ResourceStore',return_value=self.store):
            info=util.getAtomtypes()
            self.assertAlmostEqual(info.getRecordForElement('H').mass,2.008)
            self.assertAlmostEqual(info.getRecordForElement('Og').mass,294.214)

    def test_native_atominfo_and_export_styles(self):
        from p4vasp.Structure import AtomInfo
        info=apply_catalog(AtomInfo(str(self.store.path('elements'))),self.store)
        self.assertAlmostEqual(info.getRecordForElement('Og').mass,294.214)
        self.assertEqual(info.getRecordForElement('Og').radius,1)
        self.assertEqual(info.getRecordForElement('Og').covalent,0)
        self.assertAlmostEqual(info.getRecordForElement('Be').red,.761)
        import p4vasp
        from p4vasp.render_cli import atom_styles
        with patch.object(p4vasp,'p4vasp_home',str(Path(self.temp.name))):
            styles=atom_styles()
        self.assertEqual(len([s for s in styles if s in {row[0] for row in self.data.rows}]),118)
        self.assertEqual(styles['Og'],(1,(1,1,1),0))

if __name__=='__main__':unittest.main()

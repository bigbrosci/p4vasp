"""Personal edits survive upstream defaults and are consumed in a fresh process."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from p4vasp.resource_data import ResourceStore, FILES
from p4vasp.element_data import ElementData

ROOT = Path(__file__).resolve().parents[1]

class PersonalData(unittest.TestCase):
    def test_restart_update_and_runtime_consumers(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            home = folder/'home'
            profile = home/'.p4vasp/resources'
            for relative in FILES.values():
                dest = folder/'data'/relative
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT/'data'/relative, dest)
            store = ResourceStore(folder, folder/'backups', user_root=profile)
            originals = {key:(folder/'data'/FILES[key]).read_bytes() for key in ('periodic','incar')}
            data = ElementData(store)
            rows = [row[:] for row in data.rows]
            rows[5][2:10] = ['13.2','0.9','12','34','56','3','4','1']
            data.save(rows)
            for key, original in originals.items():
                self.assertEqual((folder/'data'/FILES[key]).read_bytes(), original)
            # Simulate git pull changing both an edited and an unedited default.
            path = folder/'data'/FILES['periodic']
            catalog = json.loads(path.read_text())
            catalog['elements'][5]['mass'] = 12.5
            catalog['elements'][7]['mass'] = 17.0
            path.write_text(json.dumps(catalog))
            fresh = ElementData(ResourceStore(folder, folder/'backups', user_root=profile))
            self.assertEqual(list(map(float, fresh.rows[5][2:10])), list(map(float, rows[5][2:10])))
            self.assertEqual(float(fresh.rows[7][2]), 17.0)
            with self.assertRaises(ValueError): data.save(rows)
            # Native Python loaders in a new interpreter; no inherited cache.
            script = '''
import p4vasp
p4vasp.p4vasp_home = ROOT
import p4vasp.util as util
util.getPathChain = lambda: [ROOT+'/data', HOME+'/.p4vasp']
from p4vasp.incar_generator import load_presets
from p4vasp.viewer_style import covalent_atomtypes, display_values
record = util.getAtomtypes().getRecordForElement('C')
assert record.mass == 13.2, record.mass
assert abs(record.red - 12/255) < 1e-10
assert covalent_atomtypes().getRecordForElement('C').radius == .9
assert display_values(['C'], [99], [(1,1,1)])[0] == [.9]
assert record.covalent != .9
config = load_presets()['elements']
assert config['mag_value']['C'] == 3
assert config['u_value']['C'] == 4
assert config['j_value']['C'] == 1
'''
            # Legacy XML must not undo explicit saved edits.
            (home/'.p4vasp/atomtypes.xml').write_bytes((folder/'data/atomtypes.xml').read_bytes())
            script = 'ROOT='+repr(str(folder))+'\nHOME='+repr(str(home))+'\n'+script
            env = dict(os.environ, HOME=str(home), PYTHONPATH=str(ROOT/'lib')+':'+str(ROOT/'src'))
            result = subprocess.run(['/usr/bin/python3','-c',script], env=env, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr[-2500:])
            # Multi-file failure must restore the original effective personal data.
            from unittest.mock import patch
            prior = {key:store.read(key)[1] for key in ('periodic','incar')}
            current = ElementData(store)
            changed = [row[:] for row in current.rows]
            changed[5][2] = '14'
            changed[5][7] = '5'
            save = store.save
            def fail(key, *args):
                if key == 'incar': raise PermissionError('simulated write failure')
                return save(key, *args)
            with patch.object(store, 'save', side_effect=fail):
                with self.assertRaises(PermissionError): current.save(changed)
            for key, content in prior.items(): self.assertEqual(store.read(key)[1], content)
            # Clearing a nonempty default uses a deletion patch.
            cleared = [row[:] for row in current.rows]
            cleared[5][7] = ''
            current.save(cleared)
            self.assertEqual(ElementData(store).rows[5][7], '')


if __name__ == '__main__': unittest.main()

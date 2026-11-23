"""Source dispatcher and frozen-route simulation; not a Windows binary test."""
import json,os,subprocess,sys,tempfile
from pathlib import Path
sys.path.insert(0,str(Path.cwd()/'test'))
from dos_projected_fixtures import projected_calculation
from unittest.mock import patch
from p4vasp.dos_analysis import worker_command
from p4vasp.model_worker import bash_launcher
with patch('p4vasp.model_worker.bundled_worker',return_value=Path('/tmp/worker.exe')):
 assert worker_command()==['/tmp/worker.exe','--dos-analysis']
with tempfile.TemporaryDirectory() as folder:
 root=Path(folder);exe=root/'p4vasp.exe';exe.touch();(root/'p4vasp-console.exe').touch()
 with patch.object(sys,'frozen',True,create=True),patch.object(sys,'executable',str(exe)):
  assert 'p4vasp-console.exe' in bash_launcher()
 source=projected_calculation(root/'data',with_f=True,xml=True)
 for filename in ('DOSCAR','vasprun.xml'):
  run=subprocess.run([sys.executable,'install/windows/model_worker.py','--dos-analysis'],input=json.dumps(dict(path=str(source/filename),atoms=[1],orbital='f_3,f3',spin='up')),text=True,capture_output=True,timeout=60)
  assert run.returncode==0,run.stderr+run.stdout
  result=json.loads(run.stdout)['result'];assert abs(result['rows'][0][1]-1)<1e-8
print('PASS Windows-source DOS dispatcher, bundled route and portable Bash launcher')

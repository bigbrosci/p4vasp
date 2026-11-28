"""Optional ASE bulk worker. The GTK process never imports ASE or its NumPy."""
import json
import os
from pathlib import Path
import subprocess
import sys
import threading

if __package__:
    from p4vasp.bulk_geometry import CRYSTALS, MAX_ATOMS, build_bulk, parameters
else:
    from bulk_geometry import CRYSTALS, MAX_ATOMS, build_bulk, parameters


def worker_command():
    import p4vasp
    from p4vasp.model_worker import scientific_python
    configured = os.environ.get('P4VASP_ASE_PYTHON') or os.environ.get('P4VASP_SCIENCE_PYTHON')
    python = scientific_python('ase')
    if not configured:
        from p4vasp.model_worker import bundled_worker
        bundled=bundled_worker()
        if bundled is not None:return [str(bundled),'--bulk']
    if python is None:
        if getattr(sys, 'frozen', False):
            raise RuntimeError('This portable build does not bundle ASE. Use a configured ASE source environment.')
        python = sys.executable
    script = Path(__file__).resolve()
    if not script.is_file():
        raise RuntimeError('ASE worker source is missing from this build.')
    return [python, str(script), '--worker']


class BulkTask:
    """One short-lived worker, bounded in time; no idle ASE process."""
    def __init__(self, request, callback, timeout=30, command_factory=None, label='Bulk generation'):
        self.request, self.callback, self.timeout = request, callback, timeout
        self.command_factory, self.label = command_factory, label
        self.cancelled = threading.Event()
        self.lock = threading.Lock()
        self.process = None

    def start(self):
        threading.Thread(target=self.run, daemon=True).start()

    def cancel(self):
        self.cancelled.set()
        with self.lock:
            if self.process is not None and self.process.poll() is None:
                try: self.process.terminate()
                except ProcessLookupError: pass

    def run(self):
        result, error = None, None
        try:
            command = (self.command_factory or worker_command)()
            from p4vasp.model_worker import launch_options
            options = launch_options(command)
            with self.lock:
                if self.cancelled.is_set(): raise RuntimeError(self.label+' cancelled.')
                self.process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                                stderr=subprocess.PIPE, text=True, encoding='utf-8', **options)
            try:
                output, stderr = self.process.communicate(json.dumps(self.request), timeout=self.timeout)
            except subprocess.TimeoutExpired:
                self.process.kill(); self.process.communicate()
                raise RuntimeError(self.label+' timed out.')
            if self.cancelled.is_set(): raise RuntimeError(self.label+' cancelled.')
            try: response = json.loads(output)
            except ValueError: raise RuntimeError('ASE worker could not start. Run bash install/install-science.sh, or check P4VASP_ASE_PYTHON. '+stderr[-400:])
            if self.process.returncode or not response.get('ok'):
                raise RuntimeError(response.get('error', 'ASE generation failed.'))
            result = response['result']
        except Exception as exc:
            error = str(exc)
        self.callback(result, error)


if __name__ == '__main__':
    try:
        result = build_bulk(json.load(sys.stdin))
        print(json.dumps({'ok': True, 'result': result}))
    except Exception as error:
        print(json.dumps({'ok': False, 'error': str(error)}))
        sys.exit(1)

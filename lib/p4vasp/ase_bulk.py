"""Optional ASE bulk worker. The GTK process never imports ASE or its NumPy."""
from io import StringIO
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import threading

# Fields are explicit: no inferred lattice constants or crystal structures.
CRYSTALS = {
    'sc': ('a',), 'fcc': ('a',), 'bcc': ('a',), 'diamond': ('a',),
    'hcp': ('a', 'c'), 'bct': ('a', 'c'),
    'rocksalt': ('a',), 'zincblende': ('a',), 'cesiumchloride': ('a',),
    'fluorite': ('a',), 'wurtzite': ('a', 'c', 'u'),
    'orthorhombic': ('a', 'b', 'c'),
    'rhombohedral': ('a', 'alpha'),
}
MAX_ATOMS = 10000


def parameters(request):
    name = str(request.get('name', '')).strip()
    crystal = request.get('crystal')
    mode = request.get('mode', 'primitive')
    if not name or len(name) > 40:
        raise ValueError('Enter an element or formula, e.g. Cu or NaCl.')
    if crystal not in CRYSTALS or mode not in ('primitive', 'orthorhombic', 'cubic'):
        raise ValueError('Choose a supported crystal and cell type.')
    values = {}
    for key in CRYSTALS[crystal]:
        try: value = float(request.get(key, ''))
        except (ValueError, TypeError): raise ValueError('Enter a numeric '+key+'.')
        if not math.isfinite(value) or value <= 0:
            raise ValueError(key+' must be positive and finite.')
        if key == 'alpha' and value >= 120:
            raise ValueError('Rhombohedral alpha must be between 0 and 120 degrees.')
        if key == 'u' and value >= 1:
            raise ValueError('Wurtzite u must be between 0 and 1.')
        values[key] = value
    repeat = request.get('repeat', (1, 1, 1))
    if not isinstance(repeat, (list, tuple)) or len(repeat) != 3:
        raise ValueError('Enter three positive integer supercell repetitions.')
    counts = []
    for value in repeat:
        if isinstance(value, bool) or str(value).strip() not in tuple(str(i) for i in range(1, 101)):
            raise ValueError('Each repetition must be an integer from 1 to 100.')
        counts.append(int(value))
    if math.prod(counts) > MAX_ATOMS:
        raise ValueError('Supercell exceeds the 10000 atom limit.')
    return name, crystal, mode, values, tuple(counts)


def build_bulk(request):
    name, crystal, mode, values, repeat = parameters(request)
    try:
        import ase
        from ase.build import bulk
        from ase.io import write
        from ase.formula import Formula
        from ase.data import atomic_numbers
    except ImportError as error:
        raise RuntimeError('ASE is unavailable. Run bash install/install-ase.sh in the p4vasp checkout.') from error
    composition = Formula(name).count()
    if not composition or any(symbol not in atomic_numbers or symbol == 'X' for symbol in composition):
        raise ValueError('Use valid element symbols in the chemical formula.')
    if sum(composition.values()) > 3:
        raise ValueError('Enter one prototype formula unit (e.g. Cu, NaCl or CaF2), not a supercell formula.')
    try:
        atoms = bulk(name, crystalstructure=crystal, orthorhombic=mode == 'orthorhombic',
                     cubic=mode == 'cubic', **values)
    except KeyError as error:
        raise ValueError('ASE has no basis for this formula and crystal. Choose another supported prototype.') from error
    if len(atoms)*math.prod(repeat) > MAX_ATOMS:
        raise ValueError('Supercell exceeds the 10000 atom limit.')
    atoms = atoms.repeat(repeat)
    if atoms.cell.rank != 3 or not math.isfinite(atoms.get_volume()) or atoms.get_volume() <= 1e-10:
        raise ValueError('The requested cell is degenerate.')
    stream = StringIO()
    write(stream, atoms, format='vasp', direct=True, sort=True, vasp5=True)
    return {'poscar': stream.getvalue(), 'atoms': len(atoms), 'formula': atoms.get_chemical_formula(),
            'cell': atoms.cell.array.tolist(), 'volume': atoms.get_volume(), 'ase_version': ase.__version__,
            'request': request}


def worker_command():
    import p4vasp
    root = Path(p4vasp.p4vasp_home)
    configured = os.environ.get('P4VASP_ASE_PYTHON')
    candidates = [root/'.venv-ase/bin/python', root/'.venv-ase/Scripts/python.exe']
    python = configured or next((str(path) for path in candidates if path.is_file()), None)
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
    def __init__(self, request, callback, timeout=30):
        self.request, self.callback, self.timeout = request, callback, timeout
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
            command = worker_command()
            from p4vasp.model_worker import launch_options
            options = launch_options(command)
            with self.lock:
                if self.cancelled.is_set(): raise RuntimeError('Bulk generation cancelled.')
                self.process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                                stderr=subprocess.PIPE, text=True, encoding='utf-8', **options)
            try:
                output, stderr = self.process.communicate(json.dumps(self.request), timeout=self.timeout)
            except subprocess.TimeoutExpired:
                self.process.kill(); self.process.communicate()
                raise RuntimeError('ASE bulk generation timed out.')
            if self.cancelled.is_set(): raise RuntimeError('Bulk generation cancelled.')
            try: response = json.loads(output)
            except ValueError: raise RuntimeError('ASE worker could not start. Run bash install/install-ase.sh, or check P4VASP_ASE_PYTHON. '+stderr[-400:])
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

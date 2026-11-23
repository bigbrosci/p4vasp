#!/usr/bin/env bash
# Optional isolated DOS analysis environment; leaves GTK/ASE/RDKit unchanged.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BOOTSTRAP_PYTHON="${PYTHON:-python3}"
"$BOOTSTRAP_PYTHON" -c 'import sys; sys.exit("pymatgen requires Python 3.11 or newer. Set PYTHON=/path/to/python3.") if sys.version_info < (3, 11) else None'
"$BOOTSTRAP_PYTHON" -m venv "$ROOT/.venv-pymatgen"
"$ROOT/.venv-pymatgen/bin/python" -m pip install 'pymatgen==2026.10.24'
"$ROOT/.venv-pymatgen/bin/python" - <<'PY'
from importlib.metadata import version
from pymatgen.electronic_structure.dos import CompleteDos
from pymatgen.io.vasp.outputs import Vasprun
for name in ('get_band_center', 'get_band_width', 'get_band_filling', 'get_upper_band_edge'):
    if not callable(getattr(CompleteDos, name, None)):
        raise RuntimeError('Required DOS analysis interface is missing: '+name)
print('pymatgen DOS environment ready; pymatgen', version('pymatgen'))
PY
printf '\nPython interpreter: %s\n' "$ROOT/.venv-pymatgen/bin/python"
printf 'Installation does not enable DOS analysis controls; GUI integration is a separate step.\n'

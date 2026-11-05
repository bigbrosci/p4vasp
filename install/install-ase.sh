#!/usr/bin/env bash
# Optional isolated ASE model builder; leaves the GTK interpreter unchanged.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BOOTSTRAP_PYTHON="${PYTHON:-python3}"
"$BOOTSTRAP_PYTHON" -m venv "$ROOT/.venv-ase"
"$ROOT/.venv-ase/bin/python" -m pip install 'ase==3.29.0'
"$ROOT/.venv-ase/bin/python" -c 'import ase; print("ASE model environment ready; ASE", ase.__version__)'

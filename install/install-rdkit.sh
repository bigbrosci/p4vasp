#!/usr/bin/env bash
# Optional isolated SMILES builder; never changes the GTK application's Python.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BOOTSTRAP_PYTHON="${PYTHON:-python3}"
"$BOOTSTRAP_PYTHON" -m venv "$ROOT/.venv-smiles"
"$ROOT/.venv-smiles/bin/python" -m pip install rdkit
"$ROOT/.venv-smiles/bin/python" -c 'import rdkit; print("SMILES environment ready; RDKit", rdkit.__version__)'

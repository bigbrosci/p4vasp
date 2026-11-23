#!/usr/bin/env bash
# Shared ASE/RDKit/pymatgen environment, independent of GTK/native extensions.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BOOTSTRAP_PYTHON="${PYTHON:-python3}"
"$BOOTSTRAP_PYTHON" -c 'import sys; sys.exit("Science environment requires Python >=3.11. Set PYTHON=/path/to/python3.") if sys.version_info < (3, 11) else None'
"$BOOTSTRAP_PYTHON" -m venv "$ROOT/.venv-science"
"$ROOT/.venv-science/bin/python" -m pip install -r "$ROOT/install/science-requirements.txt"
"$ROOT/.venv-science/bin/python" -m pip check
"$ROOT/.venv-science/bin/python" "$ROOT/install/check-science.py"
printf '\nScience environment ready: %s\n' "$ROOT/.venv-science/bin/python"
printf 'Restart p4vasp to use it. Legacy environments are preserved.\n'

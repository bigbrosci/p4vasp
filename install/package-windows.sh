#!/usr/bin/env bash
set -euo pipefail
if [[ "${MSYSTEM:-}" != UCRT64 ]]; then
    echo "Run this script in MSYS2 UCRT64, from a dedicated Windows checkout." >&2
    exit 1
fi
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
PYTHONPATH="$ROOT/lib" /ucrt64/bin/python -c 'import _cp4vasp'
/ucrt64/bin/python -m PyInstaller --noconfirm \
    --distpath "$ROOT/dist/windows" --workpath "$ROOT/build/windows" \
    "$ROOT/install/windows/p4vasp.spec"
cp "$ROOT/LICENSE" "$ROOT/dist/windows/p4vasp/"
cp "$ROOT/install/windows/README.txt" "$ROOT/dist/windows/p4vasp/README.txt"

# Scientific wheels use an isolated official CPython, separate from GTK/UCRT.
if [[ -z "${P4VASP_MODEL_PYTHON:-}" ]]; then
    /ucrt64/bin/python "$ROOT/install/windows/prepare_model_env.py"
    P4VASP_MODEL_PYTHON="$(/ucrt64/bin/python "$ROOT/install/windows/prepare_model_env.py" --print-path)"
fi
"$P4VASP_MODEL_PYTHON" -m PyInstaller --noconfirm \
    --distpath "$ROOT/dist/windows-model" --workpath "$ROOT/build/windows/model-worker" \
    "$ROOT/install/windows/model_worker.spec"
mkdir -p "$ROOT/dist/windows/p4vasp/model-worker"
cp -R "$ROOT/dist/windows-model/p4vasp-model-worker/." "$ROOT/dist/windows/p4vasp/model-worker/"
"$ROOT/dist/windows/p4vasp/model-worker/p4vasp-model-worker.exe" --versions > "$ROOT/dist/windows/p4vasp/MODEL-VERSIONS.json"

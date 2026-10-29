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

#!/usr/bin/env bash
# Run inside MSYS2 UCRT64, in a dedicated Windows checkout.
set -euo pipefail
if [[ "${MSYSTEM:-}" != UCRT64 ]]; then
    echo "Open MSYS2 UCRT64 before running this build." >&2
    exit 1
fi
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHON="${PYTHON:-/ucrt64/bin/python}"
export PYTHON_CONFIG="${PYTHON_CONFIG:-/ucrt64/bin/python3-config}"
export CXX="${CXX:-/ucrt64/bin/g++}"
export SWIG="${SWIG:-/ucrt64/bin/swig}"
exec bash "$ROOT/install/build-unix-py3.sh" "$@"

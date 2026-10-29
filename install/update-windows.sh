#!/usr/bin/env bash
set -euo pipefail
if [[ "${MSYSTEM:-}" != UCRT64 ]]; then
    echo "Open MSYS2 UCRT64 before updating the Windows application." >&2
    exit 1
fi
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
exec /ucrt64/bin/python "$ROOT/install/windows/update_build.py" "$@"

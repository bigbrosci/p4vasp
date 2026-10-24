#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ -z "${PYTHON:-}" ]]; then
    if [[ -x "$ROOT/.venv-macos/bin/python3" ]]; then
        PYTHON="$ROOT/.venv-macos/bin/python3"
    elif [[ -x /usr/bin/python3 ]]; then
        PYTHON=/usr/bin/python3
    else
        PYTHON=python3
    fi
fi

export P4VASP_HOME="$ROOT"
export PYTHONPATH="$ROOT/lib${PYTHONPATH:+:$PYTHONPATH}"
export UBUNTU_MENUPROXY="${UBUNTU_MENUPROXY:-0}"

"$PYTHON" "$ROOT/p4v.py" "$@" &
APP_PID=$!

terminate_app() {
    if kill -0 "$APP_PID" 2>/dev/null; then
        kill "$APP_PID" 2>/dev/null || true
    fi
}

trap 'terminate_app; wait "$APP_PID" 2>/dev/null; exit 130' INT
trap 'terminate_app; wait "$APP_PID" 2>/dev/null; exit 143' TERM

set +e
wait "$APP_PID"
STATUS=$?
set -e

trap - INT TERM
exit "$STATUS"

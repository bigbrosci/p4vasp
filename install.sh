#!/usr/bin/env bash
set -euo pipefail

# Run this script to install p4vasp globally for every user.

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ "$(uname -s)" == "Darwin" ]]; then
    echo "Detected macOS; using the Python 3 Homebrew bootstrap."
    exec bash "$ROOT/install/macos-bootstrap.sh" --no-launch "$@"
fi

if command -v apt-get >/dev/null 2>&1; then
    echo "Detected apt-get; using the Python 3 Ubuntu bootstrap."
    exec bash "$ROOT/install/ubuntu-bootstrap.sh" --no-launch "$@"
fi

make config
sudo make install

#!/usr/bin/env bash
# Compatibility entry: install the shared scientific environment.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
exec bash "$ROOT/install/install-science.sh" "$@"

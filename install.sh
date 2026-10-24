#!/usr/bin/env bash
# Unified installation entry point for Linux and macOS.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

usage() {
    cat <<'HELP'
Usage: bash install.sh [options] [-- p4vasp arguments]

Automatically selects Ubuntu/Debian, other Linux, or macOS installation.
Ubuntu/Debian: install apt dependencies, rebuild, then launch if a display exists.
Other Linux: use preinstalled dependencies, rebuild, then launch if possible.
macOS: use the existing Homebrew/Python environment installation flow.

  --skip-deps     Skip system package installation (macOS still prepares its venv).
  --skip-apt      Alias for --skip-deps, retained for compatibility.
  --skip-brew     Alias for --skip-deps, retained for compatibility.
  --skip-build    Skip rebuilding the native extension (not for source updates).
  --deps-only     Install dependencies only (Ubuntu/Debian and macOS).
  --build-only    Rebuild without system package installation or GUI launch.
  --no-launch     Install/build without starting the GUI.
  --dry-run       Print the detected route and command; make no changes.
  -h, --help      Show this help without installing anything.

macOS requires Homebrew and Xcode Command Line Tools already installed.
Other Linux requires Python development files, GTK3/PyGObject/Cairo, FLTK 1.3,
OpenGL/GLU, a C++ compiler, SWIG, NumPy and PyOpenGL; see install.md.
HELP
}

SKIP_DEPS=0
DEPS_ONLY=0
DRY_RUN=0
OPTIONS=()
APP_ARGS=()
while (($#)); do
    case "$1" in
        -h|--help) usage; exit 0 ;;
        --dry-run) DRY_RUN=1 ;;
        --skip-deps|--skip-apt|--skip-brew) SKIP_DEPS=1 ;;
        --deps-only) DEPS_ONLY=1; OPTIONS+=("$1") ;;
        --build-only) SKIP_DEPS=1; OPTIONS+=("$1") ;;
        --skip-build|--no-launch) OPTIONS+=("$1") ;;
        --) shift; APP_ARGS+=("$@"); break ;;
        --*) echo "Unknown installer option: $1 (use -- before application arguments)" >&2; exit 2 ;;
        *) APP_ARGS+=("$1") ;;
    esac
    shift
done
if [[ "$DEPS_ONLY" -eq 1 && "$SKIP_DEPS" -eq 1 ]]; then
    echo "--deps-only cannot be combined with --skip-deps or --build-only." >&2
    exit 2
fi

case "$(uname -s)" in
    Darwin)
        ROUTE="macOS (Homebrew)"
        BACKEND="$ROOT/install/macos-bootstrap.sh"
        SKIP_OPTION=--skip-brew
        ;;
    Linux)
        # Read only distribution fields, never execute os-release as shell code.
        RELEASE="${P4VASP_OS_RELEASE:-/etc/os-release}"
        DIST_ID=""
        DIST_LIKE=""
        if [[ -r "$RELEASE" ]]; then
            while IFS='=' read -r key value; do
                value="${value%\"}"; value="${value#\"}"
                value="${value%\'}"; value="${value#\'}"
                case "$key" in
                    ID) DIST_ID="$value" ;;
                    ID_LIKE) DIST_LIKE="$value" ;;
                esac
            done < "$RELEASE"
        fi
        BACKEND="$ROOT/install/ubuntu-bootstrap.sh"
        SKIP_OPTION=--skip-apt
        case " $DIST_ID $DIST_LIKE " in
            *" ubuntu "*|*" debian "*) ROUTE="Ubuntu/Debian family (apt)" ;;
            *)
                ROUTE="Other Linux (${DIST_ID:-unknown}; preinstalled dependencies)"
                if [[ "$DEPS_ONLY" -eq 1 ]]; then
                    echo "Automatic dependency installation is not supported for ${DIST_ID:-this Linux distribution}. See install.md." >&2
                    exit 2
                fi
                SKIP_DEPS=1
                ;;
        esac
        ;;
    *) echo "Unsupported operating system: $(uname -s). Supported: Linux and macOS." >&2; exit 2 ;;
esac

COMMAND=(bash "$BACKEND")
if [[ "$SKIP_DEPS" -eq 1 ]]; then COMMAND+=("$SKIP_OPTION"); fi
# Conditional expansion also works with macOS Bash 3.2 and nounset.
if [[ "${OPTIONS+x}" ]] && ((${#OPTIONS[@]})); then COMMAND+=("${OPTIONS[@]}"); fi
if [[ "${APP_ARGS+x}" ]] && ((${#APP_ARGS[@]})); then COMMAND+=(-- "${APP_ARGS[@]}"); fi
printf 'Detected: %s\n' "$ROUTE"
if [[ "$DRY_RUN" -eq 1 ]]; then
    printf 'Would run:'
    printf ' %q' "${COMMAND[@]}"
    printf '\n'
    exit 0
fi
exec "${COMMAND[@]}"

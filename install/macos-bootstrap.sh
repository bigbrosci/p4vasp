#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

INSTALL_DEPS=1
BUILD_EXT=1
LAUNCH=1
APP_ARGS=()

usage() {
    cat <<'EOF'
Usage: bash macos-start.sh [options] [p4vasp arguments]

Options:
  --skip-brew     Do not run brew install; assume dependencies are installed.
  --skip-build    Do not rebuild the native p4vasp extension.
  --deps-only     Install Homebrew packages and create the Python environment, then exit.
  --build-only    Build the native extension and exit.
  --no-launch     Install/build, but do not start the GUI.
  -h, --help      Show this help.
EOF
}

while (($#)); do
    case "$1" in
        --skip-brew)
            INSTALL_DEPS=0
            ;;
        --skip-build)
            BUILD_EXT=0
            ;;
        --deps-only)
            BUILD_EXT=0
            LAUNCH=0
            ;;
        --build-only)
            INSTALL_DEPS=0
            LAUNCH=0
            ;;
        --no-launch)
            LAUNCH=0
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        --)
            shift
            APP_ARGS+=("$@")
            break
            ;;
        *)
            APP_ARGS+=("$1")
            ;;
    esac
    shift
done

if [[ "$(uname -s)" != "Darwin" ]]; then
    echo "This installer is intended for macOS." >&2
    exit 1
fi

if ! xcode-select -p >/dev/null 2>&1; then
    echo "Xcode Command Line Tools are required. Run: xcode-select --install" >&2
    exit 1
fi

if ! command -v brew >/dev/null 2>&1; then
    echo "Homebrew is required. Install it from https://brew.sh and rerun this script." >&2
    exit 1
fi

BREW_PREFIX="$(brew --prefix)"
export PATH="$BREW_PREFIX/bin:$BREW_PREFIX/sbin:$PATH"

BREW_PACKAGES=(
    fltk@1.3
    gtk+3
    numpy
    pkg-config
    py3cairo
    pygobject3
    python
    swig
)

find_brew_python() {
    local candidate
    for candidate in \
        "$BREW_PREFIX/bin/python3" \
        "$BREW_PREFIX/opt/python/libexec/bin/python3" \
        "$BREW_PREFIX/opt/python@3.14/bin/python3.14" \
        "$BREW_PREFIX/opt/python@3.13/bin/python3.13" \
        "$BREW_PREFIX/opt/python@3.12/bin/python3.12"; do
        if [[ -x "$candidate" ]]; then
            echo "$candidate"
            return
        fi
    done
    echo "Could not find a Homebrew Python 3 executable." >&2
    exit 1
}

find_brew_python_config() {
    local python_bin=$1
    local candidate="${python_bin}-config"
    if [[ -x "$candidate" ]]; then
        echo "$candidate"
        return
    fi
    for candidate in \
        "$BREW_PREFIX/bin/python3-config" \
        "$BREW_PREFIX/opt/python/libexec/bin/python3-config" \
        "$BREW_PREFIX/opt/python@3.14/bin/python3.14-config" \
        "$BREW_PREFIX/opt/python@3.13/bin/python3.13-config" \
        "$BREW_PREFIX/opt/python@3.12/bin/python3.12-config"; do
        if [[ -x "$candidate" ]]; then
            echo "$candidate"
            return
        fi
    done
    echo "Could not find python3-config for Homebrew Python." >&2
    exit 1
}

find_brew_fltk_config() {
    local candidate
    for candidate in \
        "$BREW_PREFIX/opt/fltk@1.3/bin/fltk-config" \
        "$BREW_PREFIX/bin/fltk-config"; do
        if [[ -x "$candidate" ]]; then
            echo "$candidate"
            return
        fi
    done
    echo "Could not find fltk-config. Try: brew install fltk@1.3" >&2
    exit 1
}

if [[ "$INSTALL_DEPS" -eq 1 ]]; then
    echo "Installing macOS packages for p4vasp..."
    brew install "${BREW_PACKAGES[@]}"
fi

BREW_PYTHON="$(find_brew_python)"
BREW_PYTHON_CONFIG="$(find_brew_python_config "$BREW_PYTHON")"
BREW_FLTK_CONFIG="$(find_brew_fltk_config)"
VENV="$ROOT/.venv-macos"

if [[ ! -x "$VENV/bin/python3" ]]; then
    echo "Creating macOS Python environment..."
    "$BREW_PYTHON" -m venv --system-site-packages "$VENV"
fi

echo "Installing Python OpenGL bindings..."
"$VENV/bin/python3" -m pip install --upgrade pip setuptools wheel
"$VENV/bin/python3" -m pip install --upgrade PyOpenGL
"$VENV/bin/python3" -m pip install --upgrade PyOpenGL_accelerate || \
    echo "PyOpenGL_accelerate is optional and was skipped."

if [[ "$BUILD_EXT" -eq 1 ]]; then
    PYTHON="$VENV/bin/python3" \
    PYTHON_CONFIG="$BREW_PYTHON_CONFIG" \
    FLTK_CONFIG="$BREW_FLTK_CONFIG" \
    bash "$ROOT/install/build-macos-py3.sh"
fi

if [[ "$LAUNCH" -eq 1 ]]; then
    if [[ "${APP_ARGS+x}" ]] && ((${#APP_ARGS[@]})); then
        PYTHON="$VENV/bin/python3" exec bash "$ROOT/run-p4vasp.sh" "${APP_ARGS[@]}"
    else
        PYTHON="$VENV/bin/python3" exec bash "$ROOT/run-p4vasp.sh"
    fi
fi

#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

INSTALL_DEPS=1
BUILD_EXT=1
LAUNCH=1
APP_ARGS=()

usage() {
    cat <<'EOF'
Usage: bash ubuntu-start.sh [options] [p4vasp arguments]

Options:
  --skip-apt      Do not run apt-get; assume dependencies are installed.
  --skip-build    Do not rebuild the native p4vasp extension.
  --deps-only     Install Ubuntu packages and exit.
  --build-only    Build the native extension and exit.
  --no-launch     Install/build, but do not start the GUI.
  -h, --help      Show this help.
EOF
}

while (($#)); do
    case "$1" in
        --skip-apt)
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

APT_PACKAGES=(
    build-essential
    ca-certificates
    g++
    gir1.2-gtk-3.0
    libfltk1.3-dev
    libgl1-mesa-dev
    libglu1-mesa-dev
    libx11-dev
    libxcursor-dev
    libxext-dev
    libxft-dev
    libxinerama-dev
    libxrender-dev
    make
    mesa-common-dev
    pkg-config
    python3
    python3-cairo
    python3-dev
    python3-gi
    python3-numpy
    python3-opengl
    swig
)

install_deps() {
    if ! command -v apt-get >/dev/null 2>&1; then
        echo "apt-get was not found. This installer is intended for Ubuntu/Debian systems." >&2
        exit 1
    fi

    local sudo_cmd=()
    if [[ "${EUID:-$(id -u)}" -ne 0 ]]; then
        if ! command -v sudo >/dev/null 2>&1; then
            echo "sudo was not found. Run this script as root or install sudo first." >&2
            exit 1
        fi
        sudo_cmd=(sudo)
    fi

    echo "Installing Ubuntu packages for p4vasp..."
    "${sudo_cmd[@]}" apt-get update
    "${sudo_cmd[@]}" env DEBIAN_FRONTEND=noninteractive \
        apt-get install -y --no-install-recommends "${APT_PACKAGES[@]}"
}

if [[ "$INSTALL_DEPS" -eq 1 ]]; then
    install_deps
fi

if [[ "$BUILD_EXT" -eq 1 ]]; then
    bash "$ROOT/install/build-ubuntu-py3.sh"
fi

if [[ "$LAUNCH" -eq 1 ]]; then
    if [[ -z "${DISPLAY:-}" && -z "${WAYLAND_DISPLAY:-}" ]]; then
        echo "Build finished, but no graphical display was detected."
        echo "Start p4vasp later with: bash run-p4vasp.sh"
        exit 0
    fi
    if [[ "${APP_ARGS+x}" ]] && ((${#APP_ARGS[@]})); then
        exec bash "$ROOT/run-p4vasp.sh" "${APP_ARGS[@]}"
    else
        exec bash "$ROOT/run-p4vasp.sh"
    fi
fi

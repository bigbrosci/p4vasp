#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ODP_DIR="$ROOT/odpdom"
SRC_DIR="$ROOT/src"
LIB_DIR="$ROOT/lib"
UNAME_S="$(uname -s)"

if [[ "$UNAME_S" == "Darwin" ]]; then
    CXX="${CXX:-c++}"
else
    CXX="${CXX:-g++}"
fi

SWIG="${SWIG:-swig}"

if [[ -z "${PYTHON:-}" ]]; then
    if [[ "$UNAME_S" == "Darwin" && -x "$ROOT/.venv-macos/bin/python3" ]]; then
        PYTHON="$ROOT/.venv-macos/bin/python3"
    elif [[ -x /usr/bin/python3 ]]; then
        PYTHON=/usr/bin/python3
    else
        PYTHON=python3
    fi
fi

if [[ -z "${PYTHON_CONFIG:-}" ]]; then
    if [[ "$PYTHON" == /* && -x "${PYTHON}-config" ]]; then
        PYTHON_CONFIG="${PYTHON}-config"
    else
        PYTHON_CONFIG=python3-config
    fi
fi

require_command() {
    if ! command -v "$1" >/dev/null 2>&1; then
        echo "Required command '$1' was not found in PATH." >&2
        exit 1
    fi
}

python_value() {
    "$PYTHON" - "$@" <<'PY'
import importlib.machinery
import sys
import sysconfig

key = sys.argv[1]
if key == "include":
    print(sysconfig.get_path("include"))
elif key == "ext_suffix":
    print(importlib.machinery.EXTENSION_SUFFIXES[0])
else:
    raise SystemExit(f"unknown query: {key}")
PY
}

find_fltk_config() {
    if [[ -n "${FLTK_CONFIG:-}" ]]; then
        echo "$FLTK_CONFIG"
        return
    fi
    if command -v fltk-config >/dev/null 2>&1; then
        command -v fltk-config
        return
    fi
    if command -v fltk1.3-config >/dev/null 2>&1; then
        command -v fltk1.3-config
        return
    fi
    echo "fltk-config was not found. Install FLTK development files first." >&2
    exit 1
}

require_command "$PYTHON"
require_command "$CXX"
require_command "$SWIG"
require_command "$PYTHON_CONFIG"

FLTK_CONFIG_BIN="$(find_fltk_config)"
PY_INCLUDE="$(python_value include)"
EXT_SUFFIX="$(python_value ext_suffix)"
PY_LDFLAGS_VALUE="$("$PYTHON_CONFIG" --embed --ldflags 2>/dev/null || "$PYTHON_CONFIG" --ldflags)"
FLTK_CXXFLAGS_VALUE="$("$FLTK_CONFIG_BIN" --use-gl --cxxflags)"
FLTK_LDFLAGS_VALUE="$("$FLTK_CONFIG_BIN" --use-gl --ldflags)"

# fltk-config/python-config output shell-style flags without embedded whitespace.
read -r -a PY_LDFLAGS <<< "$PY_LDFLAGS_VALUE"
read -r -a FLTK_CXXFLAGS <<< "$FLTK_CXXFLAGS_VALUE"
read -r -a FLTK_LDFLAGS <<< "$FLTK_LDFLAGS_VALUE"

LINK_MODE=(-shared)
OPENGL_CXXFLAGS=()
OPENGL_LDFLAGS=(-lGLU -lGL)

if [[ "$UNAME_S" == "Darwin" ]]; then
    LINK_MODE=(-bundle -undefined dynamic_lookup)
    OPENGL_CXXFLAGS=(-DGL_SILENCE_DEPRECATION "-I$ROOT/install/macos-compat")
    OPENGL_LDFLAGS=(-framework OpenGL)
    PY_LDFLAGS=()
fi

mkdir -p "$LIB_DIR"

PY_DOM_DEFINE='-DPY_DOMEXC_MODULE="p4vasp.ODPdom."'
COMMON_DEFINES=("$PY_DOM_DEFINE" -DCHECK=1 -DVERBOSE=0 -DNO_GL_LISTS_S -DNO_THREADS)

echo "Using Python executable: $PYTHON"
echo "Using Python include: $PY_INCLUDE"
echo "Using extension suffix: $EXT_SUFFIX"
echo "Using FLTK config: $FLTK_CONFIG_BIN"

pushd "$ODP_DIR" >/dev/null
echo "Generating odpdom/cODP_wrap.cpp"
"$SWIG" -python -c++ "$PY_DOM_DEFINE" -Iinclude -o cODP_wrap.cpp ODP.i
popd >/dev/null

ODP_SOURCES=(
    string.cpp
    markText.cpp
    Exceptions.cpp
    Node.cpp
    NodeSequences.cpp
    Document.cpp
    CharacterNodes.cpp
    Element.cpp
    parse.cpp
)
ODP_FLAGS=(-std=gnu++11 -fPIC -w "$PY_DOM_DEFINE" "-I$PY_INCLUDE" -Iinclude)
pushd "$ODP_DIR" >/dev/null
for source in "${ODP_SOURCES[@]}"; do
    object="${source%.*}.o"
    echo "Compiling odpdom/$source"
    "$CXX" "${ODP_FLAGS[@]}" -c "$source" -o "$object"
done
popd >/dev/null

if [[ ! -f "$SRC_DIR/cp4vasp_wrap.cpp" ]]; then
    pushd "$SRC_DIR" >/dev/null
    echo "Generating src/cp4vasp_wrap.cpp"
    "$SWIG" -python -c++ -Wall "${COMMON_DEFINES[@]}" \
        -I../odpdom/include -Iinclude -o cp4vasp_wrap.cpp cp4vasp.i
    popd >/dev/null
fi

P4VASP_SOURCES=(
    Exceptions.cpp
    AtomtypesRecord.cpp
    AtomInfo.cpp
    vecutils3d.cpp
    vecutils.cpp
    utils.cpp
    domutils.cpp
    FArray.cpp
    Structure.cpp
    Chgcar.cpp
    ChgcarSmear.cpp
    Process.cpp
    VisFLWindow.cpp
    VisMain.cpp
    VisWindow.cpp
    VisEvent.cpp
    VisDrawer.cpp
    VisNavDrawer.cpp
    VisStructureDrawer.cpp
    VisStructureArrowsDrawer.cpp
    VisIsosurfaceDrawer.cpp
    ClassInterface.cpp
    VisSlideDrawer.cpp
    VisPrimitiveDrawer.cpp
    VisBackEvent.cpp
    cp4vasp_wrap.cpp
)
P4VASP_FLAGS=(
    -std=gnu++11
    -fPIC
    -w
    "$PY_DOM_DEFINE"
    -DCHECK=1
    -DVERBOSE=0
    -DNO_GL_LISTS_S
    -DNO_THREADS
    -D_LARGEFILE_SOURCE
    -D_LARGEFILE64_SOURCE
    -D_FILE_OFFSET_BITS=64
    "-I$PY_INCLUDE"
    -Iinclude
    -I../odpdom/include
    "${FLTK_CXXFLAGS[@]}"
    "${OPENGL_CXXFLAGS[@]}"
)
pushd "$SRC_DIR" >/dev/null
for source in "${P4VASP_SOURCES[@]}"; do
    object="${source%.*}.o"
    echo "Compiling src/$source"
    "$CXX" "${P4VASP_FLAGS[@]}" -c "$source" -o "$object"
done
popd >/dev/null

P4VASP_OBJECTS=()
for source in "${P4VASP_SOURCES[@]}"; do
    P4VASP_OBJECTS+=("$SRC_DIR/${source%.*}.o")
done

ODP_OBJECTS=()
for source in "${ODP_SOURCES[@]}"; do
    ODP_OBJECTS+=("$ODP_DIR/${source%.*}.o")
done

OUTPUT="$LIB_DIR/_cp4vasp$EXT_SUFFIX"
rm -f "$LIB_DIR"/_cp4vasp*.so

echo "Linking $OUTPUT"
LINK_CMD=(
    "$CXX" "${LINK_MODE[@]}" -o "$OUTPUT"
    "${P4VASP_OBJECTS[@]}"
    "${ODP_OBJECTS[@]}"
    "${FLTK_LDFLAGS[@]}"
    "${OPENGL_LDFLAGS[@]}"
)
if [[ "$UNAME_S" != "Darwin" ]]; then
    LINK_CMD+=("${PY_LDFLAGS[@]}")
fi
"${LINK_CMD[@]}"

cp "$SRC_DIR/cp4vasp.py" "$LIB_DIR/cp4vasp.py"

echo "Checking Python imports"
PYTHONPATH="$LIB_DIR${PYTHONPATH:+:$PYTHONPATH}" P4VASP_HOME="$ROOT" \
    "$PYTHON" - <<'PY'
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
import _cp4vasp
import p4vasp
print("p4vasp Unix build OK")
PY

echo "Built $OUTPUT"

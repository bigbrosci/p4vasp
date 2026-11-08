# GTK3 runtime migration

The Python GUI uses PyGObject with GTK 3. The `p4vasp.gtk3` package centralizes
GTK3 widgets, GLib callbacks, GDK helpers, and the resource/table adapters.
Startup and diagnostics no longer request PyGTK 2.

## What changed

- Replaced the GTK1/GTK2 plotting implementations with a shared GTK3 backend in
  `p4vasp.piddle.piddleGTK3`. Cairo image surfaces replace GdkPixmap/GdkGC;
  GTK's `draw` signal paints graphs, and PangoCairo renders text, including
  rotated labels. Plot resizing, keyboard zoom, pointer interaction, and
  background-buffer restoration use GTK3 APIs.
- Applets import the GTK3 runtime explicitly. Old `gtk`, `gobject`, `pango`,
  GTK1 graph, and PIDDLE GTK backend import paths forward to GTK3 for compatibility.
  They contain no GTK2 drawing implementation.
- Fixed table-model insertion/deletion/update propagation, empty models, phonon
  label editing, and selective-dynamics checkbox refreshes.
- Fixed resource loading for frame labels, notebook tabs, slider adjustments,
  menu defaults, numeric properties, progress-bar orientation, and widget sizes.
- Fixed graph event coordinates, repeated canvas initialization, lattice-entry
  callback reentrancy, and outdated file-export and text-buffer calls.
- Added the Cairo bridge dependency to the Ubuntu installer and build checks.

Existing `data/glade2/*.glade` files remain the layout source. The Python resource
loader creates GTK3 widgets directly; libglade and GTK2 are not dependencies.
GTK3-supported deprecated widgets such as GtkTable are still accepted by this
loader. This is a GTK3 runtime migration, not a GTK4 port or a wholesale UI redesign.
Historical generated documentation is not rewritten.

The native FLTK/OpenGL structure windows and GLUT k-point viewer are separate
renderers. This change does not replace their graphics APIs with GTK widgets.

### macOS Quartz event ownership (2026-11-03)

The main GUI calls `p4vasp.gtk3.macos.configure_event_loop()` before native
initialization. On Quartz only, it sets the process-local
`P4VASP_GTK_QUARTZ_EVENT_LOOP=1` flag. Native `VisCheck()` still executes queued
window commands and calls `Fl::flush()`, while GTK owns Cocoa event dequeueing
and forwards non-GTK events to AppKit/FLTK. Independently polling `Fl::check()`
would consume GTK keystrokes before GDK translates them. Standalone native
callers without this flag keep the FLTK loop. Do not set the flag for a native
standalone program without a running GTK Quartz event loop.

At the end of startup, `present_startup()` activates the terminal-launched
macOS application through AppKit and presents the main GTK window once. It
needs neither PyObjC nor Accessibility permission. Other display backends skip
these helpers. This change requires rebuilding the native extension.

Focused desktop check on macOS:

```bash
PYTHONPATH=lib P4VASP_HOME="$PWD" .venv-macos/bin/python3 test/testMacQuartzInput.py
```

This posts Cocoa events only to its own windows and checks activation, actual
SMILES typing/deletion, a second entry, native Delete delivery, and returning
to GTK. `--legacy` disables the bridge and is expected to fail at text input.
It does not validate physical keyboard layouts, input methods, or chemistry.

## Dependencies and launch

On Ubuntu/Debian:

```bash
sudo apt-get install python3-gi python3-gi-cairo python3-cairo gir1.2-gtk-3.0
./p4v.sh
```

The existing macOS bootstrap installs GTK3, PyGObject, and py3cairo. This migration
was exercised on Linux; macOS execution has not been verified in this session.

## Verification

The Vibrations toolbar entry (2026-11-07) loads `vibrations.glade` and
`VibrationsApplet`, whose page uses a GTK/Cairo 3D projection, independently of
the native FLTK Show window. ASE parsing/thermochemistry runs in a short-lived
scientific worker. Selecting Ideal gas opens a bounded, scrollable parameter dialog;
confirmation starts the calculation and confirms the displayed mode selection.
The mode preview now draws skew-cell lattice edges and display-only X/Y/Z
replicas (1..5, up to 12000 displayed atoms), wraps only a display copy of
equilibrium positions, and discovers bonds across displayed neighboring cells.
Replicas move in phase; thermochemistry and POSCAR export use only original atoms.
`viewer_style.py` shares covalent radii, element colors and bond defaults with
the Show applet and molecular previews. Native primitive resolution defaults
to 32 and the structure drawer honors that default; rebuild the native extension
on each target machine for this quality change.
The frequency table has only Mode/cm^-1/Type columns; checkbox selection is
removed. Below the responsive Paned, a two-column tool area places Cell/playback on
the left and Scale/export on the right, stacking at narrow widths while
preserving the 300-pixel frequency region. Thermochemistry is expanded by
default, with compact settings on the left and `thermo_result.py` rendering
a result card on the right (highlighted correction, quantity/value/unit rows,
conditions and mode policy). Calculation completion reveals the result after
layout; invalidation clears it. Harmonic calculations use all
positive modes; gas selection remains in the parameter dialog.
The frequency policy is fixed: positive modes below 50 cm^-1 use 50, all
imaginary modes are excluded, and stationary-point labels do not gate calculation.
The floor/tolerance entries are removed. Gas mode selection reduces vibrational
slots by the excluded imaginary-mode count and requires review.
Result export creates a JSON/Python pair through `thermo_replay.py`; the script
recalculates with ASE independently of GTK/p4vasp and source files. Timers stop on unmap/destroy, pending workers are cancelled,
and display offsets do not mutate the active system. Focused checks:

```bash
PYTHONPATH=lib:src P4VASP_HOME="$PWD" .venv-ase/bin/python test/testVibrations.py
PYTHONPATH=lib:src P4VASP_HOME="$PWD" .venv-ase/bin/python test/testThermoReplay.py
PYTHONPATH=lib:src P4VASP_HOME="$PWD" /usr/bin/python3 test/testVibrationsGtk.py
```

The first requires the optional ASE environment, the second the GUI/native
environment and a display. Both use synthetic frequency tables; see
[the usage guide](vibrations-zh.md) for scientific scope and input conventions.

Run from the checkout root with the compiled cp4vasp extension available:

```bash
PYTHONPATH="$PWD/lib:$PWD/src" P4VASP_HOME="$PWD" /usr/bin/python3 test/test.py
PYTHONPATH="$PWD/lib:$PWD/src" P4VASP_HOME="$PWD" /usr/bin/python3 test/testGtk3.py
/usr/bin/python3 test/run_gtk3_smoke.py
```

The GUI checks require a display (a desktop session or `xvfb-run`). They cover all
40 Glade resource files, Cairo/Pango drawing, resize and zoom, model notifications,
and lattice callbacks. The applet smoke runner uses a synthetic structure and an
empty in-memory database; it tests initialization, not scientific result accuracy
or database connectivity. It does not write user calculation files.

The optional `--include-glut` check also opens the separate k-point viewer. In the
current desktop test environment it fails in PyOpenGL with “Attempt to retrieve
context when no valid context”. This is an unresolved GLUT/OpenGL context issue,
not a GTK2 dependency. The default GTK smoke suite excludes this renderer explicitly.

Migration reference: [GTK's GTK2-to-GTK3 migration guide](https://docs.gtk.org/gtk3/migrating-2to3.html).

## Native structure selection regression

After rebuilding the native extension, the Shift + left-drag selection check
can be run separately with a working display:

```bash
/usr/bin/python3 test/run_box_selection.py
```

It compiles a native test using the build's object files and exercises synthetic
FLTK events against an actual OpenGL structure window. It requires g++,
fltk-config and Python development libraries. It checks toggle rectangle
selection, periodic images, hidden/occluded atoms, idle-Escape clearing, drag cancellation, camera views,
and legacy Space/rotation controls. It does not use the separate GLUT viewer
or validate scientific calculations.

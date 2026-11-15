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
removed. A homogeneous two-column Gtk.Grid organizes three rows: preview/modes,
Cell and playback/Scale and export, then thermochemistry parameters/results.
Horizontal separators and an input-pass-through vertical overlay separator align
all six cells. FlowBox controls wrap within their cells; the old Paned,
responsive orientation callbacks and thermochemistry Expander are removed.
Parameters remain visible. `thermo_result.py` provides a compact four-column
result table (energy item, equation, eV, kJ/mol), single-line headings, bold correction
and entropy explicitly per K. The page removes the nested result-card border;
its actual ASE version remains in the title. Result cells open read-only Entry
text selectors on click, supporting native clipboard copying without model writes. Policy/mode provenance stays in
exported data. Dependency hints remain available before loading data.
The selected mode caption is a top-left, input-pass-through Gtk.Overlay child
over ModeView; it no longer occupies a separate row. Calculation completion reveals the result after
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

## Native Show stroke and lighting quality (2026-11-08)

`VisFLWindow` prefers an available multisample visual and falls back to the
existing RGB/double/depth visual. `VisNavDrawer` honors the antialias toggle,
uses softer ambient/diffuse/specular lighting, and retains native selection and
camera transforms. Cell outlines share the 1-pixel default with ModeView.
`VisStructureDrawer::drawCell()` blends alpha coverage while temporarily disabling
multisampling for line rasterization (needed on the tested llvmpipe driver),
then restores GL attributes before opaque spheres/bonds. Rebuild the extension
on the target device and restart the application.

Focused actual pixel/state regression (synthetic skew cell, display required):

```bash
PYTHONPATH=lib:src P4VASP_HOME="$PWD" /usr/bin/python3 test/testShowQuality.py
```

This compares smoothing off/on and checks preserved coordinates/camera/bond
state plus the default stroke after reopening. On the tested Linux Mesa driver,
line intermediate-gray levels changed from 0 to 45 and the visual had 4 samples.
This is local-driver evidence, not a guarantee for every graphics device.

### Thermochemistry energy endpoints (2026-11-08)

Frequency loading fills E from ionic step 1. The energy entry's Open OUTCAR
button uses the same cancellable worker with action `energy` to read the last
ionic step from a separate file, leaving frequency data unchanged. The p4vasp
parser reads sigma->0 from completed FREE ENERGIE ionic summaries, excluding
electronic SCF iteration energies even when ASE would return them. Reduced
fixtures without summary headings remain supported; TOTEN fallback is labeled. Reports/replay retain energy provenance;
changing frequency source clears/refills the entry, while cancelling/failing an
energy-only load preserves the previous result. No new process type or native
extension changes are needed.

## Uniform main sidebar (2026-11-09)

`frame.glade` defines the nine ToolButtons; the GTK3 adapter loads file icons
at source size and legacy stock icons at theme-dependent size. Frame.createFrame
normalizes only this toolbar: 32-pixel aspect-preserving icon canvases, themed
stock replacements with fallback, transparent theme padding trimmed, and a
persistent Gtk.SizeGroup(BOTH) for equal button dimensions. Menu icons and
other applet toolbars are unchanged.

The frequency page now uses the homogeneous grid described above, superseding
its former deferred orientation changes. The GUI regression measures all nine
button/icon allocations and alternates narrow/wide sizes while checking equal
cell widths, matching row heights and frequency-table bounds.

## XDATCAR trajectory playback (2026-11-13)

`getSystem` dispatches XDATCAR to XdatcarSystemPM, not PoscarSystemPM.
`xdatcar.py` indexes validated frame offsets and parses individual frames through
Structure's POSCAR reader; no ASE dependency or all-frame geometry cache.
Initial/final are independent snapshots. Repeated complete headers allow
per-frame cells; keep the source file unchanged while open.

The existing frame.glade Control ToolButton and swincontrol.glade resources load
through the unchanged GTK3 adapter. StructureWindowApplet defaults XDATCAR to
its full structure sequence. StructureWindowControlApplet labels it XDATCAR
trajectory, switches single-frame endpoint views back to the sequence on step/play,
restarts from the beginning at the end, and avoids duplicate playback timers.
System changes/destruction stop the timer. XML trajectories retain their existing
sequence semantics; no native renderer/binding changes.

Focused checks: `test/testXdatcar.py`, `test/testXdatcarGtk.py` with PYTHONPATH=lib:src
and P4VASP_HOME set to the checkout. The latter exercises real Frame/native viewer,
CLI, File/Open, endpoints, timer progression and normal POSCAR return. Optional
user XDATCAR samples are read only, not included in Git.

## Drawing value semantics (2026-11-14)

PIDDLE Color and Font now implement Python 3 value equality, used by GTK3/Cairo
transparent-color checks and PS/PDF state caching. Color compares exact RGB
components and retains its tuple hash; the old weighted __cmp__ is not used as
an equality or ordering rule. Color/scalar division forwards to its existing
__div__ implementation. Scalar/Color remains unsupported through Python 3
operators; legacy explicit methods remain available.

Font equality uses face/size/bold/italic/underline; hashing uses the same fields,
so a mutable fallback-face list is unhashable. No sorting order is introduced.
Class names, instance fields, constructors and read-only attribute behavior
are retained; protocol-2/current pickle roundtrips passed, but historical user
XML sessions were not validated. Focused checks: test/testDrawingValues.py and,
with a display, test/testDrawingValuesGtk.py.

PS/PDF file output was repaired in the subsequent byte-output batch below.
No new third-party dependency or native rebuild is needed.

## PS/PDF byte output (2026-11-14)

The existing Graph export dialog still loads graphwindow.glade through the GTK3
adapter and dispatches Export.exportPS/exportEPS/exportPDF. A small internal
piddle/fileio.py buffers legacy Latin-1 strings into bytes, keeping PDF offsets
byte-based; paths are written in binary mode and closed by the exporter. Caller
binary streams stay open. StringIO remains a legacy in-memory text view; actual
text-file streams are rejected to avoid encoding/newline corruption. PathLike
PDF paths are supported. Prefixed binary streams retain correct absolute xrefs.

PS finalization state is restored even on encoding errors. Serialization happens
before opening a target path, so serialization errors do not truncate an existing
file; this is not an atomic-write guarantee against disk errors. PDF page streams
use actual byte lengths; optional zlib/ASCII85 compression uses standard-library
byte APIs. Existing old image/PIL helpers are not modernized by this change.

Focused checks: test/testVectorExport.py and test/testVectorExportGtk.py.
Tests validate xref/startxref, object/stream offsets, decompress content, multiple
pages, ownership and failed serialization. Actual DOS dialog output was verified
for PS/EPS/PDF without modifying DOS samples. No external PS/PDF renderer is
available here: signatures/structure/decoded streams are checked, not visual
rendering by an independent reader. Unicode file paths are supported; arbitrary
Unicode font embedding and historical image branches remain outside this batch.

## Remaining graph formats (2026-11-14)

The existing graphwindow.glade export dialog and Export dispatch were exercised
for DATA/AGR/FIG/SVG as well as PS/EPS/PDF. DATA and AGR implementations are
unchanged: tests compare numeric output at the existing formatting precision
and parse exported AGR using the project reader; this is not a lossless-double
or external-Grace rendering guarantee.

FIG custom RGB values are explicitly converted to integers before hexadecimal
formatting, font names accept case variants, and owned UTF-8 output files close
on write errors. SVG uses matching UTF-8 declaration/output, SVG/XLink namespaces
and no obsolete external DTD. Text and style attributes are XML-escaped. Font
fallback construction no longer mutates read-only Font objects and retains all
fallback faces; default family is the CSS generic sans-serif. Save entry points
share the same output implementation. Neither exporter gains a new dependency.

Focused test/testOtherGraphExports.py covers numeric roundtrips, SVG Unicode/XML,
font-state preservation, FIG records and file ownership. Actual DOS dialog tests
now cover all seven formats. The local GdkPixbuf SVG loader independently
rendered exported DOS and its PNG was inspected; no new renderer was installed.
External Xfig/Grace readers, arbitrary FIG Unicode fonts/images, full SVG image
branches and cross-platform rendering remain unverified.


### Legacy SQL import boundary (2026-11-14)

DBApplet remains the Resources entry. Its module and CommitApplet no longer
import db/SQLSystemPM eagerly: legacy constructors load getDatabase, and legacy
result selection loads SQLSystemPM. Class/module names, Glade files, registration
and saved-profile handling remain intact. Do not remove Commit registration based
on its hidden menu: profiles and Windows hidden-import collection use it.

`test/testLegacyDatabaseIsolation.py` checks full Frame/factory/Resources startup
with SQL imports blocked, synthetic legacy XML constructors, and a synthetic
selection callback in fresh GTK processes. No user database is connected. This
is not full legacy SQL/session acceptance; pysqlite2 remains an unresolved legacy
requirement. Local imports may still be collected by packaging, so this change
makes no bundle-size or SQL-driver removal claim.


### Removal of Glade 1 resources (2026-11-14)

The obsolete data/glade tree and util.loadGlade_old were removed after a
per-file audit. data/glade2 and util.loadGlade remain the supported runtime
entry; no layout replacement or adapter search-order change was made.
External plugins using loadGlade_old must migrate their resources/calls; there
is no alias pretending that old layouts can be loaded unchanged by GTK3.
The deleted originals remain in Git history.

The resource test now goes through util.loadGlade and separately resolves and
decodes file icons with the actual GTK3 adapter/GdkPixbuf. All 43 current layouts
and 124 file-image references passed locally; the nine GTK tests and 33 applet
startup checks passed. This does not validate external plugins or all scientific
workflows. Windows GUI spec still collects data recursively; this source tree
no longer contains the removed directory, but no new bundle was built.

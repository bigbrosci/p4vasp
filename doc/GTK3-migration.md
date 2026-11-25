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

The main frame footer (`frame.glade` → `FrameMessageDriver` →
`gtk3/daily_status.py`) uses the local date to look up the read-only bundled
SQLite schedule. Dates outside the schedule use the JSON rotation. The footer
refreshes once a minute while idle and preserves task and error messages. Its
tooltip shows the scheduled date, source details, and reflection question.
Run `test/testDailyStatusGtk.py` with the same environment and display as the
GTK checks below to check calendar lookup, footer layout, and status priority.

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


### Models: defer unopened tab construction (2026-11-14)

ModelsApplet initially constructs only SingleAtomPage. Stable notebook hosts
preserve tab labels/order and the bulk ScrolledWindow. GasPhasePage, BulkPage
and ElementTable are created on their first switch-page signal and retained
for the applet lifetime. Show the host too, including a dynamically created
viewport. GasPhasePage refreshes in its constructor; revisit refreshes once,
while keeping the existing selected-molecule edit-preservation behavior.
No asynchronous GTK widget creation or scientific formula changes are involved.
First access to a tab still pays its construction cost.

A real-GTK regression uses a temporary XYZ/resource library to verify zero
hidden constructors/scans initially, one scan on first gas entry, refresh after
adding a file, and retained charge/bulk/dirty-table edits without reconstruction.
The smoke check now selects tabs before accessing their deferred contents.
Local seven-sample initUI measurements (warm median of the final six) changed
from 13.126 ms to 5.157 ms. These exclude imports, full startup/rendering and
large-library latency; they are not an overall application speed guarantee.

The existing testBulkGtk workflow reached its final compact-window assertion
but failed at 532x409 against 480x320. The unchanged baseline reproduced exactly
the same dimensions. Earlier build/preview/save assertions passed, but the
whole test is not counted as passing; the compact-layout issue remains open.
The separate lazy bulk offscreen screenshot was inspected successfully.


### Local chat-context clipboard action (2026-11-14)

Frame.createFrame adds Edit / Copy for ChatGPT... using the existing menu builder;
no Glade layout or left-toolbar item is added. The callback uses repository
findActive (never creates a Show applet), snapshots the active system's Show
source sequence/index when available, otherwise INITIAL_STRUCTURE. It does not
copy wrapped/hidden/replicated rendering data or auxiliary model/frequency previews.
The p4vasp.chat_context helper summarizes composition/count/physical cell vectors;
normalization uses a private copy, preserving the snapshot and input flags.

The GTK3 dialog uses the shared screen-fitting helper, read-only preview, two
unchecked inclusion options and native clipboard. INCAR is loaded only on opt-in;
full POSCAR uses the existing writer with all source atoms. Character count is
shown without a fabricated token estimate. No network client, API key, browser
launch or external dependency is introduced. This is manual context preparation,
not an AI session or a complete VASP input export.

Four focused helper tests and the real Frame/menu/GTK clipboard test cover source
frame selection, scaling/flags preservation, omitted coordinates, inclusion options,
lazy INCAR and unchanged input. Offscreen dialog content was inspected on a test
white backdrop; the test does not establish Windows/macOS clipboard behavior.


### Vibration mouse navigation follows Show (2026-11-17)

The Vibrations toolbar/Structure menu still opens vibrations.glade through
VibrationsApplet and gtk3.vibrations.VibrationsPage; its embedded ModeView has
no new layout or native-window dependency. Navigation now follows
src/VisNavDrawer.cpp: left rotates, Ctrl-left spins around the screen normal,
middle pans, right horizontal drag applies exp(0.005*dx) zoom. Rotation uses
the column-major makerotmat4 signs/composition from vecutils.cpp, accumulated
as a matrix rather than constrained yaw/pitch; each drag derives from the
press snapshot, independent of intermediate motion-event count. Pan follows
Show's orthographic width sensitivity and rotates with the camera.

Wheel zoom remains a preview shortcut; smooth vertical deltas are supported,
horizontal scroll is not misinterpreted as zoom-out. Release/grab-loss ends a
drag. Zoom retains the preview's existing safety bounds. Fit resets pan/zoom,
while animation/mode changes preserve navigation. Shift-left is reserved for
Show's editing selection and does not rotate this read-only preview. Native
Show itself, source geometry/mode normalization and scientific exports are
unchanged; projection/lighting may still differ between the two backends.

Run `test/testModeViewNavigation.py` with the GUI interpreter/display. Five
actual GTK signal tests use native createrotmat3da coefficients as a rotation
oracle, exercise modifiers/pan/right-zoom/release/grab/scroll and render a
synthetic scene without changing its data. testVibrationsGtk additionally checks
pan retention while playing and selecting another mode. On this Linux/WSL run,
its complete synthetic regression passed but logged two alloc_needed draw
warnings; those screenshots are not used as full-layout evidence. The separate
navigation rendering was inspected. No physical mouse session on native Show,
macOS/Windows run, native rebuild or Windows EXE rebuild was performed.


### Hydrogen ball size (2026-11-17)

viewer_style.ball_radius applies a 1.5 multiplier only to H visual radii.
The native covalent_atomtypes copy changes radius, preserving covalent and the
shared element catalog; Show/molecular preview use that copy. ModeView keeps
unscaled radii for periodic bond discovery and separate ball_radii for drawing.
Other elements and global size controls are unchanged. No native rebuild or
Glade change is required; the existing Windows EXE does not include this update.


### Renamed frequency OUTCAR routing (2026-11-17)

SystemPM.getSystem recognizes OUTCAR, OUTCAR_* and OUTCAR-* basenames case-insensitively,
so OUTCAR_freq is routed to VibrationSystemPM instead of PoscarSystemPM.
The frequency page already passes any explicitly selected path to its reader;
no parser/layout change or sibling-file guessing is added. Invalid frequency
content still raises its original error rather than falling back to POSCAR.
The GUI regression uses OUTCAR-freq for real CLI/File/Open and OUTCAR-frequency
for compact frequency-dialog loading, continuing animation/export/thermochemistry checks.


### Native interactive detail reduced to about 70% (2026-11-21)

Control uses StructureWindowControlApplet / StructureWindowApplet and the same
FLTK/OpenGL StructureWindow as Show; its Glade/GTK3 controls are unchanged.
StructureWindow sets the native default primitive resolution to the shared
viewer_style.INTERACTIVE_PRIMITIVES_RESOLUTION (22, formerly 32) before creating
drawers. Native VisStructureDrawer.init reads that default during first GL init,
so setting a drawer's resolution before init would be overwritten. A fixed value
avoids compounding the reduction when more native windows open. This also applies
to previews that use StructureWindow; Cairo ModeView is unaffected.

22/32 is about 69% of the segment count; sphere stacks fall from 20 to 13, giving
about 45% of the previous sphere tessellation. Cell stroke width/antialiasing,
lighting, atom/bond radii and scientific data are unchanged. This is not an FPS
measurement or a guarantee of 70% perceptual quality. Independent image-export
quality settings are unchanged; raw native screenshots reflect live geometry.

Native Show quality/state/reopen and actual Control XDATCAR navigation/playback
checks pass on this Linux/WSL device, with reduced-detail screenshot inspected.
Fourteen headless export tests pass. No native rebuild is necessary for the Python
default change; no macOS/Windows acceptance or new EXE build was performed.


### ASE Surface page (2026-11-22)

Models toolbar / ModelsApplet / models.glade / GTK3 adapter retains its five
notebook hosts; tab 3 is now a lazily created, scrolled SurfacePage. Neighboring
Bulk/gas/data pages remain lazy and retain settings. The page uses existing
compact file/folder dialogs, InstallHint and shared native model preview.
Fixed atoms are marked using preview-only rings; shared preview selection is
cleared before each new model to avoid leaking markers to Bulk/gas previews.

surface_geometry.py validates requests and invokes ASE metal presets or build.surface
in a SurfaceTask, reusing BulkTask's isolated, bounded/cancellable transport.
Only the worker imports ASE. Custom Miller indices refer to the input cell,
with no conventional-cell conversion. Equivalent-layer count and geometric layer
groups are distinct; vacuum is per side. Replace old constraints with bottom
geometric-layer FixAtoms; stable species grouping keeps POSCAR flags/metadata
aligned. Preserve original bulk/files. Save to a new folder as POSCAR and
surface.json plus rebuild_surface.py/.sh. surface_replay.py embeds the same geometry
core and portable custom bulk input in standalone Python (ASE only). Bash invokes
p4v --surface-replay through surface_cli.py before GTK/native imports, reusing
the bounded scientific worker. Both create new folders and preserve constraints;
these are final construction recipes, not camera history or complete VASP inputs.
Frozen GUI specs include raw geometry/metrics helpers for source embedding;
Windows artifacts still require a target-machine build and verification.

Windows model_worker gains --surface, spec includes geometry/constraints and
future frozen checks exercise surface build/preview/save. These are source/spec
preparations, not a Windows acceptance or new EXE build. No new dependencies or
library version changes; ASE catalog source references were updated.

Focused verification: test/testAseSurface.py with the ASE interpreter checks all
presets, physical Cu(111) plane spacing/vacuum, fixed masks, custom/negative Miller
indices, CIF/species sorting, portable input and worker protocols. With GTK/display,
test/testSurfaceGtk.py exercises actual worker responsiveness, source buttons,
fixed-layer native preview, save/no-overwrite, invalidation and synthetic
cancel/explicit page-destroy behavior. Tests use temporary inputs; full application
shutdown cancellation and Windows/macOS runtime remain unverified.


### Slab Center / Bottom placement (2026-11-22)

SurfacePage adds grouped, button-style radio controls within the existing grid.
Center uses the ASE geometric-bounds convention along z. Bottom translates to
min Cartesian z=0.1 Angstrom, keeping the cell and total vacuum fixed. Both
worker generation and local repositioning use the same scalar offset helper;
existing results are repositioned on private Structure copies without ASE in GTK,
rebuilding a slab or rereading input files. Retain atom order/flags/layer metadata.
Use the existing POSCAR writer's header/flags and 17-digit numeric rows locally
to avoid Direct-coordinate round-trip drift at 0.1 Angstrom; no global writer change.

Summary/JSON distinguish actual bottom/top gaps and placement. The input vacuum
remains half the total empty space; its Bottom label says Half total vacuum.
An insufficient gap is rejected instead of enlarging the cell. Live previews
refresh and default to a side view with cell lines. StructureWindow.fitToStructure
now has opt-in include_cell=True bounds; ordinary Show/Control defaults stay
atom-focused. Shared previews explicitly reset cell visibility between models.

ASE tests independently compare recentering with Atoms.center(axis=2), plus
cell/distances/masks/idempotence and low-vacuum rejection. Real GUI tests verify
buttons, labels, live preview and saved 0.1-Angstrom coordinates/metadata. Native
Show's antialias pixel probe initially returned [0,0]; without altering rendering,
baseline and current rechecks both returned [0,45]. Treat that as an observed
capture-timing limitation, not a new antialias fix. No Windows/macOS build or
full application shutdown acceptance was performed.

### Personal element data (2026-11-22)

Models' `models.glade` hosts the lazy Python `ElementTable` (no XML layout
change). `ResourceStore` overlays personal field patches in
`~/.p4vasp/resources/{periodic,incar}.json` onto bundled defaults; explicit
root-only stores retain direct editing for isolated tools/tests. Table saves
never touch bundled files. `getAtomtypes` reapplies explicitly saved fields
after legacy XML; shared native/Cairo viewer styles honor edited display radii
without changing covalent bond thresholds. `incar_generator.load_presets` uses
the same effective resource reader. Restart applies cached defaults.
Focused checks: `test/testPersonalData.py`, `test/testPersonalDataGtk.py`,
`test/testElementData.py`, `test/testResourceData.py`, `test/testResourceHubGtk.py`.

### Shared scientific worker environment (2026-11-22)

`install/install-science.sh` installs ASE/RDKit/pymatgen into `.venv-science`,
independently of GTK. Bulk, Surface, SMILES and vibration dependency hints copy
this same installer command; their widget layout is unchanged. Existing
feature installers forward to it. `model_worker.scientific_python` centralizes
source interpreter selection while retaining legacy variables/environments;
packaged Windows worker selection remains unchanged. Projected DOS analysis
controls are described in the next section. See `doc/dependencies/README.md` for precedence
and baseline recording.

### Optional d-band analysis (2026-11-22)

Toolbar/menu → ElectronicApplet → existing graphwindowapplet.glade/GTK3 adapter
remains the plot route. The Python-created `DosAnalysis` panel is always visible
on the right as described below. Bounded scrolling keeps controls accessible
without editing shared Graph resources. Existing ElectronicControlApplet uses new
DoscarSystemPM PARTIAL_DOS(_L) arrays from the strict stdlib dos_data reader.
Analysis uses dos_analysis.py in the shared science interpreter via bounded
BulkTask; no pymatgen import in GTK. Parameter/source changes, leaving the graph
and destruction cancel stale jobs. Import failure exposes a copyable installer;
InstallHint's optional bundled flag avoids claiming pymatgen is already in the
older Windows worker. CSV includes scientific definitions and source metadata.
See doc/dos-analysis-zh.md and test/testDosAnalysis{,Gtk}.py.

### Side-by-side DOS and analysis (2026-11-22)

ElectronicApplet reparents only its `vbox2` (existing toolbar/graph) into a
scrollable left child of a horizontal Gtk.Paned, preserving access to toolbar
buttons and labels when the pane is narrow. The right child is DosAnalysis as an always
visible Gtk.Frame, with two-column controls, wrapping property labels and a
scrollable body. Initialize the divider once at 58% plot / 42% analysis, then
leave dragging to the user. Graph menus stay above both panes; graph_box and
GraphCanvas references remain unchanged. Other GraphWindowApplet users and
shared Glade resources are unchanged. testDosAnalysisGtk checks initial widget
state and placement as well as existing calculations and export flows.

### DOS maximization / partial repaint (2026-11-22)

GraphCanvas.render now synchronizes the live DrawingArea allocation, graph page
size and Cairo backing surface before rendering. A newly recreated canvas on an
already-realized widget may receive no new size-allocate signal; it must not
keep the default 500x400 buffer or an earlier graph page size. The regression
in testGtk3 reproduces that boundary without relying on a window resize.
ElectronicApplet coalesces settled-pane redraws through one GLib idle callback;
right-panel parameter/result changes request it, and destroy cancels it. These
redraws preserve curve data and zoom bounds and do not rerun DOS analysis.
testDosAnalysisGtk covers actual maximize/restore, canvas recreation, right
options and analysis, page/surface dimensions, edge pixels and preserved zoom.

### Rounded VASP DOS energy grids (2026-11-22)

Actual local calculation checks exposed rounded printed energy columns that
fail a strict equal-step test. Only for Hilbert upper-edge calculation, grids
within HILBERT_GRID_TOLERANCE (5% of mean step) of the corresponding uniform grid
are linearly resampled. Report that choice in notes/CSV; materially irregular
grids remain unavailable. Existing moment/filling calculations keep the source
grid. testDosAnalysis adds an artificial rounded-grid case checked against a
separate NumPy/SciPy transform. No user calculation files are included in tests.

### Compact DOS controls and standalone analysis script (2026-11-22)

Keep Use last DOS line. DosAnalysis displays only atoms/orbital/spin/E−EF limits
in its completed summary; source/normalization/resampling notes remain in the
tooltip and CSV. Show the actual pymatgen distribution version in the frame
label, queried once per scientific interpreter through a short metadata-only
worker action and cached; the GUI does not import pymatgen. Energy Range (eV)
uses Emin/Emax entries with EF-relative tooltips and no range presets.

Export Python script replaces the Cancel button. Parameter/source changes and
leaving still cancel jobs. dos_metrics.py contains the shared numerical method;
dos_replay.py embeds that code and the selected summed full-grid spectrum in a
standalone script. Its representative one-site structure is an API container,
not VASP calculation input. Scripts require pymatgen but not p4vasp/source files;
optional CLI limits change the window, not the fixed atom/orbital/spin selection.
CSV excludes the embedded replay spectrum. Exports/results refuse overwriting.

### Four d-band results (2026-11-22)

Remove D_d(EF) and its definition metadata from the shared dos_metrics output.
The GUI, CSV and newly exported standalone scripts retain center, width,
window filling and Hilbert upper edge. Selection/energy limits and the other
algorithms stay the same; testDosAnalysisGtk checks four displayed rows.

### Direct spin buttons (2026-11-22)

DosAnalysis uses grouped Both/Up/Down radio buttons styled as compact buttons.
Cached TOTAL_DOS and ElectronicApplet's existing DOS-read completion update
availability without a second file read or worker. Only two-channel data enable
Up/Down; scalar/unknown data select Both and disable the separate channels.
Use-last-line respects that availability. Keep lowercase worker spin values and
source-change invalidation; the numerical backend is unchanged. GTK regression
switches both DOSCAR and XML to scalar data, calculates with Both and returns to
a polarized source, checking exclusivity, restored buttons and regular-width fit.

### Orbital combinations and headless DOS entry (2026-11-23)

Orbital uses three toggle-button rows: s/p and p components, d and its components,
f and its seven components. Each shell excludes its own components; components
and different shells combine. Clearing the last choice restores d. Spin follows
these rows. dos_selection.py supplies shared orbital/atom validation; the worker
sums each selected component once before running unchanged metrics.

p4v.py dispatches the seven positional DOS arguments (or --dos-analysis) before
GTK/native imports. dos_cli.py invokes the existing science worker and writes
exclusive CSV; single-file GUI and render flags keep their existing routes.
Export scripts creates .py/.sh together: Python embeds the selected snapshot,
Bash re-reads the source through p4v and includes an alias-free launcher fallback.
New paired files are exclusive and cleaned up on failure. No shared Glade change.

The projected analysis worker supports s/p/d/f shell totals and components in both
DOSCAR and XML. dos_selection.py provides canonical ordering and per-shell conflict
validation shared by GTK/CLI. Missing selected projections on any selected atom
are errors. Aggregated sources permit shell totals only. f columns follow VASP's
ordered real harmonics; old plotting f1..f7 map to pymatgen f_3..f3 for Use last DOS
line. Metrics use the selected summed spectrum, labels identify its shell or
selected-band for mixed shells, and standalone replay preserves the label.


### Surface source actions (2026-11-24)

SurfacePage replaces the Source combo plus separate loaders with one row of
three toggle actions: Metal preset, Use bulk result, Open POSCAR / CIF.
source_mode changes only after a successful load (or explicit preset choice);
a synchronization guard prevents GTK's programmatic toggle/click callbacks from
re-entering source actions. Cancellation/unavailable Bulk restores button state
without invalidating the previous result. Successful snapshot/file reloads invalidate
results even when the source kind stays the same. ModelsApplet/models.glade host
and toolbar wiring are unchanged; the page is built by the GTK3 adapter code.

Surface Bulk import also copies its build request into read-only Element/a/c
fields, rather than leaving stale preset defaults. Those fields do not override
the full POSCAR snapshot used for cutting. File sources clear the preset fields;
returning to Metal preset restores the user's cached preset entries.


### Periodic element editor (2026-11-25)

ModelsApplet/models.glade still hosts the lazy ElementTable page through the
GTK3 adapter. ElementTable now presents 118 colored buttons in periodic positions,
with group/period headers and detached f-block rows, rather than a TreeView.
PERIODS is shared from element_data.py with the unchanged SingleAtomPage layout.
Tile CSS uses effective catalog RGB with contrasting text; missing colors have a
neutral display fallback only. Clicking opens a compact, scrollable ElementEditor
with mass/radius/RGB/Magmom/U/J, a ColorButton and a dialog Save action. Cancel
writes nothing. Validation/conflict detection/atomic backups remain in ElementData
and ResourceStore; no new persistence format or dependency. Save refreshes tile
colors in place, preserving scroll, and restart applies cached structure defaults.
No top-level spreadsheet Save/dirty state remains. Tests exercise real dialogs,
color picker, unknowns, cancel, per-user reopen and external-write conflicts.

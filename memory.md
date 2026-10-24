# p4vasp maintenance memory

Last updated: 2026-10-24. This is a repository navigation and handoff document. Verify the current source and Git state before acting; historical test results are not current guarantees.

## Start here

- Checkout: `~/opt/p4vasp`. Run commands from its root. Older notes contain paths from other computers; use repository-relative paths.
- Read `AGENTS.md` and `doc/GTK3-migration.md`. For interface work, use `.agents/skills/p4vasp-gtk-ui/SKILL.md`.
- The project rules now define document roles, on-demand context recovery, the “开工” handoff, evidence attribution, per-device checks, delivery documentation and token/tool economy. Routine efficient actions remain autonomous; users may run costly or desktop-only checks with concise commands and feedback. See `AGENTS.md`.
- Detailed bilingual change records live in `update_history/`. Keep them as the source for historical details; update this memory when new fixes change where to investigate.
- Python GUI: PyGObject/GTK3 via `lib/p4vasp/gtk3/`. Existing `data/glade2/*.glade` files are loaded by `lib/p4vasp/gtk3/glade.py`. Native FLTK/OpenGL windows and the GLUT k-point viewer use separate backends.

## Update history

| Date | Completed work | Detailed record |
| --- | --- | --- |
| 2026-09-05 | GTK3 replication controls, applet switching/lifecycle, file opening/saving, Python 3 compatibility, and initial Build blank-area fix. | [September 5](update_history/update_2026_09_05.md) |
| 2026-09-07 | Structure background/cell outlines, element colors, Top/Side controls and sphere sizing; Measure startup, default Z-matrix mode, and missing angle/dihedral rows. | [September 7](update_history/update_2026_09_07.md) |
| 2026-09-23 | STM controls/layout, native INCAR generator and save/folder dialogs, GTK3 runtime and Cairo plotting migration. | [September 23](update_history/update_2026_09_23.md) |
| 2026-09-24 | Removed only the left-toolbar New shortcut; retained Edit → New and the New applet. Reference backups are under `deprecated/new-button/`; read `deprecated/README.md` first. | [September 24](update_history/update_2026_09_24.md) |
| 2026-09-26 | Shortened INCAR help text to identify POSCAR input and `data/incar/presets.json` as the MAGMOM/UJ settings source. | [September 26](update_history/update_2026_09_26.md) |
| 2026-10-06 | Copied atoms default to T T T when selective dynamics is enabled; original flags remain unchanged. Moved update notes into `update_history/`. | [October 6](update_history/update_2026_10_06.md) |
| 2026-10-12 | Fixed simultaneous Build table/text views; disabled automatic log-file writing; added Shift + left-drag additive atom selection. | [October 12](update_history/update_2026_10_12.md) |
| 2026-10-13 | Shift-drag now toggles each atom inside the box; idle Escape clears the entire selection. | [October 13](update_history/update_2026_10_13.md) |
| 2026-10-24 | Unified installer/launcher; headless PNG export, model/material controls, current-view GUI export, and File menu separator fix. | [October 24](update_history/update_2026_10_24.md) |

## Where to investigate

### Native structure-window box selection

- Shift + left drag toggles atoms whose screen-projected centers lie in a rectangle, including occluded atoms but excluding explicitly hidden atoms. Plain left drag rotates; Space toggles one atom; Esc cancels an active drag while preserving previous selections, or clears all selections when idle. No mode button was added.
- `src/VisStructureDrawer.cpp` / `src/include/p4vasp/VisStructureDrawer.h`: gesture state, cached per-window draw transforms, periodic-image projection, deduplication, and overlay. Resizing/focus loss cancels a gesture. Projection uses the current clipping range.
- Escape follow-up: `src/VisFLWindow.cpp` must consume `FL_KEYBOARD`, `FL_SHORTCUT`, and `FL_KEYUP` for Escape even when idle. FLTK's global unhandled-Escape fallback closes the window. Normalize shortcut Escape to a key press for active box cancellation. Tests must use `Fl::handle`, not only direct drawer/window handlers; the original test missed the fallback. Unexpected closing was reproduced and fixed; the reported whole-app hang was not independently reproduced.
- `src/VisWindow.cpp`: offers gestures to the structure drawer before navigation and draws the box after all scene drawers. `src/VisFLWindow.cpp`: returns consumed events to FLTK, including Escape.
- One existing `BE_SELECTED` or `BE_DESELECTED` event per changed box/clear tells `p4v.py` to reload the complete selection. Preserve this batching for large selections.
- Rebuild native code with `bash install/build-ubuntu-py3.sh`; restarting Python alone does not compile C++ changes. Native regression: `/usr/bin/python3 test/run_box_selection.py` (requires built objects, g++, fltk-config, Python development libraries and a display).
- Native synthetic gesture/rendering checks passed on Linux on October 12, including Side view, perspective/zoom, replicas, cancellation and legacy controls. October 13 extended the native checks to toggle-off, mixed regions, outside preservation, empty-selection notifications, idle Escape clearing and cancellation with existing selections. 57 unit tests and 31 applet startup checks passed after rebuilding. Full GTK suite still has 14 resource-property subtest failures. macOS/HiDPI and full manual selection-dependent applet workflows remain unverified.

### Build table/text overlap

- `lib/p4vasp/applet/BuilderApplet.py`: `initUI()` and `on_view_button_toggled_handler()`.
- Layout: `data/glade2/builder.glade`; toolbar entry: `data/glade2/frame.glade`.
- `p4v.py` performs parent `show_all()` calls when displaying/embedding applets. These could reveal the hidden table while text mode remained selected. Resizing alone was not established as the cause.
- Both `text_editor` and `table_editor` now have `set_no_show_all(True)`; explicit radio-button handlers show/hide the selected editor. Preserve both protections.
- Regression: `test/testGtk3.py`, `test_builder_views_stay_exclusive_after_resize_and_show_all`. It checks initial table mode, switching, resizing, mapped children, allocations, and the selective-dynamics control. POSCAR parsing is isolated in this layout test.

### Automatic p4vasp.log creation

- `p4v.py`: two logger setup sites in `Frame.createFrame()`.
- The original `FrameMessageDriver(xml,"p4vasp.log")` calls are commented out. Active calls use `FrameMessageDriver(xml)`, whose default is `DummyFile` from `lib/p4vasp/message.py`.
- Keep status/error messaging active. The user asked to comment out file logging, not remove the logging implementation. Restore the commented calls in place of the no-file calls only if logging is requested again. Existing log files are not deleted.

### INCAR defaults and generation

- UI/help/save workflow: `lib/p4vasp/applet/IncarApplet.py` (panel built in Python).
- Generation: `lib/p4vasp/incar_generator.py`; defaults: `data/incar/presets.json`; usage: `data/incar/README.md`; tests: `test/testIncarGenerator.py`.
- Current help: “Reads the open POSCAR; MAGMOM/UJ values use data/incar/presets.json.” Earlier notes describing zero moments are historical; inspect current presets and generator before changing defaults.

### Copying atoms

- `lib/p4vasp/applet/MoveApplet.py`: Copy behavior. Preserve original atom flags and translations; new atoms use T T T only when selective dynamics is enabled.

## Accepted selection workflow

- The user accepted the October 13 interaction: orient the model (often Side view), Shift + left drag to toggle every atom in a region, repeat to toggle back, and press Escape outside a drag to clear the complete selection. Keep Space toggling and ordinary rotation.
- Do not revert to additive-only box selection: that was the initial October 12 implementation and was explicitly superseded by the user's request.
- Published commits: `e571b1d` introduced box selection, `5764343` prevented Escape-triggered window closing, and `aaeb737` implemented toggle selection and idle-Escape clearing. The detailed bilingual summary is `update_history/update_2026_10_13.md`.

## Known unresolved issues

### Potential POSCAR overwrite issue — investigation deferred (2026-10-13)

- User reports that saving to another folder containing an existing POSCAR sometimes appears not to overwrite it. The filename field already shows POSCAR when they click OK; whether they entered the folder or only highlighted it is not established.
- User requested recording this as a potential issue only and will provide more information if it recurs. Do not treat it as a confirmed overwrite defect or implement a fix based on the current evidence.
- Temporary-file tests: the actual `Frame.save_system_selected` handler successfully overwrote an existing POSCAR. Navigating into a destination folder or selecting its existing file also worked. Programmatically selecting only a directory left a parent-folder save path in one test; this does not reproduce or prove the user's mouse workflow.
- Confirmed code behavior: `p4v.py` saves `INITIAL_STRUCTURE`; a write error still closes the dialog and refers to disabled `p4vasp.log`. An isolated dialog callback ran twice, but the actual save handler ran once. No cause for the user's intermittent symptom was established.
- Investigate `p4v.py` (`show_save_system_fileselection`, `save_system_selected`), `lib/p4vasp/gtk3/__init__.py` (`FileSelection`), and `data/glade2/frame.glade`. No save implementation or calculation files were changed during this investigation.
- If it recurs, collect the exact destination path, click sequence, any error/status message, and before/after file contents or modification time; establish whether the structure came from Build or the final/trajectory viewer. Possible future improvements are a full destination-path display, overwrite confirmation, and keeping the dialog open with the actual write error. These are proposals, not implemented fixes.


Observed during the October 12 checks; not fixed by the view/logging changes:

- Full GTK resource tests report Glade property-conversion failures (shadow types, window hints, gravity, text wrapping). Start with `lib/p4vasp/gtk3/glade.py` and the failing resource/property reported by `test_all_resources`.
- Live POSCAR parsing during text-buffer replacement can fail with `ParseException` errors (“exceptions must derive from BaseException” / “catching classes that do not inherit from BaseException”). Trace `BuilderApplet.on_textbuff_changed_handler`, `textview2struct`, `updateStructure`, and parsing in `lib/p4vasp/Structure.py` / `lib/p4vasp/util.py`. Inspect exception definitions and callback timing before choosing a fix.
- The optional separate GLUT k-point viewer previously failed with an OpenGL context error; it is excluded from default GTK applet smoke checks. See `doc/GTK3-migration.md`.

## Verification and launch

From the checkout root, with compiled cp4vasp and GTK3 dependencies available:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD/lib:$PWD/src" P4VASP_HOME="$PWD" /usr/bin/python3 test/test.py
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD/lib:$PWD/src" P4VASP_HOME="$PWD" /usr/bin/python3 test/testGtk3.py
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 test/run_gtk3_smoke.py
```

GTK checks need a working display. On October 12, the sandbox could not connect to the display; approved execution outside it worked. Respect approval controls rather than assuming display access. Inspect the rendered panel for layout fixes; syntax/XML checks alone are insufficient.

October 12 evidence: 57 bundled tests and 31 applet startup checks passed. The focused Build test passed at 800×600, 1400×900, and 900×650; rendered views were inspected at 1400×850. The full GTK suite was not clean due to the issues above. The later logging-only change received syntax, call-site, no-file logger, and whitespace checks; GUI/full tests were not rerun for that change.

Launch updated code after closing the existing application:

```bash
bash p4v.sh
```

The launcher selects `.venv-macos/bin/python3` when available, otherwise `/usr/bin/python3` or `python3`; `PYTHON` overrides this. It sets `P4VASP_HOME` and the library path and forwards application arguments.

## Publishing preferences and recorded state

- Follow the automatic update-note commit/push workflow in `AGENTS.md`. Stage only related files; preserve unrelated changes; never force-push.
- Authorized repository: `https://github.com/bigbrosci/p4vasp.git`, remote `origin`, branch `p4vasp-py3`. Check these before publishing.
- Recent published implementation commits: `c8cf168` (matte default), `f19070b` (current-view GUI export), and `22c087a` (File menu separator). These identify changes, not a permanent HEAD; check Git for later work.
- An earlier automatic approval review blocked publishing until the user explicitly approved the destination and payload. The user then approved uploading, and the push succeeded. Report actual push results; local commits alone are not published updates.

## Installation and startup — current state

- Install/build from the checkout root using `bash install.sh`; daily startup is `bash p4v.sh`. `p4v.py` is the Python application/CLI entry, not an installer. If using a `p4v` alias, point it at the current checkout's `p4v.sh`.
- `install.sh` detects `uname -s` and Linux os-release ID/ID_LIKE without sourcing shell code. Ubuntu/Debian uses `install/ubuntu-bootstrap.sh` with apt; other Linux uses its skip-apt path with preinstalled dependencies. Automatic dnf/pacman/zypper installation is not implemented.
- macOS uses `install/macos-bootstrap.sh`, Homebrew packages including GTK3/PyGObject/py3cairo, and `.venv-macos` with system site packages. Homebrew and Xcode Command Line Tools must already exist. The Ubuntu apt command in installation documentation is not a macOS command.
- Default installation rebuilds the native extension, which is required for C++ mouse-selection changes to work on another computer. `--dry-run` previews without changes; `--deps-only` prepares dependencies; `--skip-deps` skips package installation. See [install.md](install.md) for full options.
- Obsolete wrappers removed with user approval: `ubuntu-start.sh`, `macos-start.sh`, `install/install-ubuntu-dependencies.sh`. `run-p4vasp.sh` was renamed to `p4v.sh`; `ubuntu_install.sh` was renamed to `install.sh`. Keep the backend/build scripts under `install/`.
- Installer verification: nine mocked routing/argument tests, shell syntax and local Linux dry run passed on October 24. Actual package installation, macOS execution and cross-distribution builds were not performed for the entry-point changes.

## Image export — current state

### User-selected behavior

- PNG background is **transparent by default**. The user selected the middle material preview, so **matte is the default**; classic/glossy remain available. Default brightness is 1.0 and supersampling quality is 2.
- CLI export **replaces existing output by default**, publishing only after successful rendering. `--no-clobber` prevents replacement and `--force` remains compatible. GUI file selection confirms overwrite. Input structures are protected.
- GUI export must use the **latest user-adjusted camera at save time**: rotation, zoom, translation, projection and viewport aspect ratio. Do not reset to Top/Side, automatically recenter or fit the model. If the window crops atoms, the exported framing also crops them.
- Real-time OpenGL material upgrades were discussed as future work; only the independent image exporter and its GUI panel have been implemented.

### CLI and renderer

- `p4v.py` dispatches `-o`/`--output` and help before GTK imports to `lib/p4vasp/render_cli.py`. Without output options, normal GUI startup remains. `p4v.sh` forwards arguments.
- `p4v POSCAR -o model.png` renders POSCAR/CONTCAR using pycairo without GTK windows, a display server or ASE. CLI default size is 1000×1000 and model is `spheres`.
- Models: `spheres`, `ball-stick`, `stick`, `space-filling`. The last uses larger project radii; it is **not a calibrated van der Waals model**. Colors/radii/covalent radii come from `data/atomtypes.xml`; unknown elements are gray and do not acquire inferred bonds.
- Bonds use a covalent-radius distance heuristic (default multiplier 1.15), with adjustable radius (default 0.10 Å). Pair search is quadratic. CLI connects input atoms only; automatic periodic-image bonds/replicas are not implemented.
- CLI views: top looks from +z; side rotates −90° about Cartesian x (look from +y, x right, z up), currently matching front. The superseded +90° side change was upside down because screen y is inverted. Preserve the projected-z sign regression.
- Ordered `--rotate` angles use the right-hand rule and affect only the image. This differs from the historical GUI Rotate applet's sign convention. GUI camera export bypasses CLI view presets.
- `--quality 1|2|3|4` controls supersampling, capped at 64 million working pixels. Size limits and all options are in [doc/render-cli.md](doc/render-cli.md).

### GUI panel and camera bridge

- Control's camera button **Export PNG** is defined in `data/glade2/swincontrol.glade`; the combined Structure applet uses `structureapplet.glade`. Their `on_foto_button_clicked_handler` methods open `lib/p4vasp/export_image.py`. Original single TGA handlers remain as `save_legacy_screenshot`; animation export is unchanged.
- `snapshot()` copies the native camera through `getRotMatElement(row,column)`, zoom, viewport/projection and current Cartesian structure/frame. It preserves hidden atoms, repeated cells and cell visibility. Copy native state on the main thread; workers receive Python values only. No temporary POSCAR is written.
- `render_cli.py` accepts scene/camera for GUI export while retaining CLI presets/autofit. Projection follows `src/VisNavDrawer.cpp`: orthographic .04 world units/pixel; perspective near=10, far=50, eye translation −20. Do not transpose the native matrix or omit its translation/zoom.
- Panel: preview, model/material, width, quality, brightness, refresh and export chooser. Height follows window aspect ratio. Use **Refresh preview** after changing the model view or numeric settings; actual export always takes a fresh snapshot. Rendering runs in a worker, with errors shown in the still-usable panel.
- Cairo transparency may appear white against the GTK panel; the PNG retains alpha. GUI background is always transparent.

### Rendering limitations and future work

- Cairo spheres/bonds use gradients and approximate depth sorting. This is not a full 3D renderer or a pixel-identical OpenGL screenshot; no physical contact shadows/ambient occlusion were added.
- Sphere perspective uses center-depth radius scaling; depth clipping and complex intersections remain approximate.
- GUI exports atoms, inferred bonds and cell edges. It omits arrows, isosurfaces, selection markers and custom native colors/bond lists. Explicitly repeated GUI cells are included; this does not imply complete periodic-bond handling.
- Style comparison previews were local temporary files under `/tmp/p4v-material-preview/`; do not rely on them persisting. The user structure and previews were not published.

## File menu separator

- The blank row below Reload data was the unlabeled `GtkMenuItem` named `separator` in `data/glade2/frame.glade`. It was intended to be a divider, not a missing action.
- Changed it to `GtkSeparatorMenuItem` and added the constructor mapping in `lib/p4vasp/gtk3/glade.py`; unknown classes otherwise fall back to a Box. Both resource and adapter changes are needed.
- Actual popup rendering and neighboring labels were checked on X11, and 31 applet startup checks passed. Wayland popup checking encountered a display protocol error; no application backend default was changed. Use `GDK_BACKEND=x11` as a diagnostic fallback, not an assumed permanent requirement.

## Latest verification references (2026-10-24)

These are recorded results from implementation work, not checks rerun by a documentation-only refresh:

| Check | Recorded result | Command from checkout root |
| --- | --- | --- |
| Unified installer routing | 9 passed | `/usr/bin/python3 test/testUnifiedInstaller.py` |
| Headless image export | 13 passed | `PYTHONPATH=lib P4VASP_HOME="$PWD" /usr/bin/python3 test/testRenderCLI.py` |
| Native/GTK export integration | Passed; allocated panel rendering inspected | `/usr/bin/python3 test/testExportImage.py` |
| Bundled tests | 57 passed | `PYTHONPATH="$PWD/lib:$PWD/src" P4VASP_HOME="$PWD" /usr/bin/python3 test/test.py` |
| GTK applet startup | 31 passed | `/usr/bin/python3 test/run_gtk3_smoke.py` |
| Full GTK suite | 14 known Glade property failures | `PYTHONPATH="$PWD/lib:$PWD/src" P4VASP_HOME="$PWD" /usr/bin/python3 test/testGtk3.py` |

- GUI checks need a display and compiled native extension. `testExportImage.py` checks the toolbar entry, native matrix/zoom, hidden/replicated atoms, preview, fresh camera after rotation, perspective, PNG alpha and error recovery. The standalone integration test exits without testing native FLTK worker teardown.
- macOS installation/rendering, HiDPI behavior and full manual workflows on another computer remain unverified. See the unresolved issues above and [doc/GTK3-migration.md](doc/GTK3-migration.md).

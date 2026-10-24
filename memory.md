# p4vasp maintenance memory

Last updated: 2026-10-24. This is a repository navigation and handoff document. Verify the current source and Git state before acting; historical test results are not current guarantees.

## Start here

- Checkout: `~/opt/p4vasp`. Run commands from its root. Older notes contain paths from other computers; use repository-relative paths.
- Read `AGENTS.md` and `doc/GTK3-migration.md`. For interface work, use `.agents/skills/p4vasp-gtk-ui/SKILL.md`.
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
PYTHONPATH="$PWD/lib:$PWD/src" P4VASP_HOME="$PWD" /usr/bin/python3 p4v.py
```

## Publishing preferences and recorded state

- Follow the automatic update-note commit/push workflow in `AGENTS.md`. Stage only related files; preserve unrelated changes; never force-push.
- Authorized repository: `https://github.com/bigbrosci/p4vasp.git`, remote `origin`, branch `p4vasp-py3`. Check these before publishing.
- Confirmed pushed in this session: `076cba0` (Build view fix/test/note) and `793027c` (logging change, note, publishing guidance). Later work may supersede these; inspect Git rather than treating them as a permanent HEAD.
- An earlier automatic approval review blocked publishing until the user explicitly approved the destination and payload. The user then approved uploading, and the push succeeded. Report actual push results; local commits alone are not published updates.

## Unified installation entry (2026-10-24)

- Use `bash install.sh` from the checkout root on Linux or macOS. Detection uses `uname -s` and Linux os-release ID/ID_LIKE without sourcing shell code.
- Ubuntu/Debian derivatives route to `install/ubuntu-bootstrap.sh`; other Linux automatically uses its `--skip-apt` path (dependencies must be preinstalled); macOS routes to `install/macos-bootstrap.sh` (Homebrew and Xcode tools required). Backend scripts remain intact. Obsolete wrappers `ubuntu-start.sh`, `macos-start.sh`, and `install/install-ubuntu-dependencies.sh` were removed with user approval; use the unified entry and its `--deps-only` flag instead. Keep `p4v.sh` for daily startup.
- No automatic dnf/pacman/zypper package installation was added. See `install.md` for prerequisites and supported flags. `--dry-run` previews without changes; `--skip-deps` maps to the backend's skip flag. By default native extensions are rebuilt, so source updates take effect on other computers.
- Run `/usr/bin/python3 test/testUnifiedInstaller.py` for mocked routing/argument tests. Nine tests passed; shell syntax and the local Linux dry run passed. Actual package installation, macOS execution and cross-distribution builds were not performed for this entry-point change.

## Headless PNG export (2026-10-24)

- `p4v.py` dispatches `-o`/`--output` before GTK imports to `lib/p4vasp/render_cli.py`; `p4v.sh` forwards arguments as before. Without output options normal GUI startup remains. Help now describes image export.
- `p4v POSCAR -o top.png` exports via pycairo without a display or ASE. Supports Cartesian top/front/side views, ordered right-handed rotations, size, transparent background, cell visibility and radius scale. Existing PNGs are replaced by default; `--no-clobber` prevents replacement. `--force` remains compatible; input is protected.
- Independent orthographic sphere renderer, using `data/atomtypes.xml`; no bonds/labels/periodic replicas, approximate depth ordering. Not an OpenGL screenshot. CLI rotation signs differ from historical Rotate applet. See `doc/render-cli.md`.
- Focused checks: `PYTHONPATH=lib P4VASP_HOME="$PWD" /usr/bin/python3 test/testRenderCLI.py` — eight tests passed including no-display launcher use, blocked UI imports, scale factors, rotation order and overwrite protection. A generated PNG was visually inspected. macOS and GUI interaction were not exercised for this feature.

- PNG background is now transparent by default (including the render API); `--transparent` remains supported, and `--white-background` selects opaque white. Nine focused renderer tests passed after this default change.

## Export models and quality (2026-10-24)

- `render_cli.py` adds spheres (default), ball-stick, stick and space-filling (project radii, NOT calibrated vdW). Covalent-radius bond heuristic connects input atoms only; periodic bonds remain unsupported. Pair search is quadratic; occlusion remains approximate.
- Brightness, bond radius/factor and supersampling quality are configurable. Default 2x sampling, bounded to 64M working pixels. Transparent default retained; no GUI changes. See `doc/render-cli.md`.
- Eleven renderer tests passed, including bond detection, model differences and quality limits. Ball-stick PNG visually inspected.

- PNG overwrite default changed at user request: render API and CLI replace existing output atomically after successful rendering. Eleven renderer tests passed, including default replacement and explicit no-clobber protection.

- Side export uses −90° about Cartesian x (look from +y), with x horizontal and z upward. The initial +90° correction was upside down because screen y is inverted. Side currently matches front; top/front unchanged. Twelve tests passed, including side/top −90x image equivalence and projected z sign.

- Material trials: `--material classic|matte|glossy` changes sphere and bond shading, using matte as the default after the user selected the middle preview; classic/glossy remain available. Thirteen renderer tests passed; compared all three on the user Desktop POSCAR, side view, identical settings. Local previews: `/tmp/p4v-material-preview/` (temporary, not published). No actual 3D lighting/occlusion added.

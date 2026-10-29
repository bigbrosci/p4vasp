# p4vasp maintenance memory

Last updated: 2026-10-29. This is a repository navigation and handoff document. Verify the current source and Git state before acting; historical test results are not current guarantees.

## Windows 原生构建检查点（2026-10-29）

- Git 更新配置：已独立克隆 `origin/p4vasp-py3` 到 Windows `/home/lqlhz/p4vasp-checkout`，旧 `/home/lqlhz/p4vasp-windows` 和 Downloads 便携版保留。新增 `install/update-windows.sh` / `install/windows/update_build.py`，干净仓库 fast-forward 后从提交创建隔离构建副本，检查通过才生成版本目录/ZIP/SHA256；不覆盖旧版。7 个保护/验证器测试通过。修正 GUI 入口和 Windows 子进程退出码传递后，首次完整成功构建提交 `877fb28`，runtime/GUI、ZIP CRC/SHA256 及构建后干净 Git 状态均核验通过。成功目录为 `dist/windows-releases/p4vasp-20261029-003727-877fb283-9k24i9wj`（相对新 Windows checkout）。此前失败目录保留失败标记，未覆盖旧版。用法见 install.md 的 Update from Git。
- 最新任务已推进至便携目录：用户实际双击开发启动器成功（用户反馈，非助手复测）。新增 `install/package-windows.sh`、`install/windows/p4vasp.spec`/runtime hook/README；PyInstaller 6.22.3 生成 GUI/console 两个 EXE，共享 `_internal`。本机交付目录 `C:\Users\lqlhz\Downloads\p4vasp-portable-20261029`；整目录 ZIP 同级保存。仍未签名/制作安装器，须在干净 Windows 设备验收。
- 本次助手独立核验：移出 MSYS2 目录并清空开发环境变量后，冻结 EXE 导入所有注册 applet 模块、加载 40 个资源（本机无 property errors）、原生绘制/截图、PNG、POSCAR 标记、直接 CLI preset 重放通过；GUI 截图已检查，运行中 DLL 清单无 `C:\msys64` 来源。报告/截图和模块清单位于交付目录同级 `-checks/`，未发布用户数据。未在冻结版重跑 31 个 applet 的逐项启动或完整 GTK 回归。
- `lib/p4vasp/windows_check.py` 提供显式 `--check-runtime DIR` / `--check-gui DIR` 合成诊断，进程直接退出，不验证正常 teardown。Windows 重放改为引用本机 Python/冻结版 console EXE 的 PowerShell `.ps1`，修复默认保存脚本对 Bash/fchmod 的依赖；UTF-8 BOM 和单引号转义。7 个 recipe、14 个 CLI、57 个基础测试在 Linux 本次通过。Windows `.ps1` 最初被设备策略拒绝；随后用户报告设置 CurrentUser RemoteSigned，助手实际执行原有脚本成功，含中文/单引号/与号/百分号的路径和 `--size 160x120` 参数通过，输出 PNG 尺寸已核验。未改应用代码或由助手修改策略；直接 EXE preset 重放也通过。下一步用户双击便携 EXE，然后在无 Python/GTK/MSYS2 的 Windows 设备验证，最后再制作安装器。
- 最新进展：用户报告关闭了拦截功能后，助手重试原有 `.pyd` 导入成功，未重编译或修改安全策略。Windows 下 57 个基础测试和 31 个 GTK applet 启动检查通过；合成分子原生窗口实际绘制、相机快照、当前视角 PNG 导出、POSCAR 保存重读通过。主界面加载合成 POSCAR 成功，主界面与原生截图均已检查。
- 开发启动器位于独立目录 `C:\msys64\home\lqlhz\p4vasp-windows\p4v-windows.cmd`，`--help` 通过，随后用户报告双击无错误。该目录依赖现有 MSYS2，便携版进展见本节顶部；完整退出、真实手动编辑流程、其他设备及干净机仍未验证。原策略拦截记录保留在下文作为历史，已不阻碍本次导入。
- 当前任务：Windows 双击应用的可行性验证；用户要求节省调用。用户已安装 MSYS2 并报告 GTK3 最小窗口正常；不是 p4vasp GUI 验收。
- 助手实测：通过 WSL 调用 Windows 工具链；Python 3.14.9、GCC 16.2.0、SWIG 4.5.1、FLTK 1.4.5。独立源码快照在本机 `C:\msys64\home\lqlhz\p4vasp-windows`，非 Git checkout，不含后续提交的自动更新；Linux 构建产物未替换。
- 新入口 `install/build-windows-py3.sh` 复用共享构建脚本，Windows 使用 glu32/opengl32 并重新生成 SWIG wrapper；开发启动器 `p4v-windows.cmd` 尚未运行验证，不是独立 EXE。
- 实际编译/链接成功，得到 `_cp4vasp.cp314-mingw_x86_64_ucrt_gnu.pyd`。导入被 Windows Application Control 拦截；CodeIntegrity 3077/3033 事件明确指向该文件的签名级别/策略要求。日志在独立目录 `windows-build.log`；没有绕过或修改系统策略。
- 最初受阻时的下一步为管理员确认签名/批准方式；随后验证进展见本节顶部。对外分发时仍需验证签名和安全策略兼容性，不能把本机设置变化当作已解决发布问题。详见 [Windows 构建](install.md#windows-native-build--windows-原生构建试验) 和 [October 29](update_history/update_2026_10_29.md)。

## 接手检查点（2026-10-28）

- 当前任务：借鉴 PFAS 的交接文档实践；本次只改项目规则、记忆、安装指南和更新记录，不改应用实现。
- 已完成：补充简短检查点、完整依赖迁移和展示/科学输入边界；换机操作见 [install.md](install.md#changing-computers--换机接续)，详细证据见 [October 28](update_history/update_2026_10_28.md)。现有最近实现及其历史测试仍见下文 October 24 记录。
- 本次只读核对：当前分支 `p4vasp-py3`，origin 为约定 GitHub 地址，修改前工作树干净。读取了用户指定 PFAS 路径的交接/规则文档及状态、命令索引、记忆相关摘要；没有检查其模拟数据或执行其任务。
- 未验证：本次没有运行 p4vasp GUI、重编译或复测科学功能；历史 GTK 属性错误、潜在 POSCAR 保存报告等仍未解决，见 Known unresolved issues。另一设备环境仍需独立核验。
- 下一步：按用户具体目标继续；仅“开工”时做规则规定的只读接手。本文档任务的提交/推送结果以实际 Git 结果为准，不把计划写成已发布。

## Start here

- Checkout: `~/opt/p4vasp`. Run commands from its root. Older notes contain paths from other computers; use repository-relative paths.
- Read `AGENTS.md` and `doc/GTK3-migration.md`. For interface work, use `.agents/skills/p4vasp-gtk-ui/SKILL.md`.
- The project rules now define document roles, on-demand context recovery, the “开工” handoff, evidence attribution, per-device checks, delivery documentation and token/tool economy. Routine efficient actions remain autonomous; users may run costly or desktop-only checks with concise commands and feedback. See `AGENTS.md`.
- Detailed bilingual change records live in `update_history/`. Keep them as the source for historical details; update this memory when new fixes change where to investigate.
- Python GUI: PyGObject/GTK3 via `lib/p4vasp/gtk3/`. Existing `data/glade2/*.glade` files are loaded by `lib/p4vasp/gtk3/glade.py`. Native FLTK/OpenGL windows and the GLUT k-point viewer use separate backends.

## Update history

| Date | Completed work | Detailed record |
| --- | --- | --- |
| 2026-10-28 | Adopted concise handoff checkpoints, dependency-complete migration and presentation/input boundaries from the PFAS documentation review. Documentation only. | [October 28](update_history/update_2026_10_28.md) |
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
- User priority: interactive viewing/building must stay responsive; reserve detailed rendering for exported images. Keep the existing lightweight native window, render previews at reduced resolution/sampling, and run final image work off the GTK thread. Do not enable expensive effects on every mouse move.

### CLI and renderer

- `p4v.py` dispatches `-o`/`--output` and help before GTK imports to `lib/p4vasp/render_cli.py`. Without output options, normal GUI startup remains. `p4v.sh` forwards arguments.
- `p4v POSCAR -o model.png` uses the default export-only `studio` renderer (NumPy plus pycairo), without GTK windows, a display server or ASE. `--renderer fast` retains the earlier gradient implementation. CLI default size is 1000×1000 and model is `spheres`.
- Models: `spheres`, `ball-stick`, `stick`, `space-filling`. The last uses larger project radii; it is **not a calibrated van der Waals model**. Colors/radii/covalent radii come from `data/atomtypes.xml`; unknown elements are gray and do not acquire inferred bonds.
- Bonds use a covalent-radius distance heuristic (default multiplier 1.15), with adjustable radius (default 0.10 Å). Pair search is quadratic. CLI connects input atoms only; automatic periodic-image bonds/replicas are not implemented.
- CLI views: top looks from +z; side rotates −90° about Cartesian x (look from +y, x right, z up), currently matching front. The superseded +90° side change was upside down because screen y is inverted. Preserve the projected-z sign regression.
- Ordered `--rotate` angles use the right-hand rule and affect only the image. This differs from the historical GUI Rotate applet's sign convention. GUI camera export bypasses CLI view presets.
- `--quality 1|2|3|4` controls supersampling, capped at 64 million working pixels. Size limits and all options are in [doc/render-cli.md](doc/render-cli.md).

### GUI panel and camera bridge

- Control's camera button **Export PNG** is defined in `data/glade2/swincontrol.glade`; the combined Structure applet uses `structureapplet.glade`. Their `on_foto_button_clicked_handler` methods open `lib/p4vasp/export_image.py`. Original single TGA handlers remain as `save_legacy_screenshot`; animation export is unchanged.
- `snapshot()` copies the native camera through `getRotMatElement(row,column)`, zoom, viewport/projection and current Cartesian structure/frame. It preserves hidden atoms, repeated cells and cell visibility. Copy native state on the main thread; workers receive Python values only. No temporary POSCAR is written.
- `render_cli.py` accepts scene/camera for GUI export while retaining CLI presets/autofit. Projection follows `src/VisNavDrawer.cpp`: orthographic .04 world units/pixel; perspective near=10, far=50, eye translation −20. Do not transpose the native matrix or omit its translation/zoom.
- Panel: preview, model/material, width, quality, brightness, refresh and export chooser. Preview uses studio at 520-pixel width and 1x sampling; final output uses selected quality. Closing requests cancellation and cancelled work does not replace existing output. Height follows window aspect ratio. Use **Refresh preview** after changing the model view or numeric settings; actual export always takes a fresh snapshot. Rendering runs in a worker, with errors shown in the still-usable panel.
- Cairo transparency may appear white against the GTK panel; the PNG retains alpha. GUI background is always transparent.

### Rendering limitations and future work

- `lib/p4vasp/render_studio.py` analytically intersects rays with spheres and round-ended cylinders, choosing the nearest surface per sample (including perspective/clipping planes). It uses linear-space normal lighting, controlled specular highlights, sRGB encoding and supersampling. Spatial tiles bound scratch depth/normal memory; NumPy is loaded only when exporting.
- A local finite-distance contact-darkening heuristic adds depth; this is not physical ambient occlusion, cast shadows, PBR or path tracing. The `fast` fallback retains Cairo gradients, center-depth sorting and approximate perspective radii. PNG output uses Cairo for encoding/downsampling.
- GUI exports atoms, inferred bonds and cell edges. It omits arrows, isosurfaces, selection markers and custom native colors/bond lists. Explicitly repeated GUI cells are included; this does not imply complete periodic-bond handling.
- Style comparison previews were local temporary files under `/tmp/p4v-material-preview/`; do not rely on them persisting. The user structure and previews were not published.

## File menu separator

- The blank row below Reload data was the unlabeled `GtkMenuItem` named `separator` in `data/glade2/frame.glade`. It was intended to be a divider, not a missing action.
- Changed it to `GtkSeparatorMenuItem` and added the constructor mapping in `lib/p4vasp/gtk3/glade.py`; unknown classes otherwise fall back to a Box. Both resource and adapter changes are needed.
- Actual popup rendering and neighboring labels were checked on X11, and 31 applet startup checks passed. Wayland popup checking encountered a display protocol error; no application backend default was changed. Use `GDK_BACKEND=x11` as a diagnostic fallback, not an assumed permanent requirement.

## Latest verification references (2026-10-24)

These are recorded implementation checks, not guarantees for another device. The studio update reran the export, basic, GTK startup and full GTK checks; installer results remain from earlier work:

| Check | Recorded result | Command from checkout root |
| --- | --- | --- |
| Unified installer routing | 9 passed | `/usr/bin/python3 test/testUnifiedInstaller.py` |
| Headless image export | 14 passed (studio default/fast fallback included) | `PYTHONPATH=lib P4VASP_HOME="$PWD" /usr/bin/python3 test/testRenderCLI.py` |
| Studio surface tests | 6 passed | `PYTHONPATH=lib P4VASP_HOME="$PWD" /usr/bin/python3 test/testRenderStudio.py` |
| Replay presets | 6 passed; arbitrary-angle byte-identical replay and batch input | `PYTHONPATH=lib P4VASP_HOME="$PWD" /usr/bin/python3 test/testRenderRecipe.py` |
| Native initial centering | Passed; actual screenshot inspected | `/usr/bin/python3 test/testStructureCenter.py` |
| Native/GTK export integration | Passed; panel inspected; event-loop heartbeat and cancellation checked | `/usr/bin/python3 test/testExportImage.py` |
| Bundled tests | 57 passed | `PYTHONPATH="$PWD/lib:$PWD/src" P4VASP_HOME="$PWD" /usr/bin/python3 test/test.py` |
| GTK applet startup | 31 passed | `/usr/bin/python3 test/run_gtk3_smoke.py` |
| Full GTK suite | 14 known Glade property failures | `PYTHONPATH="$PWD/lib:$PWD/src" P4VASP_HOME="$PWD" /usr/bin/python3 test/testGtk3.py` |

- GUI checks need a display and compiled native extension. `testExportImage.py` checks the toolbar entry, native matrix/zoom, hidden/replicated atoms, preview, fresh camera after rotation, perspective, PNG alpha and error recovery. The standalone integration test exits without testing native FLTK worker teardown.
- macOS installation/rendering, HiDPI behavior and full manual workflows on another computer remain unverified. See the unresolved issues above and [doc/GTK3-migration.md](doc/GTK3-migration.md).

### Studio export evidence (2026-10-24)

- On this Linux checkout with `/usr/bin/python3` and X11, the export integration serviced 104 GTK timer ticks during a 900-pixel, 3x export. This demonstrates event-loop activity, not a measured native-window FPS guarantee.
- Visually inspected old/new side-view renders of the user's Desktop POSCAR, ball-stick water and the allocated export panel. One local 700×460, 3x example took about 0.17 s (fast) versus 1.27 s (studio); this is a single example, not a general benchmark. User inputs/previews were not published.
- No native renderer or installed GTK backend changed. Large exports still consume CPU; macOS/HiDPI and real interactive frame rates remain unverified.

## Reusable GUI camera commands (2026-10-24)

- Export dialog defaults to saving a replay bundle after successful PNG output: `<image>.POSCAR` (base Cartesian geometry), `<image>.view.json` (versioned data-only camera/render/display state), `command_for_<image-stem>.sh`. Copy command shows the last successful saved command. Unchecking the recipe option writes only the PNG. Existing companions get a new `.replay-N` prefix; they are not overwritten. Geometry snapshots omit calculation settings/selective-dynamics flags.
- New `lib/p4vasp/render_recipe.py`: validation, DEFAULTS, repeat/hidden replay, snapshot serialization, shell-safe command generation and companion publication. `render_cli.py --preset FILE` applies camera/settings and rebuilds visible replicas from the supplied input. Explicit CLI image options override preset settings; --view/--rotate conflict with --preset. Keep DEFAULTS consistent with render() defaults.
- GUI snapshot copies recipe data only for an actual export with the checkbox enabled; previews avoid that extra copy. Recipes capture save-time state, including edited/current trajectory geometry. CLI replay needs no GTK/display. Other structures retain the same camera, not auto-alignment/fitting; axes/origin/scale should match and hidden indices require matching atom order.
- GUI controls compacted with a scrollable settings area and fixed export actions; copy command remains accessible at 620×600. User still edits/rotates in the lightweight native window.
- Verification: 5 recipe tests (byte-identical headless replay, batch input, overrides, validation/conflicts and collision protection), 14 CLI tests, GUI integration including real command execution, clipboard and recipe opt-out, 57 bundled tests and 31 applet startup checks passed. Allocated GTK panel inspected on X11. Full GTK retains 14 known Glade failures; macOS not tested.

- Replay command files now use `command_for_<image-stem>.sh` beside the image (e.g. model.png → command_for_model.sh), with Bash header, executable permission and forwarded CLI options. Existing files remain protected by replay suffixes. Six recipe tests passed, including running the saved script headlessly with option overrides.

## Center and fit newly opened structure windows (2026-10-24)

- User request: Show should initially center the atom model in the structure window without manual pan/window adjustment. `StructureWindow.fitToStructure()` fits the visible atom surfaces (radius included) and actual native replicas with 15% margin, ignoring empty cell/vacuum bounds. Only camera changes; source coordinates are preserved.
- `_needs_initial_fit` applies on first nonempty structure, window recreation and a new system in `StructureWindowApplet.setSystem`. Ordinary same-system frame/structure refresh preserves the camera. Recreated windows retain radius factor and repetition settings. Home in both structure control applets restores default rotation then fits; the shared STM control retains its original Home behavior.
- `VisNavDrawer.centerOn` and private pivot state keep centering stable through zoom/right-drag zoom and standard views. `replaceRotation` preserves the pivot's screen position; Home resets it. Updated native header/source and tracked SWIG wrapper/Python proxies in src and lib. Native rebuild required (`bash install.sh --build-only`); this Linux checkout was rebuilt successfully.
- `test/testStructureCenter.py` exercises offset/negative coordinates, slab vacuum, 400×300/800×600/900×300 viewports, replicas, radius preservation, view/zoom pivots, new systems, frame preservation, Home/reopening and an actual OpenGL screenshot. Center checked numerically and visually; no geometry centering/wrapping is applied.
- Passed that focused check, native box-selection regression, GUI export/replay integration, 57 bundled tests and 31 applet startup checks on Linux/X11. Full GTK retains 14 known Glade conversion failures. macOS and HiDPI not verified. Existing saved camera presets still replay their stored framing; export does not re-fit.

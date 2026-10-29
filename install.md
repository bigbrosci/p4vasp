p4vasp
==========================

Copyright notes:

The original p4vasp software is distributed under the GNU General Public License version 2 (GPLv2).

Original project:

    p4vasp — A graphical user interface for VASP

    Website: http://www.p4vasp.at

Python 3 modernization and maintenance:

    This fork has been updated and maintained for Python 3 compatibility by

    Bigbrosci      (GitHub username)

    Whitehare2023  (GitHub username)

The modifications include:

    - Migration from Python 2 to Python 3

    - Dependency updates

    - Compatibility fixes for modern systems

    - Maintenance and bug fixes

All modifications remain distributed under the GNU General Public License v2 (GPLv2).

Source-code distributions
==========================

Unified installation / 统一安装入口
--------------------------

From the checkout root, run the same command on Ubuntu, other Linux distributions,
and macOS (including WSL with a Linux distribution):

```bash
bash install.sh
```

统一入口 `install.sh` 会自动判断系统，无需手动选择 Ubuntu、其他 Linux 或 macOS 脚本。

| Detected system / 检测到的系统 | Installation flow / 安装流程 |
| --- | --- |
| Ubuntu, Debian and compatible derivatives | Install dependencies with apt, rebuild the native extension, then launch when a display is available. / 使用 apt 安装依赖，重新编译，有图形显示时启动。 |
| Other Linux distributions | Skip apt automatically, build using preinstalled dependencies, then launch when a display is available. / 自动跳过 apt，使用已安装的依赖编译并启动。 |
| macOS | Use the existing Homebrew installation, prepare `.venv-macos`, rebuild, and launch. / 使用原有 Homebrew 流程、准备 Python 环境、重新编译并启动。 |

**Other Linux / 其他 Linux：** This uses the preinstalled-dependency build workflow; it does not add automatic dnf/pacman/zypper
package installation. Install your distribution's equivalents of a C++ compiler,
Python 3 and development headers/config tool, SWIG, FLTK 1.3 development files,
OpenGL/GLU and X11 development files, GTK3/PyGObject/Cairo (including the GI Cairo
bridge), NumPy, and PyOpenGL first. The build reports missing requirements.
非 Debian 系 Linux 仍需先通过自身包管理器准备这些依赖；统一入口不会在其上误用 apt。

**macOS：** Install Xcode Command Line Tools (`xcode-select --install`) and
Homebrew first. The existing bootstrap reports missing prerequisites; it does
not automatically install Homebrew itself.

Useful options / 常用选项：

```bash
bash install.sh --help
bash install.sh --dry-run          # Show detection/command only; no changes
bash install.sh --no-launch        # Install and rebuild without opening GUI
bash install.sh --build-only       # Rebuild after git pull; no GUI launch
bash install.sh --skip-deps        # Use existing system packages
bash install.sh --deps-only        # Dependencies only: Ubuntu/Debian or macOS
bash install.sh -- '/path with spaces/POSCAR'
```

`--skip-apt` and `--skip-brew` are aliases for `--skip-deps` at the unified entry.
macOS still prepares its Python environment and OpenGL bindings with
`--skip-deps` / `--build-only`, as in the existing bootstrap.
`--deps-only` is rejected on unsupported Linux package-install routes, rather
than reporting a successful dependency installation.

The default flow **rebuilds the native extension**. After updating source on
another computer, rebuilding is required for features such as Shift-drag atom
selection; `git pull` alone does not update a locally compiled `_cp4vasp` library.
Avoid `--skip-build` when upgrading native features.

Linux installation can finish without a graphical display; launch later with
`bash p4v.sh`. WSL GUI use needs a working WSLg/X11 display connection.

The obsolete platform-specific entry wrappers have been removed. Use
`install.sh` for installation and `p4v.sh` for daily startup.
For dependency-only installation, use `bash install.sh --deps-only`.
The scripts under `install/` remain internal installation/build backends. Advanced testing can
set `P4VASP_OS_RELEASE` to an alternate os-release file; normal installation
reads `/etc/os-release` and identifies the kernel with `uname -s`.

## Windows native build / Windows 原生构建试验

已提供实验性独立目录打包入口，并在本机完成移出 MSYS2 目录后的运行检查；干净机验证尚未完成。
原生源码构建请使用独立的 Windows 源码副本，
不要在 Linux/macOS 工作副本上编译：构建会生成平台专用对象、SWIG wrapper 和 Python proxy。

在 MSYS2 **UCRT64** 终端中，完成 `pacman -Syu` 后安装：

```bash
pacman -S --needed git make \
  mingw-w64-ucrt-x86_64-gcc mingw-w64-ucrt-x86_64-swig \
  mingw-w64-ucrt-x86_64-python mingw-w64-ucrt-x86_64-python-gobject \
  mingw-w64-ucrt-x86_64-gtk3 mingw-w64-ucrt-x86_64-python-cairo \
  mingw-w64-ucrt-x86_64-python-numpy mingw-w64-ucrt-x86_64-python-pyopengl \
  mingw-w64-ucrt-x86_64-fltk
# 在独立 Windows 源码根目录执行：
bash install/build-windows-py3.sh
```

构建会检查 GTK/Cairo 和 `_cp4vasp` 导入。通过后可尝试双击 `p4v-windows.cmd`；
它依赖本机 MSYS2（默认 `C:\msys64`，可用 `P4VASP_MSYS2` 指定其他位置），不是便携安装包。
失败时保留终端错误。启动器的 `--help` 调用已验证，双击 GUI 交互尚待验收。

2026-10-29 本机 Windows 编译和链接成功，但导入被 Application Control 策略拦截。
CodeIntegrity 日志事件 3077/3033 指向新编译的 `.pyd`。需由有权限的管理员确认签名或批准要求，
再继续导入和 GUI 测试；不要把这个结果当作 DLL 缺失或 p4vasp 已在 Windows 运行成功。
本次没有修改安全策略。详细结果见 [更新记录](update_history/update_2026_10_29.md)。

同日后续：用户报告关闭拦截功能后，原有扩展导入成功，57 个基础测试、31 个 GTK 面板启动检查通过。
主界面加载合成 POSCAR、原生分子绘制、POSCAR 保存重读和当前视角 PNG 导出通过，截图已检查。
这些是本机开发环境验证，不代表独立 EXE、签名或其他电脑验证通过；助手没有修改系统安全设置。
本机试用入口为 `C:\msys64\home\lqlhz\p4vasp-windows\p4v-windows.cmd`，路径仅属此设备。

### Portable folder / 独立目录版

在原生扩展已构建通过的 Windows 源码根目录，用 UCRT64 执行：

```bash
pacman -S --needed mingw-w64-ucrt-x86_64-pyinstaller
bash install/package-windows.sh
```

输出为 `dist/windows/p4vasp/`。保留完整目录，双击 `p4vasp.exe`；
`p4vasp-console.exe` 用于报错和命令行导出。不能只复制 EXE 或删除 `_internal/`。
构建包含 Python、GTK/Cairo、原生扩展、NumPy、项目资源和依赖许可证；不包含用户计算文件。
窗口版仅为旧回调提供空输出流，不恢复自动日志文件。

从 Windows PowerShell 可进行合成检查，输出目录必须是新目录或空目录：

```powershell
.\p4vasp-console.exe --check-runtime C:\实际位置\new-runtime-check
.\p4vasp-console.exe --check-gui C:\实际位置\new-gui-check
```

诊断会打开测试窗口、保存截图/合成结构/JSON 报告并退出进程，不验证完整正常退出。
2026-10-29 已在本机“下载”目录中清空 MSYS2/Python 环境变量后验证：40 个 Glade 资源加载、
全部注册 applet 模块导入、原生绘制、POSCAR 保存重读、PNG 与 preset 导出、实际 GUI 启动。
运行中的 GUI 模块清单未发现来自 `C:\msys64` 的 DLL。这不是另一台无开发环境电脑的独立验证。

本机便携版：`C:\Users\lqlhz\Downloads\p4vasp-portable-20261029\p4vasp.exe`，
同级 ZIP 可用于整目录迁移。尚未代码签名、制作安装器或通过干净 Windows 设备验收；
GLUT k 点查看器和外部数据库未验证。Windows 图片重放生成 `.ps1`，受 PowerShell 执行策略约束；
本机最初禁止脚本执行，用户随后自行设置 CurrentUser RemoteSigned，原有重放脚本实测通过。
其他设备需独立检查策略；也可直接使用控制台 EXE 的 `--preset` 功能。

### Update from Git / 从 Git 一键更新 Windows 版

先将 Linux 上需要同步的修改提交并推送到 `origin/p4vasp-py3`。Windows 更新只能取得已发布的提交，
不会读取 Linux 未提交的文件。本机已建立新的 Git checkout：`C:\msys64\home\lqlhz\p4vasp-checkout`。
原 `p4vasp-windows` 仍为历史源码副本，保留现有可用程序；不要在那个目录运行 `git pull`。

打开 **MSYS2 UCRT64**，执行：

```bash
cd /home/lqlhz/p4vasp-checkout
bash install/update-windows.sh
```

一键入口核对 origin、分支及干净工作树，使用 `git pull --ff-only`；有本地修改、远程/分支不符、
合并冲突或网络错误时停止，不重置或自动暂存文件。随后从提交创建独立源码副本，重新编译和打包，
清空开发环境变量后运行合成 runtime/GUI 检查（会短暂打开测试窗口）。成功后在
`dist/windows-releases/` 保存独立版本目录、ZIP 和 SHA-256，版本目录含 `SOURCE-COMMIT.txt`。
不覆盖旧版，也不自动替换“下载”文件夹里的便携版。

```bash
bash install/update-windows.sh --check          # 只读核对，不拉取、不编译
bash install/update-windows.sh --build-current  # 不拉取，构建当前干净提交
```

构建日志和源码副本保存在 `build/windows-update/`；失败时保留证据，未通过的目录会标记失败，
不会作为成功 ZIP 交付。诊断不代表完整人工工作流、正常退出、签名或干净设备验收。
Python/C++/资源变化统一重编译打包；本机依赖更新不包含在该脚本内，缺依赖时按前文安装。
旧构建与 ZIP 会占用磁盘，确认不再需要后再自行清理。

2026-10-29 已在上述新 checkout 实跑完整更新流程成功：构建提交 `877fb28`，
冻结 runtime/GUI 检查、ZIP CRC/SHA-256 和构建后干净工作树核对通过。
本机成功版本为 `dist/windows-releases/p4vasp-20261029-003727-877fb283-9k24i9wj/`；
该结果不替代另一台干净 Windows 电脑的验收。

## Changing computers / 换机接续

从新设备的实际 checkout 根目录开始，先读 [AGENTS.md](AGENTS.md) 和
[memory.md](memory.md) 的接手检查点，再按任务查看历史证据。不要直接照搬旧电脑的绝对路径。

1. 核对 `pwd`、`git status --short`、`git branch --show-current` 和 `git remote get-url origin`。
   本项目发布目标为 `p4vasp-py3` / `https://github.com/bigbrosci/p4vasp.git`。
   有本地修改时先保留并核对差异，不自动覆盖或重置。
2. 获取完整源码与资源；不能只复制一个 applet 或 Python 脚本。保留 `lib/`、`src/`、
   `data/`、`install/` 和项目入口文件。不要复用另一台机器的 `.venv-macos` 或已编译原生扩展；
   依照本页安装流程重建。云盘可见文件名不等于内容已离线可读。
3. 新设备首次安装用 `bash install.sh --no-launch`；依赖已经准备好、仅更新源码时可用
   `bash install.sh --build-only`。以下为待执行建议，不代表新设备已安装或编译成功。
4. 安装完成后用 `bash p4v.sh` 检查启动，并按任务运行
   [GTK3 与原生选择检查](doc/GTK3-migration.md#verification)。无显示环境时可先按
   [导出指南](doc/render-cli.md) 检查无窗口 PNG；导出成功不能代替 GUI 检查。
5. 在 memory 接手检查点记录日期、平台/设备（未知写未标识）、实际检查范围、失败或未验证项。
   Linux 通过不能代替 macOS、HiDPI 或另一台电脑的验证。

迁移用户计算数据时应独立保存所需 POSCAR/CONTCAR、INCAR、KPOINTS、POTCAR 等实际输入，
不随代码提交这些文件或凭据。图片重放需要配套的 `.POSCAR`、`.view.json` 和
`command_for_*.sh`，其中结构快照不保存选择性动力学标记或完整计算设置，不能替代计算输入。
详见 [重放说明](doc/render-cli.md)。
保存的命令脚本含生成设备的绝对路径，换机后应核对并改用本机入口，例如在新 checkout 根目录运行
`bash p4v.sh /实际位置/model.png.POSCAR -o /实际位置/replayed.png --preset /实际位置/model.png.view.json`。
以上路径为待替换示例，不能直接当作本机已有文件。

Rebuild the environment and native extension on the destination machine. Keep complete source/resource
dependencies and any replay companions together; saved images and replay geometry do not replace
calculation inputs. Record destination-machine checks separately from historical results.

Starting with the magic `p4v` command
--------------------------

Add the following alias to your shell configuration file.

-----------

**macOS (zsh)**

Edit:

    ~/.zshrc

and add:

    alias p4v='xxx/p4vasp/p4v.sh'

Then reload the shell:

    source ~/.zshrc

---------------------

**Ubuntu / Linux (bash)**

Edit:

    ~/.bashrc

and add:

    alias p4v='xxx/p4vasp/p4v.sh'

Then reload the shell:

    source ~/.bashrc


GTK3 GUI runtime
--------------------------

The GUI now uses GTK3/PyGObject and Cairo. On Ubuntu/Debian, existing installations
may need the Cairo bridge package:

```bash
sudo apt-get install python3-gi python3-gi-cairo python3-cairo gir1.2-gtk-3.0
```

See [GTK3 migration and verification](doc/GTK3-migration.md) for details and GUI tests.

## 无窗口导出 PNG / Headless PNG export

```bash
bash p4v.sh POSCAR -o top.png
bash p4v.sh POSCAR -o rotated.png --rotate=30x,-20y,10z --size 1200x900
```

配置 `p4v` 别名后也可使用 `p4v POSCAR -o top.png`。无需启动 GUI 或显示服务器；依赖安装流程已包含的 NumPy 和 pycairo。更多视角、透明背景和覆盖选项见 [图片导出指南](doc/render-cli.md)。
With the alias configured, use `p4v POSCAR -o top.png`. No GUI or display server is needed. See the [rendering guide](doc/render-cli.md) for options and rendering limitations.

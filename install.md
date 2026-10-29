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

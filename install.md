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

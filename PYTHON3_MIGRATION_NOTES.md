# p4vasp Python 3 Migration Notes

## 目标

这个分支的目标是把原始 p4vasp 从 Python 2 / PyGTK / GTK2 迁到 Python 3，同时尽量保持软件原有功能不变：

- 读取 VASP 输入文件，例如 POSCAR，提供模型查看和构建界面。
- 读取 VASP 输出文件，例如 vasprun.xml，保留结果浏览、DOS/bands、convergence、structure view 等分析入口。
- 保留原来的 Glade2 界面文件和菜单/applet 组织方式，减少业务逻辑重写风险。

## 迁移思路

1. Python 代码先做语法和标准库兼容，把 print、异常语法、迭代器、字符串/bytes、已迁移模块等问题处理掉。
2. 保留原来的 `gtk` 调用方式，在 `lib/gtk` 下做 PyGTK 风格 facade，底层使用 PyGObject/GTK3。
3. 保留 `data/glade2/*.glade`，用 `lib/gtk/glade.py` 做最小 libglade 兼容加载器，避免重画所有老界面。
4. 原生可视化扩展 `_cp4vasp` 继续用 C++/SWIG 构建，只修 Python 3、现代编译器、OpenGL/FLTK 链接问题。
5. Windows WSL、Ubuntu 和 macOS 通过启动脚本自动安装/构建依赖，用户 clone 后用一条命令启动。

## 当前安装入口

Windows WSL (Ubuntu):

```bash
git clone -b python3 https://github.com/Whitehare2023/p4vasp.git
cd p4vasp
bash ubuntu-start.sh
```

Ubuntu:

```bash
git clone -b python3 https://github.com/Whitehare2023/p4vasp.git
cd p4vasp
bash ubuntu-start.sh
```

macOS:

```bash
git clone -b python3 https://github.com/Whitehare2023/p4vasp.git
cd p4vasp
bash macos-start.sh
```

已经安装过系统依赖时，可以用 `--skip-apt` 或 `--skip-brew` 跳过系统包安装，只重建并启动：

```bash
bash ubuntu-start.sh --skip-apt
bash macos-start.sh --skip-brew
```

WSL 如果没有图形界面，脚本会完成安装和编译后退出；之后在有 WSLg/X11 的环境里运行：

```bash
bash run-p4vasp.sh
```

## 注意点

- 布局问题大多来自老 Glade2 的 `x_options` / `y_options`。GTK3 兼容层必须按这些 attach options 还原 GTK2 表格行为，否则 applet 会变宽或高度不展开。
- Builder applet 的 atom table 需要作为可扩展区域打包，并放进 scrolled window，否则打开 POSCAR 后只能看到很少几行。
- Structure 3D 窗口由 FLTK 管理，标题栏关闭按钮要在回调里立即 hide，同时继续发送原有 close event 给 Python 层清理状态。
- 修改 `src/*.cpp` 或 SWIG 接口后，客户需要重新跑启动脚本，让 `_cp4vasp` 重新编译。

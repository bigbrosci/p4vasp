# p4vasp 常用命令 / Usage commands

先安装并在当前终端加载命令：

```bash
bash install.sh
source ~/.bashrc
```

在计算文件所在目录运行，文件名可替换成实际路径。

```bash
p4v                 # 打开主界面
p4v POSCAR          # 查看 VASP 结构
p4v test.xyz        # 通过 ASE 读取 XYZ 结构
p4v OUTCAR          # 打开频率计算 OUTCAR，再点击 Vibrations
```

XYZ 导入和频率分析需要 ASE。普通优化 OUTCAR 不包含完整振动模式。

从 POSCAR 导出俯视图和侧视图，无需打开图形窗口：

```bash
p4v POSCAR -o top.png --view top
p4v POSCAR -o side.png --view side
```

图片保存在当前目录；已有同名图片会被覆盖。更多参数见 [图片导出指南](doc/render-cli.md)。

macOS 的 zsh 终端也可手动执行 `source ~/.bashrc`；新开的 zsh 终端需要重新加载。已有 Bash 专用配置的 `.bashrc` 应在 Bash 终端加载。

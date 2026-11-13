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
p4v XDATCAR         # 打开轨迹，点击 Control 播放或逐帧查看
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

## XDATCAR轨迹播放

运行`p4v XDATCAR`后点击Control，Structure step默认选择`XDATCAR trajectory`。播放按Speed设定的帧步长前进，每200毫秒更新一次，到末帧自动停止；再次播放可从头开始。首帧、末帧和前后单步按钮均可用，序号从0开始；停止后保留当前帧。

下拉菜单的Initial positions和Final positions分别显示XDATCAR首帧和末帧；即使停留在这两个单帧选项，点击播放或步进也会自动回到完整轨迹。File/Open选择XDATCAR同样适用，不需要ASE。文件必须保留在原位置以便按索引读取，播放中不要替换或追加文件；新增帧请重新打开。

读取支持Direct／Cartesian坐标、VASP4／5头及重复完整头的变晶胞轨迹；不完整帧会报错，不会伪造缺失原子。轨迹只反映文件实际保存的帧，不推断是优化还是分子动力学，也不插值未保存过程或补充能量／力。此改动需新源码，旧Windows EXE须另行打包。

# p4vasp 常用命令 / Usage commands

先安装并在当前终端加载命令：

```bash
bash install.sh
source ~/.zshrc    # macOS 默认 zsh；Bash 使用 source ~/.bashrc
```

在计算文件所在目录运行，文件名可替换成实际路径。

```bash
p4v                 # 打开主界面
p4v POSCAR          # 查看 VASP 结构
p4v XDATCAR         # 打开轨迹，点击 Control 播放或逐帧查看
p4v test.xyz        # 通过 ASE 读取 XYZ 结构
p4v OUTCAR          # 打开频率计算 OUTCAR，再点击 Vibrations
p4v OUTCAR_freq     # 支持 OUTCAR_* 文件名（不区分大小写）
p4v OUTCAR-freq     # 同样支持 OUTCAR-*，如 OUTCAR-frequency
```

XYZ 导入和频率分析需要 ASE。普通优化 OUTCAR 不包含完整振动模式。

从 POSCAR 导出俯视图和侧视图，无需打开图形窗口：

```bash
p4v POSCAR -o top.png --view top
p4v POSCAR -o side.png --view side
```

图片保存在当前目录；已有同名图片会被覆盖。更多参数见 [图片导出指南](doc/render-cli.md)。

请以安装末尾打印的 source 路径为准：zsh 使用 `.zshrc`（尊重 `ZDOTDIR`），Bash 使用 `.bashrc`。新开的对应 shell 终端自动加载别名。

## XDATCAR轨迹播放

运行`p4v XDATCAR`后点击Control，Structure step默认选择`XDATCAR trajectory`。播放按Speed设定的帧步长前进，每200毫秒更新一次，到末帧自动停止；再次播放可从头开始。首帧、末帧和前后单步按钮均可用，序号从0开始；停止后保留当前帧。

下拉菜单的Initial positions和Final positions分别显示XDATCAR首帧和末帧；即使停留在这两个单帧选项，点击播放或步进也会自动回到完整轨迹。File/Open选择XDATCAR同样适用，不需要ASE。文件必须保留在原位置以便按索引读取，播放中不要替换或追加文件；新增帧请重新打开。

读取支持Direct／Cartesian坐标、VASP4／5头及重复完整头的变晶胞轨迹；不完整帧会报错，不会伪造缺失原子。轨迹只反映文件实际保存的帧，不推断是优化还是分子动力学，也不插值未保存过程或补充能量／力。此改动需新源码，旧Windows EXE须另行打包。

## 无界面DOS分析

需先安装统一科学环境：`bash install/install-science.sh`。下面命令不打开GUI，直接输出CSV：

```bash
p4v DOSCAR 1-3 dxy,dyz both -6 0 result.csv
p4v vasprun.xml all d both full full all-d.csv
p4v --dos-analysis --help
```

参数顺序为：文件、原子编号/范围、轨道、自旋、Emin、Emax、输出CSV。
多个原子或轨道用逗号，各轨道总壳层与自身分量不能混用；能量相对EF=0，已有CSV不覆盖。
单参数`p4v DOSCAR`仍打开界面。Export scripts生成Python快照脚本和调用该入口的Bash脚本，详见[分析与脚本说明](doc/dos-analysis-zh.md)。


## 无界面 Bulk 生成与重建

```bash
p4v bulk Cu fcc cubic --a 3.615 -o POSCAR
p4v bulk Ti hcp primitive --a 2.95 --c 4.68 --repeat 2 2 1 -o POSCAR.Ti
p4v bulk --help
```

Bulk 的 **Save POSCAR** 同时保存 `rebuild_bulk.py` 和 `rebuild_bulk.sh`。可运行
`python rebuild_bulk.py -o POSCAR.python` 或 `bash rebuild_bulk.sh POSCAR.command`。
已有输出文件不会被覆盖。用法与依赖见 [Bulk 保存与重建](doc/ase-bulk-zh.md#4-保存与重建-poscar)。

## 重建已保存的Surface

Surface保存时自动生成两个脚本和surface.json；以下命令不打开GUI，输出目录必须不存在：

```bash
python rebuild_surface.py --output rebuilt_python
bash rebuild_surface.sh rebuilt_bash
p4v --surface-replay surface.json rebuilt_cli
```

Python需要ASE，可脱离p4vasp及原始体相文件；Bash/CLI需要p4vasp的ASE环境。
记录最终切面、超胞、真空、固定层和摆放参数，不包含完整VASP计算输入。
详见[Surface保存与重建](doc/ase-surface-zh.md#4-文件与依赖)。

DOS分析还支持s/p/d/f：`p4v DOSCAR all p both -6 0 p.csv`。
多个壳层可用`s,p`；f分量负编号写`f_3,f_2,f_1`，正编号写`f0,f1,f2,f3`。
源文件缺少所选投影时报错，详见[轨道分析说明](doc/dos-analysis-zh.md#spdf投影分析)。

# DOS 与 pymatgen 分析

原有 DOS+bands 的绘图、自旋上下显示、缩放、Graph 导出以及 Local DOS+bands control 保留。分析是新增功能，不改变原曲线或计算输入。

## 安装与打开

```bash
bash install/install-science.sh
p4v DOSCAR
# 或
p4v vasprun.xml
```

ASE、RDKit、pymatgen共用科学环境；GUI仍用原解释器。也支持File/Open；缺少pymatgen时，原绘图继续可用，分析区域提供可复制安装命令。此功能目前在Linux/WSL源码版验证，尚未更新Windows EXE或验收macOS。

## 操作

1. 点击 **DOS+bands**，左侧显示原DOS绘图与工具栏，右侧直接显示 **d-band analysis (pymatgen-实际版本)**，例如`d-band analysis (pymatgen-2026-10-24)`，无需展开。拖动中间分隔线可调整两侧宽度；小窗口可在右侧区域滚动。最大化、恢复窗口及切换右侧参数后，左图按当前实际尺寸重绘并保留缩放范围。
2. 选择 **All atoms**、**Elements**（如`Fe, Ni`）或 **Atom numbers**（从1开始，如`1-4, 8`）。元素与原子编号二选一。**Use selected atoms**复用结构选择；**Use last DOS line**复用Local DOS控制中最后一条投影线的原子和自旋。后者不使用曲线的倍率或正负号，默认分析全部d，若该线只选了一个d轨道则复用它。
3. **Orbital**单独一排按钮：`d`、`dxy`、`dyz`、`dz2`、`dxz`、`dx2`（dx²−y²）。`d`表示全部d，与单个轨道互斥；单个轨道可多选，先求和再分析，重复轨道不重复计数。取消最后一个选择会回到d。下一排为 **Spin: Both / Up / Down** 互斥按钮。无自旋计算只启用Both，Up/Down灰显；切回自旋数据恢复。Both对可用通道求和，不平均；无自旋时不额外乘2。
4. 在同一行的 **Energy Range (eV)**、**Emin**、**Emax** 紧凑输入框中输入相对费米能级的上下限。留空使用原文件完整能量网格。分析范围与绘图缩放独立，超出数据范围会报错，不静默外推。
5. 点击 **Analyze d-DOS**。读取和计算在独立短进程中进行，120秒超时；改参数、换系统或离开面板会取消已有任务，旧回调不会恢复过期结果。
6. 完成后状态仅显示`atoms 1,2,3 | d | up | E−EF: -6 to 0 eV.`这类选择摘要；来源、求和方式和重采样细节保留在悬浮提示及CSV，版本放在顶部。**Copy results**复制表格；双击数值可进入文字编辑状态复制单个数字（编辑不保存）。**Export CSV**保存结果及来源、所选原子/元素/轨道/自旋、费米能级、范围、版本、归一化方式和计算定义；不覆盖已有文件。更改参数后需重新计算才能导出。

## 导出Python和Bash脚本

完成分析后点击 **Export scripts**，选择一个新的`.py`文件名，同时生成同名`.py`和`.sh`。任意一项已存在都会拒绝导出；失败时清理本轮创建的文件，避免留下半套脚本。参数变化或离开面板仍会自动取消运行中的计算。

- **Python**：嵌入当前原子/轨道/自旋已求和的完整d-DOS与计算代码，不依赖p4vasp或原VASP文件，不运行VASP。单个代表性原子仅作数值API容器，不是计算结构。可以调整积分范围；换原子/轨道/自旋需重新导出。
- **Bash**：调用下方的`p4v`命令行功能，重新读取原DOSCAR/XML及匹配结构。可直接编辑原子、轨道、自旋、范围和输出文件。它依赖原数据和支持新命令的p4vasp安装，不使用Python脚本中的快照。

```bash
# Python脚本：在仓库根目录用科学环境运行
.venv-science/bin/python /path/to/analysis.py
.venv-science/bin/python /path/to/analysis.py --emin -6 --emax 0 --output /path/to/new-result.csv

# Bash脚本：可选参数覆盖输出CSV位置
bash /path/to/analysis.sh
bash /path/to/analysis.sh /path/to/another-result.csv
```

Python默认写`analysis_results.csv`，Bash默认写`analysis_cli.csv`，都拒绝覆盖已有文件。Python脚本开头有依赖安装命令，版本变化会提示。Bash非交互执行不自动加载`.bashrc`别名，因此脚本在找不到`p4v`命令时，使用导出机器的`p4v.sh`路径定义兼容函数；换机后可修改该路径或把正确的p4v安装到PATH。

## 命令行分析（不打开GUI）

```bash
p4v DOSCAR selected_atoms orbitals both/up/down Emin Emax xxx.csv
```

上行为参数说明，实际使用示例：

```bash
p4v DOSCAR 1-3 dxy,dyz both -6 0 result.csv
p4v DOSCAR 1,3 d up -8 2 other.csv
p4v vasprun.xml all d both full full full-range.csv
# 参数帮助
p4v --dos-analysis --help
```

原子从1编号，可用逗号和范围，或`all`。多个轨道用逗号放在一个参数中；`d`不能与单个轨道混合。能量相对EF=0，`full`表示使用该侧源网格边界。非自旋计算建议用`both`，不存在的down通道会报错。路径有空格时加引号，输出CSV拒绝覆盖。

该入口在GTK/原生窗口导入之前分流，用统一科学环境计算。也可显式写`p4v --dos-analysis DOSCAR ...`。单参数`p4v DOSCAR`仍打开原GUI；原图片导出参数不变。命令行与GUI使用相同分析方法、选择校验和CSV定义。

## 数据要求

- 总DOS不能代替d投影DOS。DOSCAR没有投影时仍可画总DOS，但无法分析d-band。
- DOSCAR需要同目录匹配的、显式包含元素符号的VASP5 **POSCAR**或**CONTCAR**，优先POSCAR，不读取POTCAR。原子数必须一致；用户仍需确认元素顺序与DOSCAR相同，仅原子数一致不能证明文件匹配。
- 支持共线非自旋/自旋的spd、spdf汇总以及9/16轨道lm投影。只有汇总d时请选择d，不能分解或组合不存在的独立d轨道。旧Local DOS控制也可使用新读入的DOSCAR投影。
- SOC/非共线投影暂不支持，会拒绝相关INCAR/XML设置或不支持的列数。单自旋17列在缺少INCAR时有布局歧义，要求提供INCAR。请保留实际计算的INCAR，不要删除SOC标记来绕过校验。
- 截断、原子块数错误、非有限数、网格或列数不一致、明显负投影密度会拒绝。不把绘图向下显示的spin-down负号带入分析，也不以绝对值掩盖坏数据。

## 指标与定义

设相对能量为ε=E−EF，ρ为所选原子/轨道/自旋的**原始正投影DOS之和**，积分窗口为[a,b]。

| 指标 | 定义 | 单位 |
|---|---|---|
| d-band center | ∫ερdε / ∫ρdε | eV |
| d-band width | √[∫(ε−center)²ρdε / ∫ρdε]，标准差，不是半峰宽 | eV |
| d-band filling | 窗口内费米能级以下积分 / 窗口内全部积分 | 无量纲 |
| d-band upper edge | 完整所选d-DOS的Hilbert变换最大值，在所选窗口内的峰位置 | eV |

中心、宽度和upper edge使用pymatgen CompleteDos。中心/宽度的窗口端点线性插值后积分。填充度在窗口与EF处插值并使用梯形积分，明确包含EF端点；这是本程序的窗口填充度定义，不直接套用pymatgen没有能量范围参数、使用严格ε<0网格掩码的get_band_filling。它不是投影d电子数，也不是以10个d态归一化的占据率。

Hilbert变换使用完整所选谱，窗口只限制峰位置搜索。VASP文本能量常因小数舍入看起来不等距：当原网格与同端点/点数的等距网格最大偏差不超过平均步长5%时，只为Hilbert计算线性插值到等距网格；界面提示及CSV记录点数、步长和最大调整量，center/width/filling仍用原始网格。5%是限制插值幅度的数值判据，不是科学误差保证；更明显的不均匀网格仍显示Unavailable。零投影权重拒绝计算。界面和CSV均保留这些限制，不能把缺失值当零。

多原子结果按投影态权重合并，不是各原子band center的算术平均。跨体系比较需要相同投影设置、窗口与自旋约定；局域轨道方向依赖计算坐标系，本程序不自动旋转到局部配位坐标。d-band指标本身不能直接证明吸附强弱或催化活性。

API定义参考：[pymatgen CompleteDos](https://pymatgen.org/pymatgen.electronic_structure.html#pymatgen.electronic_structure.dos.CompleteDos)。

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
3. 选择全部 **d** 或单独的 **dxy/dyz/dz2/dxz/dx2**（dx2表示dx²−y²），以及同排的 **Both / Up / Down** 三个互斥按钮。无自旋计算只启用Both，Up和Down灰显；切回自旋计算后自动恢复。可用性按实际总DOS通道判断，尚未读到数据时也暂时禁用独立通道。Both表示可用通道相加而非平均；无自旋时就是唯一总通道，不额外乘2。
4. 在同一行的 **Energy Range (eV)**、**Emin**、**Emax** 紧凑输入框中输入相对费米能级的上下限。留空使用原文件完整能量网格。分析范围与绘图缩放独立，超出数据范围会报错，不静默外推。
5. 点击 **Analyze d-DOS**。读取和计算在独立短进程中进行，120秒超时；改参数、换系统或离开面板会取消已有任务，旧回调不会恢复过期结果。
6. 完成后状态仅显示`atoms 1,2,3 | d | up | E−EF: -6 to 0 eV.`这类选择摘要；来源、求和方式和重采样细节保留在悬浮提示及CSV，版本放在顶部。**Copy results**复制表格；双击数值可进入文字编辑状态复制单个数字（编辑不保存）。**Export CSV**保存结果及来源、所选原子/元素/轨道/自旋、费米能级、范围、版本、归一化方式和计算定义；不覆盖已有文件。更改参数后需重新计算才能导出。

## 导出Python分析脚本

完成当前分析后，点击 **Export Python script** 保存`.py`。此按钮替代原Cancel按钮；参数变化或离开面板仍会自动取消运行中的任务。**Use last DOS line**继续保留。

脚本嵌入当前原子/轨道/自旋已经求和的完整d-DOS与计算方法，不需要原始DOSCAR/XML或p4vasp安装，不运行VASP。单个代表性原子仅作pymatgen API的数据容器，不代表导出了新的计算结构。使用装有pymatgen的Python运行，例如在仓库根目录：

```bash
.venv-science/bin/python /path/to/d-band-analysis.py
# 可只调整积分范围；原子、轨道、自旋选择固定为导出时的选择
.venv-science/bin/python /path/to/d-band-analysis.py --emin -6 --emax 0 --output /path/to/new-result.csv
```

默认输出脚本同目录的`脚本名_results.csv`，拒绝覆盖已有文件。脚本开头包含依赖安装命令；版本不同时会提示。若要换原子、轨道或自旋，请在p4vasp重新分析并导出；脚本不包含全部投影通道。CSV仍记录完整选择、来源、版本和数值定义，不嵌入原始结构文件或全部投影。

## 数据要求

- 总DOS不能代替d投影DOS。DOSCAR没有投影时仍可画总DOS，但无法分析d-band。
- DOSCAR需要同目录匹配的、显式包含元素符号的VASP5 **POSCAR**或**CONTCAR**，优先POSCAR，不读取POTCAR。原子数必须一致；用户仍需确认元素顺序与DOSCAR相同，仅原子数一致不能证明文件匹配。
- 支持共线非自旋/自旋的spd、spdf汇总以及9/16轨道lm投影。汇总d不能分解为五个独立d轨道。旧Local DOS控制也可使用新读入的DOSCAR投影。
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

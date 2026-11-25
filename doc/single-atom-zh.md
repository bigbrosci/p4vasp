# 单原子参考信息与输入生成

在 **Models → single atom** 点击元素，自动打开 **Single atom** 弹窗。

## 参考资料（只读）

显示名称、符号/原子序数、当前元素资料中的质量，以及中性自由原子的基态电子组态、基态能级、LS标签对应的S和多重度2S+1。
电子组态及能级来自离线NIST ASD 5.12快照，涵盖H至Hs共108项；不在快照中的元素、未指认LS项或jj耦合条目的S/多重度显示Unknown，不按J或电子数猜测。
[原始NIST表](https://physics.nist.gov/cgi-bin/ASD/ie.pl?at_num_out=on&biblio=on&e_out=0&el_name_out=on&level_out=on&shells_out=on&spectra=H-DS+i&unc_out=on&units=1)使用包括[Cd]/[Hg]在内的闭壳层缩写；部分重元素数据为估计或近似LS指认。
参考值不是离子态数据，也不意味着DFT必然得到相同基态或自动施加轨道占据。

资源为`data/resources/atomic_states.json`及捕获的表格行`atomic_states_source.txt`，JSON记录来源/DOI/日期/捕获摘要。
维护时可用`python tools/import_atomic_reference.py`从捕获行重建JSON，程序运行不联网、不要求ASE/pymatgen。

## 当前计算设置

- **Charge**默认0，正值少电子，负值多电子。
- **ISPIN**默认2（允许自旋极化），1是不自旋极化；它不是S或未成对电子数。
- **MAGMOM (μB)**默认留空，不写显式初始磁矩。中性、LS信息可用且非重原子时可点Use atomic 2S，采用2S作为可编辑的初始值；不保证最终磁矩或能量基态。带电、LS未知或Z>86时需自行判断，按钮禁用。
- **Constrain spin**默认关闭。打开后明确设置NUPDOWN=N↑−N↓；中性适用条目可先填入参考2S。约束时空MAGMOM自动与NUPDOWN一致；显式不一致会拒绝生成。NUPDOWN为0也有效。
- **POTCAR ZVAL**可留空；如果填写，必须是所选POTCAR的价电子数，不是元素原子序数。已知时检查NELECT−NUPDOWN非负且为偶数。
- **Cell lengths**默认13×14×15 Å，三个方向可改，原子仍在晶胞中心。KPOINTS仍为Gamma 1×1×1，保留现有INCAR标准与ALGO=ALL、NELM=500。

[ISPIN](https://vasp.at/wiki/ISPIN)、[MAGMOM](https://vasp.at/wiki/MAGMOM)与[NUPDOWN](https://vasp.at/wiki/NUPDOWN)含义不同。
磁矩初始化不等于强制最终态；固定总自旋也不固定各个轨道的占据。全电子参考中的自旋可能涉及POTCAR已冻结的芯态，需核对所选价电子空间；未提供ZVAL时程序无法确认价电子数/自旋奇偶关系。
原子计算还需验证POTCAR、盒子/截断能和电子态收敛，参见[VASP原子计算说明](https://vasp.at/wiki/Calculation_of_atoms)。

## 预览与导出

**INCAR preview**标签显示即将导出的完整INCAR。点击弹窗底部 **Generate inputs**，选择父目录和新文件夹名，生成INCAR、KPOINTS、POSCAR，不覆盖已有目录。
成功导出后记住本次会话中该元素的设置；Cancel不修改全局元素默认值或写文件，主页面Generate inputs可重新打开当前元素的设置。

中性体系默认不写NELECT。带电时，若提供ZVAL，按`NELECT = ZVAL − Charge`写入；例如Cu的POTCAR若ZVAL=11，Charge=+1时NELECT=10，Charge=−1时为12。
未提供ZVAL时允许导出明确标注的模板，INCAR写`NELECT = SET_AFTER_POTCAR`，**必须在运行VASP前根据所选POTCAR替换为数值**。
弹窗、目录窗口及主页面均提示待完成NELECT；不能从NIST全电子组态擅自推算POTCAR价电子数。参见[NELECT](https://vasp.at/wiki/NELECT)。

该弹窗的设置用于当前原子输入，不改p4vasp data中的质量、颜色、Magmom/U/J默认资料；不会运行VASP或生成POTCAR。

## 固相结构参考

弹窗同时显示 **Phase (~298 K, ~1 bar)**、**Solid structure** 和 **Structure conditions**，并提供独立的 **Crystal structure reference** 来源链接。
常温固体给出相应体相结构，例如Cu为fcc、Fe为bcc、Mg为hcp；Si/Ge标为金刚石结构，石墨不混同hcp，α-Mn不混同简单bcc。
气体和液体给出明确标注条件的低温固相参考，例如α-N₂采用35.6 K以下的分子立方相参考，而不是把氮气称为六方晶体。
氢的hcp描述分子中心排布，取向与正/仲氢组成有关；氦是例外，常压降温不会凝固，⁴He低温hcp固相需要约25 bar或更高压力。

离线`data/resources/crystal_states.json`首版收录83个元素的审阅条目，未核验结构显示Unknown，不推测超重元素结构。室温参考取约298 K、1 bar，不能作为完整温压相图。
依据[用户提供的结构索引](https://periodictable.com/Properties/A/CrystalStructure.html)，结合[AFLOW原型及文献](https://aflow.org/p/struk_A.html)、[NIST氢资料](https://nvlpubs.nist.gov/nistpubs/Legacy/MONO/nbsmonograph168.pdf)与[氦综述](https://doi.org/10.1103/RevModPhys.84.759)区分晶格、原子基元及相条件。
这些内容只读，不改ISPIN/MAGMOM或自动生成bulk；Single atom仍生成盒子中心的单个孤立原子。

## 两种磁矩来源

**Use atomic 2S**（原Use reference）按NIST中性自由原子的LS项取2S，作为自旋初始MAGMOM估计，不是含轨道贡献的总磁矩，也不是由J算有效磁矩。Fe的基态⁵D对应S=2，因此按钮填4 μB。
**p4vasp data → Magmom**则是可编辑的计算初始矩预设，例如Fe的3 μB；它不是NIST自由原子基态数据，也不应视作实验体相磁矩。弹窗分别显示两者的来源与当前值，原子参考按钮不会覆盖个人预设。两者都不保证最终DFT磁矩，按钮默认不自动应用。

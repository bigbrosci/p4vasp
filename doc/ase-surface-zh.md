# ASE表面建模

入口：左侧 **Models → surface**。页面首次点击才创建；切换标签保留设置，不在主界面导入ASE。
本版沿用独立ASE计算环境，提供常用金属面和按输入晶胞切面的首版流程。

## 1. 快速生成Cu(111)

1. 点击顶部 **Metal preset**，Metal surface选择 **fcc111**。
2. Element填Cu，a填3.615 Å；这是可修改的演示输入，不是自动优化的晶格常数。
3. Atomic layers填4，In-plane repeat填2、2。
4. Vacuum EACH side填10 Å，Fix bottom geometric layers填2，Layer tolerance保留0.3 Å。
5. 点击 **Build surface**，得到16原子、4几何层，其中底部8原子固定。
6. 默认选中 **Center**。可点 **Bottom** 将最低原子移到z=0.1 Å，或点Center恢复居中。**Preview 3D**以完整晶胞侧视图显示真空，可旋转观察。有一个或多个固定坐标的原子会显示 X。
7. **Save POSCAR** 选择父目录及新文件夹名，自动保存POSCAR、surface.json、rebuild_surface.py和rebuild_surface.sh；已有文件夹不覆盖。

改变参数或输入来源后，旧结果和保存按钮失效，需重新Build。生成在独立进程运行，可Cancel，默认60秒超时。
这不是DFT优化或稳定性筛选；没有生成INCAR、KPOINTS或POTCAR。

## 2. 来源与晶面约定

顶部只有一排三个来源按钮：**Metal preset｜Use bulk result｜Open POSCAR / CIF**，高亮项表示当前来源。
Use bulk result直接读取bulk结果快照，Open POSCAR / CIF直接打开选择窗口，无需先选下拉框。
取消文件选择或bulk尚无结果时，保留之前的来源和已生成结构；成功载入新快照/文件后需重新Build。
Use bulk result后，灰色Element/a/c显示Bulk生成时的输入参数，仅供核对；实际切面采用完整结构快照，包括超胞。需要改晶格时回bulk修改并重新生成，再点Use bulk result。导入文件时这些预设参数框留空，使用文件晶胞；切回Metal preset会恢复原先预设输入。


| 来源 | 操作与含义 |
|---|---|
| Metal preset | fcc111、fcc100、fcc110、bcc110、bcc100、bcc111、hcp0001；必须输入元素和晶格长度，hcp还需c。使用ASE对应标准表面构建器，层数为其原子层数。hcp0001的三指数显示为(0 0 1)。 |
| Use bulk result | 先在bulk页Build，再点击Use bulk result，取得该结果的POSCAR快照；不是实时追踪bulk之后的修改。 |
| Open POSCAR / CIF | Open POSCAR / CIF明确选择周期体相结构；CIF多数据块读取最后一份，POSCAR按单结构读取；不自动给分子添加晶胞。 |

后两种来源调用ASE通用surface。**(h k l)相对于输入晶胞，不自动转换成常规胞**。
如果希望使用通常文献中的常规胞指数，应先提供相应常规胞；例如在Bulk页对支持的晶型选择cubic。
它们的layers表示ASE的“等价层”，可能包含多个几何原子层，结果另显示实际几何层数。
指数允许−10到10的整数，不能全零；公因子会约去，例如(2 2 2)按(1 1 1)处理。

本版只按所选输入和切面生成一个默认终止方式，不枚举不同终止面，也不判定极性或表面稳定性。

## 3. 尺寸与固定原子

- **In-plane repeat**：沿生成表面两个面内基矢重复，不是固定的屏幕X/Y方向。各1—100，总原子不超过10000。
- **Vacuum EACH side**：几何表面上下各留该厚度。Center下填10 Å表示两侧各10 Å，总空隙20 Å。Bottom下标签显示Half total vacuum，同一数值仍表示总空隙的一半，最低原子留0.1 Å，上侧空隙为19.9 Å。POSCAR本身不保存ASE的非周期方向标记，VASP仍按三维周期体系和真空处理。
- **Layer tolerance**：ASE沿表面法线识别几何层时的相邻距离容差。默认0.3 Å；复杂起伏层需要用户调整并检查，不按化学组成猜测层编号。
- **Fix bottom geometric layers**：从最低层向上固定指定层，写FFF，其他原子写TTT。0表示全部自由且不输出Selective dynamics行；必须至少留一层自由。此规则替换输入中的固定约束，不与旧掩码叠加。

保存前按元素稳定分组，固定标记和层编号一起同步排序；不靠重新排序后的旧原子索引猜固定位置。
原输入文件及bulk结果不修改。

## 4. 文件与依赖

`POSCAR`用于后续结构计算。`surface.json`记录ASE版本、建模参数、晶胞、几何层数、固定原子数以及与POSCAR行序一致的layer_numbers。
层编号从底部1开始，原子索引按POSCAR从0开始。自定义体相来源在参数中嵌入POSCAR，文件导入不依赖原文件的绝对路径。
保存时同时导出两个重建脚本，记录最终建模参数、体相快照和Center/Bottom位置；不是逐次鼠标操作或相机记录，也不包含全部VASP计算设置。

在保存目录运行以下任一方式，输出到新的文件夹：

```bash
python rebuild_surface.py --output rebuilt_python
bash rebuild_surface.sh rebuilt_bash
```

Python脚本内嵌生成代码与输入，只需ASE，不依赖p4vasp或原始POSCAR/CIF；建议使用脚本顶部注明的ASE版本。
Bash脚本调用`p4v --surface-replay surface.json rebuilt_bash`，需要已安装p4vasp及ASE环境。
未找到p4v命令时会回退到导出时的启动器位置；换机后应配置p4v命令或修改脚本中的路径。
两个脚本都重建POSCAR、参数JSON和脚本，不覆盖已有目录；重复运行请另选输出目录。
相同ASE版本下验证晶胞、坐标、元素顺序和固定标记一致；POSCAR数字格式可能不同。
直接编辑Python中的REQUEST可以修改建模参数，Bash则读取旁边JSON中的request。
这不会运行VASP，也不会生成INCAR、KPOINTS或POTCAR。

如果未安装ASE，在项目目录运行：

```bash
bash install/install-science.sh
```

页面底部也提供按当前安装位置生成的可复制命令。使用现有ASE环境可设置P4VASP_ASE_PYTHON，不把ASE强行装进GTK解释器。
Linux/WSL验证了实际ASE构建、原生预览与保存；2026-11-23 Windows冻结包亦通过构建/预览/保存及无界面重放检查，macOS和另一台干净Windows未验收。
11月21日Windows便携包不含本次Surface功能；新包路径及范围见[Windows交付记录](windows-update-workflow-zh.md)。


## 5. Center与Bottom

两个互斥按钮既可在Build前选择，也可对已有结果立即切换，无需重新切面或重新读取源文件。
Center按ASE center(axis=2)的几何包围盒居中，不是质量中心；保持晶胞高度不变。
Bottom只沿z平移，使最低原子的**笛卡尔z坐标为0.1 Å**。晶胞尺寸、总真空量、原子间距、层号及F/T标记不变；
例如Center上下各10 Å的模型切到Bottom后，下方留0.1 Å，上方19.9 Å。

预览打开时自动刷新，保存的是当前摆放方式。surface.json中的placement、vacuum_bottom、vacuum_top记录实际状态；
vacuum_each_side仅Center下有数值，Bottom下为null，request.vacuum仍为居中等效的每侧值。
POSCAR若用Direct坐标，文件中的分数z不会直接等于0.1，换算到Å后才是0.1。
总真空必须大于0.1 Å才能选择Bottom，不会为此自动拉长晶胞。
0.1 Å是初始留边，不保证优化位移后绝不会跨越周期边界，仍应检查优化后的结构。

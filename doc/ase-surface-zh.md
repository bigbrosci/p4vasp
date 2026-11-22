# ASE表面建模

入口：左侧 **Models → surface**。页面首次点击才创建；切换标签保留设置，不在主界面导入ASE。
本版沿用独立ASE计算环境，提供常用金属面和按输入晶胞切面的首版流程。

## 1. 快速生成Cu(111)

1. Source选择 **Metal preset**，Metal surface选择 **fcc111**。
2. Element填Cu，a填3.615 Å；这是可修改的演示输入，不是自动优化的晶格常数。
3. Atomic layers填4，In-plane repeat填2、2。
4. Vacuum EACH side填10 Å，Fix bottom geometric layers填2，Layer tolerance保留0.3 Å。
5. 点击 **Build surface**，得到16原子、4几何层，其中底部8原子固定。
6. **Preview 3D** 打开原生预览，标记圈表示固定原子，可旋转观察；不是对源结构的编辑。
7. **Save POSCAR** 选择父目录及新文件夹名，保存POSCAR和surface.json；已有文件夹不覆盖。

改变参数或输入来源后，旧结果和保存按钮失效，需重新Build。生成在独立进程运行，可Cancel，默认60秒超时。
这不是DFT优化或稳定性筛选；没有生成INCAR、KPOINTS或POTCAR。

## 2. 来源与晶面约定

| 来源 | 操作与含义 |
|---|---|
| Metal preset | fcc111、fcc100、fcc110、bcc110、bcc100、bcc111、hcp0001；必须输入元素和晶格长度，hcp还需c。使用ASE对应标准表面构建器，层数为其原子层数。hcp0001的三指数显示为(0 0 1)。 |
| Bulk result | 先在bulk页Build，再点击Use bulk result，取得该结果的POSCAR快照；不是实时追踪bulk之后的修改。 |
| Structure file | Open POSCAR / CIF明确选择周期体相结构；CIF多数据块读取最后一份，POSCAR按单结构读取；不自动给分子添加晶胞。 |

后两种来源调用ASE通用surface。**(h k l)相对于输入晶胞，不自动转换成常规胞**。
如果希望使用通常文献中的常规胞指数，应先提供相应常规胞；例如在Bulk页对支持的晶型选择cubic。
它们的layers表示ASE的“等价层”，可能包含多个几何原子层，结果另显示实际几何层数。
指数允许−10到10的整数，不能全零；公因子会约去，例如(2 2 2)按(1 1 1)处理。

本版只按所选输入和切面生成一个默认终止方式，不枚举不同终止面，也不判定极性或表面稳定性。

## 3. 尺寸与固定原子

- **In-plane repeat**：沿生成表面两个面内基矢重复，不是固定的屏幕X/Y方向。各1—100，总原子不超过10000。
- **Vacuum EACH side**：几何表面上下各留该厚度。填10 Å表示两侧各10 Å；周期镜像之间的总空隙为20 Å。POSCAR本身不保存ASE的非周期方向标记，VASP仍按三维周期体系和真空处理。
- **Layer tolerance**：ASE沿表面法线识别几何层时的相邻距离容差。默认0.3 Å；复杂起伏层需要用户调整并检查，不按化学组成猜测层编号。
- **Fix bottom geometric layers**：从最低层向上固定指定层，写FFF，其他原子写TTT。0表示全部自由且不输出Selective dynamics行；必须至少留一层自由。此规则替换输入中的固定约束，不与旧掩码叠加。

保存前按元素稳定分组，固定标记和层编号一起同步排序；不靠重新排序后的旧原子索引猜固定位置。
原输入文件及bulk结果不修改。

## 4. 文件与依赖

`POSCAR`用于后续结构计算。`surface.json`记录ASE版本、建模参数、晶胞、几何层数、固定原子数以及与POSCAR行序一致的layer_numbers。
层编号从底部1开始，原子索引按POSCAR从0开始。自定义体相来源在参数中嵌入POSCAR，文件导入不依赖原文件的绝对路径。
这份JSON用于追溯，首版尚未生成独立重放Python脚本，也不包含全部VASP计算设置。

如果未安装ASE，在项目目录运行：

```bash
bash install/install-ase.sh
```

页面底部也提供按当前安装位置生成的可复制命令。使用现有ASE环境可设置P4VASP_ASE_PYTHON，不把ASE强行装进GTK解释器。
本轮Linux/WSL验证了实际ASE构建、原生预览与保存；macOS及Windows成品尚未验收。
11月21日Windows便携包不含本次Surface功能；Windows worker/spec和诊断入口已接入，需后续重新构建验证。

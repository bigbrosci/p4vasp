# SMILES 生成气相初始结构

入口：**Database → Models → gas phase**。原来的 XYZ 本地库保留，新增 SMILES 输入行。

## 使用

1. 输入 SMILES，例如乙醇 `CCO`、苯 `c1ccccc1`、铵离子 `[NH4+]`。
2. 点击 **Build 3D + optimize**。程序补全显式氢，生成三维候选构象并做分子力场优化。完成后列表出现 `[SMILES]` 条目，并自动打开三维预览。
3. 核对结构、Charge、Multiplicity 和晶胞。形式电荷由 SMILES 填入；**自旋多重度一律留空，由用户确认**，不能仅凭 SMILES 判断磁态。例如氧气的普通 SMILES 不足以确定其自旋态。
4. 继续使用已有 **Preview 3D** 和 **Generate inputs**，选择文件夹生成 INCAR、KPOINTS、POSCAR。带电体系沿用 `NELECT = SET_AFTER_POTCAR` 待填模板。

生成结构暂存在当前 Models 页面内存中，不自动写入 XYZ 库；离开 Models 前用 Generate inputs 保存，POSCAR 保留优化后几何。列表中的 XYZ 文件仍能照常选择；Refresh 保留当前生成结构及已填参数。重新生成只保留最新一份 SMILES 结构。失败或取消不会覆盖之前的结构。

## 初步优化的含义

采用 RDKit 的 **ETKDGv3**，固定随机种子 `20261031`，最多生成 8 个候选（去重后可能更少）；参数完整时用 **MMFF94s**，否则尝试 **UFF**。最多优化 1000 步，取已经收敛的候选中力场能量最低的一份。没有可收敛候选或缺力场参数时明确报错，不把未优化结构标为成功。

这是分子力场初始几何，不是 DFT 优化、真实气相最低能构型、热力学能量或最终磁态。界面显示的能量为力场能量（kcal/mol），不能直接与 VASP 能量比较。INCAR 注释记录规范化 SMILES、RDKit 版本、方法、种子及力场能量。固定版本和参数有利于重复生成；不同版本不保证相同坐标。

显式 `@`／`@@` 等立体信息用于约束构型，未指定的潜在立体信息会提示该几何只是一个可能的结果；请预览核对。SMILES 的同位素标记可保留在来源注释，但 POSCAR 只写元素符号，不自动设置同位素质量。

首版支持常见有机／主族分子（H、B、C、N、O、F、Si、P、S、Cl、Se、Br、I）。多个片段、盐、金属及不支持的元素要求改用已有 XYZ 接口；不自动摆放片段或重建配位。限制为最多 100 个非氢原子、加氢后最多 300 原子、SMILES 长度最多 2048 字符。

实现参考：[RDKit Python 入门](https://www.rdkit.org/docs/GettingStartedInPython.html)、[力场接口](https://www.rdkit.org/docs/source/rdkit.Chem.rdForceFieldHelpers.html)。

## 可选依赖安装

XYZ、单原子和其他功能不需要 RDKit。Linux 源码版可在仓库根目录执行：

```bash
bash install/install-rdkit.sh
```

脚本用 `python3` 创建仓库内 `.venv-smiles`，只在该环境安装 RDKit 及其依赖，不改 GTK 应用所用 Python。需要 Python 的 venv／pip 支持和首次安装的网络。也可指定创建环境的解释器：

```bash
PYTHON=/path/to/python3 bash install/install-rdkit.sh
```

界面自动找到该环境；也可使用已经装好 RDKit 的外部 Python：

```bash
P4VASP_SMILES_PYTHON=/path/to/python bash p4v.sh
```

这里必须是 Python 可执行文件路径，不要附加命令参数。环境只在本设备安装有效，不要把同步来的虚拟环境视为其他设备可用环境。当前 Linux 已验证；macOS／Windows／冻结 EXE 的依赖与打包未验证，Windows 构建仍暂停。

每次点击生成仅启动一个隔离计算进程，RDKit 单线程，不在打开页面时启动常驻任务；GUI 保持响应。**Cancel**、离开页面和 60 秒超时会终止并回收该进程。主界面不导入 RDKit 或它的 NumPy，因此不与 GTK 环境的二进制依赖混用。缺依赖会提示安装方法，XYZ 功能继续可用。

## 本机验证命令

安装可选环境后，从仓库根目录运行：

```bash
PYTHONPATH=lib P4VASP_HOME="$PWD" .venv-smiles/bin/python test/testSmilesChemistry.py
PYTHONPATH=lib:src P4VASP_HOME="$PWD" /usr/bin/python3 test/testSmilesTask.py
GDK_BACKEND=x11 PYTHONPATH=lib:src P4VASP_HOME="$PWD" /usr/bin/python3 test/testSmilesGtk.py
```

最后一项需要显示环境和现有原生扩展。测试生成临时输入，不能替代 VASP 收敛性或科学结果验证。

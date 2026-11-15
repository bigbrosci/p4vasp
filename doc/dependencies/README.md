# 依赖维护入口

本目录用于长期维护依赖信息，不负责安装、不自动升级，也不取代平台安装脚本。初版于2026年11月14日建立。

## 文件各自负责什么

| 文件 | 职责 | 不负责什么 |
|---|---|---|
| [catalog.json](catalog.json) | 唯一的分层依赖目录：用途、运行环境、必需/功能/间接/构建/历史类别、平台包名及源码依据 | 不重复抄写安装脚本中的精确版本，不是安装器输入 |
| [snapshots/](snapshots/) | 某个日期、设备平台、Python环境实际可发现的版本、原始Requires-Dist及ABI记录 | 不是安装锁文件、最小依赖集合、完整系统库清单或功能通过证明 |
| [dependency_snapshot.py](../../tools/dependency_snapshot.py) | 只读生成快照，校验清单结构/源码引用；只使用Python标准库 | 不import科学/GUI依赖、不运行安装命令、不自动清理环境 |
| [安装指南](../../install.md) | 用户如何安装和启动 | 不再另维护一套精确版本表 |
| [全层盘点报告](../dependency-inventory-2026-11-14-zh.md) | 当时的人工调查证据与待办 | 历史结论不会自动成为新设备的实测结果 |

平台脚本仍是执行层的依据：Ubuntu/Debian看`install/ubuntu-bootstrap.sh`，macOS看`install/macos-bootstrap.sh`，可选科学环境看`install/install-ase.sh`和`install/install-rdkit.sh`，Windows看spec、`prepare_model_env.py`及相关构建入口。清单的sources指向这些位置，避免版本号在两处手工同步。

## 环境边界

- `gui`：主GUI和原生模块所用Python。当前Linux示例是`/usr/bin/python3`，不是激活的base或ASE环境；macOS应使用实际GUI解释器。
- `ase`：隔离ASE环境；不要求把ASE装进主GUI解释器。
- `smiles`：隔离RDKit环境；不要求将其合并进ASE或GTK环境。
- `windows-model`：构建Windows科学worker的官方CPython环境；**不是已冻结的worker.exe**。
- `build`：用于GUI打包/开发的Python，可与实际GUI解释器对应。

profile只是记录者对该解释器角色的说明。选错profile不会替你切换Python，也不会安装所缺组件。清单中feature表示对应功能需要，并不代表任意启动方式都需要；transitive表示间接依赖，未直接import不能作为删除依据。

GLUT尚有干净设备/平台声明待核验项，已经在catalog注明“pending”，没有编造包名或悄悄改变安装器。不要把“系统库能定位”写成“图形功能验收通过”。

## 日常使用

在仓库根目录执行。下面仅做清单检查，不采集环境，也不安装任何东西：

```bash
python3 tools/dependency_snapshot.py --check
python3 test/testDependencySnapshot.py
```

初次建立基线、更换设备、实际安装/升级依赖或准备发行时，用**目标解释器**生成快照。例如Linux：

```bash
/usr/bin/python3 tools/dependency_snapshot.py --profile gui --output /tmp/p4vasp-linux-gui.json
.venv-ase/bin/python tools/dependency_snapshot.py --profile ase --output /tmp/p4vasp-linux-ase.json
.venv-smiles/bin/python tools/dependency_snapshot.py --profile smiles --output /tmp/p4vasp-linux-smiles.json
```

macOS同样运行这个工具，但将命令前面的解释器换成该设备实际的GUI／ASE／SMILES解释器。不要直接运行从另一设备同步的虚拟环境。Windows在构建Python中执行该工具，例如MSYS2 UCRT64的GUI打包环境：

```bash
/ucrt64/bin/python tools/dependency_snapshot.py --profile build --output /tmp/p4vasp-windows-gui-build.json
```

Windows科学worker则用实际的官方CPython构建解释器运行脚本并选择`windows-model`；该路径以当前缓存配置为准，不在共享说明中写死用户名。已冻结EXE没有通用的Python脚本执行接口，应保留更新器生成的runtime/gui/models报告及源码标识，不能把本工具的源码环境快照当作冻结包验收。

工具拒绝覆盖已有输出；同日重采请换新文件名，如加`-r2`。没有`--output`时JSON输出到标准输出，可自行重定向。输出缺少某项发行元数据时仍会生成报告，状态为metadata-not-found；**成功生成快照不等于依赖齐全或程序可用**。

## 快照如何保存

1. 先写临时文件，核对profile、平台、Python版本和SOABI是否正确。
2. 查看declared以及distributions差异。后者是当前解释器全部可发现的发行元数据，可能含与p4vasp无关的包，不能直接拿来批量安装/卸载。
3. 原始Requires-Dist包含markers/extras，工具没有解析为“本次实际激活”的完整依赖图；原生库、系统包和冻结归档也不在该列表里。
4. 需要留存时命名为`YYYY-MM-DD-平台-角色[-设备代号][-r2].json`，放snapshots。不同设备不要互相覆盖；不必为普通代码修改反复生成版本快照。
5. 提交前检查包名/版本、原始依赖字符串是否含内部来源地址等不宜共享信息。工具不记录主机名、用户名、完整解释器路径、环境变量、凭据或用户计算路径。
6. 配套更新记录明确“采集元数据”和“实际功能测试”各自做了什么。初版三个Linux快照只采集元数据，不能作为新Windows或Mac的验收。

快照含UTC采集时刻、源码Git提交（Git不可用则null）、清单/工具SHA256。基线提交可能是本次维护提交之前的应用版本，哈希用于明确采集时实际工具与清单；快照本身不是可执行锁文件，也不保证二进制可复现。

## 后续新增／升级／移除依赖时

按这一套顺序维护，避免出现新的散落清单：

1. 在catalog中定位或增加条目：用途、kind、profiles、sources；原生项说明平台映射或明确待核验。
2. 修改真正执行安装/打包的脚本或spec。精确版本在执行源中维护，不在README再复制一次。当前第一批未改这些执行行为。
3. 若环境确实变化，采集相关环境的新快照，对比新增/消失/变更版本及间接依赖；不要改写旧快照。
4. 运行清单检查及工具专项测试，再按受影响功能实际验证：例如ASE需测体相/格式/热化学，RDKit需测SMILES生成，原生库需重编译并测窗口；Windows还需成品报告。
5. 同一交付中同步catalog、必要的安装说明、快照和双语更新记录；memory只保存当前状态及证据索引，不复制整个依赖目录。

对历史组件，先确认功能/注册/旧保存格式和引用闭包，再决定归档；对间接依赖，先确认依赖方与受影响功能。不要单凭目录大、年代老、某个模块没import或两处出现同名库就删除。

## 当前边界

这只是第一批基础整理：没有统一运行时、升级/卸载库、修改原生链接、修复旧接口或裁剪EXE。严格版本锁定、自动检测脚本与catalog的语义一致性、系统包快照、完整SBOM和成品依赖树仍属后续独立工作。

## 已建立的修复前检查点（2026-11-14）

开始旧接口修复前，源码`49ff6cd88b5906e83c5c3ea31f2a176491b733bb`已标记并推送到GitHub标签：

```text
checkpoint/2026-11-14-before-legacy-interface-fixes
```

本机备份位于仓库相对路径`build/checkpoints/2026-11-14-49ff6cd-before-legacy-fixes/`：包含source.tar.gz、当前Linux原生模块、三个解释器快照、GTK/原生窗口基线日志、恢复说明及SHA256SUMS。已校验所有摘要，并在临时独立目录解压及导入保存的源码/原生模块；未做恢复目录的完整GUI验收。该目录被Git忽略，GitHub标签只保存源码，不含本机二进制备份。

恢复时先关闭程序，把源码解压到另一个目录，不覆盖当前工作树；同一兼容Linux环境可按备份README复制原生模块并使用原解释器。虚拟环境和系统库没有复制，这不是独立发行包或整机镜像；本批不升级库，因此原有科学环境继续保留。跨设备/ABI必须重编译，不要使用破坏性reset覆盖无关改动。

第一批仅将Property线程状态改为is_alive、VAC耗时改为perf_counter，保留原有线程开关和计算公式。其他审计项与依赖版本升级另行处理。

# Linux 更新后构建 Windows 版本：操作流程

更新日期：2026-11-23。本文保存在同一 Git 仓库，Linux checkout 中也可查阅。
前提：Windows 已安装 MSYS2 UCRT64 和项目构建依赖，且已建立独立 Git checkout。
首次安装、依赖和构建细节见 [安装指南](../install.md#windows-native-build--windows-原生构建试验)。

## 当前交付（2026-11-23）

冻结源码`5ca60f29fb9f552dfacbf6ef86f273a4d8ceb9d3`。完整EXE路径：

```text
C:\msys64\home\lqlhz\p4vasp-checkout\dist\windows-releases\p4vasp-20261123-013128-5ca60f29-r5cg71v2\p4vasp.exe
```

同级ZIP：

```text
C:\msys64\home\lqlhz\p4vasp-checkout\dist\windows-releases\p4vasp-20261123-013128-5ca60f29-r5cg71v2.zip
```

ZIP为198095378字节，SHA256：`76a023a937326818b43596c69961becf4eba2ccbcb4683ddb02f81d4ff7be64d`，另有同名`.zip.sha256`。
完整解压后双击p4vasp.exe，保留整个`_internal`和`model-worker`；不需要另安装Python或设置科学库PATH。
旧发行包保留，本次未另复制到桌面或发布GitHub Release附件。

本版包含Surface切面、固定层、Center/Bottom及保存时Python/Bash重建脚本；个人元素数据覆盖；
DOS左右分栏分析、s/p/d/f三排轨道、自旋按钮、多轨道、三位小数及a.u.填充度、独立Python/Bash脚本和无界面命令。
ASE/RDKit/pymatgen随包科学worker与UCRT64 GTK运行时隔离，实际版本见MODEL-VERSIONS.json，精确构建安装源见prepare_model_env.py。

当前Windows设备成品runtime/gui/models报告均ok/frozen，新增双来源s/p/d/f、f分量、导出脚本及无界面DOS/Surface重放通过；
另在MSYS2实际执行导出的两种Bash脚本，在Windows科学Python实际执行两种独立Python脚本，数值及Surface坐标/晶胞/固定标记核对通过。
独立检查SOURCE-COMMIT、raw helper、ZIP CRC/SHA256通过；预览/建模及公开人工谱回归不等于全部科学任务或另一台干净Windows验收。
Bash脚本仍需Bash（如MSYS2），独立Python脚本仍需其相应科学库；双击GUI不需要这些外部环境。

构建日志：`build/windows-update/5ca60f29-z_n6ok88`；报告：`dist/windows-releases/p4vasp-20261123-013128-5ca60f29-r5cg71v2-checks`。
依赖快照见[依赖维护记录](dependencies/README.md)。后续纯交付文档提交不改变本包SOURCE-COMMIT，无需为文档重复打包。

## 历史交付（2026-11-21）

冻结源码`f5de130ec89e55a76431d0edf8280a609abdd88e`，EXE完整路径：

```text
C:\msys64\home\lqlhz\p4vasp-checkout\dist\windows-releases\p4vasp-20261121-183334-f5de130e-cbhlyoey\p4vasp.exe
```

同级ZIP完整路径：

```text
C:\msys64\home\lqlhz\p4vasp-checkout\dist\windows-releases\p4vasp-20261121-183334-f5de130e-cbhlyoey.zip
```

ZIP 157639531字节，SHA256：`899c35382a75ed3a455c38276eee93608924f73e5e92039f3f79e587ed8f3336`，有同名`.zip.sha256`。
保留整个解压目录的`_internal`和`model-worker`，不能只复制EXE。

本版包含振动鼠标导航统一、H球放大、OUTCAR_freq/OUTCAR-freq/OUTCAR-frequency识别和较轻的实时渲染。
Windows原生编译及成品runtime/gui/models检查通过，独立核对源码、43布局、无旧Glade及ZIP完整性/摘要；
仍需另一台干净Windows及具体科研计算的实际验收。日志在Windows checkout的
`build/windows-update/f5de130e-rkgbsiva`，报告为同级`p4vasp-20261121-183334-f5de130e-cbhlyoey-checks`。
构建环境元数据快照见[依赖维护入口](dependencies/README.md)，并非冻结成品的完整依赖清单。
后续交付文档提交不改变本包SOURCE-COMMIT，不因文档同步重复构建。

## 历史交付（2026-11-14）

当时构建源码为`58e353dc12181e0b4c17604479c90f16bd480ac7`。EXE完整路径：

```text
C:\msys64\home\lqlhz\p4vasp-checkout\dist\windows-releases\p4vasp-20261114-221532-58e353dc-uhsvnjm6\p4vasp.exe
```

同级ZIP：

```text
C:\msys64\home\lqlhz\p4vasp-checkout\dist\windows-releases\p4vasp-20261114-221532-58e353dc-uhsvnjm6.zip
```

ZIP为157631180字节，SHA256：`9130b10606b2822989b30f70bd6a8ac0cfd2b8fb628a951f058db2e473f17540`，另有同名`.zip.sha256`。
保留整个解压目录的`_internal`与`model-worker`，双击p4vasp.exe；不能只复制EXE。

本机Windows UCRT64完整重编译/打包，隔离环境runtime/gui/models报告均通过，随包ASE3.29.0、RDKit2026.09.1；
新增Models按需加载及手动ChatGPT复制入口已包含。独立核对源码标记、43现行布局、旧Glade缺席及ZIP CRC/摘要。
另一台干净Windows和全部科学流程仍未验收。构建日志在Windows checkout的
`build/windows-update/58e353dc-ev9tc_kn`，成品报告在交付目录同级的`p4vasp-20261114-221532-58e353dc-uhsvnjm6-checks`。
后续纯交付文档提交不会改变SOURCE-COMMIT，也不需要重复构建。

下列11月6日和11月5日路径为历史交付记录，日常使用优先以上新版。

## 随包ASE与RDKit（2026-11-06）

当前打包流程已加入独立model-worker，携带ASE3.29.0、RDKit2026.09.1及匹配Python运行库；GUI继续使用原UCRT64工具链。首次构建会从Python.org／PyPI准备项目专用缓存环境，后续复用；不需要给Windows系统安装Python。程序运行时不联网安装依赖，不需配置PATH。

更新仍执行原来的 `bash install/update-windows.sh`。自动验收新增冻结版 `--check-models`，覆盖实际bulk与SMILES界面、随包计算程序、预览、保存和取消。只有整包检查通过后才生成成功ZIP。请保留主目录的 `_internal` 与 `model-worker`，不能只复制EXE。依赖许可随包保留。

本次完整构建及迁移Downloads后的runtime／gui／models三项验收均通过，涵盖32Cu超胞、乙醇SMILES优化、预览、保存及取消。交付位置：

```text
C:\Users\lqlhz\Downloads\p4vasp-20261106-231955-7ccd76d3-isn9bffb\p4vasp.exe
```

双击即可启动。bulk页选择晶体类型／晶格参数／超胞，点击Build bulk、Preview 3D或Save POSCAR；gas phase页输入SMILES，点击Build 3D + optimize，再预览，确认Charge／Multiplicity后Generate inputs。请将完整目录一起复制；分子力场优化得到的是初始结构。

同名ZIP约149MiB，SHA256：`fc109421ddacfbf01cdd9a82fe49c6e26ce4b432bb4101eb36f9855521446823`。包的源码版本为`7ccd76d`，依赖版本另见根目录MODEL-VERSIONS.json。未核验另一台干净Windows，详细证据见[当日更新记录](../update_history/update_2026_11_06.md)。下方11月1日旧包不含这些依赖。

## 最近一次构建（2026-11-01）

用户已恢复Windows打包。当前已生成的便携版源提交为 `9ba86cd855c52754d3be66be3b9d91d00ec4ad24`，交付目录：

```text
C:\Users\lqlhz\Downloads\p4vasp-20261101-190120-9ba86cd8-g3u1bhr3
```

双击其中 `p4vasp.exe`；同级ZIP可分发，先完整解压。构建及迁移到下载目录后的冻结runtime／GUI检查通过，ZIP校验通过。便携包不含可选RDKit，SMILES生成仍需另配环境且本次未验收。其他机器、完整人工建模与正常退出仍需确认。以下更新步骤继续适用于后续源码更新，不能将此版本当作后续提交的自动构建。

## 1. 完成并发布 Linux 更新

先在 Linux checkout 修改、检查并测试 p4vasp，然后将本次相关变更提交并推送到
`https://github.com/bigbrosci/p4vasp.git` 的 `p4vasp-py3` 分支。
Windows 更新只能取得已推送的提交，不会取得 Linux 工作区中的未提交文件，
也不能直接使用 Linux 编译的原生扩展。

需要助手执行时，可以说：

> 把这次更新同步发布，并构建新版 Windows。

助手应按项目规则检查目标、完成相关验证并报告实际提交/推送/构建结果。

## 2. 在 Windows 运行一键更新

从开始菜单打开 **MSYS2 UCRT64**，输入以下两行：

```bash
cd /home/lqlhz/p4vasp-checkout
bash install/update-windows.sh
```

这是当前设备的目录示例，对应 Windows 路径：

```text
C:\msys64\home\lqlhz\p4vasp-checkout
```

其他设备应替换为其实际 checkout 路径。旧 `p4vasp-windows` 目录是历史源码副本，
不要把它当成可 `git pull` 的仓库。

脚本会核对分支、origin 和工作树，执行 fast-forward 更新，从提交创建独立构建副本，
重新编译 Windows 原生扩展，再打包并运行合成检查。
检查期间会短暂打开测试窗口，**等待它自动结束，不要手动关闭测试窗口**。
脚本不会自动升级本机依赖。

## 3. 确认成功或处理报错

只有看到 **`SUCCESS`** 才表示本次脚本的构建和自动检查通过。
终端会显示 EXE、ZIP 和 SHA-256。版本目录中还包含：

- `SOURCE-COMMIT.txt`：本次实际构建的 Git 提交。
- `BUILD-STATUS.txt`：自动验证状态。

若报错，停止后查看终端给出的日志目录，或把错误末尾发给助手。
日志和构建副本位于 checkout 的 `build/windows-update/`。
有本地修改、远程/分支不符或无法 fast-forward 时，脚本会停止；
先保留并核对修改，不要为更新直接清空或重置文件。
未通过检查的目录会保留失败标记，不能当作成功版本使用；旧版仍保留。

## 4. 找到并试用新版

在文件资源管理器中打开当前设备的输出目录：

```text
C:\msys64\home\lqlhz\p4vasp-checkout\dist\windows-releases
```

找到与终端 `SUCCESS` 输出对应的新版本目录，双击其中的 **`p4vasp.exe`**。
每次版本名包含构建时间、源提交短号和唯一后缀；不要误选标记失败的旧目录。

用一份测试用 POSCAR 副本，按需要人工检查：

1. 打开文件，点击 Show 查看原子结构。
2. 旋转、缩放、选择原子，确认常用交互正常。
3. 使用 Build 或 Move atoms → Copy；选择性动力学开启时，新复制原子应为 T T T。
4. 另存到测试目录，重新打开核对坐标与标记。
5. 导出 PNG，确认视角、图片和保存位置符合预期。

自动合成检查不等于完整人工验收、科学结果验证或正常退出验证。

## 5. 验收后替换日常版本

确认新版正常后，可把**整个版本目录**复制到习惯的位置，并重新创建指向新版
`p4vasp.exe` 的快捷方式。不要只复制 EXE，也不要删除 `_internal`。
脚本不会自动替换“下载”文件夹中的旧便携版或已有快捷方式。

同级 ZIP 用于备份或传到其他 Windows 电脑；应先完整解压，再运行 EXE。
先保留上一版，发现问题时切回旧目录即可。确认不再需要后再清理旧构建和 ZIP。

第一次向其他电脑分发前，仍需在没有 Python、GTK、MSYS2 的干净 Windows 环境验证。
当前尚未代码签名或制作安装器，另一设备的安全策略与依赖可用性也需独立核验。

## 可选命令与重放脚本

在正确 checkout 的 UCRT64 窗口中：

```bash
bash install/update-windows.sh --check          # 只读核对；不拉取、不编译
bash install/update-windows.sh --build-current  # 不拉取，构建当前干净提交
```

PNG 重放脚本为 Windows PowerShell `.ps1`，受设备执行策略约束。
本机在用户自行设置 CurrentUser RemoteSigned 后已验证通过，不代表另一电脑也已配置。
普通 GUI 使用无需为了重放而修改策略；也可直接用 `p4vasp-console.exe --preset`。
详见 [图片导出与重放指南](render-cli.md#生成复现命令与批量导出--replay-commands-and-batch-export)。

## 现有验证记录

2026-10-29，一键更新已从提交 `877fb28` 完整实跑成功，冻结 runtime/GUI、ZIP CRC、
源提交记录和 SHA-256 检查通过，构建后 Git checkout 仍干净。
这些是该设备当时的实际结果，不是未来每版或其他电脑的保证。
完整历史见 [当日更新记录](../update_history/update_2026_10_29.md)，
当前接手状态见 [memory.md](../memory.md)。

## 2026-11-07 本机交付

最新便携包：`C:\Users\lqlhz\Downloads\p4vasp-20261107-221244-a2019291-mbolv7gc`，双击其中的 `p4vasp.exe`；分享时发送旁边的同名 ZIP，接收者完整解压后启动，不能只复制 EXE。

源码提交为 `a2019291c590f6d1ef04da47b7899ace1771074a`，自带 ASE 3.29.0 和 RDKit 2026.09.1，包含频率分析与通用结构导入。构建目录和 Downloads 均通过运行环境／界面／建模检查，另通过随包频率读取与热化学校正检查；这不代替另一台干净电脑的验收。详细检查范围和限制见 [当日更新](../update_history/update_2026_11_07.md)。

ZIP 为 156,976,870 字节；SHA256：`548390f2d818d96b3a617af4ddaf5e77bae6080df76d765dacbd38c36f6c0023`。

# Linux 更新后构建 Windows 版本：操作流程

更新日期：2026-10-29。本文保存在同一 Git 仓库，Linux checkout 中也可查阅。
前提：Windows 已安装 MSYS2 UCRT64 和项目构建依赖，且已建立独立 Git checkout。
首次安装、依赖和构建细节见 [安装指南](../install.md#windows-native-build--windows-原生构建试验)。

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

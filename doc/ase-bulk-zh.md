# 使用ASE生成体相结构

更新日期：2026年11月4日。入口：左侧 **Models → bulk**。

本页在p4vasp中提供参数界面，实际晶体构建调用ASE `ase.build.bulk`，超胞调用ASE重复晶胞功能。结构直接在p4vasp原生窗口预览，可保存POSCAR。首版仅包含bulk，surface仍保留空框架。

## 1. 安装可选依赖

在项目根目录执行：

```bash
bash install/install-ase.sh
```

bulk页面最下方显示按当前项目实际路径生成的安装命令，可选中复制或点击 **Copy command**；在终端粘贴运行即可，无需先切换目录。窗口较矮时向下滚动查看。页面不会自动执行安装。

脚本创建独立 `.venv-ase` 环境并安装已验证的ASE 3.29.0，不替换GTK应用使用的Python。当前维护设备已安装并验证，其他设备需单独执行。也可用 `P4VASP_ASE_PYTHON` 指向已安装兼容ASE的Python解释器。

GUI主进程不导入ASE或其NumPy；点击Build bulk才启动一个计算进程，任务结束即退出，没有常驻后台进程。支持取消，默认30秒超时，关闭页面时取消任务；默认单线程数值计算。

本轮验证范围为Linux／WSL。Windows旧便携包未更新，尚未包含这一页和可选ASE计算环境；macOS与Windows本轮未实测。

## 2. 填写结构参数

| 项目 | 用法 |
| --- | --- |
| Element / formula | 一个结构原型的化学式，例如Cu、Si、NaCl、ZnS、CaF2；不要填写Cu32来表示超胞 |
| Crystal structure | 选择晶体原型，必须与化学式的元素数、配比匹配 |
| Cell type | primitive为原胞，orthorhombic为正交晶胞，cubic为立方晶胞；具体组合需ASE支持 |
| a、b、c | 晶格参数，单位Å；仅当前晶型需要的输入框可编辑 |
| alpha | 菱方晶格夹角，单位度，范围0—120之间，不含端点 |
| u | 纤锌矿结构内部坐标，无量纲，范围0—1之间，不含端点 |
| n1、n2、n3 | 沿生成晶胞三个基矢的重复次数，各为1—100整数；不是始终沿屏幕XYZ方向 |

初始Cu／fcc／a=3.615 Å为可修改的演示输入，不是自动优化后的晶格常数。所有启用的晶格参数必须明确填写，不自动猜测长度。

支持以下13个ASE原型：sc、fcc、bcc、diamond、hcp、bct、rocksalt、zincblende、cesiumchloride、fluorite、wurtzite、orthorhombic、rhombohedral。

hcp、bct、wurtzite需要a和c；orthorhombic需要a、b和c；rhombohedral需要a和alpha，部分结构还依赖ASE已有的基元资料，例如Bi。这里是预定义晶体原型，不是任意化合物的空间群建模器。某些晶型不支持指定的正交／立方晶胞形式，程序会显示ASE错误，不静默替换结构。ASE 3.29.0的tetragonal路径在核验中不支持所需生成方式，首版不列入选项。

总原子数上限为10000，会在创建超胞前校验；不接受无效元素、非有限或非正长度、非整数重复数及退化晶胞。

## 3. 生成和预览

1. 点击 **Build bulk**。
2. 等待完成；期间设置暂时锁定，界面仍可响应，可点击Cancel取消。
3. 查看化学式、原子数、ASE版本、实际晶胞基矢和体积。
4. 点击 **Preview 3D**，在独立原生结构窗口旋转、缩放查看。

例如：Cu，fcc，cubic，a=3.615 Å，重复2×2×2，应得到32个Cu原子，晶胞边长7.23 Å。

预览与气相预览复用会话内辅助窗口，窗口标题与元素显示参数按模型更新。预览不改写当前加载系统，也不通过方向键／Delete编辑当前系统。预览不是原子结构优化；旋转窗口不会旋转保存的科学坐标。

改变任何设置都会使旧结果失效，并禁用预览／保存，需重新Build bulk，避免把新参数与旧结构混淆。

## 4. 保存POSCAR

点击 **Save POSCAR**，填写新文件夹名称与父目录，确认后在新文件夹写入 `POSCAR`。不覆盖已有文件夹，取消不写文件，保存失败显示错误。

本页只生成结构文件，不生成INCAR、KPOINTS或POTCAR，不设置磁矩、自旋、U／J或计算任务。POSCAR按元素分组、使用Direct坐标；没有额外添加固定原子约束。保存后使用Open打开该POSCAR，即可进入现有Show／Build／Move等编辑流程。

预览和保存读取同一份生成结果，不根据当前表单再次偷偷计算。会话结果只暂存于页面内存，离开Models前请先保存。

## 5. 验证范围

本机Linux／X11已验证真实ASE几何（13个原型样例、FCC晶胞与超胞体积／数目、NaCl配比与最近邻距离、HCP与菱方参数）、输入拒绝、跨Python进程POSCAR交接、缺依赖提示、取消／超时回收，以及实际GTK／原生预览和保存弹窗。

检查使用合成模型与临时目录；不代表材料基态结构、DFT收敛或所有用户化合物均已验证。ASE／新NumPy组合在几何测试中可出现弃用提示，现有Resources回归退出仍见cmatrix析构警告，均未作为本次修复成果。完整GTK已知失败套件、其他平台及Windows重新打包未运行。

来源：[ASE晶体构建接口](https://docs.ase-lib.org/ase/build/build.html)。

# p4vasp 近期更新总结与使用说明

整理日期：2026年11月1日。范围：2026年10月13日至11月1日，以当前 `p4vasp-py3` 分支的最终行为为准。历史中途布局与参数方案已合并，不作为当前使用说明。

项目主页：https://github.com/bigbrosci/p4vasp/tree/p4vasp-py3

## 一、结构选择与键盘建模

### 框选、取消和清空

按住 Shift，用鼠标左键拖出矩形，会反转框内原子的选择状态：未选中的变为选中，已选中的取消。框外原子保持原状态；被遮挡原子可以选中，主动隐藏的原子不参与框选。

- 重复框选同一区域，可再次反转选择。
- 拖动过程中按 Esc，取消本次框选并保留原有选择。
- 松开鼠标后按 Esc，清空全部选择，结构窗口保持打开。
- 原有鼠标旋转、空格键切换单原子选择继续保留。

### 按当前视角移动原子

选好原子，调整模型视角，让结构窗口获得键盘焦点，再按上下左右方向键。原子沿当前屏幕方向移动；改变视角后，移动方向随之改变。

默认步长为每次 **0.1 Å**，不随缩放改变。可在原有 Move 面板中调整 Arrow-key step，范围为0.001—10 Å，会话内共享。原来的 Edit → Move atoms 向量移动和复制操作继续保留。

### 围绕所选原子质心旋转

按住 Shift，再按方向键：

| 按键 | 效果 |
| --- | --- |
| Shift＋上／下 | 围绕穿过质心的当前屏幕水平X轴旋转 |
| Shift＋左／右 | 围绕穿过质心的当前屏幕竖直Y轴旋转 |

每次旋转 **5°**，以真实质量加权质心为中心。有效质量缺失时会拒绝旋转，不用几何中心代替。周期副本按原胞原子去重；跨晶胞边界的分子不会自动重新拼接，旋转前应检查当前坐标是否符合预期。

### 删除原子与实时统计

结构窗口左下角显示总元素数目，例如 `Cu:64, C:10, H:20, O:2`；右下角显示当前选中元素及数目。统计按原胞原子计算，不重复计入显示用的周期副本；总数包含隐藏原子。

选中原子后，直接按 Delete 即可删除，原有 Build 中的删除按钮保留。键盘移动、旋转和删除作用于来源系统的初始／Build结构，不编辑最终结构、轨迹、原胞或STM只读视图。修改后仍需按原保存流程保存POSCAR；操作保留适用的晶胞、坐标表示和剩余原子的选择性动力学标记。

## 二、结构显示与图片导出

### 打开结构时自动居中

点击 Show 后，新打开的结构窗口按可见原子范围居中并适配大小，减少模型偏离视野或显示过小的问题。后续仍可手动调整视角、平移和缩放。

### 按当前视角导出

在结构窗口调整构图，进入 Control，点击相机图标 Export PNG，即可预览并导出当前视角。支持球体、球棍、棍状等显示模式，以及尺寸、画质、亮度和材质设置。

默认使用透明背景与哑光材质。导出读取保存时的最新视角、显示帧、隐藏原子和晶胞复制等显示状态；保持窗口构图，已被窗口裁切的部分不会自动恢复。交互窗口保持轻量渲染，精细渲染在导出时执行。

导出的是原子、推断键及晶胞边框，不包含所有屏幕覆盖内容，例如选择标记、箭头和等值面。按距离推断的显示键不能代替化学键级判断。

### 命令行与视角复现

无需打开GUI即可导出PNG，例如：

```bash
bash p4v.sh POSCAR -o top.png
bash p4v.sh POSCAR -o side.png --view side
bash p4v.sh POSCAR -o molecule.png --model ball-stick --no-cell --quality 3
```

同时提供当前视角的复现命令和批量导出方式，便于对多份结构生成相同构图。已有图片默认可覆盖，需保护时使用 `--no-clobber`。视角脚本和快照用于复现展示，不等于完整计算输入或全部VASP参数备份。

详见[图片导出说明](render-cli.md)。

### 保存位置窗口与WSL光标

图片保存位置改为紧凑的文件名／目录选择窗口，按屏幕工作区调整初始尺寸，目录列表可滚动，保留覆盖确认和取消，改善窗口超屏导致按钮无法点击的问题。

Linux原生结构窗口同步GTK光标主题与尺寸，并明确使用普通箭头。WSLg最终显示的物理光标大小仍受系统合成与缩放影响，不能认定所有电脑上的大光标问题均已解决。

## 三、独立的模型入口

左侧原Database入口改为独立 **Models**，顶部排列五个标签：

| 标签 | 当前用途 |
| --- | --- |
| single atom | 选择元素并生成单原子输入文件 |
| gas phase | 从XYZ库或SMILES创建气相结构和输入文件 |
| bulk | 保留框架，尚未填充功能 |
| surface | 保留框架，尚未填充功能 |
| p4vasp data | 查看和编辑元素资料 |

Models和Resources页面隐藏无关的System／Selection栏，切回结构编辑面板时恢复。左侧Commit快捷按钮已移除；历史New快捷入口与保留的新建功能分别处理，未删除全部新建能力。

### 单原子输入生成

进入 single atom，选择周期表中的元素，点击 Generate inputs，填写新文件夹名称与父目录，即可生成：

- **POSCAR**：13×14×15 Å正交晶胞，原子位于晶胞中心。
- **KPOINTS**：Gamma中心1×1×1网格。
- **INCAR**：基于程序内部标准预设，设置 `ISPIN=2`、`ALGO=ALL`、`NELM=500`，不设置 `MAGMOM`。

支持118个元素。输出要求使用新目录，不覆盖已有目录，不生成POTCAR。其他INCAR参数沿用标准预设，使用前仍应按实际计算目的检查，不能把模板视为所有元素的最优计算参数。

### 本地XYZ气相分子库

将分子放入 `data/models/gas_phase/`，按统一XYZ格式保存，刷新气相页面后选择分子，核对电荷、自旋多重度和晶胞，再生成输入。

```text
3
name="Water" charge=0 multiplicity=1 units=angstrom
O 0.000 0.000 0.000
H 0.758 0.000 0.504
H -0.758 0.000 0.504
```

第一行为原子数，第二行为元数据，后续每行是元素符号和以Å为单位的笛卡尔坐标。使用单帧文件；缺少电荷或多重度时需在界面补齐。坐标只做整体居中，不擅自补原子或重排分子。输出INCAR、KPOINTS和POSCAR，不覆盖已有目录。

完整格式见[气相库说明](../data/models/gas_phase/README.md)。

### SMILES生成与初步优化

在 gas phase 中输入SMILES，点击 Build 3D + optimize，程序使用可选RDKit环境生成三维结构、显式补氢，并进行力场初步优化。完成后复用原有三维预览、电荷／自旋设置和输入生成按钮。

安装可选组件：

```bash
bash install/install-rdkit.sh
```

生成流程采用ETKDGv3构象生成，优先MMFF94s，条件合适时使用UFF；支持取消与60秒超时。形式电荷自动填入，**自旋多重度仍需用户确认**。盐、多片段和金属体系等不支持的输入，应改用已有XYZ结构。

生成结果暂存在当前页面内存中，离开Models前应导出POSCAR。力场初步优化不等于DFT优化，也不保证全局最低能构型。气相预览已改用较小的共价半径球，并修正部分C—H显示键缺失的问题，不改变导出的原子坐标。

详见[SMILES气相建模说明](smiles-gas-phase-zh.md)。

### 带电体系只填写Charge

用户输入体系电荷，例如负离子填 `-1`，正离子填 `1`。实际电子数的关系为：

```text
NELECT = 所有原子的POTCAR价电子总数 − Charge
```

由于默认没有POTCAR，程序不能可靠地自动给出NELECT。当前中性模板省略NELECT；带电模板写入 `NELECT = SET_AFTER_POTCAR` 占位及说明。必须在准备好POTCAR后，根据实际ZVAL替换占位，再提交计算，不能直接运行未补全的带电模板。

## 四、元素资料表

在 **Models → p4vasp data** 中查看或编辑资料。表格覆盖118个元素，包含名称、原子序数、质量、半径、RGB三列颜色、Magmom、U和J，单位写入列标题。

RGB使用 **0—255整数**。新增元素颜色参考Jmol配色，部分质量与半径数据参考ASE资料；缺失字段留空，不伪造数值，也不会自动把所有元素填入磁矩或U／J。

保存直接修改程序自带数据文件，包含校验、冲突保护和备份；备份位于 `~/.p4vasp/backups/`。部分缓存需重启后生效。重新安装或更新可能影响自定义文件，修改前应保留副本；个人或工作目录中的元素设置仍可能覆盖程序默认值。资料表参数不会自动成为所有建模任务的计算参数。

## 五、资源导航、常用链接与交流

顶部 **Database → Resources** 现在包含 Databases、Useful tools and links、交流与支持三个标签。

### 在线数据库

使用四列卡片，超过16项自动增加行，当前共18个入口。点击后在网格下方显示网址并复制到剪贴板，用户可粘贴到浏览器；剪贴板不可用时可手动Ctrl+C。启动程序不自动联网抓取数据库内容，访问权限仍由相应网站决定。

| 数据库 | 网址 |
| --- | --- |
| Open Catalyst Project | https://opencatalystproject.org/ |
| ioChem-BD | https://www.iochem-bd.org/ |
| Materials Project | https://materialsproject.org/ |
| CRC Handbook | https://hbcp.chemnetbase.com/ |
| NIST WebBook | https://webbook.nist.gov/chemistry/ |
| NOMAD | https://nomad-lab.eu/ |
| ChemSpider | https://www.chemspider.com/ |
| Catalysis-Hub | https://www.catalysis-hub.org/ |
| OQMD | https://oqmd.org/ |
| AFLOW | https://aflow.org/ |
| Materials Cloud | https://www.materialscloud.org/ |
| NIST JARVIS | https://jarvis.nist.gov/ |
| PubChem | https://pubchem.ncbi.nlm.nih.gov/ |
| COD | https://www.crystallography.net/cod/ |
| ICSD | https://icsd.products.fiz-karlsruhe.de/en |
| CCDC Access Structures | https://www.ccdc.cam.ac.uk/structures/ |
| NIST-JANAF | https://janaf.nist.gov/ |
| The Cambridge Cluster Database | http://www-wales.ch.cam.ac.uk/CCD.html |

### 常用工具与链接

Useful tools and links保留相同的卡片、网址显示和复制操作，当前包括：

| 入口 | 网址 |
| --- | --- |
| VASPwiki | https://vasp.at/wiki/Main_page |
| 大师兄网站 | https://www.bigbrosci.com/zh-cn/latest/ |
| ASE | https://docs.ase-lib.org/ |
| Pymatgen | https://pymatgen.org/ |
| phonopy | https://phonopy.github.io/phonopy/ |
| Cantera | https://cantera.org/ |

### 交流二维码与中文显示

“交流与支持”展示QQ群、微信和公众号二维码。点击可放大、缩放、按100%显示或查看原图；QQ群号 **1131610080** 支持复制。微信展示昵称 **BigBroSci**，不将昵称当作微信号。

用户提供的JPG完整保留，页面只在内存中截取二维码区域和缩放。程序自带开源中文字体，并修复主界面已缓存字体后中文仍显示方框的问题；无需修改系统字体配置。手机扫码和二维码有效期尚未实测。

## 六、安装与日常启动

Linux和macOS使用统一入口：

```bash
git clone -b p4vasp-py3 https://github.com/bigbrosci/p4vasp.git
cd p4vasp
bash install.sh
```

Ubuntu／Debian自动安装依赖并编译；其他Linux依赖系统预先配置；macOS使用Homebrew并准备对应Python环境，需要先具备Homebrew和Xcode命令行工具。

默认安装结束后，打开p4vasp，界面初始化并显示后停留约2秒，再自动退出。终端随后打印安装成功与实际路径对应的别名，例如：

```bash
alias p4v='bash /home/你的用户名/opt/p4vasp/p4v.sh'
```

将安装器实际输出的那一行添加到 `~/.bashrc`，保存后执行：

```bash
source ~/.bashrc
p4v
```

macOS默认zsh应写入 `~/.zshrc` 并执行 `source ~/.zshrc`。安装器不自动修改用户配置。日常 `p4v` 或 `bash p4v.sh` 启动不会两秒后关闭。

无显示环境会明确跳过预览；启动失败不会显示GUI通过。`--no-launch`、`--build-only`、`--deps-only` 保留各自不预览的行为。源码更新包含原生功能时，其他电脑仍需重编译，不能只同步Python文件。

Ubuntu／WSL图形环境需GTK3、PyGObject、Cairo、OpenGL及适当字体；构建依赖由安装脚本处理。现代WSL2通常使用WSLg，无需另外安装整个桌面。此前讨论的系统中文字体等手动补充命令，不代表已全部加入安装脚本或在每台设备安装。

完整说明见[安装指南](../install.md)。

## 七、Windows版本与更新流程

10月29日已建立Windows原生构建、独立便携目录和Git驱动更新流程，并有当时版本的实际构建、运行检查与压缩包校验记录。便携版应整体复制目录，不能只拿走一个EXE。

随后按用户要求暂停Windows新版本打包。**最近增加的键盘建模、模型库、资源导航和交流页等源码功能，不表示已经进入现有Windows便携包。** 重新发布需明确恢复构建，并在Windows重新编译、打包和验收。

流程见[Windows更新操作说明](windows-update-workflow-zh.md)。

## 八、版权与维护说明

关于窗口保留Orest Dubay原版权及原项目网址，明确列出：

- Python2到Python3移植的主要贡献者：Bigbrosci、Whitehare2023。
- 后续 `p4vasp-py3` 维护与新功能开发：Bigbrosci。
- 新贡献的2026年Bigbrosci版权说明。

当前Homepage指向本分支GitHub页面，关于窗口支持换行、滚动和文字复制。原有许可证及源文件许可条款保留，详见[版权与贡献说明](../AUTHORS.md)。

## 九、维护记录与跨设备交接

参考用户指定PFAS项目的文档经验，完善了项目规则、简短接手检查点、按设备记录验证结果，以及迁移时完整核对依赖的流程。保留现有文档分工：项目规则、当前记忆、历史更新和操作指南各司其职，不额外增加重复的状态文件。

换机时需核对Python、GTK／Cairo、原生扩展和资源文件；同步代码不代表目标设备已安装依赖或完成重编译。图片重放还需携带结构快照与视角文件，并更换原设备的绝对路径。重放快照不保存选择性动力学标记，不能当作完整科学输入使用。

## 十、验证范围与仍需跟进的问题

本总结引用各次更新中记录的检查结果，**不是在整理文档时重新运行全部测试**。相关Linux检查包括基础测试、原生选择／键盘回归、实际GTK页面与剪贴板、临时目录输入生成、气相预览、图片导出、字体缓存回归及安装两秒预览等。最近记录的注册面板启动检查为32项，明确排除独立GLUT查看器。

需要保留以下边界：

- Linux通过不代表macOS或Windows全部通过；Windows历史成果与最近未打包源码分开说明。
- 完整GTK资源套件仍有已记录的属性转换问题；独立GLUT k点查看器仍有OpenGL上下文问题。
- 部分测试退出可见既有cmatrix析构／对象释放警告，未作为已修复内容。
- 用户曾报告POSCAR保存／覆盖的偶发疑问，未建立确定原因或宣称修复；保存后应按实际文件核对。
- Build文本实时解析的既有异常仍有历史记录，未认定在本轮修复。
- WSL高分屏光标、手机实际扫码、所有真实模型及完整手动工作流仍需用户环境验收。
- 单原子和气相输入是建模模板，需核对赝势、电子数、自旋、收敛与任务参数；预览或导出成功不能替代VASP科学计算验证。

## 十一、详细记录与后续查阅

- [完整操作指南](interface-guide-zh.md)
- [10月13日更新记录](../update_history/update_2026_10_13.md)
- [10月24日更新记录](../update_history/update_2026_10_24.md)
- [10月28日更新记录](../update_history/update_2026_10_28.md)
- [10月29日更新记录](../update_history/update_2026_10_29.md)
- [10月31日更新记录](../update_history/update_2026_10_31.md)
- [11月1日更新记录](../update_history/update_2026_11_01.md)

本文为功能汇总与使用说明；当前维护状态仍以项目memory和各项更新证据为准。

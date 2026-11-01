# p4vasp maintenance memory

Last updated: 2026-11-01. This is a repository navigation and handoff document. Verify the current source and Git state before acting; historical test results are not current guarantees.

## Useful tools 预留标签（2026-11-01）

- 按用户要求，ResourceHub 在 p4vasp data 右侧新增 Useful tools 空标签页，后续软件／GitHub名单由用户提供，未自行填内容。
- 本机实际GTK检查标签顺序、切换及空初始状态通过，700×480绘制截图已查看；退出仍见既有cmatrix析构警告。本次未重跑全套测试或其他平台，Windows打包暂停。

## Show 原子计数与 Delete 快捷删除（2026-11-01）

- 用户要求结构弹窗左下角显示各元素原子数，并用 Delete 直接删选择、Build 按钮不变。`src/VisWindow.cpp` 在原生GL最后绘制屏幕坐标统计，源info按元素合并，不重复计周期副本，包含隐藏原子，长行折行／空结构Atoms:0；旋转缩放不改变位置。
- 同文件捕获无修饰 Delete，将去重原胞选择及原子数快照以BE_ATOM_MOVE index2发给现有Python分发，无新绑定接口。`atom_movement.py delete_selected/handle_event` 只改来源窗口初始／Build结构，校验索引和原子数以拒绝过期重复请求；清空选择、刷新同系统面板，保留相机／晶胞／坐标表示／剩余标记。只读最终／轨迹／原胞／STM及气相预览不改。Builder源码和原删除入口未改，实际原按钮也已验证。
- 当前Linux已完整原生重编译。3项删除数据测试、扩展原生框选／方向／Delete回归、真实Show/Builder集成（含Cu重复块计数、删除前后HUD、空结构、去重／过期／最终只读、其他系统不更新、相机保留、POSCAR标记）通过；三张原生截图已查看。7移动旋转、原生居中、GTK/原生图片导出、57基础、32启动通过。原生独立测试见Fontconfig提示，已有ODP释放警告仍未处理；不代表完整GTK或其他平台通过。
- 详细记录见 update_history/update_2026_11_01.md，操作指南已补充。本机重启即可；其他源码设备需重编译，Windows打包仍暂停。既有未跟踪Fe_single_atom目录保留未发布。

## 气相 C–H 显示键修复（2026-10-31）

- 用户截图显示乙醇 C–C／C–O 可见而 C–H 缺失。原生距离判键默认因子1.0，C0.77+H0.32=1.09 Å，略小于部分优化C–H键长；气相独立预览设置setBondFactor(1.2)，保留0.5倍共价半径球，不改全局默认或输出结构。
- 实际XYZ／SMILES GTK和原生回归通过。用真实原生半径及getBondFactor检查乙醇应有8对连接（5个C–H），原生截图已查看，C–H均显示；未将此当作化学键级识别。此次未跑全套测试或其他平台，Windows打包暂停。

## 气相预览球半径（2026-10-31）

- 用户报告气相球体过大，要求使用原子半径而非范德华半径。`gtk3/gas_phase.py molecular_atomtypes` 深复制默认 AtomInfo，预览 radius 改为 covalent，窗口球缩放0.5；缺失正共价半径时raw半径0.7 Å（最终球0.35 Å）。XYZ和SMILES共用，不改颜色、判键共价半径、全局缓存／资料或输出结构。
- 本机实际X11 GTK／原生XYZ和SMILES流程通过；核对原生氧球取共价半径、缩放0.5、全局半径未变及Og缺值显示回退，原生截图已查看。此次未重跑全套基础／启动、其他平台或科学计算；Windows打包继续暂停。

## gas phase SMILES 建模（2026-10-31，当前状态）

- 用户授权新增SMILES生成及初步优化，XYZ库保留。gas phase 增加 SMILES 输入、Build 3D + optimize、Cancel；完成后在同一列表加入临时 [SMILES] 条目并自动三维预览，复用已有电荷／自旋／晶胞／Generate inputs。形式电荷自动填入，多重度始终留空待确认；刷新保留临时结构及人工填写，重新生成重置确认。结构仅在当前页内存，离开Models前应导出POSCAR，不自动写XYZ库。
- `smiles_builder.py`：RDKit ETKDGv3、固定seed20261031、最多8候选、MMFF94s优先／UFF参数完整时回退、1000步，选收敛候选中最低力场能量，显式补氢。多片段／盐／金属与超范围元素要求XYZ；潜在未指定立体信息提示只是一种构型，显式立体信息保持。100重原子／300总原子／2048字符限制，失败不生成假成功结果；不是DFT或全局最低能保证。
- 依赖为独立可选 `.venv-smiles`，脚本 `install/install-rdkit.sh`，也可设置 P4VASP_SMILES_PYTHON。仅用户点击后启动一个隔离单线程计算进程，GUI线程只调度；60秒超时／Cancel／页面销毁均终止回收。主GUI不导入RDKit/其NumPy。当前Linux实际安装：可选Python3.14.6、RDKit2026.09.1；GUI /usr/bin/python3 为3.14.4，不证明其他设备环境可用。
- Molecule增加可选内存来源与provenance，原XYZ仍检查文件变化；生成结构导出记录SMILES、方法、版本、seed、力场能量／警示。NELECT带电占位沿用，不增加伪电子数。已有单原子／XYZ行为保持。
- 验证：6项真实化学专项（显式H、收敛／重现、实际3D手性、形式电荷、UFF回退、失败拒绝）、4项隔离worker专项（真实POSCAR／带电模板交接、取消／超时回收）、实际X11 GTK/原生端到端（响应计时器、预览、真实保存弹窗、同SMILES重复生成、刷新、错误／取消保留、页销毁）、原XYZ GUI、5气相／5单原子、57基础与32启动通过。缺RDKit的系统Python实际返回安装说明；截图已查看。未做DFT、完整GTK套件或其他平台；Windows打包仍暂停。
- 使用与可选依赖见 doc/smiles-gas-phase-zh.md、install.md。本任务开始前已有未跟踪 data/models/gas_phase/Fe_single_atom/，未修改或纳入提交；不要把它当成本次测试产物。

## Charge 输入与带电 INCAR 模板（2026-10-31，当前补充）

- 用户明确默认无 POTCAR，只需在 INCAR 加 NELECT 并告知用法。移除气相界面手填 NELECT，Charge 接受带符号整数。带电导出不再受缺 NELECT 阻挡，写入活动占位 `NELECT = SET_AFTER_POTCAR`、ZVAL总和减Charge公式及正负号／自旋核对说明；保存弹窗和状态提示补全后运行。中性不写NELECT。不提供猜测数值，带电输出为待补全模板，不是可直接运行的完整INCAR。
- 5项气相数据专项及实际X11 GTK/原生完整导出回归通过，检查±1公式／占位、去除NELECT输入、真实保存弹窗与提醒；截图已查看。本次未重跑全套基础／启动或其他平台。指南与库README已同步；下方早期“必须手填NELECT”已被此补充替代。Windows打包暂停。

## gas phase 本地 XYZ 库（2026-10-31，当前状态）

- 用户确认本地文件接口。新增 `data/models/gas_phase/`（water／oxygen_triplet 示例及 README），`gas_phase_inputs.py` 严格解析单帧 XYZ，第二行支持 name/charge/multiplicity/units；只允许 Å、有限坐标及元素符号，缺电荷／多重度必须填写，错误按文件行号展示。Models 的 gas phase 页使用 `gtk3/gas_phase.py`，进入自动扫描，另有 Refresh／打开目录；无后台扫描进程或联网服务。bulk／surface 仍空，名称／SMILES 转换未实现。
- 可预览、编辑 charge/multiplicity/NELECT/三向晶胞，再经复用的紧凑目录弹窗导出新目录三文件。POSCAR 按元素分组、只整体平移包围盒居中，片段间几何保持；默认晶胞各方向 max(13/14/15, ceil(跨度+12 Å))。Gamma 1×1×1。INCAR 用内部 Standard，覆盖 ISPIN2、ISMEAR0、SIGMA0.01、NUPDOWN=multiplicity−1；不设MAGMOM／自动U/J，不继承SOC／非共线。中性NELECT省略，带电必须按实际POTCAR价电子提供整数NELECT并检查自旋奇偶，不按原子序数猜。生成前复核XYZ语义未变；不覆盖旧目录，写失败清理。
- 预览是会话共用的单独原生窗口，不修改当前系统。`p4v.py idle_func` 优先消费预览的选择、移动和窗口事件，防止影响主系统或关闭 Models；窗口隐藏先 VisSync，保持绘图对象存活。测试发现直接 StructureWindow.hide 后丢引用会在异步 FL_HIDE 中崩溃，改为会话持有／隐藏并同步后，反复预览、关闭、重开和页销毁通过；未声称修复原有全局 StructureWindow.hide。
- 本机 Linux：5 项气相数据专项、5 项单原子、6 项 INCAR、57 基础、32 applet 启动通过。实际 X11 GTK／原生测试覆盖坏文件行、缺元数据、刷新保留人工编辑、真实三维加载、合成预览选择／关闭事件路由、带电导出（真实保存弹窗）、取消及关闭重开／销毁；截图已查看。预览事件测试最初误用未暴露SWIG构造器，改用模拟事件引用真实窗口核验；不作为应用问题。未做VASP能量／磁态验证、其他平台或完整GTK套件，Windows打包仍暂停。
- 格式与边界见 `data/models/gas_phase/README.md`、操作指南气相章节；带电修正／赝势仍由用户核对。接手下一步由用户实际分子反馈决定，不自动开发 bulk/surface 或恢复 Windows 打包。

## single atom 输入生成（2026-10-31，当前任务已完成）

- Models 第一页现为 118 元素周期表：选择后高亮，Generate inputs 打开紧凑目录弹窗，指定新文件夹名称及父目录，生成 INCAR／KPOINTS／POSCAR；后三页仍空，系统／选择栏仍隐藏。`gtk3/single_atom.py` 承担 UI，`single_atom_inputs.py` 承担内容和写入。复用已有 FolderDialog/fit_dialog，不恢复 Windows 打包。
- 用户澄清以 p4vasp INCAR 功能为准。助手找到了外部 qrob/actions_py/in.py 包装及 brain/incar.py，其基础参数与仓库 presets.json 当前一致；最终实现直接用内部 load_presets/generate_incar 全部 Standard，覆盖 ISPIN=2、ALGO=ALL、NELM=500，删除任何基础 MAGMOM，不使用元素磁矩/U/J，不额外套用 Task。SYSTEM 标注元素，其他基础参数保留，包括现有 NSW 等；不依赖或执行外部脚本。
- POSCAR 正交 13×14×15 Å，单元素单原子 Direct 0.5/0.5/0.5；KPOINTS 为 Gamma 1×1×1、零偏移。要求新目录，不覆盖既有目录；中途写入失败清理本次已写内容，取消不写。未修改当前系统或源预设，不生成 POTCAR 或提交计算。
- 本机 Linux：5 项新数据专项通过（全部118元素中心／晶胞／计数、INCAR基础继承及覆盖／无MAGMOM、KPOINTS、路径保护／同名不覆盖／中途失败清理），6 项原 INCAR 生成测试、57 基础、32 applet 启动通过。实际 X11 GTK 选择切换、高亮、按钮状态、弹窗创建/取消及动作接线通过，Models 主界面和紧凑目录弹窗截图已查看。仅临时目录测试，不是 VASP 计算验证；其他平台／完整 GTK 套件未测。
- 使用说明见 doc/interface-guide-zh.md 单原子输入生成。后续 gas phase／bulk／surface 等待用户指定；本任务不授权自动生成其他模型或恢复 Windows 打包。

## Models 改为顶部横向标签（2026-10-31）

- 用户要求 Models 与 Resources 的标签布局一致，已将原 2×2 空框改为 Gtk.Notebook，顶部横排 single atom、gas phase、bulk、surface，默认 single atom，内容全部为空。Glade 提供 models_host，ModelsApplet.initUI 创建四页；系统／选择栏继续隐藏。
- 本机实际 Frame 专项验证四页标题／默认页／切换／空内容和系统栏显隐通过，900×640 绘制截图已查看。本次仅布局调整，未重跑全套应用测试或其他平台。后续模型内容仍等待用户指定，Windows 打包暂停。

## Database 隐藏系统／选择栏（2026-10-31）

- 后续用户确认 Models 也需隐藏，已补齐 ModelsApplet 显示策略；实际 Frame 的 Models 隐藏／show_all 保护／切回 Builder 恢复专项通过，900×640 四空框截图已查看。本次未重复全套测试。

- 用户要求删除 Database 页面顶部 SYSTEM／SELECTION。ResourceHub 和 ModelsApplet 均设置 `show_system_selection=False`，`p4v.py Frame.updateContextControls` 根据当前嵌入面板控制 frame.glade 的 table1，Database 资源页及 Models 页隐藏两行，切回 Builder 等嵌入编辑页恢复；设置 no_show_all 防止父级 show_all 再显示，嵌入／外置切换也同步。
- 本机实际 Frame 检查 Database 隐藏、show_all 后仍隐藏、切到 Builder 恢复均通过，900×640 绘制截图已查看；57 基础和 32 applet 启动通过。首次夹具选用默认外置 Lattice，未真正替换主面板，改为嵌入 Builder 后验证；未将此误报为应用问题。其他平台／完整 GTK 套件未测，Windows 打包继续暂停。

## 完整元素资料与表内单位（2026-10-31，当前状态）

- 后续按用户要求恢复列标题单位：mass (u)、radii (Å)、R/G/B (0–255)、Magmom (μB)、U/J (eV)，删除表格外单位段。表格已扩为 H–Og 共 118 行；替代下方早期 36 行记录。缺失字段可留空、补填或清空，不填零；RGB 仍为 0–255 整数。
- 新程序默认资料为 `data/resources/elements.json`：已有 XML 36 元素原值迁入，补充来自 ASE 3.29.0 的质量、vdw_radii、jmol_colors、covalent_radii；118 项质量、62 项显示半径、109 套颜色、96 项共价半径。ASE 的缺失／dummy 共价半径已转 null。源归档 SHA-256、许可与维护导入脚本均保留，不增加 ASE 运行依赖。
- `element_data.py` 表格保存改写新 JSON，与 INCAR JSON 继续用备份／校验／冲突／回滚；旧 atomtypes.xml 不改，数字占位保留。`util.getAtomtypes` 在基础 XML 后合并新资料，再应用个人／工作目录 XML；`render_cli.atom_styles` 同样读新资料。运行时空质量为未知，空半径有 1 Å 显示回退，空 RGB 通道用白色分量，空共价半径为 0（不据此判键）；这些回退不写入科学资料。已有结构不自动改写。
- 本机 Linux：9 项元素专项（含 118 行／缺失、补填清空、原值保留、RGB、双文件失败回滚、实际 AtomInfo／图片样式加载、个人覆盖顺序）、5 项资源测试、6 项渲染、7 项平移旋转、57 基础、32 applet 启动通过。实际 X11 GTK 118 行编辑保存及头尾截图通过；修正了 XML 惰性数组不能 append 的补充加载问题。仍见既有 ODP／cmatrix 退出警告，未声称修复。
- 当前设备验证不代表其他平台；完整 GTK 套件、其他设备和用户真实模型未测，Windows 打包暂停。操作、同位素质量与数据来源见 `data/resources/README.md`。更新安装时须保留新 JSON 与相关 helper，运行默认值改变需重启。

## 数据库卡片仅显示名称（2026-10-31）

- 用户要求去掉 OQ／OQMD 等重复缩写，在线卡片现仅显示网站名称；已移除缩写标签和目录 badge 字段，4×4 排列及下方网址展示／复制保留。当前指南已同步。
- 本机实际 X11 GTK 集成和 5 项资源测试通过，640×480 绘制截图已查看。未重跑全套测试或其他平台；既有退出析构警告仍在。

## 元素表 RGB 改为 0–255（2026-10-31）

- 用户要求 RGB 用 255 形式，表格显示与编辑已改为 0–255 整数，单位提示同步。内部 XML 仍为 0–1，保存仅转换实际修改的通道，未编辑的原始颜色精度保留；读入按 255 倍四舍五入显示。
- 本机 5 项元素数据专项及实际 X11 GTK 集成通过，截图已查看。覆盖 0／128／255 转换往返、拒绝越界和小数、编辑其他字段不改变 RGB 原始精度。未重跑全套应用测试、未改生产数据、其他平台未测；既有退出析构警告仍在，Windows 打包暂停。

## 在线网址显示与复制（2026-10-31）

- ResourceHub 的在线网格下方增加固定网址框和状态提示，点击卡片更新并选中链接，同时写入系统 CLIPBOARD；剪贴板异常时提示 Ctrl+C 手动复制，不再自动开浏览器。4×4 卡片与元素表保留。
- 本机 X11 GTK 集成通过：连续选择两网站、实际剪贴板读回与显示一致、模拟剪贴板失败仍可见 URL、原元素表编辑保存回归；640×480 绘制截图已查看。退出仍有已有 cmatrix.Vector 析构警告。未验证 Windows/WSLg 跨主机剪贴板或其他平台；未重跑全套基础／启动测试，Windows 打包继续暂停。

## p4vasp data 元素表（2026-10-31）

- 后续按用户要求移除表格底部 INCAR presets／Website catalog 两按钮；实际 GTK 显示和原编辑保存集成再次通过，截图已查看。仅删入口，数据文件保留。

- 后续按用户要求将列标题简化为 Magmom、U、J，并在表格上方增加独立单位说明：mass=u、radii=Å、Magmom=μB、U/J=eV，原子序数与 RGB 无量纲，Name 为元素符号。实际 GTK 绘制及原集成检查、4 项数据专项再次通过；640×480 中单位说明与按钮可见。

- 用户要求将内部资料卡片改为表格，已由 `gtk3/element_table.py` 展示 `element_data.py` 合并的 36 个已有真实元素，按原子序数排序。10 列：Name、atomic number、mass、radii、R、G、B、Magmom（磁矩）、U、J；前两列只读，其他列双击编辑／Enter／Save。RGB 表格为 0–255 整数（内部 0–1），磁矩可负，空白磁矩／U／J 表示无设置；保留共价半径、数字占位和未显示的元素默认值。无新增元素或填补科学数据。
- ResourceHub 的 p4vasp data 标签页现在直接为表格，底部的 INCAR presets／Website catalog 按钮已按后续要求移除，保留表格 Save／Reload。双源保存有备份、校验、冲突检查和失败回滚；回滚失败明确报需手工恢复，不保证多文件断电事务。Reload 询问未保存修改；切换 applet／关闭前需先保存。重启应用默认值，Windows 打包仍暂停。
- 本机 Linux：4 项合并表专项、5 项原资源专项、实际 X11 GTK 表格修改／保存／非法值拒绝和绘制截图通过，57 基础、32 applet 启动通过。GUI 初次夹具漏拦已绑定错误回调导致模态等待，停止后修正夹具并通过；不是应用保存失败。退出仍见已有 cmatrix.Vector 析构警告。未写生产数据、未测其他平台和完整 GTK 套件。详细记录见当日更新。

## Models 模型库空框架（2026-10-31）

- 用户要求将 Database 下拉菜单 Commit 换成 Models；`CommitApplet.menupath=None` 仅隐藏菜单项，工具栏 Commit 保留。新增注册 `ModelsApplet.py` 和 `data/glade2/models.glade`，后续已改为顶部四个空标签页：single atom、gas phase、bulk、surface，不填内容或添加建模操作。Resources 保留。
- 本机 Linux GTK 实际启动及 640×400 绘制检查通过，四框标题、空内容和可见尺寸已核对；57 基础测试和 32 applet 启动通过。界面专项退出仍见已有 cmatrix.Vector 析构警告。其他平台未测，Windows 打包继续暂停；后续内容等待用户指示。详见当日更新记录。

## 数据库资源导航（2026-10-31）

- 已按用户最终确认的 16 个网站实现四列四行在线导航，入口为工具栏 Database／菜单 Database → Resources，名称缩写图标，后续按用户要求改为点击后在网格下方显示网址并自动复制剪贴板，不自动打开浏览器。`data/resources/websites.json` 保存名单与网址；程序启动不联网获取数据。
- `ResourceHubApplet.py` 提供在线／内部两个标签页和文本编辑器；六个内部卡片对应 `atomtypes.xml`、`incar/presets.json`、网站目录三个真实文件。按用户选择直接修改程序文件；`resource_data.py` 负责校验、外部修改冲突保护、备份到 `~/.p4vasp/backups/` 和原子替换，错误不降级成用户覆盖。网站保存刷新；元素／INCAR 缓存重启生效。旧 Query 保留为 LegacyDBApplet、Commit 未改。
- 本机 Linux：5 项资源专项、实际 GTK 面板 4×4／六卡片／模拟浏览器派发／临时文件编辑保存校验备份、57 基础、31 applet 启动通过，640×480 绘制截图已查看。GUI 测试退出有 cmatrix.Vector 析构警告，未修复；未逐站打开真实浏览器，未验证其他平台或完整 GTK 套件。未修改实际元素／INCAR 数据。Windows 打包继续暂停。
- 操作与限制见 `data/resources/README.md` 和 `doc/interface-guide-zh.md`；元素表只有 48 条含占位记录，不冒充完整周期表。重装可能覆盖直接修改；已有个人／工作目录元素表仍可能覆盖默认值。下一步由用户实际使用反馈；不自动恢复 Windows 打包。

## 当前视角方向键平移与质心旋转（2026-10-31）

- 后续新增 Shift＋方向键围绕真实质量加权质心旋转，每次固定 5°；上下绕当前屏幕水平 X 轴，左右绕竖直 Y 轴，采用右手规则，上/左为负、下/右为正。仍仅编辑来源窗口的初始／Build 结构，普通箭头平移保留；状态栏显示质心。质量优先取结构，缺失查元素表，不可用时拒绝编辑；不做周期分子自动重构，周期重复编号仅计算一次。
- 复用 BE_ATOM_MOVE 的 index 区分平移/旋转，无新增公开绑定接口；本机 Linux 再次重编译。坐标专项已扩展到 7 项，含不等质量质心、5°、逆旋转、距离/标记/晶胞保留、单原子与缺质量保护；原生测试覆盖两种键盘模式在多视角/透视/缩放下的方向和快照。实际 GTK 合成模型旋转/保存及新提示布局通过，57 基础、31 启动再次通过。读取质量表时见已有 ODP 释放警告，不据此认定该问题已修复；用户真实模型及其他平台未验证。Windows 构建继续暂停。

- 用户要求保留原 Move／Copy，新增选原子、调整视角后用方向键沿屏幕水平/竖直方向移动；确认默认 0.1 Å，可调整。实现只在原生结构窗口普通方向键按下、无修饰键/无鼠标拖动且有选择时发请求。
- `src/VisWindow.cpp` 捕获按键瞬间相机的屏幕方向及去重原胞原子编号；`VisBackEvent` 增加 BE_ATOM_MOVE 和快照载荷，经 p4v.py 事件队列交给 `lib/p4vasp/atom_movement.py`。Python 按来源窗口定位所属初始结构，更新并刷新同系统面板，最终/轨迹/原胞/STM 视图不编辑。保留相机、选择、晶胞、原坐标模式/比例和选择性动力学标记。原向量按钮实现未改。
- MoveApplet 在 moveapplet.glade 的现有 vbox 中加入 Arrow-key step (Å)，默认 0.1，范围 0.001–10 Å，当前会话共享。相机逆旋转决定方向，步长不受缩放/透视影响。操作指南新增对应步骤。
- 本机 Linux 原生构建及 SWIG 绑定已更新（本机 SWIG 4.4.0，仓库此前生成件标记 4.4.1，完整再生成导致生成文件差异较大）。3 项坐标专项含直接/笛卡尔及 4 类比例、重复编号、保存标记；扩展原生回归含四方向、多视角/任意旋转、缩放/透视、周期去重、选择和方向快照、空选择/修饰键，以及原框选/旋转/Esc；均通过。真实 GTK Move 面板步长绑定、所属结构更新、选择/相机保留、只读最终视图和保存重读检查通过，面板已绘制检查；57 个基础测试、31 个 applet 启动通过。
- 测试基于合成结构；完整人工操作、完整 GTK 已知失败套件和其他平台未重测。用户需关闭旧进程再启动。Windows 打包继续暂停，不生成新版 EXE。详细记录见 [October 31](update_history/update_2026_10_31.md)。

## 当日收尾与下次接手（2026-10-29）

- 今天已完成 Windows 开发/便携构建与 Git 更新流程、中文操作指南、桌面公众号长短稿，以及 PNG 保存位置窗口的源码修复。详细证据见 [当日更新记录](update_history/update_2026_10_29.md)，不要把各阶段测试计数合并或记为新的测试结果。
- 最后代码提交：`eedbf98`（紧凑图片保存窗口）、`6cd66f1`（WSL 进程内光标偏好与 Linux 普通箭头），均已发布；本机 Linux 原生扩展已重编译。用户随后认为大鼠标可能是电脑 WSL 环境问题，这是用户判断，根因未确认；未反馈重启后是否改善，不能记为已解决。
- Windows 打包按用户要求继续暂缓。最近已验证的更新流程产物仍来自 `877fb28`，不含最后两项修复；`eedbf98` 的中断构建已标记未验证，不可当作新版交付。旧成功便携版保留。未经用户重新授权，不恢复打包或修改系统鼠标/桌面设置。
- 下次“开工”先做有限只读检查，报告上述边界；根据用户意图确认 Linux 保存窗口和重启后的光标实际效果，或继续 Windows 构建。干净 Windows 设备验收、签名/安装器、已知 GTK 属性/解析及潜在保存问题仍未完成。
- 本次收尾只补记忆和历史，未运行新的应用测试、重编译或启动后台任务。

## WSL 结构窗口鼠标检查点（2026-10-29）

- 用户确认大鼠标发生在 Linux/WSL 版，要求先处理该问题、暂缓 Windows 打包。已停止上一轮 Windows updater/PyInstaller 进程，未完成目录 `p4vasp-20261029-232315-eedbf98c-fnyq8wqg` 标为中断且未验证，旧成功版本保留；本任务不继续生成 Windows 包。
- 用户截图显示视觉上明显放大的箭头；助手当前实测 GTK 偏好 Adwaita/24、显示缩放 2，Xcursor 默认名义尺寸 16；现有结构窗口及测试窗口的 X11 光标图像为 24×24，未独立复现截图中的物理放大。相似 WSLg 上游报告仅作线索，不能确认本次根因。
- `lib/p4vasp/gui_environment.py` 在 WSL 中按 GTK 偏好设置本进程 XCURSOR_SIZE/THEME（保留用户显式设置），由 `Frame.init3d` 在原生初始化前调用；`src/VisFLWindow.cpp` 在 Linux 的 SHOW/ENTER 事件明确选择箭头。已完成本机 Linux 原生重编译，不改系统设置。用户正在运行的旧进程须重启；最终屏幕效果待用户反馈，不能宣称视觉问题完全修复。
- 本次证据：4 项配置测试、实际 Frame.init3d 设置检查、生产窗口普通箭头 24×24 测量、原生框选/旋转/Escape 回归、57 个基础测试和 31 个 GTK applet 启动通过。未重跑完整 GTK/Windows/macOS；未验证所有缩放/显示器。操作说明补充于 doc/interface-guide-zh.md。

## PNG 保存位置窗口修复（2026-10-29）

- 用户截图报告默认 GTK 文件选择窗口超出屏幕，无法点按钮。`ExportImageDialog.choose_file` 已改用 `lib/p4vasp/gtk3/file_dialogs.py` 的紧凑 Filename/Folder/Browse 窗口，初始尺寸按父窗口所在显示器工作区调整，目录列表滚动；文件名补全、目录验证、覆盖确认和取消保留，导出面板记忆目录。
- Windows 源码专项 5 项在普通及两倍 GTK 缩放通过，640×480 工作区内按钮分配已检查，已查看保存/浏览窗口实际绘制截图。Linux 显示外沙箱专项 5 项及原有 native/GTK 导出集成通过，57 个基础测试通过；最初沙箱内 GUI 因显示不可用跳过，未将其记为通过。macOS、全套 GTK 及完整人工工作流未重测。
- 冻结版诊断补充实际保存窗口/目录浏览器及操作按钮检查。源码修复已发布；其后 Windows 打包因用户要求暂缓而中断，未完成结果不得当成成功版本。旧便携版不会自动得到此改动；待用户重新授权继续打包。

## 公众号汇总稿交付（2026-10-29）

- 按后续要求另存约 1800 字的特色与使用精简稿到 `$DES/p4vasp_更新特色与使用方法_公众号精简版.md`，保留原长稿。重点为框选、居中、当前视角导出、批量复现、Windows 双击及更新命令；仅桌面交付，未上传文章正文，未重跑应用测试。
- 用户要求整理 10 月 13 日至 29 日全部更新为中文 Markdown，已按 13/24/28/29 日更新记录与当前记忆整理，保存到本机 `$DES`（Windows 桌面）的 `p4vasp_2026年10月13日至29日更新汇总_公众号稿.md`。正文采用最终行为，区分修复、新能力、维护流程及未解决/未验证项；未将 10 月 12 日以前的改动算成本期新增。
- 文章草稿仅在用户桌面交付，不纳入仓库或发布到公众号；核对来源、中文内容、UTF-8 和桌面副本逐字节一致。本次未改应用、未重跑测试或构建，文中验证均引用历史记录。

## Windows 原生构建检查点（2026-10-29）

- 日常使用入口已整理为 [Linux → Windows 更新操作流程](doc/windows-update-workflow-zh.md)，同一仓库的 Linux checkout 可直接查阅；install.md 已添加导航。覆盖 Linux 发布、UCRT64 命令、成功/失败判断、输出位置、人工验收及旧版回退。本次仅补文档，未重新构建或改变既有 ZIP；先前构建结果仍为历史证据。
- Git 更新配置：已独立克隆 `origin/p4vasp-py3` 到 Windows `/home/lqlhz/p4vasp-checkout`，旧 `/home/lqlhz/p4vasp-windows` 和 Downloads 便携版保留。新增 `install/update-windows.sh` / `install/windows/update_build.py`，干净仓库 fast-forward 后从提交创建隔离构建副本，检查通过才生成版本目录/ZIP/SHA256；不覆盖旧版。7 个保护/验证器测试通过。修正 GUI 入口和 Windows 子进程退出码传递后，首次完整成功构建提交 `877fb28`，runtime/GUI、ZIP CRC/SHA256 及构建后干净 Git 状态均核验通过。成功目录为 `dist/windows-releases/p4vasp-20261029-003727-877fb283-9k24i9wj`（相对新 Windows checkout）。此前失败目录保留失败标记，未覆盖旧版。用法见 install.md 的 Update from Git。
- 最新任务已推进至便携目录：用户实际双击开发启动器成功（用户反馈，非助手复测）。新增 `install/package-windows.sh`、`install/windows/p4vasp.spec`/runtime hook/README；PyInstaller 6.22.3 生成 GUI/console 两个 EXE，共享 `_internal`。本机交付目录 `C:\Users\lqlhz\Downloads\p4vasp-portable-20261029`；整目录 ZIP 同级保存。仍未签名/制作安装器，须在干净 Windows 设备验收。
- 本次助手独立核验：移出 MSYS2 目录并清空开发环境变量后，冻结 EXE 导入所有注册 applet 模块、加载 40 个资源（本机无 property errors）、原生绘制/截图、PNG、POSCAR 标记、直接 CLI preset 重放通过；GUI 截图已检查，运行中 DLL 清单无 `C:\msys64` 来源。报告/截图和模块清单位于交付目录同级 `-checks/`，未发布用户数据。未在冻结版重跑 31 个 applet 的逐项启动或完整 GTK 回归。
- `lib/p4vasp/windows_check.py` 提供显式 `--check-runtime DIR` / `--check-gui DIR` 合成诊断，进程直接退出，不验证正常 teardown。Windows 重放改为引用本机 Python/冻结版 console EXE 的 PowerShell `.ps1`，修复默认保存脚本对 Bash/fchmod 的依赖；UTF-8 BOM 和单引号转义。7 个 recipe、14 个 CLI、57 个基础测试在 Linux 本次通过。Windows `.ps1` 最初被设备策略拒绝；随后用户报告设置 CurrentUser RemoteSigned，助手实际执行原有脚本成功，含中文/单引号/与号/百分号的路径和 `--size 160x120` 参数通过，输出 PNG 尺寸已核验。未改应用代码或由助手修改策略；直接 EXE preset 重放也通过。下一步用户双击便携 EXE，然后在无 Python/GTK/MSYS2 的 Windows 设备验证，最后再制作安装器。
- 最新进展：用户报告关闭了拦截功能后，助手重试原有 `.pyd` 导入成功，未重编译或修改安全策略。Windows 下 57 个基础测试和 31 个 GTK applet 启动检查通过；合成分子原生窗口实际绘制、相机快照、当前视角 PNG 导出、POSCAR 保存重读通过。主界面加载合成 POSCAR 成功，主界面与原生截图均已检查。
- 开发启动器位于独立目录 `C:\msys64\home\lqlhz\p4vasp-windows\p4v-windows.cmd`，`--help` 通过，随后用户报告双击无错误。该目录依赖现有 MSYS2，便携版进展见本节顶部；完整退出、真实手动编辑流程、其他设备及干净机仍未验证。原策略拦截记录保留在下文作为历史，已不阻碍本次导入。
- 当前任务：Windows 双击应用的可行性验证；用户要求节省调用。用户已安装 MSYS2 并报告 GTK3 最小窗口正常；不是 p4vasp GUI 验收。
- 助手实测：通过 WSL 调用 Windows 工具链；Python 3.14.9、GCC 16.2.0、SWIG 4.5.1、FLTK 1.4.5。独立源码快照在本机 `C:\msys64\home\lqlhz\p4vasp-windows`，非 Git checkout，不含后续提交的自动更新；Linux 构建产物未替换。
- 新入口 `install/build-windows-py3.sh` 复用共享构建脚本，Windows 使用 glu32/opengl32 并重新生成 SWIG wrapper；开发启动器 `p4v-windows.cmd` 尚未运行验证，不是独立 EXE。
- 实际编译/链接成功，得到 `_cp4vasp.cp314-mingw_x86_64_ucrt_gnu.pyd`。导入被 Windows Application Control 拦截；CodeIntegrity 3077/3033 事件明确指向该文件的签名级别/策略要求。日志在独立目录 `windows-build.log`；没有绕过或修改系统策略。
- 最初受阻时的下一步为管理员确认签名/批准方式；随后验证进展见本节顶部。对外分发时仍需验证签名和安全策略兼容性，不能把本机设置变化当作已解决发布问题。详见 [Windows 构建](install.md#windows-native-build--windows-原生构建试验) 和 [October 29](update_history/update_2026_10_29.md)。

## 接手检查点（2026-10-28）

- 当前任务：借鉴 PFAS 的交接文档实践；本次只改项目规则、记忆、安装指南和更新记录，不改应用实现。
- 已完成：补充简短检查点、完整依赖迁移和展示/科学输入边界；换机操作见 [install.md](install.md#changing-computers--换机接续)，详细证据见 [October 28](update_history/update_2026_10_28.md)。现有最近实现及其历史测试仍见下文 October 24 记录。
- 本次只读核对：当前分支 `p4vasp-py3`，origin 为约定 GitHub 地址，修改前工作树干净。读取了用户指定 PFAS 路径的交接/规则文档及状态、命令索引、记忆相关摘要；没有检查其模拟数据或执行其任务。
- 未验证：本次没有运行 p4vasp GUI、重编译或复测科学功能；历史 GTK 属性错误、潜在 POSCAR 保存报告等仍未解决，见 Known unresolved issues。另一设备环境仍需独立核验。
- 下一步：按用户具体目标继续；仅“开工”时做规则规定的只读接手。本文档任务的提交/推送结果以实际 Git 结果为准，不把计划写成已发布。

## Start here

- Checkout: `~/opt/p4vasp`. Run commands from its root. Older notes contain paths from other computers; use repository-relative paths.
- Read `AGENTS.md` and `doc/GTK3-migration.md`. For interface work, use `.agents/skills/p4vasp-gtk-ui/SKILL.md`.
- The project rules now define document roles, on-demand context recovery, the “开工” handoff, evidence attribution, per-device checks, delivery documentation and token/tool economy. Routine efficient actions remain autonomous; users may run costly or desktop-only checks with concise commands and feedback. See `AGENTS.md`.
- Detailed bilingual change records live in `update_history/`. Keep them as the source for historical details; update this memory when new fixes change where to investigate.
- Python GUI: PyGObject/GTK3 via `lib/p4vasp/gtk3/`. Existing `data/glade2/*.glade` files are loaded by `lib/p4vasp/gtk3/glade.py`. Native FLTK/OpenGL windows and the GLUT k-point viewer use separate backends.

## Update history

| Date | Completed work | Detailed record |
| --- | --- | --- |
| 2026-10-28 | Adopted concise handoff checkpoints, dependency-complete migration and presentation/input boundaries from the PFAS documentation review. Documentation only. | [October 28](update_history/update_2026_10_28.md) |
| 2026-09-05 | GTK3 replication controls, applet switching/lifecycle, file opening/saving, Python 3 compatibility, and initial Build blank-area fix. | [September 5](update_history/update_2026_09_05.md) |
| 2026-09-07 | Structure background/cell outlines, element colors, Top/Side controls and sphere sizing; Measure startup, default Z-matrix mode, and missing angle/dihedral rows. | [September 7](update_history/update_2026_09_07.md) |
| 2026-09-23 | STM controls/layout, native INCAR generator and save/folder dialogs, GTK3 runtime and Cairo plotting migration. | [September 23](update_history/update_2026_09_23.md) |
| 2026-09-24 | Removed only the left-toolbar New shortcut; retained Edit → New and the New applet. Reference backups are under `deprecated/new-button/`; read `deprecated/README.md` first. | [September 24](update_history/update_2026_09_24.md) |
| 2026-09-26 | Shortened INCAR help text to identify POSCAR input and `data/incar/presets.json` as the MAGMOM/UJ settings source. | [September 26](update_history/update_2026_09_26.md) |
| 2026-10-06 | Copied atoms default to T T T when selective dynamics is enabled; original flags remain unchanged. Moved update notes into `update_history/`. | [October 6](update_history/update_2026_10_06.md) |
| 2026-10-12 | Fixed simultaneous Build table/text views; disabled automatic log-file writing; added Shift + left-drag additive atom selection. | [October 12](update_history/update_2026_10_12.md) |
| 2026-10-13 | Shift-drag now toggles each atom inside the box; idle Escape clears the entire selection. | [October 13](update_history/update_2026_10_13.md) |
| 2026-10-24 | Unified installer/launcher; headless PNG export, model/material controls, current-view GUI export, and File menu separator fix. | [October 24](update_history/update_2026_10_24.md) |

## Where to investigate

### Native structure-window box selection

- Shift + left drag toggles atoms whose screen-projected centers lie in a rectangle, including occluded atoms but excluding explicitly hidden atoms. Plain left drag rotates; Space toggles one atom; Esc cancels an active drag while preserving previous selections, or clears all selections when idle. No mode button was added.
- `src/VisStructureDrawer.cpp` / `src/include/p4vasp/VisStructureDrawer.h`: gesture state, cached per-window draw transforms, periodic-image projection, deduplication, and overlay. Resizing/focus loss cancels a gesture. Projection uses the current clipping range.
- Escape follow-up: `src/VisFLWindow.cpp` must consume `FL_KEYBOARD`, `FL_SHORTCUT`, and `FL_KEYUP` for Escape even when idle. FLTK's global unhandled-Escape fallback closes the window. Normalize shortcut Escape to a key press for active box cancellation. Tests must use `Fl::handle`, not only direct drawer/window handlers; the original test missed the fallback. Unexpected closing was reproduced and fixed; the reported whole-app hang was not independently reproduced.
- `src/VisWindow.cpp`: offers gestures to the structure drawer before navigation and draws the box after all scene drawers. `src/VisFLWindow.cpp`: returns consumed events to FLTK, including Escape.
- One existing `BE_SELECTED` or `BE_DESELECTED` event per changed box/clear tells `p4v.py` to reload the complete selection. Preserve this batching for large selections.
- Rebuild native code with `bash install/build-ubuntu-py3.sh`; restarting Python alone does not compile C++ changes. Native regression: `/usr/bin/python3 test/run_box_selection.py` (requires built objects, g++, fltk-config, Python development libraries and a display).
- Native synthetic gesture/rendering checks passed on Linux on October 12, including Side view, perspective/zoom, replicas, cancellation and legacy controls. October 13 extended the native checks to toggle-off, mixed regions, outside preservation, empty-selection notifications, idle Escape clearing and cancellation with existing selections. 57 unit tests and 31 applet startup checks passed after rebuilding. Full GTK suite still has 14 resource-property subtest failures. macOS/HiDPI and full manual selection-dependent applet workflows remain unverified.

### Build table/text overlap

- `lib/p4vasp/applet/BuilderApplet.py`: `initUI()` and `on_view_button_toggled_handler()`.
- Layout: `data/glade2/builder.glade`; toolbar entry: `data/glade2/frame.glade`.
- `p4v.py` performs parent `show_all()` calls when displaying/embedding applets. These could reveal the hidden table while text mode remained selected. Resizing alone was not established as the cause.
- Both `text_editor` and `table_editor` now have `set_no_show_all(True)`; explicit radio-button handlers show/hide the selected editor. Preserve both protections.
- Regression: `test/testGtk3.py`, `test_builder_views_stay_exclusive_after_resize_and_show_all`. It checks initial table mode, switching, resizing, mapped children, allocations, and the selective-dynamics control. POSCAR parsing is isolated in this layout test.

### Automatic p4vasp.log creation

- `p4v.py`: two logger setup sites in `Frame.createFrame()`.
- The original `FrameMessageDriver(xml,"p4vasp.log")` calls are commented out. Active calls use `FrameMessageDriver(xml)`, whose default is `DummyFile` from `lib/p4vasp/message.py`.
- Keep status/error messaging active. The user asked to comment out file logging, not remove the logging implementation. Restore the commented calls in place of the no-file calls only if logging is requested again. Existing log files are not deleted.

### INCAR defaults and generation

- UI/help/save workflow: `lib/p4vasp/applet/IncarApplet.py` (panel built in Python).
- Generation: `lib/p4vasp/incar_generator.py`; defaults: `data/incar/presets.json`; usage: `data/incar/README.md`; tests: `test/testIncarGenerator.py`.
- Current help: “Reads the open POSCAR; MAGMOM/UJ values use data/incar/presets.json.” Earlier notes describing zero moments are historical; inspect current presets and generator before changing defaults.

### Copying atoms

- `lib/p4vasp/applet/MoveApplet.py`: Copy behavior. Preserve original atom flags and translations; new atoms use T T T only when selective dynamics is enabled.

## Accepted selection workflow

- The user accepted the October 13 interaction: orient the model (often Side view), Shift + left drag to toggle every atom in a region, repeat to toggle back, and press Escape outside a drag to clear the complete selection. Keep Space toggling and ordinary rotation.
- Do not revert to additive-only box selection: that was the initial October 12 implementation and was explicitly superseded by the user's request.
- Published commits: `e571b1d` introduced box selection, `5764343` prevented Escape-triggered window closing, and `aaeb737` implemented toggle selection and idle-Escape clearing. The detailed bilingual summary is `update_history/update_2026_10_13.md`.

## Known unresolved issues

### Potential POSCAR overwrite issue — investigation deferred (2026-10-13)

- User reports that saving to another folder containing an existing POSCAR sometimes appears not to overwrite it. The filename field already shows POSCAR when they click OK; whether they entered the folder or only highlighted it is not established.
- User requested recording this as a potential issue only and will provide more information if it recurs. Do not treat it as a confirmed overwrite defect or implement a fix based on the current evidence.
- Temporary-file tests: the actual `Frame.save_system_selected` handler successfully overwrote an existing POSCAR. Navigating into a destination folder or selecting its existing file also worked. Programmatically selecting only a directory left a parent-folder save path in one test; this does not reproduce or prove the user's mouse workflow.
- Confirmed code behavior: `p4v.py` saves `INITIAL_STRUCTURE`; a write error still closes the dialog and refers to disabled `p4vasp.log`. An isolated dialog callback ran twice, but the actual save handler ran once. No cause for the user's intermittent symptom was established.
- Investigate `p4v.py` (`show_save_system_fileselection`, `save_system_selected`), `lib/p4vasp/gtk3/__init__.py` (`FileSelection`), and `data/glade2/frame.glade`. No save implementation or calculation files were changed during this investigation.
- If it recurs, collect the exact destination path, click sequence, any error/status message, and before/after file contents or modification time; establish whether the structure came from Build or the final/trajectory viewer. Possible future improvements are a full destination-path display, overwrite confirmation, and keeping the dialog open with the actual write error. These are proposals, not implemented fixes.


Observed during the October 12 checks; not fixed by the view/logging changes:

- Full GTK resource tests report Glade property-conversion failures (shadow types, window hints, gravity, text wrapping). Start with `lib/p4vasp/gtk3/glade.py` and the failing resource/property reported by `test_all_resources`.
- Live POSCAR parsing during text-buffer replacement can fail with `ParseException` errors (“exceptions must derive from BaseException” / “catching classes that do not inherit from BaseException”). Trace `BuilderApplet.on_textbuff_changed_handler`, `textview2struct`, `updateStructure`, and parsing in `lib/p4vasp/Structure.py` / `lib/p4vasp/util.py`. Inspect exception definitions and callback timing before choosing a fix.
- The optional separate GLUT k-point viewer previously failed with an OpenGL context error; it is excluded from default GTK applet smoke checks. See `doc/GTK3-migration.md`.

## Verification and launch

From the checkout root, with compiled cp4vasp and GTK3 dependencies available:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD/lib:$PWD/src" P4VASP_HOME="$PWD" /usr/bin/python3 test/test.py
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD/lib:$PWD/src" P4VASP_HOME="$PWD" /usr/bin/python3 test/testGtk3.py
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 test/run_gtk3_smoke.py
```

GTK checks need a working display. On October 12, the sandbox could not connect to the display; approved execution outside it worked. Respect approval controls rather than assuming display access. Inspect the rendered panel for layout fixes; syntax/XML checks alone are insufficient.

October 12 evidence: 57 bundled tests and 31 applet startup checks passed. The focused Build test passed at 800×600, 1400×900, and 900×650; rendered views were inspected at 1400×850. The full GTK suite was not clean due to the issues above. The later logging-only change received syntax, call-site, no-file logger, and whitespace checks; GUI/full tests were not rerun for that change.

Launch updated code after closing the existing application:

```bash
bash p4v.sh
```

The launcher selects `.venv-macos/bin/python3` when available, otherwise `/usr/bin/python3` or `python3`; `PYTHON` overrides this. It sets `P4VASP_HOME` and the library path and forwards application arguments.

## Publishing preferences and recorded state

- Follow the automatic update-note commit/push workflow in `AGENTS.md`. Stage only related files; preserve unrelated changes; never force-push.
- Authorized repository: `https://github.com/bigbrosci/p4vasp.git`, remote `origin`, branch `p4vasp-py3`. Check these before publishing.
- Recent published implementation commits: `c8cf168` (matte default), `f19070b` (current-view GUI export), and `22c087a` (File menu separator). These identify changes, not a permanent HEAD; check Git for later work.
- An earlier automatic approval review blocked publishing until the user explicitly approved the destination and payload. The user then approved uploading, and the push succeeded. Report actual push results; local commits alone are not published updates.

## Installation and startup — current state

- Install/build from the checkout root using `bash install.sh`; daily startup is `bash p4v.sh`. `p4v.py` is the Python application/CLI entry, not an installer. If using a `p4v` alias, point it at the current checkout's `p4v.sh`.
- `install.sh` detects `uname -s` and Linux os-release ID/ID_LIKE without sourcing shell code. Ubuntu/Debian uses `install/ubuntu-bootstrap.sh` with apt; other Linux uses its skip-apt path with preinstalled dependencies. Automatic dnf/pacman/zypper installation is not implemented.
- macOS uses `install/macos-bootstrap.sh`, Homebrew packages including GTK3/PyGObject/py3cairo, and `.venv-macos` with system site packages. Homebrew and Xcode Command Line Tools must already exist. The Ubuntu apt command in installation documentation is not a macOS command.
- Default installation rebuilds the native extension, which is required for C++ mouse-selection changes to work on another computer. `--dry-run` previews without changes; `--deps-only` prepares dependencies; `--skip-deps` skips package installation. See [install.md](install.md) for full options.
- Obsolete wrappers removed with user approval: `ubuntu-start.sh`, `macos-start.sh`, `install/install-ubuntu-dependencies.sh`. `run-p4vasp.sh` was renamed to `p4v.sh`; `ubuntu_install.sh` was renamed to `install.sh`. Keep the backend/build scripts under `install/`.
- Installer verification: nine mocked routing/argument tests, shell syntax and local Linux dry run passed on October 24. Actual package installation, macOS execution and cross-distribution builds were not performed for the entry-point changes.

## Image export — current state

### User-selected behavior

- PNG background is **transparent by default**. The user selected the middle material preview, so **matte is the default**; classic/glossy remain available. Default brightness is 1.0 and supersampling quality is 2.
- CLI export **replaces existing output by default**, publishing only after successful rendering. `--no-clobber` prevents replacement and `--force` remains compatible. GUI file selection confirms overwrite. Input structures are protected.
- GUI export must use the **latest user-adjusted camera at save time**: rotation, zoom, translation, projection and viewport aspect ratio. Do not reset to Top/Side, automatically recenter or fit the model. If the window crops atoms, the exported framing also crops them.
- User priority: interactive viewing/building must stay responsive; reserve detailed rendering for exported images. Keep the existing lightweight native window, render previews at reduced resolution/sampling, and run final image work off the GTK thread. Do not enable expensive effects on every mouse move.

### CLI and renderer

- `p4v.py` dispatches `-o`/`--output` and help before GTK imports to `lib/p4vasp/render_cli.py`. Without output options, normal GUI startup remains. `p4v.sh` forwards arguments.
- `p4v POSCAR -o model.png` uses the default export-only `studio` renderer (NumPy plus pycairo), without GTK windows, a display server or ASE. `--renderer fast` retains the earlier gradient implementation. CLI default size is 1000×1000 and model is `spheres`.
- Models: `spheres`, `ball-stick`, `stick`, `space-filling`. The last uses larger project radii; it is **not a calibrated van der Waals model**. Colors/radii/covalent radii come from `data/atomtypes.xml`; unknown elements are gray and do not acquire inferred bonds.
- Bonds use a covalent-radius distance heuristic (default multiplier 1.15), with adjustable radius (default 0.10 Å). Pair search is quadratic. CLI connects input atoms only; automatic periodic-image bonds/replicas are not implemented.
- CLI views: top looks from +z; side rotates −90° about Cartesian x (look from +y, x right, z up), currently matching front. The superseded +90° side change was upside down because screen y is inverted. Preserve the projected-z sign regression.
- Ordered `--rotate` angles use the right-hand rule and affect only the image. This differs from the historical GUI Rotate applet's sign convention. GUI camera export bypasses CLI view presets.
- `--quality 1|2|3|4` controls supersampling, capped at 64 million working pixels. Size limits and all options are in [doc/render-cli.md](doc/render-cli.md).

### GUI panel and camera bridge

- Control's camera button **Export PNG** is defined in `data/glade2/swincontrol.glade`; the combined Structure applet uses `structureapplet.glade`. Their `on_foto_button_clicked_handler` methods open `lib/p4vasp/export_image.py`. Original single TGA handlers remain as `save_legacy_screenshot`; animation export is unchanged.
- `snapshot()` copies the native camera through `getRotMatElement(row,column)`, zoom, viewport/projection and current Cartesian structure/frame. It preserves hidden atoms, repeated cells and cell visibility. Copy native state on the main thread; workers receive Python values only. No temporary POSCAR is written.
- `render_cli.py` accepts scene/camera for GUI export while retaining CLI presets/autofit. Projection follows `src/VisNavDrawer.cpp`: orthographic .04 world units/pixel; perspective near=10, far=50, eye translation −20. Do not transpose the native matrix or omit its translation/zoom.
- Panel: preview, model/material, width, quality, brightness, refresh and export chooser. Preview uses studio at 520-pixel width and 1x sampling; final output uses selected quality. Closing requests cancellation and cancelled work does not replace existing output. Height follows window aspect ratio. Use **Refresh preview** after changing the model view or numeric settings; actual export always takes a fresh snapshot. Rendering runs in a worker, with errors shown in the still-usable panel.
- Cairo transparency may appear white against the GTK panel; the PNG retains alpha. GUI background is always transparent.

### Rendering limitations and future work

- `lib/p4vasp/render_studio.py` analytically intersects rays with spheres and round-ended cylinders, choosing the nearest surface per sample (including perspective/clipping planes). It uses linear-space normal lighting, controlled specular highlights, sRGB encoding and supersampling. Spatial tiles bound scratch depth/normal memory; NumPy is loaded only when exporting.
- A local finite-distance contact-darkening heuristic adds depth; this is not physical ambient occlusion, cast shadows, PBR or path tracing. The `fast` fallback retains Cairo gradients, center-depth sorting and approximate perspective radii. PNG output uses Cairo for encoding/downsampling.
- GUI exports atoms, inferred bonds and cell edges. It omits arrows, isosurfaces, selection markers and custom native colors/bond lists. Explicitly repeated GUI cells are included; this does not imply complete periodic-bond handling.
- Style comparison previews were local temporary files under `/tmp/p4v-material-preview/`; do not rely on them persisting. The user structure and previews were not published.

## File menu separator

- The blank row below Reload data was the unlabeled `GtkMenuItem` named `separator` in `data/glade2/frame.glade`. It was intended to be a divider, not a missing action.
- Changed it to `GtkSeparatorMenuItem` and added the constructor mapping in `lib/p4vasp/gtk3/glade.py`; unknown classes otherwise fall back to a Box. Both resource and adapter changes are needed.
- Actual popup rendering and neighboring labels were checked on X11, and 31 applet startup checks passed. Wayland popup checking encountered a display protocol error; no application backend default was changed. Use `GDK_BACKEND=x11` as a diagnostic fallback, not an assumed permanent requirement.

## Latest verification references (2026-10-24)

These are recorded implementation checks, not guarantees for another device. The studio update reran the export, basic, GTK startup and full GTK checks; installer results remain from earlier work:

| Check | Recorded result | Command from checkout root |
| --- | --- | --- |
| Unified installer routing | 9 passed | `/usr/bin/python3 test/testUnifiedInstaller.py` |
| Headless image export | 14 passed (studio default/fast fallback included) | `PYTHONPATH=lib P4VASP_HOME="$PWD" /usr/bin/python3 test/testRenderCLI.py` |
| Studio surface tests | 6 passed | `PYTHONPATH=lib P4VASP_HOME="$PWD" /usr/bin/python3 test/testRenderStudio.py` |
| Replay presets | 6 passed; arbitrary-angle byte-identical replay and batch input | `PYTHONPATH=lib P4VASP_HOME="$PWD" /usr/bin/python3 test/testRenderRecipe.py` |
| Native initial centering | Passed; actual screenshot inspected | `/usr/bin/python3 test/testStructureCenter.py` |
| Native/GTK export integration | Passed; panel inspected; event-loop heartbeat and cancellation checked | `/usr/bin/python3 test/testExportImage.py` |
| Bundled tests | 57 passed | `PYTHONPATH="$PWD/lib:$PWD/src" P4VASP_HOME="$PWD" /usr/bin/python3 test/test.py` |
| GTK applet startup | 31 passed | `/usr/bin/python3 test/run_gtk3_smoke.py` |
| Full GTK suite | 14 known Glade property failures | `PYTHONPATH="$PWD/lib:$PWD/src" P4VASP_HOME="$PWD" /usr/bin/python3 test/testGtk3.py` |

- GUI checks need a display and compiled native extension. `testExportImage.py` checks the toolbar entry, native matrix/zoom, hidden/replicated atoms, preview, fresh camera after rotation, perspective, PNG alpha and error recovery. The standalone integration test exits without testing native FLTK worker teardown.
- macOS installation/rendering, HiDPI behavior and full manual workflows on another computer remain unverified. See the unresolved issues above and [doc/GTK3-migration.md](doc/GTK3-migration.md).

### Studio export evidence (2026-10-24)

- On this Linux checkout with `/usr/bin/python3` and X11, the export integration serviced 104 GTK timer ticks during a 900-pixel, 3x export. This demonstrates event-loop activity, not a measured native-window FPS guarantee.
- Visually inspected old/new side-view renders of the user's Desktop POSCAR, ball-stick water and the allocated export panel. One local 700×460, 3x example took about 0.17 s (fast) versus 1.27 s (studio); this is a single example, not a general benchmark. User inputs/previews were not published.
- No native renderer or installed GTK backend changed. Large exports still consume CPU; macOS/HiDPI and real interactive frame rates remain unverified.

## Reusable GUI camera commands (2026-10-24)

- Export dialog defaults to saving a replay bundle after successful PNG output: `<image>.POSCAR` (base Cartesian geometry), `<image>.view.json` (versioned data-only camera/render/display state), `command_for_<image-stem>.sh`. Copy command shows the last successful saved command. Unchecking the recipe option writes only the PNG. Existing companions get a new `.replay-N` prefix; they are not overwritten. Geometry snapshots omit calculation settings/selective-dynamics flags.
- New `lib/p4vasp/render_recipe.py`: validation, DEFAULTS, repeat/hidden replay, snapshot serialization, shell-safe command generation and companion publication. `render_cli.py --preset FILE` applies camera/settings and rebuilds visible replicas from the supplied input. Explicit CLI image options override preset settings; --view/--rotate conflict with --preset. Keep DEFAULTS consistent with render() defaults.
- GUI snapshot copies recipe data only for an actual export with the checkbox enabled; previews avoid that extra copy. Recipes capture save-time state, including edited/current trajectory geometry. CLI replay needs no GTK/display. Other structures retain the same camera, not auto-alignment/fitting; axes/origin/scale should match and hidden indices require matching atom order.
- GUI controls compacted with a scrollable settings area and fixed export actions; copy command remains accessible at 620×600. User still edits/rotates in the lightweight native window.
- Verification: 5 recipe tests (byte-identical headless replay, batch input, overrides, validation/conflicts and collision protection), 14 CLI tests, GUI integration including real command execution, clipboard and recipe opt-out, 57 bundled tests and 31 applet startup checks passed. Allocated GTK panel inspected on X11. Full GTK retains 14 known Glade failures; macOS not tested.

- Replay command files now use `command_for_<image-stem>.sh` beside the image (e.g. model.png → command_for_model.sh), with Bash header, executable permission and forwarded CLI options. Existing files remain protected by replay suffixes. Six recipe tests passed, including running the saved script headlessly with option overrides.

## Center and fit newly opened structure windows (2026-10-24)

- User request: Show should initially center the atom model in the structure window without manual pan/window adjustment. `StructureWindow.fitToStructure()` fits the visible atom surfaces (radius included) and actual native replicas with 15% margin, ignoring empty cell/vacuum bounds. Only camera changes; source coordinates are preserved.
- `_needs_initial_fit` applies on first nonempty structure, window recreation and a new system in `StructureWindowApplet.setSystem`. Ordinary same-system frame/structure refresh preserves the camera. Recreated windows retain radius factor and repetition settings. Home in both structure control applets restores default rotation then fits; the shared STM control retains its original Home behavior.
- `VisNavDrawer.centerOn` and private pivot state keep centering stable through zoom/right-drag zoom and standard views. `replaceRotation` preserves the pivot's screen position; Home resets it. Updated native header/source and tracked SWIG wrapper/Python proxies in src and lib. Native rebuild required (`bash install.sh --build-only`); this Linux checkout was rebuilt successfully.
- `test/testStructureCenter.py` exercises offset/negative coordinates, slab vacuum, 400×300/800×600/900×300 viewports, replicas, radius preservation, view/zoom pivots, new systems, frame preservation, Home/reopening and an actual OpenGL screenshot. Center checked numerically and visually; no geometry centering/wrapping is applied.
- Passed that focused check, native box-selection regression, GUI export/replay integration, 57 bundled tests and 31 applet startup checks on Linux/X11. Full GTK retains 14 known Glade conversion failures. macOS and HiDPI not verified. Existing saved camera presets still replay their stored framing; export does not re-fit.

# p4vasp maintenance memory

Last updated: 2026-11-26. This is a repository navigation and handoff document. Verify the current source and Git state before acting; historical test results are not current guarantees.

## Windows发布进行中：诊断跟随新界面（2026-11-26）

- 用户要求最新EXE。首轮333c69a在Windows独立checkout完成native/GUI/worker冻结，runtime/gui ok，但models被旧multiplicity空白断言拒绝，失败产物p4vasp-20261126-020443-333c69a5-oqkrtslg不交付/不打ZIP。日志/tmp/p4vasp-windows-20261126.log，Windows build/windows-update/333c69a5-lj4y3is0；应用实际已正确用1。
- windows_model_check改验默认1及清空字段0/1导出；windows_check补实际内嵌启动/Cairo Show无native打开及异步关闭，使用有界GTK事件处理。Linux源--check-gui已通过/tmp/p4vasp-release-gui-20261126-r3/report.json，非冻结验收；初轮无界处理及未等待异步close的诊断尝试已更正，不记通过。
- 另首轮Windows源Cairo完整controls测试在临时runner适配启动等待、/tmp路径和退出cwd后通过/tmp/p4vasp-windows-20261126-cairo.log，截图C:/msys64/tmp/p4vasp-cairo-show-20261126.png已查看；这些是Windows源界面证据，不冒充冻结新版专项。首次环境采样12/48分发版本同11月24，失败构建的未提交快照不作最终基线。
- 下一步已获授权：推送诊断更新后正常updater重建，全冻结runtime/gui/models通过再验ZIP/SHA/SOURCE、采最终目标解释器基线、写交付目录并推送文档。保留旧成品，不需再询问；最终包尚未完成。

## Gas Build 3D默认Charge/Multiplicity（2026-11-26）

- 按用户要求，gtk3/gas_phase.py中SMILES Build 3D计算字段默认0/1；构建开始捕获现有值，空白补0/1，成功后保留，重新构建不覆盖用户修改。生成输入时SMILES空白也补默认并回显；显式非法值仍按原校验拒绝。RDKit形式电荷/未知自旋元数据不改，不自动覆盖用户计算设置；原XYZ元数据和未知必填逻辑保持，placeholder按来源显示Default或Required。Glade/入口不改。
- 本机Linux/WSL真实SmilesGtk构建/优化/空白导出0/1/用户-1与2重建保留/刷新/预览/错误/取消通过/tmp/gas-spin-default-smiles.log；XYZ实界面/元数据/带电模板/保存取消通过/tmp/gas-spin-default-xyz.log，5气相输入及语法/diff通过/tmp/gas-spin-default-inputs.log。XYZ测试旧install-rdkit.sh断言已改为现行install-science.sh后重验，非本次安装逻辑改动。使用指南/分子库README及双语同步，无依赖/环境/Windows包，Mac/Windows未验收。

## 普通Show统一Cairo（2026-11-26）

- 用户决定将普通Show改为与主区域/频率相同Cairo，而不是嵌入FLTK。StructureWindowApplet创建gtk3/structure_window.py的CairoStructureWindow，兼容原Control/序列接口；ShowController复用StructurePreviewApplet显示/编辑钩子，StructureView/ModeView共用球棍/颜色/半径/导航/选区，初始结构才可编辑，File原保存路线不改。恢复焦点不自动替换内嵌编辑器，关闭释放Gtk并停止同体系播放，允许重开。
- 兼容六视角（与native矩阵逐一比较）、Home/缩放、半径/键、隐藏/晶胞/背景、投影箭头、各轴1–10扩展（总显示12000保护）、TGA/PNG截图与透明图片导出快照。显示副本保留Direct/Cartesian，native数值归一化尺度后转Python副本；空结构绕开native空指针。periodic_preview.geometry新增可选centered/wrap/max_repeat，Show使用居中重复及显式单位胞副本以保持导出一致，频率默认不变。快照平移含zoom/pan，并验证与render_cli像素投影/重复坐标一致；同源轨迹/重复刷新保留相机。
- 体数据等值面和Perspective仍需专用FLTK/OpenGL，首次使用才创建并把完整Control接口转交给旧后端；None/Orthographic条件满足后回Cairo，转接保留半径/重复/隐藏/晶胞/背景/箭头及相机。不是Cairo体绘制实现，其他模型/STM及GLUT不迁移，不能删native依赖。Glade/adapter/菜单/工具栏未改。
- 本次Linux/WSL实际Cairo Show外观数据/正负体积三轴尺度/六视角/Control/隐藏/重复/半径/箭头/截图与导出相机/初始编辑及final保护/人工CHGCAR与透视返回/关闭播放和重开通过/tmp/cairo-show-controls.log，截图/tmp/p4vasp-cairo-show.png已查看；原启动编辑/File Save、XDATCAR切帧/定时播放、频率实界面通过/tmp/cairo-show-{startup,trajectory,vibrations}.log。6导航/3显示几何/10 GTK/34默认面板/58基础/3依赖工具及目录check/语法/diff通过，对应/tmp/cairo-show-{navigation,geometry,adapter,smoke,base,dependencies}.log。诊断中的空结构native异常、坐标表示、选择/焦点及导出位移问题修正后重验；仍见旧GTK/GDK/SWIG析构/弃用提示，不宣称修复。
- 当前任务完成，使用/架构/依赖用途与当日双语同步；无新依赖/版本或环境变化，不采新快照/原生重编/Windows包，Mac/Windows未验收，私有Cu3Ru1未访问。源码版重启生效。

## 内嵌结构键鼠编辑与File保存（2026-11-26）

- 用户要求启动主区域与Show保持选择/编辑一致并能File保存。新增gtk3/structure_view.py的StructureView，仅Startup启用：空格拾取鼠标下最前原子，Shift左框逐个toggle、Esc取消框/清空选择、Delete、当前视角方向键移动0.1 Å、Shift方向键质心旋转5°；鼠标进入获取键盘焦点，失焦/改窗口取消框，Ctrl/Alt/Meta不触发编辑。蓝圈高亮，顶部Selection与底部Selected同步，共用SelectionListener，原导航保留。
- StructurePreviewApplet.edit直接调用atom_movement三函数写INITIAL_STRUCTURE，刷新同体系所有面板；File原Save回调无需修改，保存当前真实结构。相同source刷新保留相机，换source清空选择；图像位置副本不再被误当可保存编辑副本。ModeView只抽共享project/projection_scale，振动仍只读。Show/Control转换/Glade/toolbar及Build不改；使用说明与架构同步，新记录update_2026_11_26.md双语。
- Linux/WSL本次实际GTK空格/框toggle/重复框取消/Esc/失焦与resize取消、顶栏/计数、箭头/旋转/Delete及修饰键防误删、相机保持/约束/删除至空、实际File菜单/保存chooser OK和POSCAR坐标/顺序/约束回读通过/tmp/embedded-edit-gtk.log；原CLI/尺度/Show-Control新原生窗/Info/系统刷新也通过。7移动科学/6导航/10 GTK/34默认面板启动及语法/diff通过，日志/tmp/embedded-edit-{movement,navigation,adapter,smoke}.log，截图/tmp/p4vasp-embedded-selection.png已查看并修复初轮蓝圈路径连线。既有SWIG泄漏/析构/弃用提示未修复；未访问私有example，无依赖/快照/原生重编/Windows包，Mac/Windows未验收。任务完成，源码重启生效。

## 启动主区域结构预览（2026-11-25）

- 用户希望p4v POSCAR启动后主区域显示结构，Show/Control替换内嵌预览且仍弹独立窗口。新增StructurePreviewApplet并注册，init默认改用它；复用ModeView只读Cairo预览/Show共用样式及导航，无ASE/额外原生窗口。显示INITIAL_STRUCTURE副本、晶胞及元素数量，换算正/负体积/三轴POSCAR尺度，保留原坐标/文件；空/无效/超限提示，沿用12000显示原子保护。
- Frame.showApplet仅Show遇到仍有panel的startup_preview时切换原Control，Control直接切换；panel存在判断防Control创建原生Show时递归，其他面板的Show行为不变。Edit → Info仍保留，frame.glade/工具栏/adapter/原生编辑及轨迹未改；预览无选择/删除，独立视角不传Show，指南明确展示不替代科学输入。
- Linux/WSL本次实际CLI启动、预览显示、源文件/结构不变、三种尺度/坐标、实际Show/Control工具栏（含Control新建原生窗口）、Info保留、空/切换系统通过/tmp/startup-preview-gtk.log；截图/tmp/p4vasp-startup-preview.png已查看。10 GTK及34默认面板启动（含新预览，不含GLUT）通过/tmp/startup-preview-{adapter,smoke}.log，语法/diff通过。初轮用纯Python Structure不存在的clone失败，改setStructure副本后通过，不把初轮记通过。无新依赖/快照/原生重编/Windows包，Mac/Windows未验收，私有example未访问。任务完成，源码重启生效。

## k点窗口关闭与上下文修复（2026-11-25）

- 用户报告Electronic → View k-points窗口无法关闭。本机先复现GLUT创建窗口后PyOpenGL因Wayland自动选EGL而注册callback失败（/tmp/kpoints-before.log），未完成初始化的窗口无事件处理；OpenGLPaint3D在Linux有DISPLAY且未显式指定后端时选GLX，保留其他平台/用户选择，不改GTK/原生Show后端或依赖。
- KpointsViewerApplet改用16 ms GLib定时器，不依赖任务队列；X关闭/字节Esc及销毁移除timer/menu/Dyna listener，freeglut continue不退出主程序，可重新打开。删除隐藏窗口/回调中递归事件处理，用两个后续GTK轮次完成关闭通知/原生释放；raw GLUT destroy避免PyOpenGL便利包装过早清理C callback，最终再清context缓存。期间诊断捕获过悬空窗口及回调释放导致的崩溃，已修正后完整重验，未把失败记通过。Models/Glade/菜单入口未改。
- Linux/WSL本次实际X11 WM_DELETE、Esc、连续重开、重复销毁、原生窗口消失及GTK idle响应通过，/tmp/kpoints-lifecycle.log；原先失败独立启动现通过/tmp/kpoints-after.log，10 GTK适配器和含GLUT的34面板启动通过/tmp/kpoints-{adapter,smoke}.log，语法/diff通过。人工结构仅验生命周期和回调执行，不作为科研路径准确性/渲染画质验收；原有native析构警告仍在。架构/用法/双语同步，无新依赖/快照/原生重编或Windows包，Mac/Windows未验收，私有example未访问。当前任务完成，源码重启生效。

## 数据库新增periodic table（2026-11-25）

- data/resources/websites.json新增第19张periodic table卡片，URL https://periodictable.com/，沿用Database → Resources → Databases四列导航、点击下方显示网址并自动复制。无Applet/Glade/适配器改动。
- Linux/WSL本次5资源测试、实际ResourceHub含新卡片标签/位置/网址/剪贴板及原导航/编辑集成通过，/tmp/periodic-link-{data,gtk}.log；/tmp/p4vasp-online-links.png已查看。初轮测试误用Button.get_label，改读已有卡片child Label后通过；旧析构提示仍在。diff通过，资源说明/双语同步，无依赖或Windows包，Mac/Windows未验收。

## 单原子磁矩来源说明（2026-11-25）

- 用户指出Fe原子参考4与p4vasp data预设3不一致。AtomInputDialog把Use reference改名Use atomic 2S，在设置区明确显示NIST中性自由原子LS的2S估计及当前个人/默认Magmom预设，说明均非最终DFT磁矩；Fe S=2/多重度5→4 μB，预设3是独立可编辑初始化，不宣称实验体相值。按钮逻辑/全局数据/默认空MAGMOM不变，原Models资源/入口不变。
- 本机Linux/WSL实际弹窗回归验证Fe来源/2S=4/当前预设/按钮填4及原电荷/约束/预览=导出/取消流程；日志/tmp/atomic-moment-source-gtk.log。语法/diff通过，指南及双语同步；无新依赖或Windows包，Mac/Windows未验收。

## 单原子固相结构参考（2026-11-25）

- 用户要求补充常温稳定晶型、气体低温固相。AtomInputDialog增加Phase (~298 K, ~1 bar)、Solid structure、Structure conditions只读行及独立晶体来源链接；现有滚动设置/底部Generate保留，ModelsApplet/models.glade/工具栏无改动。atomic_reference.crystal_reference独立缓存data/resources/crystal_states.json，83元素条目逐项保存相态/结构/条件/注释/URL，未审阅元素Unknown，不猜超重元素。默认单原子/自旋及输入生成不受晶型驱动。
- 以用户periodictable.com索引为起点，结合AFLOW原型/文献、NIST氢及氦综述区分graphite/diamond、hcp/dhcp、复杂α-Mn、低温分子固相；N采用35.6 K以下α-N2 Pa-3参考，He注明常压不凝固、4He低温hcp需约25 bar或更高压力。不是完整相图或体相生成器；来源链接和用途见doc/single-atom-zh.md及资源README。
- Linux/WSL本次3固相数据/坏文件/输入隔离测试、8原单原子输入及真实AtomInputDialog Cu/He/Og参考/自旋/电荷/预览=导出/取消/重开回归通过，10 GTK适配器及语法/diff通过。实际截图/tmp/p4vasp-atomic-crystal-reference.png已查看，长条件换行、底部按钮可见，更多设置在原滚动区；日志/tmp/crystal-reference-{core,inputs,gtk,adapter}.log。无新依赖/环境快照/原生重编/Windows包，Mac/Windows未验收，私有example未访问。当前任务完成，源码重启生效。

## 单原子参考与计算设置弹窗（2026-11-25）

- 用户批准选择元素后弹出基本资料/电子组态及自旋设置。SingleAtomPage.choose自动打开gtk3/atom_input.py的AtomInputDialog，主Generate可重开；只读名称/Z/当前质量/NIST中性组态/能级/LS对应S和多重度，设置Charge、ISPIN、可选MAGMOM、默认关闭NUPDOWN约束、可选POTCAR ZVAL及盒子。INCAR preview与导出同一快照，成功后记住该元素本会话设置，Cancel不写全局元素资料/文件；内容可滚动，底部操作始终可见。
- atomic_reference.py只读缓存data/resources/atomic_states.json；官方NIST ASD5.12(2024)中性H–Hs108项，工具抓取的表格行atomic_states_source.txt及tools/import_atomic_reference.py可重建，来源/DOI/2026-11-25日期/SHA在JSON。LS自旋从已指认项前缀提取，jj/仅J或快照外均Unknown，不由J或全电子配置猜POTCAR。可用中性Z≤86时Use reference明确填2S初始矩；带电/未知/重原子需手动，参考不强加占据或保证DFT基态。
- single_atom_inputs新增settings_values和可选settings参数，旧API默认仍三文件/13×14×15中心单原子/Gamma1³、ISPIN2/ALGOALL/NELM500且无显式MAGMOM。清理通用标准的MAGMOM/NELECT/NUPDOWN/SOC标记后应用显式设置；约束时空MAGMOM与NUPDOWN一致，验证有限值/正盒长/整数Charge/NUPDOWN、已知ZVAL时电子数及奇偶。中性NELECT省略，带电且ZVAL已知按ZVAL−Charge；未知则明确NELECT=SET_AFTER_POTCAR模板，弹窗/目录/主状态提示运行前补全，不读/生成POTCAR。
- Linux/WSL：8输入/来源重建回归通过（全部118默认、正负电荷/自旋/盒子/奇偶/防覆盖/失败清理、108组态电子总数/LS奇偶及NIST代表条目），实际新弹窗参考/格式/按键/约束/缺资料/精确INCAR预览=写出/重开/取消通过，截图/tmp/p4vasp-atomic-reference-settings.png已查看。原SingleAtom文件/文件夹流程、完整双周期表缩放、1 Models惰性、10 GTK、33面板、58基础及语法/diff通过；日志/tmp/atom-popup-{inputs,gtk,single,fit,lazy,adapter,editor,smoke,base}.log。旧offscreen单原子测试因Wayland窗口/模态阻塞已停止，改真实Window后通过；主窗旧restore警告及析构/弃用提示不宣称修复。
- 操作专用doc/single-atom-zh.md、资源README、架构及双语同步。无新依赖/环境/快照/原生重编或Windows包，Mac/Windows未验收；源码版重启后使用，未访问私有example，任务完成。

## Single atom周期表同步自适应（2026-11-25）

- 用户要求single atom同样完整显示。将FittedPeriodicGrid抽到gtk3/periodic_grid.py，参数化行/列，ElementTable沿用默认19×11；SingleAtom用原18×9元素布局，移除固定最小宽度及ScrolledWindow，共用按可用宽高调整字号/格子逻辑。保留原灰色按钮/选中高亮、Generate inputs及保存目录流程；输出路径改按字符换行，避免长路径撑宽面板。
- Linux/WSL实际完整p4v双标签首次/多次缩放/最大化/还原，全部118格及网格在面板内，SingleAtom可选Og/H并启用生成；实际SingleAtom生成/取消/目录按钮连线及小面板含输出路径的边界检查通过。/tmp/p4vasp-single-atom-fit-{compact,maximized}.png截图已查看。个人元素编辑回归、1 Models惰性、10 GTK和33面板通过，日志/tmp/single-atom-fit-{frame,inputs,editor,lazy,adapter,smoke}.log，语法/diff通过。已知还原GTK自然分配警告及原生析构/弃用提示未修复，未当作新增通过项。
- 操作/架构及当日双语同步，无科学输入算法/依赖/环境变化、快照或Windows重打包，Mac/Windows未验收；当前任务完成，源码重启生效。

## 周期表自动适配面板（2026-11-25）

- 用户报告初次打开p4vasp data不完整，最大化才全。ElementTable移除40×44固定格子及表格ScrolledWindow，FittedPeriodicGrid提供较小最小请求、按可用宽高计算共用字号/零最小padding，调用原生Gtk.Grid分配；保留118按钮、族/周期/f区、焦点/悬停/属性及个人Save。窗体越小字号越小，无需周期表横纵滚动；主窗其他控件仍有自己的最小尺寸。
- Linux/WSL实际完整p4v主窗首次进入、多个缩放、最大化/还原全部118格和网格均在面板内，Og可打开/取消，字号随大小变化；实际小独立面板及个人保存/颜色/取消/冲突、ResourceHub集成通过，截图/tmp/p4vasp-periodic-fit-{compact,maximized,small}.png已查看。10 GTK、1 Models惰性及33面板通过；日志/tmp/periodic-fit-{frame,editor,hub,lazy,adapter,smoke}.log，语法/diff通过。无科学/依赖/环境变更或Windows重打包，Mac/Windows未验收。
- 最大化还原时曾见gtk_distribute_natural_allocation critical，使用HEAD原固定周期表复现同一提示（/tmp/periodic-fit-baseline.log），不归因/宣称修复此既有主窗状态切换问题；旧native析构/GTK弃用提示仍在。保留原生GTK分配，不引入自绘/手工子控件分配；用法/架构/中英同步，当前任务完成，源码重启生效。

## p4vasp data彩色周期表及元素属性弹窗（2026-11-25）

- Models → p4vasp data的ElementTable从TreeView换成118个元素按钮周期表，显示族/周期、分开f区；默认/个人有效RGB着色并按亮度选文字色，无颜色资料仅中性灰显示，不补写科学数据。元素布局PERIODS移至element_data.py共用，single_atom仍保持原布局/入口；ModelsApplet/models.glade/工具栏不变，页面仍惰性创建。
- 点击元素弹出紧凑可滚动ElementEditor，符号/Z只读，可改质量、显示半径、0–255 RGB/颜色选择器、Magmom、U/J。弹窗Save校验后调用原ElementData/ResourceStore个人覆盖/备份/冲突检测/失败回滚，立即刷新格子颜色、不重建网格/跳滚动；Cancel或关闭不写。旧整表Save/dirty/内联编辑代码删除，Reload读已保存数据，已有结构默认缓存仍需重启。未改变持久化格式/参考值/原生或科学算法。
- 本机Linux/WSL真实GTK通过118格/实际CSS颜色、身份/单位/Save显示、RGB校验及picker、修改半径/Magmom/U/J、个人保存/新建页读取、取消无写、未知颜色不回填及外部修改冲突；测试用户目录全部在临时路径，自带periodic/incar/XML哈希未变。实际截图/tmp/p4vasp-data-periodic-default.png、p4vasp-data-periodic.png及p4vasp-element-properties.png已查看；截图关闭动画以消除过渡帧。1 Models惰性加载/ResourceHub集成/SingleAtom真实界面通过，9元素数据+1个人覆盖+5资源后端、10 GTK、33面板及58基础通过，日志/tmp/periodic-editor-{gtk,lazy,hub,single,data,personal,resource,adapter,smoke,base}.log。初轮smoke旧model断言失败，更新至新buttons/data接口后33通过；既有Vector析构/GTK弃用提示仍在，不记作修复。
- 用法/资料README/架构及双语记录同步，修正旧资料README仍宣称直接改仓库的过时说明。无依赖/环境变化/快照、原生重编或Windows打包，Mac/Windows未验收，本轮不访问私有example。源码版重启后使用，当前任务完成。

## 每日一句日期词库（2026-11-25）

- 主窗口空闲底栏从 `data/quotes/daily.sqlite3` 只读加载 1000 条排期，按本机日期选择（2026-11-25 至 2029-08-20）；悬停查看日期、出处和思考问题。无当日排期或数据库不可用时使用原中英文词库，任务/错误优先。
- 本机 macOS arm64 PyGObject/GTK3 实际窗口验证了排期切换、同栏对齐、状态优先及定时器销毁，已查看 /tmp/p4vasp-daily-quote.png。10 GTK、58 基础、SQLite 完整性及缺失/损坏后备通过。当前源码版重启生效。Windows 规格已收录整个 data 目录，未重建或验证 Windows 包，也未运行 Linux GUI。详细记录见 [11 月 25 日更新](update_history/update_2026_11_25.md)。

## Windows新版交付完成（2026-11-24）

- 用户要求将Surface来源三按钮与Bulk晶格显示修复打包。冻结源码42b9802aa894d8d3068e8684b92d9d95f58f6f54，EXE：C:\msys64\home\lqlhz\p4vasp-checkout\dist\windows-releases\p4vasp-20261124-190354-42b9802a-9_742f0r\p4vasp.exe；同级.zip/.zip.sha256，198097752字节，SHA256=f42c2974c7d8d7c680b2c15ae78240b45badbfe9eef3e3d9760f68f8e6df8d7e。完整_internal/model-worker需保留，旧包保留，未复制桌面/上传Release附件；后续纯文档提交不改变SOURCE-COMMIT。
- 本机Windows原生及GUI/worker冻结成功，updater SUCCESS且wrapper零退出；runtime/gui/models均ok/frozen，含Surface预览/固定层/四文件保存/CLI重放、双来源s/p/d/f及既有ASE/RDKit/取消。另Windows源GTK用实际ASE Cu a=3.6345确认三按钮/只读值/完整快照及回预设，日志/tmp/windows-surface-lattice-20261124.log，Windows Temp的p4vasp-surface-lattice-20261124.png及冻结Surface截图已查看；该3.6345专项是源GTK测试，未冒充冻结专项或全部科研场景/干净Windows验收。
- 独立SOURCE/ZIP CRC/SHA256通过，不含私有Cu3Ru1。目标GUI/worker快照doc/dependencies/snapshots/2026-11-24-windows-{gui,model}-42b9802a.json，12/48项版本与11月23日一致、源码/工具/清单摘要核对通过；3依赖工具/清单/diff通过。未额外重复11月23日独立脚本重放测试，不记作本次实测。
- 构建日志build/windows-update/42b9802a-n3t5a1cv；报告dist/windows-releases/p4vasp-20261124-190354-42b9802a-9_742f0r-checks；Linux启动/tmp/p4vasp-windows-20261124.log。交付指南/当日双语同步，当前完成，无待自动构建任务。

## Surface Bulk晶格显示修正（2026-11-24）

- 用户报告Bulk用Cu a=3.6345而Surface灰框仍3.615。源码确认切面已使用完整POSCAR快照，旧灰框为未刷新的Metal preset默认值，未覆盖科学输入。现from_bulk保存其原始request，update_fields只读显示name/a/c；导入文件清空这些预设框，回Metal preset恢复之前缓存，guard避免字段同步触发失效回调。不把输入a等同于原胞/超胞基矢长度。
- Linux/WSL实际GTK用3.6345生成Cu bulk、快照切面/显示值/只读检查、request不含预设a且完整POSCAR不变通过；原Surface来源/预览/Center/Bottom/保存/取消回归通过，/tmp/surface-bulk-lattice-gtk.log，实际截图/tmp/p4vasp-surface-bulk-lattice.png已查看。语法/diff及操作/架构/双语同步；科学算法/依赖/环境不变，Windows未重包，Mac/Windows本改动未验收。

## Surface来源合并三按钮（2026-11-24）

- 用户确认删除Source下拉框，与原读取按钮合并为Metal preset／Use bulk result／Open POSCAR / CIF等宽一排ToggleButton，高亮当前来源。surface.py用source_mode，选预设直接切换，成功读取Bulk快照/文件后再切换并使旧结果失效；同类来源重读也失效，取消文件或无Bulk结果则恢复按钮并保留原来源/结果。GTK set_active可能触发clicked，_source_sync防重入；不改ASE算法、输出recipe、models.glade/ModelsApplet/工具栏入口。
- 本机Linux/WSL真实Surface GTK通过三按钮初始/缺Bulk/取消/实际Bulk与文件读取/回预设、原生预览、Center/Bottom、四文件保存、失效/取消/销毁；实际截图/tmp/p4vasp-surface-page.png已查看，控制项无裁切。1 Models惰性加载及10 GTK适配器通过，日志/tmp/surface-source-buttons-{gtk,lazy,adapter}.log，语法/diff通过；既有native Vector析构提示仍见lazy测试退出。操作/架构/双语同步。无依赖/环境/快照、原生重编或Windows重打包，11月23日EXE仍为旧来源布局，Mac/Windows本改动未验收。当前任务完成，源码版重启生效。

## Windows新版交付完成（2026-11-23）

- 用户要求更新历史、生成Windows及推送，已完成冻结源码5ca60f29fb9f552dfacbf6ef86f273a4d8ceb9d3的包，包含近期Surface/个人数据/DOS+s/p/d/f和重放等；pymatgen加入官方CPython科学worker，与UCRT64 GUI隔离，ASE/RDKit pin保持。DOS/Surface Bash共用冻结console回退，源码仍p4v.sh；新增Windows科学诊断及公开人工fixture，不含私有example。
- EXE：C:\msys64\home\lqlhz\p4vasp-checkout\dist\windows-releases\p4vasp-20261123-013128-5ca60f29-r5cg71v2\p4vasp.exe；同级.zip及.zip.sha256，198095378字节，SHA256=76a023a937326818b43596c69961becf4eba2ccbcb4683ddb02f81d4ff7be64d。保留完整_internal/model-worker，不单拎EXE；旧包保留，未另复制桌面或上传Release附件。包SOURCE-COMMIT不随后续文档提交改变。
- 当前Windows实际原生编译/GUI与worker冻结成功，runtime/gui/models报告均ok=True/frozen=True，含Surface Bottom保存、双来源s/p/d/f、f列序/双脚本、无界面DOS/Surface重放及既有ASE/RDKit/取消。另在MSYS2运行导出DOS/Surface Bash、官方科学Python运行两独立脚本，结果及晶胞/顺序/坐标/固定标记一致。Windows Surface截图已查看。独立核对SOURCE/helper/ZIP CRC/SHA256通过；不是另一台干净Windows/所有科学场景全面验收。
- 发布实际依赖快照doc/dependencies/snapshots/2026-11-23-windows-{gui,model}-5ca60f29.json，GUI Python3.14.9/UCRT与worker3.13.17/MSVC分开，12/48项元数据，pymatgen2026.10.24/core2026.10.31、ASE3.29.0、RDKit2026.9.1；源码与工具/清单hash核对通过。元数据非DLL清单/锁文件，原始无Git PATH临时捕获留Windows Temp，公共快照含来源提交；旧记录不覆盖。
- 日志Windows build/windows-update/5ca60f29-z_n6ok88，报告dist/windows-releases/p4vasp-20261123-013128-5ca60f29-r5cg71v2-checks；Linux启动/tmp/p4vasp-windows-20261123.log及/tmp/windows-exported-replays-20261123.log。WSL启动wrapper最终返回143，但updater日志SUCCESS、成品三个报告及独立ZIP/脚本检查完整通过，不以wrapper退出码0作为证据。源协议/模拟冻结路由、2 CLI、3Surface、2Python、3bundled routing、58基础及3依赖工具/清单/语法/diff通过。指南/当日双语同步；本任务完成，无待自动开发或重建任务。

## DOS分析扩展s/p/d/f及三排轨道（2026-11-23）

- gtk3/dos_analysis.py Orbital三排：s/p及py,pz,px；d及5分量；f及7分量。总壳层与自身分量互斥，分量和不同壳层可组合，空选回d；Spin在其下，Analyze DOS按钮。标题及结果按单壳层显示s/p/d/f-band，跨壳层为selected-band，三位小数/a.u.保留。Use last DOS line同步所有轨道，旧plot f1…f7按VASP列序转换分析f_3…f3，负m按钮显示f−3等，CLI用f_3等规范名。
- dos_selection共享校验/排序/去重/壳层冲突；dos_analysis读取DOSCAR/XML s/p/d/f总量及LM分量，每个选中原子缺任一投影即报错，不补零/借总DOS。汇总源只允许总壳层，SOC限制不变。dos_metrics用对应壳层API容器算同一谱矩/填充/Hilbert算法；跨壳层为求和谱的数值描述，不声称是d带。独立Python保留band_label，Bash/CLI复用相同选择。
- Linux/WSL 11科学（公开人工spd/spdf、9/16轨道、双来源、非自旋、缺f/汇总拒分量、f列顺序/权重等）、2隔离Python（p谱）、2实际CLI/双脚本（含f分量）通过；真实GTK三排/互斥/组合/边界、s/p/f实际计算与三位小数/标题、原DOS/复制/导出/切源/最大化通过，/tmp/p4vasp-dos-spdf.png及最大化图已查看。10 GTK、33面板、58基础、3依赖工具/清单及语法/diff通过；日志/tmp/dos-spdf-{core,replay,cli,gtk,gtk-base,smoke,base}.log。未访问私有example，未改环境/重采快照/重编或Windows包，Mac/Windows未验收。用法/架构/依赖用途及当日中英同步，任务完成。

## DOS结果表格三位小数（2026-11-23）

- gtk3/dos_analysis.py结果表格用%.3f，复制结果沿用表格，Unavailable保持文字；内部计算及CSV/脚本数值精度保持原样。操作说明同步。
- 本机Linux/WSL真实DOS GTK计算/复制/导出/切源/最大化回归通过，日志/tmp/dos-three-decimals-gtk.log；语法/diff通过。未改科学算法或依赖，未构建Windows或验收Mac。

## d-band filling单位标签（2026-11-23）

- 按用户要求dos_metrics将filling单位显示由dimensionless改为a.u.，共享结果同步GUI/复制/CSV及新导出Python脚本，填充度仍为原无量纲积分比值，数值算法不变。doc/dos-analysis-zh.md同步。
- Linux/WSL 10 DOS科学、2独立脚本及真实DOS分析GTK回归通过，日志/tmp/dos-filling-unit-{core,replay,gtk}.log；语法/diff通过。不改依赖/环境或构建EXE，Mac/Windows未验收。

## Surface初始说明文字移除（2026-11-23）

- 按用户要求移除Surface初始status中的Choose a source及Miller指数/固定规则说明，状态标签保留供构建、保存和错误反馈。规则仍见doc/ase-surface-zh.md，建模逻辑不变。
- Linux/WSL实际显示页确认初始文字为空、Build可用、Center默认、Save未生成时禁用；实际Surface GTK预览/来源/保存等回归通过，日志/tmp/surface-remove-hint-gtk.log。语法/diff通过；未验收Mac/Windows，不改依赖或重建EXE。

## Surface保存自动导出重建脚本（2026-11-23）

- Models → surface的Save POSCAR自动保存POSCAR、surface.json、rebuild_surface.py/.sh；最终切面/层数/超胞/真空/固定层/Center或Bottom及自定义体相快照一并记录，不记鼠标历史/相机，不生成完整VASP输入。surface_geometry.py抽取同一ASE数值核心，原ase_surface API继续可用；surface_replay.py嵌入核心和request，独立Python只需ASE，建议同版本。Bash使用p4v --surface-replay JSON 新目录，找不到p4v时回退导出机器p4v.sh；换机需有效p4v路径。已有目录拒绝覆盖。
- surface_cli.py在GTK/native导入前分流，复用现有60秒科学worker；默认脚本输出surface_rebuilt，可另指定目录。重建比较科学结构等价，不承诺原生/ASE写出字节格式完全相同。GUI打包spec补收集原始surface_geometry.py/dos_metrics.py供脚本嵌入，Windows诊断增加两脚本存在断言，未构建EXE或验收Windows/Mac。
- 本机Linux/WSL：8既有Surface科学回归、3新增重放测试通过，人工Cu预设及自定义CIF删除后，隔离Python、无DISPLAY/Wayland的真实Bash/CLI重建保持元素顺序/晶胞/坐标/固定标记/层号/request；检查原生Bottom重定位、空格路径、坏JSON与防覆盖。实际Surface GTK保存四文件、预览/Center/Bottom/来源/失效/取消及10 GTK回归通过。3依赖工具、清单、语法/diff通过；日志/tmp/surface-replay-{core,tests,gtk,gtk-base}.log。未访问私有example/改依赖环境或重采快照；操作指南、架构、依赖源码索引和当日双语记录同步。当前完成，下一次启动生效。

## 多轨道按钮／双脚本／无界面DOS命令完成（2026-11-23）

- 用户要求Orbital单独一行d及5分量，多分量可组合、d与分量互斥；Spin移下一行。DosAnalysis用ToggleButton组及同步guard，最后一项取消回d；set_orbitals/orbital_name替代旧下拉，Use last DOS line可复制多个d分量，全部5项时用d。dos_selection.py统一原子/轨道解析，逗号或列表标准化/去重；d+分量拒绝，LM各分量原始密度先求和，指标算法不变。仅有汇总d的源仍需选d。
- p4v.py在GTK/native导入前分流位置参数：p4v DOSCAR atoms orbitals spin Emin Emax output.csv，也支持XML、显式--dos-analysis和帮助。dos_cli.py用既有科学worker/120秒/独占CSV，不开GUI；原子1起范围或all，轨道逗号、spin both/up/down，能量相对EF或full。少参数但明显原子选择意图也走CLI报usage，单文件GUI/图片导出路由保持原有逻辑。
- Export scripts一次生成同名.py/.sh，检查两者存在并用独占创建，异常清理本轮文件；原save_script单Python接口保留。Python为所选谱快照，不依赖原数据/p4vasp，仍可改范围；Bash重新读原数据，写出可编辑的p4v位置命令，非交互无alias时用导出机器p4v.sh函数回退，不source用户bashrc。默认输出分别_results.csv/_cli.csv，已有CSV拒覆盖，Bash支持第1参数另指定输出。换机需源文件及有效p4v路径，不将快照当VASP输入。
- Linux/WSL：10科学回归含组合/去重/冲突、2Python隔离重放、2实际CLI/双脚本测试通过（无DISPLAY/Wayland、禁止gi导入、DOSCAR/XML、含空格路径、少参数usage、已存文件保护、Bash真正运行并匹配数值）。真实GTK多选/d互斥/空选回d、组合计算、两导出对话框产生.py/.sh、非自旋灰显、最大化/复制/取消等通过，截图/tmp/p4vasp-dos-maximized-redraw.png已查看。10 GTK、33面板、58基础、3依赖工具/清单及语法/diff通过，日志/tmp/dos-multi-{core,replay,cli,gtk,gtk-base,smoke,base}.log。
- 本地私有Cu3Ru1额外无界面多轨道命令与相同后端结果一致，5项源哈希不变，输出仅/tmp/cu3ru1-cli-*；公开测试全为人工谱，不提交example/私有输出。命令指南/分析说明/架构/依赖源码索引及当日中英同步；无新依赖/环境，不重采快照/重编或Windows包，Mac/Windows未验收。任务完成，用户可重启GUI或直接用新命令。

## Spin三按钮与无自旋灰显（2026-11-22）

- 用户要求Spin下拉改Both/Up/Down按钮。DosAnalysis用互斥RadioButton隐藏圆点、三按钮局部紧凑CSS；对接set_spin/spin_name，Use last DOS line复用同一选择方法。只有实际TOTAL_DOS恰两通道才启用Up/Down；单通道或未知时Both并灰显另外两项。set_system仅读已READY缓存，ElectronicApplet原DOS读取后通知，不额外读文件或启动探测进程。结果/worker保持lowercase spin及原算法，不把非自旋Both乘2。
- Linux/WSL真实GTK通过3按钮逐一点击/互斥/请求映射，DOSCAR和XML切到单通道后两按钮灰显、Both实际分析，再切回双通道恢复；既有选择/脚本导出/最大化重绘通过。初轮普通宽度下按钮拥挤，局部减padding后检查Down右边界在面板内，截图/tmp/p4vasp-dos-{maximized-redraw,spin-nonspin}.png已查看。10 GTK、33面板、编译/diff通过；日志/tmp/dos-spin-buttons-{gtk,gtk-base,smoke}.log。
- 用法/架构/双语同步，未改科学函数或依赖/环境，不重复科学回归/快照，不触及私有example或打包Windows，Mac/Windows未验收。

## Energy Range单行紧凑输入（2026-11-22）

- 用户要求Energy Range/Emin/Emax一行。gtk3/dos_analysis.py改同一横向Box，两个Entry约4字符视觉宽度且不拉伸，空值占位Full；未设置输入长度限制，负数/小数仍完整读取，留空全网格及EF相对定义不变。
- 本机Linux/WSL真实DOS分析GTK通过计算/手动改参/导出/最大化重绘/紧凑窗口；截图/tmp/p4vasp-dos-maximized-redraw.png已查看，标题和两框同排。日志/tmp/dos-range-one-row-gtk.log，编译/diff/用法检查通过；不额外重跑未改科学算法，不触及私有example/环境/EXE，Mac/Windows未验收。当前用法与中英记录同步。

## 删除D_d(EF)结果项（2026-11-22）

- 用户要求删除EF处d投影态密度，dos_metrics去掉对应数值/定义元数据；GUI、CSV和新导出独立脚本共同只输出center/标准差width/window filling/Hilbert upper edge四项。积分范围/其余数值方法、Use last DOS line及脚本导出入口保留。
- Linux/WSL：9科学回归、2独立脚本回归及真实DOS分析GTK通过；投影选择幅度检查改用积分weight比例，GUI确认4行，最大化/重绘、实际两种导出仍通过。截图/tmp/p4vasp-dos-maximized-redraw.png已查看。日志/tmp/dos-remove-ef-{core,replay,gtk}.log，编译/diff/当前用法核对通过。当前文档删除旧EF指标说明，历史更新条目不改。
- 本轮不读写/上传私有example数据，无依赖/环境/快照、原生重编、Windows/Mac验收；重启后生效，新导出使用四项结果。

## DOS精简界面与独立脚本导出完成（2026-11-22）

- 用户撤销删除Use last DOS line的要求，前一轮未提交的删除已撤回，按钮/逻辑/测试继续保留。用户明确range仍手填，不加预设；Energy Range (eV)下Emin/Emax，EF=0说明放输入提示。完成摘要仅atoms/轨道/自旋/E−EF上下限；来源/求和/重采样详情留tooltip/CSV。顶部d-band analysis (pymatgen-实际版本，点改横线)，通过独立worker的metadata-only action查询并按解释器缓存，不在GUI导入科学库/写死版本。
- Cancel按钮改Export Python script，结果有效且未计算时可用；参数/换源/离开仍自动取消。dos_metrics.py抽取原数值方法，analyze保留选择与读取，结果附隐藏replay快照（选中投影之和的完整相对能量谱、单代表site API容器、元数据），CSV不塞谱。dos_replay.py导出同一核心代码+快照，独立Python/pymatgen即可重算，不依赖p4vasp/原DOSCAR/XML；可CLI改积分限，不能直接换原子/轨道/自旋，代表site不等于完整计算结构。脚本和输出CSV独占写入，不覆盖。
- 此前五指标重构在本地真实两来源×两元素与原结果一致（只记定性，不公开私有数值）；其后用户要求删除D_d(EF)，当前状态见上方删除记录。
- Linux/WSL：9原科学回归、2独立脚本测试通过（删除合成源文件、-I清环境运行、结果一致、改窗口/拒绝覆盖）；真实GTK包含初始版本/精简摘要/保留最后线/选中原子、实际CSV及脚本对话框、改参取消、最大化与复制/缺库提示通过；10 GTK、33面板、58基础、3依赖工具/清单、编译/diff通过。日志/tmp/dos-export-{core,replay,gtk,gtk-base,smoke,base}.log；实际私有Cu数据的两个来源精确界面文本和本地独立脚本匹配通过，截图/tmp/cu3ru1-controls.png已查看，5源文件哈希不变，私有生成脚本/结果仍仅/tmp/cu3ru1-script-*，example不跟踪/上传。
- 文档/依赖用途源码索引/中英同步；无新依赖/环境变化，不重复采快照/原生重编或Windows包/Mac验收。当前任务完成，重启GUI载入控件改动。

## 本地私有Cu3Ru1实际数据验证（2026-11-22）

- 用户新放example/Cu3Ru1，明确禁止上传该目录。已在本机.git/info/exclude加入/example/Cu3Ru1/，git check-ignore确认DOSCAR/POTCAR排除、git ls-files确认无跟踪；以后不得stage/上传该目录，也不把其中结构/输入/结果数值/截图复制进公共测试或文档。该本地exclude不随仓库同步，其他设备仍需遵守用户限制。
- 实际DOSCAR/vasprun.xml分别按Cu、Ru分析，解析一致性及独立NumPy中心/宽度积分核对通过；真实GUI从DOSCAR启动、File/Open XML、两个元素/五指标、旧Local DOS负向自旋投影、最大化True/改轨道/重建画布/恢复、图页/缓存/边缘像素、GUI不导入pymatgen通过。不是独立物理基准或其他参数/任务验收。临时脚本/日志/截图/结果仅在/tmp/cu3ru1*，不提交；5项源文件DOSCAR/XML/POSCAR/CONTCAR/INCAR前后SHA256一致，没有测试写入该目录，未读取或上传POTCAR内容。
- 发现真实VASP文本舍入导致步距略有变化，原严格uniform判断将upper edge错误置Unavailable。现Hilbert单独把与同端点/点数等距网格偏差≤平均步长5%的谱线性插值，保留原始moment/filling，notes/CSV显式记录插值点数/步长/最大调整；超过判据仍Unavailable。5%为数值限制而非物理误差保证。新公开回归为独立生成的人工舍入谱，未使用私人数据。
- 9项pymatgen回归通过（新增SciPy独立Hilbert参考，原显著非均匀仍拒该指标），4 DOSCAR读取回归通过；本机实际数据四组合和GUI通过，截图/tmp/cu3ru1-maximized.png已查看，哈希/ignore检查通过。日志/tmp/cu3ru1-{analysis,gui,synthetic-regression,reader-regression}.log；范围仅Linux/WSL、实际数据与合成回归，不重跑无关整套GUI、不新增依赖/重复快照/重编或EXE。仅通用修复/合成测试/说明和记录可按工作流推送，私有目录保持本地。

## DOS最大化后半图／重绘同步修复（2026-11-22）

- 用户报告最大化后点右侧选项左图半幅、似卡住。本机最初简单最大化/改参未复现同样现象；进一步构造已realize的DrawingArea重建GraphCanvas且不产生新size-allocate，确认图页仍790x610而实际控件1000x700，新缓存默认500x400，新增GTK回归修复前失败。不是声称复现了用户桌面的全部触发条件。
- GraphCanvas.render每次绘制前按已realize控件同步world.page_size和Cairo缓存，覆盖重建/错过分配事件边界。ElectronicApplet对分栏size-allocate、右侧改参/结果变化合并单个GLib idle重绘，布局稳定后updateSize；销毁取消排队，保留数据和world缩放范围，不重算科学结果。
- 本机Linux/WSL：新增重用已realize控件测试后GTK10通过（含默认缓存/当前页/背景缓存尺寸及zoom不变）。真实分析GTK最大化状态True，最大化后重建canvas/3轮轨道自旋切换/计算/恢复均通过area/world/surface尺寸及边缘背景像素检查，原曲线/zoom、两来源、取消/复制/真实CSV对话框仍通过；截图/tmp/p4vasp-dos-maximized-redraw.png已查看。CSV夹具初轮目标变为x导致期望文件失败，改响应时显式设置目标后通过，未改导出实现、未归因具体桌面输入来源。
- 当前旧DOSCAR真实启动/切面板/FileOpen/XML刷新/能带/resize通过；33面板、58基础、7PS/PDF及5其他图形导出通过，语法/diff通过。日志/tmp/dos-redraw-{buffer-before,buffer-after,gtk,legacy,smoke,base,vector,other-exports}.log，最初简单场景日志/tmp/dos-redraw-repro.log保留。GTK/GI既有弃用告警保留。
- 仅GUI绘图同步，无科学算法/依赖/环境变化，无新快照、原生重编/Windows包/Mac或另一台设备验收；用户实际桌面需重启后复核。操作/架构和中英记录同步，当前已确认边界修复完成。

## DOS左右分栏布局完成（2026-11-22）

- 用户要求左DOS/右pymatgen且直接显示。ElectronicApplet将自身graphwindowapplet.glade的vbox2（原工具栏+graph_box）移入横向Gtk.Paned左侧滚动容器，右侧DosAnalysis由Expander改Frame。菜单保持顶部，共享Glade/其他GraphWindowApplet不改；右侧两列参数/两行按钮、属性文字换行，表格占剩余高度，均可滚动。
- 分隔线首次实际分配按58%/42%初始化，之后不重置用户拖动；左plot显式hexpand/vexpand，避免新增Viewport时仅显示默认400像素高度。小窗口左侧也可横向滚动访问原工具栏/整图，右侧控件和缺库提示滚动访问，不宣称任意尺寸无裁切。新测试900x650请求在本机实际分配952x739，不能记成900x650通过。
- 本机Linux/WSL实际GTK分析流程通过Frame初始直接可见/左右位置、异步DOSCAR/XML/选中原子和最后线/CSV对话框/剪贴板/取消换源/缺库提示、分隔线保留和小窗口。常规/小窗截图/tmp/p4vasp-dos-analysis-side{,-compact}.png已查看；常规窗图与5项结果同时可见，小窗使用滚动。初轮Pango错误导入从adapter改gi.repository，位置断言改translate_coordinates（有独立Gdk窗口时allocation.x是子窗口本地坐标），不是左右实际反置。
- 布局迭代中4旧DOS启动/Open/切面板/自旋/能带/resize、最终GTK9/面板33通过；最终源码另复查DOSCAR旧流程，证据见/tmp/dos-side-{gtk,legacy,final-legacy,gtk-base,smoke}.log。无科学计算/解析/依赖改动，不重复科学数值测试或快照；Mac/Windows未测、无原生重编或EXE。本轮仅布局，操作/架构与中英更新同步。

## DOS+pymatgen首版集成完成（2026-11-22）

- 用户要求保留原DOS绘图并增加分析。DOS+bands仍由ElectronicApplet/GraphWindowApplet→graphwindowapplet.glade/GTK3 adapter绘制；新增折叠、限高可滚动的gtk3/dos_analysis.DosAnalysis，不改共享Glade或旧菜单/图线操作。按元素或1起原子、全部/单个d轨道、both/up/down及相对EF窗口计算五项，复用结构选择/最后DOS线的原子自旋，明确不复用线倍率/符号。可复制整表/文字单值，真实CompactFileDialog独占CSV导出附完整定义/对象/版本/来源/范围，不覆盖。
- dos_data.py为纯标准库共线DOSCAR投影读取，DoscarSystemPM提供PARTIAL_DOS(_L)给原Local DOS控制；支持spd/spdf和9/16lm、1/2spin。检查截断/块数/网格/负值/非有限数及SOC标记。无投影总DOS旧读法不变。DOSCAR分析需匹配显式元素符号VASP5 POSCAR优先/CONTCAR次选，不读取POTCAR；核对原子数但不能验证同数异顺序。SOC/非共线拒绝，17列单spin缺INCAR布局歧义拒绝。XML由科学worker内Vasprun读取，不读取POTCAR/本征值。
- dos_analysis.py在共享science解释器短进程，通过BulkTask120s/取消/回调；主GUI不导入pymatgen。改参数/换源/离开/销毁取消并拒过期回调。独立脚本初测发现项目uuid.py遮蔽标准库，移除脚本目录、保留lib入口后清PYTHONPATH协议通过；XML汇总OrbitalType与lm Orbital均处理。InstallHint新增可选bundled参数，pymatgen不误报旧Windows已包含；真实GUI初测发现no-show-all令错误提示不可见，显式show修复。
- 科学定义：center与标准差width通过pymatgen，窗口端点插值；filling为窗口内≤EF积分/窗口总积分（自行梯形/EF插值，非pymatgen严格<0且无窗口的原方法，非投影电子数）；upper edge为完整所选d谱Hilbert变换在窗口内的峰位置，非均匀原网格返回Unavailable；D_d(EF)在完整网格插值且不除原子数，EF不在网格返回Unavailable。原始正spin密度求和，不取图中负号、不用abs掩盖坏值。详见doc/dos-analysis-zh.md。
- 2026-11-22本机Linux/WSL现有science环境：8实际pymatgen数值/读取/清PYTHONPATH新进程/CSV测试通过，含高斯解析中心/标准差/CDF/EF值/Hilbert峰近似、DOSCAR/XML等价、轨道/自旋/选择/范围、聚合、零/负权重/非均匀/错结构/截断等；4旧DOSCAR测试含原投影数组通过。真实GTK通过异步tick、旧曲线不变/GUI未import科学库、两个文件源、结构选择/最后线复用、原Line下自旋负向绘制、剪贴板、真实导出对话框、改参/取消/换源拒过期及模拟缺库提示；截图/tmp/p4vasp-dos-analysis.png已查看，分析区域通过滚动访问完整结果。
- 4旧真实启动/File/Open/反复切面板/XML/DOSCAR-only/自旋/带图/resize通过；9 GTK、33面板、58基础、3既有通用进程取消/超时、3依赖工具/清单、语法/diff通过。首次sandbox GTK9全skip不算通过，授权显示后9实际通过；新reader测试曾误import GUI导致无display中止，已把Line检查移到GUI测试，reader恢复独立。新GUI首次startup等待不足夹具改等待实际frame，不算应用修复。日志/tmp/dos-analysis-{core,old-reader,gtk,legacy-gtk,gtk-base,smoke,base,transport}.log。
- 用法/架构/安装/目录及双语同步；通用进程测试初轮发现前轮统一环境后缺库文案断言仍指向旧install-ase，现同步新入口后3项通过；无新依赖/环境变化、不重复采快照、不重编原生/打包Windows，不声称Mac/Windows或用户真实DOS文件验收。当前任务完成，后续用户实际文件检验；偏度/峰度、批量每原子报告等未自动扩展。

## 统一科学环境完成（2026-11-22）

- 用户明确要求ASE/RDKit/pymatgen同环境。install/install-science.sh创建.venv-science，install/science-requirements.txt唯一维护三项直接依赖版本，安装后pip check及install/check-science.py实际计算检查；原install-ase/rdkit/pymatgen三个入口转发，不再新建各自环境；Bulk/Surface/SMILES/振动可复制提示统一为install-science，实际Bulk复制/剪贴板断言通过。GUI仍独立，旧目录未删除。
- model_worker.scientific_python统一查找：显式功能变量优先、其次P4VASP_SCIENCE_PYTHON、.venv-science、旧功能环境；ASE/RDKit worker共用，结构导入/Surface/热化学跟随ASE入口；默认冻结Windows仍使用随包worker。pymatgen仅安装/解析器接口准备，DOS分析GUI尚未实现；Windows构建源仍原独立模型worker体系，不自动加入pymatgen或重建EXE。
- 本机Linux/WSL实际安装成功，/usr/bin/python3首次venv因缺ensurepip失败，默认python3重建后安装成功；最终目标解释器报告Python3.14.4、ASE3.29.0/RDKit2026.9.2/pymatgen2026.10.24，目标元数据快照doc/dependencies/snapshots/2026-11-22-linux-science.json。快照source_revision为安装时HEAD5f303bd，带本轮未提交清单，非最终提交/锁文件；无覆盖旧快照。分发包元数据不等于完整原生依赖验收。
- 实际检查：ASE Cu构造、RDKit嵌入/UFF、pymatgen CompleteDos解析矩形谱中心/宽度独立解析值、Vasprun导入通过；pip check无冲突。6 Bulk、8 Surface、5 RDKit、10振动热化学、3worker路由/隔离、3BulkTask、4SmilesTask、58基础、3依赖工具及清单/语法/diff通过。真实Smiles GTK生成/预览/导出/取消通过；真实Bulk GTK先完成生成/32原子原生预览/保存，再在既有480x320窗口尺寸断言失败，不写整套通过，已知cmatrix/VisSync退出告警保留。日志/tmp/p4vasp-science-install.log及/tmp/science-{bulk,surface,smiles,vibrations,tasks,smiles-task,base,bulk-gtk,smiles-gtk}.log。
- 当前安装/操作指南及双语历史同步，Mac/另一设备/Windows未验收；用户本机源码重启即可用科学环境。下一步是DOSCAR投影与pymatgen分析接入，不把本轮环境统一说成d-band界面实现。

## pymatgen安装入口准备（2026-11-22）

- 用户确认d-band分析方向并要求类似ASE/RDKit的安装脚本。新增install/install-pymatgen.sh，独立.venv-pymatgen（gitignore），检查Python≥3.11，精确版本仅脚本维护；安装后检查CompleteDos四种指标接口及Vasprun导入，不导入GTK/改ASE或RDKit。发行来源https://pypi.org/project/pymatgen/及官方releases核对。
- 清单新增pymatgen角色/安装来源，安装指南含复制命令和实际安装后快照命令。bash -n、依赖清单检查、3项DependencySnapshot测试、diff通过；本轮未执行网络安装、未创建环境，因此不采虚假新快照，不声称科学接口实测或Mac/Windows通过。Windows包不变。
- 待办：DOSCAR投影解析、pymatgen独立worker与GUI选择/分析/导出仍未实现；用户已表达方向，下一步围绕该功能继续，不能把安装脚本视为DOS分析交付。

## p4vasp data个人覆盖完成（2026-11-22）

- 用户报告git pull后自定义值被重置及重启不生效。源码确认原表直接写跟踪文件、viewer强制共价显示半径、INCAR单独读取程序JSON；改ResourceStore默认periodic/incar为个人字段差异覆盖，位于~/.p4vasp/resources/{periodic,incar}.json。默认数据不改，未编辑字段跟随上游；显式root工具/旧测试保持原直写，user_root可用于隔离测试。
- util.getAtomtypes在旧home/CWD XML后仅重放明确保存字段，保留无个人覆盖时旧优先级；viewer_style原生/振动共享读取显式显示半径，默认紧凑共价外观、H已有1.5显示倍率和共价成键阈值保留。INCAR generator统一ResourceStore读取；不表示每个建模任务自动启用Magmom/U/J（单原子等原有策略不变）。Save/Reload状态说明个人路径，重启使缓存生效。
- 本机Linux/WSL：新独立进程测试验证默认文件字节不改、模拟上游变化后覆盖保留且未改字段更新、过期编辑冲突、legacy XML优先级、mass/RGB/radius及INCAR三项消费者、双文件失败回滚/清空；真实GTK个人表编辑Save/重新构造读取及状态通过。9元素、5资源、58基础和原有Resources GTK集成通过；语法/diff通过。日志/tmp/personal-{core,elements,resources,base,gtk,gtk-profile}.log。原Resources GTK退出仍有已知cmatrix析构None告警，不算新修复。
- 文档/双语同步，无依赖或环境变化、原生重编/EXE/Mac/Windows验收。新旧本机设置不被代码主动清理，已经被旧更新丢失的内容只能从既有备份找回；不把历史自定义仓库数据自动认作个人覆盖。当前任务完成，下一步由用户指定。

## Surface Center／Bottom完成（2026-11-22）

- 用户要求居中/靠底按钮，Bottom最低z=0.1Å。SurfacePage新增互斥按钮，生成前传placement参数，生成后用私有Structure副本即时平移，GUI不导入ASE、不重新切面/读取源。中心为ASE几何包围盒中心；Bottom保留晶胞高度/总真空，默认20Å空隙分配为底0.1/顶19.9，保留原子间距/排序/层号/F/T。真空输入Bottom标签改Half total vacuum，metadata记录placement/vacuum_bottom/top，vacuum_each_side为null。
- ase_surface.position_offset共用于worker/本地结果，普通writer保留头/旗标，局部17位数值重写避免其10位Vector格式导致Direct坐标回读约7e-10Å漂移（初轮核心/UI严格检查失败后修复，未放松容差）。gap≤0.1拒绝Bottom，不擅自扩胞；0.1仅初始留边，不承诺优化后不跨界。
- Surface原生预览默认侧视、显示晶胞并刷新；StructureWindow.fitToStructure新增可选include_cell，默认False保持Show/Control原拟合。共享模型预览按请求重置cell显示，避免影响后续gas/bulk。
- 本机Linux/WSL：8 ASE核心通过，与独立Atoms.center(axis=2)对照、0.1/上下真空、晶胞/距离/标记/重复切换/源不变/坏真空；真实Surface GTK验证按钮/动态标签、原生预览、Bottom保存POSCAR+JSON及旧流程。1 Models惰性、9 GTK、58基础通过；原生Show像素初次[0,0]失败，未改绘图代码，git HEAD原实现及当前复查均[0,45]通过，记录捕获时序波动而非画质修复。日志/tmp/p4vasp-slab-position-{core,gtk,show,show-baseline,lazy,gtk-base,base}.log，Center/Bottom截图/tmp/p4vasp-surface-{center,bottom}.png已查看。
- 用法/架构/双语同步，未来Windows模型诊断加入Bottom坐标验证；本轮仅源码/语法，不重编原生/构建EXE或跨平台验收。不引入依赖、不采重复快照；源码重启生效，现有Windows包不含Surface/本次定位功能。

## 当前完成：ASE Surface首版（2026-11-22）

- 用户授权先做Surface。Models→surface由空框架改为惰性滚动SurfacePage，保持五标签/左右入口不变。ase_surface.py使用现有ASE构建fcc111/100/110、bcc110/100/111、hcp0001模板，或Bulk结果快照/用户POSCAR/CIF按(h k l)切面；使用SurfaceTask复用BulkTask独立进程/60秒/取消机制，GUI不导入ASE，不引入pymatgen。
- 参数含明确元素/a/c、原子层或ASE等价层、面内重复、每侧真空、底部几何固定层/容差。自定义指数基于输入晶胞，不自动常规胞化；指数公因子约去。用ASE get_layers/FixAtoms，替换输入旧约束；元素稳定分组后层号/固定标记与POSCAR行序对齐。10000原子/数值/退化检查；源输入不改。预览固定层标记圈，shared model preview清旧选择以免向Bulk/gas泄漏。
- 保存新目录POSCAR+surface.json（参数/版本/层号/嵌入自定义体相），不覆盖已有目录；首版无独立重放脚本/INCAR/KPOINTS/POTCAR，无终止面枚举/极性稳定性判断/吸附物放置。默认Cu/fcc111/a3.615、4层2x2、每侧10Å、固定底2层→16原子8固定；自定义equivalent layers不等同几何原子层。详见doc/ase-surface-zh.md。
- 本机Linux/WSL GUI /usr/bin/python3及已有.venv-ase ASE3.29.0：6核心专项通过全部模板、Cu111解析层距/双侧真空/掩码、负指数/自定义源、CIF混合元素与可移植源、坏参数及独立/Windows-source dispatcher协议。真实Surface GTK通过惰性初始化、预设指数显示、异步响应/原生16原子8标记、Bulk/实际文件导入、新目录保存/防覆盖、失效、模拟取消回调及显式page.destroy；不是整机正常退出/实际Surface进程取消的全面验收。3既有通用任务测试另覆盖真实进程取消/超时。
- 1 Models惰性含Surface设置保留、Resources复制/表格编辑集成、9 GTK、58基础、33面板、3依赖工具及清单检查通过；编译/diff/文档核对通过。日志/tmp/p4vasp-surface-{core,gtk,task,lazy,resources,gtk-base,base,smoke,dependencies}.log，页面/tmp/p4vasp-surface-page.png、原生固定层/tmp/p4vasp-surface-preview.png已查看。初轮发现文件选择器返回str需Path转换（实现修复），预设(hkl)显示同步也已核对；offscreen父窗口/父销毁夹具改真实GtkWindow及显式page.destroy后通过，未将夹具变动写作应用修复。ASE/NumPy弃用及既有cmatrix退出告警保留。
- Windows worker/spec及未来--check-models新增Surface生成预览保存检查，但本轮仅源码/语法/ASE源协议，不构建EXE、不声称Windows/Mac验收，11月21日包不含Surface。既有ASE依赖用途/源码索引同步，无环境或版本变化，不重复采快照。界面/安装/架构/双语同步，当前首版任务完成，无自动继续复杂终止面、吸附物或Windows构建的任务。

## 当前交付完成：11月21日Windows版

- 用户要求的最新Windows EXE已完成。冻结源码f5de130ec89e55a76431d0edf8280a609abdd88e，包含此前鼠标导航、H球1.5倍、OUTCAR_*及OUTCAR-*识别、Control/Show实时22段和shell安装收尾改动；未继续额外清理/功能开发。此前三文件连字符改动已验证并提交，不再挂起。
- EXE：C:\msys64\home\lqlhz\p4vasp-checkout\dist\windows-releases\p4vasp-20261121-183334-f5de130e-cbhlyoey\p4vasp.exe；同级p4vasp-20261121-183334-f5de130e-cbhlyoey.zip及.zip.sha256，157639531字节，SHA256=899c35382a75ed3a455c38276eee93608924f73e5e92039f3f79e587ed8f3336。保留整个目录的_internal和model-worker，不单拎EXE；未另复制桌面，旧发行包保留。
- 当前Windows UCRT64完整原生编译/冻结成功，隔离环境runtime/gui/models均ok=True/frozen=True，含复制/剪贴板、图形/PNG/固定标记、ASE导入与32Cu建模预览保存、RDKit乙醇生成预览导出和取消等既有成品检查。独立SOURCE-COMMIT、43布局/旧Glade缺席、ZIP CRC/SHA256核对通过；不等于逐项新功能人工鼠标或全部科学场景验收，另一台干净Windows未测。
- 发布基线依赖快照：doc/dependencies/snapshots/2026-11-21-windows-{gui,model}-f5de130e.json，实际目标解释器采集12/22项元数据、GUI Python3.14.9/UCRT ABI与worker Python3.13.17/MSVC ABI分开；工具/清单摘要及源码核对通过，不是冻结DLL清单/锁文件。依赖清单检查及3项snapshot工具测试通过，未手工升级依赖。
- 日志位于Windows checkout build/windows-update/f5de130e-rkgbsiva，成品报告为dist/windows-releases/p4vasp-20261121-183334-f5de130e-cbhlyoey-checks；Linux构建启动/tmp/p4vasp-windows-20261121.log，58基础/频率GUI准备验证/tmp/p4vasp-exe1121-{base,frequency}.log。指南/双语/记忆同步；后续纯文档提交不改变冻结源码，无待自动构建任务。

## 当前任务完成：Control／Show实时细节约70%（2026-11-21）

- 用户因画质提高后操作慢要求约70%质量。Control Glade/StructureWindowControlApplet→StructureWindowApplet→StructureWindow共用原生OpenGL，不改GTK布局；viewer_style.INTERACTIVE_PRIMITIVES_RESOLUTION=22（原32）。StructureWindow在创建窗口/绘制器之前设原生默认值，适配首次GL init读取默认的机制，固定22避免每开窗口重复乘0.7；也影响使用StructureWindow的模型预览，不改Cairo振动预览。
- 保留晶胞1像素线/抗锯齿/光照、H显示倍率、原子/成键/相机/数据；分段22/32≈69%，sphere stacks20→13，球面面片约45%。未测交互FPS、不保证主观画质/速度比例。独立导出Quality/分辨率/预设不改；原生截图反映当前实时画质。
- 本机Linux/WSL实际ShowQuality通过22默认值、细线抗锯齿灰阶[0,45]、相机/结构/成键/重开保持；真实Control XDATCAR初末帧/步进/播放停止重启通过；14个headless导出检查通过。截图/tmp/p4vasp-interactive70-show.png已查看（由原生TGA经系统loader转换）；首次sandbox loader受D-Bus权限限制，允许显示后读取成功，非渲染故障。日志/tmp/p4vasp-interactive70-{show,control,export}.log，编译/diff/文档检查通过。
- 无依赖升级/原生重编/跨平台或EXE打包，源码重启生效。当时另有OUTCAR-命名扩展的三文件未提交，未混入渲染提交；随后Windows任务中在f5de130完成重新验证、记录和推送。原先其他旧接口待办仍不自动执行。

## 频率文件OUTCAR_freq识别修复（2026-11-17）

- 用户报告重命名OUTCAR_freq打不开。确认SystemPM.getSystem仅匹配OUTCAR，File/Open/CLI误走POSCAR；振动页显式读路径原已支持任意名。增加不区分大小写的OUTCAR_*前缀识别，保留OUTCAR及其他文件分派，不自动猜邻目录文件或放宽内容校验。
- 新TestSystemPM路由检查覆盖OUTCAR/OUTCAR_freq/outcar_FREQ/OUTCAR_2026、OUTCARLIKE负例及坏内容异常不回退。修前58基础1失败，修后58全通过。testVibrationsGtk改用真实合成OUTCAR_freq，CLI、实际File/Open选择及振动页CompactFileDialog全部通过，后续播放/Scale/POSCAR标记/热化学/异步回归通过，输入字节保持检查通过。
- 本机Linux/WSL /usr/bin/python3 3.14.4显示环境，证据/tmp/p4vasp-outcar-name-{before,base,gtk}.log；编译/diff/文档核对通过。未提供用户原始文件，故未独立核验其内容；未跨平台、原生重编、升级库或重打EXE。memory/指南/usage/架构/双语同步，源码重启生效，既有Windows包未包含此修复。

## 氢球半径显示放大1.5倍（2026-11-17）

- 用户认为H太小，按1.5倍（非加1.5Å）实现。viewer_style.ball_radius只放大H；covalent_atomtypes在显示副本改radius不改covalent，作用于Show及分子预览。ModeView新增ball_radii画球，radii保持原值用于bonds，防止放大球导致额外成键。元素资料/质量/坐标/导出不变，非H及整体尺寸控制不改。
- 本机Linux/WSL实际GTK 6导航/显示检查通过（5原导航+1新H检查），核对H倍率、非H不变、原子表不变和边界附近只保留原C-H键；首轮测试把无向键端点顺序当作固定顺序而失败，修正夹具后通过。截图/tmp/p4vasp-hydrogen-radius.png已查看。原生ShowQuality实际Cu窗口/抗锯齿/相机状态检查通过；原生H样式副本值已核对，但未单独截图H原生窗口。日志/tmp/p4vasp-hydrogen-{radius,show}.log，编译/diff/文档核对通过。
- 指南/架构/双语同步；未重复整套9 GTK/57基础/33面板，不把前批通过算本批。无依赖升级/原生重编/跨平台或EXE构建；源码重启生效，既有Windows包不含本次改动。当前无自动继续任务。

## 当前任务完成：Vibrations鼠标导航对齐Show（2026-11-17）

- 用户要求以Show为准统一振动预览鼠标操作。入口Vibrations工具栏/菜单→vibrations.glade→VibrationsApplet→VibrationsPage→gtk3/mode_view.py；保留布局和Show原生实现。源码对照VisNavDrawer.cpp/vecutils.cpp：左键旋转、Ctrl左键屏幕法线旋转、中键平移、右键水平exp(.005dx)缩放；按下快照计算整次拖动、矩阵组合及旋转平移匹配Show正交导航。保留预览滚轮缩放，支持smooth、忽略水平滚动；释放/丢grab清拖动。
- 相机状态独立于坐标，模式/播放保留；Cell/晶胞fit仍重置pan/zoom。Shift左键在Show是编辑框选，预览只读不新增选中、不旋转；后端投影/光照及预览缩放安全范围仍有差异，不宣称所有编辑手势或逐像素相同。
- 本机Linux/WSL /usr/bin/python3 3.14.4、有DISPLAY：新5项真实GTK信号检查通过，与现有原生createrotmat3da系数（与4x4同式）核对组合旋转/屏幕roll，覆盖中键/右键/释放/grab/普通及smooth滚轮/数据不变。独立截图/tmp/p4vasp-mode-navigation.png已查看。完整合成OUTCAR GUI测试增加播放/换模式保留pan并通过，含Scale/导出标记/热化学/异步清理；日志出现2次alloc_needed绘制告警，未单独定位，不用该集成截图作完整布局验收。
- 3周期几何、9 GTK、57基础、33面板通过，Python编译/diff/文档检查通过。日志/tmp/p4vasp-mode-nav-{test,vibrations,geometry,gtk,base,smoke}.log。未操作真实用户OUTCAR、物理鼠标操作原生Show、跨平台、原生重编或EXE构建；11/14 Windows包不含本次修复。指南/架构/11月17日双语同步，无自动继续任务，按新指令接手。

## 安装收尾按shell配置（2026-11-14）

- 用户指出Mac末尾不应统一source bashrc。finish-install.sh恢复按SHELL选择：zsh用ZDOTDIR或HOME的.zshrc，其余沿用.bashrc，显式P4VASP_SHELL_RC优先；提示实际写入路径。仍用bash install.sh，不加载/迁移旧用户配置。此前统一bashrc记录为旧行为。
- 本Mac Bash3.2下特殊路径alias单引号拼接失败，改printf %q生成完整alias值；临时rc特殊路径/幂等/备份/权限/符号链接、zsh加载调用/自定义覆盖、失败/deps-only测试通过。初次5项中3失败：旧引号、Linux无display夹具在Mac不适用、zsh命令解析需eval；分别修实现和夹具后5项通过，10统一安装检查通过。使用临时配置和启动stub，未修改真实用户rc/安装依赖/运行GUI或重编原生。
- install.md/usage_commands.md/入口help同步。下一步按新指令；现有用户若仅source zshrc，旧bashrc里的alias不会自动迁移，应在后续安装时按新逻辑配置。详见update_history/update_2026_11_14.md。

## 当前接手检查点：保存与Windows交付完成（2026-11-14）

- 用户决定保留轻量复制入口、不扩展AI，本次收尾和Windows构建已完成。源码基线58e353dc12181e0b4c17604479c90f16bd480ac7（含全部近期修复、清理、Models按需加载和复制入口），既有修前标签/本机备份及旧发行包保留。工作区仅用户XDATCAR未跟踪，不读不删不提交。
- 新EXE：C:\msys64\home\lqlhz\p4vasp-checkout\dist\windows-releases\p4vasp-20261114-221532-58e353dc-uhsvnjm6\p4vasp.exe；同级p4vasp-20261114-221532-58e353dc-uhsvnjm6.zip及.zip.sha256，ZIP 157631180字节，SHA256=9130b10606b2822989b30f70bd6a8ac0cfd2b8fb628a951f058db2e473f17540。必须保留整个目录（_internal、model-worker），不能单拎EXE。未另复制到桌面。
- Windows UCRT64原生完整重编译/冻结成功，隔离环境runtime/gui/models三成品报告ok=True且frozen=True。涵盖43布局、保存对话框、复制摘要/完整POSCAR/INCAR及剪贴板、原生画图/PNG/固定标记、ASE读XYZ/32Cu建模/预览/保存、RDKit乙醇生成/预览/三输入导出及取消。ASE3.29.0、RDKit2026.09.1、worker Python3.13.17；SOURCE-COMMIT一致，独立ZIP CRC/摘要核对通过，包内无旧data/glade。
- 证据在Windows checkout：build/windows-update/58e353dc-ev9tc_kn（native/package日志），dist/windows-releases/p4vasp-20261114-221532-58e353dc-uhsvnjm6-checks（runtime/gui/models报告）。Linux启动日志/tmp/p4vasp-windows-20261114.log及准备检查/tmp/p4vasp-windows-prep-{models,context}.log。成品结果与先前Linux测试分开记录；仍非另一台干净Windows/全部科学场景/正常退出全面验收。
- 保留待办：Linux bulk紧凑窗口480x320断言旧/新均532x409，完整testBulkGtk不计通过；旧SQL驱动、字典旧排序及历史后端未全部清理。未升级依赖版本，不扩展AI或另启动性能任务。当前无待自动构建事项；后续按新指令继续。交付记录后续文档提交不改变已冻结源码，不因此重复打包。

## 手动ChatGPT问答：本地结构摘要复制（2026-11-14）

- 用户同意复制结构/参数并关注数字token；实现Edit→Copy for ChatGPT...（Frame动态菜单，无左栏/Glade改动）。默认摘要含来源、原子数、组成、物理晶胞矢量，无逐原子坐标；完整POSCAR和INCAR手动勾选，字符数不冒充token。无网络/API/自动浏览器/依赖，不自动产生API费。
- chat_context.capture_structure优先同一当前体系Show的原始序列/index并复制，否则INITIAL_STRUCTURE；不取渲染包装/隐藏/扩展，也不自动取Models/振动独立预览或未写回编辑。format_context只规范化私有副本用于晶胞摘要，完整writer保留源全部原子/固定标记；快照在对话框打开时固定，INCAR仅勾选读取并缓存。不是完整计算输入导出。
- 新4纯检查通过，覆盖摘要省坐标/物理scale、原数据不变、完整POSCAR回读含F/T、帧/体系选择和无结构。真实Frame菜单/GTK预览/双选项/懒读取INCAR/剪贴板回读通过；截图/tmp/p4vasp-chat-context.png白底离屏内容已查看（最初透明背景截图不作为完整视觉依据）。9 GTK、57基础、33面板通过，编译/diff及文档链接通过；证据/tmp/p4vasp-chat-context-{unit,gtk,base,gtk-base,smoke}.log。既有cmatrix退出警告保留。
- 界面指南/架构/双语同步；未发任何结构给聊天服务、未读取用户XDATCAR、原生/跨平台/EXE未验收，Windows仍最后。此功能完成；bulk紧凑窗口旧问题仍见流畅度检查点，不因本任务改写为已修。

## 流畅度第一批：Models按需创建标签页（2026-11-14）

- 用户授权优化运行流畅度，仍不升库/改科学公式，Windows最后。测量发现Models.initUI一次创建隐藏气相/bulk/元素表；改为首次switch-page构造，稳定host保持标签及bulk ScrolledWindow，实例复用保留输入/脏表；gas首次依构造扫描一次，重访仍刷新。必须host.show_all显示动态viewport。未改启动时的模块导入或把所有耗时转后台。
- 同一临时benchmark七次initUI、后六暖中位13.1256ms→5.1569ms（约61%减少，只计页面构造，不是全程序/首次标签打开/大文件/渲染收益）。证据/tmp/p4vasp-models-bench-{before,after}.log，脚本/tmp/p4vasp-models-bench.py；初始cProfile套smoke因os._exit未保存，改为直接runcall/initUI计时，不冒充完整启动分析。
- 新testModelsLazyGtk通过真实临时库/资源，验证隐藏构造/scan均0、首次scan1/重访2、只构造一次、新XYZ出现、选中分子charge/bulk字段/未保存表编辑不丢及viewport mapped。初始夹具未选分子导致charge被正常清空，已补明确选择；非应用修复。截图/tmp/p4vasp-models-lazy-bulk.png已查看。9 GTK、57基础、33面板和Resources网格/复制/保存检查通过，编译/diff通过。
- 限制：testBulkGtk真实ASE构建/32原子预览/保存取消等前序断言通过，但最终480x320紧凑窗口断言失败，实际532x409；通过git show读取066fa5f的ModelsApplet原实现注入对照同样失败，不能记全项通过。日志/tmp/p4vasp-models-bulk-{baseline,current}.log及bulk.log；普通原生窗口截图全黑不作视觉成功证据。既有cmatrix退出和PyGObject弃用警告保留。
- 当前优化及验证完成，界面指南/架构/双语同步；未读取/提交XDATCAR、重编原生、跨平台或EXE。后续优先定位bulk紧凑布局限制，其他流畅度瓶颈继续先测量再改，不自动启动库升级或Windows构建。

## 旧接口第九批：移除旧Glade目录及加载器（2026-11-14）

- 用户批准继续，删除data/glade全部44个旧布局/图片（264639字节）及util.loadGlade_old；Git保存历史，不复制归档。data/glade2无改动、loadGlade/GTK3适配器/历史会话类保留；仓库运行源码无旧函数/真正libglade导入残留。外部插件若曾调用已移除接口需迁移到现行资源，不提供假兼容别名。
- testGtk3资源检查改走真实util.loadGlade，新增每处文件图片按适配器路径查找并用GdkPixbuf解码；43布局和124图片引用通过。新跑9 GTK、57基础、33面板（GLUT除外）通过，Models截图/tmp/p4vasp-models-no-context.png已查看工具栏图标和元素表；不声明布局修复/完整科学验收。日志/tmp/p4vasp-remove-glade-{gtk,base,smoke}.log，编译/diff/文档及静态打包输入核对通过。
- GUI spec仍递归收集data，但本checkout旧目录已不存在，未改spec/执行PyInstaller，不代表旧Windows包已更新或ZIP减少同样大小。未升级库/重编原生/跨平台，用户XDATCAR未读未提交。Windows仍最后；下一步可核对历史绘图后端的真实调用及打包边界，不因缺依赖直接删除。

## 旧Glade与打包引用专项核对（2026-11-14）

- 用户要求核对，Windows最后。本轮不删除/改UI/改spec；报告doc/legacy-glade-resources-2026-11-14-zh.md逐项列14旧布局和30旧图片。旧目录44文件264639字节，30图片均与现行副本SHA256相同；14布局虽有同名现行副本但内容不同。旧frame标准XML解析失败，13份其余可解析，不算古老libglade可用性验收。
- 当前43布局124处文件图片引用按GTK3适配器候选顺序全部可解析、0旧目录、0缺失；loadGlade_old仅见定义但外部插件未核验。Windows GUI spec复制整个data，旧目录会随包进入；worker无项目data显式输入。此为静态配置证据，未执行Windows打包/估算ZIP收益。
- 新跑8 GTK资源/行为、33面板启动通过（不含GLUT），证据/tmp/p4vasp-glade-audit-{gtk,smoke}.log；逐文件临时JSON/脚本同前缀。无布局视觉修复声明/完整科学流程/跨平台/原生重编/库升级。下一步可成批删除旧目录和旧函数并验证现役资源；本轮尚未执行，用户XDATCAR未读未提交。

## 旧接口第八批：删除已退役构建文件（2026-11-14）

- 用户明确批准删除无用旧入口。删除src/Makefile、src/Makefile.MacOS、odpdom/Makefile及仅供前两者使用的src/Configuration.mk；不复制归档，Git保留历史。上一批临时P4VASP_ALLOW_LEGACY_BUILD开关随之撤销。install.md改为当前安装/重编译命令，diagnostic.py错误提示去除旧make/Makefile建议。
- 当前install/build-unix-py3.sh完整编译src/odpdom并链接Linux扩展成功，GTK/Cairo/_cp4vasp导入通过；8 GTK、57基础通过，bash语法、Linux安装器dry-run构建路由、Python编译和diff检查通过。证据/tmp/p4vasp-removed-make-{build,gtk,base}.log。不是Mac/Windows或完整GUI流程验收，无EXE/升库；原修前备份不变。
- 引用核对未发现现役构建使用删除文件。install/configure.py仍是独立历史配置生成器（根Configuration.mk，与删除的src配置不同），src/fltk-config.py/旧Glade/其他历史脚本本批未删除或执行，不宣称全部清理。用户XDATCAR未读未提交；后续继续逐项核对资源/历史工具，Windows最后。

## 旧接口第七批：旧构建入口保护（2026-11-14）

- 核对当前install.sh→平台bootstrap/wrapper→build-unix-py3.sh，后者直接编译src/odpdom，不调用三个旧Makefile。src/Makefile、src/Makefile.MacOS、odpdom/Makefile增加默认解析阶段停止提示，指向仓库根bash install.sh；保留原规则，显式P4VASP_ALLOW_LEGACY_BUILD=1可绕过，但不代表Python3兼容。clean同样受保护，install.md说明。
- 本机9项make -n检查通过（各all/clean默认拒绝无recipe输出、显式开关clean打印），日志/tmp/p4vasp-legacy-build-guards.log；5个当前入口bash -n及Linux install.sh --dry-run --build-only路由通过。未实际make/清理/安装/重编译/GUI/跨平台或EXE验收；MacOS命名Makefile仅在本机GNU make解析，不算Mac验证。
- 无库升级/资源删除/旧类移动；用户XDATCAR保留不读取不提交。下一步仍可评估loadGlade_old及旧data/glade逐项资源引用/发行包边界，需兼容证据后再归档；Windows最后，原回退标签不变。

## 旧接口第六批：Resources与旧SQL延迟加载（2026-11-14）

- 现役DBApplet/完整面板注册不再提前导入db或SQLSystemPM；LegacyDBApplet/CommitApplet仅在显式构造时加载getDatabase，旧结果选择时才加载SQLSystemPM。保留历史类名、模块路径、Glade、注册和会话处理；未删除SQL功能、迁移驱动或裁剪冻结依赖。修正Commit菜单注释，面板smoke仅对显式旧SQL面板注入空数据库。
- 新3项独立进程GTK检查通过：阻断SQL导入的完整Frame/注册/Resources/SetupProfile启动、合成旧XML类路径构造、合成旧选择回调。修前2失败，修后3通过；不连接用户数据库，不代表真实旧SQL/完整用户会话验收。Resources真实网格/复制/编辑检查通过，截图/tmp/p4vasp-online-links.png已查看；退出时既有cmatrix析构警告仍存在。
- 本机57基础、8 GTK、33面板（GLUT除外）、编译及diff通过。日志/tmp/p4vasp-sql-{isolation-before,isolation-after,resources,gtk,smoke,base}.log。无依赖升级、用户XDATCAR读取/提交、原生重编、跨平台或新EXE；Windows仍最后。下一步可评估无主旧构建/资源引用，先查打包及兼容边界，不据年代直接删除。

## 旧接口第五批：FIG/SVG及DATA/AGR核对（2026-11-14）

- 用户同意下一计划首项，仍不升级库/科学公式，Windows最后。真实导出基线复现FIG _makeCustomColor用%x格式化float；SVG默认Font.face只读赋值、旧Latin1声明与实际文本编码不一致、未转义XML及后备字体覆盖也经专项确认。DATA/AGR成功回读，未改实现/精度。
- FIG显式int RGB、常用字体名lower匹配，with管理UTF8输出以异常关闭。SVG UTF8声明+写入一致，SVG/XLink命名空间，去旧外部DTD，escape文字/quoteattr样式，本地构造字体列表不改Font，默认sans-serif；save委托save_避免重复写法。无需新库。
- 新testOtherGraphExports5项通过数据/AGR（原精度）回读、Unicode/XML/默认及列表字体不变、FIG颜色/转义/大小写、故障关闭。修前1通过1失败3错误；GUI探针最初DATA文件大小和data=None期望源假设已纠正，不计为应用缺陷。testVectorExportGtk扩展真实七格式按钮/扩展名、DATA数值、AGR项目读回、SVG XML、原PS/PDF及源DOS不变通过；GdkPixbuf现有SVG加载器独立渲染，/tmp/p4vasp-exported-dos-svg.png已查看（曲线/标签），无新增安装。
- 既有7矢量输出、5绘图值、57基础、8 GTK、33面板（GLUT除外）、编译/diff通过；日志/tmp/p4vasp-other-{formats-before,formats-after,exports-gtk,formats-base,formats-gtk-base,formats-smoke}.log。外部Xfig/Grace及PS/PDF阅读器/任意FIG Unicode字体/图像分支/跨平台/EXE未验收；DATA原g精度不等于全双精度无损。指南/架构/审计/双语同步，XDATCAR不读取不提交；原备份和标签不变。下一步按已定路线评估旧SQL/历史组件引用与会话兼容，尚未执行归档或库升级。

## 旧接口第四批：PS/EPS/PDF文件输出（2026-11-14）

- 用户继续，Windows明确最后打包。旧PS/PDF字符串写wb、PDF PathLike误走默认路径及压缩页Python2字节处理已修。新增piddle/fileio.py标准库ByteBuffer（Latin1单字节、实际tell偏移）及路径/二进制流输出边界；保留StringIO旧视图，拒普通文本文件流防UTF8/换行损坏；调用方流不关闭，路径with关闭，带前缀binary流xref保持绝对偏移。无全局getFileObject重写，其他旧后端不混入。
- PS先收集/编码尾部，finally恢复code/文档页标记；PDF先完整序列化再开路径，序列化失败不截断已有文件（非磁盘故障原子事务）。PDFStream长度按字节，zlib.compress+标准base64.a85encode替代旧字节算法，终止符不被换行切开。源pdfdoc保留原Latin1编码，未新增库/改默认压缩策略/坐标/科学数据。
- testVectorExport7项通过：真实中文/特殊字符路径PS/PDF、binary/StringIO不关流、压缩流独立解码、带前缀xref、多页混合压缩、拒文本流、编码失败保留文件及PS状态；独立核对xref/startxref对象偏移、声明流长和解码内容。修前5项失败，压缩检查最初需去除流末CRLF后解码，已区分检查修正。旧DrawingValues5通过。
- 实际testVectorExportGtk通过DOS Export Data对话框Export按钮的PS/EPS/PDF写出、扩展名匹配、PDF结构及DOS样本不变，截图/tmp/p4vasp-vector-export-dialog.png已查看；57基础/8 GTK/33面板（不含GLUT）、编译/diff通过，证据/tmp/p4vasp-vector-{before,after,gtk,base,gtk-base,smoke}.log。无外部PDF/PS阅读器/渲染器（未安装）、任意Unicode字体/旧图像分支/跨平台/用户数据/新EXE验收。文档状态与双语同步，XDATCAR不提交；旧字典排序/历史组件及其他已列接口仍待后续，不自动升库。

## 旧接口第三批：绘图值比较及除法（2026-11-14）

- 用户继续并明确Windows EXE最后统一更新。调用检查：现役Cairo透明色及PS/PDF状态缓存用==/!=，旧__cmp__未被Python3运算符调用；StructuredDictionary.__cmp__无现役调用/明确总排序语义，未改字典/序列化分派，不注入全局cmp。
- piddle.Color新增精确RGB __eq__，保留现有tuple哈希，避免旧加权亮度把不同RGB当相等；__truediv__复用原__div__，保留旧显式方法，不新增反向除法或大小排序。Font按face/size/bold/italic/underline相等并同字段哈希，face为可变list时正常不可哈希；构造/字段/只读属性不变。
- 修前4项值对象检查3失败1错误，修后5项（含PS/PDF文本流）全通过；protocol2/current pickle往返、不同颜色同亮度/哈希/列表字体/非同类/除零均核对，但未加载真实旧XML会话。2实际Gtk/Cairo像素检查通过透明clone不画/透明清屏及颜色除法+字体绘制，截图/tmp/p4vasp-drawing-values.png已查看。57基础、8 GTK、真实DOS缩放/刻度/样本保持、33面板启动（GLUT除外）、编译/diff通过；日志/tmp/p4vasp-drawing-{before,gtk,base,gtk-base,dos,smoke}.log。
- 新实际问题：临时路径PSCanvas.save/PDFCanvas.save均str→binary TypeError（PDF BytesIO同样失败），StringIO均生成成功；不是当前值比较引入，待下一批文件I/O修复，不宣称完整导出通过。无用户数据读写/升级库/原生重编/跨平台/EXE，XDATCAR保留不提交。审计/架构/维护说明/双语同步；下步可在现有授权方向处理该导出缺陷，Windows统一留最后。

## 旧接口第二批：VAC/FFT与滤波（2026-11-14）

- 用户“继续”按前批待办推进，仍不升级库。VAC.updateGraph数组/range的len(freq)/2改//2，保留Python2前半谱整数截断；fftGen及filter开关回调的两处.state改用get_active，六个输入/标签同步敏感状态。Read VAC→FFT及VAC/FFT/VAC+FFT菜单、四窗函数保留。
- 测试暴露默认7+7窗大于短谱时data未初始化，以及左边缘拟合位置偏移；新增共享单点拟合按start/stop裁边，position=index-start，项数限可用样本，供纯函数/调度生成器共用。保留历史dimension为项数，0旁路；无效滤波参数或VAC不足2样本提示且不覆盖原结果。原幅度Wss/0.7及频轴转换未改，不宣称科学归一化完整正确。
- 新testLegacyFFT六项（含子场景）：奇偶/4窗、解析8点单频、短序列大窗、两端多项式、坏参数及空/单点保护；与独立polynomial.polyfit及解析谱比较通过。前轮源码真实.state/未初始化data失败已复现；测试world双轴夹具补齐后通过。testLegacyVacGtk扩展真实按钮、过滤敏感、奇偶谱、实际下拉四窗/双图、信号异常捕获，最终截图/tmp/p4vasp-legacy-fft.png已查看。首轮真实控件暴露第二处.state及夹具缺POTIM，修正后全程重跑，不计失败通过。
- 既有6线程/VAC、57基础、8 GTK、33面板（GLUT除外）及编译/diff通过；证据/tmp/p4vasp-fft-{before,after,gtk,runtime,base,gtk-base,smoke}.log。无用户轨迹读取/跨平台/EXE/原生重编；XDATCAR不提交。审计/用法/维护指南/双语同步，旧布局裁字保留。仍待旧比较/序列化/历史分支及VAC物理时间轴/归一化等独立核验；不自动扩大成库升级/清理。

## 保存基线与旧接口修复第一批（2026-11-14）

- 用户授权保存当前能运行版本并开始；明确选择“先修复旧接口，暂不升级库”。修复前本机8 GTK及实际ASE导入/原生Show合成检查通过。源码49ff6cd建标签checkpoint/2026-11-14-before-legacy-interface-fixes并已推送；本机build/checkpoints/2026-11-14-49ff6cd-before-legacy-fixes保存Git源码archive、原有Linux扩展、三个新采环境快照及基线日志/README/SHA256SUMS，摘要全核对，临时独立目录解压+原生/源码导入通过。不是整机/venv镜像，标签不含二进制；本批不动库，原环境保留。备份目录已Git忽略，用户XDATCAR未纳入。
- Property.isPending以局部thread快照调用is_alive，保留现有默认has_threading=0；VAC七处clock换perf_counter，仅修改耗时显示，不改数值算法。A03比较/序列化/历史分支及所有包版本暂不动。
- 新testLegacyRuntime六项：真实Thread未启/运行/结束，Property真实require单次读取及notify（仅测试中启线程），单/多系统VAC含选择/跳帧与独立解析式1e-12比较。修复前2个isAlive及4个clock失败，修复后全通过；初始无显示导入崩溃及缺INITIAL_STRUCTURE测试夹具已纠正，不冒充应用修复。实际testLegacyVacGtk通过真实Read VAC按钮、调度/有限数值/曲线，最终1200宽截图已查看；旧左控制列仍裁字，未改布局。
- 57基础、8 GTK、33面板启动（GLUT除外）、编译/diff通过；日志/tmp/p4vasp-legacy-{before,after,vac-gtk,base,gtk,smoke}.log。未测FFT/滤波/真实用户轨迹、Mac/Windows或新EXE，无原生变更不重编。静态新发现VAC FFT分支len(freq)/2整数计数问题，记录候选而未混入本批，不能把VAC计算通过当FFT通过。审计报告/依赖维护说明/双语同步；本批完成，后续按明确新任务推进。

## 依赖维护第一批：统一目录与版本快照（2026-11-14）

- 用户同意先做清单/快照/安装说明，并强调长期维护。入口doc/dependencies/README.md；catalog.json集中分层用途、profile、来源和平台包映射，不重复维护精确版本或改变安装行为；缺GLUT平台项保留pending。现有安装/构建源继续是执行权威，未增加第二套安装器/锁文件。
- 新增标准库工具tools/dependency_snapshot.py：目标解释器执行，--check校验catalog/schema/源码引用；profile选择来自catalog同一处。读取发行元数据/原始Requires-Dist、平台/Python SOABI、Git及清单/工具摘要，输出只读JSON快照，独占新建拒绝覆盖；不import科学GUI库、不装卸包、不采用户/主机名、环境变量或完整解释器路径。全环境分发清单非最小依赖/活跃依赖图/锁文件/成品验收。
- 实际生成11/14 Linux gui/ase/smiles三个快照（73/15/4项可发现发行元数据）存doc/dependencies/snapshots，核对工具/清单SHA256一致。install.md及AGENTS.md增加唯一维护入口、依赖变动时同步规则；普通源码变更不反复采集。源码快照基线525f3c5，非本次提交前全部树的冻结证明。
- 3工具专项通过（真实catalog与坏引用/重复ID/profile拒绝，模拟缺元数据/规范化名/保留markers，真实CLI采集/不覆盖/--check）；编译、JSON/UTF8/链接/围栏/diff通过。无依赖升级/清理/原生/GUI/科学/Windows/Mac运行或EXE构建。XDATCAR仍未跟踪不提交。第一批完成；版本锁、完整SBOM、系统快照/成品裁剪及旧接口修复仍未实施，按后续明确指令继续。

## 扩展全层依赖审计（2026-11-14）

- 用户补充“不限Python2/GTK，其他未知库也检查”。新增doc/dependency-inventory-2026-11-14-zh.md并与前份报告互链：覆盖科学/传递库、原生ELF、ctypes字体/平台接口、构建/文档命令、内置PDF/UUID/ODP、GLTT/xmllib及Windows冻结样包。无应用/环境修改。
- 只读发行元数据：GTK Python3.14.4 NumPy2.3.5；ASE环境Python3.14.6/ASE3.29.0/NumPy2.5.4/SciPy1.18.1/Matplotlib3.11.2/Pillow13；SMILES环境RDKit2026.9.1/NumPy2.5.4/Pillow13。ASE元数据要求SciPy/Matplotlib/typing_extensions，RDKit要求NumPy/Pillow，不是无直接import就可删。新增实际stringformat缺xmllib，uuid/Collada/polyfunc仅导入通过。
- readelf核对现役_cp4vasp9条直接NEEDED，系统GL/GLU/GLUT/FLTK及字体库可定位，glutInit符号存在但未开窗；Ubuntu脚本未显式列GLUT，干净设备依赖仍需核验。构建命令可找到，epydoc/doxygen/povray未找到，后者不等于.pov文件导出失败。
- 11/12的4add680包作为静态样本（非当前源码新EXE）：GUI_internal1444文件154557675字节，worker_internal616文件180276495字节，176 DLL；NumPy双份隔离有ABI原因。worker有SciPy/PIL/RDKit，无Matplotlib目录，spec明确排除；目录清单非完整模块/功能验证。版本固定不覆盖全部间接依赖，pip list缓存不是安装锁文件。未联网、未跨平台运行/重建/GUI或用户数据操作，未生成完整SBOM/漏洞扫描；UTF8/链接/差异检查通过。只交付审计，待用户指定清理范围。

## Python2/旧GTK及冗余代码审计（2026-11-14）

- 用户仅授权先找出来再清理，本轮无应用/安装/打包改动。报告doc/legacy-code-audit-2026-11-14-zh.md，基线38c344d；跟踪1740文件、282 Python AST全解析通过（3.14.6），静态导入/注册/Glade/构建/冻结/重复内容核对。238旧名候选含compat别名/局部变量等假阳性，不作错误计数。
- /usr/bin/python3 3.14.4临时对象探针复现Property.thread.isAlive AttributeError、StructuredDictionary.__cmp__缺cmp、SQLiteDBI(':memory:')缺pysqlite2、Color除法TypeError；VAC仍调用不存在time.clock为源码+环境证据未执行任务。历史PIL/QD分别缺Image/Qd，Tk2先缺tkinter且源码有Tkinter未绑定；PS/PDF/FIG/SVG仅导入通过，非导出验收。
- 候选：loadGlade_old/data/glade、仍注册的Commit/LegacyDB/SQL链、旧Makefile python2及distutils入口、QuickDraw/wx/Tk/PIL后端、SetupProfile_old和旧生成文档。必须保留：现役GTK3/适配层/data/glade2、graph仍用的顶层gtk、compat全局别名、现役导出后端、FLTK/ODP源及SWIG生成/复制关系。doc/api925文件32094794字节不在Windows datas，不能把清理量等同EXE缩小。
- 无GUI/科学/原生/跨平台测试，无用户计算/数据库操作；未读XDATCAR，保持未跟踪不提交。仅文档核对/UTF8/差异，详细检查范围和分批建议见报告。审计完成，下一步需用户指定清理批次，本记录不授权自动清理或构建。

## XDATCAR完整轨迹与Control播放（2026-11-13）

- 用户放入根目录XDATCAR，报告只能显示最后结构。getSystem原走PoscarSystemPM、缺少轨迹属性。新增xdatcar.XdatcarSequence按帧文件偏移索引，逐帧用Structure/POSCAR读取（支持Direct/Cartesian、VASP4/5、重复完整头变胞、坏/缺帧拒绝），无需ASE；XdatcarSystemPM提供完整序列和独立首末快照，不推断邻目录能量/力。
- 原frame.glade Control→swincontrol.glade/GTK3 adapter→StructureWindowControlApplet/StructureWindowApplet链保持。XDATCAR默认完整轨迹，菜单名XDATCAR trajectory；单帧Initial/Final看首末，播放/步进自动回全序列，到末停止再播重头，重复播放不叠计时器，换系统/销毁停止；普通POSCAR返回初始视图，XML序列语义保留。源文件必须原位不变，新增帧需重开，序号从0起。
- 本Linux实际GTK/原生CLI及File/Open、首末/前后、定时进帧/暂停/重播/重复点击、返回POSCAR通过；用户根目录XDATCAR只读识别71原子1000帧，原生核对0/499/999坐标与中段定时前进。Control及两张原生帧图已查看。3专项（含变胞/VASP4/截断/非有限）、现有ASE导入实际GTK、8 GTK及33面板启动（不含GLUT）通过；编译/diff通过。GUI初轮检查导入顺序及返回POSCAR样例缺CONTCAR已纠正，最终重跑通过，不计失败为通过。
- 文档usage_commands/GTK架构/当日双语同步。证据/tmp/p4vasp-xdatcar-{gtk,import-regression,gtk-base,smoke}.log。未跨平台/重打EXE，无原生改动不需重编译；用户XDATCAR保持未跟踪不提交。任务完成，重启源码版生效；不自动构建Windows。

## 半月总结与最新Windows交付（2026-11-12）

- 用户要求10/29—11/12半月汇总和最新EXE。中文28项功能/用法总结仅交付桌面：/mnt/c/Users/lqlhz/Desktop/p4vasp_近半个月更新总结_2026-10-29至2026-11-12.md；核对逐日记录与指南、UTF-8/围栏及桌面副本一致，不把历史平台测试写成本次通过。
- Windows更新器从4add680023c752fdb01d60c6adbf0e55910ce482隔离重编译/冻结成功，日志build/windows-update/4add6800-n4026gyq。产物：C:\msys64\home\lqlhz\p4vasp-checkout\dist\windows-releases\p4vasp-20261112-211415-4add6800-gkmr_u_4\p4vasp.exe，同级同名.zip/.zip.sha256，SHA256=01e8e4261b52ffe6607fc6d2b3d65d5adff49ceb678f3eed035cb7f5e4f4ee6e。
- 成品runtime/gui/models三报告ok=True；额外核对_internal/figures四张运行时图片及daily.json16条名句存在、SOURCE-COMMIT一致。成品帮助页人工交互/扫码、频率R25、另一台干净Windows未另验收；不以文件存在推断功能全通过。EXE/ZIP留Windows checkout，未另复制到桌面。本文档后续提交不改变已冻结源码，无待自动继续构建事项。

## 中英文每日一句与wikidog致谢（2026-11-11）

- 用户要求采纳wikidog于11月10日建议：名言除中文外加入英文。daily.json保留12中文并每3条后插入1英文，共16条/16天离线日期循环；新增可选language字段，daily_status英文按作者/作品展示，旧条目中文书名号及坏文件后备保持。英文3条Emerson Self-Reliance及1条Hamlet，核对全文来源见词库README。
- acknowledgments.json新增wikidog/既有QQ65387222/建议中英文名句/2026-11-10，不改旧Windows建议、不增加捐款。Frame原状态区/Glade/adapter与Help菜单入口不变。
- 本Mac实际testDailyStatusGtk通过（新增双语/来源、原日期稳定/循环、700/900宽对齐、状态/错误优先、进度/计时器清理）；英文Label及真实致谢Dialog精确行检查通过，截图/tmp/p4vasp-{english-quote,wikidog-credit}.png已查看。JSON解析、编译/diff通过；非跨平台或EXE验收，无原生修改。任务完成，重启生效；既有cODP生成差异保留。

## Help and Support 图片整理（2026-11-11）

- 按用户要求新增根目录figures/，迁移根目录3张原图与data/community三张运行时图片，逐字节对比HEAD均相同；新增用户已移入checkout的QQgroup_V.jpg（大师兄科研群-V，1012023869），原图保留、仅内存裁剪。图标/字体位图/历史文档截图保留原路径；已向用户说明此范围，未收到扩大范围答复。
- Database → Resources → Help and Support替换旧中文页签；CommunityPage加载figures/下四张二维码，现有p4vasp群号复制不变。Windows spec增加figures，未重打包。指南、figures README和旧目录迁移说明同步。
- 本Mac实际testCommunityGtk（四图、裁剪、中文、剪贴板、缩放/原图/窄窗口）、testResourceHubGtk（含英文页签）及DBApplet启动通过；真实950×750页面截图/tmp/p4vasp-support-four.png已查看，四图/相邻控制完整。Resources退出仍有Vector析构警告及旧主题SVG警告，未修复；手机扫码有效性/其他平台/新EXE未验证。编译与diff检查通过，无原生变更。既有cODP.py差异保留不提交。
- 任务完成；后续按新指令，未自动迁移程序内部位图。详情见update_history/update_2026_11_11.md新增章节。

## macOS Resources字体崩溃修复（2026-11-11）

- 用户点击Database → Resources出现PANGO_IS_FC_FONT_MAP断言及SIGSEGV。community.load_chinese_font在darwin直接使用系统中文字体，避免将CoreText映射传给PangoFc；Linux/Windows加载路径保留。入口仍为frame菜单→DBApplet/ResourceHubApplet→resources.glade/GTK3 adapter→CommunityPage，无布局或原生改动。
- 本Mac实际DBApplet启动检查、8项GTK3回归通过；中文无缺字、三张二维码、复制群号、放大弹窗和重复调用检查通过；真实映射900×640窗口截图/tmp/p4vasp-macos-community.png已查看，中文/按钮/二维码完整。沙箱GUI初次退出134，桌面权限执行后通过；临时脚本首轮Pango导入错误已更正，Offscreen初图裁切后改真实窗口确认。Offscreen弹窗Gdk origin警告及既有主题SVG/弃用警告不计作全部清理。
- 纯Python修复，重启p4v即可；未重编译、跨平台复测或打包EXE。既有odpdom/cODP.py生成差异保留不提交。任务完成，下一步用户实际点击复核；不自动执行其他旧待办。详情见update_history/update_2026_11_11.md。

## Windows新版构建交付（2026-11-10）

- 用户授权更新EXE，现有update-windows.sh在Windows checkout快进至0ed090d78dd4d619bc539046c73d26837fc4327b；隔离原生编译、主程序和ASE/RDKit worker打包成功。日志：Windows checkout的build/windows-update/0ed090d7-rx70hnsi。
- 产物目录：C:\msys64\home\lqlhz\p4vasp-checkout\dist\windows-releases\p4vasp-20261110-002141-0ed090d7-g7r84bku，内含p4vasp.exe；同级同名.zip及.zip.sha256。SHA256：8c417e19eac64a497002f1b26481afe75526badab04f40a3be77b62c29ece920。
- 成品runtime/gui/models三份report.json的ok均True（同级-checks目录）：43 Glade资源无property错误、原生绘制/PNG/选择性标记、GUI启动、ASE bulk/XYZ、RDKit乙醇及导出/多片段拒绝/取消回收。ASE3.29.0/RDKit2026.09.1，GUI Python3.14.9、worker3.13.17。本次未单独做成品频率页/真实R25或干净另一台Windows验收；不能把这些检查当作全部科学功能通过。未复制到桌面/Downloads。无进一步构建待自动执行；本次后续文档提交不改变已打包源码。

## 热化学计算按钮文案（2026-11-09）

- gtk3/vibrations.py将Calculate correction改为Get Thermochemistry，回调及计算不变，操作指南同步。实际Linux完整合成频率GTK回归通过，最终结果截图已查看按钮显示，编译/diff通过；未跨平台/重打EXE。

## 首步能量排除电子SCF中间值（2026-11-09）

- 用户指定桌面R25并报告E=6548.33227256。只读核验OUTCAR：该值来自Iteration 1(1)电子迭代，正式首个FREE ENERGIE汇总sigma->0=-215.08849841（without entropy=-214.90142429）。原ASE index0优先路径误取电子步，原fallback也未区分。
- vibrations.ionic_energy改直接按正式离子汇总读取首/末sigma->0，跳过SCF中间能量并兼容free多空格；该步缺sigma保留明确TOTEN回退，无汇总的精简fixture仍支持。来源变p4vasp OUTCAR，GUI/JSON沿用现有来源传递。真实R25首步函数及完整read_outcar快照均=-215.08849841，末步=-215.08007107；未修改文件或重新计算。
- 10后端测试（新增SCF前后干扰及未完成末步回归）、2独立脚本、完整合成频率实际GTK通过，首次GUI旧ASE来源断言更新后重跑通过（/tmp/p4vasp-ionic-summary-gtk.log）；编译/diff通过。真实R25只验证读取及快照，未做GUI热化学计算；未跨平台/EXE打包。指南及双语同步。

## 结果单行表头与单元格复制（2026-11-09）

- thermo_result.py删除表头强制换行；TreeView禁整行选择，左键释放在单元格内启动只读Entry，支持原生文字选择/Ctrl+C/右键复制，不连接写回处理。链路仍为原Glade/adapter/VibrationsApplet→结果组件，无入口变化。
- 本机实际GTK宽表截图已查看；独立检查点击电子能单元格、只读状态、选择/剪贴板精确为6548.332273、底层值不变及单行表头通过，450/700/1200列宽回归通过。完整合成频率GUI通过（/tmp/p4vasp-thermo-copy.log），编译/diff通过。未跨平台/打包EXE、未改科学计算。

## 热化学表格宽度分配（2026-11-09）

- thermo_result.py四列均开启expand，GTK剩余宽度不再全归最右列，保留紧凑基础列宽和用户拖动。实际Linux独立GTK在450/700/1200宽验证余量均分（整数余数最多3px），1200时列宽272/302/292/310，宽表截图已查看；完整频率合成GTK回归通过（/tmp/p4vasp-thermo-columns.log）。初始独立检查Stack显示顺序及余数断言已纠正，不计作通过。编译/diff通过，未改科学数据，未跨平台/打包EXE。

## 频率页三行两列网格（2026-11-09）

- 当前任务完成：gtk3/vibrations.py以同宽Gtk.Grid替代Paned/独立工具组/热化学Expander。三行分别结构/波数、Cell播放/Scale、热化学参数/结果；横线及输入穿透的中线分隔，FlowBox局部换行。结果四列表头换行、列宽紧凑，页面去掉嵌套结果卡边框；加载成功后隐藏安装提示。科学计算/模式向量/保存逻辑未变。
- 本机Linux实际GTK合成OUTCAR完整流程通过，反复700/900/1200/700/1050/700/1200宽验证六格坐标、同宽同高、列表与结果边界；动画/周期副本/Scale/能量选择/气相/双文件保存回归通过。最终气相结果截图已查看；8 GTK测试、33面板启动（不含GLUT）、编译/diff通过。证据：/tmp/p4vasp-six-cell-{layout,gtk,smoke}.log。
- 指南/架构/当日双语已同步。未重跑科学后端或原生测试，无原生改动；未操作R25、未Mac/Windows实测或重打EXE。下一步仅按新指令继续，旧Windows打包状态不由本次推断。

## 左侧九按钮统一尺寸（2026-11-09）

- 用户报告新增frequency按钮小。链路frame.glade toolbar→GTK3 adapter（PNG32/stock主题默认小尺寸）→p4v.Frame.createFrame→现有点击分发。Frame仅对主侧栏规范：DND图标大小、实际32×32居中画布保持纵横比、主题图标/stock回退、去掉主题多余透明留白，Gtk.SizeGroup BOTH及homogeneous统一九按钮尺寸；标签/tooltip/功能不改，不改菜单或其他工具栏图标。
- 验证发现只设toolbar DND仍有Open图像分配16×32，已改实际pixbuf画布。扩展测试还暴露频率resize_tools在分配过程中改orientation导致viewport卡旧宽775，现改idle后变方向并queue_resize；不只是放宽测试，700/900/1200/700/1050/700/1200反复尺寸均验证列表边界。
- 本机Linux实际Frame九按钮宽高相同、九图标均32×32、频率点击/默认状态/完整周期/模式/能量/气相/报告脚本流程通过；最终小窗口截图已查看。8 GTK/33面板（GLUT除外）、编译/diff通过。前轮尺寸失败不计通过，最终修复后完整重跑通过。未实测其他设备/DPI或新Windows包，无原生改动/重编译，未操作R25/无关删除。指南/架构/当日双语同步。

## 热化学结果四列表格与kJ/mol显示（2026-11-08）

- 用户要求右侧按item/Equation/eV/kJ/mol显示。ThermoResult改只读TreeView，四列Energy item/Equation/Value in eV/Value in kJ/mol，8行E/ZPE/U/H/S/TS/ΔF或G/Total F或G，校正行加粗。公式区分harmonic F=U-TS与gas G=H-TS，H=U+kBT，U_th与S分量用tooltip解释。精确SI e与NA相乘换算96.48533212331002；S单独注明per K，数值带/K避免误当能量。
- 保留实际ASE标题、温压/气相条件及与左参数区等高；空E及不可用H/Total用双列—。正常宽度完整四列，窄时表内滚动。JSON/独立脚本仍使用原eV计算结果，本次只展示换算，无科学计算改动。
- 实际Linux完整频率GTK通过四列表头、负电子能/熵换算数值、F/G公式、空值、列宽/结果边界/等高、原能源选择/气相/周期/动画/导出流程；已查看最终表格及末列局部截图。首轮列宽使表头/熵单位偏挤，已扩大后检查真实viewport与显示。8 GTK/33面板通过（GLUT除外），编译/diff通过；未重跑后端/原生或跨平台/EXE，未操作R25/无关删除。指南/架构/双语同步。

## E自动读第一步与单独OUTCAR末步选择（2026-11-08）

- 用户确认频率任务第一个ionic step能量正确，要求E右侧可另开OUTCAR取最后一步。vibrations.py新增ionic_energy/first_ionic_energy：优先ASE vasp-out index0/-1的sigma->0，简化输出失败时p4vasp按第一/最后能量块解析，缺sigma时明确标TOTEN fallback。频率快照带electronic_energy_eV/source；run_request新增energy动作，复用既有可取消worker，不新增长驻进程。
- set_data默认填频率第一步，换源缺能量清空；E右侧Open OUTCAR用CompactFileDialog读取另一个普通优化/静态OUTCAR末步，只更改E和energy_source，不换结构/模式/显示/Scale。手工编辑/清空保留；另选文件取消或失败保留原能量/结果。计算/JSON/脚本记录energy_source(path、首/末步、类型、reader)，总F/G加实际E，独立脚本仍不读取源文件。
- 9后端专项通过（合成ASE可读3帧首-10.25/末-12.25、简化首末、sigma优先、TOTEN0回退/无能量）；2独立脚本回归通过。实际GTK完整频率流程通过自动E/tooltip、总能量、手工覆盖/来源、另选无模式OUTCAR末步、频率快照不变、取消/失败不改、保存两类来源、换源清空、700-1200布局及原操作；已查看700宽新按钮/自动值截图。8 GTK/33面板（GLUT不含）、编译/diff通过。
- 本机Linux合成数据验收，未读改R25、未跨平台或重打EXE，无原生改动不重编译；Windows worker现有ase.io.vasp hiddenimport覆盖新读取路径，但未冻结实测。指南/架构/双语同步，用户无关删除保留不提交，本任务完成。

## POSCAR固定标记自动保留/缺失直接导出（2026-11-08）

- 按用户要求删除Confirm export without selective-dynamics flags及其阻挡。选择虚频后保存按钮不再依赖约束来源；匹配POSCAR/CONTCAR的固定标记自动保留，找不到则沿用无约束POSCAR，不补猜标记、不需确认。读取器/坐标/Scale/模式判断/已有文件保护不改。
- 实际Linux完整频率合成GTK专项通过，既有匹配标记导出仍为T/F/T，无来源时直接保存且文件无Selective段、重读isSelective为False；确认框不存在，原动画/周期/气相/结果/脚本流程通过，更新后截图已查看，编译/diff通过。本次聚焦验证，未重跑广泛GTK/启动或科学后端，未跨平台/重打EXE，无原生改动；未操作R25，用户无关删除保留，指南/双语同步。

## 精简结果卡片与预览左上角模式标题（2026-11-08）

- 用户修改1：ThermoResult删除底部频率下限/纳入/虚频/电子能说明/驻点警告，实际ASE版本放标题Thermochemistry Results (ASE x)，保留数值/条件。结果Frame与左参数列均Fill，测试确认等高；JSON/脚本原记录不删，科学计算未改。
- 用户修改2：VibrationsPage以Gtk.Overlay叠加Mode编号/波数于ModeView左上角，删下方独占行，最大位移改tooltip；overlay pass-through不抢拖动。Glade/adapter/applet入口无变化。
- 实际Linux频率完整GTK合成流程通过：F/G标题实际版本、无details、左右等高、左上角坐标/输入穿透、700/900/1200布局及原播放/Scale/周期/气相参数/保存/失效流程；截图已查看，编译/diff通过。8 GTK与33面板启动通过（不含GLUT）。未Mac/Windows或新EXE，未改原生/重编译，未操作R25/无关删除。指南/架构/双语同步。

## Show晶胞细线与真实抗锯齿（2026-11-08）

- 用户希望Show接近频率效果，重点是粗糙box线。原生cell默认2→1，与viewer_style.CELL_LINE_WIDTH和ModeView共用整数1（native setter要求int）；StructureWindow创建/重开都设细线。VisFLWindow按can_do选择MSAA visual，否则回退；VisNavDrawer启停线平滑/MSAA并采用更柔和的ambient .4/diffuse .7/specular .35、shininess32、左上光源。drawCell scoped alpha blending且暂时禁用MSAA以确保实际线覆盖，结束恢复GL状态，保留深度/选择/相机逻辑。
- 本机Linux原生重编译通过；实际GL探针Mesa4.5/llvmpipe、samples4/buffers1。第一轮直接MSAA+线平滑仍无中间灰，改cell独立alpha覆盖后实际Show截图边缘45灰阶；新testShowQuality.py同图AA关闭/开启为0/45，断言真实像素而非只验flag，同时检查相机/坐标/键因子不变及重开宽1。before/after截图已查看。初始float1.0传native int setter曾失败，改整数后全部重跑通过，不将失败记为验收。
- 实际Show导入/更新、居中/重复/重开、Delete/Builder/标记、C++框选/深度/隐藏/副本/Esc/Side/Space/旋转通过；实际频率完整流程、8 GTK、33面板（GLUT除外）、57基础通过，编译/diff通过。新测试只合成数据，不读改R25。未其他显卡/Mac/Windows验收、未重打EXE；同原生导航器其他预览也采用新光照，仍不保证与Cairo像素相同。其他设备需重编译，本机重启即可。指南/架构/当日双语同步，用户无关删除和R25不提交。

## Scale工具区与默认展开的右侧热化学结果（2026-11-07）

- 用户要求Scale放Cell/播放右侧、Thermochemistry默认展开、结果右置并美化。VibrationsPage工具区左右分组，左Cell XYZ+播放，右Scale/Zero/POSCAR，内容宽>=820横排，窄时上下避免裁切；模式说明单独下方。热化学默认展开，紧凑参数/计算/保存列在左，新增gtk3/thermo_result.py卡片在右：强调ΔF/G，ZPE/U/H/S/TS/E/Total F或G按值/单位对齐，条件与模式处理分组，E留空显示—且标correction only。
- 计算后等布局80ms自动揭示结果，过期/销毁回调跳过；参数变更清空卡片并禁保存，错误显示右侧消息。Model标签简化Harmonic/Ideal gas，tooltip保留模型含义；气相弹窗/固定50/虚频排除/科学计算/原始导出不变，Glade/adapter/applet宿主无修改。
- 实际Linux GTK频率完整合成流程通过：默认展开、700/900/1200宽频率三列完整、1050宽Scale在右、结果卡片位于设置右侧、F/G字段/单位/温压值、计算保存可用、参数失效清空、既有周期/动画/Scale/POSCAR/气相弹窗/双文件保存通过；8 GTK、33面板启动（GLUT不含）、编译/diff通过。已查看F/G右侧卡片截图。首轮测试截图曾待布局GTK断言，check_resize后重跑无断言；结果80ms后滚动以避免按空卡片高度定位。科学后端本次未改未重跑；Mac/Windows未验收，未打EXE，未操作R25。指南/架构/双语同步，无关删除保留不提交。

## 频率晶胞/XYZ显示重复与Show样式统一（2026-11-07）

- 按用户要求新增频率Cell（默认开）及X/Y/Z SpinButton（1..5，初始1）。periodic_preview.py按真实晶格向量（含斜胞）仅映射显示平衡坐标并生成平移副本/去重晶胞线；按副本平衡距离成键，可显示扩展区域跨边界连接。ModeView以固定图像偏移应用每帧原模式，所有副本同相；显示原子上限12000，超限回退控件原值，换文件重复数归1。热化学、Scale导出和原数据不变，扩展中保存仍原晶胞原子。
- viewer_style.py共享p4vasp元素表颜色、共价半径/缺失.7后备、球比例.5、成键因子1.2、键颜色/半径；原子表仅克隆不改写。Show入口与气相预览用共享样式，频率绘图用相同值；原元素radius参考数据保留，Show默认显示改为共价球，大小控制仍可调。StructureWindow重开保存成键因子。原生VisPrimitiveDrawer默认细分16→32，VisStructureDrawer初始化尊重默认值，本机Linux重编译通过；两后端不是像素一致或同一光照/遮挡实现。
- 证据：3纯显示几何专项通过（跨界键、斜胞/未包裹坐标、复制位移、晶胞边、非法/上限）；实际GTK全频率流程含XYZ2x2x1/Cell开关/原快照不变/扩展中保存2原子/700-1200宽、模式动画/Scale/弹窗/结果脚本通过。实际Show工具栏匹配颜色/共价大小/成键/细分32、XYZ导入/换源通过，气相原生预览/输入导出、Show/Delete/Builder/标记、居中/重复/重开也通过；8后端/2独立脚本/8 GTK/33面板启动/57基础通过，GLUT排除。编译/diff通过。
- 初次斜胞测试预期坐标手算错误已更正后通过；一次widget.draw截图未等布局导致GTK断言，不记为视觉通过，等布局重跑后截图/tmp/p4vasp-vibrations-periodic.png已查看；Show原生TGA转换/tmp/p4vasp-show-smooth.png已查看。没有大体系性能、任意q点相位或跨平台验收；Windows旧包未更新，目标机需重编译。未读取/修改/提交R25，用户无关删除保留。指南/架构/双语记录同步，本任务已完成。

## 频率列表完整显示与移除Thermo列（2026-11-07）

- 用户报告右侧列表裁切并要求删除Thermo列。确认原Paned左侧播放行撑大自然最小宽度、右侧只预留210；现播放/模式说明移至结构与列表下方整行，页内ModeView最小宽200，右侧预留300，按实际分配宽度调整分隔位置。表格仅Mode/cm⁻¹/Type三列，固定列宽60/130/100，保留表内纵向滚动和手动分隔拖动。Glade/适配器/VibrationsApplet宿主链不变，无原生改动。
- 移除可见Thermo开关及失去对应操作的额外实频确认/主面板最高频按钮；表面谐振每次自动用全部正实频，气相在已有参数弹窗筛选/确认，内部仍存模式选择供计算。切回Harmonic不会沿用气相只选部分的旧状态。固定50与全部虚频排除保持。
- 实际Linux GTK完整频率合成流程通过：700/900/1200宽下三列表头/列宽均在可见区域、列表右沿不越主窗口、初始布局截图/tmp/p4vasp-vibrations-compact.png已查看；原动画/Scale/POSCAR/气相弹窗/自动计算/脚本保存及gas→harmonic恢复全部实频通过。8 GTK/33面板启动通过（GLUT不含），编译/diff通过；没有重跑科学后端（本次未改），未Mac/Windows验收或新EXE。指南/架构/双语同步；只合成数据，不操作R25，用户无关删除/目录不提交。

## 固定50cm⁻¹实频下限与全部虚频排除（2026-11-07）

- 按用户最新规则，热化学正实频低于50统一按50（含ZPE/热项/熵），50及以上不变，全部虚频/零频过滤，删除floor/tolerance输入，旧request对应字段忽略且不写入新settings。不再因虚频数量拒绝计算，Stationary point只记录标签；额外剔除正实频仍需确认。gas_mode_count统一前后端：3N-6/5减去虚频数、最低0，按假定虚频占振动自由度建议最高实频并确认；不自动区分虚频的平动/转动来源。无正实频的harmonic仍拒绝空求和。
- 结果新增frequency_policy/excluded_imaginary_modes/warnings，界面显示固定规则及排除编号，独立脚本复制政策并按有效频率重算。8后端（20/50/80边界、多虚频含主动选中也过滤、不改原数据、legacy忽略、气相空振动项及原解析/解析公式/压力自旋对称数）、2独立F/G脚本（新增低频/多虚频、与原结果12位一致）、实际GTK频率全流程通过，已查看移除字段后的主面板截图；编译/diff通过。未重复8GTK/33启动或跨平台验收/打包。
- 用户明确本次只改程序，不重算或操作R25；此轮仅合成输入和临时文件，不读改R25、不提交用户目录，用户自行移除。memory/双语记录/指南同步；原样例删除保持不提交。已交付Windows旧包未包含本次变更。

## R25低NWRITE频率OUTCAR兼容修复（2026-11-07）

- 用户报告本地R25/OUTCAR在频率面板打开空白。实际只读复现read_outcar报VRHFIN缺失：该VASP6.5.1/IBRION5/NWRITE0输出没有VRHFIN/per-potential POMASS，元素仅POTCAR行、质量在单行汇总。vibrations.py新增POTCAR/TITEL元素后备（支持赝势后缀/重复列表），POMASS解析同一行全部数值；保留原VRHFIN、质量处理及约束核对。无GUI布局/原生改动。
- 实际R25修复后识别Cu48/Zn16/H2/O1、67原子、9模式、3虚频(41.175864/164.078614/603.853579 cm^-1)、4种正确质量，匹配POSCAR约束。实际GTK通过Open按钮读取、列表/三维显示/动画、模式9 Scale .2及临时POSCAR逐坐标/前64原子固定标记核对，截图/tmp/p4vasp-R25-frequency.png已查看；原R25文件未改。
- 8后端测试通过（新增合成POTCAR/TITEL后备、后缀/重复列表、单行质量、质量加权位移/标记），2独立脚本回归通过，编译/diff通过。只本机Linux，未重跑全套GTK/启动或Mac/Windows验证/打包。指南/当日双语同步；R25未跟踪目录（含用户计算与POTCAR）及原样例删除不纳入提交。

## 气相弹窗增加温度与压力（2026-11-07）

- 用户要求已实现：GasThermoDialog增加Temperature(K)/Pressure(Pa)可编辑输入，初始默认298.15/101325，重开沿用主面板值。确认时正有限数校验，再同步回主面板及既有worker；取消不更改主面板。JSON与独立脚本保存实际值。无Glade/adapter/toolbar变更。
- 本机实际GTK频率全流程通过：默认值、取消不改、零/NaN拒绝、自定义350K/200000Pa自动G、结果/JSON/脚本值一致及模拟640x480按钮位置，弹窗截图已查看；2独立脚本F/G重跑回归通过，编译/diff通过。复用前轮8GTK/33面板为历史证据，未重复执行；未Mac/Windows验收或重新生成EXE。指南/双语更新同步，用户样例删除不提交。

## 气相热化学弹窗与独立重跑脚本（2026-11-07）

- 当前任务已完成源码实现：Vibrations模型选Ideal gas立即打开GasThermoDialog，输入geometry/Spin S/symmetry，显示T/P/驻点及拟纳入/排除模式；确认后自动启动既有独立ASE worker，取消不启动。主Calculate可重开；三项气相输入从主面板移至弹窗，其他条件与极小值/TS/自由度检查保留。优先保留数量匹配的用户选择，否则建议最高实频，用户明确确认而非静默排除。Glade入口/adapter/VibrationsApplet链不变。
- 新thermo_replay.py用于两种模型的JSON+同名Python双文件导出，任一已存在拒绝覆盖并清理本次已创建的另一文件。脚本内嵌结构/质量/原频率摘要/有效频率/设置，只依赖ASE+NumPy，无需原OUTCAR/GUI/p4vasp；固定本次选择重算，不运行DFT。直接python thermochemistry.py输出thermochemistry_rerun.json，--output可换新名字，保留覆盖保护；脚本注明ASE版本依赖，版本不同时警告。用户外部私有脚本仅只读借鉴，未修改或复制其物种表/错误的频率去重逻辑。
- 证据：2项独立重跑专项通过，分别真实ASE计算F/G后移除原OUTCAR/POSCAR、清PYTHONPATH并以-I独立执行脚本，数值与原结果12位小数一致；默认/自定义输出、重复拒绝、双文件冲突保护/清理通过。7既有科学后端通过；实际Linux GTK全流程通过，新增弹窗取消/非法自旋/几何与模式确认/自动G计算/真实双文件保存，原动画/Scale/POSCAR/F/加载/取消保留；8 GTK与33面板启动通过，不含GLUT。编译/diff检查通过。
- 小屏幕首轮与第二轮GUI检查发现自然尺寸/桌面边框仍溢出，不计通过；缩至500x300并滚动内容后模拟640x480下实际窗口552x389、动作位于范围内，截图/tmp/p4vasp-gas-thermo-dialog.png已查看。早期挂起modal测试进程已终止。仅本机Linux/合成输入验证，未实测Mac/Windows；已交付a201929旧EXE不含本次弹窗/脚本，未自动重新打包。指南与当日双语记录同步；用户Fe_single_atom删除保持不提交。

## Windows 最新便携包交付（2026-11-07）

- 用户授权打包当前最新Windows EXE。专用Windows checkout正常fast-forward到a2019291c590f6d1ef04da47b7899ace1771074a；使用现有update-windows.sh流程：git archive隔离快照、原生重编译、主程序/独立科学worker冻结、runtime/gui/models三检查、ZIP/hash。复用已缓存CPython3.13.17/ASE3.29.0/RDKit2026.09.1；GTK主程序UCRT Python3.14.9。构建日志Windows checkout build/windows-update/a2019291-66jd864x。
- 成品已复制到C:\Users\lqlhz\Downloads\p4vasp-20261107-221244-a2019291-mbolv7gc，双击p4vasp.exe，整个目录必须保留。旁边同名ZIP为156976870字节，SHA256 548390f2d818d96b3a617af4ddaf5e77bae6080df76d765dacbd38c36f6c0023。包内SOURCE-COMMIT记录a201929完整提交；后续文档交付提交不改变已打包源码。
- 构建目录和Downloads迁移后均实际Windows通过runtime/gui/models：43 Glade资源无属性错误、注册面板可导入、紧凑PNG/文件夹按钮、原生渲染与重放/选择性标记、32Cu bulk构建/原生预览/真实POSCAR保存、乙醇RDKit优化/预览/三文件保存、XYZ无晶胞补box、非法多片段拒绝与取消回收。检查PATH仅Windows系统目录并清除外部解释器覆盖。另Downloads随包worker以合成6模式OUTCAR检查物理位移.4、虚频识别及ASE谐振F/理想气体G成功；ZIP CRC与SHA256一致。报告Downloads同名-checks/delivery.json及三个子报告，已查看bulk界面截图。
- 新包包含ASE通用格式导入、频率分析与Help致谢源码。频率此次仅新包解析/热化学worker补测，未对完整频率动画/Scale交互逐项Windows验收；不是另一台干净电脑或全部科学结果/普通退出验收，未签名。交付已完成，无待后台构建。用户删除的Fe_single_atom三文件保持原状，不纳入提交；包采用已提交源码仍含该历史样例。

## 统一安装与独立命令文档（2026-11-07）

- 按最新要求撤回自动source入口：Linux/macOS统一bash install.sh；统一配置~/.bashrc，末尾提示source ~/.bashrc，常用启动和top/side命令移至usage_commands.md。删除receipt与zshrc分流，Bash误source安装入口安全返回，不改变父终端选项。安装指南同步；下方自动source/zshrc记录为历史行为。
- 本机5 finish与10 unified专项通过，含特殊路径、幂等、备份/权限/符号链接、失败/deps-only、zsh环境仍写指定bashrc、父终端误source安全返回；shell语法/diff通过。首次unittest模块调用因test包命名冲突未运行，改直接执行两测试文件后15项通过。未真实安装、未改用户rc、未验收Mac/zsh或GUI；本机无zsh。zsh手动source但新终端不自动读取bashrc，已有Bash专用配置可能不兼容，指南注明。用户删除的Fe_single_atom三个输入文件不纳入提交。

## 安装末尾常用命令示例（2026-11-07）

- 用户要求用常用命令替代bashrc说明，并加top/side导出。finish-install.sh正常结束只显示简短GUI/Command setup结果及NEXT STEP/COMMON COMMANDS/EXPORT PNG：p4v、POSCAR、test.xyz、频率OUTCAR、两条--view top/side导出。保留ASE条件、计算目录提示；自动配置/父source机制不变，正常不打印rc路径/追加/备份细节，出错仍显示原因与NOT CONFIGURED，普通bash调用仅提示开新终端。备份仍在实际rc同目录。
- 本机6 finish与13 unified测试通过（含新输出断言、源入口/receipt回归），shell语法/diff通过。实际临时合成POSCAR经p4v.sh执行两条打印参数（仅替换alias为bash绝对启动器）无DISPLAY导出top/side，各1000×1000，PNG可读且哈希不同；没有真实重新安装、改用户rc或GUI验收。安装指南与双语记录同步，未生成Windows包。

## 安装后自动source当前Bash（2026-11-07）

- 用户要求安装后自动source。已新增Bash用source install.sh入口：安装/构建仍在隔离子进程中执行，finish-install仅在成功配置后通过私有临时receipt回传rc路径（NUL分隔），父Bash自动builtin source并确认p4v别名存在，打印ready。不会用exec替换父终端，不改变父目录/安装器选项或泄漏临时函数；receipt成功/失败均清理。
- 普通bash install.sh因进程模型不能替父终端source，保留手动reload/新终端提示；source入口明确选当前Bash的bashrc而非登录SHELL可能指向的zshrc。zsh仍用bash install.sh及其zsh提示，未增加zsh直接source支持。dry-run/help/deps-only不加载，安装或配置失败不加载，不伪报ready。
- 本机6 finish-install专项、13 unified-installer专项通过：父Bash能立即调用alias、交互Bash rc guard、父ROOT/选项/cwd保留、失败码23保留且父继续、无成功receipt不加载、dry/help/deps跳过和临时文件清理。真实入口source ./install.sh --dry-run、4脚本bash -n/测试编译/diff通过。使用临时rc和backend/launcher stub；没有真实安装、修改/加载本机用户bashrc、GUI或实际macOS/zsh验收。安装指南和当日双语记录同步；源码任务已完成，未授权另行构建Windows。

## 安装自动配置shell别名（2026-11-07）

- 用户明确授权将配置bashrc写入安装流程，替代手动复制四行命令。统一install.sh经Unix后端finish-install.sh调用新configure-shell.py；默认~/.bashrc，SHELL为zsh时用ZDOTDIR或~/.zshrc。自动维护带标记的p4vasp区块，更新路径/重复安装幂等，保留其他内容/非UTF8字节/权限/符号链接，已有文件每次改变前备份，临时文件原子替换，不执行用户配置。
- GUI启动失败时仍提前返回、不改rc；headless/no-launch/build-only成功流程会配置，两个后端deps-only跳过。写入或标记错误明确NOT CONFIGURED并给手动提示，不能误报已配置。英文完成区块保留，NEXT STEP改为单行source实际rc；子进程无法替父终端生效，新终端按各自启动文件读取。
- 本机5项testInstallFinish通过：实际临时rc写入/读取alias（特殊路径含空格、单引号、$、反引号）、重复不改mtime/不增备份、更换checkout/备份字节/权限/非UTF8保留、失败与deps-only不写、headless/no-launch、zsh+ZDOTDIR目标/残缺标记拒绝、符号链接保留；9统一分流通过，4脚本bash -n/新helper编译/diff通过。均使用临时rc及启动stub，不重跑真实安装/GUI或修改本机用户bashrc；未实际macOS/zsh执行验收。当前安装指南/双语记录已同步，前条“只打印不修改”是旧行为；用户预设/原图/Fe_single_atom保留。

## 安装结束英文提示与复制配置命令（2026-11-07）

- 用户要求安装末尾英文、分隔线和可复制bashrc配置命令。install/finish-install.sh改为英文Launching及分隔清楚的结果/NEXT STEP/START区块；GUI PASSED与SKIPPED区分，启动失败仍返回原错误码、不打印完成提示。输出四行带单引号heredoc的cat追加alias及source ~/.bashrc；保持原路径安全引用，不自动修改用户配置，macOS打印替代zshrc命令块。
- 本机2项testInstallFinish通过：成功/错误码/无显示/禁启动、含空格/单引号/$路径、在临时rc文件执行实际打印命令并调用alias，以及模拟Darwin分支的zsh块语法（非真macOS/zsh验收）；9统一安装分流通过，4个相关脚本bash -n及diff通过。只预览LAUNCH=0的真实结束输出，未重跑安装/GUI预览或编译原生，用户bashrc未修改。install.md及双语当日记录同步；无其他安装功能/Windows打包改动。

## Help致谢表（2026-11-07）

- 按用户纠正，名单与GTK模型按Date升序（从早到晚）：wikidog 2026-10-26、ai-vasp 2026-10-31、岁月静好 2026-11-05；模型显式排序，后续新增不依赖JSON插入顺序。本次实际GTK模型顺序／临时逆序插入专项、JSON／编译／diff检查通过，未重跑整套GUI或构建Windows。

- 后续按用户提供新增第3位wikidog，QQ 65387222，建议“Windows版本的生成”，日期2026-10-26，Donate留空。仅名单数据／双语记录更新；JSON精确行值／3行与diff检查通过，无界面代码变更，不重跑GUI。

- 后续按用户补充新增第5列Date：ai-vasp为2026-10-31，岁月静好为2026-11-05；JSON及表格同步，按工作区设置的默认宽度增至780。实际Frame Help→表格5列／准确日期／Close通过，截图已查看；本次仅日期列专项及JSON/编译/diff检查，下面8 GTK为初版验证，不冒充本次重跑。

- 用户要求Help新增Acknowledgment，四列Who/QQ号/Donate/Suggestion。p4v.Frame.createHelpMenu新增动作→gtk3/acknowledgment.py创建只读滚动Gtk.Dialog；没有Glade变更，保留About/License。数据在data/acknowledgments.json：ai-vasp/1106151494/20元/空；岁月静好/1020948036/空/DOS可视化Y轴显示Bug。全部由用户提供，未自行补充贡献或金额。
- 本机Linux11/7实际Frame菜单点击、精确表头和两行、Close可见并关闭通过，已查看映射widget截图/tmp/p4vasp-acknowledgment.png，中文正常；8 GTK、JSON/编译/diff通过。同步指南和双语当日记录。纯Python/数据新增，重启即可；未构建Windows或验证其他平台，不改用户预设/原图/Fe_single_atom。名单后续按明确提供信息维护。

## 频率面板文件窗口按钮不可见修复（2026-11-07）

- 用户报告Open frequency OUTCAR弹窗找不到按钮，类似旧PNG窗口超屏。源码确认gtk3/vibrations.py使用原生Gtk.FileChooserDialog，仅set_default_size不足以限制自然最小尺寸／桌面保存尺寸；此前未验证这一用户环境尺寸。现改用file_dialogs.py新增CompactFileDialog，继承已用FolderDialog的紧凑Gtk.Dialog导航，fit_dialog按工作区设尺寸，use_header_bar=False底部动作固定；该面板Open及POSCAR/JSON保存一起接入，原PNG/Folder逻辑保留。
- 支持目录/文件列表、Up/Home、双击、文件名、完整路径Enter、失效路径错误、Cancel和新文件名校验；路径保留真实尾空格。GUI长目录用例发现新增dialog曾strip尾空格导致拒绝合法目录，已修正并重跑；首轮被等待modal的测试进程已终止，不记为通过。
- 本机Linux 11/7：8项testExportDestination通过（含3新增compact用例，模拟640×480工作区/实际映射按钮坐标、长/中文/空格路径、打开/保存/取消/已有文件拒绝与旧PNG回归）；实际Vibrations完整Open/双保存/F/G/Scale等集成通过，8 GTK通过，编译/diff通过。已查看frequency-open.png/frequency-save.png映射widget截图，按钮位于窗口内；截图在/tmp/p4vasp-frequency-dialogs。未在另一平台/用户实际DPI设置核验，不新建Windows EXE。
- 操作指南和当日双语记录同步；本任务已完成，纯Python更新重启即可，无原生重编译。保留用户无关预设/原图/Fe_single_atom。

## 频率分析三步功能（2026-11-07）

- 当前任务：用户批准频率列表／动画、ASE热化学、沿虚频Scale导出，源码已完成。新增左侧Vibrations及Analysis菜单→vibrations.glade→VibrationsApplet→gtk3/vibrations.py；ModeView用GTK/Cairo交互三维投影嵌入面板，右侧模式列表；不嵌FLTK，不改Show/Build。vibrations.py为数据／worker核心，新增VibrationSystemPM支持p4v OUTCAR及主Open；面板可独立Open，或从当前系统PATH找OUTCAR。
- 首版仅频率OUTCAR：最后模式组、逐原子坐标／编号／数值检查；末尾实际位移段原样使用，否则除以OUTCAR POMASS的sqrt，不再归一化。平衡坐标来自模式表；匹配POSCAR/CONTCAR才继承固定标记，缺失必须确认无约束导出。缩减模式集提示核对，自定义质量保留。无直接XML Hessian/全q点/IR强度功能，不证明真实用户频率完整或收敛。
- 无量纲Scale[-1,1]、0.1步长，从原坐标加scale×实际位移；静态拖动/Zero暂停动画，POSCAR仅导出静态值，新文件exclusive写，不覆盖源。播放/旋转/缩放仅显示副本；切面板停止timer，destroy/换源取消worker。ASE读数/热化学复用BulkTask命令工厂与隐藏独立worker，90秒超时。
- HarmonicThermo输出F矫正，IdealGasThermo输出G矫正；温度K、压力Pa、气相几何/对称数/自旋S、可选电子能，逐模式选择/排除需确认；气相模式数明确核对。实频下限/小虚频容差默认0，后者需用户明确指定并确认排除，绝不取绝对值入热化学；minimum无实质虚频，TS恰一。报告含ZPE/U/H/S/TS与矫正及设置/有效频率，可保存JSON；参数变更清除旧结果。
- 本机Linux 11/7证据：7后端专项（独立谐振子公式、气相压力/对称数/自旋解析差值、物理/质量加权向量、signed Scale与flags、不累积、坏/截断表和不匹配参考）通过；实际Frame的CLI OUTCAR/左按钮/内嵌预览/点模式动画、Scale/真实POSCAR保存、F/G计算/JSON保存/实际Open/缺flags确认/切回/取消与销毁通过。截图为真实映射GTK widget.draw结果，已查看；桌面Gdk捕获首轮黑屏不当可视证据。夹具改为等待文件选择器路径就绪，未当应用修复。
- 另3 BulkTask、3 DOSCAR、57基础、2冻结路由（含--vibrations）、5 ASE导入、7更新器、8 GTK、33面板启动（不含GLUT）、4原启动场景通过；XML/编译/diff通过。初版展开热化学横向溢出已改单列参数，实际导出按钮位于窗口内；纵向通过滚动访问。操作详见doc/vibrations-zh.md，双语记录update_2026_11_07.md。
- 接手边界：本功能已完成源码交付；Windows脚本/worker增加thermochemistry入口，但未构建新EXE，11/6旧包不含新功能；macOS/Windows未实测，无真实用户OUTCAR/完整人工或科学验收，不自动启动下一轮打包。用户INCAR预设/二维码原图/Fe_single_atom保留。

## ASE通用结构导入（2026-11-07）

- 本次任务已实现：getSystem新增ASESystemPM，CLI与File/Open共用；保留目录／DOSCAR／XML／POSCAR分流。ase_import.py在既有ASE解释器或新版随包worker里读取8类扩展名（xyz/extxyz/cif/pdb/mol/sdf/xsf/traj），不向GTK进程导入ASE；超时60秒，错误显示原因，Open失败保留旧系统，CLI失败不再中断初始化。
- 无晶胞时三个笛卡尔跨度分别加20Å并将两侧留白各设10Å，单原子20Å盒；完整晶胞／坐标和原子顺序保留，部分晶胞／空／非法坐标拒绝。支持的多帧读最后一帧，不导入整条轨迹；只转几何与可表示的POSCAR信息，不承诺任意ASE元数据／原始PBC的显示等价；原文件不写。
- 本机Linux 11/7：5专项覆盖全部8类扩展名、跨度／留白／单原子／顺序／非正交cell／最后帧／含空格与@路径／坏数据／旧分流／worker失败；2冻结路由与环境测试、3DOSCAR、57基础、8真实GTK、32面板启动（不含GLUT）和4旧启动场景通过。真实CLI XYZ→Show原生窗口、Open extxyz→原窗口刷新、坏文件保留原系统通过，已查看原生截图；初次沙箱不能连X11，授权显示后执行，8GTK首次skip不算通过。夹具的ToolButton信号、过早导入导致旧wildcard名遮蔽、复用旧chooser问题已修正，非应用功能改动。
- Windows worker新增--read-structure、格式hiddenimports与下次--check-models导入断言；本次未构建或实测新Windows包，11/6交付EXE仍不含此功能。macOS未测；未改原生C++。指南及双语update_2026_11_07.md已同步。无进一步构建待自动执行，后续重新打包需用户任务；保留用户INCAR预设、原图与Fe_single_atom。

## Windows随包ASE／RDKit：已交付（2026-11-06）

- 用户明确要求生成自带ASE/RDKit的Windows版本。已实现独立CPython model-worker、冻结客户端自动选择／子进程环境清理／隐藏控制台和已内置提示；不在GTK/UCRT进程加载MSVC科学DLL。主包脚本新增worker冻结，更新器新增--check-models真实GUI验收，旧版保留。
- Windows缓存：LOCALAPPDATA/p4vasp-build/python-3.13.17，官方embeddable CPython3.13.17＋ASE3.29.0＋RDKit2026.09.1＋PyInstaller6.22.3；引导pip wheel按PyPI元数据SHA256检查，Python来源与下载哈希／依赖清单保留。专用探针在Windows checkout build/windows-update/model-tools，不影响Git干净检查。
- 独立冻结worker的版本查询、32Cu bulk和乙醇MMFF94s收敛实测通过；2路由／隔离、3bulk worker、4SMILES worker、7更新器保护测试、57基础和实际Linux bulk/SMILES GUI回归通过。源码7ccd76d3243ffb20bd2dfab998747d08dad10f3a已提交／推送并完成原生编译、完整冻结构建和实际Windows模型界面验收。
- 交付：Windows Downloads/p4vasp-20261106-231955-7ccd76d3-isn9bffb，双击p4vasp.exe；同名ZIP为156,510,557字节，SHA256 fc109421ddacfbf01cdd9a82fe49c6e26ce4b432bb4101eb36f9855521446823。原构建及迁移Downloads后均通过runtime/gui/models三项：42资源无属性错误、紧凑文件对话框／PNG／POSCAR、实际32Cu bulk与9原子乙醇的随包计算／原生预览／真实保存、非法多片段拒绝和取消回收；PATH仅Windows/System32与Windows，清除外部解释器覆盖，未用构建环境提供科学依赖。模型页截图已查看；ZIP CRC／哈希／源码版本／Python许可检查通过。报告在两处同名-checks目录。
- 后续接手：本任务已完成，无待继续构建；尚未在另一台干净Windows机器验收，未签名，也不等于全部科学结果／普通交互和退出的人工验收。详细双语记录见update_history/update_2026_11_06.md。更新器仍自动包含依赖；不因本次任务自动开展surface等功能。原INCAR预设、原图和Fe_single_atom继续保留，不打包未提交数据。

## DOS缩放刻度长小数（2026-11-06）

- 用户报告缩放后部分Y轴ticks出现很多小数位。graph.py中X/YAxis.render用str(i*major)直接显示二进制尾差；新增Axis.formatTick共用格式，默认6有效数字，按刻度量级／步长增加分辨率（上限17），归一负零。只改文字，不改DOS、能量、范围或刻度位置。
- 2项专项（双轴0.2／0.25步长、负值／负零、近1的1e-8细步长、1e9偏移与2e-12小数值相邻刻度区分）通过。真实Linux X11 DOSCAR曲线缩放／双轴绘制标签捕获／原数据不变通过，截图已查看；8 GTK及57基础通过。其他平台／Windows包未测，操作指南和双语当日记录同步。

## DOS切换与Open载入修复（2026-11-06）

- 用户报告p4v空参／DOSCAR／vasprun.xml首次DOS可见，切其他面板再回来或File/Open载入则空白。用真实Frame/startApplet分发＋合成数据复现GraphCanvas.updateSize调用GTK3 Gdk.Window不存在的get_size，刷新生成器抛AttributeError；现改读绘图DrawingArea实际allocation，兼容尚未realize的状态，保留重绘／视图逻辑。
- getSystem原将DOSCAR当PoscarSystemPM，新增DoscarSystemPM按所选文件读TOTAL_DOS和头部E_FERMI，不要求POSCAR/INCAR（有结构文件时可读），不解析DOSCAR为原子坐标。readDOSCAR按NEDOS读取3列／5列自旋总DOS，忽略后续投影块，校验截断／列不一致；上下通道保留正原始值，由现ElectronicApplet按已有约定负向绘下通道。空参启动无XML但有DOSCAR时载入DOSCAR，无两文件仍空白。
- 本机11/6：3项解析／dispatch／独立源测试通过；实际GTK四种启动（当前XML目录、DOSCAR参数、XML参数、DOSCAR-only目录）、多次Info/Models/Build/电子控制切换、真实文件选择器OK＋含空格路径、活跃图时换源、E−E_F与不同幅度／spin两通道、DOS+bands合成两带、绘图尺寸／可见曲线通过，截图已查看。57基础、8 GTK、32启动和4场景空白启动回归通过（GLUT未测）。GTK／GI弃用及一次初始自然分配提示保留，真实用户计算文件／其他平台／完整人工科学验收／会话存储未核验，不重编译或打包Windows。
- 新测试test/testDoscarSystem.py、test/testElectronicDosGtk.py和test/dos_fixtures.py（仅合成输入）。回归初期不间断清空GTK事件队列导致测试超时，改为有界事件批次；DOS-only跳过不存在XML后留在Info的测试夹具错误已修正，不当作应用缺陷。操作指南及双语当日记录同步；原INCAR预设／原图／Fe_single_atom保留不提交。

## 底部全宽每日一句（2026-11-04）

- 后续按用户要求删除可见“每日一句：”前缀，仅显示名句与出处；实际GTK显示／日期与状态优先回归通过，截图已查看。

- 用户要求原底部文字框改每日名句，左沿到Models右侧。frame.glade原水平进度／状态行改垂直：上方按需进度条，下方status_frame内可选／换行GtkLabel，与applet_box全宽对齐，原statusbar ID及set_text/get_text接口保留。
- daily_quotes.py离线加载data/quotes/daily.json的12条公版经典，按本地日期轮换，缺失／坏文件用后备；gtk3/daily_status.py在空闲／OK时显示，60秒查日期、任务／ERROR优先不被刷新覆盖，destroy清理定时器。FrameMessageDriver接控制器，不改实际日志／错误报出。中文字体仅非darwin调用既有加载器，避免新增触发已知Quartz/PangoFc问题；不声称修复Mac Resources。
- 实际Linux X11检查日期稳定／次日与循环、中文无缺字、700／900宽主内容对齐、可复制、进度条上下位置与显隐、任务／错误优先及计时器回收通过，截图已查看；4场景真实启动回归通过。57基础／32启动通过（不含GLUT）；其他平台、完整GTK旧失败套件及Windows包未测。语句来源/抓取限制见data/quotes/README.md，指南与双语记录同步。

## 空白启动的初始结构误报（2026-11-04）

- 用户报告底部反复ERROR no initial structure available。源码根因：p4v.init无条件追加XMLSystemPM("vasprun.xml")，即使目录无该文件或已有显式系统；SystemPM.fetchStructure随后报错并创建空结构。未修改fetchStructure的真实文件错误行为。
- 启动现仅在无显式／已恢复系统时加载实际存在的默认XML；否则建立带URL空串／PATH当前目录／New structure名称的SetupPM空结构，避免URL未初始化的附带错误。可选setup.xml不存在时不读，存在但坏文件仍保留错误处理。无文件启动不自动把当前目录POSCAR当输入，仍可Open或命令参数指定。
- testStartupSystemGtk.py实际初始化4种隔离临时场景通过：空目录无错误／可见状态OK、显式POSCAR单原子、显式POSCAR＋坏默认XML不干扰、已有无initialpos的XML仍报告真实错误；空白主界面截图已查看。57基础／32启动通过（不含GLUT），未改科学数据、全套GTK／其他平台或Windows包未测。旧进程需重启。

## 建模页底部可复制安装命令（2026-11-04）

- 用户要求ASE与RDKit安装命令直接可复制。gtk3/install_hint.py共用底部提示：只读可选Entry＋Copy command，按实际项目绝对路径和shell转义生成bash install脚本命令，任意工作目录可运行；不自动执行。bulk／gas phase分别接install-ase.sh／install-rdkit.sh，独立于运行状态提示，后续报错不覆盖命令。bulk小窗口可滚动到底部。
- Windows原生／冻结包或脚本缺失时不展示假安装命令，禁用复制并说明需源码环境。实际X11 bulk命令／剪贴板、生成／原生预览／保存／紧凑布局和原gas phase集成通过，底部截图已查看；未安装依赖第二次／改Windows包或跨平台验证。指南与双语当日记录同步。

## ASE bulk 接入检查点（2026-11-04）

- 用户确认首批仅bulk：晶型、晶格参数、超胞、预览、保存POSCAR。Models → bulk已接入13种真实ASE原型，显式晶格参数／primitive-orthorhombic-cubic／基矢重复，最高10000原子；不支持组合报错，参数改变使旧结果失效。surface仍空，不做ASE整套GUI／计算器或本轮Windows打包。
- ase_bulk.py为标准库前端＋独立ASE worker：只点击Build才启进程，单线程数值库、Cancel／30秒超时／销毁取消并回收。install/install-ase.sh创建.gitignore忽略的.venv-ase，当前Linux实际安装ASE3.29.0／worker Python3.14.6；GUI /usr/bin/python3为3.14.4且无ASE，不导入worker依赖。可选P4VASP_ASE_PYTHON覆盖。其他设备／Windows旧包依赖未安装或核验。
- gtk3/bulk.py提供滚动参数页／结果摘要；复用gtk3/gas_phase.py会话辅助窗口与事件保护，新增show_model_preview切换气相共价球或bulk默认资料／标题，防止预览编辑当前系统。single_atom.InputFolderDialog仅增加可选动作文字，bulk保存新文件夹内POSCAR，保留同名保护／取消；需Open后继续编辑，不生成INCAR/KPOINTS/POTCAR或额外约束。
- 本机11/4：5项真实ASE几何／输入（13原型样例、FCC胞／超胞数目体积、NaCl配比距离、HCP／菱方、拒绝非法／超大化学式）；3项真实worker交接／缺依赖／超时取消回收通过。实际X11 GTK＋原生32Cu预览、键盘事件隔离、界面响应、真实保存／取消／不覆盖／POSCAR重读／结果失效／独立bulk滚动页480×320通过，页面与原生截图已查看。完整Models标签有原有最小宽度，不将独立小页尺寸冒充全窗口尺寸。
- 原气相／单原子／Resources-Models实际GTK回归、57基础及32启动通过；Resources退出cmatrix旧警告与ASE/NumPy弃用提示保留。最初测试误用StructureWindow.getStructure已改为实际structure属性；ASE3.29 tetragonal核验失败，未列入首版。未跑完整GTK旧失败套件／其他平台或DFT。指南doc/ase-bulk-zh.md、操作／安装说明及双语当日记录已同步；下一步用户实际bulk反馈，surface待后续明确需求。
- 首次推送因另一设备macOS提交a7841ff被拒，正常merge保留其启动／输入修复及Resources字体崩溃限制；memory冲突保留双方检查点，日期11/4。合并后bulk实际GTK／原生、57基础、32启动再次通过；本机Linux不冒充Mac验收。
- 用户既有INCAR预设修改、根目录原图与Fe_single_atom保持，不纳入提交；不自动重建Windows包或接入RDKit。

## macOS 窗口激活与键盘输入接手检查点（2026-11-03）

- 用户报告本 Mac 已安装，启动窗口在其他应用后面、Models → gas phase → SMILES 无法输入。助手桌面检查：Intel Mac／Darwin24.6.0、Python3.15.2、GTK3.24 Quartz；纯GTK按键成功，加入原生FLTK轮询即丢失，已复现事件循环竞争。
- 已实现 `gtk3/macos.py`：Frame原生初始化前配置进程内Quartz标记，macOS `VisCheck` 处理原生命令并flush，由GTK取Cocoa事件及转交非GTK事件；启动完成后AppKit激活并present一次。涉及 `p4v.py`、`src/VisMain.cpp`，本Mac已重编译，其他源码Mac须重编译。入口为frame.glade→ModelsApplet→models.glade→GasPhasePage，无布局改动。
- 本次专项真实Cocoa输入／退格／Charge、应用激活、原生选中原子Delete事件及返回GTK继续输入通过；旧循环对照按预期失败。截图已查看，完整两秒启动预览、57基础、8 GTK通过；31 applet启动通过、1失败（DBApplet/Resources），不含GLUT。详细证据、命令与限制见 [November 3](update_history/update_2026_11_03.md)。物理键盘／输入法、用户重启反馈、完整人工三维操作及其他平台未验收。
- 新发现独立未解决项：Resources交流页字体注册在macOS非Fc字体后端调用PangoFc，启动检查及单独ResourceHub均在 `PANGO_IS_FC_FONT_MAP` 断言后退出139。未纳入本次两项修复，后续需处理 `gtk3/community.py load_chinese_font` 的后端分支，不能将完整smoke记为通过。
- 已有 `odpdom/cODP.py` SWIG4.4.0→4.5.1生成差异保留、不提交。下一步：用户关闭旧进程后`p4v`验证实际置前与SMILES物理输入；可继续定位Resources字体问题，但不把本检查点当成新增功能授权。提交／推送结果以实际交付报告为准。

## Windows新版交付检查点（2026-11-01）

- 用户已明确恢复打包，之前“Windows暂停”条目为历史。Windows干净checkout从约定origin fast-forward后，UCRT64隔离重编译／PyInstaller完成源提交 `9ba86cd855c52754d3be66be3b9d91d00ec4ad24`。
- 已交付Windows下载目录：`C:\Users\lqlhz\Downloads\p4vasp-20261101-190120-9ba86cd8-g3u1bhr3`，双击p4vasp.exe；同级ZIP为75,104,955字节，SHA256 `4c78367281feafa6586a016be41caf707f60a839df77f7feb647e5d9bd9dfbe1`，整目录／ZIP／哈希已复制且核对。旧版保留，未改快捷方式或用户输入。
- 构建与Downloads迁移冻结runtime／GUI均通过，42个Glade资源无属性错误、原生结构／左右计数、相机PNG、POSCAR标记／紧凑保存窗口通过，截图已查看。新资源确实入包；源码快照另过Resources/Models六网址剪贴板、临时元素编辑、中文缓存／三二维码／放大／窄窗口与单原子生成；不冒充冻结版全部新功能验收。源快照最初连续剪贴板合成检查失败，映射窗口且点击间处理200ms事件后通过，仍见GDK选择警告。
- 迁移首次检查在复制完成前缺DLL，失败报告保留；完整复制后最终成功报告为Downloads同级 `-checks-final`。Windows构建日志在 `build/windows-update/9ba86cd8-f2hf3s7a`（Windows checkout相对路径），源码页面证据在其new-pages；构建产物与checks在dist/windows-releases。
- 构建后Windows --check通过，工作树干净，分支／origin正确；本次诊断脚本已归档到构建证据目录。
- 便携包不带RDKit，SMILES外部环境未验收；干净机、签名、完整正常退出／全部人工键盘建模／科学计算未验证。下一步为用户双击试用；本次交付记录是后续文档提交，EXE仍标上述源提交。双语详情见当日update，指南已同步。

## 更新记录双语格式（2026-11-01）

- 用户要求严格沿用以往English／中文记录更新过程。update_history/update_2026_11_01.md从已提交内容重建，保留原中文过程与证据，补齐对应英文分区；后续维护更新继续使用双语，不用中文用户总结替代维护历史。
- 用户表示已将中文文档移到桌面；当前检查发现当日update文件在工作树缺失，而doc中的综合总结仍存在，未定位／修改桌面文件，不推断具体桌面路径。此次仅核对文档结构、内容对应与差异，不重新验证历史应用结果。

## 近期综合总结文档（2026-11-01）

- 用户要求汇总近期全部总结，已整理doc/recent-updates-2026-11-01-zh.md，覆盖10月13日至11月1日最终功能、使用方式、安装／alias、Windows暂停边界、维护交接与未解决项。作为用户指南型汇总，不替代memory或历史证据。
- 本次仅文档整理；已核对当前资源名单、入口和说明、本地链接、UTF-8、代码围栏及差异。验证章节引用历史检查，不记为本次重跑应用测试；未安装／构建／操作其他平台。

## Useful tools and links 六个入口（2026-11-01）

- ResourceHub标签由Useful tools改为Useful tools and links，原两入口保留，新增ASE https://docs.ase-lib.org/、Pymatgen https://pymatgen.org/、phonopy https://phonopy.github.io/phonopy/、Cantera https://cantera.org/，均已核对官方页面；四列自动换行，点击显示并复制网址行为不变。
- 本机实际X11 GTK六网址显示／真实剪贴板读回、异常后备、中文及原Resources/Models编辑集成通过，640×480截图已查看。既有cmatrix退出警告仍存在；其他平台／浏览器操作未测。指南和当日更新同步。

## 安装末尾两秒预览与alias（2026-11-01）

- install/finish-install.sh统一Linux/macOS收尾：默认启动GUI，p4v.py初始化完成且窗口mapped后计时2000ms退出，打印中文成功与实际路径alias p4v='bash …/p4v.sh'，提示~/.bashrc/source；macOS提示zsh替代。不会自动编辑用户配置，日常启动不变。
- gtk3/install_preview.py提供仅安装时环境开关、60秒启动上限、异常／提前关闭失败处理；无显示跳过且不宣称GUI通过，no-launch/build-only/deps-only不预览。原生3D初始化失败在预览模式传播。
- 本机真实bash install.sh --skip-deps --skip-build预览退出与输出通过（未重新安装／编译），9路由测试、收尾特殊路径alias实际执行／失败返回／无显示与禁启动检查通过；其他平台未运行。install.md与当日更新同步。

## Useful tools 两个入口（2026-11-01）

- ResourceHub新增VASPwiki（https://vasp.at/wiki/Main_page，官方Wiki入口已查）和大师兄网站（用户指定https://www.bigbrosci.com/zh-cn/latest/），四列网格方式排列，点击在本页底部显示并复制网址。与Databases共享show_link逻辑，保留Ctrl+C后备。
- 实际X11 GTK集成验证两个网址显示／真实剪贴板读回／故障后备及中文无缺字，截图已查看；原Resources/Models编辑回归通过。既有cmatrix退出警告仍见，其他平台／浏览器跳转未测。使用指南和当日更新同步，Windows打包保持暂停。

## 中文方框修复（2026-11-01）

- 用户截图报告交流页中文仍为方框；已用GTK先渲染文字再加载页面复现。之前冷启动专项通过不足以覆盖已缓存字体的主界面。
- community.py向Pango实际持有的FcConfig补注册字体并清理PangoFc缓存；已缓存中文的回归、中文无缺字／二维码／剪贴板／窄窗口、Resources与Models集成通过，修复截图已查看。用户实际重启后效果待反馈，其他平台未验证；原集成退出cmatrix警告仍存在。

## 交流与支持二维码（2026-11-01）

- 当前任务完成：Database → Resources 新增“交流与支持”，三张用户JPG按字节复制至data/community；中文卡片、QQ群1131610080复制、点击放大／100%／原图切换。微信仅标昵称BigBroSci，不冒充微信号。根目录用户原图保留，不纳入提交。
- gtk3/community.py负责页面及屏幕范围弹窗；ResourceHub沿用resources.glade宿主及现有Database菜单／GTK3适配器。自带Noto Sans SC及OFL许可，仅进程注册字体，当前Linux原先无中文字体。
- 本机实际GTK中文无缺字、三图与裁剪边界、剪贴板、缩放／完整原图、420宽布局及原Resources/Models集成通过，截图已查看；原集成退出仍见cmatrix析构警告。32个GTK applet启动通过（不含GLUT），发布图片与用户原图逐字节相同。手机扫码、账号有效性及其他平台未测；Windows打包继续暂停。详见当日update记录；后续替换二维码按data/community/README，不自动扩展其他功能。

## Homepage 指向 p4vasp-py3（2026-11-01）

- 用户指定当前主页为 https://github.com/bigbrosci/p4vasp/tree/p4vasp-py3，About顶部已显示可点击Homepage，旧p4vasp.at单独标Original project website；静态后备文字及AUTHORS同步。
- 2项文字／转义与实际GTK两个标题／长路径小工作区检查通过，截图已查看；未实际打开浏览器／重跑全套或其他平台。

## About 版权与贡献说明（2026-11-01）

- 用户明确署名：Python2→3移植主要由Bigbrosci与Whitehare2023共同贡献，随后p4vasp-py3维护／新开发由Bigbrosci负责。新 `about.py` 统一两个版本状态的About文字，保留Orest Dubay原版权，分列移植与后续维护，新增2026 Bigbrosci新贡献版权及仓库地址。`AUTHORS.md`保存同样角色说明；LICENSE与源文件原许可不改，GPLv2文本及原有or-later许可均保留。
- frame.glade静态后备文字同步，About增加滚动／换行／选中复制和屏幕范围尺寸。2项文字与转义测试、实际GTK两个标题状态／可见按钮／长路径480×400工作区检查及32启动通过；实际截图已查看。角色归属按用户提供，不冒充独立Git历史审计。未重跑全套GTK或其他平台；用户INCAR修改和Fe_single_atom目录保留不提交。

## 新增剑桥团簇数据库（2026-11-01）

- 用户指定The Cambridge Cluster Database，原网址 http://www-wales.ch.cam.ac.uk/CCD.html，官方页面已核对（现标题Cambridge Energy Landscape Database）。作为第18张卡片加入，保留指定网址，仍四列换行。
- 5项资源及实际GTK集成通过，含第18项位置和网址剪贴板读回；截图已查看。文档同步，无全套／其他平台验证，已有INCAR修改不纳入提交。

## 新增 NIST-JANAF（2026-11-01）

- 用户指定第17个数据库NIST-JANAF，网址 https://janaf.nist.gov/，官方主页已核对为热化学表SRD13。网站目录新增一项，校验不再限定16项，仍四列自动换行／滚动。
- 5项资源测试与实际GTK集成通过，含第17张卡片位置及JANAF真实剪贴板网址读回；页面截图已查看。文档同步，无其他平台／全套测试，既有INCAR修改未纳入提交。

## 界面文字精简（2026-11-01）

- 用户要求删除single atom底部ISPIN等参数提示，并把Resources的Online databases改为Databases。初始参数提示已移除，状态区初始隐藏、生成成功后显示路径；Resources标签为Databases／Useful tools，生成参数不改。
- 单原子GTK创建／取消／动作、资源与元素表GTK回归、Models启动通过；主界面与标签截图已查看。未重跑全套测试、其他平台或原生编译；已有INCAR预设修改未纳入本次更新。

## Models 独立入口与元素表迁移（2026-11-01）

- 用户要求将左侧 Database 换为独立 Models，Database 菜单删除 Models／只留 Resources。frame.glade 的 astart 改为 ModelsApplet，Models.menupath=None但工厂注册保留。Models 五页顺序 single atom、gas phase、bulk、surface、p4vasp data；ElementTable原组件移入最右侧，数据文件与保存规则不变。Resources 仅 Online databases／Useful tools，继续通过 Database → Resources 访问。
- 本机实际GTK集成验证Resources网址复制、Models五页及元素表临时编辑／保存／非法值拒绝，32 applet启动通过；900×640实际Frame截图已查看。Models/Resources仍隐藏System／Selection，单原子／气相入口沿用。文档当前导航已同步，未重跑全套GTK或其他平台，未改原生代码／无需重编译。
- 本任务开始时已有 data/incar/presets.json 用户修改和未跟踪 Fe_single_atom 目录，均保留、不纳入提交。Windows打包继续暂停。

## 右下角选中原子计数（2026-11-01）

- 用户要求左下角保留总数，右下角显示选中元素与数目。原生VisWindow的HUD已扩为左右独立计数区，右侧如Selected: Cu:1, H:1；按原胞编号去重周期副本、忽略无效编号，按结构元素顺序显示，无选择Selected:0。左右各自折行避免重叠，坐标／选择／导出输入不改。
- 本机原生重编译通过；实际Show/Builder集成、原生框选／键盘回归及初始居中／多视角测试通过。700×500选中／删除后截图已查看：总数96原子时，选中重复Cu副本与H显示Cu1/H1，删除后总Cu63/H19、Selected0。此次未重跑全套基础／启动或其他平台，原生独立测试仍见Fontconfig提示，Windows打包暂停。

## 移除左侧 Commit（2026-11-01）

- 按用户要求从 frame.glade 删除左工具栏 Commit 按钮；旧 CommitApplet／后台代码保留，Database 与其他按钮不改。指南同步。
- 实际GTK加载检查按钮不存在、Database可见及分配尺寸通过，800×600截图已查看。本次仅资源入口删除，未重跑应用全套或其他平台；旧“工具栏Commit保留”记录为历史状态。

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

- 发布核对：macOS文件系统不区分大小写，QQ/qq和WeChat/wechat为相同内容；运行时与测试统一采用Git实际保存的QQ.jpg、WeChat.jpg，避免Linux路径缺失。

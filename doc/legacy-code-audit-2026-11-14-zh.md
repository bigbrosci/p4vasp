# p4vasp旧依赖与遗留代码审计

审计日期：2026年11月14日。源码基线：`38c344da8821eaf0345869c72c329bd8fd174bdd`，分支`p4vasp-py3`。

补充范围：用户随后要求不限Python2/GTK，[全层依赖盘点](dependency-inventory-2026-11-14-zh.md)另列科学库、原生库、外部工具、内置第三方代码、间接依赖与Windows冻结样包证据。

本轮只找问题、评估依赖和清理边界，不删除、迁移或修复应用代码，也不改安装环境。最终清理范围需下一轮确定。

### 同日修复跟进

在保存49ff6cd源码检查点及本机原生/环境记录后，A01改用Thread.is_alive，A02的7处time.clock改为perf_counter；不启用原本默认关闭的属性线程开关，不改VAC数值公式。6项线程/VAC数值回归及真实VAC按钮/曲线检查通过，详见当日更新记录与[恢复说明](dependencies/README.md)。下文仍保留修复前审计证据，不能再将A01/A02描述为最新源码未修复项。

同日第二批已跟进FFT：数组/range长度用整数除法，两处旧GTK.state改按过滤开关状态；修正滤波两端位置及短序列窗口重叠导致的未初始化变量，统一两条滤波路径的单点拟合。新增6项FFT/滤波数值检查及实际FFT按钮/菜单/双图验证通过，保留原频轴/幅度约定，不升级库。旧VAC控制列裁字、全部科学归一化审定及其他旧接口仍未处理，不能将本批检查写成所有VAC场景通过。

同日第三批修复PIDDLE值语义：Color按RGB精确相等、Font按字体属性相等，哈希同步；Color/scalar除法使用Python3入口。保留类名/字段/旧显式方法，不引入大小排序。A03字典__cmp__没有现役调用且总排序语义不明确，仍未迁移；标量/Color反向除法也未擅自定义。5值对象/PS-PDF文本流测试、2实际GTK像素测试及DOS绘图回归通过，pickle仅验证协议2与当前协议往返，不代表历史用户会话已验收。

第四批已修复前述PS/PDF路径输出的str/bytes问题：新增内部字节缓冲与输出边界，PDF索引/流长度按字节，压缩页用标准库zlib/ASCII85；PS状态在失败后恢复，序列化失败不先截断目标。7项专项及真实DOS导出按钮→PS/EPS/PDF通过，含中文路径、二进制流、兼容StringIO、多页/压缩及xref核对。未使用外部阅读器渲染；任意Unicode字体和图片嵌入仍未验证，不把结构检查写成完整格式支持。

第五批已核对其余DATA/AGR/FIG/SVG：DATA/AGR数值回读通过，未修改实现；FIG修复RGB十六进制浮点格式错误、字体名大小写和异常关闭；SVG修复字体只读修改、UTF8声明/命名空间、文本/属性转义和后备字体列表。5项专项与真实DOS七格式导出通过，并通过现有系统GdkPixbuf独立渲染DOS SVG查看结果。未安装依赖；外部Xfig/Grace、FIG任意Unicode字体/图片及SVG图片分支未完整验收。

## 1. 结论

项目不是仍在运行Python 2／GTK2的程序：当前主入口使用Python 3、PyGObject、GTK3和Cairo，Unix及Windows构建入口也已使用Python 3。真正的问题是：新运行时之下仍保留旧接口、过渡适配、历史功能及旧构建入口。

最优先处理的是仍可进入的运行时旧接口，其次是旧SQL分支与旧资源；兼容层、原生模块和图形导出不能仅因年代久就删除。

### 本次覆盖与证据等级

- 对Git已跟踪的1740个文件建立目录清单；其中282个Python文件均完成AST语法解析，语法失败为0。扫描使用本机Python 3.14.6，少量运行探针使用`/usr/bin/python3` 3.14.4。
- 检查主入口、安装/构建脚本、模块导入、字符串注册的applet、Glade加载、导出调用链、Windows冻结清单及生成文件关系。
- 扫描得到238处旧名称/属性候选，**不是238个错误**。例如`StringType`已由兼容层补齐，`file`可能是普通局部变量，`self.clock`可能是正常动画计数，必须逐项判别。
- 小型独立探针验证线程旧方法、旧比较函数、旧SQLite依赖、部分历史绘图模块导入及颜色除法；只操作临时对象/内存数据库，无用户计算输入或用户数据库操作。
- 本轮没有运行完整GUI、科学计算、原生重编译或跨平台测试，不以历史通过记录代替本次检查。不依赖外网资料，结论来自当前源码及本机探针。
- AST无报错只证明能解析，不能证明路径运行正常。静态“未发现引用”也不等于外部脚本、旧会话或动态插件绝不使用。

第六批已去除DBApplet/CommitApplet模块顶层SQL导入，改在旧构造/选择回调时加载。保留旧类路径、注册、Glade及会话入口；3项独立进程检查覆盖阻断SQL的现役启动、合成XML及旧选择回调。未迁移旧驱动、归档旧类或缩减冻结依赖，真实用户数据库/完整旧会话仍未验收。以下表格保留初始审计证据，当前状态以本段及memory为准。

## 2. 当前仍需要保留的依赖

| 组件 | 当前用途及证据 | 本轮判断 |
|---|---|---|
| PyGObject／GTK3／Cairo | `lib/p4vasp/gtk3/__init__.py:8`起明确要求Gtk/Gdk 3.0；`p4v.py:39`使用GTK3绘图 | 当前主GUI基础，保留 |
| GdkPixbuf 2.0 | `gtk3/__init__.py`要求的是独立GdkPixbuf库的版本 | 不等于依赖GTK2，不能按数字2误删 |
| `data/glade2` | `util.loadGlade`实际从该目录加载；43个Glade文件由GTK3适配器处理 | 目录名虽旧，仍是现役布局来源 |
| `p4vasp.gtk3`的Combo／OptionMenu等适配 | `gtk3/__init__.py:160,177`将旧调用方式映射到GTK3控件；`gtk3/glade.py`解释旧XML属性 | 大量现役面板依赖，需逐页迁移后缩减 |
| FLTK／OpenGL／SWIG | 原生Show、STM等窗口，独立于GTK主界面 | 不是旧GTK包，当前不能移除 |
| PyOpenGL／GLUT | `KpointsViewerApplet.py:27`→`paint3d/OpenGLPaint3D.py` | 有独立功能入口，不能因主结构窗口不使用就判废弃 |
| ODP原生XML解析 | `util.py`的XML解析→`p4vasp.ODPdom`→`_cp4vasp`；Unix构建仍编译odpdom源文件 | 现役依赖，`odpdom/`不能整目录删除 |
| NumPy | 数组、计算和绘图；`util.isNumericArray`实际检查`numpy.ndarray` | Numeric字样不等于依赖旧Numeric包 |
| ASE／RDKit及worker | 体相、结构格式导入、热化学、SMILES；Windows另包科学运行组件 | 新功能依赖，不属于本轮旧依赖清理对象 |

## 3. 优先修复：有明确不兼容证据的接口

优先级P1表示先修复后再清理依赖，P2表示可拆分迁移，P3表示整理或长期处理。优先级不是安全漏洞等级。

| 编号 | 位置 | 问题与证据 | 影响范围／建议 |
|---|---|---|---|
| A01 / P1 | `lib/p4vasp/Property.py:124–127` | `isPending()`调用`Thread.isAlive()`；探针将普通Thread赋给Property.thread后，实际得到AttributeError | 属性线程读取路径；改用`is_alive`并验证线程状态，不应删除Property机制 |
| A02 / P1 | `lib/p4vasp/applet/VACApplet.py:186,219–304` | 可从Mechanics → VAC进入的计算生成器仍多次调用`time.clock()`；本机time模块没有此属性 | VAC计算路径；应选合适的计时函数并做真实VAC回归。本次没有执行完整VAC计算 |
| A03 / P2 | `lib/p4vasp/Dictionary.py:296–302` | `__cmp__`调用已不存在的`cmp`；直接调用探针得到NameError | 旧字典比较API。Python 3通常不自动调用`__cmp__`，因此不能写成所有字典操作均坏；需决定替换比较语义还是移除旧API |
| A04 / P1（旧SQL功能内） | `lib/p4vasp/db.py:732` | SQLite连接仍导入`pysqlite2.dbapi2`；`SQLiteDBI(':memory:')`在本机因缺pysqlite2失败 | 旧SQL存储，不是新版网址导航；保留功能则迁移sqlite3，否则先切断入口后归档 |
| A05 / P2 | `lib/p4vasp/piddle/piddle.py:154,157` | Color仅实现`__div__`／`__rdiv__`；探针`Color(1,1,1)/2`得到TypeError | 旧绘图库公共API的Python 3语义缺口；不证明当前某个DOS操作必然失败，需补针对性渲染/颜色运算测试 |
| A06 / P2 | `lib/p4vasp/piddle/piddleTK2/piddleTK.py:18–19` | 已改为`import tkinter`，下一行却仍用未绑定的`Tkinter` | 旧Tk分支的源码错误。本机先因未安装tkinter而导入失败，尚未实际走到NameError；不能把两者混为同一个实测结论 |

A01、A03、A04、A05为本机具体操作复现；A02、A06为源码加运行环境证据，未做对应完整GUI操作。只要保留这些功能，就应修复，不能把有缺陷直接等同于无用。

## 4. 旧SQL数据库：新版导航背后仍有残留

| 编号 | 位置 | 证据与判断 | 清理前置条件 |
|---|---|---|---|
| B01 / P2 | `lib/p4vasp/applet/DBApplet.py:28–31,104,238` | 现役DBApplet继承ResourceHubApplet，显示资源导航；同文件仍带LegacyDBApplet、旧Query及SQL导入 | 先将历史类与现役入口解耦，确认旧会话不会反序列化这些类 |
| B02 / P2 | `lib/p4vasp/applet/CommitApplet.py:38`、`appletlist.py:6` | 按钮/菜单已移除，但类仍被applet字符串注册，Windows spec也据注册表收集模块。注释仍声称toolbar可用，与当前布局不符 | 不是“完全未被导入”；先处理注册、旧会话及打包，再移模块/commit.glade |
| B03 / P2 | `p4v.py:346,702` | 仍绑定`on_commitbutton_clicked`到quickCommit，并保留提交方法；当前两套Glade中未找到这个信号名 | 高置信旧回调候选；兼顾外部插件绑定后可去除，不应误删其他保存/导出操作 |
| B04 / P2 | `db.py:770`、`SQLSystemPM.py`、`utils/commitXDATCAR.py` | MySQLdb接口、SQLSystemPM及命令行提交工具仍形成一组依赖 | MySQLdb名字本身不证明Python2专属；该组属于旧功能决策，不能只删db.py而留引用 |

新版Databases、Useful tools and links、Models无需因此恢复SQL依赖。也不能因为旧Commit已无按钮，就认定其注册、冻结体积和兼容风险都已经消失。

## 5. 旧GTK资源与兼容路径

| 编号 | 对象 | 证据与判断 | 建议 |
|---|---|---|---|
| C01 / P2 | `lib/p4vasp/util.py:484–491`的loadGlade_old | 唯一仍明确导入真正libglade并指向`data/glade`的函数；当前仓库搜索仅见定义，没有调用 | 较高置信归档/删除候选；先核对外部API使用 |
| C02 / P2 | `data/glade/` | 44个跟踪文件，其中14个.glade，总计264639字节；与当前`data/glade2`分离。Windows spec目前复制整个data目录 | 候选旧资源；逐个核对图像引用，不能仅按目录批量删除。未来可先从发行包排除无用部分 |
| C03 / P2 | `lib/pygtk.py`、`lib/gobject.py`、`lib/pango.py` | 现均为GTK3转发/空require垫片；AST未发现非历史Python源码直接导入这些顶层模块 | 候选兼容别名，不是应安装的PyGTK2依赖；先考虑外部脚本、序列化和兼容测试 |
| C04 / 必须暂留 | `lib/gtk/`及`lib/p4vasp/graph.py:27` | graph.py仍实际`from gtk import *`，而本地gtk模块转发GTK3；testGtk3也专门检查该兼容路径 | 不能现在整组删除lib/gtk；先改graph显式导入再做图形/导出回归 |
| C05 / P3 | `GraphCanvas_gtk1.py`、`AppletTree_old.py`、`piddleGTK`／`piddleGTKp4`／`piddleGTK2p4` | 当前文件已是简短转发，没有第二套GTK1/2绘制实现；旧piddle路径还被兼容测试引用 | 可逐步缩减公开别名；仅删除这些小文件对性能/体积帮助有限 |
| C06 / 必须暂留 | `gtk3/glade.py`及GTK3适配控件 | 旧Glade属性、stock图标、OptionMenu、TreeStore等在现役面板仍使用 | 长期逐页改原生GTK3布局；不建议为了清旧名同时迁移GTK4 |

**特别提醒：**`data/glade`和`data/glade2`不能混为一谈；后者是当前界面资源。`deprecated/new-button`也只是移除左侧New按钮前的备份，当前Edit → New功能仍存在。

## 6. 老绘图后端：可缩减，但不能整包删除

### 6.1 明确仍有现役调用的部分

`lib/p4vasp/GraphCanvas.py:165–186`仍调用PS、PDF、FIG和SVG导出；主绘图使用PIDDLE核心及piddleGTK3。因此必须先保留：

- `piddle.py`及GTK3/Cairo后端。
- `piddlePS.py`、`piddlePDF.py`、`piddleFIG.py`、`piddleSVG/`及它们实际引用的辅助模块。
- PS/PDF的字体、图片及格式支持需沿调用链核对，不可只看某个文件没有被主程序顶层导入。

本轮PS／PDF／FIG／SVG模块在本机均能导入，**未验证完整绘图导出**；部分内部图片分支仍用`import Image`等旧名称，不能据模块导入成功认定这些路径可用。

### 6.2 历史后端候选

| 编号 | 对象 | 证据 | 建议 |
|---|---|---|---|
| D01 / P2 | `piddlePIL.py`及`pilfonts/` | 仍用顶层Image/ImageFont/ImageDraw；本机导入缺Image。85个跟踪字体资源主要与该历史后端相关 | 未发现主应用的直接导入，先归档候选；核对Tk及外部脚本后再移字体 |
| D02 / P2 | `piddleQD.py`、`PixMapWrapper.py` | QuickDraw/Qd/MacOS旧接口，本机导入缺Qd | 与当前macOS Cocoa/GTK3不是同一后端；高置信历史实现，仍需检查引用闭包 |
| D03 / P2 | `piddleWX.py`、`piddleWxDc.py` | 使用旧`wxPython.wx`路径，主要被历史piddletest引用 | 主界面不是wx，考虑整组归档而非新增wx依赖来维持无人使用分支 |
| D04 / P2 | `piddleTK.py`、`piddleTK2/` | 旧Tk/PIL后端，TK2包入口还转发到另一份TK；同时存在A06问题 | 不能把“有两份”直接当相同文件；先决定不支持Tk后端，再归档实现和测试入口 |
| D05 / P3 | `piddleGL.py`、`piddleVCR.py`、旧演示/测试 | 未发现应用目录之外部直接导入证据，部分由piddletest动态选择 | 低于完整运行证据的候选；与K点查看的paint3d/OpenGL不是同一组件，不能误删后者 |

整个piddle目录有127个跟踪文件，合计838936字节。不能把这些大小全部算作可节省空间，也不能直接推断Windows ZIP会减少多少。

## 7. 旧构建入口与生成件

| 编号 | 对象 | 判断 | 后续处理 |
|---|---|---|---|
| E01 / P2 | `src/Configuration.mk:1–5` | 明确执行python2并包含Python2 print语句 | 不再是install.sh使用的主构建路径；归档或改成明确拒绝旧入口 |
| E02 / P2 | `src/Makefile`、`src/Makefile.MacOS`、`odpdom/Makefile:12` | 旧Makefile依赖上述配置，odpdom也直接写python2；Mac旧路径还用python-config | 作为旧构建入口一组处理。不是删除src/odpdom源代码 |
| E03 / P2 | `odpdom/setup.py:3` | 仍从distutils.core导入setup/Extension；当前主构建脚本不调用它 | 若保留独立安装需现代化打包；否则归档。当前环境是否由setuptools提供替代未做安装验收 |
| E04 / 必须暂留 | `src/cp4vasp_wrap.cpp` | 搜索到PyInt/PyString/Py_InitModule等，但位于SWIG生成的跨版本条件/别名中；现役构建使用该生成文件 | 不能文本替换或当死代码删除；修改接口应改.i/头文件并按现有流程生成及编译 |
| E05 / 必须暂留 | `src/cp4vasp.py`与`lib/cp4vasp.py` | 逐字节相同，主构建脚本末尾明确复制代理到lib | 有意的构建/运行分工，不是可以随意删一份的重复代码 |
| E06 / P3 | odpdom中的多个ODPdom Python实现 | 目录与lib下有相近接口，但实际扩展导入方式不同，未被完全相同文件检测归为重复 | 需分别验证独立ODP包、当前_cp4vasp路径及minidom回退；不能仅看名字相同就去重 |

当前`install.sh` → bootstrap → `build-unix-py3.sh`及Windows构建链已绕开这些旧Makefile。当前安装脚本未发现要求安装PyGTK2或Numeric的有效依赖项。

## 8. 兼容层、旧保存格式与冗余定义

### 8.1 p4vasp.compat不能直接删除

`lib/p4vasp/compat.py`提供StringType、IntType、ListType等别名，并修改标准库types/string及builtins.intern；`p4vasp/__init__.py`会加载它。Array、Structure、Property、graph、repository、store等仍依赖其导出。

它既是迁移债务，也是目前大量代码能运行的原因。建议逐模块替换星号导入和旧类型判断，最后才关闭全局注入；尤其`InstanceType=object`不能机械改为新类型判断，旧会话序列化/反序列化语义必须测试。

### 8.2 其他候选

- `lib/p4vasp/setupstore.py:51`保留SetupProfile_old，仓库非生成文档中仅查到定义。可作为候选，但旧保存文件可能按类名引用；先做会话样例检查。
- 多个模块中`try: from io import StringIO`失败后又执行同一导入，已经不具备Python2回退作用。属于可单独整理的冗余，不是功能缺陷。
- 很多`from ... import *`、注释掉的旧实现及历史日志增加阅读成本，但不能按行数自动判定无用；避免在科学算法修改中顺便大面积格式化。
- `__cmp__`在字典、PIDDLE颜色/字体中仍出现；__div__等旧数据模型方法需核对当前调用和对应Python3方法，而非只做语法转换。

## 9. 文档、历史备份及资源体积

| 对象 | 跟踪范围与证据 | 处理建议 |
|---|---|---|
| `doc/api/` | 925个跟踪文件、32094794字节（约30.6 MiB），是历史生成HTML等资料 | 适合移出主源码包或重新生成并单独发布；可能保留旧路径和Py2例子，不要当成运行代码缺陷 |
| `deprecated/` | 5个文件、84286字节，README明确说明是New按钮备份 | 明确历史归档；已与现役NewApplet/new.glade检出精确重复，但不代表现役Edit → New可删 |
| `data/glade/applet.glade`与`applet1.glade` | 精确重复 | 属于旧资源整理候选，仍先核对资源关联 |
| `lib/cp4vasp.py`与`src/cp4vasp.py` | 精确重复但有构建复制关系 | 保留，见E05 |
| ignored构建、虚拟环境、缓存 | 非Git跟踪；.gitignore已排除.so/.pyd/__pycache__等 | 不把本机生成文件计作仓库死代码；不自动删除用户虚拟环境和构建缓存 |

Windows spec复制整个data目录，因此旧data/glade确实有随包带入的可能；但doc/api没有在该datas清单中，不能声称删除30 MiB文档就能让当前EXE缩小30 MiB。

## 10. 建议清理顺序与验收范围

1. **先修明确兼容缺陷：**A01、A02；再决定A03/A05的API语义。测试属性线程、真实VAC任务、颜色/字典行为，避免只测面板能启动。
2. **拆旧SQL与现役Resources：**明确不再维护SQL后，再迁移LegacyDBApplet／CommitApplet／SQLSystemPM／提交工具、注册表、Glade及旧会话处理；不是只移除按钮。
3. **归档无主路径的构建/资源：**E01–E03、loadGlade_old、data/glade、明确历史备份。先检查文本引用和打包清单，移除后做安装、Glade加载及打包清单回归。
4. **缩减历史绘图后端：**优先QuickDraw、wx、Tk/PIL分组；保留GTK3及PS/PDF/FIG/SVG，并测试实际导出，包括图像、Unicode、字体等分支。paint3d保留独立评估。
5. **逐模块去Python2兼容语法：**处理星号导入、类型别名与旧方法，保留会话读写兼容测试，最后再考虑删除全局compat注入和顶层gtk别名。
6. **独立整理生成文档：**不与科学代码重构混为一个提交，不承诺未测的平台或EXE效果。

以上是待实施路线，**本次没有执行任何一项清理**。需要逐批提交、逐批验证，保留可回退边界。

## 11. 本次最小检查摘要

| 检查 | 本轮结果 | 限制 |
|---|---|---|
| 跟踪Python文件AST解析 | 282/282通过 | 不证明运行路径正常 |
| Thread属性状态探针 | 复现isAlive AttributeError | 临时Thread，没有启动用户任务 |
| StructuredDictionary旧比较 | 复现cmp NameError | 直接调用旧API，不等于常规相等操作失败 |
| time.clock | 当前解释器无该属性，VAC源码仍调用 | 未执行完整VAC GUI |
| SQLite内存连接 | 缺pysqlite2 | 无用户数据库操作；MySQL未连接 |
| Color除法 | TypeError | 未推断所有现役图都受影响 |
| PIL/QuickDraw历史模块导入 | 分别缺Image/Qd | 未安装这些旧依赖 |
| Tk2导入 | 本机先缺tkinter，另有未绑定Tkinter静态证据 | 未测试安装tkinter后的完整后端 |
| PS/PDF/FIG/SVG模块导入 | 均通过 | 不代表实际导出/图片分支通过 |
| GUI／原生／Windows／macOS完整验收 | 未运行 | 本轮为审计，未改变应用 |

临时扫描明细保存在`/tmp/p4vasp-legacy-audit.json`，它是本机辅助证据而非项目运行依赖；后续会话可能已不存在，以本报告的源码基线和位置为准。用户XDATCAR未读取或提交。

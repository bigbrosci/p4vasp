# p4vasp全层依赖盘点：Python库、原生库与打包组件

日期：2026年11月14日。源码基线：`2825886`（上一轮审计报告提交，应用源码仍为38c344d）。

这是对[旧依赖与遗留代码审计](legacy-code-audit-2026-11-14-zh.md)的扩展：不仅找Python2／GTK残留，还覆盖科学计算、文件格式、绘图、系统动态库、构建工具、内置第三方源码、传递依赖及便携包重复组件。只盘点，不清理、不安装、不升级。

## 1. 先说结论

需要审查的不只是“过时的库”，还包括以下情况：

1. 库仍有用途，但版本或平台声明不完整。
2. 主代码没直接导入，却被ASE／RDKit等间接依赖。
3. 已经不走的历史代码还引用缺失的库。
4. 同一库在不同Python／ABI环境重复携带，不能直接合并。
5. 第三方实现直接放在源码里，pip包列表根本看不到。
6. 字体、系统动态库、构建命令由运行时动态寻找，不会全部出现在Python导入语句中。
7. 顶层版本固定而间接依赖浮动，无法仅凭Git提交完全重建相同环境。

本轮已覆盖上述层次，但不宣称穷尽所有外部插件、动态格式插件或所有DLL的兼容情况。没有做在线漏洞库扫描，也没有认定任何库因年代老就存在安全漏洞。

## 2. 依赖地图

```text
p4vasp主进程（Python 3）
├─ PyGObject → GTK3 / GLib / Pango / GdkPixbuf
│  ├─ Cairo / FreeType / HarfBuzz / Fontconfig等字体绘制组件
│  └─ Linux显示后端 / macOS Quartz / Windows系统绘制
├─ NumPy → 现役数组、声子、VAC、渲染等
├─ _cp4vasp → FLTK 1.3 / OpenGL / GLU / C++运行库 / Python ABI
│  └─ 集成ODP XML解析器
├─ PyOpenGL → 独立K点GLUT查看器
├─ 项目内PIDDLE及PDF/PS/FIG/SVG实现
├─ 可选旧SQL → pysqlite2 / MySQLdb / 自带UUID实现
└─ 独立科学worker（JSON通信）
   ├─ ASE → NumPy / SciPy / Matplotlib / typing_extensions
   └─ RDKit → NumPy / Pillow
```

构建与运行分开：C++编译器、SWIG、Python开发头、fltk-config、pkg-config、Make、Git、pip和PyInstaller主要服务安装/发布，不表示便携版用户必须安装它们。

## 3. Python及科学库清单

| 库／组件 | 现役用途 | 是否可直接清理 | 检查位置及说明 |
|---|---|---|---|
| NumPy | Array、VAC、声子、渲染、ASE/RDKit计算 | 不可 | `Array.py`、`PhononsCalculation.py`、`render_studio.py`、`VACApplet.py`等均实际使用 |
| SciPy | ASE相关算法的传递依赖 | 不可仅凭没有直接import就删 | `.venv-ase`的ASE元数据要求`scipy>=1.8.1`；Windows科学worker也打入SciPy |
| ASE | bulk、非VASP结构读取、热化学、频率处理所需结构/元素数据 | 保留可选worker | `ase_bulk.py`、`ase_import.py`、`vibrations.py`；主GUI解释器不必安装ASE |
| RDKit | SMILES、ETKDG构象、MMFF/UFF初步优化 | 保留可选worker | `smiles_builder.py:23`起；不是只能画二维图的依赖 |
| Matplotlib | ASE安装元数据中的要求 | 可研究发行裁剪，不能直接删环境依赖 | ASE要求`matplotlib>=3.5.2`；本项目主GUI画图用Cairo/PIDDLE。Windows两份spec显式排除Matplotlib，本轮实际样包也未见其目录；不代表ASE所有未来功能都不需要它 |
| Pillow | RDKit传递依赖，也出现在部分历史绘图分支 | 需分开评估 | RDKit元数据要求Pillow，Windows科学worker存在PIL目录；旧代码顶层`import Image`不是现代Pillow正常导入方式 |
| typing_extensions | ASE安装依赖 | 不能只按项目源码搜不到就删 | 当前ASE元数据要求`>=4.13.1` |
| PyOpenGL | K点查看器及旧绘图分支 | 不可整库删除 | `KpointsViewerApplet`→`paint3d/OpenGLPaint3D`为现役；旧piddleGL是另一条历史路径 |
| PyGObject / pycairo / gi-cairo桥 | 主界面与Cairo GTK绘图 | 保留 | 是多个关联包，不是装一个gtk命名的pip包即可替代；apt/homebrew/MSYS2安装方式分别处理 |
| tkinter | 历史PIDDLE Tk后端 | 主界面不要求 | 本机GTK解释器没有该模块；Windowsspec显式排除。别为维持未用旧后端贸然加入全局依赖 |
| pysqlite2 / MySQLdb | 旧SQL功能 | 先决定去留 | 新Resources网址导航不依赖SQL，但Commit仍注册；第一份报告有详细证据 |
| zlib / xml / json等 | 标准库或Python系统构建能力 | 不是普通pip依赖 | 不把标准库当第三方待卸载包 |

### 本机环境快照（只读元数据，不是全功能验收）

| 环境 | Python | NumPy | ASE | SciPy | RDKit | Pillow | Matplotlib |
|---|---|---|---|---|---|---|---|
| GTK解释器 `/usr/bin/python3` | 3.14.4 | 2.3.5 | 未发现发行元数据 | 未发现 | 未发现 | 未发现 | 未发现 |
| `.venv-ase` | 3.14.6 | 2.5.4 | 3.29.0 | 1.18.1 | 未发现 | 13.0.0 | 3.11.2 |
| `.venv-smiles` | 3.14.6 | 2.5.4 | 未发现 | 未发现 | 2026.9.1 | 13.0.0 | 未发现 |

GTK环境另发现PyGObject 3.56.2、pycairo 1.27.0、PyOpenGL 3.1.10的发行元数据。表中“未发现”指该解释器的importlib.metadata结果，不等于本机从未装过、不等于其他环境没有，也不保证有元数据的包都能成功运行。

NumPy在三个环境版本不同，当前通过进程/JSON隔离；不能把这种隔离误判为同一进程混用。也不能把一个虚拟环境的成功当成主进程依赖齐全。

## 4. C/C++与系统动态库

### 4.1 本机原生扩展实际声明的链接依赖

只读`readelf -d lib/_cp4vasp.cpython-314-x86_64-linux-gnu.so`得到：

- `libfltk_gl.so.1.3`、`libfltk.so.1.3`
- `libGLU.so.1`、`libGL.so.1`
- `libpython3.14.so.1.0`
- `libstdc++.so.6`、`libgcc_s.so.1`
- `libm.so.6`、`libc.so.6`

这不是Windows或macOS的链接清单，也不穷尽FLTK/GL自身的传递依赖；系统库不应随项目清理动作从操作系统删除。

### 4.2 静态import看不到的依赖

| 对象 | 依赖来源 | 风险／边界 |
|---|---|---|
| 字体注册 | `gtk3/community.py`用ctypes寻找fontconfig、pangocairo、pangoft2；Windows调用gdi32 | 不是普通Python模块；历史macOS崩溃正涉及不同字体后端映射，不能合并为一个无平台分支 |
| macOS激活／事件 | `gtk3/macos.py`调用系统libobjc及AppKit/GTK Quartz | 当前无需额外PyObjC；不要因未见pip包就当缺依赖 |
| GLUT | PyOpenGL的K点查看器 | 本机找得到`libglut.so.3`，`glutInit`符号可用；没有真正打开GLUT窗口。Ubuntu bootstrap未显式列出GLUT开发/运行包，是否由系统/传递依赖补齐需在干净设备核验 |
| X11及字体/窗口扩展 | Ubuntu bootstrap的X11/Xcursor/Xext/Xft/Xinerama/Xrender相关开发包，FLTK显示链 | 不是旧GTK2证据；是否可缩减要按编译/链接和目标显示后端验证 |
| OpenGL驱动与兼容接口 | Show的即时模式GL、GLU球体等 | 源码依赖兼容绘图接口；升级窗口库或图形上下文不能按普通Python包升级看待 |

本机find_library能找到GL、GLU、GLUT、FLTK、fontconfig、pangocairo、pangoft2；这仅证明库可定位。没有以此声称显卡、驱动、显示服务器和全部ABI都验收通过。

## 5. 内置第三方实现与历史特殊库

这些通常不会出现在`pip list`里。

| 对象 | 本轮发现 | 建议 |
|---|---|---|
| 项目内PIDDLE | 同时带GTK3、格式导出及多个历史后端 | 依功能闭包裁剪；前份报告已区分现役导出与历史GUI后端 |
| 项目内PDFgen/pdfdoc/pdfmetrics | 源文件带1998–1999年的第三方实现和版权条款，piddlePDF仍使用 | 不能因为pip未装reportlab就认为PDF依赖不存在；也不能把项目内实现与现代ReportLab发行包简单视作可互换 |
| `lib/p4vasp/uuid.py` | 自带UUID实现，版本0.3.2，`db.getDatabase`仍调用 | 可考虑迁移标准库uuid，但要保留旧ID格式；本轮导入成功，未做算法等价测试。名称里MD5/SHA1属于UUID类型，不据此认定密码安全问题 |
| ODPdom | 内置C++解析器及Python接口，另有LGPL许可文件 | 当前XML处理依赖，保留或另立解析器替换任务，不因不是pip库就忽略 |
| GLTT | `piddleGL.py:328`顶层导入`GLTT.GLTTFont`，并非只有注释提及 | 历史文字/OpenGL后端候选；与PyOpenGL/现役GLUT查看器分开处理。未安装GLTT做验收 |
| `xmllib` | `piddle/stringformat.py:40`导入；实际导入该模块失败，缺xmllib | 旧格式化分支需归档或替换解析器；未发现主路径外部直接导入，不自动加装同名第三方包来蒙混兼容 |
| QuickDraw生态 | Qd、QuickDraw、MacOS、W、Wkeys、Events、Evt、Fonts、Scrap、QDRotate等历史引用 | 不属于当前macOS Cocoa方案；按旧后端整组核对，避免一个一个追装 |
| wxPython旧API | `wxPython.wx` | 不是当前主界面必需，不应为修某个历史分支加入一套新GUI工具包 |
| `img`／`imgformat`／`macfs` | PixMapWrapper、pdfdoc历史平台分支中仍可见 | 不是主启动必装清单，实际调用条件需细查后再移除 |
| `textClasses` | polyfunc中的测试函数引用 | 导入polyfunc本轮成功，不能把嵌套测试导入认定启动依赖缺失 |

AST扫描中的`from .MeshTools`、`from .core`属于项目相对导入，**不应误判成要pip安装MeshTools/core**。同样，`cp4vasp`和`_cp4vasp`是项目代理/原生模块，不是随便安装一个PyPI同名包即可解决。

第三方源码、字体和参考数据的原始署名/许可应随归档和发行清单保留；本轮仅做来源盘点，没有进行完整许可审查或法律判断。

## 6. 外部工具：安装时、文档时和运行时分开

| 工具／能力 | 使用阶段 | 本机情况／证据 |
|---|---|---|
| g++、SWIG、Python开发头、python-config、fltk-config | 原生构建 | 主构建脚本显式检测；本机相关可执行命令可找到 |
| Make、pkg-config | 平台安装/构建 | bootstrap列出，当前PATH可找到；不表示主构建的每一步都调用Make |
| Git、Bash、Windows PowerShell | 更新、打包编排及重放 | 不应当作用户双击已打包GUI的运行前提；生成.ps1仍依赖PowerShell |
| pip、venv | Unix可选科学环境及Windows构建缓存准备 | 不应污染GTK解释器，当前脚本建立隔离环境 |
| PyInstaller及altgraph、pefile、hooks-contrib等 | EXE构建工具链 | 构建缓存有这些发行包；不等于成品运行需另安装它们 |
| epydoc、doxygen | `doc/Makefile`生成旧API文档 | 本机两个命令都未找到；这是旧文档重建缺依赖，不是主GUI不能启动 |
| POV-Ray | 使用导出的.pov文件进一步渲染 | ExportApplet生成Povray文件；未发现该导出路径必须启动povray的证据。本机无povray命令，不影响“仅写.pov”的判断 |
| 系统浏览器／剪贴板 | 用户使用网站入口、复制等 | 当前网站导航展示并复制链接，不需要装一个额外Python浏览器库 |

旧`src/fltk-config.py`在实际运行时可能调用`ext/build-fltk.sh`本地构建FLTK；主build-unix-py3.sh直接查找fltk-config。两条路径不要混用，也不应将旧辅助脚本的本地缓存当作主入口必须保留的依赖。

## 7. Windows冻结包的实际携带情况

检查对象是**11月12日已交付的4add680构建**：`p4vasp-20261112-211415-4add6800-gkmr_u_4`。它用于本轮依赖样本，不是11月13日XDATCAR源码的新构建验收。

### 7.1 实际文件清单与大小

| 区域 | 文件数 | 文件字节合计 | 说明 |
|---|---:|---:|---|
| 主GUI `_internal` | 1444 | 154557675 | GTK/UCRT Python及其依赖、数据等 |
| 科学worker `_internal` | 616 | 180276495 | 独立官方CPython、ASE/RDKit等 |
| GUI内dependency-licenses | 116 | 1362631 | 是上面GUI目录的子集，不可重复加总 |

整个样包共找到176个.dll文件。数量多不等于都有问题；字节合计不是ZIP大小，也不代表均可删除。

GUI与worker里都发现NumPy；GUI中未见SciPy／PIL／Matplotlib／RDKit目录，worker中有SciPy、PIL、RDKit，未见Matplotlib目录。PyInstaller可能还把Python模块放入归档，目录清单不是所有模块的完整清单。

### 7.2 哪些重复暂时有理由

主GUI使用MSYS2 UCRT Python 3.14，科学worker使用官方CPython 3.13。NumPy的二进制模块及BLAS等不能简单互换，双环境解决的是科学wheel与GTK工具链的兼容问题。

因此“发现两份NumPy”不等于“删掉一份就好”。若要减包，需要独立评估是否统一运行时；那是架构任务，需同时验收GTK、原生扩展、ASE、RDKit、文件格式、取消/退出等，不在本轮实施。

### 7.3 可以继续研究的体积候选

- `model_worker.spec`对ASE/RDKit使用较广的数据/动态库收集，可能带入非当前功能使用的数据；需要按现有化学/格式/热化学路径建立清单后裁剪，不能直接只保留能让import成功的文件。
- `p4vasp.spec`复制整个系统share/licenses目录，存在与实际运行二进制不一一对应的条目。该子目录约1.3 MB，不能凭此承诺大幅减包；也不能先删许可再判断依赖。
- 当前spec已排除Matplotlib、Tk及若干Qt模块，不能把它们作为“新发现可以立即从EXE删除”的节省量。
- 旧data/glade资源有整目录随data打包的路径，仍是可追踪的资源候选；历史doc/api则不在该清单中。

没有删除DLL、修改spec或重打包，也没有逐一验证176个DLL的来源、可加载性、版本兼容或漏洞状态。

## 8. 版本和重建可复现性

| 位置 | 已固定内容 | 尚未完全固定的内容 |
|---|---|---|
| `install/install-ase.sh` | ASE 3.29.0 | NumPy/SciPy/Matplotlib等由安装时解析 |
| `install/install-rdkit.sh` | 无RDKit精确版本 | RDKit及传递依赖均随安装环境解析 |
| `prepare_model_env.py` | CPython 3.13.17、ASE 3.29.0、RDKit 2026.9.1、PyInstaller 6.22.3；pip启动轮子也指定版本 | 间接依赖及PyInstaller hooks等仍可能变化 |
| apt/Homebrew/MSYS2 | 在脚本中声明包名/部分系列 | 系统仓库版本随日期变化，不是跨平台统一锁定 |

Windows准备器把`pip list`写入构建缓存的PACKAGES.json，它是**构建后的记录**，不是安装前严格执行的锁文件；成品MODEL-VERSIONS.json也不是全部依赖清单。当前仓库未发现统一requirements/lock文件。

CPython下载使用官方HTTPS，下载后记录SHA256，代码没有用仓库中预先固定的期望摘要做独立比对；pip wheel启动段则有与返回元数据摘要的比较。这里记录两者验证机制不同，不据此认定下载已被篡改，也未联网重新核验上游发行内容。

建议后续按平台分别保存直接/间接依赖版本及来源、解释器/ABI、原生库和构建工具版本；再决定哪些需要严格锁定。不能把Windows锁文件直接套给Linux或macOS，也不要将操作系统包与pip依赖混为一份“删除清单”。

## 9. 后续清理分组建议

1. **功能缺陷组：**前份报告的isAlive、time.clock、cmp等，加上本轮发现的xmllib历史分支。现役功能优先修；无主入口历史分支先决定归档。
2. **历史第三方组：**QuickDraw/wx/Tk/PIL/GLTT及老测试、未用格式化模块，按依赖闭包处理；不删除仍用于PS/PDF导出的组件。
3. **依赖声明组：**补充GLUT等功能所需平台声明，区分必需/可选/构建/开发依赖，给出分层清单。
4. **版本复现组：**统一记录各平台的版本/ABI及间接包清单，先记录再讨论锁定策略。
5. **冻结包裁剪组：**先做清单和依赖图，再裁数据、DLL与重复环境；用成品功能测试验证，不只看构建成功。
6. **许可证与来源整理组：**对项目内第三方源码、字体、数据、冻结库建立对应索引，迁移时保留来源记录。

这六组都只是待办建议，本轮无执行。不能把“用户不知道的库”或“不是主Python直接import的库”自动判为垃圾。

## 10. 本轮检查限制

已做：Python导入位置盘点、包发行元数据读取、环境间比较、原生ELF依赖读取、系统库/命令定位、部分历史模块导入、Windows样包文件/目录/大小清单、安装和spec源码核对。

未做：联网下载/安装/升级、用户计算与数据库读取、完整GUI/科学计算、macOS/Windows运行、每个文件格式插件逐项测试、所有动态库递归解析、完整SBOM生成、在线漏洞或完整许可审查。数据存在、命令存在、模块可导入都不等同于功能完整验收。

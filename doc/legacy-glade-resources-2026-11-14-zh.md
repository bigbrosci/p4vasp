# 旧Glade资源与打包引用核对（2026-11-14）

后续实施状态：用户批准后，2026-11-14第九批已移除本报告列出的44个data/glade文件和util.loadGlade_old，data/glade2不变。新增真实加载/图片解码回归通过，9 GTK、57基础、33面板通过；未构建Windows，现有安装包不会因此自动变化。以下保留删除前5225117审计记录（其检查源码基线为fdbcc2e），供历史追溯，不应把旧路径理解为当前存在。

源码基线：`fdbcc2e`，本机Linux/WSL检查。本轮为核对，不删除资源、不修改加载器或打包配置，不生成Windows版本。

## 结论与当前入口

- `data/glade/`共44个Git跟踪文件、264639字节（14份布局205759字节，30张图片58880字节）。它与仍在使用的`data/glade2/`是不同目录，不能按名称一起清理。
- `p4v.py`的Frame和Applet的`gladefile`通过`p4vasp.util.loadGlade`进入GTK3适配器，路径固定为`data/glade2/`；图形/结构等现役同名布局也使用这条路径。
- `lib/p4vasp/util.py`的`loadGlade_old`仍指向旧目录并在调用时导入真正的libglade。排除生成API、历史记录和审计文字后的仓库源码检索仅发现其定义，没有现役调用。无法从仓库检查证明外部插件从未使用该函数。
- 因此旧目录已是可移除候选；删除应与旧加载函数的处理配套，避免留下指向不存在目录的接口。历史内容可由Git查阅，不需要再复制一套归档。

## 布局逐项清单

14份旧布局都存在同名的现行布局，但SHA256均不相同，不能用旧文件覆盖现行文件。

| 旧布局（相对data/glade） | 字节数 | 同名现行布局 | 标准XML检查 |
|---|---:|---|---|
| `applet.glade` | 2457 | `data/glade2/applet.glade` | GTK-Interface |
| `applet1.glade` | 2457 | `data/glade2/applet1.glade` | GTK-Interface |
| `applet2.glade` | 3178 | `data/glade2/applet2.glade` | GTK-Interface |
| `frame.glade` | 34532 | `data/glade2/frame.glade` | ElementTree解析失败：85行15列 |
| `graphapplet.glade` | 3534 | `data/glade2/graphapplet.glade` | GTK-Interface |
| `graphwindow.glade` | 9550 | `data/glade2/graphwindow.glade` | GTK-Interface |
| `lbandsapplet.glade` | 27735 | `data/glade2/lbandsapplet.glade` | GTK-Interface |
| `ldosapplet.glade` | 29811 | `data/glade2/ldosapplet.glade` | GTK-Interface |
| `manipulatestructureapplet.glade` | 24786 | `data/glade2/manipulatestructureapplet.glade` | GTK-Interface |
| `mytest1.glade` | 6228 | `data/glade2/mytest1.glade` | GTK-Interface |
| `phonons.glade` | 11839 | `data/glade2/phonons.glade` | glade-interface |
| `structureapplet.glade` | 44927 | `data/glade2/structureapplet.glade` | GTK-Interface |
| `structuremeasure.glade` | 2299 | `data/glade2/structuremeasure.glade` | GTK-Interface |
| `textapplet.glade` | 2426 | `data/glade2/textapplet.glade` | GTK-Interface |

`frame.glade`的失败是旧文件的标准XML探针结果，不是现行frame.glade故障，也没有使用古老libglade做兼容验收；其余13份可被标准XML解析，不等于可被GTK3适配器直接使用。

## 图片逐项清单

以下15种图片在旧目录根部及其pixmaps子目录各有一份，共30份。逐文件SHA256与现行根目录、pixmaps目录的同名图片均一致；保留现行副本即可，不需要从旧目录搬运。

| 文件名 | 旧位置 | 内容相同的现行位置 |
|---|---|---|
| `arrowsXYB.xpm` | `data/glade/arrowsXYB.xpm`；`data/glade/pixmaps/arrowsXYB.xpm` | `data/glade2/arrowsXYB.xpm`；`data/glade2/pixmaps/arrowsXYB.xpm` |
| `arrowsXYF.xpm` | `data/glade/arrowsXYF.xpm`；`data/glade/pixmaps/arrowsXYF.xpm` | `data/glade2/arrowsXYF.xpm`；`data/glade2/pixmaps/arrowsXYF.xpm` |
| `arrowsXZB.xpm` | `data/glade/arrowsXZB.xpm`；`data/glade/pixmaps/arrowsXZB.xpm` | `data/glade2/arrowsXZB.xpm`；`data/glade2/pixmaps/arrowsXZB.xpm` |
| `arrowsXZT.xpm` | `data/glade/arrowsXZT.xpm`；`data/glade/pixmaps/arrowsXZT.xpm` | `data/glade2/arrowsXZT.xpm`；`data/glade2/pixmaps/arrowsXZT.xpm` |
| `arrowsZYL.xpm` | `data/glade/arrowsZYL.xpm`；`data/glade/pixmaps/arrowsZYL.xpm` | `data/glade2/arrowsZYL.xpm`；`data/glade2/pixmaps/arrowsZYL.xpm` |
| `arrowsZYR.xpm` | `data/glade/arrowsZYR.xpm`；`data/glade/pixmaps/arrowsZYR.xpm` | `data/glade2/arrowsZYR.xpm`；`data/glade2/pixmaps/arrowsZYR.xpm` |
| `cube.xpm` | `data/glade/cube.xpm`；`data/glade/pixmaps/cube.xpm` | `data/glade2/cube.xpm`；`data/glade2/pixmaps/cube.xpm` |
| `cuc.xpm` | `data/glade/cuc.xpm`；`data/glade/pixmaps/cuc.xpm` | `data/glade2/cuc.xpm`；`data/glade2/pixmaps/cuc.xpm` |
| `home.png` | `data/glade/home.png`；`data/glade/pixmaps/home.png` | `data/glade2/home.png`；`data/glade2/pixmaps/home.png` |
| `home.xpm` | `data/glade/home.xpm`；`data/glade/pixmaps/home.xpm` | `data/glade2/home.xpm`；`data/glade2/pixmaps/home.xpm` |
| `perspective.xpm` | `data/glade/perspective.xpm`；`data/glade/pixmaps/perspective.xpm` | `data/glade2/perspective.xpm`；`data/glade2/pixmaps/perspective.xpm` |
| `tuc.xpm` | `data/glade/tuc.xpm`；`data/glade/pixmaps/tuc.xpm` | `data/glade2/tuc.xpm`；`data/glade2/pixmaps/tuc.xpm` |
| `zoom11.xpm` | `data/glade/zoom11.xpm`；`data/glade/pixmaps/zoom11.xpm` | `data/glade2/zoom11.xpm`；`data/glade2/pixmaps/zoom11.xpm` |
| `zoomm.xpm` | `data/glade/zoomm.xpm`；`data/glade/pixmaps/zoomm.xpm` | `data/glade2/zoomm.xpm`；`data/glade2/pixmaps/zoomm.xpm` |
| `zoomp.xpm` | `data/glade/zoomp.xpm`；`data/glade/pixmaps/zoomp.xpm` | `data/glade2/zoomp.xpm`；`data/glade2/pixmaps/zoomp.xpm` |

现行43份布局共124处非stock文件图片引用，按适配器`_image_path`实际候选顺序（布局目录、data、data/pixmaps）检查：124处可解析，0处落入data/glade，0处缺失。检查覆盖icon/pixbuf/pixmap/file/filename属性；不推断外部插件生成的任意动态路径。内容相同不代表本轮已删除现行目录里的重复图片，后者尚未整理。

## 安装与打包边界

| 入口 | 本轮源码证据 | 影响 |
|---|---|---|
| 当前Linux/macOS安装和原生构建 | bootstrap/wrapper使用当前checkout及build-unix-py3.sh，未见data/glade专用复制步骤 | 不需要旧布局来编译C++/ODP；macOS本机未执行 |
| Windows GUI `install/windows/p4vasp.spec` | datas显式包含整个data目录；package-windows.sh执行此spec | 旧目录仍会被递归带入后续GUI包；没有单独的glade排除项 |
| Windows科学worker `install/windows/model_worker.spec` | 收集ASE/RDKit资源、元数据及LICENSE，不显式收集项目data | 不是旧Glade的显式来源；未执行PyInstaller分析，不声称已核对全部hook产物 |
| 运行时GTK资源 | util.loadGlade→GTK3适配器→data/glade2 | 保留整套现行布局及其图片、资源搜索顺序 |

本轮只静态检查Windows配置，不构建EXE，也不估算压缩后节省量。264639字节是本次旧目录跟踪文件总量，不等于ZIP缩减量。

## 验证与后续边界

- 新鲜运行本机8项GTK检查通过，包含43份现行资源加载；33个面板启动检查通过（不含独立GLUT查看器）。日志`/tmp/p4vasp-glade-audit-{gtk,smoke}.log`。
- 临时逐文件SHA256/属性解析明细`/tmp/p4vasp-glade-audit.json`，辅助脚本`/tmp/p4vasp-glade-audit.py`；临时证据不保证跨会话保留，以本报告清单和源码基线为准。
- 以上是合成加载/启动及静态引用证据，没有本轮布局变更或视觉修复声明，没有完整科学流程、历史libglade、外部插件或Mac/Windows验收。
- 后续可将旧目录和旧加载函数作为一批删除，随后检查现行资源图片加载、菜单/面板与静态打包输入。保留data/glade2、GTK3适配器、兼容会话类以及deprecated中的历史New按钮说明。
- 用户XDATCAR未读取或提交，未升级任何库，Windows继续最后更新。

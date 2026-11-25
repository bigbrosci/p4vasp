# 数据库导航与内部资料

从顶部菜单 **Database → Resources** 打开在线数据库及 Useful tools；元素表从左侧 **Models → p4vasp data** 打开。此页面隐藏共用的 System／Selection 两行；切回结构编辑面板恢复。

## 在线数据库

18 张卡片按四列排列，新增项目自动换行，必要时滚动，只显示网站名称。点击后在网格下方显示可选中复制的网址，并自动复制到剪贴板；不自动打开浏览器。剪贴板不可用时可在网址框按 Ctrl+C 手动复制。悬停显示用途和网址，启动不联网获取图标或数据。

网站目录为 `websites.json`。部分服务需注册、订阅或许可证，导航不提供这些权限。左侧 Models 以顶部横向五个标签页 single atom、gas phase、bulk、surface、p4vasp data 展示模型及元素资料，Database 菜单只保留 Resources；左侧工具栏 Commit 已移除。

## 元素资料表

**p4vasp data** 用周期表显示 H 到 Og 的 118 个元素，元素格使用默认RGB颜色及已保存的个人覆盖；没有颜色资料时显示中性灰。点击元素，在属性弹窗中修改mass (u)、radii (Å)、RGB (0–255)、Magmom (μB)、U/J (eV)。Name与atomic number只读。颜色可用选择器或RGB输入，点弹窗Save保存并刷新元素格；Cancel/关闭不保存。结构默认值仍需重启p4vasp后应用。周期表自动适应当前面板，格子及文字随大小调整，全部118元素无需横向/纵向滚动；很小的窗口中可悬停查看元素信息。

目前包含 118 项质量、62 项显示半径、109 套颜色，以及既有磁矩／U／J 默认值。空白表示未知或未设置，不代表零；可补填或清空单元格。RGB 接受 0–255 整数，保存为内部 0–1，未编辑的通道保留原始精度。质量须为正，半径非负，所有填写数值须有限；磁矩允许负数。radii 是可视化显示半径，并非所有元素都有统一意义的“原子半径”。

程序默认元素资料现为 `data/resources/elements.json`，磁矩／U／J 仍在 `data/incar/presets.json`。原 `data/atomtypes.xml` 保留为历史初始表和数字占位记录来源，其已有 36 个真实元素的质量、半径、共价半径和颜色在补全时原值迁入新资料；属性编辑基于新JSON与个人覆盖，不修改旧XML。共价半径保留在资料中，不是弹窗中的显示半径。

## 数据来源与缺失值

补充数据来自 ASE 3.29.0 发布包：质量用 `atomic_masses_iupac2016`；新显示半径用 `vdw_radii`（范德华半径）；新增颜色用 `jmol_colors`（Jmol 配色）；补充共价半径用 `covalent_radii`。已有 36 元素的设置优先保留。质量包含对没有稳定同位素的元素所选同位素质量，不应一概当作天然丰度标准原子量。ASE 的缺失／占位半径被转换为 null，没有作为实测数值填入。

来源说明：[ASE 数据文档](https://ase-lib.org/ase/data.html)、[ASE 官方源码](https://gitlab.com/ase/ase)。归档文件名与 SHA-256 在 JSON 的 source 字段中，[ASE 许可](ASE-LICENSE.txt)随数据保留。维护者可用 `python3 tools/import_element_reference.py /path/to/ase-3.29.0-py3-none-any.whl` 重建补充表；这是按旧 XML 重建默认数据，会覆盖 JSON 个性修改，不应作为普通更新步骤。运行 p4vasp 不需要安装 ASE。

GTK 原生结构显示和图片导出均读取新资料。为让未知资料的元素仍可绘制，运行时对空半径使用 1 Å 的显示回退、空 RGB 通道使用白色分量；空质量为未知，不能据此求质量中心；空共价半径不用于自动判键。这些只是运行时回退，不保存为表格中的科学资料。已有 `~/.p4vasp/atomtypes.xml` 或当前目录元素表依旧可覆盖 GUI 默认值；独立图片导出的原有路径不读取这些个人 XML 覆盖。

## 保存与恢复

元素属性Save保存到`~/.p4vasp/resources/periodic.json`及`incar.json`的个人字段覆盖，不修改程序自带的默认JSON；未修改字段继续跟随新版默认值，`git pull`不会覆盖个人修改。保存前备份到`~/.p4vasp/backups/`。外部源文件变化会拒绝保存；第二个文件写入失败时尝试回滚第一个，回滚失败会报告恢复路径，多文件写入不是断电安全事务。显式指定ResourceStore根目录的独立维护工具/测试仍可直接编辑其根目录文件。

弹窗Save前仅为本次编辑，Cancel或关闭即丢弃；Reload重新读取已保存设置。元素及INCAR缓存需重启后应用，不自动重写当前结构或已生成输入。恢复个人设置前保留现有覆盖文件与备份，再恢复到对应用户覆盖路径并重启。

本地气相 XYZ 库位于 `data/models/gas_phase/`，格式与操作见 [分子库说明](../models/gas_phase/README.md)。

第 17 个入口为 [NIST-JANAF](https://janaf.nist.gov/)，提供 NIST-JANAF 热化学表（SRD 13）。

第 18 个入口为 [The Cambridge Cluster Database](http://www-wales.ch.cam.ac.uk/CCD.html)（剑桥团簇数据库），官网现标题为 Cambridge Energy Landscape Database，提供团簇全局优化与结构数据。

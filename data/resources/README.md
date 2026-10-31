# 数据库导航与内部资料

从工具栏 **Database** 或菜单 **Database → Resources** 打开。

- **Online databases**：首版 16 张卡片，四列四行。点击通过系统默认浏览器打开网站，悬停显示用途和网址。名称缩写作为离线图标，不冒充网站官方标志。程序不在启动时联网获取图标或数据。
- **p4vasp data**：点击内部资料卡片，在文本编辑窗口查找、修改、保存。元素、质量、半径与颜色共用 `data/atomtypes.xml`；INCAR 模板与磁性／U／J 默认值共用 `data/incar/presets.json`。卡片只是同一真实文件的不同查找入口。网站卡片编辑本目录的 `websites.json`。

编辑器显示实际路径，Save 校验 XML／JSON 结构、数值和网址；保存前备份到 `~/.p4vasp/backups/`，再替换程序自带文件。权限不足或外部文件已改变时显示错误并保留未保存文本；外部变动需 Reload 后重新核对。Reload 和关闭会询问是否放弃未保存内容。网站目录保存后立即刷新，元素表及 INCAR 缓存需重启程序。恢复时从备份复制回编辑器所示路径，再重启。

这里编辑的是当前安装版本的实际文件，不是用户覆盖文件。更新、重新安装可能覆盖这些修改，请另存备份并核对后迁移；只读安装目录需要有写入权限，不自动提权。元素表目前包含 48 条记录（含占位记录），并非完整的 118 元素周期表。已有 `~/.p4vasp/atomtypes.xml` 或工作目录元素表仍可能按原有逻辑覆盖程序默认值。修改这些默认资料不会自动改写已经加载的结构或已生成的计算输入，科学参数应自行核对。

16 个入口由用户确认：Open Catalyst Project、ioChem-BD、Materials Project、CRC Handbook、NIST WebBook、NOMAD、ChemSpider、Catalysis-Hub、OQMD、AFLOW、Materials Cloud、NIST JARVIS、PubChem、COD、ICSD、CCDC Access Structures。网址以 `websites.json` 为准。部分服务需要注册、订阅或许可证；导航卡片不提供这些权限。CCDC 基础结构获取与高级检索的权限可能不同。

原 SQL Query 代码保留为 `LegacyDBApplet`，原 Commit 入口未改；本导航不依赖配置 SQL 数据库。

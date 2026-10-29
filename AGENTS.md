# p4vasp project guidance

- Read `memory.md` for the update history, code locations, known unresolved issues, and previous verification results before investigating fixes. Keep it current when maintenance work changes this context.

- Open this checkout at `~/opt/p4vasp` and read `doc/GTK3-migration.md` for the current GUI architecture. Use paths relative to the checkout; some older update notes contain a path from another computer.
- The Python GUI uses PyGObject with GTK3 through `p4vasp.gtk3`. The existing `data/glade2/*.glade` resources remain layout sources loaded through the GTK3 adapter. Native FLTK/OpenGL windows and the separate GLUT k-point viewer have different backends.
- For a UI change, trace the Glade resource, adapter, applet, and toolbar/menu entry involved. Check the displayed widget and its initial state, not just that resource XML parses. Keep neighboring controls usable when changing layout.
- `deprecated/` holds reference copies of removed UI code; read its README before restoring or changing that material. Keep the historical New menu/applet distinct from the removed left-toolbar New shortcut.
- Run focused checks for changed files, then the relevant commands documented in `doc/GTK3-migration.md` when dependencies and a display are available. Report any GUI checks that could not run; a passing syntax check alone does not establish the visual behavior.

For GTK interface changes or regressions, use the `p4vasp-gtk-ui` skill.

## 文档分工与按需接手

- `AGENTS.md` 管项目规则；`memory.md` 管当前状态、代码位置和证据索引；`update_history/` 保留历史；安装与操作指南说明用法；skill 保存可复用方法。不要另建职责重复的 agent.md、状态记忆或状态 skill。
- 启动或恢复上下文时，先读适用规则及 memory 的相关摘要，再查目标涉及的源码和文档。同会话已读且未变化的内容直接复用；缺失入口应报告并定位替代来源，不编造状态。
- 用户仅说“开工”时，按 memory 和 Git 状态定位最近的未完成任务，做有限只读检查，简短报告任务、已确认状态、待办和下一步。IDE 打开的其他项目文件不自动成为目标；候选不明确时先做共同检查，再询问。已有明确开发指令时直接执行其授权范围。

## 证据、跨设备与交付

- 区分用户报告、助手源码/只读检查、静态/合成测试和实际 GUI 操作。记录日期、相关文件、结果证据、限制及未完成项；用户执行的检查明确注明来源。建议命令标为待执行，历史通过不写成本次通过。
- 设备环境分别核验：Linux 上通过不代表 macOS 或另一台电脑通过。按任务需要检查当前路径、解释器、GTK/Cairo、原生扩展和显示环境；设备记录注明必要的设备/平台、日期及实际检查范围，未知项写未核验。记录中不包含凭据。
- 通用命令和新导航尽量使用仓库相对路径；已有历史证据中的路径不批量改写。共享代码/记忆不证明另一设备已安装依赖或重编译原生扩展。
- 交付时按实际变更同步 memory、更新记录和相关安装/操作指南；入口改变时同步其使用说明，规则改变时更新本文件。只记录新增或改变的状态，避免复制长背景；任务中断也留下已完成与待完成边界。无状态变化的普通问答不必机械追加记录。
- 文档变更核对来源、链接与差异，并注明检查范围；不机械重跑应用测试。实现变更仍需完成相关验证。
- 换机或中断前，在 `memory.md` 的简短接手检查点更新：当前任务、已完成产物、证据日期/范围、未验证或受阻项、下一步及其授权边界。检查点引用详细记录，不复制整段历史；已有明确任务时继续执行，不把检查点当成自动执行旧待办的授权。
- 迁移和交付按完整依赖核对：Python/helper、资源/预设、原生源码与目标机重编译要求、重放所需结构与视角文件。文件存在不等于可读、可导入或运行成功；同步来的虚拟环境和原生二进制不视为目标机可用环境。
- 展示产物与科学输入分开说明：图片、隐藏原子、相机居中及重放快照不能替代完整计算输入；检查相关实现并明确未保存的参数，不从渲染成功推断结构或科学结果正确。

## 节省 token 与工具调用

- 在保证任务完成和验证充分的前提下，减少不必要的工具调用。优先复用当前会话信息和 memory，聚焦检索任务相关文件，合并独立检查并限制输出长度；避免重复读取、无目标全目录扫描、高频轮询和无新变化时反复测试。
- 对耗时、输出量大或需要用户实际桌面操作的步骤，可提供简短、可复制的命令，请用户执行并反馈关键结果，再据此继续分析。能直接高效完成的常规操作仍由助手执行，避免增加用户负担。
- 节省用量不能省略必要验证，不能把未执行的检查记为通过；区分用户反馈与助手独立核验。不因等待可选反馈而停止其他可独立完成的工作。

## Update notes and GitHub publishing

- After creating or updating an `update_history/update_*.md` note for completed work, run the relevant checks, commit the note together with its related implementation/test changes, and automatically push to `origin` on branch `p4vasp-py3` (`https://github.com/bigbrosci/p4vasp.git`). This is the user's requested publishing workflow; do not ask for routine confirmation, but respect required tool approval controls and destination-specific approval requirements.
- Stage only files related to the completed update. Preserve unrelated working-tree changes. Use a normal push; do not force-push or overwrite remote work.
- If the remote or branch differs from the destination above, or a push is blocked, explain the issue rather than silently publishing elsewhere or claiming success.
- Report the commit and whether the GitHub push succeeded.

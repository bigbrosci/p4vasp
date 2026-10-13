# p4vasp project guidance

- Read `memory.md` for the update history, code locations, known unresolved issues, and previous verification results before investigating fixes. Keep it current when maintenance work changes this context.

- Open this checkout at `~/opt/p4vasp` and read `doc/GTK3-migration.md` for the current GUI architecture. Use paths relative to the checkout; some older update notes contain a path from another computer.
- The Python GUI uses PyGObject with GTK3 through `p4vasp.gtk3`. The existing `data/glade2/*.glade` resources remain layout sources loaded through the GTK3 adapter. Native FLTK/OpenGL windows and the separate GLUT k-point viewer have different backends.
- For a UI change, trace the Glade resource, adapter, applet, and toolbar/menu entry involved. Check the displayed widget and its initial state, not just that resource XML parses. Keep neighboring controls usable when changing layout.
- `deprecated/` holds reference copies of removed UI code; read its README before restoring or changing that material. Keep the historical New menu/applet distinct from the removed left-toolbar New shortcut.
- Run focused checks for changed files, then the relevant commands documented in `doc/GTK3-migration.md` when dependencies and a display are available. Report any GUI checks that could not run; a passing syntax check alone does not establish the visual behavior.

For GTK interface changes or regressions, use the `p4vasp-gtk-ui` skill.

## Update notes and GitHub publishing

- After creating or updating an `update_history/update_*.md` note for completed work, run the relevant checks, commit the note together with its related implementation/test changes, and automatically push to `origin` on branch `p4vasp-py3` (`https://github.com/bigbrosci/p4vasp.git`). This is the user's requested publishing workflow; do not ask for routine confirmation, but respect required tool approval controls and destination-specific approval requirements.
- Stage only files related to the completed update. Preserve unrelated working-tree changes. Use a normal push; do not force-push or overwrite remote work.
- If the remote or branch differs from the destination above, or a push is blocked, explain the issue rather than silently publishing elsewhere or claiming success.
- Report the commit and whether the GitHub push succeeded.

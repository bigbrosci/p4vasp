# Deprecated UI code

## 2026-09-24 — Remove the left-panel New button

Removed the **New** button from the vertical toolbar at the user's request
because it was not useful in their workflow.

The `new-button/` folder contains unmodified copies taken before the change:

- `data/glade2/frame.glade`: complete original main-window layout.
- `data/glade2/new.glade`: the UI opened by the New applet.
- `lib/p4vasp/applet/NewApplet.py`: the applet implementation and handlers.
- `toolbar-button.glade.txt`: the exact removed toolbar child block.

Only the toolbar child in the active `data/glade2/frame.glade` was removed.
The applet and its **Edit → New** menu entry remain available. The shared
`Frame.initToolbarAppletButtons` method in `p4v.py` still wires the other
toolbar buttons; it previously opened `p4vasp.applet.NewApplet.NewApplet`
through the removed widget's `astart` identifier.

These backup files are reference copies and are not loaded by the application.
To restore the button, insert the block in `new-button/toolbar-button.glade.txt`
as the first child of the `toolbar` widget, immediately before **Open**, in
`data/glade2/frame.glade`. Prefer this targeted restoration over replacing the
whole layout, which could overwrite later changes.

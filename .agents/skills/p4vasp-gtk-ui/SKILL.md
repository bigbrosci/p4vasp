---
name: p4vasp-gtk-ui
description: Diagnose or change p4vasp GTK3 applet layouts, toolbar controls, and GUI behavior while checking the displayed result.
---

# p4vasp GTK3 UI changes

Read `doc/GTK3-migration.md` and locate the relevant `data/glade2/*.glade` resource, GTK3 adapter, applet, and any toolbar or menu wiring. Old import names may forward to `p4vasp.gtk3`; inspect the active implementation before editing.

- Reproduce the reported UI behavior where a display is available. For missing or collapsed controls, inspect packing, allocation, and initial values as well as the XML structure. A resource can load successfully while a control remains hidden.
- Preserve unrelated actions and state when removing or moving a button. Distinguish a toolbar shortcut from a menu item and applet implementation.
- Validate changed XML and Python, run the focused project tests, then use the GTK3 checks documented in `doc/GTK3-migration.md` if the environment supports them. For visual claims, inspect the actual panel or a representative GUI regression test.
- Keep test scope clear: synthetic applet startup does not verify scientific calculations, and the separate GLUT k-point viewer has its own OpenGL requirements.

Describe the resulting behavior and the exact checks that ran. Do not claim the visual layout is fixed based only on syntax or XML parsing.

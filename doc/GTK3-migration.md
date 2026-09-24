# GTK3 runtime migration

The Python GUI uses PyGObject with GTK 3. The `p4vasp.gtk3` package centralizes
GTK3 widgets, GLib callbacks, GDK helpers, and the resource/table adapters.
Startup and diagnostics no longer request PyGTK 2.

## What changed

- Replaced the GTK1/GTK2 plotting implementations with a shared GTK3 backend in
  `p4vasp.piddle.piddleGTK3`. Cairo image surfaces replace GdkPixmap/GdkGC;
  GTK's `draw` signal paints graphs, and PangoCairo renders text, including
  rotated labels. Plot resizing, keyboard zoom, pointer interaction, and
  background-buffer restoration use GTK3 APIs.
- Applets import the GTK3 runtime explicitly. Old `gtk`, `gobject`, `pango`,
  GTK1 graph, and PIDDLE GTK backend import paths forward to GTK3 for compatibility.
  They contain no GTK2 drawing implementation.
- Fixed table-model insertion/deletion/update propagation, empty models, phonon
  label editing, and selective-dynamics checkbox refreshes.
- Fixed resource loading for frame labels, notebook tabs, slider adjustments,
  menu defaults, numeric properties, progress-bar orientation, and widget sizes.
- Fixed graph event coordinates, repeated canvas initialization, lattice-entry
  callback reentrancy, and outdated file-export and text-buffer calls.
- Added the Cairo bridge dependency to the Ubuntu installer and build checks.

Existing `data/glade2/*.glade` files remain the layout source. The Python resource
loader creates GTK3 widgets directly; libglade and GTK2 are not dependencies.
GTK3-supported deprecated widgets such as GtkTable are still accepted by this
loader. This is a GTK3 runtime migration, not a GTK4 port or a wholesale UI redesign.
Historical generated documentation is not rewritten.

The native FLTK/OpenGL structure windows and GLUT k-point viewer are separate
renderers. This change does not replace their graphics APIs with GTK widgets.

## Dependencies and launch

On Ubuntu/Debian:

```bash
sudo apt-get install python3-gi python3-gi-cairo python3-cairo gir1.2-gtk-3.0
./run-p4vasp.sh
```

The existing macOS bootstrap installs GTK3, PyGObject, and py3cairo. This migration
was exercised on Linux; macOS execution has not been verified in this session.

## Verification

Run from the checkout root with the compiled cp4vasp extension available:

```bash
PYTHONPATH="$PWD/lib:$PWD/src" P4VASP_HOME="$PWD" /usr/bin/python3 test/test.py
PYTHONPATH="$PWD/lib:$PWD/src" P4VASP_HOME="$PWD" /usr/bin/python3 test/testGtk3.py
/usr/bin/python3 test/run_gtk3_smoke.py
```

The GUI checks require a display (a desktop session or `xvfb-run`). They cover all
40 Glade resource files, Cairo/Pango drawing, resize and zoom, model notifications,
and lattice callbacks. The applet smoke runner uses a synthetic structure and an
empty in-memory database; it tests initialization, not scientific result accuracy
or database connectivity. It does not write user calculation files.

The optional `--include-glut` check also opens the separate k-point viewer. In the
current desktop test environment it fails in PyOpenGL with “Attempt to retrieve
context when no valid context”. This is an unresolved GLUT/OpenGL context issue,
not a GTK2 dependency. The default GTK smoke suite excludes this renderer explicitly.

Migration reference: [GTK's GTK2-to-GTK3 migration guide](https://docs.gtk.org/gtk3/migrating-2to3.html).

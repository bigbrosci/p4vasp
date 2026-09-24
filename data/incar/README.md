# INCAR generator

Open **INCAR** beside **Build** in the left toolbar, or choose
**Edit → INCAR generator**.

1. Choose presets in Functional, Correction, Model, System, and Tasks.
   The panel starts with no selections.
2. Add or change values in **Custom parameters**, one `TAG = value` per line.
   The preview updates immediately. Hover over a preset to see its values.
3. Click **Save INCAR…** and choose the destination. Existing files require
   overwrite confirmation. Only the INCAR file is written.

**Refresh** clears all preset buttons, standard sections, and custom parameters,
returning to the initial unselected state.

**MAGMOM** is a separate task from ISPIN. It reads the active system's initial
structure (the opened POSCAR / Build structure) and generates zero moments in
POSCAR species order. For example:

```text
# Cu (64), C (1), H (2), O (3)
MAGMOM = 64*0  1*0  2*0  3*0
```

Without an open structure it writes `MAGMOM =` with a blank value. Enter a
`MAGMOM = ...` line in Custom parameters to set moments manually. The species
comment is retained. Repeated species blocks remain in POSCAR order.

DFT+U still uses the active structure for LDAUL/LDAUU/LDAUJ with the Q-robot
U/J defaults. Without element names, supply those tags in Custom parameters.

`presets.json` contains the user's Q-robot category presets, standard sections,
and element defaults, adapted from `incar_gui/task_config.json`, `brain/incar.py`,
and `brain/data.py`. These values are preserved as starting points, including
the original U/J values. Edit the JSON to customize defaults; reopen the panel
to load changes. The panel does not require Q-robot, Flask, ASE, or a browser.

Precedence is: standard sections → Functional/Correction/Model/System presets →
Tasks → geometry helpers → Custom parameters. Each tag appears once in the
output. Functional, model, dispersion, and primary calculation choices are
mutually exclusive within their groups. Supplementary tasks such as ISPIN and
Dipole can be combined. Additional inputs such as NEB IMAGES can be entered in
Custom parameters.

Validation covers assignment syntax and geometry information needed by the
helpers. It does not validate the physical suitability or installed VASP support
of the original presets. No VASP calculations are launched.

p4vasp Windows x64 - experimental portable folder

Keep this entire folder together. Double-click p4vasp.exe to start.
Do not move only the EXE: _internal and model-worker contain required libraries/data.
No separate Python, GTK or MSYS2 installation should be needed.
An independent clean-machine acceptance check is still required.

For errors or command-line PNG export, use p4vasp-console.exe.
  p4vasp-console.exe POSCAR -o image.png

Bundled modeling: ASE bulk and RDKit SMILES generation/initial optimization
work through the included model-worker executable. No PATH or Python setup is
required. Keep model-worker with the main application; its private runtime is
separate from GTK. These are initial structures, not DFT-optimized results.

Structure import (new builds): launch p4vasp.exe test.xyz, or use File/Open,
then Show. XYZ/extxyz, CIF, PDB, MOL/SDF, XSF and ASE trajectory are supported.
Cell-free structures receive 10 Angstrom of padding on each Cartesian side;
complete cells and atom order are retained. Supported multi-frame formats use
the last frame. This imports geometry, not complete calculation metadata.

Vibrations (new builds): open a VASP frequency OUTCAR and click Vibrations,
or use that panel's Open button. Modes animate in an embedded GTK preview;
imaginary modes support dimensionless Scale -1..1 and new POSCAR export.
ASE harmonic/ideal-gas corrections require explicit mode/parameter review.

Optional synthetic diagnostics (use new/empty output folders):
  p4vasp-console.exe --check-runtime C:\path\to\new-output
  p4vasp-console.exe --check-gui C:\path\to\new-gui-output
  p4vasp-console.exe --check-models C:\path\to\new-model-output
These open test windows, write synthetic outputs/reports and exit the process.
They do not establish full normal shutdown or scientific result correctness.

Windows image replay companions use PowerShell .ps1 scripts. The copied command
is PowerShell syntax. Paths refer to the exporting machine; update them if moved.
PowerShell script execution is subject to your device's execution policy.
No security-policy bypass is included. This build is not code-signed.
The separate GLUT k-point viewer and external databases are not validated.

Source and project license:
https://github.com/bigbrosci/p4vasp/tree/p4vasp-py3
See LICENSE and _internal/dependency-licenses for bundled dependency notices.
This development package is not yet an installer or a signed public release.

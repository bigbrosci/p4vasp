p4vasp Windows x64 - experimental portable folder

Keep this entire folder together. Double-click p4vasp.exe to start.
Do not move only the EXE: the _internal folder contains required libraries/data.
No separate Python, GTK or MSYS2 installation should be needed.
An independent clean-machine acceptance check is still required.

For errors or command-line PNG export, use p4vasp-console.exe.
  p4vasp-console.exe POSCAR -o image.png

Optional synthetic diagnostics (use new/empty output folders):
  p4vasp-console.exe --check-runtime C:\path\to\new-output
  p4vasp-console.exe --check-gui C:\path\to\new-gui-output
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

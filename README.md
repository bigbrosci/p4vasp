p4vasp
==========================

Copyright notes:

The original p4vasp software is distributed under the GNU General Public License version 2 (GPLv2).

Original project:

    p4vasp — A graphical user interface for VASP

    Website: http://www.p4vasp.at

Python 3 modernization and maintenance:

    This fork has been updated and maintained for Python 3 compatibility by

    Bigbrosci      (GitHub username)

    Whitehare2023  (GitHub username)

The modifications include:

    - Migration from Python 2 to Python 3

    - Dependency updates

    - Compatibility fixes for modern systems

    - Maintenance and bug fixes

All modifications remain distributed under the GNU General Public License v2 (GPLv2).

Source-code distributions
==========================

Ubuntu Installation
--------------------------

Run:
```
   $ bash ubuntu-start.sh 
```
Mac Installation
--------------------------

Run:
```
   $ bash macos-start.sh 
```

Starting:
--------------------------

Start with the magic `p4v` command:

Add the following alias to your shell configuration file.

macOS (zsh)

-----------

Edit:

    ~/.zshrc

and add:

    alias p4v='xxx/p4vasp/run-p4vasp.sh'

Then reload the shell:

    source ~/.zshrc

Ubuntu / Linux (bash)

---------------------

Edit:

    ~/.bashrc

and add:

    alias p4v='xxx/p4vasp/run-p4vasp.sh'

Then reload the shell:

    source ~/.bashrc


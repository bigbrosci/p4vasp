"""About-dialog credits for the original project and the p4vasp-py3 fork."""
from html import escape

ORIGINAL_NOTICE = 'Copyright (C) 2003, 2004 Orest Dubay <dubay@danubiananotech.com>'
PORT_CREDITS = 'Primary contributors: Bigbrosci and Whitehare2023 (GitHub usernames)'
MAINTENANCE_CREDITS = 'Maintained and further developed by Bigbrosci (GitHub username).'
NEW_NOTICE = 'Copyright (C) 2026 Bigbrosci, for new contributions.'


def about_markup(metadata):
    version = [getattr(metadata, key, None) for key in ('name','version','release','build_date')]
    if all(value is not None for value in version):
        name, number, release, build = map(lambda value: escape(str(value)), version)
        title = '<big><b>%s <i>v%sr%s</i></b></big>\nBuild: %s' % (name, number, release, build)
    else:
        title = '<big><b>P4vasp <span foreground="red"><i>development version</i></span></b></big>'
    return title+'''\nA graphical user interface for VASP

<b>Original project</b>
%s
Website: http://www.p4vasp.at

<b>Python 2 to Python 3 port</b>
%s

<b>p4vasp-py3: ongoing maintenance and new development</b>
%s
%s
Repository: https://github.com/bigbrosci/p4vasp

GNU General Public License (GPL); original notices retained.
<u>ABSOLUTELY NO WARRANTY.</u>
See Help/License agreement for details.

<small>P4vasp home directory: %s</small>''' % (
        escape(ORIGINAL_NOTICE), escape(PORT_CREDITS), escape(MAINTENANCE_CREDITS),
        escape(NEW_NOTICE), escape(str(metadata.p4vasp_home)))

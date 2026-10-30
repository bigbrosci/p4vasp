"""Process-local settings for the mixed GTK/native GUI on WSL."""
import os
import sys


def configure_wsl_cursor(settings, environ=None, platform=None):
    """Give FLTK/Xcursor the GTK preference before its X11 display is opened.

    Do not change desktop resources, user files, or explicit environment choices.
    The WSL compositor may still scale the resulting cursor; this is not a
    replacement for checking the pointer on the user's display.
    """
    environ = os.environ if environ is None else environ
    platform = sys.platform if platform is None else platform
    if not platform.startswith('linux') or not any(environ.get(key) for key in ('WSL_DISTRO_NAME', 'WSL_INTEROP')):
        return
    if settings is None:
        return
    size = settings.get_property('gtk-cursor-theme-size') or 24
    theme = settings.get_property('gtk-cursor-theme-name')
    if size > 0:
        environ.setdefault('XCURSOR_SIZE', str(size))
    if theme:
        environ.setdefault('XCURSOR_THEME', theme)

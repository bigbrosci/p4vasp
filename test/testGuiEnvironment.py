"""Process-local WSL cursor preferences; no display or global settings changes."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'lib'))
from p4vasp.gui_environment import configure_wsl_cursor


class Settings:
    def __init__(self, size=24, theme='Adwaita'):
        self.values = {'gtk-cursor-theme-size': size, 'gtk-cursor-theme-name': theme}

    def get_property(self, name):
        return self.values[name]


class CursorEnvironment(unittest.TestCase):
    def test_wsl_matches_gtk(self):
        env = {'WSL_DISTRO_NAME': 'Ubuntu'}
        configure_wsl_cursor(Settings(), env, 'linux')
        self.assertEqual(env['XCURSOR_SIZE'], '24')
        self.assertEqual(env['XCURSOR_THEME'], 'Adwaita')

    def test_explicit_preferences_preserved(self):
        env = {'WSL_INTEROP': 'present', 'XCURSOR_SIZE': '48', 'XCURSOR_THEME': 'custom'}
        before = env.copy()
        configure_wsl_cursor(Settings(), env, 'linux')
        self.assertEqual(env, before)

    def test_other_platforms_unchanged(self):
        for platform, env in [('linux', {}), ('win32', {'WSL_DISTRO_NAME': 'x'}), ('darwin', {})]:
            before = env.copy()
            configure_wsl_cursor(Settings(), env, platform)
            self.assertEqual(env, before)

    def test_gtk_unspecified_size_falls_back(self):
        env = {'WSL_DISTRO_NAME': 'Ubuntu'}
        configure_wsl_cursor(Settings(0, None), env, 'linux')
        self.assertEqual(env['XCURSOR_SIZE'], '24')
        self.assertNotIn('XCURSOR_THEME', env)


if __name__ == '__main__':
    unittest.main()

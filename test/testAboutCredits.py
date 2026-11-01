"""Authorship roles, retained original notice and escaped About metadata."""
from types import SimpleNamespace
import unittest
import xml.etree.ElementTree as ET
from p4vasp.about import about_markup, ORIGINAL_NOTICE

class Credits(unittest.TestCase):
    def test_development_roles_and_original_notice(self):
        markup=about_markup(SimpleNamespace(p4vasp_home='/tmp/p4vasp'))
        text=''.join(ET.fromstring('<root>'+markup+'</root>').itertext())
        self.assertIn(ORIGINAL_NOTICE,text)
        self.assertIn('Primary contributors: Bigbrosci and Whitehare2023',text)
        self.assertIn('Maintained and further developed by Bigbrosci',text)
        self.assertIn('Copyright (C) 2026 Bigbrosci, for new contributions.',text)
        self.assertIn('development version',text)

    def test_version_and_path_markup_escape(self):
        markup=about_markup(SimpleNamespace(name='Fork <A&B>',version='3',release='1',build_date='2026-11-01',p4vasp_home='/tmp/A&B/<fork>'))
        text=''.join(ET.fromstring('<root>'+markup+'</root>').itertext())
        self.assertIn('Fork <A&B> v3r1',text)
        self.assertIn('/tmp/A&B/<fork>',text)
        self.assertNotIn('development version',text)

if __name__=='__main__':unittest.main()

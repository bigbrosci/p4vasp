"""Prompt size/content boundaries and source snapshots; no API dependency."""
from io import StringIO
from types import SimpleNamespace
import unittest
from p4vasp.Structure import Structure
from p4vasp.chat_context import format_context, capture_structure

POSCAR = '''water
2
5 0 0
0 6 0
0 0 7
O H
1 2
Selective dynamics
Direct
0.123456789 0.2 0.3 F F F
0.4 0.5 0.6 T T T
0.7 0.8 0.9 T F T
'''


def structure():
    s = Structure(); s.read(StringIO(POSCAR)); return s


class ChatContextTest(unittest.TestCase):
    def test_summary_is_compact_and_does_not_mutate_scale(self):
        s = structure(); before = s.toString()
        text = format_context(s)
        self.assertIn('Atoms: 3', text)
        self.assertIn('O: 1, H: 2', text)
        self.assertIn('10 0 0', text)
        self.assertIn('0 12 0', text)
        self.assertNotIn('0.123456789', text)
        self.assertNotIn('```', text)
        self.assertEqual(s.toString(), before)

    def test_full_poscar_keeps_coordinates_and_flags(self):
        s = structure(); before = s.toString()
        text = format_context(s, include_poscar=True, incar='ISPIN = 2')
        block = text.split('```text\n')[1].split('```')[0]
        restored = Structure(); restored.read(StringIO(block))
        self.assertEqual(restored.toString(), before)
        self.assertIn('ISPIN = 2', text)
        self.assertEqual(s.toString(), before)

    def test_current_frame_is_source_not_rendered_copy(self):
        initial = structure(); frame = structure(); frame[0][0] = .9
        system = SimpleNamespace(INITIAL_STRUCTURE=initial)
        viewer = SimpleNamespace(system=system, swin=object(), index=1,
                                 getSequence=lambda: [initial, frame])
        snapshot, source = capture_structure(system, viewer)
        self.assertEqual(snapshot[0][0], .9)
        self.assertIn('frame 2', source)
        frame[0][0] = .8
        self.assertEqual(snapshot[0][0], .9)
        snapshot, source = capture_structure(system, SimpleNamespace(system=object(), swin=object()))
        self.assertEqual(snapshot.toString(), initial.toString())
        self.assertIn('initial', source)

    def test_no_structure_and_summary_size_independent_of_coordinates(self):
        self.assertIn('No structure loaded.', format_context())
        self.assertEqual(capture_structure(None), (None, 'No active system'))
        s = structure()
        short = format_context(s)
        for row in s.positions:
            row[0] = .987654321012345
        self.assertEqual(format_context(s), short)


if __name__ == '__main__':
    unittest.main()

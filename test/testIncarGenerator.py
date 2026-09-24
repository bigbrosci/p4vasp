import copy
from io import StringIO
import unittest

from p4vasp.Structure import Structure
from p4vasp.incar_generator import (
    generate_incar, load_presets, parse_custom, species_from_structure,
)


class TestIncarGenerator(unittest.TestCase):
    def setUp(self):
        self.config = load_presets()

    def test_precedence_and_unique_tags(self):
        original = copy.deepcopy(self.config)
        content = generate_incar(self.config, ["Slab", "Opt", "WRITE", "Electronic"],
                                 ["d_elec", "d_ionic"], "ediff = 1e-7; SYSTEM = My geometry")
        params = parse_custom(content)
        self.assertEqual(params["EDIFF"], "1e-7")
        self.assertEqual(params["SYSTEM"], "My geometry")
        self.assertEqual(params["LWAVE"], "T")
        self.assertEqual(params["NSW"], "200")
        keys = [line.split("=", 1)[0].strip() for line in content.splitlines() if "=" in line]
        self.assertEqual(len(keys), len(set(keys)))
        self.assertEqual(self.config, original)

    def test_species_order_and_repeated_blocks(self):
        structure = Structure()
        structure.read(StringIO("""Fe O Fe
1
5 0 0
0 5 0
0 0 5
Fe O Fe
1 2 1
Direct
0 0 0
0.2 0.2 0.2
0.4 0.4 0.4
0.6 0.6 0.6
"""))
        species = species_from_structure(structure)
        self.assertEqual(species, [("Fe", 1), ("O", 2), ("Fe", 1)])
        params = parse_custom(generate_incar(self.config, ["DFT+U", "ISPIN", "MAGMOM"], [], species=species))
        self.assertEqual(params["MAGMOM"], "1*0  2*0  1*0")
        self.assertEqual(params["LDAUL"], "2  -1  2")
        self.assertEqual(params["LDAUU"], "5.0  0  5.0")
        self.assertEqual(params["LDAUJ"], "1.0  0  1.0")

    def test_missing_geometry_requires_helpers_or_manual_values(self):
        for species in ([], [("", 2)]):
            with self.assertRaises(ValueError):
                generate_incar(self.config, ["DFT+U"], [], species=species)
        content = generate_incar(self.config, ["ISPIN", "DFT+U"], [],
                                 "MAGMOM = 2*4\nLDAUL = 2\nLDAUU = 4\nLDAUJ = 0")
        self.assertEqual(parse_custom(content)["MAGMOM"], "2*4")

    def test_magmom_zero_defaults_and_comment(self):
        content = generate_incar(self.config, ["MAGMOM"], [],
                                 species=[("Cu", 64), ("C", 1), ("H", 2), ("O", 3)])
        self.assertIn("# Cu (64), C (1), H (2), O (3)\nMAGMOM = 64*0  1*0  2*0  3*0", content)
        self.assertNotIn("MAGMOM", parse_custom(generate_incar(self.config, ["ISPIN"], [])))
        self.assertEqual(parse_custom(generate_incar(self.config, ["MAGMOM"], []))["MAGMOM"], "")
        content = generate_incar(self.config, ["MAGMOM"], [], "MAGMOM = 2*3", [("Fe", 2)])
        self.assertIn("# Fe (2)\nMAGMOM = 2*3", content)

    def test_custom_parser_and_errors(self):
        self.assertEqual(parse_custom("# comment\nencut = 500 ! eV\nNSW=10; NSW=20"),
                         {"ENCUT": "500", "NSW": "20"})
        for text in ("ENCUT", "ENCUT=", "bad tag = 1"):
            with self.assertRaises(ValueError):
                parse_custom(text)

    def test_title_cannot_inject_tags(self):
        content = generate_incar(self.config, [], [], system_name="title\nNSW=99; ENCUT=1 # test")
        self.assertEqual(list(parse_custom(content)), ["SYSTEM"])


if __name__ == "__main__":
    unittest.main()

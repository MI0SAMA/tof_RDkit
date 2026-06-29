import unittest

from tofsims_formula_network.ion_rules import apply_adduct, apply_h_shift


class IonRulesTests(unittest.TestCase):
    def test_applies_h_shift_without_negative_hydrogen_counts(self):
        self.assertEqual(apply_h_shift({"C": 7, "H": 8}, -1), {"C": 7, "H": 7})
        self.assertEqual(apply_h_shift({"C": 7, "H": 8}, 1), {"C": 7, "H": 9})
        self.assertIsNone(apply_h_shift({"C": 1}, -1))

    def test_applies_additive_and_subtractive_adducts(self):
        self.assertEqual(apply_adduct({"C": 7, "H": 8}, "Na"), {"C": 7, "H": 8, "Na": 1})
        self.assertEqual(apply_adduct({"C": 7, "H": 8}, "-H"), {"C": 7, "H": 7})
        self.assertIsNone(apply_adduct({"C": 7, "H": 8}, "-O"))


if __name__ == "__main__":
    unittest.main()

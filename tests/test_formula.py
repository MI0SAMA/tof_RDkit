import unittest

from tofsims_formula_network.formula import (
    add_formula,
    exact_mass,
    mass_error,
    normalize_formula_string,
    parse_formula,
    subtract_formula,
)


class FormulaTests(unittest.TestCase):
    def test_parses_and_formats_hill_formula(self):
        self.assertEqual(parse_formula("C7H8"), {"C": 7, "H": 8})
        self.assertEqual(normalize_formula_string("H8C7"), "C7H8")
        self.assertEqual(normalize_formula_string("ClNa"), "ClNa")

    def test_adds_and_subtracts_formula_counts(self):
        self.assertEqual(add_formula(parse_formula("C7H8"), parse_formula("H")), {"C": 7, "H": 9})
        self.assertEqual(subtract_formula(parse_formula("C7H8"), parse_formula("H")), {"C": 7, "H": 7})
        self.assertIsNone(subtract_formula(parse_formula("C7H8"), parse_formula("O")))

    def test_calculates_exact_mass_and_error(self):
        self.assertAlmostEqual(exact_mass(parse_formula("H2O")), 18.010564684, places=6)
        da, ppm = mass_error(18.011, 18.010564684)
        self.assertAlmostEqual(da, 0.000435316, places=6)
        self.assertGreater(ppm, 0)


if __name__ == "__main__":
    unittest.main()

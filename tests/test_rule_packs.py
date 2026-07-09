import unittest

from tofsims_formula_network.formula import format_formula, parse_formula
from tofsims_formula_network.rule_packs import (
    generate_carbon_cluster_formulas,
    generate_external_adduct_variants,
    generate_siloxane_fragments,
)
from tofsims_formula_network.utils import default_config


class RulePackTests(unittest.TestCase):
    def test_carbon_cluster_generates_low_mass_hydrocarbon_series(self):
        cfg = default_config()
        row = {"compound_id": "COC"}
        records = generate_carbon_cluster_formulas(row, parse_formula("C9H14"), cfg)
        formulas = {format_formula(record.counts) for record in records}

        self.assertIn("C3H5", formulas)
        self.assertIn("C4H", formulas)
        self.assertIn("C9H7", formulas)

    def test_carbon_cluster_adds_oxygen_only_for_oxygenated_parents(self):
        cfg = default_config()
        row = {"compound_id": "PET"}
        records = generate_carbon_cluster_formulas(row, parse_formula("C10H8O4"), cfg)
        formulas = {format_formula(record.counts) for record in records}

        self.assertIn("C4HO", formulas)
        self.assertIn("C9H9O3", formulas)

    def test_siloxane_pack_is_pdms_specific(self):
        cfg = default_config()
        pdms = generate_siloxane_fragments({"compound_id": "PDMS"}, parse_formula("C4H14O2Si2"), cfg)
        formulas = {format_formula(record.counts) for record in pdms}

        self.assertIn("C3H9Si", formulas)
        self.assertIn("C5H15OSi2", formulas)
        self.assertIn("O2Si", formulas)

    def test_external_adduct_variants_apply_configured_adducts(self):
        cfg = default_config()
        records = generate_external_adduct_variants(
            {"compound_id": "POMC"},
            [parse_formula("H2O")],
            cfg,
        )
        formulas = {format_formula(record.counts) for record in records}

        self.assertIn("H2NaO", formulas)
        self.assertIn("H2KO", formulas)
        self.assertIn("CsH2O", formulas)
        self.assertIn("H3Na2O2", formulas)


if __name__ == "__main__":
    unittest.main()

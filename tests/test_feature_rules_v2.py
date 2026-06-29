import unittest

from tofsims_formula_network.feature_rules_v2 import detect_structure_features, generate_feature_rule_candidates
from tofsims_formula_network.formula import format_formula, parse_formula
from tofsims_formula_network.molecule_io import mol_from_smiles
from tofsims_formula_network.utils import default_config


class FeatureRulesV2Tests(unittest.TestCase):
    def test_fluorocarbon_rules_trigger_from_c_f_bond_not_material_name(self):
        cfg = default_config()
        mol = mol_from_smiles("C(F)(F)(F)C(F)(F)F")
        features = detect_structure_features(mol)
        candidates = generate_feature_rule_candidates(mol, parse_formula("C2F6"), cfg)
        formulas = {(format_formula(item.counts), item.ion_mode, item.rule_pack) for item in candidates}

        self.assertTrue(features["fluorocarbon_motif"])
        self.assertIn(("F", "negative", "fluorocarbon_fragmentation"), formulas)
        self.assertIn(("CF3", "positive", "fluorocarbon_fragmentation"), formulas)

    def test_acetal_and_aromatic_rules_are_feature_triggered(self):
        cfg = default_config()
        acetal = mol_from_smiles("COC")
        aromatic = mol_from_smiles("c1ccccc1O")

        acetal_candidates = generate_feature_rule_candidates(acetal, parse_formula("CH2O"), cfg)
        aromatic_candidates = generate_feature_rule_candidates(aromatic, parse_formula("C6H6O"), cfg)
        acetal_formulas = {format_formula(item.counts) for item in acetal_candidates}
        aromatic_formulas = {format_formula(item.counts) for item in aromatic_candidates}

        self.assertIn("C2H5O2", acetal_formulas)
        self.assertIn("C6H5", aromatic_formulas)
        self.assertIn("C6H5O", aromatic_formulas)


if __name__ == "__main__":
    unittest.main()

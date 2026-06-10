import tempfile
import unittest
from pathlib import Path

import pandas as pd

from tofsims_formula_network.matching import match_rf_with_network
from tofsims_formula_network.network import generate_formula_network, write_network_csv, write_network_json
from tofsims_formula_network.reporting import write_markdown_report
from tofsims_formula_network.utils import default_config


class NetworkMatchingReportingTests(unittest.TestCase):
    def test_smiles_network_contains_parent_h_shift_and_adducts(self):
        cfg = default_config()
        row = {
            "compound_id": "STD001",
            "name": "Toluene",
            "smiles": "Cc1ccccc1",
            "formula": "",
            "group": "small_organic",
            "notes": "",
        }
        records = generate_formula_network(row, cfg)
        formulas = {record.formula for record in records}
        self.assertIn("C7H8", formulas)
        self.assertIn("C7H7", formulas)
        self.assertIn("C7H9", formulas)
        self.assertIn("C7H8Na", formulas)
        self.assertIn("C14H17", formulas)

    def test_rf_formula_intersection_and_report_outputs(self):
        cfg = default_config()
        row = {
            "compound_id": "STD001",
            "name": "Toluene",
            "smiles": "Cc1ccccc1",
            "formula": "",
            "group": "small_organic",
            "notes": "",
        }
        records = generate_formula_network(row, cfg)
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            json_path = tmp_path / "network.json"
            csv_path = tmp_path / "network.csv"
            write_network_json(records, json_path, row)
            write_network_csv(records, csv_path)
            network_df = pd.read_csv(csv_path)
            rf_df = pd.DataFrame(
                [
                    {"spectrum_id": "sample001", "peak_mz": 91.054, "candidate_formula": "H7C7", "rf_rank": 1},
                    {"spectrum_id": "sample001", "peak_mz": 50.0, "candidate_formula": "Xe", "rf_rank": 2},
                ]
            )
            matches = match_rf_with_network(rf_df, network_df, cfg)
            self.assertEqual(len(matches), 1)
            self.assertEqual(matches.iloc[0]["matched_formula"], "C7H7")

            report_path = tmp_path / "sample001_report.md"
            write_markdown_report("sample001", matches, pd.DataFrame(), report_path, cfg)
            text = report_path.read_text(encoding="utf-8")
            self.assertIn("TOF-SIMS Formula Network Matching Report", text)
            self.assertIn("C7H7", text)


if __name__ == "__main__":
    unittest.main()

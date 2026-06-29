import unittest

import pandas as pd

from tofsims_formula_network.evaluation_v2 import centroid_peaks, classify_peak
from tofsims_formula_network.utils import default_config


class EvaluationV2Tests(unittest.TestCase):
    def test_centroid_merges_adjacent_points(self):
        df = pd.DataFrame(
            [
                {"mz": 100.000, "intensity": 10.0},
                {"mz": 100.010, "intensity": 30.0},
                {"mz": 101.000, "intensity": 5.0},
            ]
        )
        out = centroid_peaks(df, da=0.03, ppm=50)

        self.assertEqual(len(out), 2)
        self.assertEqual(int(out.iloc[0]["peak_count"]), 2)
        self.assertAlmostEqual(float(out.iloc[0]["intensity"]), 40.0)

    def test_classifies_contaminants_and_low_mass_features(self):
        cfg = default_config()

        self.assertEqual(classify_peak(22.9898, "positive", cfg), ("contaminant", "Na+", False))
        self.assertEqual(classify_peak(18.9984, "negative", cfg), ("low_mass_feature", "F-", True))
        self.assertEqual(classify_peak(10.0, "negative", cfg), ("low_mass_background", "below_min_main_mz", False))
        self.assertEqual(classify_peak(55.0, "positive", cfg), ("structural_candidate", "", True))


if __name__ == "__main__":
    unittest.main()

import tempfile
import unittest
from pathlib import Path

from tofsims_formula_network.spectrum_io import read_spectrum_txt, standardize_spectrum


class SpectrumIOTests(unittest.TestCase):
    def test_reads_comma_space_and_tab_separated_peak_lists(self):
        with tempfile.TemporaryDirectory() as tmp:
            samples = {
                "comma.txt": "Mass,Intensity\n15.023,1023\n27.018,5021\n",
                "space.txt": "m/z intensity\n15.023 1023\n27.018 5021\n",
                "tab.txt": "# comment\n15.023\t1023\n27.018\t5021\n",
            }
            for name, content in samples.items():
                path = Path(tmp) / name
                path.write_text(content, encoding="utf-8")
                df = read_spectrum_txt(path)
                std = standardize_spectrum(df, "sample", str(path))
                self.assertEqual(list(std.columns), ["spectrum_id", "mz", "intensity", "source_file"])
                self.assertEqual(len(std), 2)
                self.assertEqual(std.iloc[0]["mz"], 15.023)

    def test_binary_like_file_fails_with_clear_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "binary.txt"
            path.write_bytes(b"\x00\x01\x02\x03" * 100)
            with self.assertRaises(ValueError) as ctx:
                read_spectrum_txt(path)
            self.assertIn("No numeric peak columns", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()

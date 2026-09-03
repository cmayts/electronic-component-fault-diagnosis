import tempfile
import unittest
from pathlib import Path

from component_diagnostics.io import analyze_csv, write_reports


class ReportTests(unittest.TestCase):
    def test_example_generates_all_reports(self):
        source = Path(__file__).parents[1] / "examples" / "synthetic_measurements.csv"
        results = analyze_csv(source)
        self.assertEqual(len(results), 8)
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            write_reports(results, output)
            self.assertTrue((output / "diagnostic_results.csv").exists())
            self.assertIn("Electronic Component Diagnostic Report", (output / "diagnostic_report.html").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

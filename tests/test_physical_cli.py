"""CLI integration: v0.6 stays isolated from earlier graph/ETQ workflows."""
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest


class PhysicalCLITests(unittest.TestCase):
    def test_physical_model_and_report_replay(self):
        root = Path(__file__).resolve().parents[1]
        cmd = [sys.executable, "-m", "edgewalk", "--physical-model",
               "kepler-earth-anchored-v1"]
        p = subprocess.run(cmd, cwd=root, capture_output=True, text=True, check=True)
        report = json.loads(p.stdout)
        self.assertEqual(report["exactEvidence"]["permutationCount"], 5040)
        self.assertFalse(report["calibration"]["astronomicalInferenceCalibrated"])
        with TemporaryDirectory() as tmp:
            report_path = Path(tmp)/"report.json"
            report_path.write_text(p.stdout, encoding="utf-8")
            replay = subprocess.run([sys.executable, "-m", "edgewalk",
                                     "--verify-physical-report", str(report_path)],
                                    cwd=root, capture_output=True, text=True)
            self.assertEqual(replay.returncode, 0, replay.stderr)
            self.assertTrue(json.loads(replay.stdout)["verified"])
            report["numericalDiagnostics"]["exactConditionalPermutationTail"] = 0
            report_path.write_text(json.dumps(report), encoding="utf-8")
            rejected = subprocess.run([sys.executable, "-m", "edgewalk",
                                       "--verify-physical-report", str(report_path)],
                                      cwd=root, capture_output=True, text=True)
            self.assertNotEqual(rejected.returncode, 0)
            self.assertFalse(json.loads(rejected.stdout)["verified"])

    def test_unsupported_model_rejected_by_cli(self):
        root = Path(__file__).resolve().parents[1]
        result = subprocess.run([sys.executable, "-m", "edgewalk", "--physical-model",
                                 "speculative-five-dimensional-spacetime"],
                                cwd=root, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unregistered physical model", result.stderr)


if __name__ == "__main__":
    unittest.main()

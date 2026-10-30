"""v0.6 physical adapter tests: NASA-pinned source; no simulated cosmology."""
import copy
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from edgewalk.physical import (
    DATASET_SHA256, load_observations, run_physical_model, verify_physical_report,
)


class PhysicalTests(unittest.TestCase):
    def test_real_source_fixture_and_exact_count(self):
        rows, sha = load_observations()
        self.assertEqual(sha, DATASET_SHA256)
        self.assertEqual(len(rows), 8)
        result = run_physical_model()
        self.assertEqual(result["exactEvidence"]["permutationCount"], 5040)
        self.assertEqual(result["exactEvidence"]["extremeOrTiedCount"], 1)
        self.assertAlmostEqual(result["numericalDiagnostics"]["exactConditionalPermutationTail"], 1/5040)
        self.assertFalse(result["calibration"]["astronomicalInferenceCalibrated"])
        self.assertTrue(result["calibration"]["nullExactlyEnumerated"])
        self.assertTrue(verify_physical_report(result))

    def test_replay_full_report_and_type_tampering(self):
        original = run_physical_model()
        self.assertEqual(original, run_physical_model())
        mutated = copy.deepcopy(original)
        mutated["numericalDiagnostics"]["logMeanSquaredError"] = 0.0
        self.assertFalse(verify_physical_report(mutated))
        mutated = copy.deepcopy(original)
        mutated["exactEvidence"]["permutationCount"] = 5040.0
        self.assertFalse(verify_physical_report(mutated))
        mutated = copy.deepcopy(original)
        mutated["calibration"]["astronomicalInferenceCalibrated"] = True
        self.assertFalse(verify_physical_report(mutated))

    def test_reject_unregistered_models_and_data_tampering(self):
        with self.assertRaisesRegex(ValueError, "unregistered"):
            run_physical_model("five-dimensional-gravity")
        with TemporaryDirectory() as tmp:
            path = Path(tmp)/"data.csv"
            real = Path(__file__).resolve().parents[1]/"edgewalk"/"data"/"nasa_planetary_orbits_2025.csv"
            path.write_bytes(real.read_bytes())
            self.assertEqual(run_physical_model(observations_path=path),run_physical_model())
            path.write_bytes(path.read_bytes().replace(b"365.2",b"365.3"))
            with self.assertRaisesRegex(ValueError, "checksum"):
                run_physical_model(observations_path=path)

    def test_source_provenance_and_claim_boundaries(self):
        result = run_physical_model()
        self.assertEqual(result["exactEvidence"]["sourceLastUpdated"], "2025-03-18")
        self.assertIn("nssdc.gsfc.nasa.gov",result["exactEvidence"]["sourceUrl"])
        self.assertEqual(result["findings"]["physicalDarkSector"], "NOT TESTED")
        self.assertIn("NOT TESTED",result["findings"]["signature3plus2"])
        self.assertNotIn("ETQ/V3",result["receiptDomain"])


if __name__ == "__main__":
    unittest.main()

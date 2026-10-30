"""SPARK v0.7.1 contract tests.

These Python checks test specification boundaries and the report assessor.
They do not compile Ada or discharge GNATprove verification conditions.
"""
from __future__ import annotations
import importlib.util
from pathlib import Path
import json
import unittest

from edgewalk.core import etq_address, inverse_etq_address, parity

ROOT = Path(__file__).resolve().parents[1]
SPARK = ROOT / "proofs" / "spark"


def assessor():
    file = SPARK / "scripts" / "assess_proof.py"
    spec = importlib.util.spec_from_file_location("spark_assessor", file)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.assess_report


class SparkContractTests(unittest.TestCase):
    def test_complete_finite_crt_specification(self):
        for n in range(303):
            data = etq_address(n)
            site, fibre = data["siteIndex"], data["fibreLabel"]
            self.assertEqual(inverse_etq_address(site, fibre), n)
            self.assertEqual(data["tensorIndex"], 3 * site + fibre)
            self.assertEqual(data["phaseExponent"], (3, 2, 3)[fibre])
            # Independent bounded Ada expression, not importing the Ada code.
            offset = (2 * (fibre + 3 - site % 3)) % 3
            self.assertEqual(site + 101 * offset, n)
        for site in range(101):
            for fibre in range(3):
                n = site + 101 * ((2 * (fibre + 3 - site % 3)) % 3)
                self.assertEqual(n % 101, site)
                self.assertEqual(n % 3, fibre)
                self.assertLess(n, 303)

    def test_gf2_parity_reference_extremes(self):
        mask = (1 << 23) - 1
        for a in (0, 1, 3, 5, 127, 1 << 22, mask):
            for b in (0, 1, 3, 5, mask):
                self.assertEqual(parity(a, b), (a & b).bit_count() % 2)
        self.assertEqual(parity(mask, mask), 1)

    def test_adjacency_transition_negative_controls(self):
        vertices = range(45)
        self.assertEqual(len(tuple(vertices)), 45)
        edges = {(0, 23), (23, 0)}
        def permitted(source, candidate):
            return (source != candidate and
                    (source, candidate) in edges and
                    (candidate, source) in edges)
        self.assertTrue(permitted(0, 23))
        self.assertFalse(permitted(0, 24))
        self.assertFalse(permitted(0, 0))
        edges.remove((23, 0))
        self.assertFalse(permitted(0, 23))

    def test_spark_scope_contains_contracts_and_excludes_io_harness(self):
        spec = (SPARK / "src" / "edgewalk_reference.ads").read_text()
        body = (SPARK / "src" / "edgewalk_reference.adb").read_text()
        project = (SPARK / "edgewalk_spark.gpr").read_text()
        self.assertIn("SPARK_Mode => On", spec)
        self.assertIn("SPARK_Mode => On", body)
        for symbol in ("Address_Of", "Sequence_Of", "Tensor_Of",
                       "Phase_Of", "Parity", "Is_Valid_Edge", "Checked_Step"):
            self.assertIn(symbol, spec)
            self.assertIn(symbol, body)
        self.assertIn("Post =>", spec)
        self.assertIn("Depends =>", spec)
        self.assertIn("edgewalk_reference.ads", project)
        self.assertIn("edgewalk_reference.adb", project)
        self.assertNotIn("reference_selftest.adb", project)

    def test_pinned_toolchain_and_no_fabricated_pass(self):
        lock = json.loads((SPARK / "toolchain-lock.json").read_text())
        self.assertEqual(lock["crateVersions"],
                         {"gnat_native": "16.1.0",
                          "gnatprove": "16.1.0", "gprbuild": "26.0.1"})
        self.assertFalse(lock["archiveChecksumsVerified"])
        shell = (SPARK / "scripts" / "verify.sh").read_text()
        self.assertIn("--output-header", shell)
        self.assertIn("--mode=all", shell)
        self.assertIn("--report=all", shell)
        self.assertIn("SPARK_STATUS=REVIEW_REQUIRED", shell)
        self.assertNotIn("SPARK_STATUS=PASS", shell)

    def test_assessor_missing_or_malformed_reports_fail_closed(self):
        assess = assessor()
        for payload in ("", "GNATprove succeeded", "Total   0"):
            report = assess(payload)
            self.assertEqual(report["status"], "UNVERIFIED")
            self.assertTrue(report["obligations"])

    def test_assessor_tracks_unproved_and_justified(self):
        assess = assessor()
        header = ("SPARK Analysis results        Total          Flow   Interval"
                  "                         Provers   Justified   Unproved")
        def row(label, count, justified, unproved):
            # Match column positions of GNATprove's fixed-width summary.
            h = header
            p = h.index("Justified")
            q = h.index("Unproved")
            base = f"{label:<31}{count:<10}."
            return base.ljust(p) + str(justified).ljust(q-p) + str(unproved)
        def report(j, u):
            return "\n".join((
                "GNATprove FSF 16.1.0",
                header,
                row("Run-time Checks", 12, 0, 0),
                row("Functional Contracts", 8, 0, 0),
                row("Total", 20, j, u),
            ))
        clean = assess(report(0, 0))
        self.assertEqual(clean["status"], "REVIEW_REQUIRED")
        self.assertEqual(clean["unprovedChecks"], 0)
        self.assertNotEqual(clean["status"], "PASS")
        rejected = assess(report(0, 3))
        self.assertEqual(rejected["status"], "UNVERIFIED")
        self.assertEqual(rejected["unprovedChecks"], 3)
        justified = assess(report(2, 0))
        self.assertEqual(justified["status"], "UNVERIFIED")
        self.assertEqual(justified["justifiedChecks"], 2)


if __name__ == "__main__":
    unittest.main()

"""v0.7.2 oracle/fixture mechanics; no Ada compiler runs in default tests."""
from __future__ import annotations
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPARK = ROOT / "proofs" / "spark"
BRIDGE = SPARK / "conformance" / "bridge.py"


def module():
    spec = importlib.util.spec_from_file_location("edgewalk_differential_bridge", BRIDGE)
    assert spec and spec.loader
    item = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(item)
    return item


class ProofConformanceBridgeTests(unittest.TestCase):
    def test_golden_fixture_family_sizes_and_repeatability(self):
        v = module()
        cases, expected, counts = v.cases_and_expected()
        self.assertEqual(counts, {
            "address": 303, "inverse": 303, "parity": 1024,
            "edgeGrid": 8100, "walk": 303, "total": 10033,
        })
        self.assertEqual(cases.count(b"\n"), counts["total"])
        self.assertEqual(expected.count(b"\n"), counts["total"])
        self.assertEqual(v.cases_and_expected(), (cases, expected, counts))
        self.assertTrue(cases.startswith(b"A 0\nA 1\n"))
        self.assertIn(b"A 302\n", cases)
        self.assertIn(b"I 100 2\n", cases)
        self.assertIn(b"P 0 8388607\n", cases)
        self.assertIn(b"E 0 0 1 1\n", cases)
        self.assertIn(b"E 0 23 1 1\n", cases)

    def test_audited_ada_source_and_report_unchanged(self):
        v = module()
        self.assertEqual(v.validate_sources(), {
            "edgewalk_reference.ads":
                "4608dc2406f241dd186ee39a38004704068b853d3b44a1401ca1b3bdf2a63bd0",
            "edgewalk_reference.adb":
                "3eb7dd71ad47b9ab08c2a94bea32089f8c306e42f5715daf3e765b20d90c18fe",
        })
        self.assertEqual(
            v.digest((SPARK / "audits" / "2026-10-30-6a8c0c7" /
                      "original" / "gnatprove.out").read_bytes()),
            v.ARCHIVED_REPORT_SHA256)

    def test_python_only_mock_is_not_a_real_ada_run(self):
        v = module()
        cases, expected, counts = v.cases_and_expected()
        # Synthetic mocked Ada output. This is a test of comparison logic,
        # NOT evidence that any Ada executable has run.
        report = v.compare(cases, expected, expected)
        self.assertEqual(report["cases"], counts)
        self.assertEqual(report["status"], "OUTPUT_MATCH_REVIEW_REQUIRED")
        self.assertFalse(report["pythonFormalEquivalence"])
        self.assertEqual(len(report["pythonCoreSha256"]), 64)
        self.assertEqual(len(report["adaDriverSha256"]), 64)
        self.assertEqual(report["leanKernelStatus"], "NOT_ESTABLISHED_BY_THIS_RUN")
        self.assertEqual(report["adaProofEvidence"],
                         "ARCHIVED_48_CHECKS_ZERO_UNPROVED_NOT_RERUN")
        self.assertEqual(report["sha256"]["adaObserved"],
                         report["sha256"]["pythonExpected"])

    def test_mismatch_and_length_negative_controls(self):
        v = module()
        cases, expected, _ = v.cases_and_expected()
        with self.assertRaisesRegex(ValueError, "input fixture changed"):
            v.compare(cases.replace(b"A 0\n", b"A 1\n", 1), expected, expected)
        with self.assertRaisesRegex(ValueError, "Python expected fixture changed"):
            v.compare(cases, expected.replace(b"A 0 0 0", b"A 0 1 0", 1), expected)
        with self.assertRaisesRegex(ValueError, "Ada/Python mismatch"):
            v.compare(cases, expected, expected.replace(b"A 0 0 0", b"A 0 1 0", 1))
        with self.assertRaisesRegex(ValueError, "Ada/Python mismatch"):
            v.compare(cases, expected, expected[:-1])
        with self.assertRaisesRegex(ValueError, "Ada/Python mismatch"):
            v.compare(cases, expected, expected + b"E 0 1 1 1 1 1\n")

    def test_receipt_replay_rejects_rehashed_forgery(self):
        v = module()
        cases, expected, _ = v.cases_and_expected()
        authentic = v.compare(cases, expected, expected)  # deliberately mocked
        self.assertEqual(authentic["receiptDomain"], "EDGEWALK/V072/CONFORMANCE")
        self.assertEqual(v.verify_receipt(cases, expected, expected,
                                          v.canonical(authentic)), authentic)
        tampered = dict(authentic)
        tampered["pythonFormalEquivalence"] = True
        # Even when a malicious writer recomputes the receipt digest,
        # independent regeneration rejects the altered claim.
        tampered.pop("receiptSha256")
        tampered["receiptSha256"] = v.digest(
            b"EDGEWALK/V072/CONFORMANCE\x00" + v.canonical(tampered))
        with self.assertRaisesRegex(ValueError, "receipt bytes or provenance"):
            v.verify_receipt(cases, expected, expected, v.canonical(tampered))
        with self.assertRaisesRegex(ValueError, "receipt bytes or provenance"):
            v.verify_receipt(cases, expected, expected,
                             v.canonical(authentic) + b"\n")

    def test_python_case_input_and_output_are_canonical(self):
        v = module()
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "text"
            for payload in (b"", b"A 0", b"A 0\r\n", b"A \x00\n", b"\xff\n"):
                path.write_bytes(payload)
                with self.assertRaises((ValueError, UnicodeError)):
                    v.validated_read(path)
            path.write_bytes(b"A 0\n")
            self.assertEqual(v.validated_read(path), b"A 0\n")

    def test_cli_generate_does_not_claim_ada_success(self):
        with TemporaryDirectory() as tmp:
            cases = Path(tmp) / "cases.txt"
            expected = Path(tmp) / "expected.txt"
            run = subprocess.run(
                [sys.executable, str(BRIDGE), "generate",
                 "--cases", str(cases), "--expected", str(expected)],
                cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertEqual(json.loads(run.stdout)["status"], "PYTHON_FIXTURES_ONLY")
            self.assertEqual(cases.read_bytes().count(b"\n"), 10033)
            with self.assertRaises(FileExistsError):
                cases.open("xb")

    def test_driver_separate_from_proved_spark_project(self):
        proof = (SPARK / "edgewalk_spark.gpr").read_text()
        project = (SPARK / "conformance.gpr").read_text()
        driver = (SPARK / "conformance" / "conformance_driver.adb").read_text()
        self.assertIn("conformance_driver.adb", project)
        self.assertNotIn("conformance_driver.adb", proof)
        self.assertIn("with Edgewalk_Reference;", driver)
        for symbol in ("Address_Of", "Sequence_Of", "Parity", "Checked_Step"):
            self.assertIn(symbol, driver)
        self.assertIn("while not End_Of_File", driver)
        self.assertNotIn("SPARK_Mode => On", driver)
        self.assertEqual(module().digest((SPARK / "src" / "edgewalk_reference.adb").read_bytes()),
                         module().PROOF_SOURCES["edgewalk_reference.adb"])

    def test_ada_runs_only_in_offline_sandbox(self):
        script = (SPARK / "conformance" / "run.sh").read_text()
        self.assertIn("/usr/bin/bwrap --unshare-all", script)
        self.assertIn("--clearenv", script)
        self.assertIn("--tmpfs /home", script)
        self.assertIn("--tmpfs /root", script)
        self.assertIn("--tmpfs /sandbox-home", script)
        self.assertIn('--ro-bind "$toolchain_dir" "$toolchain_dir"', script)
        self.assertIn("python3 conformance/check_toolchain.py", script)
        self.assertIn("./bin/conformance_driver <", script)
        self.assertIn("--receipt results/receipt.json", script)
        self.assertIn("python3 conformance/bridge.py verify", script)
        self.assertGreater(script.index("gprbuild -P conformance.gpr"),
                           script.index("/usr/bin/bwrap --unshare-all"))
        self.assertNotIn("SPARK_STATUS=PASS", script)
        syntax = subprocess.run(["bash", "-n", str(SPARK / "conformance" / "run.sh")],
                                capture_output=True, text=True)
        self.assertEqual(syntax.returncode, 0, syntax.stderr)


if __name__ == "__main__":
    unittest.main()

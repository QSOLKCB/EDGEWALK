"""SPARK evidence archive tests use SYNTHETIC logs, never original proof files."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


REPO = Path(__file__).resolve().parents[1]
SPARK = REPO / "proofs" / "spark"


def archive_module():
    spec = importlib.util.spec_from_file_location(
        "edgewalk_spark_evidence_archive", SPARK / "audit" / "capture.py")
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def synthetic_evidence(directory: Path):
    """Fixture that exercises archive checks only, NOT a GNATprove execution."""
    audit = archive_module()
    category_rows = "\n".join(
        "{:<28} {:>2}     .        .       .       .".format(name, count)
        for name, count in audit.CHECKS.items()
    )
    units = "\n".join(
        "  Edgewalk_Reference." + name +
        " at edgewalk_reference.ads:30 flow analyzed (0 errors, 0 checks, "
        "0 warnings and 0 pragma Assume statements) and proved (1 checks)"
        for name in ("Address_Of", "Checked_Step", "Is_Valid_Edge", "Parity",
                     "Phase_Of", "Sequence_Of", "Tensor_Of")
    )
    units = (
        "  Edgewalk_Reference at edgewalk_reference.ads:3 flow analyzed "
        "(0 errors, 0 checks, 0 warnings and 0 pragma Assume statements) "
        "and proved (0 checks)\n" + units
    )
    report = (
        "date               : " + audit.REPORT_TIME + "\n"
        "gnatprove version  : FSF 16.1.0\n"
        "command line       : gnatprove -P edgewalk_spark.gpr --mode=all "
        "--level=2 --report=all --output-header --proof-warnings=on -j1\n"
        "SPARK Analysis results        Total        Flow   Provers   "
        "Justified   Unproved\n"
        + category_rows + "\n"
        "Total                            48    16 (33%)      32 (67%)"
        "           .          .\n"
        "Analyzed 1 unit\n"
        "in unit edgewalk_reference, 8 subprograms and packages out of 8 analyzed\n"
        + units + "\n"
    )
    values = {
        "gnatprove.out": report,
        "gnatprove-run.txt": "Phase 3 of 3: flow analysis and proof ...\n"
                            " info: postcondition proved\n",
        "gnatprove-exit.txt": "0\n",
        "ada-selftest.txt": "ADA_REFERENCE_SELFTEST=PASS (runtime tests only)\n",
        "gnat-version.txt": "GNATMAKE 16.1.0\n",
        "gprbuild-version.txt": "GPRBUILD 26.0.0 (2026-04-15)\n",
        "gnatprove-version.txt": "FSF 16.1.0\n",
        "toolchain-executable-sha256.txt": "".join(
            value + "  /home/test/opt/edgewalk-spark-toolchain/bin/" + name + "\n"
            for name, value in audit.TOOL_HASHES.items()
        ),
        "gnatprove-assessment.json": json.dumps({
            "status": "REVIEW_REQUIRED", "totalChecks": 48,
            "justifiedChecks": 0, "unprovedChecks": 0,
        }),
    }
    for name, value in values.items():
        (directory / name).write_bytes(value.encode("utf-8"))


class SparkAuditArchiveTests(unittest.TestCase):
    def test_sources_match_historical_proof_commit(self):
        a = archive_module()
        result = a.historical_sources(SPARK, REPO)
        self.assertEqual(set(result), set(a.SNAPSHOT_FILES))
        for path, sha in a.SOURCE_HASHES.items():
            self.assertEqual(a.digest(result[path]), sha)

    def test_synthetic_archive_capture_and_replay(self):
        a = archive_module()
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            evidence, archive = root / "evidence", root / "audit"
            evidence.mkdir()
            synthetic_evidence(evidence)
            result = a.write_archive(evidence, archive)
            self.assertEqual(result["originalFileCount"], 9)
            checked = a.verify_archive(archive)
            self.assertEqual(checked["status"], "ARCHIVE_REPLAY_VERIFIED")
            self.assertEqual(checked["reportedChecks"], 48)
            self.assertEqual(
                (archive / "original" / "gnatprove.out").read_bytes(),
                (evidence / "gnatprove.out").read_bytes())
            with self.assertRaises(FileExistsError):
                a.write_archive(evidence, archive)

    def test_report_tampering_rejected(self):
        a = archive_module()
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            evidence = root / "evidence"
            evidence.mkdir()
            synthetic_evidence(evidence)
            f = evidence / "gnatprove.out"
            f.write_text(f.read_text().replace("Total                            48",
                                                "Total                            47"))
            with self.assertRaisesRegex(ValueError, "total/flow/prover"):
                a.write_archive(evidence, root / "audit")
            self.assertFalse((root / "audit").exists())

    def test_archive_checksum_and_missing_evidence_fail_closed(self):
        a = archive_module()
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            evidence = root / "evidence"
            evidence.mkdir()
            with self.assertRaisesRegex(ValueError, "missing"):
                a.write_archive(evidence, root / "audit")
            synthetic_evidence(evidence)
            a.write_archive(evidence, root / "audit")
            original = root / "audit" / "original" / "gnatprove-run.txt"
            original.write_bytes(original.read_bytes() + b"tampered")
            with self.assertRaisesRegex(ValueError, "archive"):
                a.verify_archive(root / "audit")

    def test_claims_distinguish_ada_lean_and_vendor_provenance(self):
        text = archive_module().review_text().decode("utf-8")
        self.assertIn("NOT a statement", text)
        self.assertIn("Lean v0.7.0 kernel gate", text)
        self.assertIn("NOT an independent", text)
        self.assertIn("Python", text)
        self.assertIn("48 obligations", text)


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
"""Capture/verify original SPARK proof bytes. This does not rerun GNATprove.

Original local files MUST be copied without alteration. Never synthesize a
report from a printed transcript, or call an archive vendor-authenticated.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

SPARK = Path(__file__).resolve().parents[1]
ROOT = SPARK.parents[1]
PROOF_REVISION = "6a8c0c72dd8f456e75907b213c46828395fc9ca2"
REPORT_TIME = "2026-10-30T13:43:44Z"
SOURCE_HASHES = {
    "src/edgewalk_reference.ads": "4608dc2406f241dd186ee39a38004704068b853d3b44a1401ca1b3bdf2a63bd0",
    "src/edgewalk_reference.adb": "3eb7dd71ad47b9ab08c2a94bea32089f8c306e42f5715daf3e765b20d90c18fe",
}
TOOL_HASHES = {
    "gnatmake": "005cfc99713f3513671c74175547528f961698f7d44e23f33976a53bcb11c52b",
    "gprbuild": "aff9fde5ca766d5497da9dec185cb8b96878206a0d02512aa5685e1e56d0a4d3",
    "gnatprove": "544e6da2eedc24ce87d9200d44f61e8e789726466e81e68bf8935489d7f5323e",
}
ORIGINAL_FILES = (
    "ada-selftest.txt", "gnatprove.out", "gnatprove-run.txt",
    "gnatprove-exit.txt", "gnat-version.txt", "gprbuild-version.txt",
    "gnatprove-version.txt", "toolchain-executable-sha256.txt",
    "gnatprove-assessment.json",
)
SNAPSHOT_FILES = (
    "src/edgewalk_reference.ads", "src/edgewalk_reference.adb",
    "edgewalk_spark.gpr", "reference_tests.gpr",
    "tests/reference_selftest.adb", "toolchain-lock.json",
    "scripts/verify.sh", "scripts/assess_proof.py",
    "scripts/check_toolchain.py",
)
CHECKS = {
    "Data Dependencies": 7,
    "Flow Dependencies": 1,
    "Initialization": 2,
    "Run-time Checks": 23,
    "Assertions": 2,
    "Functional Contracts": 7,
    "Termination": 6,
}
BANNERS = {
    "gnat-version.txt": "GNATMAKE 16.1.0",
    "gprbuild-version.txt": "GPRBUILD 26.0.0",
    "gnatprove-version.txt": "FSF 16.1.0",
}
MAX_FILE_BYTES = 16_000_000


def fail(message: str) -> None:
    raise ValueError("SPARK evidence: " + message)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, ensure_ascii=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8") + b"\n"


def read_file(path: Path) -> bytes:
    if (path.is_symlink() or not path.is_file()
            or path.stat().st_size > MAX_FILE_BYTES):
        fail("missing, symlinked or oversized file: " + str(path))
    return path.read_bytes()


def as_text(data: bytes, filename: str) -> str:
    try:
        return data.decode("utf-8", errors="strict")
    except UnicodeError as exc:
        raise ValueError("SPARK evidence: invalid UTF-8 " + filename) from exc


def unique_pairs(pairs: list[tuple[str, object]]) -> dict:
    value = {}
    for key, item in pairs:
        if key in value:
            fail("duplicate JSON key " + key)
        value[key] = item
    return value


def validate_originals(original: Path) -> dict[str, bytes]:
    payload = {name: read_file(original / name) for name in ORIGINAL_FILES}
    transcript = as_text(payload["gnatprove.out"], "gnatprove.out")
    run = as_text(payload["gnatprove-run.txt"], "gnatprove-run.txt")
    if as_text(payload["gnatprove-exit.txt"], "gnatprove-exit.txt").strip() != "0":
        fail("GNATprove exit code is not zero")
    if as_text(payload["ada-selftest.txt"], "ada-selftest.txt").strip() != (
            "ADA_REFERENCE_SELFTEST=PASS (runtime tests only)"):
        fail("Ada runtime self-test did not pass")

    for name, banner in BANNERS.items():
        first = as_text(payload[name], name).splitlines()
        if not first or not (
                first[0] == banner or first[0].startswith(banner + " ")):
            fail("unexpected executable banner in " + name)
    observed_hashes = {}
    for line in as_text(payload["toolchain-executable-sha256.txt"], "tool hashes").splitlines():
        match = re.fullmatch(r"([0-9a-f]{64})\s+\S*/bin/(gnatmake|gprbuild|gnatprove)", line)
        if match is None or match.group(2) in observed_hashes:
            fail("malformed or duplicate executable checksum entry")
        observed_hashes[match.group(2)] = match.group(1)
    if observed_hashes != TOOL_HASHES:
        fail("toolchain executable SHA-256 differs from observed run")
    # Verify that the digest file still refers to the actual installed bytes
    # when the original executables are available. The archive itself can be
    # replayed offline without redistributing copyrighted tool binaries.
    if ("date               : " + REPORT_TIME) not in transcript:
        fail("GNATprove report timestamp differs")
    if "gnatprove version  : FSF 16.1.0" not in transcript:
        fail("GNATprove report compiler identity differs")
    command = ("command line       : gnatprove -P edgewalk_spark.gpr --mode=all "
               "--level=2 --report=all --output-header --proof-warnings=on -j1")
    if command not in transcript:
        fail("GNATprove report invocation differs")

    for name, count in CHECKS.items():
        lines = [line for line in transcript.splitlines()
                 if re.match(r"^\s*" + re.escape(name) + r"\s+" + str(count)
                             + r"\s+", line)]
        if len(lines) != 1:
            fail("missing or conflicting report category " + name)
    total_pattern = (r"(?m)^\s*Total\s+48\s+16\s+\(33%\)\s+32\s+"
                     r"\(67%\)\s+\.\s+\.\s*$")
    if re.search(total_pattern, transcript) is None:
        fail("GNATprove total/flow/prover/justified/unproved categories differ")
    if ("Analyzed 1 unit" not in transcript
            or "8 subprograms and packages out of 8 analyzed" not in transcript):
        fail("GNATprove unit coverage not established")
    unit_rows = [line for line in transcript.splitlines()
                 if re.match(r"^\s+Edgewalk_Reference(?:\.\w+)? at ", line)]
    if len(unit_rows) != 8:
        fail("GNATprove did not report all eight package/subprogram entries")
    for line in unit_rows:
        if ("0 errors" not in line or "0 warnings" not in line
                or "0 pragma Assume statements" not in line):
            fail("GNATprove unit has errors, warnings or assumptions")
    if "info: postcondition proved" not in run:
        fail("original GNATprove transcript lacks proven postconditions")
    if re.search(r"(?im)^\s*(?:error:|warning:|.*not proved\b)", run):
        fail("GNATprove transcript contains unresolved error or warning")
    assessment = json.loads(as_text(payload["gnatprove-assessment.json"], "assessment"),
                            object_pairs_hook=unique_pairs,
                            parse_constant=lambda _: fail("nonfinite JSON"))
    if not isinstance(assessment, dict) or any((
            assessment.get("status") != "REVIEW_REQUIRED",
            assessment.get("totalChecks") != 48,
            assessment.get("justifiedChecks") != 0,
            assessment.get("unprovedChecks") != 0)):
        fail("GNATprove assessment does not match reported obligations")
    return payload


def historical_sources(spark_root: Path, git_root: Path) -> dict[str, bytes]:
    copied = {}
    # Take *every* reproducibility source from the actual proof commit,
    # not whatever happens to be checked out when the archive is captured.
    for rel in SNAPSHOT_FILES:
        command = ["git", "-C", str(git_root), "show",
                   PROOF_REVISION + ":proofs/spark/" + rel]
        proc = subprocess.run(command, capture_output=True, check=False)
        if proc.returncode != 0:
            fail("historical proof source is unavailable: " + rel)
        raw = proc.stdout
        if rel in SOURCE_HASHES and digest(raw) != SOURCE_HASHES[rel]:
            fail("historical source fingerprint mismatch: " + rel)
        if rel in SOURCE_HASHES and digest(read_file(spark_root / rel)) != digest(raw):
            fail("working Ada source differs from proved Git revision: " + rel)
        copied[rel] = raw
    return copied


def review_text() -> bytes:
    return ("""# EDGEWALK v0.7.1 — Original SPARK proof evidence

**Status:** GNATprove reported all 48 obligations discharged for the
specified SPARK package, with zero justified and zero unproved. Original
prover reports are retained byte-for-byte alongside this review. This is
NOT a statement that the existing Python implementation was formally proved.

- Source revision: """ + PROOF_REVISION + """
- GNATprove report timestamp (UTC): """ + REPORT_TIME + """
- Compiler/prover: GNATMAKE 16.1.0, GPRBUILD 26.0.0 (Alire crate
  gprbuild=26.0.1), GNATprove FSF 16.1.0.
- Ada reference self-test: PASS; GNATprove exit: 0.
- Categories: 7 data dependencies, 1 flow dependency, 2 initialization,
  23 runtime-safety checks, 2 assertions, 7 functional contracts,
  6 termination = 48 total.
- 16 checks by flow analysis; 32 by automated prover.
- Detailed report: 1 analyzed Ada unit, 8 of 8 package/subprogram entries
  analyzed, 0 errors/warnings/pragma Assume statements.
- Source SHA-256 (spec): """ + SOURCE_HASHES["src/edgewalk_reference.ads"] + """
- Source SHA-256 (body): """ + SOURCE_HASHES["src/edgewalk_reference.adb"] + """

## Trust and claim limits

This archive preserves recorded execution evidence and matches it to source
and executable fingerprints. Those executable hashes are NOT an independent
publisher signature or an authenticated binary-release archive. An external
auditor must still establish toolchain provenance independently.

GNATprove discharges the contracts that were ACTUALLY DECLARED in the
Ada source; it does not prove full Golay code distance, the entire graph's
physical significance, equivalence with Python, or any cosmological model.
The separate Lean v0.7.0 kernel gate is NOT covered by this result.

No GNATprove logs were regenerated or rewritten by the capture process.
The SHA256SUMS file binds these unmodified bytes; the Git commit storing the
archive supplies the external content-addressed audit checkpoint.
""").encode("utf-8")


def payload_files(evidence: Path, spark: Path, repo: Path) -> dict[str, bytes]:
    originals = validate_originals(evidence)
    sources = historical_sources(spark, repo)
    result = {"original/" + k: v for k, v in originals.items()}
    result.update({"sources/" + k: v for k, v in sources.items()})
    result["REVIEW.md"] = review_text()
    return result


def write_archive(evidence: Path, output: Path, spark: Path = SPARK,
                  repo: Path = ROOT) -> dict:
    payload = payload_files(evidence, spark, repo)
    metadata = {
        "schema": "edgewalk.spark-audit-archive/v1",
        "proofSourceRevision": PROOF_REVISION,
        "reportedAtUtc": REPORT_TIME,
        "verification": "GNATprove 48 reported; 0 unproved; 0 justified; human review retained",
        "leanKernelVerification": "NOT_INCLUDED",
        "vendorArchiveAuthentication": "NOT_ESTABLISHED",
        "files": {p: {"sha256": digest(b), "byteLength": len(b)}
                  for p, b in sorted(payload.items())},
    }
    payload["manifest.json"] = canonical(metadata)
    payload["SHA256SUMS.txt"] = "".join(
        digest(payload[name]) + "  " + name + "\n"
        for name in sorted(payload)).encode("ascii")
    # Never overwrite anything, even an empty existing directory.
    output.mkdir(parents=False, exist_ok=False)
    for name, raw in sorted(payload.items()):
        destination = output / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("xb") as stream:
            stream.write(raw)
    return {"status": "ARCHIVE_CREATED", "path": str(output),
            "fileCount": len(payload), "originalFileCount": len(ORIGINAL_FILES)}



def verify_archive(output: Path, spark: Path = SPARK, repo: Path = ROOT) -> dict:
    raw_manifest = read_file(output / "manifest.json")
    manifest = json.loads(as_text(raw_manifest, "manifest.json"),
                          object_pairs_hook=unique_pairs,
                          parse_constant=lambda _: fail("nonfinite JSON"))
    if (not isinstance(manifest, dict)
            or manifest.get("schema") != "edgewalk.spark-audit-archive/v1"
            or manifest.get("proofSourceRevision") != PROOF_REVISION
            or manifest.get("reportedAtUtc") != REPORT_TIME):
        fail("invalid archive manifest")
    payload = payload_files(output / "original", output / "sources", repo)
    expected_paths = set(payload) | {"manifest.json", "SHA256SUMS.txt"}
    actual_paths = {str(p.relative_to(output)) for p in output.rglob("*")
                    if p.is_file() or p.is_symlink()}
    if actual_paths != expected_paths:
        fail("archive contains missing or unexpected files")
    if manifest.get("files") != {
            p: {"sha256": digest(b), "byteLength": len(b)}
            for p, b in sorted(payload.items())}:
        fail("archive file hashes/lengths mismatch")
    for path, expected in payload.items():
        actual = read_file(output / path)
        if actual != expected:
            fail("archive payload mismatch: " + path)
    checksum = "".join(
        digest(read_file(output / name)) + "  " + name + "\n"
        for name in sorted((*payload, "manifest.json"))).encode("ascii")
    if read_file(output / "SHA256SUMS.txt") != checksum:
        fail("archive checksum listing mismatch")
    return {"status": "ARCHIVE_REPLAY_VERIFIED",
            "originalFileCount": len(ORIGINAL_FILES),
            "sourceFileCount": len(SNAPSHOT_FILES),
            "reportedChecks": 48, "unproved": 0, "justified": 0}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--capture", type=Path, metavar="NEW_DIRECTORY")
    group.add_argument("--verify", type=Path, metavar="ARCHIVE_DIRECTORY")
    parser.add_argument("--evidence", type=Path, default=SPARK / "evidence")
    args = parser.parse_args()
    try:
        result = (write_archive(args.evidence, args.capture) if args.capture
                  else verify_archive(args.verify))
    except (OSError, ValueError) as exc:
        print("ARCHIVE_STATUS=UNVERIFIED: " + str(exc), file=sys.stderr)
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())

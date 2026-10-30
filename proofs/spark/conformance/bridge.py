#!/usr/bin/env python3
"""Deterministic, bounded Python↔Ada differential conformance. No proof claim.

The Ada executable must be compiled and run separately in the offline bwrap
sandbox. Merely generating Python oracle cases is NOT an Ada conformance run.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

from edgewalk.core import (build_tanner, etq_address, inverse_etq_address,
                           parity, run_walk)

PROOF_SOURCE_REVISION = "6a8c0c72dd8f456e75907b213c46828395fc9ca2"
PROOF_SOURCES = {
    "edgewalk_reference.ads": "4608dc2406f241dd186ee39a38004704068b853d3b44a1401ca1b3bdf2a63bd0",
    "edgewalk_reference.adb": "3eb7dd71ad47b9ab08c2a94bea32089f8c306e42f5715daf3e765b20d90c18fe",
}
# Hash of genuine archived report, not an assertion that GNATprove reruns here.
ARCHIVED_REPORT_SHA256 = "f5c834388ef37b118c7d761f7f0a36947fa413116b24d002acd6f1cf66234fcd"
FAMILY_COUNTS = {"address": 303, "inverse": 303, "edgeGrid": 8100, "walk": 303}
MAX_SIZE = 4_000_000
ROOT = Path(__file__).resolve().parents[1]
WORD_MAX = (1 << 23) - 1


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def exact_bytes(text: str) -> bytes:
    return text.encode("ascii", "strict")


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, ensure_ascii=True,
                       separators=(",", ":"), allow_nan=False) + "\n").encode("ascii")


def vertex_id(label: str) -> int:
    channel, index = label.split(":")
    value = int(index)
    if channel == "q" and 0 <= value < 23:
        return value
    if channel == "x" and 0 <= value < 11:
        return 23 + value
    if channel == "z" and 0 <= value < 11:
        return 34 + value
    raise ValueError("invalid combined Tanner vertex label")


def words() -> tuple[int, ...]:
    # Fixed, declared candidate set; no os randomness, clock or external input.
    result = [0, 1, 2, 3, 5, 7, 127, 255, 0x555555, 0x2AAAAA,
              0x400000, WORD_MAX, WORD_MAX - 1, 0x123456, 0x654321]
    state = 303
    for _ in range(17):
        state = (1_103_515_245 * state + 12_345) % (1 << 23)
        result.append(state)
    values = tuple(dict.fromkeys(result))
    if len(values) != 32 or any(not 0 <= x <= WORD_MAX for x in values):
        raise AssertionError("changed parity fixture family")
    return values


def cases_and_expected() -> tuple[bytes, bytes, dict[str, int]]:
    source: list[str] = []
    expected: list[str] = []
    count = dict(FAMILY_COUNTS)
    for n in range(303):
        value = etq_address(n)
        source.append(f"A {n}")
        expected.append(f"A {n} {value['siteIndex']} {value['fibreLabel']} "
                        f"{value['tensorIndex']} {value['phaseExponent']}")
    for site in range(101):
        for fibre in range(3):
            source.append(f"I {site} {fibre}")
            expected.append(f"I {site} {fibre} {inverse_etq_address(site, fibre)}")
    pool = words()
    count["parity"] = len(pool) ** 2
    for a in pool:
        for b in pool:
            source.append(f"P {a} {b}")
            expected.append(f"P {a} {b} {parity(a, b)}")
    for start in range(45):
        for candidate in range(45):
            for forward, reverse in ((0, 0), (0, 1), (1, 0), (1, 1)):
                accepted = start != candidate and forward == 1 and reverse == 1
                source.append(f"E {start} {candidate} {forward} {reverse}")
                expected.append(f"E {start} {candidate} {forward} {reverse} "
                                f"{int(accepted)} {candidate if accepted else start}")
    adjacency = build_tanner()
    for step in run_walk(adjacency):
        start = vertex_id(step["from"])
        candidate = vertex_id(step["to"])
        if (start == candidate
                or step["to"] not in adjacency[step["from"]]
                or step["from"] not in adjacency[step["to"]]):
            raise AssertionError("Python Tanner walk is not reciprocal")
        source.append(f"E {start} {candidate} 1 1")
        expected.append(f"E {start} {candidate} 1 1 1 {candidate}")
    count["total"] = len(source)
    if len(source) != len(expected) or count["total"] != sum(
            value for key, value in count.items() if key != "total"):
        raise AssertionError("fixture family counts drift")
    return exact_bytes("\n".join(source) + "\n"), exact_bytes(
        "\n".join(expected) + "\n"), count


def validated_read(path: Path) -> bytes:
    if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_SIZE:
        raise ValueError("missing, symlinked or oversized conformance file: " + str(path))
    data = path.read_bytes()
    if not data or not data.endswith(b"\n") or b"\r" in data or b"\x00" in data:
        raise ValueError("noncanonical conformance text: " + str(path))
    data.decode("ascii", "strict")
    return data


def validate_sources() -> dict[str, str]:
    found: dict[str, str] = {}
    for name, expected in PROOF_SOURCES.items():
        actual = digest(validated_read(ROOT / "src" / name))
        if actual != expected:
            raise ValueError("Ada source no longer matches audited proof commit: " + name)
        found[name] = actual
    archive = ROOT / "audit" / "gnatprove.out"
    if digest(validated_read(archive)) != ARCHIVED_REPORT_SHA256:
        raise ValueError("archived GNATprove report fingerprint changed or missing")
    return found


def compare(cases: bytes, expected: bytes, actual: bytes,
            *, source_hashes: dict[str, str] | None = None) -> dict:
    canonical_cases, canonical_expected, counts = cases_and_expected()
    if cases != canonical_cases:
        raise ValueError("input fixture changed from independent Python generation")
    if expected != canonical_expected:
        raise ValueError("Python expected fixture changed from fresh computation")
    if actual != expected:
        left = expected.splitlines()
        right = actual.splitlines()
        index = next((i for i, (a, b) in enumerate(zip(left, right))
                      if a != b), min(len(left), len(right)))
        exp = left[index].decode("ascii", "backslashreplace") if index < len(left) else "<EOF>"
        got = right[index].decode("ascii", "backslashreplace") if index < len(right) else "<EOF>"
        raise ValueError(f"Ada/Python mismatch at record {index + 1}: expected {exp!r}, got {got!r}")
    receipt = {
        "schema": "edgewalk.spark-python-conformance/v1",
        "status": "CONFORMANT_TESTED",
        "cases": counts,
        "sha256": {"cases": digest(cases), "pythonExpected": digest(expected),
                   "adaObserved": digest(actual)},
        "proofSourceRevision": PROOF_SOURCE_REVISION,
        "adaSourceSha256": source_hashes or dict(PROOF_SOURCES),
        "archivedGnatproveReportSha256": ARCHIVED_REPORT_SHA256,
        "adaProofEvidence": "ARCHIVED_48_CHECKS_ZERO_UNPROVED_NOT_RERUN",
        "leanKernelStatus": "NOT_ESTABLISHED_BY_THIS_RUN",
        "pythonFormalEquivalence": False,
        "scope": "bounded address/inverse; 32x32 parity samples; 8100 edge flag controls; 303 Python walk edges",
    }
    receipt["receiptDomain"] = "EDGEWALK/V072/CONFORMANCE"
    receipt["receiptSha256"] = digest(
        b"EDGEWALK/V072/CONFORMANCE\x00" + canonical(receipt))
    return receipt


def verify_receipt(cases: bytes, expected: bytes, actual: bytes,
                   recorded: bytes) -> dict:
    # Reconstruct everything instead of trusting a self-consistent but
    # forged manifest or a caller-provided "success" flag.
    proven = compare(cases, expected, actual,
                     source_hashes=validate_sources())
    if recorded != canonical(proven):
        raise ValueError("conformance receipt bytes or provenance changed")
    return proven


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_subparsers(dest="mode", required=True)
    gen = mode.add_parser("generate")
    gen.add_argument("--cases", required=True, type=Path)
    gen.add_argument("--expected", required=True, type=Path)
    cmp = mode.add_parser("compare")
    cmp.add_argument("--cases", required=True, type=Path)
    cmp.add_argument("--expected", required=True, type=Path)
    cmp.add_argument("--actual", required=True, type=Path)
    cmp.add_argument("--receipt", required=True, type=Path)
    ver = mode.add_parser("verify")
    ver.add_argument("--cases", required=True, type=Path)
    ver.add_argument("--expected", required=True, type=Path)
    ver.add_argument("--actual", required=True, type=Path)
    ver.add_argument("--receipt", required=True, type=Path)
    args = parser.parse_args()
    try:
        src = validate_sources()
        if args.mode == "generate":
            cases, expected, counts = cases_and_expected()
            for path, contents in ((args.cases, cases), (args.expected, expected)):
                with path.open("xb") as target:
                    target.write(contents)
            print(json.dumps({"status": "PYTHON_FIXTURES_ONLY", "cases": counts},
                             sort_keys=True))
        elif args.mode == "compare":
            actual = validated_read(args.actual)
            receipt = compare(validated_read(args.cases),
                              validated_read(args.expected), actual,
                              source_hashes=src)
            with args.receipt.open("xb") as target:
                target.write(canonical(receipt))
            print(json.dumps({"status": receipt["status"],
                              "cases": receipt["cases"]}, sort_keys=True))
        else:
            report = verify_receipt(validated_read(args.cases),
                                    validated_read(args.expected),
                                    validated_read(args.actual),
                                    validated_read(args.receipt))
            print(json.dumps({"status": "REPLAY_VERIFIED",
                              "cases": report["cases"]}, sort_keys=True))
        return 0
    except (ValueError, OSError, UnicodeError) as exc:
        print("SPARK_CONFORMANCE=UNVERIFIED: " + str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

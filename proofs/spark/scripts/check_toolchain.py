#!/usr/bin/env python3
"""Validate actual SPARK tool banners separately from pinned Alire releases.

This runs inside the offline sandbox. It is NOT evidence of GNATprove
verification or authenticated toolchain provenance.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


APPROVED_CRATE_RELEASES = {
    "gnat_native": "16.1.0",
    "gprbuild": "26.0.1",
    "gnatprove": "16.1.0",
}
APPROVED_EXECUTABLE_BANNERS = {
    "gnat_native": "GNATMAKE 16.1.0",
    # Alire gprbuild=26.0.1 reports GPRBUILD 26.0.0 in its --version output.
    "gprbuild": "GPRBUILD 26.0.0",
    "gnatprove": "FSF 16.1.0",
}


def verify_versions(lock: dict, captures: dict[str, str]) -> bool:
    """Fail closed on altered pins, missing files or misleading version text."""
    if not isinstance(lock, dict):
        raise ValueError("invalid toolchain lock")
    if lock.get("crateVersions") != APPROVED_CRATE_RELEASES:
        raise ValueError("Alire crate release pins changed")
    if lock.get("reportedExecutableVersions") != APPROVED_EXECUTABLE_BANNERS:
        raise ValueError("approved executable banner pins changed")
    if set(captures) != set(APPROVED_EXECUTABLE_BANNERS):
        raise ValueError("missing or unexpected toolchain version captures")
    for tool, expected in APPROVED_EXECUTABLE_BANNERS.items():
        output = captures[tool]
        if not isinstance(output, str) or not output:
            raise ValueError("empty version capture: " + tool)
        first_line = output.splitlines()[0]
        # Anchor the full version as a token on the FIRST line; a substring
        # in a warning, another version, or a suffix is not acceptable.
        if first_line != expected and not first_line.startswith(expected + " "):
            raise ValueError("UNVERIFIED: executable banner mismatch: " + tool)
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lock", type=Path, required=True)
    parser.add_argument("--gnat", type=Path, required=True)
    parser.add_argument("--gprbuild", type=Path, required=True)
    parser.add_argument("--gnatprove", type=Path, required=True)
    args = parser.parse_args()
    lock = json.loads(args.lock.read_text(encoding="utf-8"))
    captures = {
        "gnat_native": args.gnat.read_text(encoding="utf-8"),
        "gprbuild": args.gprbuild.read_text(encoding="utf-8"),
        "gnatprove": args.gnatprove.read_text(encoding="utf-8"),
    }
    verify_versions(lock, captures)
    print("SPARK_TOOLCHAIN_BANNERS=MATCH (NOT A PROOF VERDICT)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Fail-closed SOURCE audit, not a Lean compiler or kernel proof."""
from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
LEAN_DIR = ROOT / "Edgewalk"
PIN = "56a005855ea17e0b0958f73ec801ae140b0a1679"
TOOLCHAIN = "leanprover/lean4:v4.35.0"
REQUIRED = {
    "CRT.lean": ("address_injective", "inverse_right", "inverse_left",
                 "address_bijective"),
    "Phase.lean": ("exponent_is_potential_difference", "three_step_closure",
                   "total_phase_after_101_fibre_cycles"),
    "Monomial.lean": ("supportPower_minimal", "iterateStep_eq_power",
                      "monomial_exact_order_303"),
    "GF2.lean": ("self_add_zero", "xor_cancel", "dot_symmetric",
                 "dot_add_left", "dot_duplicate_zero"),
}
# No proof holes, arbitrary axioms, compiler-backed decision bypasses, or
# unsafe/meta proof construction are permitted in this v0.7 proof project.
BLOCKED = re.compile(
    r"\b(?:sorry|admit|axiom|unsafe|native_decide|run_tac|"
    r"declare_syntax_cat|set_option\s+autoImplicit)\b"
)


def audit(root: Path = ROOT) -> list[str]:
    errors = []
    lean_root = root / "Edgewalk"
    toolchain = root / "lean-toolchain"
    config = root / "lakefile.toml"
    if not toolchain.is_file() or toolchain.read_text().strip() != TOOLCHAIN:
        errors.append("Lean toolchain pin differs from v4.35.0")
    if not config.is_file():
        errors.append("missing Lake config")
    else:
        source = config.read_text()
        if PIN not in source or "mathlib4" not in source:
            errors.append("Mathlib commit pin missing or changed")
        if re.search(r'rev\s*=\s*"(?:master|main|latest)"', source):
            errors.append("floating dependency branch forbidden")
    for name, symbols in REQUIRED.items():
        file = lean_root / name
        if not file.is_file():
            errors.append("missing Lean module: " + name)
            continue
        source = file.read_text(encoding="utf-8")
        if BLOCKED.search(source):
            errors.append("forbidden proof hole/axiom in " + name)
        for symbol in symbols:
            if not re.search(r"\btheorem\s+" + re.escape(symbol) + r"\b", source):
                errors.append("missing declared theorem " + name + "/" + symbol)
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    errors = audit(args.root)
    if errors:
        print("SOURCE_AUDIT=FAIL (NOT KERNEL VERIFIED)")
        for message in errors:
            print(" - " + message)
        return 1
    print("SOURCE_AUDIT=PASS (NOT KERNEL VERIFIED)")
    print("Kernel acceptance requires lake build AND lake check --paranoid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

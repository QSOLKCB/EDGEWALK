#!/usr/bin/env python3
"""Fail-closed Lean source audit. A pass is NOT a kernel verification."""
from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys

try:
    import tomllib
except ModuleNotFoundError:
    # Python 3.10 support; the verifier requires an actual TOML parser.
    try:
        import tomli as tomllib
    except ModuleNotFoundError:
        raise SystemExit("Install Python >=3.11 or 'tomli' for proof-source auditing")

ROOT = Path(__file__).resolve().parents[1]
PIN = "56a005855ea17e0b0958f73ec801ae140b0a1679"
TOOLCHAIN = "leanprover/lean4:v4.35.0"
MATHLIB_URL = "https://github.com/leanprover-community/mathlib4"
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
ROOT_IMPORTS = "".join(f"import Edgewalk.{name[:-5]}\n" for name in REQUIRED)
BLOCKED = re.compile(
    r"\b(?:sorry|admit|axiom|unsafe|native_decide|run_tac|"
    r"declare_syntax_cat|set_option\s+autoImplicit)\b"
)


def audit(root: Path = ROOT) -> list[str]:
    errors = []
    lean_root = root / "Edgewalk"
    toolchain = root / "lean-toolchain"
    config = root / "lakefile.toml"
    if not toolchain.is_file() or toolchain.read_text(encoding="utf-8").strip() != TOOLCHAIN:
        errors.append("Lean toolchain pin differs from v4.35.0")
    if not config.is_file():
        errors.append("missing Lake config")
    else:
        try:
            parsed = tomllib.loads(config.read_text(encoding="utf-8"))
        except (tomllib.TOMLDecodeError, UnicodeError):
            errors.append("invalid Lake TOML configuration")
        else:
            requires = parsed.get("require")
            if (not isinstance(requires, list) or len(requires) != 1
                    or requires[0] != {"name": "mathlib", "git": MATHLIB_URL, "rev": PIN}):
                errors.append("effective Mathlib URL/revision/dependency pin changed")
            if (parsed.get("name") != "edgewalk_proofs"
                    or parsed.get("defaultTargets") != ["Edgewalk"]
                    or parsed.get("lean_lib") != [{"name": "Edgewalk"}]):
                errors.append("Lake root/build targets changed")
    root_module = root / "Edgewalk.lean"
    if (not root_module.is_file()
            or root_module.read_text(encoding="utf-8") != ROOT_IMPORTS):
        errors.append("root module must import all four expected proof modules, unchanged")
    expected_files = set(REQUIRED)
    actual_files = {p.relative_to(lean_root).as_posix() for p in lean_root.rglob("*.lean")} if lean_root.is_dir() else set()
    if actual_files != expected_files:
        errors.append("Lean proof module file set differs from approved list")
    for name, symbols in REQUIRED.items():
        file = lean_root / name
        if not file.is_file():
            errors.append("missing Lean module: " + name)
            continue
        source = file.read_text(encoding="utf-8")
        approved_import = ("import Mathlib" if name in ("CRT.lean", "GF2.lean")
                           else "import Edgewalk.CRT" if name == "Phase.lean"
                           else "import Edgewalk.Phase")
        import_lines = [line.strip() for line in source.splitlines()
                        if line.strip().startswith("import ")]
        if import_lines != [approved_import]:
            errors.append("unapproved Lean module imports in " + name)
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
    print("Kernel acceptance requires explicit Lake builds AND lake check --paranoid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

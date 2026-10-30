"""Source gates and finite independent reference checks for Lean v0.7.

IMPORTANT: passing this Python suite never means Lean has kernel-checked a proof.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
import shutil
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
LEAN = ROOT / "proofs" / "lean"


def audit_module():
    path = LEAN / "scripts" / "static_audit.py"
    spec = importlib.util.spec_from_file_location("edgewalk_lean_audit", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class LeanSourceContractTests(unittest.TestCase):
    def test_pins_and_required_theorem_declarations(self):
        self.assertEqual(audit_module().audit(), [])
        self.assertEqual((LEAN / "lean-toolchain").read_text().strip(),
                         "leanprover/lean4:v4.35.0")

    def test_source_gate_rejects_proof_holes_and_changed_pins(self):
        audit = audit_module()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)
            shutil.copytree(LEAN / "Edgewalk", path / "Edgewalk")
            shutil.copy(LEAN / "lakefile.toml", path)
            shutil.copy(LEAN / "lean-toolchain", path)
            module = path / "Edgewalk" / "CRT.lean"
            module.write_text(module.read_text() + "\nexample : True := by sorry\n")
            self.assertTrue(any("forbidden" in error for error in audit.audit(path)))
            module.write_text(module.read_text().replace("by sorry", "by trivial"))
            (path / "lean-toolchain").write_text("leanprover/lean4:v4.36.0\n")
            self.assertTrue(any("toolchain pin" in error for error in audit.audit(path)))

    def test_crt_addresses_are_a_complete_bijection(self):
        pairs = [(n % 101, n % 3) for n in range(303)]
        self.assertEqual(len(set(pairs)), 303)
        for n, (j, a) in enumerate(pairs):
            inverse = j + 101 * (2 * (a + 3 - (j % 3)) % 3)
            self.assertEqual(inverse, n)

    def test_phase_gauge_closure_and_exact_order_reference(self):
        potential = (0, 3, 1)
        phase = (3, 2, 3)
        for a in range(3):
            self.assertEqual((potential[(a+1) % 3] - potential[a]) % 4, phase[a])
            self.assertEqual(sum(phase[(a+i) % 3] for i in range(3)) % 4, 0)
        for start in range(303):
            self.assertEqual(sum(phase[(start+i) % 3] for i in range(303)) % 4, 0)
            self.assertEqual((start+303) % 303, start)
        for k in range(1,303):
            self.assertNotEqual(k % 303, 0)

    def test_gf2_characteristic_two_reference(self):
        for x in range(2):
            self.assertEqual((x+x) % 2, 0)
            for y in range(2):
                self.assertEqual((x+y+x) % 2, y)


if __name__ == "__main__":
    unittest.main()

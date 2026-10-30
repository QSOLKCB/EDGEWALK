"""Regression: Alire package releases may have different executable banners.

All checks are standard-library-only and do NOT execute Ada or GNATprove.
"""
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1] / "proofs" / "spark"
SCRIPT = ROOT / "scripts" / "check_toolchain.py"
LOCK = ROOT / "toolchain-lock.json"

BANNERS = {
    "gnat_native": "GNATMAKE 16.1.0\nCopyright (C) 1995-2025\n",
    "gprbuild": "GPRBUILD 26.0.0 (2026-04-15) (x86_64-pc-linux-gnu)\nCopyright (C) 2004-2026\n",
    "gnatprove": "FSF 16.1.0\nWhy3 for gnatprove version 1.8.2+git\n",
}


def checker():
    spec = importlib.util.spec_from_file_location("edgewalk_spark_tool_versions", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SparkToolchainBannerTests(unittest.TestCase):
    def test_declared_package_versions_and_actual_banners_are_distinct(self):
        lock = json.loads(LOCK.read_text())
        self.assertEqual(lock["crateVersions"], {
            "gnat_native": "16.1.0", "gnatprove": "16.1.0",
            "gprbuild": "26.0.1",
        })
        self.assertEqual(lock["reportedExecutableVersions"], {
            "gnat_native": "GNATMAKE 16.1.0",
            "gnatprove": "FSF 16.1.0",
            "gprbuild": "GPRBUILD 26.0.0",
        })
        self.assertTrue(checker().verify_versions(lock, BANNERS))

    def test_reject_wrong_executable_banners_and_substrings(self):
        verify = checker().verify_versions
        lock = json.loads(LOCK.read_text())
        for tool, invalid in (
            ("gprbuild", "GPRBUILD 26.0.1 (wrong)\n"),
            ("gprbuild", "GPRBUILD 26.0.0-malicious\n"),
            ("gprbuild", "notice GPRBUILD 26.0.0\n"),
            ("gnat_native", "GNATMAKE 14.3.0\n"),
            ("gnatprove", "FSF 15.1.0\n"),
        ):
            with self.subTest(tool=tool, text=invalid), self.assertRaises(ValueError):
                verify(lock, dict(BANNERS, **{tool: invalid}))

    def test_reject_changed_lock_and_missing_capture(self):
        verify = checker().verify_versions
        lock = json.loads(LOCK.read_text())
        changed = json.loads(json.dumps(lock))
        changed["crateVersions"]["gprbuild"] = "26.0.0"
        with self.assertRaises(ValueError):
            verify(changed, BANNERS)
        changed = json.loads(json.dumps(lock))
        changed["reportedExecutableVersions"]["gprbuild"] = "GPRBUILD 18.0w"
        with self.assertRaises(ValueError):
            verify(changed, BANNERS)
        with self.assertRaises(ValueError):
            verify(lock, {"gnat_native": BANNERS["gnat_native"]})

    def test_version_check_executes_inside_the_existing_sandbox(self):
        shell = (ROOT / "scripts" / "verify.sh").read_text()
        self.assertIn("python3 scripts/check_toolchain.py", shell)
        self.assertGreater(shell.index("python3 scripts/check_toolchain.py"),
                           shell.index("/usr/bin/bwrap --unshare-all"))
        self.assertNotIn('if v[name] not in output', shell)
        self.assertNotIn("SPARK_STATUS=PASS", shell)


if __name__ == "__main__":
    unittest.main()

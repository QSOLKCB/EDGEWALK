"""v0.5 evidence tests. Synthetic ETQ bytes/mock source are NEVER real ETQ validation."""
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from edgewalk.evidence import (verify_etq_release, verify_evidence_package,
                               write_evidence_package, BUNDLE_FILES, RECEIVER_FILENAMES)
from edgewalk.etq import ETQBundle


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def _sha(raw):
    return hashlib.sha256(raw).hexdigest()


def _dh(domain, value):
    return _sha(domain.encode() + b"\0" + _canonical(value))


def synthetic_release(root):
    """Exercises secondary byte/receipt checks ONLY; core ETQ loader mocked."""
    root = Path(root)
    domains = {"receipt": "ETQ/V3/RECEIPT/v1", "receiverPrefix": "ETQ/V3/RECEIVER/"}
    contract = {"determinism": {"hashDomains": domains}}
    docs = {"contract.json": _canonical(contract), "contract.schema.json": b"{}",
            "events.json": b"{}", "events.csv": b"testing\n",
            "events.mid": b"MThd", "graph.json": b"{}", "event-atlas.json": b"{}"}
    receivers = []
    for fname in sorted(RECEIVER_FILENAMES):
        rid = "test-" + fname.replace(".", "-")
        raw = docs[fname]
        receivers.append({"receiverId": rid, "filename": fname, "sha256": _sha(raw),
                          "byteLength": len(raw),
                          "semanticSha256": _sha((domains["receiverPrefix"]+rid+"/v1").encode()
                                                 + b"\0" + raw)})
    receipt = {"eventCommitment": {"fileSha256": _sha(docs["events.json"]),
                                   "canonicalEventDocumentSha256": "pinned-event"},
               "contract": {"fileSha256": _sha(docs["contract.json"])},
               "receivers": receivers}
    receipt["receiptCoreSha256"] = _dh(domains["receipt"], receipt)
    docs["observation-receipt.json"] = _canonical(receipt)
    manifest = {"artifacts": [{"filename": name, "sha256": _sha(raw), "byteLength": len(raw)}
                              for name, raw in sorted(docs.items())],
                "receiptCoreSha256": receipt["receiptCoreSha256"], "manifestCoreSha256": "mock-core"}
    docs["manifest.json"] = _canonical(manifest)
    for name, raw in docs.items():
        (root/name).write_bytes(raw)
    return docs


FAKE_BUNDLE = ETQBundle({}, (), {}, "pinned-event", "pinned-edges")


class EvidenceTests(TestCase):
    def test_golay_only_package_replay_and_no_overwrite(self):
        with TemporaryDirectory() as d:
            target = Path(d)/"out"
            created = write_evidence_package(target, ensemble_size=4, swaps=2,
                                             seed=8, bootstrap_draws=32)
            self.assertEqual(created["etqGate"], "not-run")
            verified = verify_evidence_package(target)
            self.assertTrue(verified["verified"])
            self.assertEqual(verified["etqGate"], "not-run")
            self.assertEqual(len(list(target.iterdir())), 6)
            with self.assertRaises(FileExistsError):
                write_evidence_package(target, ensemble_size=4, swaps=2,
                                       seed=8, bootstrap_draws=32)

    def test_report_tampering_fails_even_if_manifest_not_updated(self):
        with TemporaryDirectory() as d:
            target = Path(d)/"out"
            write_evidence_package(target, ensemble_size=4, swaps=2, bootstrap_draws=32)
            file = target/"experiment.json"
            record = json.loads(file.read_text())
            record["exactEvidence"]["systems"]["golay/reference"]["observed"]["fourCycles"] += 1
            file.write_bytes(_canonical(record))
            with self.assertRaisesRegex(ValueError, "tampering"):
                verify_evidence_package(target)

    def test_float_tampering_rejected_even_if_files_rehashed(self):
        with TemporaryDirectory() as d:
            target = Path(d)/"out"
            write_evidence_package(target, ensemble_size=4, swaps=2, bootstrap_draws=32)
            file = target/"experiment.json"
            record = json.loads(file.read_text())
            observed = record["exactEvidence"]["systems"]["golay/reference"]["observed"]
            observed["fourCycles"] = float(observed["fourCycles"])
            raw = _canonical(record)
            file.write_bytes(raw)
            manifest = json.loads((target/"manifest.json").read_text())
            manifest["files"]["experiment.json"] = {"sha256": _sha(raw), "byteLength": len(raw)}
            (target/"manifest.json").write_bytes(_canonical(manifest))
            (target/"SHA256SUMS.txt").write_text("".join(
                _sha((target/name).read_bytes())+"  "+name+"\n"
                for name in sorted((*manifest["files"], "manifest.json"))))
            with self.assertRaisesRegex(ValueError, "replay failed"):
                verify_evidence_package(target)

    def test_etq_gate_requires_real_source(self):
        with TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                write_evidence_package(Path(d)/"out", etq_directory=Path(d),
                                       ensemble_size=4, swaps=2, bootstrap_draws=32)
            self.assertFalse((Path(d)/"out").exists())

    def test_secondary_etq_receipts_with_mocked_source(self):
        with TemporaryDirectory() as d:
            synthetic_release(d)
            with patch("edgewalk.evidence.load_etq_bundle", return_value=FAKE_BUNDLE):
                data = verify_etq_release(d)
            self.assertEqual(data["gate"], "passed")
            self.assertEqual(set(data["artifactSha256"]), BUNDLE_FILES)
            (Path(d)/"events.mid").write_bytes(b"corrupted")
            with patch("edgewalk.evidence.load_etq_bundle", return_value=FAKE_BUNDLE):
                with self.assertRaisesRegex(ValueError, "artifact length or checksum"):
                    verify_etq_release(d)

    def test_core_receipt_tampering_even_after_manifest_rehash(self):
        with TemporaryDirectory() as d:
            synthetic_release(d)
            p = Path(d)/"observation-receipt.json"
            receipt = json.loads(p.read_text())
            receipt["receivers"][0]["mediaType"] = "forged"
            new = _canonical(receipt)
            p.write_bytes(new)
            m = Path(d)/"manifest.json"
            manifest = json.loads(m.read_text())
            for row in manifest["artifacts"]:
                if row["filename"] == "observation-receipt.json":
                    row["sha256"] = _sha(new)
                    row["byteLength"] = len(new)
            m.write_bytes(_canonical(manifest))
            with patch("edgewalk.evidence.load_etq_bundle", return_value=FAKE_BUNDLE):
                with self.assertRaisesRegex(ValueError, "receipt core digest mismatch"):
                    verify_etq_release(d)

    def test_golay_only_forged_provenance_rejected_even_if_rehashed(self):
        with TemporaryDirectory() as d:
            target = Path(d)/"out"
            write_evidence_package(target, ensemble_size=4, swaps=2, bootstrap_draws=32)
            file = target/"validation.json"
            record = json.loads(file.read_text())
            record["forgedEtqAuthenticated"] = True
            raw = _canonical(record)
            file.write_bytes(raw)
            manifest = json.loads((target/"manifest.json").read_text())
            manifest["files"]["validation.json"] = {"sha256": _sha(raw), "byteLength": len(raw)}
            (target/"manifest.json").write_bytes(_canonical(manifest))
            (target/"SHA256SUMS.txt").write_text("".join(
                _sha((target/name).read_bytes())+"  "+name+"\n"
                for name in sorted((*manifest["files"], "manifest.json"))))
            with self.assertRaisesRegex(ValueError, "forged ETQ source"):
                verify_evidence_package(target)

    def test_stable_evidence_bytes_and_honest_claims(self):
        with TemporaryDirectory() as d:
            a, b = Path(d)/"a", Path(d)/"b"
            write_evidence_package(a, ensemble_size=4, swaps=2, bootstrap_draws=32, seed=12)
            write_evidence_package(b, ensemble_size=4, swaps=2, bootstrap_draws=32, seed=12)
            self.assertEqual({p.name:p.read_bytes() for p in a.iterdir()},
                             {p.name:p.read_bytes() for p in b.iterdir()})
            cal = json.loads((a/"calibration.json").read_text())
            self.assertFalse(cal["calibrated"])
            findings = (a/"findings.md").read_text()
            self.assertIn("INCONCLUSIVE", findings)
            self.assertIn("NOT TESTED", findings)

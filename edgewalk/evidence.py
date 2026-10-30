"""v0.5 evidence packages: read-only ETQ validation, exact replay and honest claims.

Never writes to SONIFICATION or treats synthetic fixtures as authenticated ETQ data.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from statistics import mean

from .core import canonical_bytes
from .controls import run_controlled_experiment, replay_experiment_receipt, _summarize
from .etq import _read, _domain_hash, load_etq_bundle

RECEIVER_FILENAMES = frozenset({
    "events.json", "events.csv", "graph.json", "event-atlas.json", "events.mid",
})
BUNDLE_FILES = RECEIVER_FILENAMES | {
    "contract.json", "contract.schema.json", "observation-receipt.json"
}
PACKAGE_FILES = ("experiment.json", "validation.json", "calibration.json", "findings.md")
MAX_ARTIFACT_BYTES = 12_000_000


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _require(condition: bool, reason: str):
    if not condition:
        raise ValueError("EDGEWALK evidence: " + reason)


def _bytes(root: Path, filename: str) -> bytes:
    _require(filename in BUNDLE_FILES or filename == "manifest.json",
             "unrecognised ETQ artifact")
    p = root / filename
    _require(p.is_file() and not p.is_symlink(), "missing/symlinked upstream artifact: " + filename)
    _require(p.stat().st_size <= MAX_ARTIFACT_BYTES, "oversized upstream artifact")
    return p.read_bytes()


def verify_etq_release(directory, *, trusted_manifest_sha256=None):
    """Verify a full release against an EXTERNAL, independently trusted SHA-256 pin.

    Never accept manifest/receipt digests from the submitted bundle as their
    own trust anchor. The caller must obtain the pin independently, from a
    previously authenticated release record. A caller-supplied digest is a
    trust assertion, not proof that its origin was independently verified.
    """
    _require(isinstance(trusted_manifest_sha256, str)
             and len(trusted_manifest_sha256) == 64
             and all(c in "0123456789abcdef" for c in trusted_manifest_sha256),
             "trusted manifest SHA-256 required from independent upstream source")
    root = Path(directory)
    manifest_bytes = _bytes(root, "manifest.json")
    _require(_sha(manifest_bytes) == trusted_manifest_sha256,
             "trusted manifest SHA-256 mismatch")
    bundle = load_etq_bundle(root)
    manifest, _ = _read(root, "manifest.json")
    receipt, receipt_raw = _read(root, "observation-receipt.json")
    contract, contract_raw = _read(root, "contract.json")
    domains = contract["determinism"]["hashDomains"]
    rows = manifest.get("artifacts")
    _require(isinstance(rows, list) and len(rows) == len(BUNDLE_FILES), "manifest artifact count")
    mapped = {}
    for row in rows:
        _require(isinstance(row, dict), "invalid manifest row")
        filename = row.get("filename")
        _require(isinstance(filename, str) and filename in BUNDLE_FILES and filename not in mapped,
                 "unexpected or duplicate manifest filename")
        mapped[filename] = row
    _require(set(mapped) == BUNDLE_FILES, "incomplete ETQ bundle manifest")
    artifact_hashes = {}
    for filename in sorted(BUNDLE_FILES):
        raw = _bytes(root, filename)
        expected = mapped[filename]
        digest = _sha(raw)
        _require(expected.get("sha256") == digest and type(expected.get("byteLength")) is int
                 and expected["byteLength"] == len(raw), "artifact length or checksum: " + filename)
        artifact_hashes[filename] = digest
    _require(manifest.get("receiptCoreSha256") == receipt.get("receiptCoreSha256"),
             "manifest/receipt core mismatch")
    receipt_core = dict(receipt)
    receipt_core.pop("receiptCoreSha256", None)
    _require(_domain_hash(domains["receipt"], receipt_core) == receipt.get("receiptCoreSha256"),
             "receipt core digest mismatch")
    _require(artifact_hashes["observation-receipt.json"] == _sha(receipt_raw), "receipt bytes")
    _require(receipt.get("eventCommitment", {}).get("fileSha256") == artifact_hashes["events.json"],
             "event bytes vs observation receipt")
    _require(receipt.get("eventCommitment", {}).get("canonicalEventDocumentSha256") ==
             bundle.event_document_receipt, "event semantic commitment")
    _require(receipt.get("contract", {}).get("fileSha256") == _sha(contract_raw),
             "contract observation receipt")
    receiver_rows = receipt.get("receivers")
    _require(isinstance(receiver_rows, list) and len(receiver_rows) == len(RECEIVER_FILENAMES),
             "receiver receipt count")
    receiver_names = set()
    for row in receiver_rows:
        _require(isinstance(row, dict), "invalid receiver row")
        filename, receiver_id = row.get("filename"), row.get("receiverId")
        _require(filename in RECEIVER_FILENAMES and filename not in receiver_names,
                 "unexpected/duplicate receiver")
        _require(isinstance(receiver_id, str) and receiver_id and "/" not in receiver_id
                 and "\x00" not in receiver_id, "receiver ID")
        receiver_names.add(filename)
        raw = _bytes(root, filename)
        _require(row.get("sha256") == artifact_hashes[filename] and
                 type(row.get("byteLength")) is int and row["byteLength"] == len(raw),
                 "receiver byte commitment")
        semantic_domain = domains["receiverPrefix"] + receiver_id + "/v1"
        _require(row.get("semanticSha256") == _sha(semantic_domain.encode("utf-8") + b"\0" + raw),
                 "receiver semantic commitment")
    _require(receiver_names == RECEIVER_FILENAMES, "missing receiver")
    return {"gate": "passed", "schema": "edgewalk.etq-validation/v1",
            "modelId": "ETQ-303", "modelVersion": "3.0.0",
            "artifactSha256": artifact_hashes,
            "trustedManifestSha256": trusted_manifest_sha256,
            "eventDocumentSha256": bundle.event_document_receipt,
            "liftedEdgesSha256": bundle.graph_edges_receipt,
            "manifestCoreSha256": manifest["manifestCoreSha256"],
            "receiptCoreSha256": receipt["receiptCoreSha256"]}


def _calibration(record):
    """Exploratory serial diagnostics; mixing and exchangeability unproved."""
    systems = {}
    for name, entry in sorted(record["exactEvidence"]["systems"].items()):
        metrics = {}
        for metric in record["exactEvidence"]["config"]["metrics"]:
            values = [x["metrics"][metric] for x in entry["controls"]]
            n = len(values)
            mid = n // 2
            average = mean(values)
            variance = sum((v-average)**2 for v in values)
            lag_num = sum((values[i]-average)*(values[i+1]-average) for i in range(n-1))
            lag_corr = lag_num / variance if variance else None
            metrics[metric] = {
                "sampleCount": n,
                "firstHalfMean": float(mean(values[:mid])),
                "secondHalfMean": float(mean(values[mid:])),
                "lagOneAutocorrelationDiagnostic": float(lag_corr) if lag_corr is not None else None,
                "constantSeries": variance == 0,
            }
        systems[name] = metrics
    return {"schema": "edgewalk.calibration-gate/v1", "calibrated": False,
            "reason": "Finite-step degree-preserving two-switch chains lack established stationary and exchangeable sampling distribution; diagnostics do not establish calibration",
            "systems": systems, "statisticalClaim": "inconclusive"}


def _findings(record, gate):
    names = ", ".join(sorted(record["exactEvidence"]["systems"]))
    return ("# EDGEWALK v0.5 Evidence Findings\n\n"
            "## Verified exact results\n\n"
            "- Golay/CSS integer graph experiments replay deterministically under declared settings.\n"
            "- Source and control graph fingerprints plus exact integer metrics are committed by EDGEWALK/V4/EXPERIMENT.\n"
            "- Included systems: " + names + ".\n"
            "- ETQ-303 authentic export gate: **" + gate + "**.\n\n"
            "## Statistical interpretation\n\n"
            "- **INCONCLUSIVE:** Controls are finite two-switch chains whose mixing, independence and exchangeability have not been established.\n"
            "- Bootstrap bands and Holm-adjusted ranks from v0.4 remain exploratory; they are not calibrated physical p-values.\n\n"
            "## Physical hypotheses\n\n"
            "- **NOT TESTED:** Dark matter, dark energy, (3,2)-spacetime, or spacetime-based QEC models.\n"
            "- Numerical or graph-structural resemblance is not evidence for those hypotheses.\n\n"
            "## Reproduction\n\n"
            "Use the matching EDGEWALK v0.5 code and run python -m edgewalk --verify-evidence OUTPUT"
            + (" with the same --etq-bundle input." if gate == "passed" else ".")
            + "\n")


def _json(value):
    return canonical_bytes(value)


def write_evidence_package(output, *, etq_directory=None, ensemble_size=4,
                           swaps=4, seed=303, bootstrap_draws=64,
                           variants=("reference", "shear-a", "shear-b"),
                           trusted_etq_manifest_sha256=None):
    """Create a fresh folder exclusively; no overwrites, deletions or source writes."""
    etq = None
    validation = {"schema": "edgewalk.etq-validation/v1", "gate": "not-run",
                  "reason": "No independently authenticated ETQ v3 export supplied"}
    if etq_directory is not None:
        validation = verify_etq_release(
            etq_directory, trusted_manifest_sha256=trusted_etq_manifest_sha256)
        etq = load_etq_bundle(etq_directory)
    else:
        _require(trusted_etq_manifest_sha256 is None,
                 "trusted manifest pin supplied without ETQ source")
    report = run_controlled_experiment(etq, ensemble_size=ensemble_size,
                                       swaps=swaps, seed=seed, bootstrap_draws=bootstrap_draws,
                                       variants=variants)
    # Persist the auxiliary bootstrap configuration outside the v0.4 exact
    # evidence core, preserving its domain-separated SHA-256 identity.
    report["analysisParameters"] = {"bootstrapDraws": bootstrap_draws}
    calibration = _calibration(report)
    payload = {"experiment.json": _json(report), "validation.json": _json(validation),
               "calibration.json": _json(calibration),
               "findings.md": _findings(report, validation["gate"]).encode("utf-8")}
    manifest = {"schema": "edgewalk.evidence-package/v1",
                "exactExperimentSha256": report["sha256"],
                "etqGate": validation["gate"],
                "files": {name: {"sha256": _sha(raw), "byteLength": len(raw)}
                         for name, raw in sorted(payload.items())},
                "claimBoundary": "Evidence packaging and replay, not statistical or physical validation"}
    payload["manifest.json"] = _json(manifest)
    payload["SHA256SUMS.txt"] = ("".join(_sha(payload[name])+"  "+name+"\n"
                                       for name in sorted(payload) if name != "SHA256SUMS.txt")).encode("ascii")
    dest = Path(output)
    dest.mkdir(parents=False, exist_ok=False)
    for filename in sorted(payload):
        with (dest / filename).open("xb") as fp:
            fp.write(payload[filename])
    return {"directory": str(dest), "files": len(payload),
            "exactExperimentSha256": report["sha256"], "etqGate": validation["gate"]}


def _unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def _load(package, filename):
    path = package / filename
    _require(path.is_file() and not path.is_symlink() and path.stat().st_size <= MAX_ARTIFACT_BYTES,
             "missing, symlinked or oversized package file")
    return path.read_bytes()


def verify_evidence_package(directory, *, etq_directory=None, trusted_etq_manifest_sha256=None):
    package = Path(directory)
    manifest = json.loads(_load(package, "manifest.json"), object_pairs_hook=_unique_pairs,
                          parse_constant=lambda x: (_ for _ in ()).throw(ValueError("nonfinite")))
    _require(manifest.get("schema") == "edgewalk.evidence-package/v1", "manifest schema")
    _require(set(manifest.get("files", {})) == set(PACKAGE_FILES), "manifest files")
    for name in PACKAGE_FILES:
        raw = _load(package, name)
        row = manifest["files"][name]
        _require(row.get("sha256") == _sha(raw) and type(row.get("byteLength")) is int
                 and row["byteLength"] == len(raw), "package artifact tampering: " + name)
    sums = "".join(_sha(_load(package, name))+"  "+name+"\n"
                   for name in sorted((*PACKAGE_FILES, "manifest.json")))
    _require(_load(package, "SHA256SUMS.txt") == sums.encode("ascii"), "checksum listing")
    record = json.loads(_load(package, "experiment.json"), object_pairs_hook=_unique_pairs,
                        parse_constant=lambda x: (_ for _ in ()).throw(ValueError("nonfinite")))
    validation = json.loads(_load(package, "validation.json"), object_pairs_hook=_unique_pairs)
    _require(manifest["exactExperimentSha256"] == record["sha256"], "experiment receipt")
    _require(manifest["etqGate"] == validation.get("gate"), "integration gate label")
    if validation["gate"] == "passed":
        _require(etq_directory is not None, "ETQ bundle required to replay ETQ evidence")
        expected = verify_etq_release(
            etq_directory, trusted_manifest_sha256=trusted_etq_manifest_sha256)
        _require(validation == expected, "ETQ source identity differs")
        etq = load_etq_bundle(etq_directory)
    else:
        _require(validation == {
            "schema": "edgewalk.etq-validation/v1",
            "gate": "not-run",
            "reason": "No independently authenticated ETQ v3 export supplied"
        } and etq_directory is None and trusted_etq_manifest_sha256 is None,
                 "unverified or forged ETQ source metadata")
        etq = None
    _require(replay_experiment_receipt(record, etq), "exact experiment replay failed")
    params = record.get("analysisParameters")
    _require(isinstance(params, dict) and set(params) == {"bootstrapDraws"}
             and type(params["bootstrapDraws"]) is int
             and 32 <= params["bootstrapDraws"] <= 4096,
             "missing or invalid exploratory bootstrap settings")
    # Exact v0.4 replay intentionally ignores exploratory analysis; v0.5
    # separately checks the COMPLETE submitted numerical summary by bytes.
    _require(_json(record.get("exploratoryAnalysis")) ==
             _json(_summarize(record["exactEvidence"], params["bootstrapDraws"])),
             "exploratory summary does not match independently replayed controls")
    _require(_load(package, "calibration.json") == _json(_calibration(record)),
             "calibration diagnostics do not match exact controls")
    _require(_load(package, "findings.md") == _findings(record, validation["gate"]).encode("utf-8"),
             "findings are not the declared report")
    return {"verified": True, "etqGate": validation["gate"],
            "exactExperimentSha256": record["sha256"], "files": len(PACKAGE_FILES)+2}

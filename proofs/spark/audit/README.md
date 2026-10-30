# EDGEWALK v0.7.1 — Original Evidence Capture

This directory contains the reviewed run and standard-library evidence capture tool.
The adjacent `../audits/2026-10-30-6a8c0c7/` directory now contains **all 21
original-byte evidence/archive files** extracted from the operator-supplied ZIP.
All 21 uploaded Git blob hashes match the ZIP's original bytes. Do not rewrite
or replace them with reconstructed terminal transcripts.

## Requirements

- Local EDGEWALK Git checkout containing original proof commit
  `6a8c0c72dd8f456e75907b213c46828395fc9ca2`.
- Unmodified local files at `proofs/spark/evidence/` from the reported
  2026-10-30T13:43:44Z proof execution.
- Python 3.10+; no network or additional packages required.
- No need to rerun GNATprove or install any tool to capture existing files.

## Commands for independent recapture in a NEW directory

```bash
cd ~/EDGEWALK
python3 proofs/spark/audit/capture.py \
  --capture /tmp/edgewalk-spark-audit-recapture
python3 proofs/spark/audit/capture.py \
  --verify /tmp/edgewalk-spark-audit-recapture
python3 -m unittest discover -s tests -v
```

The destination **must not exist** before capture. The script checks the
historical Git revision and source SHA-256, the exact recorded tool fingerprints,
the GNATprove report header, per-category totals, per-subprogram coverage,
zero justified/unproved, compiler/prover exit code, runtime self-test, and
the original assessor's `REVIEW_REQUIRED` status. A mismatch stops capture.

The original archive has **already been added to the GitHub audit branch**.
Do not rerun capture into that existing directory, because the script
intentionally rejects overwriting it. The generated files are not gitignored;
no binaries, credential files, caches, or complete toolchain archives were added.

## Included archive source snapshot

The capture script copies the following sources **from the pinned historical
Git revision**, not from any subsequently edited current working files:
Ada specification/body, both GPR projects, Ada runtime test harness,
toolchain declaration and the three verifier/assessor scripts.

The archive's SHA256SUMS.txt lists all archived files including its manifest,
but excludes itself to prevent circular hashing. Manifest JSON binds byte
lengths and digests. Git's commit digest is the external archive checkpoint;
the manifest alone is not a publisher authenticity signature.

## Status boundaries

- **GNATprove run:** reported 48 checks, 0 unproved, 0 justified.
- **Original file upload:** complete — 21 exact-match Git blobs (9 original
  evidence files, 9 source snapshot files, manifest, SHA256SUMS, REVIEW).
- **Toolchain identity:** recorded entry-point fingerprints, not externally
  authenticated original release archives.
- **Lean kernel proofs:** not part of this SPARK audit.
- **Python:** 82 audit-branch tests reported passing; not formally proved equivalent.

The synthetic fixture in `tests/test_spark_audit_archive.py` only tests the
capture/replay code; it is **not** an authentic GNATprove run.

## Audit import verified

The operator-supplied ZIP had SHA-256:

`643c10e8f5d4ec13bfee91451198d3d3c4ca2c17939f120256e1af39cf20265e`

The ZIP passed manifest/SHA256SUMS validation, and all 21 expanded Git blobs
were checked against the original ZIP byte sequences by their Git object SHA-1.
The verified artifact is directly browsable at
[2026-10-30-6a8c0c7](../audits/2026-10-30-6a8c0c7).

To independently replay the committed archive:

```bash
python3 proofs/spark/audit/capture.py \
  --verify proofs/spark/audits/2026-10-30-6a8c0c7
```

Expected output includes `"status":"ARCHIVE_REPLAY_VERIFIED"` and
`"reportedChecks":48`. Toolchain vendor authentication and the separate
Lean kernel proof remain outside the archive's claims.

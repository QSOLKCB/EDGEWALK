# EDGEWALK v0.7.1 — Original Evidence Capture

This directory holds a **review of the user-supplied report** and a safe,
standard-library-only local archival tool. It does **not** currently contain
the original GNATprove evidence files. Do not fill the originals folder with
transcribed text or fabricated output.

## Requirements

- Local EDGEWALK Git checkout containing original proof commit
  `6a8c0c72dd8f456e75907b213c46828395fc9ca2`.
- Unmodified local files at `proofs/spark/evidence/` from the reported
  2026-10-30T13:43:44Z proof execution.
- Python 3.10+; no network or additional packages required.
- No need to rerun GNATprove or install any tool to capture existing files.

## Commands (run in an EDGEWALK checkout)

```bash
cd ~/EDGEWALK
python3 proofs/spark/audit/capture.py \
  --capture proofs/spark/audits/2026-10-30-6a8c0c7
python3 proofs/spark/audit/capture.py \
  --verify proofs/spark/audits/2026-10-30-6a8c0c7
python3 -m unittest discover -s tests -v
```

The destination **must not exist** before capture. The script checks the
historical Git revision and source SHA-256, the exact recorded tool fingerprints,
the GNATprove report header, per-category totals, per-subprogram coverage,
zero justified/unproved, compiler/prover exit code, runtime self-test, and
the original assessor's `REVIEW_REQUIRED` status. A mismatch stops capture.

For GitHub upload, commit the freshly generated
`proofs/spark/audits/2026-10-30-6a8c0c7/` directory onto this audit PR
branch. Keep all files **exactly as captured**. Unlike
`proofs/spark/evidence/`, the reviewed audit folder is not gitignored.
Do not add binaries, credentials, full HOME directories, caches, or tool
archives under this audit PR.

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
- **Original file upload:** not yet performed.
- **Toolchain identity:** recorded entry-point fingerprints, not externally
  authenticated original release archives.
- **Lean kernel proofs:** not part of this SPARK audit.
- **Python:** 75 runtime tests reported passing, not formally proved equivalent.

The synthetic fixture in `tests/test_spark_audit_archive.py` only tests the
capture/replay code; it is **not** an authentic GNATprove run.

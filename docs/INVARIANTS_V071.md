# EDGEWALK v0.7.1 — SPARK Reference Kernel Invariants

1. Preserve all v0.1–v0.7.0 Python/Lean/ETQ canonical computations, receipts
   and original source artifacts. No network, GitHub Actions, upstream writes
   or implicit changes to the Python engine.
2. All verification-relevant Ada code lives in the two source files of
   `edgewalk_spark.gpr` with `SPARK_Mode => On`. A non-SPARK runtime test
   harness must never be reported as proved Ada code.
3. ETQ addressing is bounded to 0..302 sequence indices, 0..100 sites,
   0..2 fibre states, 0..302 tensor indices; inverse mapping and all arithmetic
   must have explicit postconditions and overflow/range proof obligations.
4. GF(2) parity is over exactly two 23-bit words using bitwise AND, a
   bounded loop and characteristic-two output. It does NOT prove Golay rank,
   syndrome or distance.
5. A validated edge transition requires a reciprocal adjacency pair and
   forbids self-loops; invalid candidates are rejected without moving.
   This checks one supplied edge, not complete graph validity.
6. GNATprove must run in mode=all with output-header, report=all and explicit
   proof settings; do not infer a proof from successful Ada compilation,
   a process exit code or a vacuous empty report.
7. Source and tool versions, report header, per-unit coverage and unresolved
   obligations must be retained. No unapproved assumptions, pragma
   Assume/Annotate justified checks or suppressed checks are permitted.
8. `toolchain-lock.json` records exact Alire crate versions, not verified
   archive digests. Do not assert supply-chain authenticity until the actual
   executables and source checksums have been independently checked.
9. Any proof assessment without a genuine GNATprove report must return
   NOT_RUN/UNVERIFIED; zero outstanding checks gives REVIEW_REQUIRED until
   manually audited, not an automatic proof PASS.
10. v0.7.2 conformance must explicitly compare Python to the Ada reference
    and registered mathematical specification; neither Lean theorems nor Ada
    contracts automatically prove Python.
11. Keep the engineering 3+2 channels separate from any (3,2) physical
    spacetime signature. No astrophysical or cosmological implication.
12. Run Ada builds and GNATprove inside a disposable, unprivileged, offline
    container/VM with no host credentials exposed. Avoid processing
    contributor-controlled GPR/Ada sources on a privileged reviewer host.

# EDGEWALK v0.7.1 — Original SPARK proof evidence

**Status:** GNATprove reported all 48 obligations discharged for the
specified SPARK package, with zero justified and zero unproved. Original
prover reports are retained byte-for-byte alongside this review. This is
NOT a statement that the existing Python implementation was formally proved.

- Source revision: 6a8c0c72dd8f456e75907b213c46828395fc9ca2
- GNATprove report timestamp (UTC): 2026-10-30T13:43:44Z
- Compiler/prover: GNATMAKE 16.1.0, GPRBUILD 26.0.0 (Alire crate
  gprbuild=26.0.1), GNATprove FSF 16.1.0.
- Ada reference self-test: PASS; GNATprove exit: 0.
- Categories: 7 data dependencies, 1 flow dependency, 2 initialization,
  23 runtime-safety checks, 2 assertions, 7 functional contracts,
  6 termination = 48 total.
- 16 checks by flow analysis; 32 by automated prover.
- Detailed report: 1 analyzed Ada unit, 8 of 8 package/subprogram entries
  analyzed, 0 errors/warnings/pragma Assume statements.
- Source SHA-256 (spec): 4608dc2406f241dd186ee39a38004704068b853d3b44a1401ca1b3bdf2a63bd0
- Source SHA-256 (body): 3eb7dd71ad47b9ab08c2a94bea32089f8c306e42f5715daf3e765b20d90c18fe

## Trust and claim limits

This archive preserves recorded execution evidence and matches it to source
and executable fingerprints. Those executable hashes are NOT an independent
publisher signature or an authenticated binary-release archive. An external
auditor must still establish toolchain provenance independently.

GNATprove discharges the contracts that were ACTUALLY DECLARED in the
Ada source; it does not prove full Golay code distance, the entire graph's
physical significance, equivalence with Python, or any cosmological model.
The separate Lean v0.7.0 kernel gate is NOT covered by this result.

No GNATprove logs were regenerated or rewritten by the capture process.
The SHA256SUMS file binds these unmodified bytes; the Git commit storing the
archive supplies the external content-addressed audit checkpoint.

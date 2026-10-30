# EDGEWALK v0.7.0 — Formal Verification Invariants

1. v0.1–v0.6 identity-bearing receipts, Golay/ETQ original code and validated output formats remain untouched. No modifications to QEC or SONIFICATION. No GitHub Actions.
2. Lean toolchain: leanprover/lean4:v4.35.0. Mathlib4 source pin: 56a005855ea17e0b0958f73ec801ae140b0a1679. Review generated lake-manifest.json after actual Lake resolution before accepting a release.
3. Allow only kernel-checkable theorem proofs with no sorry, admit, new axioms, unsafe elaborators, native_decide or compiler-trust shortcuts. Static scanning is an additional guard, not a substitute for kernel checking.
4. Mandatory acceptance is an actual successful lake build and lake check --paranoid with the pinned source (including its sandboxed and independent kernels), plus a reviewed transcript, lockfile, and a full Python regression suite. Failed/missing tools mean NOT RUN or FAILED, never PASS.
5. CRT proof means bijection Fin303 -> Fin101 x Fin3 with the exact published arithmetic inverse; it says nothing about adjacency or physical dimensions.
6. Phase proof means exact modulo-four (3,2,3) Gaussian exponent closure; not an audio rendering or a physical quantum measurement.
7. Monomial proof concerns a declared state Fin303 x ZMod4, one-step support shift and phase action, and exact 303-order return. It does not certify a hardware unitary, physical E8 embedding, or the Python/Node implementation.
8. GF(2) theorems are universal characteristic-two identities and dot-product laws; they do NOT establish concrete Golay rank, distance seven, or a decoder FER result. Golay-specific formal matrix certificates remain future work.
9. No source-audit-only status may be labelled kernel checked. A proof receipt needs toolchain and exact commit identities, full checker transcript and explicit PASS/FAIL/NOT-RUN verdict. No fabricated hashes or execution logs.
10. All null/negative proof results and unsolved obligations remain visible. Any theorem statement weakened to fit a proof is a contract change subject to review. No cosmological or (3,2) spacetime ontology is inferred.

11. Every operation that can elaborate or execute Lean source—including Lake builds, cache commands and paranoid checking—must remain inside a restricted offline sandbox. No host credentials, HOME, secrets, sockets or writable checkout are mounted. A missing sandbox or offline dependency is NOT RUN, never PASS.
12. Python 3.10 without tomllib/tomli must retain a dependency-free full regression suite. The auditor requires byte-for-byte approved Lake TOML on that platform, and additionally checks effective parsed configuration on Python 3.11+. Never accept a hash merely because it appears in a comment.
13. Protect against #eval and similar elaboration-time IO with sandbox isolation as the security boundary; static keyword lint is secondary. Negative controls must include this exploit and missing Python TOML modules.

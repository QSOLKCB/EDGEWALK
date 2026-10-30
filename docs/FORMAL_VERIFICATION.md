# EDGEWALK v0.7.0 — Formal Verification Audit

## Scope and explicit state

A pinned Lean 4 + Mathlib project is committed at proofs/lean.
This is a **candidate formalization** pending actual Lean compilation and
kernel verification. The development runtime did not have Lean, Lake, or
bubblewrap installed and cannot download GitHub release archives; therefore
the status of ALL Lean theorems is **KERNEL CHECK NOT RUN** at the time of
the PR. No theorem is described as verified until the real checker succeeds.

## Theorems and claim boundary

| Module | Proposed checked target | Deliberate exclusion |
|---|---|---|
| CRT | address, inverse, injectivity, surjectivity, bijection | physical geometry; ETQ graph adjacency |
| Phase | modulo-four exponents (3,2,3), gauge potential, 3-step closure | quantum hardware; sonified signal |
| Monomial | actual finite repeated phase-twisted support step, algebraic exact order 303 | physical monomial unitary, original source code correctness |
| GF2 | characteristic-two cancellation and finite dot-product laws | actual Golay H matrix rank/distance |

The monomial proof uses a phase potential on the independent ternary fibre:
potential (0,1,2) = (0,3,1) in ZMod4. Its successor differences produce
(3,2,3); cumulative phases telescope along the 303-index cyclic support.
The proof relates the closed algebraic formula to recursive iteration.
This is stronger than merely confirming an order-303 support cycle.
However the entire theorem proof is only accepted once the pinned Lean
kernel validates the text.

## Trust chain and exact commands

From an EDGEWALK checkout with network access for initial, explicitly
requested mathlib dependency provisioning and a working bubblewrap sandbox:

~~~bash
python -m unittest discover -s tests -v
cd proofs/lean
python3 scripts/static_audit.py
bash scripts/verify.sh
~~~

The script rejects missing/incompatible Lean version, missing Lake/bwrap,
forbidden syntax and changed source pins. It then resolves exact Mathlib
revision, obtains the cache, builds all four modules and performs
\`lake check --paranoid\`. Review/commit the generated lake-manifest.json
after successful dependency resolution; inspect the checker output and
tool versions. Do not replace an absent manifest with fabricated content.
The verifier emits a PASS marker **only** after the actual kernel accepts
every proof, never after the static scanner alone.

Explicit release acceptance requires:
- nonzero proof holes/axiom audit findings == 0
- build success, no unresolved proof goals
- lake check --paranoid success under pinned toolchain and dependencies
- reviewed lockfile and committed toolchain/code reference
- full Python tests pass without changing existing receipts
- no unsupported assertion that the Lean proofs certify Python or physics

The no-GitHub-Actions preference remains in force.

## Future work

For the concrete binary Golay \`[[23,1,7]]\` matrix, independently
construct the 11x23 parity matrix in Lean, prove GF(2) rank, H H^T = 0,
logical dimension and minimum distance. Then implement the SPARK
reference and a separate conformance/semantic refinement argument.


## PR #7 post-audit corrections (2026-10-30)

Three issues were confirmed in the first candidate (5cd2231):
1. The CRT inverse proof contained an unnecessary intermediate modulo 303
   in two Lean \`change\` goals; both were removed without changing the theorem.
2. Lake's root import set cannot define proof acceptance by itself. The
   source audit now requires an **exact** Edgewalk.lean import list and
   exactly the approved module files/import dependencies. The verification
   script explicitly builds Edgewalk.CRT, Edgewalk.Phase, Edgewalk.Monomial,
   Edgewalk.GF2, and Edgewalk before paranoid kernel checking.
3. Mathlib is now validated by parsing the **effective TOML configuration**,
   enforcing the exact Mathlib URL and commit SHA as well as the expected
   Lake root target. A pin merely present in a comment fails.

Regression tests include a trivial-root/broken-CRT negative control and an
altered Mathlib revision/URL with the original pin present only in comments.

**The initial verifier's KERNEL_CHECKED=PASS from the negative control is
INVALID EVIDENCE.** Only a fresh run on the corrected branch can establish
kernel-verified status. No replacement lockfile or kernel log has been
fabricated here. The external reviewer reported 54 passing Python tests
and one pre-existing physical-model CLI error also reproducible on the base;
that failure must remain visible but is a separate issue from these proofs.

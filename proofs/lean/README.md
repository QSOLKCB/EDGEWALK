# EDGEWALK v0.7.0 — Lean mathematical foundation

**Status:** Proof source submitted for independent review; no kernel-checked
verdict may be claimed until the pinned toolchain actually runs successfully.

## Pinned dependencies

- lean-toolchain: leanprover/lean4:v4.35.0
- Mathlib source: https://github.com/leanprover-community/mathlib4
- Exact Mathlib revision: 56a005855ea17e0b0958f73ec801ae140b0a1679
- All proof modules are explicit Lake targets.
- Generated lake-manifest.json is not supplied without an actual Lake resolution;
  generate, review and commit it when the final toolchain execution occurs.

## Verifier (explicit operation, not a GitHub Action)

Requires elan/Lean, Lake, Python 3.10+, bubblewrap with working user namespaces,
and network access ONLY when first resolving the declared mathematical dependency.

    cd proofs/lean
    bash scripts/verify.sh

The script checks source pins/forbidden constructs, executes lake update, fetches
the pinned Mathlib cache, builds the Lean project, and performs
lake check --paranoid. A static pass is NOT a theorem-proof acceptance.
The script stops with an error and no passing proof receipt on any failure.

## Proof scope

- CRT.lean: address + inverse, injectivity and the 303-to-(101,3) bijection.
- Phase.lean: exact modulo-four Gaussian phase exponents, three-step closure,
  and an explicit phase potential.
- Monomial.lean: an executable mathematical monomial step on
  Fin 303 x ZMod 4, the phase-gauge closed-form power, equivalence with
  iteration, exact 303-step return, and exclusion of every smaller
  positive identity power.
- GF2.lean: characteristic-two cancellation, finite binary dot-product
  symmetry, bilinearity and duplicate-zero laws.

**Unproved v0.7 claims:** concrete Golay [[23,1,7]] rank/distance and
entire Tanner-graph eigenvalue identities. General characteristic-two
laws are not a proof that a particular Golay parity matrix has rank 11.
Likewise, none of these algebraic theorems certifies the Python/JavaScript
implementation, cryptographic source provenance, or physical spacetime.

## Mandatory acceptance criteria

- No sorry, admit, unapproved axiom, unsafe/meta code or native_decide.
- Pinned Lean and Mathlib revisions, with a reviewed generated lockfile.
- Complete lake build, lake check --paranoid and a human-reviewed transcript.
- Full Python suite unchanged and passing.
- No GitHub Actions; no modifications to SONIFICATION or QEC.
- Do not mark proofs as kernel-checked based only on source inspection.

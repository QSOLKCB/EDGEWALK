# EDGEWALK agent instructions

Read this file and docs/INVARIANTS.md before changing code.

## Mission
Build an auditable cross-domain graph-stability experiment that separates exact algebra, authored mapping, numerical diagnostics, empirical observations and speculative interpretations.

## Non-negotiable
- No edits to QEC or SONIFICATION from EDGEWALK. Consume upstream artifacts read-only. ETQ-303's canonical event document, CRT order, phases and hashes are immutable.
- Every reported Tanner walk hop MUST be an actual undirected Tanner edge. An ETQ CRT event-address transition is not itself an ETQ Cartesian-graph edge.
- Exact GF(2) arithmetic for CSS parity, rank and logical dimensions. Never replace with floating-point rank.
- Stable ordering, integer tie breaks, no network access or downloads in default execution. Avoid timestamp/randomized identity. No nondeterministic dictionary/set iteration in canonical receipts.
- Domain-separated SHA-256 receipts use EDGEWALK domain labels; do not impersonate ETQ source receipts.
- Keep graph-adjacency matrices (real/integer graph operators) separate from mod-2 parity-check matrices.
- Do not claim the Golay code proves a spacetime, dark energy or dark matter hypothesis. No arbitrary equivalence inferred from 2+3 or 3+2 labels.
- No GitHub Actions unless explicitly requested.
- Add tests for new claims/edge cases, preserve minimal dependencies and ensure a full local suite is run before PR submission.

## Review format
Findings P0/P1/P2, exact reproduction, minimal correction, tests, and a verdict. Preserve negative findings. Document every new mapping and control group.


## v0.3 numerical controls

Read docs/INVARIANTS_V03.md. Never mix X/Z CSS channels for scalar BP, infer stability at a non-fixed trial point, label partial eigenpairs as full spectra, or place floating eigenvalues in canonical receipts. Preserve failing numerical tests when fixing a defect.

## v0.4 control experiments

Read docs/INVARIANTS_V04.md and docs/CONTROL_PROTOCOL.md. Never call a degree-preserving null graph a new Golay code or ETQ root realization. The null sampler and event schedule must be deterministic and local, exact evidence hash-bound, optional statistics excluded from receipt identity. Report the finite Markov-chain nonuniformity caveat rather than claiming validated physical p-values. Add deterministic failing tests and run the full suite.


## v0.5 evidence rules

Read docs/INVARIANTS_V05.md and docs/EVIDENCE_PROTOCOL.md. Never claim an authentic ETQ run based on mocked or synthetic data. Verify the complete manifest and observation-receipt byte/semantic lineage before labelling ETQ validated. Evidence packages must be exclusive-create, replay exact v0.4 core, bind report bytes without circular checksums and explicitly classify unvalidated statistical inference. Fail closed on missing provenance. No network calls, write access to upstream repos or GitHub Actions.


## P1/P2 receipt hardening (v0.5)

Never derive the expected manifest SHA-256 from the candidate ETQ bundle.
Require independently authenticated full-release trust input; no input means
fail closed, and the caller-supplied hash is not provenance proof by itself.
Verification of the v0.5 package also must reconstruct the complete optional
statistical summary using recorded bootstrap settings, independently of the
v0.4 exact receipt. Tamper tests must include recomputation of all dependent
manifest, receiver and checksum digests.


## v0.6 physical-model admission gate

Read docs/INVARIANTS_V06.md and docs/PHYSICAL_PROTOCOL.md before changes.
A physical model is not eligible on aesthetic/graph resemblance alone: it
requires specific equations, units, independently available observations,
a stated data-source digest, a fixed score and null, an explicit physical
exchangeability/generative model argument, and an honest calibration verdict.
Unknown models must fail closed. NASA Kepler is a **retrospective example of
an exactly enumerated conditional label null**, NOT a physically randomized
dataset or a dark-sector test. Never interpret 2+3 engineering channels as
(3,2) spacetime signature. Do not alter v0.1–v0.5 receipts or workflows.


## v0.7 Lean formal proof gate

Before touching proofs, read docs/INVARIANTS_V07.md and
docs/FORMAL_VERIFICATION.md. The exact Lean project is in proofs/lean.
Toolchain and Mathlib source revision must remain pinned. No sorry, admit,
new axiom, unsafe, native_decide or unreviewed metaprogramming proof bypasses.
Run the source audit, Lake build, and lake check --paranoid. If Lean,
Mathlib, bubblewrap or the kernel checker cannot run, report NOT RUN rather
than PASS; never claim a proof was kernel-checked by human inspection.
Theorem statements are scoped to finite ETQ algebra and GF(2) identities:
concrete Golay matrix rank/distance and Python/Node executable conformance
are not proved in v0.7. No network access in ordinary runtime and no GitHub
Actions or upstream changes.

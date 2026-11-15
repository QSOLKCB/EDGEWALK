# EDGEWALK

Deterministic Golay quantum error correction, Tanner and ETQ-303 edge-walk experiments, and spectral-algebra diagnostics. **This is a mathematical research laboratory, not evidence that spacetime is quantum-error-correcting.**

## v0.1 baseline (unchanged)

Python 3.10+, no default third-party dependencies:

~~~bash
python -m edgewalk
python -m edgewalk --full
python -m unittest discover -s tests -v
~~~

The baseline proves Golay CSS [[23,1,7]] invariants, constructs a 45-node Tanner graph, and commits to a 303-step ETQ-inspired auxiliary schedule.

## v0.2 ETQ-303 integration (read-only)

Obtain the published **ETQ-303 v3.0.0** release output from [SONIFICATION](https://github.com/QSOLKCB/SONIFICATION), following its own build instructions and verification:

~~~bash
# Run in a local SONIFICATION checkout; no GitHub Actions
npm test
npm run verify
npm run build:v3
# In an EDGEWALK checkout, point to the generated directory
python -m edgewalk --etq-bundle ../SONIFICATION/dist/etq-303-v3.0.0
# Optional floating-point Laplacian / adjacency eigenspectra:
python -m pip install numpy
python -m edgewalk --etq-bundle ../SONIFICATION/dist/etq-303-v3.0.0 --numerical
~~~

The ETQ adapter **requires all four** original files: contract.json, events.json, graph.json and manifest.json. The small examples/etq-303.v3.canonical.json contract is not a substitute for a built output bundle. No network is used by EDGEWALK at runtime, and no upstream artifacts are modified.

The adapter validates the published event and lifted-edge domain-separated commitments, manifest file checksums, canonical event sequence, Gaussian-unit symbols, graph indices, adjacency and connectivity. A separate deterministic receiver produces *actual graph-edge walks*. The original CRT support traversal is **not a graph walk**.

The v0.2 report includes exact graph spectral moments, non-backtracking state and transition counts, degree profiles, 303-step walk coverage, and **degree-preserving rewiring controls**. Controls are graphs, not valid Golay CSS codes or canonical ETQ products. Exact EDGEWALK comparison receipts exclude NumPy results; optional float64 eigenvalue/IPR output is auxiliary and solver-dependent.

**Interpretation limit:** A numerical resemblance is not a demonstrated spacetime connection, dark matter/energy alternative, or statistically significant result. No coupled physical equations are used. The current null control is a *single deterministic graph rewire*, not a distribution of matched random ensembles; no p-values are claimed.

## Roadmap, contracts and licensing

See [docs/INVARIANTS.md](docs/INVARIANTS.md), [docs/INVARIANTS_V02.md](docs/INVARIANTS_V02.md), [docs/RESEARCH_PLAN.md](docs/RESEARCH_PLAN.md), and [AGENTS.md](AGENTS.md) for strict mathematical and epistemic guardrails.

Source references:
- [QEC](https://github.com/QSOLKCB/QEC)
- [SONIFICATION ETQ-303](https://github.com/QSOLKCB/SONIFICATION) — v3.0.0 original DOI [10.5281/zenodo.21455181](https://doi.org/10.5281/zenodo.21455181)

EDGEWALK is Apache-2.0. SONIFICATION upstream remains its own MPL-2.0 project; integration reads generated output, does not copy its implementation, and keeps upstream canonical hashes unchanged. No GitHub Actions are added.


## v0.3 Spectral Stability Engine (optional)

Install the numerical extras:

    python -m pip install -e '.[stability]'
    python -m unittest discover -s tests -v

Generate an unmodified SONIFICATION ETQ-303 v3 bundle using its own npm test, verify and build:v3 commands. Then in EDGEWALK:

    python -m edgewalk --etq-bundle ../SONIFICATION/dist/etq-303-v3.0.0 --stability

Optional skip of the large sparse non-backtracking solve:

    python -m edgewalk --etq-bundle ../SONIFICATION/dist/etq-303-v3.0.0 --stability --no-nonbacktracking

The read-only upstream adapter verifies ETQ source commitments before this engine runs. The v0.2 comparison receipt SHA-256 remains unchanged by the stability flag. All floats live in stabilityAuxiliary, which is NOT identity-bearing.

The engine computes directed-edge Hashimoto eigenmodes with residuals and qualified IPR; Bethe Hessian spectra; complete clustered Laplacian eigenspace projectors; an exact ETQ Cartesian topology check followed by the numeric {lambda,lambda+3,lambda+3} test; isolated X- and Z-channel scalar sum-product BP Jacobians with a fixed-point residual gate; and paired positive vertex-potential perturbations against degree-preserving graph-only controls.

These are mathematical diagnostics. The BP proxy is not quantum decoding performance; a single deterministic control is not a null distribution; partial spectral samples are not full spectra. No physical cosmology interpretation is implied. See docs/INVARIANTS_V03.md.

Integration gate: tests using synthetic 303-state Cartesian graphs validate the mathematics and code paths, NOT the original published ETQ-303 source identity. A verified run against the actual SONIFICATION artifact bundle remains mandatory for a real end-to-end result. No GitHub Actions are added.

## v0.4.0 — Controlled Spectral Experiments

Reproducible **integer-only core**, with no extra dependencies for the Golay controls:

~~~bash
python -m edgewalk --controls
python -m edgewalk --controls --control-samples 32 --control-swaps 16 --control-seed 303
python -m unittest discover -s tests -v
~~~

For the ETQ-303 Cartesian-product control, first generate and independently verify the original SONIFICATION v3.0.0 build bundle, then:

~~~bash
python -m edgewalk --controls --etq-bundle ../SONIFICATION/dist/etq-303-v3.0.0
~~~

The adapter remains **read-only** and validates ETQ's published commitments. Synthetic test fixtures are not equivalent to an archived ETQ integration run. No network fetch is performed by EDGEWALK.

**What the controls do:** reference and two elementary-GF(2)-sheared Golay Tanner check bases are valid CSS stabilizer bases. For each basis, its null ensemble uses deterministic channel-preserving Tanner two-switches which preserve every vertex's X/Z degrees but may violate CSS constraints. ETQ controls first verify the real graph's `G101 □ C3` topology, then rewire the 101-node base while preserving degree, reconnect and lift back to `G101 □ C3`. These nulls retain product geometry but are not released ETQ root models.

The **exact experiment evidence**, including source and null graph SHA-256 fingerprints, integer fourth adjacency spectral moments/4-cycles, 303-event edge-walk coverage, paired 1-/2-edge deletion deltas, fixed settings and seeds, is bound by `EDGEWALK/V4/EXPERIMENT`. Run `edgewalk.controls.replay_experiment_receipt` to independently regenerate the integer portion. Changing bootstrap output does not change exact identity.

The **separate exploratory analysis** reports the generated null mean and median, a seeded percentile-bootstrap interval for the null mean, empirical two-sided tail fractions, and Holm-adjusted exploratory tail ranks across the predeclared metric family. Finite-step graph two-switches are *not established as uniform, stationary, independent or exchangeable null draws*. Consequently, these are **not calibrated p-values or frequentist confidence intervals for physics**. A significant cosmological, dark-energy or dark-matter result is **not** claimed. Source graphs have different sizes and degrees; absolute comparisons across Golay and ETQ are descriptive only.

See [CONTROL_PROTOCOL](docs/CONTROL_PROTOCOL.md), [INVARIANTS_V04](docs/INVARIANTS_V04.md) and [RESEARCH_PLAN](docs/RESEARCH_PLAN.md). The existing v0.1, v0.2 and v0.3 command paths and exact receipts are unchanged. No GitHub Actions have been introduced.


## v0.5.0 — Experimental Validation & Evidence

The v0.5 release provides a **read-only ETQ-303 v3.0.0 release-integrity gate**, deterministic experiment evidence packages, independent replay commands, calibration diagnostics, and a conservative findings report. Python standard library only for the evidence workflow.

Build the source ETQ bundle in its own SONIFICATION checkout using its published Node workflow; this project never changes those files. A valid v3 bundle contains contract.json, contract.schema.json, events.json, events.csv, events.mid, graph.json, event-atlas.json, observation-receipt.json and manifest.json.

~~~bash
# Source gate: only with independently authenticated ETQ_PIN and original output
python -m edgewalk --validate-etq ../SONIFICATION/dist/etq-303-v3.0.0 \
  --trusted-etq-manifest-sha256 "$ETQ_PIN"

# Golay-only evidence (ETQ gate explicitly recorded as not-run)
python -m edgewalk --evidence-out evidence-golay \
  --control-samples 4 --control-swaps 2 --bootstrap-draws 32
python -m edgewalk --verify-evidence evidence-golay

# Complete ETQ/Golay integration, only with actual verified source output
python -m edgewalk --evidence-out evidence-etq \
  --etq-bundle ../SONIFICATION/dist/etq-303-v3.0.0 \
  --trusted-etq-manifest-sha256 "$ETQ_PIN"
python -m edgewalk --verify-evidence evidence-etq \
  --etq-bundle ../SONIFICATION/dist/etq-303-v3.0.0 \
  --trusted-etq-manifest-sha256 "$ETQ_PIN"

python -m unittest discover -s tests -v
~~~

The package is a **new, exclusive directory** (never overwritten), containing experiment.json, validation.json, calibration.json, findings.md, manifest.json and SHA256SUMS.txt. Exact v0.4 evidence is replayed and its original domain-separated hash preserved. The package manifest commits all accompanying artifact bytes; the checksum list excludes itself to prevent a circular hash.

ETQ validation calls the v0.2 cryptographically pinned source adapter and additionally checks **all** manifest-listed output bytes, the signed-by-hash observation receipt core, and receiver SHA-256 commitments. This establishes release-artifact **integrity relative to published commitments**, not authorship, physical provenance or observational validation.

Calibration deliberately fails closed: lag-one and split-half metrics are diagnostic, but the finite two-switch chains are not proven mixed, stationary, independent or exchangeable. No calibrated significance, physics confidence interval, dark-energy conclusion or dark-matter conclusion is reported. See docs/INVARIANTS_V05.md and docs/EVIDENCE_PROTOCOL.md. The authentic ETQ end-to-end gate must be executed on actual upstream files: synthetic fixture tests do not count as passing it. No GitHub Actions are added.


### Mandatory v0.5 trust pin and exploratory-summary replay

The upstream ETQ-303 publication pins events and lifted edges, but no independently
published **complete v3.0.0 manifest SHA-256** has been verified for this
implementation. The full ETQ validation gate therefore **fails closed** by
default: a self-consistent manifest and observation receipt cannot establish
an authentic complete export. Supply `--trusted-etq-manifest-sha256 SHA256`
only with a digest separately obtained and authenticated from the publisher
or another trusted archival source. **Never compute this pin from the bundle
being validated**; doing so reintroduces the forgery vulnerability. The caller
is responsible for the independent provenance of this pin. The CLI cannot
itself prove a caller-supplied digest was obtained independently.

~~~bash
python -m edgewalk --validate-etq SOURCE_DIR \
  --trusted-etq-manifest-sha256 TRUSTED_64_HEX_SHA256

python -m edgewalk --evidence-out evidence-etq --etq-bundle SOURCE_DIR \
  --trusted-etq-manifest-sha256 TRUSTED_64_HEX_SHA256

python -m edgewalk --verify-evidence evidence-etq --etq-bundle SOURCE_DIR \
  --trusted-etq-manifest-sha256 TRUSTED_64_HEX_SHA256
~~~

A real release pin should be published separately (for example in a signed,
version-specific release statement) before anyone claims the full gate passed.
Golay-only packages do not need an ETQ pin and continue to record `not-run`.

The v0.5 package also records `analysisParameters.bootstrapDraws` outside
the exact v0.4 evidence commitment. Verification independently reconstructs
every `exploratoryAnalysis` field, including the seeded bootstrap intervals
and tail-rank adjustments. Incorrect or type-altered summaries are rejected
even when the package's outer manifest/checksum values are recomputed. The
v0.4 exact receipt identity remains unaffected by bootstrap settings.


## v0.6.0 — Independent Physical Model Adapter (strict gate)

The first accepted **physical-domain adapter** is a retrospective, bounded
Kepler third-law demonstration using publicly available [NASA NSSDCA Planetary
Fact Sheet](https://nssdc.gsfc.nasa.gov/planetary/factsheet/) data
(last updated 18 March 2025). The exact fixture transcribes eight planets'
mean heliocentric distances (millions of km) and orbital periods (days).
NASA's mean distance is a *proxy* for a Keplerian semimajor axis, not a claim
of independently reprocessed orbital elements. The CSV's SHA-256 is pinned in
the adapter; execution never downloads untrusted data or substitutes a file.

**Specified physical equation:** P(a) = P_Earth (a/a_Earth)^(3/2),
with one Earth anchor and seven held-out planet pairs. The fixed test
statistic is mean squared log-period prediction error (smaller is better).
The null enumerates *all 7! = 5040* assignments of the seven orbital
periods to the seven distances. The tail probability is an **exact conditional
permutation rank** for the explicitly defined *uniform random-label null*.
It is not an approximate MCMC null, and no asymptotic normality assumption
is required for that conditional calculation.

**Critical distinction:** the actual planets were not randomly assigned
their periods. Random-label exchangeability is **not demonstrated as a
physical observation-generating mechanism**. Therefore this is NOT an
astrophysically calibrated test of Kepler's law, a discovery p-value, or
prospective hypothesis confirmation; NASA's data predate v0.6. The apparent
support is a retrospective instructional benchmark. The resulting
`calibration` object explicitly reports
`nullExactlyEnumerated=true` but
`astronomicalInferenceCalibrated=false`.

~~~bash
python -m edgewalk --physical-model kepler-earth-anchored-v1 > kepler-report.json
python -m edgewalk --verify-physical-report kepler-report.json
python -m unittest discover -s tests -v
~~~

This model is **not** an adapter for the Alexander–Temple–Vogler cosmology
or (3,2)-signature hypotheses. Any proposed additional physical model must
supply the exact governing equations, parameter units/bounds, independently
available observations and source identity, fixed test statistic, explicit
exchangeability/generative-null justification, predeclared decision rule,
and negative-result protocol **before** it is registered. Unknown model IDs
fail closed.

The v0.6 receipt domain is `EDGEWALK/V6/PHYSICAL-EXACT` and
commits the external data transcription digest, source description, fixed
protocol, permutation count and exact tail count. Numerical diagnostics are
separate but the verifier independently recomputes the entire JSON report,
including its floats. Earlier receipts remain unchanged. The **engineering
(2,3) channel structure does not imply any physical (3,2) spacetime signature.**

Read [docs/PHYSICAL_PROTOCOL.md](docs/PHYSICAL_PROTOCOL.md) and
[docs/INVARIANTS_V06.md](docs/INVARIANTS_V06.md). No GitHub Actions added.


## v0.7.0 — Lean 4 Mathematical Foundation (review-gated)

The separately versioned proof project lives under [proofs/lean](proofs/lean).
It pins **Lean 4.35.0** and an exact compatible Mathlib commit. The
candidate theorem modules cover the ETQ-303 CRT bijection, Gaussian-unit
phase closure, the actual repeated phase-twisted monomial step's exact order
303, and universal GF(2) cancellation/dot-product identities.

~~~bash
python -m unittest discover -s tests -v
cd proofs/lean
python3 scripts/static_audit.py  # source check ONLY, not a proof
bash scripts/verify.sh          # Lake + kernel + independent checkers
~~~

The last command requires the pinned Lean toolchain, Mathlib, and bubblewrap.
It performs Lake dependency resolution, a complete build and
\`lake check --paranoid\`. **A source audit or Python arithmetic replay does
not mean a Lean theorem has been kernel-checked.** This pull request must not
be certified or merged as a completed formal-verification milestone until
the kernel checker passes and the generated Lake lockfile is reviewed.
No GitHub Actions are added.

The GF(2) module proves universal algebraic identities, NOT the concrete
Golay parity-check rank, orthogonality receipt or code distance. The monomial
theorem describes the declared ETQ phase/support convention, NOT the physical
existence of a quantum gate or spacetime field. Neither proves the existing
Python/Node implementations correct; differential conformance is a separate
v0.7.2 milestone. See [FORMAL_VERIFICATION](docs/FORMAL_VERIFICATION.md).

### v0.7 proof-verifier security gate

All Lean builds and paranoid checking now run under an **offline bubblewrap
sandbox**, including the source audit. No contributor Lean code is elaborated
on the reviewer's credential-bearing host. The verifier requires previously
reviewed `lake-manifest.json` and offline Mathlib sources; missing inputs
result in NOT RUN, not a fabricated proof result. Set up these dependencies
through a separately trusted, isolated provisioning procedure. The standard
Python 3.10 regression suite needs no `tomli` package: the auditor checks
an exact allowlisted Lake configuration. See proofs/lean/README.md.

## v0.7.1 — SPARK Ada Reference Kernel (48 checks discharged)

The narrow Ada/SPARK reference in `proofs/spark/` covers ETQ CRT addressing,
phase/tensor fields, 23-bit GF(2) parity and reciprocal-edge transitions.
An authentic offline GNATprove FSF 16.1.0 run at historical source commit
`6a8c0c7` reported 48 checks (16 flow and 32 prover), zero unproved and
zero justified. All original logs are preserved with source snapshots,
checksums and an audit manifest.

These results establish the **declared Ada contracts only**. Python
equivalence, full nonzero-word parity correctness and the separate Lean
kernel gate remain outside the scope of this audit. Recorded executable
fingerprints do not authenticate the original vendor release archives.

## SPARK v0.7.1 verification evidence audit

The original unmodified 2026-10-30 GNATprove logs, source/toolchain
fingerprints and checksum-bound manifest are preserved in [the 21-file
archived evidence set](proofs/spark/audits/2026-10-30-6a8c0c7).
See [the evidence review](docs/SPARK_FORMAL_VERIFICATION_EVIDENCE_v071.md)
and [archive replay tool](proofs/spark/audit/capture.py). The SPARK result
does not establish independent vendor authentication, the Lean kernel
verification or Python/Ada semantic equivalence.

## v0.7.2 — Executable Python/SPARK Proof-Conformance Bridge

The [v0.7.2 protocol](docs/INVARIANTS_V072.md) adds a **real Ada**
stdin/stdout test driver using the unchanged, source-hash-pinned v0.7.1
SPARK package, and a Python oracle over 10,033 deterministic cases:
303 forward CRT, 303 inverse CRT, 1,024 sampled 23-bit parity pairs,
8,100 45-vertex edge-acceptance controls and 303 real Tanner-walk edges.

~~~bash
python3 -m unittest discover -s tests -v
cd proofs/spark
bash conformance/run.sh
~~~

The latter step builds and executes the Ada harness **only inside an offline
Bubblewrap sandbox**, checks the pinned toolchain, regenerates Python
expectations and rejects any mismatched records. It writes inert comparison
artifacts and a deterministic, SHA-256-bound receipt under ignored
`proofs/spark/conformance-output/`. No GitHub Actions. It requires the
separately provisioned GNAT/GPRbuild/GNATprove toolchain and original archived
v0.7.1 proof report. Until that command has been run and reviewed on a
real Ada-equipped host, this v0.7.2 feature is **implementation ready,
execution unverified**.

The conformance driver itself is non-SPARK and not formally proved. Testing
finite cases does not prove Python/Ada semantic equivalence, expand Ada's
declared contracts, or establish Lean kernel verification.

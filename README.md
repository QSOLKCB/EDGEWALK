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
# Standalone source authenticity gate (requires real SONIFICATION output)
python -m edgewalk --validate-etq ../SONIFICATION/dist/etq-303-v3.0.0

# Golay-only evidence (ETQ gate explicitly recorded as not-run)
python -m edgewalk --evidence-out evidence-golay \
  --control-samples 4 --control-swaps 2 --bootstrap-draws 32
python -m edgewalk --verify-evidence evidence-golay

# Complete ETQ/Golay integration, only with actual verified source output
python -m edgewalk --evidence-out evidence-etq \
  --etq-bundle ../SONIFICATION/dist/etq-303-v3.0.0
python -m edgewalk --verify-evidence evidence-etq \
  --etq-bundle ../SONIFICATION/dist/etq-303-v3.0.0

python -m unittest discover -s tests -v
~~~

The package is a **new, exclusive directory** (never overwritten), containing experiment.json, validation.json, calibration.json, findings.md, manifest.json and SHA256SUMS.txt. Exact v0.4 evidence is replayed and its original domain-separated hash preserved. The package manifest commits all accompanying artifact bytes; the checksum list excludes itself to prevent a circular hash.

ETQ validation calls the v0.2 cryptographically pinned source adapter and additionally checks **all** manifest-listed output bytes, the signed-by-hash observation receipt core, and receiver SHA-256 commitments. This establishes release-artifact **integrity relative to published commitments**, not authorship, physical provenance or observational validation.

Calibration deliberately fails closed: lag-one and split-half metrics are diagnostic, but the finite two-switch chains are not proven mixed, stationary, independent or exchangeable. No calibrated significance, physics confidence interval, dark-energy conclusion or dark-matter conclusion is reported. See docs/INVARIANTS_V05.md and docs/EVIDENCE_PROTOCOL.md. The authentic ETQ end-to-end gate must be executed on actual upstream files: synthetic fixture tests do not count as passing it. No GitHub Actions are added.

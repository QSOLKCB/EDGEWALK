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

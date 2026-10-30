# EDGEWALK

Deterministic laboratory for **Golay quantum error correction**, Tanner graph edge walks, **ETQ-303-inspired** event scheduling, and spectral stability experiments.

**Research status:** mathematical/software methods only. No evidence is claimed for physical spacetime error correction, dark-matter alternatives, dark-energy alternatives, or multidimensional spacetime.

## v0.1.0: executable reference baseline

The first stage constructs the classical binary Golay [23,12,7] code from the cyclic generator polynomial, derives its 11-row dual parity checks and uses those checks as **both** X and Z stabilizers of the CSS quantum Golay [[23,1,7]] code. It constructs a 45-node, 176-edge combined X/Z Tanner graph. A reproducible 303-event **auxiliary schedule** chooses valid edges, records event addresses, and commits results to a domain-separated SHA-256 receipt.

The schedule is *inspired by*, but is **not**, the canonical ETQ-303 event document. It does not copy, rewrite, or replace the immutable ETQ-101/303 protocols and does not treat the original CRT support traversal as a graph-edge walk.

Run with Python 3.10+ and no third-party dependencies:

    python -m edgewalk
    python -m edgewalk --full
    python -m unittest discover -s tests -v

Default output is a compact JSON summary including the receipt. The --full form adds all 303 adjacency-verified transitions.

## Foundational references

- QEC toolkit: https://github.com/QSOLKCB/QEC
- ETQ-303 canonical source: https://github.com/QSOLKCB/SONIFICATION
- ETQ-303 v3 DOI: https://doi.org/10.5281/zenodo.21455181

Read AGENTS.md, docs/INVARIANTS.md and docs/RESEARCH_PLAN.md before extending the experiment. No GitHub Actions are configured. Run the local test suite before opening or merging a PR.

## Scope boundary

Mathematically equivalent implementation choices are not automatically physically equivalent theories. Golay code distance is not a cosmological observable; algebraic vector-space dimensions are not spacetime dimensions; spectra computed from differently constructed graphs must not be compared without controls. Negative/null outcomes are first-class results.

## Licensing

EDGEWALK is Apache-2.0 (see LICENSE). Other QSOL projects have their own licence/identity; use references or independently authored adapters rather than copying their source or changing their released contracts.

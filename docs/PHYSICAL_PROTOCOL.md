# EDGEWALK v0.6 — Independent Physical-Model Protocol

## Model: Kepler Earth-anchored v1
- Data source: NASA NSSDCA Planetary Fact Sheet, https://nssdc.gsfc.nasa.gov/planetary/factsheet/, listed last updated 2025-03-18. Numbers are a pinned **transcription** of published rounded mean heliocentric distance and orbital period, not a cryptographic proof of publisher-origin bytes and not independent instrument observations.
- Physics: Kepler's approximately two-body law P^2/a^3 = constant. Operational equation P(a)=P_Earth (a/a_Earth)^(3/2); Earth provides the one scale parameter, seven other planet pairs are scoring rows. This is a source-rounded teaching benchmark, not a high-precision N-body model.
- Parameters/units: input distances in millions of kilometres, output in days. Earth anchor fixed using published Earth entry, no test-row parameter fit.
- Scoring: average squared residual in natural-log orbital period across the seven held-out labels; smaller is better, no alternate metric selected after observing results.
- Null: all 5040 bijections of the seven recorded periods to the seven distances with equal probability under an explicitly defined *random assignment null*. Exact one-sided tail = count(permuted score <= observed)/5040, ties included. No finite-sample Monte Carlo uncertainty for the conditional enumerated assignment null.
- **Physical inference gate:** the planets were NOT randomized. Exchangeability of periods across their distances as an astronomical data-generating mechanism is not established. Thus an exactly calibrated **conditional mathematical** null does NOT equal an astronomically calibrated sampling model. The report must emit both truths separately.
- **Protocol status:** retrospectively specified on 2026-10-30 using NASA data published before that date. Any 'predeclared' claim applies to the code's unchanging evaluation protocol, not an earlier prospective preregistration.

## Replay and provenance
`python -m edgewalk --physical-model kepler-earth-anchored-v1 > kepler-report.json` produces deterministic JSON. `python -m edgewalk --verify-physical-report kepler-report.json` replays source checksum, fixed model, entire permutation enumeration and all numerical diagnostics. The CSV is distributed in the Python package, locally and read-only, without web access. Source is acknowledged by URL, source date, input units and pinned transcription checksum. Neither the JSON receipt nor code itself proves the external provenance of that transcription.

## Extension and exclusion
A prospective physical hypothesis involving a 5D signature, Friedmann instability, gravity or decoding dynamics must independently specify exact equations, boundary/initial conditions, observed quantities and units, instrument/dataset provenance, uncertainty model, meaningful null-generating process, exchangeability assumptions, controlled reference distributions, multiplicity corrections and preregistered test criteria. No such physics adapters are automatically derived from ETQ-303 or Golay. The (2,3) analysis MUX is engineered software architecture, NOT a (3,2) spacetime.

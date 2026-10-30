# EDGEWALK v0.5.0 — Experimental Evidence Invariants

1. Preserve exact v0.1 Golay, v0.2 ETQ commitments, v0.3 numerical boundaries and v0.4 experiment SHA-256. No modified upstream QEC/SONIFICATION sources.
2. ETQ validation is read-only, local, requires the actual original v3.0.0 build output, runs load_etq_bundle and validates every listed upstream artifact SHA-256 and byte length, the manifest core, observation receipt core and all receiver byte and semantic hashes. Reject missing, duplicate and unexpected manifest entries, symlinks, and oversized files.
3. The ETQ gate is either passed after real integrity validation or not-run when absent; a fabricated/partial input must fail. Archive source hashing means compatibility with published bytes, not proof of authorship, physical realization or statistical validity.
4. Write packages only to a previously nonexistent directory with exclusive file writes. No overwrite, cleanup/delete or implicit network.
5. Package files: experiment.json (v0.4 exact and exploratory), validation.json, calibration.json, findings.md, manifest.json, SHA256SUMS.txt. Manifest hashes every preceding file. The checksum listing hashes all files except itself.
6. Exact replay must recompute the complete v0.4 experiment including source identities, each control graph and integer result, rehash the *submitted exact evidence*, and check source ETQ again when necessary. Float substitutions into integer receipts must not pass.
7. Package verification checks every file and its checksum list, exact replay, independently reconstructed calibration diagnostics and deterministic findings content. External changes that are merely self-consistent JSON must not bypass replay.
8. Sampling diagnostics (first/second-half means and lag-one serial correlation) are descriptive. Report calibrated=false unless a separately validated mixing/exchangeability model is added. Never call v0.4 exploratory tail fractions calibrated p-values.
9. Findings language: supported exact graph arithmetic/replay; INCONCLUSIVE inference about cross-system mechanism; NOT TESTED dark matter/dark energy/(3,2)-spacetime. Do not infer physical theory from topology.
10. The authentic SONIFICATION integration check remains a release gate until an actual verified original bundle is run, even if synthetic/mock tests pass. No GitHub Actions.


11. **External trust required:** the full ETQ v3 manifest SHA-256 must match a separately authenticated trusted value, supplied through the dedicated CLI/API parameter. Missing pins fail closed; pins calculated from the submitted bundle are not independent trust roots. No internally self-consistent receipt may authenticate itself.
12. **Auxiliary replay required:** the package stores its bootstrap draw count outside the v0.4 exact core; the verifier regenerates every exploratory summary deterministically and compares canonical bytes. Rehashing a forged exploratory result cannot make it valid.

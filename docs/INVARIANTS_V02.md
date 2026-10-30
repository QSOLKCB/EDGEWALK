# v0.2 auxiliary analysis invariants

v0.1 Golay/CSS, 45-node Tanner and 303-event contracts remain unchanged.

1. ETQ source is read-only and local. Bundle must have unmodified ETQ-303 v3.0.0 events.json, graph.json, contract.json, manifest.json, valid byte hashes and manifest core, published event-document and lifted-edge semantic commitments.
2. No source event is silently converted into a graph edge. Any reported walk hop must be bidirectionally adjacent in the selected receiver graph.
3. ETQ nodes: exactly 303 tensor basis indices with site = index//3 and fibre = index%3; 5364 unique sorted undirected edges; only valid base-or-fibre Cartesian edge kinds; degree range 24–57; connected.
4. Each canonical source event matches its exact CRT address, phase and next sequence/tensor index. The input document itself states eventTraversalIsGraphWalk: false.
5. Golay and ETQ comparisons are descriptive. Each has a separate degree-preserving deterministic two-switch graph-only control. This does not preserve CSS orthogonality, ETQ product algebra or physical predictions.
6. Auxiliary spectra use NumPy float64 by explicit opt-in. No eigensolver result or floating value goes into EDGEWALK exact receipt identity. GF(2) algebra remains integer-only.
7. SHA256 receipt domain for comparison is EDGEWALK/V2/COMPARISON, not any ETQ domain. JSON exact core uses compact, lexicographically sorted integer/string data only.
8. No network calls, GitHub Actions, machine-specific timestamps, or modification of upstream QEC/SONIFICATION code. Physical claims require independent validation.

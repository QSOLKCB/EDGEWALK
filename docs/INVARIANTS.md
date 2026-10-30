# EDGEWALK invariants (v0.1.0)

1. **Classical source code**: length 23, 12 independent cyclic-generator rows defined by g(x)=x^11+x^9+x^7+x^6+x^5+x+1 (bit mask 0xAE3). The classical code has parameters [23,12,7].
2. **Quantum CSS checks**: dual nullspace has 11 independent rows, and H_X=H_Z=H with H H^T = 0 over GF(2). Therefore n=23, rank(H_X)=rank(H_Z)=11, k=1. The minimum weight of a non-stabilizer logical operator is 7.
3. **Tanner representation**: 23 common qubit nodes, 11 X-check nodes, 11 Z-check nodes; exactly 45 nodes and 176 undirected edges for the chosen deterministic check basis. Basis choice matters; these graph counts are fixture-specific, not invariant under every stabilizer basis.
4. **ETQ-inspired schedule**: for event n in [0,302], j=n mod 101, a=n mod 3, index=3j+a, phase exponents=(3,2,3), symbolic multipliers=(-i,-1,-i). CRT inverse must round-trip. Phase product over each three-step fibre cycle is 1. This is an auxiliary EDGEWALK mapping, not the canonical ETQ event document.
5. **Edge-walk contract**: for every source/destination pair, source and destination are distinct and mutually adjacent. Each step uses a stable sorted neighbour list and integer selection, without floating-point decisions or a random seed.
6. **Receipt identity**: UTF-8 compact sorted-key JSON with integer values, domain EDGEWALK/V1/WALK followed by NUL before SHA-256. Receipt commits to exact walk events plus graph/source metadata. It is not an ETQ hash.
7. **Separation**: any Laplacian or non-backtracking spectral numerics are auxiliary; no floating eigensolver value may alter core identity or select an exact graph edge.
8. **Scientific boundary**: analogies among Golay, ETQ and proposed cosmological spacetime dynamics are test hypotheses, not validated physical relations. Geometry drawn as a graph embedding is authored unless explicitly proven intrinsic.
9. **Baseline reproducibility**: Python standard library only; run python -m unittest discover -s tests -v; no CI workflow is implied.

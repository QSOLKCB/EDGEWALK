# v0.3 numerical spectral stability contract

1. v0.1 Golay/CSS invariants and v0.2 ETQ read-only validation are unchanged. External repositories are not mutated.
2. Numerical calculations are optional, require NumPy/SciPy, and are excluded from the existing EDGEWALK exact comparison receipt.
3. Hashimoto oriented-edge states (u,v) transition to (v,w) iff w!=u; operator dimension = 2m and transitions = sum_v d_v(d_v-1). Stable sorting fixes indices.
4. ARPACK eigenpairs are numerical subsets: record solver, residuals, tolerance, returned modes; near-degenerate non-normal eigenvector IPR is withheld. A subset is not the full spectrum.
5. Bethe Hessian H(r)=(r*r-1)I-rA+D uses explicit positive r. Partial smallest eigenvalues do not reveal total negative inertia.
6. Laplacian spectral projectors are rotation-invariant within grouped eigenspaces; tolerance determines clusters. Full diagonals are available in the API but omitted from compact summaries.
7. The ETQ shift {lambda_i,lambda_i+3,lambda_i+3} is tested only after exact G101 Cartesian C3 adjacency validation. Synthetic fixtures do not authenticate ETQ published hashes.
8. Classical scalar BP uses one CSS check channel at a time. A local-attractor label requires an actual fixed point with residual below threshold. This does not establish quantum decoder FER or cosmological dynamics.
9. Paired positive diagonal potential perturbations use a stable vertex name, common epsilon and fixed degree-preserving rewires; such controls do not preserve CSS, ETQ, or physical validity and are not significance tests.
10. No floating identity fields, network access, hidden timestamps, upstream changes, or GitHub Actions. All null findings must be preserved. Run full local suite before merge.

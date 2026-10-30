# EDGEWALK research plan and falsification gates

## Hypothesis H0 (null)
Similar-looking spectral/stability features between Golay Tanner walks and ETQ-303-derived graph observations arise from graph size, node-degree profiles, deterministic scheduling, or plotting choices rather than a shared underlying mechanism.

## H1 (conditional, testable)
After controlling for degree profiles, vertex counts, schedule, and metric normalization, selected graph and perturbation diagnostics show reproducible associations exceeding the null ensemble. An association is not proof of common physical implementation.

## Planned phases
- **v0.1**: exact Golay construction, honest Tanner adjacency, 303-event auxiliary walk and immutable receipt. Validate all discrete invariants.
- **v0.2**: an ETQ read-only input adapter that validates upstream version/identity and consumes exact upstream graph/event artifacts. The fixture must not be reconstructed by assuming a CRT step is a graph edge.
- **v0.3**: numeric auxiliary graph Laplacian, non-backtracking spectrum, IPR, spectral gaps, local BP Jacobian proxy; report solver precision and degeneracy policy. No numeric values in exact receipts.
- **v0.4**: paired controls, degree-preserving edge rewires (subject to bipartite constraints), schedule permutations, multiple check-basis choices, pre-registered thresholds and negative-result reports.
- **v0.5+**: conditional, independent spacetime-model adapters only with explicitly stated physical predictions and externally provided model equations/data. Do not conflate 3+2 engineering channels with (3,2) spacetime signature.

## Evaluation
Separate exact correctness, software reproducibility, numerical robustness, and empirical interpretation. Compare out-of-sample metrics under matched controls. Report confidence intervals and multiple-comparison handling; archive failed and null comparisons.

## ETQ caution
ETQ-303's event support map (j,a)->(j+1 mod 101,a+1 mod 3) generally changes both coordinates, so it does not trace edges of G101 □ C3. A separate verified traversal must be built for any graphical edge-walk claim.

## Gremlin notes
- **G-001 false edge**: treating CRT support steps as Cartesian product graph edges. Prohibited.
- **G-002 rank confusion**: using real-valued rank rather than GF(2) rank. Prohibited.
- **G-003 spectral fishing**: selecting a graph, coordinate mapping, or eigensolver solely because plots look similar. Controlled experiments required.
- **G-004 identity laundering**: treating an EDGEWALK schedule as the original ETQ event receipt. Prohibited.

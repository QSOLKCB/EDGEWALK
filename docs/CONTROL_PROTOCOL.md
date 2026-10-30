# EDGEWALK v0.4 — Registered Graph-Control Protocol

## Objective and falsification
H0: any apparent Golay/ETQ spectral resemblance is explainable by graph degrees, event scheduler and authored representations. H1: explicitly declared features survive suitable constraints and out-of-sample nulls. No physical equivalence is tested in v0.4.

## Sampling families
The input to EDGEWALK is the same repository-defined Golay [23,1,7] CSS code or a **read-only authenticated ETQ v3 bundle**. Golay reference and two independent elementary-check-row shears preserve the code subspace but alter its Tanner presentation. Each graph gets an independent SHA-256 counter stream keyed by (integer seed, system label, replicate). The channel-preserving Golay two-switch randomizes graph topology, not stabilizer algebra. ETQ base rewiring maintains |V|=101, base vertex degrees and connectivity, then uses the same Cartesian C3 lift as the source. A source-to-null comparison is size- and degree-matched **within that system**; comparisons between Golay and ETQ are **not** matched by graph size or degrees. No inference is made across their absolute metric scales.

Rewire is a finite Markov chain with explicit proposal, rejection, maximum attempt cap, distinct-replicate fingerprinting and nonuniformity caveat. Replicates are algorithmically deterministic, but that does not make samples independent or uniformly distributed. This is a reproducibility stage, not a calibrated random-graph ensemble.

## Exact metric contract (declared before sampling)
For each graph, compute the number of unique 4-cycles C4, the number of unique adjacency-verified edges used by a fixed 303-step ETQ-inspired walk, and the **difference** in exact trace(A^4) after deleting the first one and the first two lexical undirected edges. Both deletion perturbations are paired by edge **rank** only, not by physical or graph-isomorphism identity. Exact spectral moment identity:

    trace(A^4) = 2m + 4 sum_v binom(d_v,2) + 8 C4.

The 303-step receiver must visit only actual graph edges, not ETQ CRT support transitions.

## Statistics and identity
All graph fingerprints, original metric vectors, replicate vectors and recorded settings enter a SHA-256 domain-separated exact evidence receipt (`EDGEWALK/V4/EXPERIMENT`). `replay_experiment_receipt` rebuilds every integer array from the published configuration and the same verified ETQ bundle when supplied. No floating values or bootstrap output are in receipt identity.

A distinct floating analysis reports the null median, null mean, seeded 95% percentile bootstrap interval for the **generated null mean**, two-sided empirical tail rank relative to null median, and exploratory Holm step-down adjustment across the entire predeclared family. Neither the bootstrap interval nor adjusted tail rank is a calibrated physics confidence interval/p-value without a justified exchangeable null sampling model.

## Controls and follow-up gates
Use at least four distinct controls; default 16, maximum 128. Predefine seed, swaps, number of bootstrap draws, variants and perturbation ranks. Report every null, including no-effect and contradictory results. A future statistical release requires tested chain mixing, burn-in, independence analysis, different check bases, independent out-of-sample data and multiple controlled replicates. A future physics release requires independently specified spacetime equations and observations.

## Reproduction
Run `python -m edgewalk --controls --control-samples 16 --control-swaps 16 --control-seed 303` and `python -m unittest discover -s tests -v`. Add `--etq-bundle <generated-v3-directory>` for read-only ETQ with validated original hashes. Do not use synthetic fixture tests as evidence of authentic ETQ integration.

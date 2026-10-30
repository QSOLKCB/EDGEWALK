# EDGEWALK v0.7.2 — Proof-Conformance Bridge

**Purpose:** executable, deterministic, fail-closed differential tests comparing
the existing Python reference behavior with calls to the **actual Ada**
`Edgewalk_Reference` procedures whose source bytes were audited in v0.7.1.

**This is a new runtime test protocol, NOT a new mathematical proof.** The
separate Lean v0.7.0 kernel gate is not marked passed; no entire Python
implementation is proved equivalent to Ada by finite case comparisons.

## Actual implementation, not a mock

- `proofs/spark/conformance/conformance_driver.adb` is a **non-SPARK IO**
  executable that parses bounded decimal test records on stdin, calls
  `Edgewalk_Reference.Address_Of`, `Sequence_Of`, `Parity` and
  `Checked_Step`, and writes actual Ada outputs to stdout.
- `proofs/spark/conformance.gpr` builds the executable independently of the
  proved `edgewalk_spark.gpr`. The original package specification/body are
  **not modified**; the source SHA-256 fingerprints are checked before every
  real run against the archived v0.7.1 proof evidence.
- `proofs/spark/conformance/bridge.py` generates independent Python
  expected outputs, compares each Ada result, and refuses mutated inputs,
  golden output tampering, missing/extra/modified lines, changed Ada sources,
  missing archived GNATprove report, or an invalid result.
- `proofs/spark/conformance/run.sh` stages only the needed source, pinned
  toolchain version checker and actual audited GNATprove report, then runs
  fixture generation, GPRbuild, real Ada driver and Python comparison inside
  a **private offline Bubblewrap sandbox**. The system toolchain is never used
  for compiling this contributor-controlled Ada source.

No network, unreviewed tool downloads, external dependencies, GitHub Actions,
privileged execution, or modifications to the QEC/SONIFICATION upstream.

## Deterministic case matrix

| Case family | Count | Python oracle vs real Ada |
| --- | ---: | --- |
| Address `A n` | 303 | All `0..302` CRT site/fibre, tensor index, phase |
| Inverse `I s f` | 303 | All 101 sites × 3 fibres |
| Parity `P a b` | 1,024 | 32 × 32 declared 23-bit integer word samples including 0, extremes and LCG points |
| Edge controls `E s c forward reverse` | 8,100 | All 45² source/candidate pairs × four directed-edge configurations (includes self/nonedge/one-way) |
| Tanner walk edge calls | 303 | Actual 303 events of Python `run_walk()`, remapped to 45 numbered vertices |
| **Total** | **10,033** | Ordered, byte-for-byte comparison |

The `E` protocol supplies **one forward and reverse adjacency pair per
record**, not a complete graph snapshot. Python's edge oracle is the declared
reciprocal, non-self-loop predicate and the output target rule. For the last
303 records, source/target pairs come from the **real Python Golay Tanner walk**,
and Python independently validates that each pair is reciprocal. The Ada
driver checks the given pair: this is *not* a formal validation of the entire
Tanner graph. An ETQ CRT event is still not an ETQ Cartesian-graph edge.

The parity sample family is not exhaustive over both 23-bit word domains.
The 303/303 address families and all 45²×4 edge flags **are exhaustive
within their declared bounded fixtures**. Every case has an exact decimal
input/output row; no floating point, sampling clocks or uncontrolled entropy.

## Actual run on an independently provisioned Ubuntu host

Install/pin the Alire toolchain according to `proofs/spark/README.md`
(GNAT 16.1.0, GNATprove 16.1.0, GPRbuild Alire 26.0.1 with 26.0.0
executable banner). The archived v0.7.1 GNATprove evidence must exist in the
checkout. Then:

```bash
cd ~/EDGEWALK
python3 -m unittest discover -s tests -v
cd proofs/spark
bash conformance/run.sh
```

The run requires `/usr/bin/bwrap` with working user namespaces and a trusted
preinstalled `~/opt/edgewalk-spark-toolchain` directory. All Ada compilation
and execution occur inside the no-network sandbox; the compiler prefix is
read-only and the real `/home` is not mounted.

On a real successful run, `proofs/spark/conformance-output/` contains:

- `cases.txt`, `python-expected.txt`, `ada-observed.txt`: precise compared
  input and two independent outputs, 10,033 records each
- `receipt.json`: canonical exact comparison schema, deterministic SHA-256
  of those three files, declared counts and explicit limits
- Actual compiler/prover banner captures and executable SHA-256 observations.

The receipt status is **`OUTPUT_MATCH_REVIEW_REQUIRED`**: an editable
receipt alone cannot prove that Ada executed. The runner prints
`SPARK_CONFORMANCE=TESTED` **only after** it compiled and
ran the Ada executable and the Python comparison matched all rows. It
never prints a proof PASS marker. An existing output folder is not overwritten.
Failures emit `UNVERIFIED`, return nonzero and retain any safe intermediate
text outputs for inspection; they cannot produce a success receipt.

The saved receipt can be independently replayed without rerunning Ada:

```bash
python3 conformance/bridge.py verify \\
  --cases conformance-output/cases.txt \\
  --expected conformance-output/python-expected.txt \\
  --actual conformance-output/ada-observed.txt \\
  --receipt conformance-output/receipt.json
```

Replay regenerates Python values and checks the entire receipt including its
domain-separated digest, the archived GNATprove report fingerprint, the
unchanged audited Ada sources, and both Python-core/IO-driver source hashes.
It returns `REPLAY_VERIFIED`, not an Ada or Lean proof certificate.

To rerun, use a fresh output directory:
`bash conformance/run.sh conformance-output-second-run`.

### Local default suite vs real Ada integration

`tests/test_proof_conformance_bridge.py` exercises fixture generation,
source/report pinning, comparison logic, injected mismatches and security
contracts. Its positive comparator test intentionally uses **mocked**
Ada output copied from Python to test the validator. It **is not** a real
conformance result and must never be cited as such. Only the separate offline
Ada driver run yields an authentic differential observation.

## Formal and provenance boundaries

**GNATprove:** v0.7.1's archived source-exact run discharged 48 reported
checks (0 unproved / justified) *for the declared Ada contracts*. The v0.7.2
runner checks source hashes and the audited report fingerprint, but does not
rerun GNATprove. Neither the non-SPARK IO driver nor the Python code acquires
Ada's formal proof status. Notably the existing parity postcondition asserts
only the zero-input property; 1,024 correct observed parity pairs do not
strengthen that formal contract.

**Lean:** v0.7.0 has no independently supplied kernel-check transcript.
This bridge cannot change its status.

**Supply chain:** toolchain version banners and executable hashes are
observational provenance. Alire vendor archive authentication remains a
separate independently reviewed requirement.

**Physics:** these finite software comparisons do not test spacetime,
dark energy, dark matter or an observational physical mechanism.

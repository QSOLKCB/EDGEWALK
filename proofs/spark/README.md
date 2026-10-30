# EDGEWALK v0.7.1 — SPARK Ada reference kernel

**Status:** candidate reference implementation; GNATprove verification **NOT RUN**
in this development environment. No statement of Ada-contract proof success is
made merely because source code or a runtime self-test exists.

## Scope (intentionally narrower than Python EDGEWALK)

The SPARK-mode package `Edgewalk_Reference` in `src/` implements:

1. **ETQ addressing:** `Sequence_Index = 0..302`, `Site_Index = 0..100`,
   `Fibre_Index = 0..2`; total address mapping, inverse CRT mapping,
   tensor index `3*site+fibre`, and fibre-dependent phase exponents (3,2,3).
2. **GF(2) parity:** parity of the bitwise AND of two 23-bit words, computed
   by an exactly bounded 23-iteration shift loop. No general GF(2) rank,
   stabilizer distance or error-correction proof is claimed.
3. **Checked edge transitions:** fixed 45-vertex adjacency matrix
   (qubits 0..22, X checks 23..33, Z checks 34..44 by convention).
   Only reciprocal, non-self-loop edges are accepted; a rejected candidate
   returns the unchanged source vertex. The package does not assert that a
   caller's graph is a particular Tanner graph or CSS code.

All operations use bounded integer/modular types. The package spec declares
postconditions and a `Depends` contract. It contains no file IO, network
access, floating-point heuristics, Python bindings or third-party runtime.

## Declared toolchain versions (Alire registry coordinates)

`toolchain-lock.json` declares:

- GNAT native `16.1.0`
- GNATprove `16.1.0`
- GPRbuild `26.0.1`
- Linux x86-64 target

This lock lists **versions only**; it does not contain verified release
archive SHA-256 values and does not itself attest source or tool provenance.
Provision independently in a clean, disposable Linux container/VM using a
trusted Alire index and verify downloaded archives. No automatic downloads,
updates, or unsigned installations occur in EDGEWALK runtime. The verification
script checks the installed command version strings and writes authentic
version captures to `evidence/`.

## Local commands — run INSIDE an isolated offline development environment

```sh
cd proofs/spark
bash scripts/verify.sh
```

The script requires the pre-provisioned versioned toolchain, executes
`gprbuild -P reference_tests.gpr -p` to compile a **non-SPARK IO self-test**
and runs exhaustive CRT round trips and negative edge tests. It invokes
`gnatprove -P edgewalk_spark.gpr --mode=all --level=2 --report=all
--output-header --proof-warnings=on -j1`, preserving the original output
and exit code in `evidence/`.

`scripts/assess_proof.py` reads the original
`obj/gnatprove/gnatprove.out` report, classifies absent/empty/unknown
summaries as UNVERIFIED, and records total, justified, and unproved check
counts with unresolved obligations. Even if the report claims zero unproved
and justified checks, its status is **REVIEW_REQUIRED**, not a fabricated
verified proof. A reviewer must inspect the genuine invocation header,
coverage of both source files, source/tool hashes, contract consistency
and proof transcript before claiming a proof is discharged.

**Important:** The project `edgewalk_spark.gpr` includes only the two
SPARK source files. The separate `reference_tests.gpr` includes the
Ada.Text_IO runtime harness but is never included in the GNATprove proof
project. Both must pass for separate runtime and proof assertions.

## Mandatory release gates

- Full Python suite in a real checkout (standard library only).
- GNAT/GPRbuild compilation, 303×CRT round trips and self-test.
- Actual GNATprove run and reviewed report for each declared contract, with
  any unproved or justified obligations disclosed.
- Independently reviewed toolchain versions/archive digests and source SHA.
- No automatic equivalence claim about existing Python implementation.
- Lean v0.7.0 kernel proof status is independent; Ada postconditions do not
  transfer Lean theorems into Python automatically.
- No GitHub Actions and no changes to upstream SONIFICATION or QEC.

The next v0.7.2 milestone may add canonical differential comparison cases,
but must not label tested Python conformance a formal Python proof.


## Isolated Alire 2.1.1 toolchain prefix

The verifier now accepts the Alire installation at `$HOME/opt/edgewalk-spark-toolchain`.
It can accept another direct child of `$HOME/opt` using the environment variable:

```bash
export EDGEWALK_SPARK_TOOLCHAIN="$HOME/opt/edgewalk-spark-toolchain"
cd proofs/spark
bash scripts/verify.sh
```

It mounts only the configured toolchain tree, read-only at its original absolute
path. The rest of `/home` is a new, private tmpfs, and the verifier never
copies compiler executables into `/usr`. The full Alire prefix remains present
for GNATprove's `libexec/spark` helpers and relative resources.

The installed `bin/gnatmake`, `bin/gprbuild`, and `bin/gnatprove` must resolve
inside the approved prefix; the sandbox uses those executables, not Ubuntu's
older system compiler. Tool versions and SHA-256 fingerprints are captured
in evidence. A recorded digest is **not** vendor authentication.

Missing sandbox, tooling, exact versions or proof evidence means NOT_RUN or
UNVERIFIED. GNATprove results remain REVIEW_REQUIRED pending human audit.
No `sudo`, symlinks into `/usr`, source changes or GitHub Actions are needed.


## Alire crate release vs executable banner (2026-10-30)

Alire's `gprbuild=26.0.1` package reports
`GPRBUILD 26.0.0 (2026-04-15) (x86_64-pc-linux-gnu)` when its
executable is queried with `--version`. These are distinct identifiers.
Never weaken the release pin to `26.0.0` or accept a matching substring
somewhere in stdout. `toolchain-lock.json` records both the exact pinned
Alire `crateVersions` and the observed, explicitly approved
`reportedExecutableVersions` for GNATMAKE, GPRBUILD and GNATprove.

Inside the offline Bubblewrap execution,
`scripts/check_toolchain.py` checks that the lock retains approved crate
versions and that the FIRST LINE of each actual executable capture
starts with its correct full banner followed by whitespace/end-of-line.
Missing, altered, or misleading version output fails before Ada build.
Executable SHA-256 and vendor archive provenance are recorded separately;
a passing banner test does not certify origin or Ada proof obligations.

The pre-existing `test_physical_model_and_report_replay` was also adjusted
to submit canonically serialized tampered JSON. Noncanonical input continues
to fail at the CLI parser; canonical tampering must produce verified=false.

After merging this patch, rerun from a fresh `main` checkout:

```bash
cd ~/EDGEWALK
python3 -m unittest discover -s tests -v
cd proofs/spark
bash scripts/verify.sh
```

Do not treat an absence of `SPARK_STATUS=UNVERIFIED` as proof discharge.
Review the actual GNATprove transcript and all remaining obligations.

## GNAT 16.1.0 warning-as-error in parity loop (PR #10 follow-up)

The first authentic isolated GPRbuild run reached the Ada compiler after all
74 Python tests and pinned toolchain banners passed, but `-gnatwe` correctly
treated a warning about `Result_Bit in Bit` (redundant subtype membership)
as a build failure. The reference no longer uses that tautological check
or the redundant `Remaining <= Word_23'Last` loop invariant. Instead the
loop carries the zero-input postcondition explicitly: if either operand is
zero, the remaining word and parity accumulator must stay zero.

The compiler warning is a source issue, **not** proof that a GNATprove
verification condition failed. The corrected Ada source and Python
regression were committed, but must be recompiled inside the offline
sandbox; successful compilation and even a runtime self-test are separate
from independently reviewed SPARK proof obligations.

#!/usr/bin/env bash
# Invoke only inside a disposable, unprivileged OFFLINE VM/container.
# Compilation alone or a GNATprove exit code is never a verified proof receipt.
set -euo pipefail
cd "$(dirname "$0")/.."
for executable in gprbuild gnatprove gnatmake python3; do
  command -v "$executable" >/dev/null || {
    echo "SPARK_STATUS=NOT_RUN: missing $executable" >&2
    exit 2
  }
done

# Preserve the authentic tool outputs; do not invent a passing report.
mkdir -p evidence
gnatmake --version > evidence/gnat-version.txt
gprbuild --version > evidence/gprbuild-version.txt
gnatprove --version > evidence/gnatprove-version.txt
python3 - <<'PY'
import json
from pathlib import Path
v = json.loads(Path("toolchain-lock.json").read_text())["crateVersions"]
for name, filename in (("gnat_native", "gnat-version.txt"),
                       ("gprbuild", "gprbuild-version.txt"),
                       ("gnatprove", "gnatprove-version.txt")):
    output = (Path("evidence") / filename).read_text()
    if v[name] not in output:
        raise SystemExit("UNVERIFIED: toolchain version mismatch: " + name)
PY

# The test harness is separate from SPARK proof scope; the SPARK project
# only enumerates the two package sources, never the I/O-enabled self-test.
gprbuild -P reference_tests.gpr -p
./bin/reference_selftest > evidence/ada-selftest.txt

set +e
gnatprove -P edgewalk_spark.gpr --mode=all --level=2 --report=all   --output-header --proof-warnings=on -j1   > evidence/gnatprove-run.txt 2>&1
proof_exit=$?
set -e
echo "$proof_exit" > evidence/gnatprove-exit.txt

if [[ -f obj/gnatprove/gnatprove.out ]]; then
  python3 scripts/assess_proof.py obj/gnatprove/gnatprove.out     --out evidence/gnatprove-assessment.json
else
  echo "SPARK_STATUS=UNVERIFIED: GNATprove report missing" >&2
  exit 1
fi
if [[ "$proof_exit" -ne 0 ]]; then
  echo "SPARK_STATUS=UNVERIFIED: GNATprove failed" >&2
  exit 1
fi
echo "SPARK_STATUS=REVIEW_REQUIRED: never claim proof PASS from this script alone"

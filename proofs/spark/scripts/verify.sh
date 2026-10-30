#!/usr/bin/env bash
# All contributor-controlled GPR/Ada compilation and GNATprove execution occur
# ONLY in a temporary offline bubblewrap sandbox with no host HOME or tokens.
set -euo pipefail
cd "$(dirname "$0")/.."

if [[ ! -x /usr/bin/bwrap ]]; then
  echo "SPARK_STATUS=NOT_RUN: trusted /usr/bin/bwrap required" >&2
  exit 2
fi
for exe in gprbuild gnatprove gnatmake python3; do
  path="$(command -v "$exe" || true)"
  if [[ -z "$path" || "$(realpath "$path")" != /usr/* ]]; then
    echo "SPARK_STATUS=NOT_RUN: $exe must be preinstalled under /usr for offline sandbox" >&2
    exit 2
  fi
done

scratch="$(mktemp -d)"
trap 'rm -rf -- "$scratch"' EXIT
mkdir -p "$scratch/work"
cp -a -- src tests scripts *.gpr toolchain-lock.json "$scratch/work/"
mounts=()
for dir in /lib /lib64 /bin; do
  if [[ -d "$dir" ]]; then
    mounts+=(--ro-bind "$dir" "$dir")
  fi
done

# Never mount real /home, /root, /run, /mnt, SSH agent or Docker socket.
set +e
/usr/bin/bwrap --unshare-all --die-with-parent --new-session --clearenv \
  --ro-bind /usr /usr "${mounts[@]}" \
  --dir /work --bind "$scratch/work" /work \
  --tmpfs /tmp --tmpfs /home --tmpfs /root --proc /proc --dev /dev \
  --setenv HOME /home --setenv PATH /usr/local/bin:/usr/bin:/bin \
  --setenv GIT_CONFIG_NOSYSTEM 1 --setenv GIT_CONFIG_GLOBAL /dev/null \
  --chdir /work /usr/bin/bash -euc '
    for executable in gprbuild gnatprove gnatmake python3; do
      command -v "$executable" >/dev/null || exit 2
    done
    mkdir -p evidence
    gnatmake --version > evidence/gnat-version.txt
    gprbuild --version > evidence/gprbuild-version.txt
    gnatprove --version > evidence/gnatprove-version.txt
    python3 - <<PY
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
    gprbuild -P reference_tests.gpr -p
    ./bin/reference_selftest > evidence/ada-selftest.txt
    set +e
    gnatprove -P edgewalk_spark.gpr --mode=all --level=2 --report=all \
      --output-header --proof-warnings=on -j1 \
      > evidence/gnatprove-run.txt 2>&1
    proof_exit=$?
    set -e
    echo "$proof_exit" > evidence/gnatprove-exit.txt
    if [[ -f obj/gnatprove/gnatprove.out ]]; then
      cp obj/gnatprove/gnatprove.out evidence/gnatprove.out
      python3 scripts/assess_proof.py evidence/gnatprove.out \
        --out evidence/gnatprove-assessment.json
    else
      echo "SPARK_STATUS=UNVERIFIED: GNATprove report absent" >&2
      exit 1
    fi
    if [[ "$proof_exit" -ne 0 ]]; then
      echo "SPARK_STATUS=UNVERIFIED: GNATprove failed" >&2
      exit 1
    fi
    echo "SPARK_STATUS=REVIEW_REQUIRED: no automatic proof certification"
  '
sandbox_exit=$?
set -e

# Persist only well-defined inert text evidence, never sandbox-created code.
mkdir -p evidence
for name in gnat-version.txt gprbuild-version.txt gnatprove-version.txt \
            ada-selftest.txt gnatprove-run.txt gnatprove-exit.txt \
            gnatprove.out gnatprove-assessment.json; do
  candidate="$scratch/work/evidence/$name"
  if [[ -f "$candidate" && ! -L "$candidate" ]]; then
    cp -- "$candidate" "evidence/$name"
  fi
done
if [[ "$sandbox_exit" -ne 0 ]]; then
  echo "SPARK_STATUS=UNVERIFIED: isolated compile/proof process failed (exit $sandbox_exit)" >&2
  exit "$sandbox_exit"
fi
echo "SPARK_STATUS=REVIEW_REQUIRED: proof evidence retained for independent audit"

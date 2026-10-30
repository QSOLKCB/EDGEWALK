#!/usr/bin/env bash
# All contributor-controlled GPR/Ada compilation and GNATprove execution occur
# ONLY in a temporary, offline bubblewrap sandbox. Alire's original installation
# path is mounted READ ONLY; the reviewer's remaining HOME is not accessible.
set -euo pipefail
cd "$(dirname "$0")/.."

if [[ ! -x /usr/bin/bwrap ]]; then
  echo "SPARK_STATUS=NOT_RUN: trusted /usr/bin/bwrap required" >&2
  exit 2
fi

# Accept one direct child of ~/opt, including ~/opt/edgewalk-spark-toolchain.
# Keeping the original absolute path accommodates Alire's helper/runtime paths.
# Do not install anything or run compiler code during this host-side preflight.
home_real="$(realpath -e -- "$HOME")"
if [[ "$home_real" != /home/* || "$home_real" == /home/*/* ]]; then
  echo "SPARK_STATUS=NOT_RUN: expected /home/USER layout" >&2
  exit 2
fi
opt_real="$(realpath -e -- "$home_real/opt" 2>/dev/null || true)"
requested="${EDGEWALK_SPARK_TOOLCHAIN:-$home_real/opt/edgewalk-spark-toolchain}"
toolchain_dir="$(realpath -e -- "$requested" 2>/dev/null || true)"
if [[ -z "$opt_real" || -z "$toolchain_dir" ||
      "$(dirname -- "$toolchain_dir")" != "$opt_real" ||
      ! -d "$toolchain_dir" ]]; then
  echo "SPARK_STATUS=NOT_RUN: toolchain must be under ~/opt/<name>" >&2
  exit 2
fi

# Refuse symlinks that resolve outside the approved read-only tree.
for exe in gnatmake gprbuild gnatprove; do
  candidate="$toolchain_dir/bin/$exe"
  resolved="$(realpath -e -- "$candidate" 2>/dev/null || true)"
  if [[ ! -x "$candidate" || "$resolved" != "$toolchain_dir/"* ]]; then
    echo "SPARK_STATUS=NOT_RUN: invalid isolated tool path: $exe" >&2
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

# /home is a fresh tmpfs. Only this one prefix is bound back, read-only.
# No original reviewer HOME, SSH agent, cloud tokens or network are exposed.
set +e
/usr/bin/bwrap --unshare-all --die-with-parent --new-session --clearenv \
  --ro-bind /usr /usr "${mounts[@]}" \
  --tmpfs /home --dir "$home_real" --dir "$opt_real" \
  --ro-bind "$toolchain_dir" "$toolchain_dir" \
  --dir /work --bind "$scratch/work" /work \
  --tmpfs /tmp --tmpfs /root --tmpfs /sandbox-home --proc /proc --dev /dev \
  --setenv HOME /sandbox-home \
  --setenv EDGEWALK_SPARK_TOOLCHAIN "$toolchain_dir" \
  --setenv PATH "$toolchain_dir/bin:$toolchain_dir/libexec/spark/bin:/usr/bin:/bin" \
  --setenv GIT_CONFIG_NOSYSTEM 1 --setenv GIT_CONFIG_GLOBAL /dev/null \
  --chdir /work /usr/bin/bash -euc '
    for exe in gnatmake gprbuild gnatprove; do
      actual="$(command -v "$exe" || true)"
      if [[ "$actual" != "$EDGEWALK_SPARK_TOOLCHAIN/bin/$exe" ]]; then
        echo "SPARK_STATUS=UNVERIFIED: unexpected $exe at $actual" >&2
        exit 2
      fi
    done
    mkdir -p evidence
    sha256sum "$EDGEWALK_SPARK_TOOLCHAIN/bin/gnatmake" \
              "$EDGEWALK_SPARK_TOOLCHAIN/bin/gprbuild" \
              "$EDGEWALK_SPARK_TOOLCHAIN/bin/gnatprove" \
              > evidence/toolchain-executable-sha256.txt
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

# Preserve only fixed-name inert log files, including partial failure evidence.
mkdir -p evidence
for name in gnat-version.txt gprbuild-version.txt gnatprove-version.txt \
            toolchain-executable-sha256.txt \
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

#!/usr/bin/env bash
# v0.7.2: compile and execute contributor Ada ONLY in an offline bwrap
# sandbox. The source is the exact v0.7.1 proved Ada package. This is
# executable cross-language testing, NOT a GNATprove or Lean proof.
set -euo pipefail
cd "$(dirname "$0")/.."

if [[ ! -x /usr/bin/bwrap ]]; then
  echo "SPARK_CONFORMANCE=NOT_RUN: trusted /usr/bin/bwrap is required" >&2
  exit 2
fi
home_real="$(realpath -e -- "$HOME")"
opt_real="$(realpath -e -- "$home_real/opt" 2>/dev/null || true)"
requested="${EDGEWALK_SPARK_TOOLCHAIN:-$home_real/opt/edgewalk-spark-toolchain}"
toolchain_dir="$(realpath -e -- "$requested" 2>/dev/null || true)"
if [[ "$home_real" != /home/* || "$home_real" == /home/*/* ||
      -z "$opt_real" || -z "$toolchain_dir" ||
      "$(dirname -- "$toolchain_dir")" != "$opt_real" ||
      ! -d "$toolchain_dir" ]]; then
  echo "SPARK_CONFORMANCE=NOT_RUN: isolated Alire toolchain must be in ~/opt/<name>" >&2
  exit 2
fi
for exe in gnatmake gprbuild gnatprove; do
  candidate="$toolchain_dir/bin/$exe"
  resolved="$(realpath -e -- "$candidate" 2>/dev/null || true)"
  if [[ ! -x "$candidate" || "$resolved" != "$toolchain_dir/"* ]]; then
    echo "SPARK_CONFORMANCE=NOT_RUN: toolchain executable invalid: $exe" >&2
    exit 2
  fi
done

out="${1:-conformance-output}"
if [[ -e "$out" || -L "$out" ]]; then
  echo "SPARK_CONFORMANCE=NOT_RUN: output directory already exists: $out" >&2
  exit 2
fi
scratch="$(mktemp -d)"
trap 'rm -rf -- "$scratch"' EXIT
mkdir -p "$scratch/work" "$scratch/work/edgewalk" "$scratch/work/audit"
cp -a -- src conformance conformance.gpr toolchain-lock.json "$scratch/work/"
cp -- scripts/check_toolchain.py "$scratch/work/conformance/check_toolchain.py"
cp -- ../../edgewalk/core.py ../../edgewalk/__init__.py "$scratch/work/edgewalk/"
cp -- audits/2026-10-30-6a8c0c7/original/gnatprove.out "$scratch/work/audit/gnatprove.out"

mounts=()
for dir in /lib /lib64 /bin; do
  if [[ -d "$dir" ]]; then
    mounts+=(--ro-bind "$dir" "$dir")
  fi
done

set +e
/usr/bin/bwrap --unshare-all --die-with-parent --new-session --clearenv \
  --ro-bind /usr /usr "${mounts[@]}" \
  --tmpfs /home --dir "$home_real" --dir "$opt_real" \
  --ro-bind "$toolchain_dir" "$toolchain_dir" \
  --dir /work --bind "$scratch/work" /work \
  --tmpfs /tmp --tmpfs /root --tmpfs /sandbox-home --proc /proc --dev /dev \
  --setenv HOME /sandbox-home --setenv PYTHONPATH /work \
  --setenv EDGEWALK_SPARK_TOOLCHAIN "$toolchain_dir" \
  --setenv PATH "$toolchain_dir/bin:$toolchain_dir/libexec/spark/bin:/usr/bin:/bin" \
  --setenv GIT_CONFIG_NOSYSTEM 1 --setenv GIT_CONFIG_GLOBAL /dev/null \
  --chdir /work /usr/bin/bash -euc '
    for exe in gnatmake gprbuild gnatprove; do
      actual="$(command -v "$exe" || true)"
      if [[ "$actual" != "$EDGEWALK_SPARK_TOOLCHAIN/bin/$exe" ]]; then
        echo "SPARK_CONFORMANCE=UNVERIFIED: wrong compiler path" >&2
        exit 2
      fi
    done
    mkdir -p results
    gnatmake --version > results/gnat-version.txt
    gprbuild --version > results/gprbuild-version.txt
    gnatprove --version > results/gnatprove-version.txt
    python3 conformance/check_toolchain.py \
      --lock toolchain-lock.json \
      --gnat results/gnat-version.txt \
      --gprbuild results/gprbuild-version.txt \
      --gnatprove results/gnatprove-version.txt
    sha256sum "$EDGEWALK_SPARK_TOOLCHAIN/bin/gnatmake" \
              "$EDGEWALK_SPARK_TOOLCHAIN/bin/gprbuild" \
              "$EDGEWALK_SPARK_TOOLCHAIN/bin/gnatprove" \
              > results/toolchain-sha256.txt
    python3 conformance/bridge.py generate \
      --cases results/cases.txt --expected results/python-expected.txt
    gprbuild -P conformance.gpr -p
    # Exercise the real Ada input gate as negative controls too: invalid
    # opcodes, out-of-domain input, overflow and extra fields must fail.
    for bad in "X 0" "A 303" "I 101 0" "P 8388608 0" \
               "E 0 45 1 1" "E 0 1 1 1 1"; do
      if printf "%s\n" "$bad" | ./bin/conformance_driver > /dev/null 2>&1; then
        echo "SPARK_CONFORMANCE=UNVERIFIED: Ada accepted bad record: $bad" >&2
        exit 1
      fi
    done
    ./bin/conformance_driver < results/cases.txt > results/ada-observed.txt
    python3 conformance/bridge.py compare \
      --cases results/cases.txt --expected results/python-expected.txt \
      --actual results/ada-observed.txt --receipt results/receipt.json
    echo "SPARK_CONFORMANCE=TESTED: compiled Ada output matches independent Python cases"
  '
sandbox_exit=$?
set -e

# Only inert test output; never binaries or compiler-built artifacts.
mkdir -- "$out"
for name in cases.txt python-expected.txt ada-observed.txt receipt.json \
            gnat-version.txt gprbuild-version.txt gnatprove-version.txt \
            toolchain-sha256.txt; do
  candidate="$scratch/work/results/$name"
  if [[ -f "$candidate" && ! -L "$candidate" ]]; then
    cp -- "$candidate" "$out/$name"
  fi
done
if [[ "$sandbox_exit" -ne 0 || ! -f "$out/receipt.json" ]]; then
  echo "SPARK_CONFORMANCE=UNVERIFIED: differential runner failed (exit $sandbox_exit)" >&2
  exit 1
fi
echo "SPARK_CONFORMANCE=TESTED: immutable outputs retained at $out"

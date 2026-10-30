#!/usr/bin/env bash
# Proof-source audit, every Lake build, and paranoid checks run ONLY inside
# an unprivileged offline bubblewrap sandbox. No host elaboration.
set -euo pipefail
cd "$(dirname "$0")/.."

if [[ ! -x /usr/bin/bwrap ]]; then
  echo "UNVERIFIED: trusted /usr/bin/bwrap is required" >&2
  exit 2
fi
command -v elan >/dev/null || { echo "UNVERIFIED: elan unavailable" >&2; exit 2; }
command -v realpath >/dev/null || { echo "UNVERIFIED: realpath unavailable" >&2; exit 2; }

# Elan path resolution does not execute any contributor Lean source.
LEAN_BIN="$(realpath "$(elan which lean)")"
LAKE_BIN="$(realpath "$(elan which lake)")"
TOOLCHAIN_ROOT="$(dirname "$(dirname "$LEAN_BIN")")"
if [[ "$LEAN_BIN" != "$TOOLCHAIN_ROOT/bin/lean" ||
      "$LAKE_BIN" != "$TOOLCHAIN_ROOT/bin/lake" ||
      ! -x "$LEAN_BIN" || ! -x "$LAKE_BIN" ]]; then
  echo "UNVERIFIED: unexpected or unavailable Lean/Lake toolchain layout" >&2
  exit 2
fi

# Private writable copy. Never elaborate in the reviewer's live checkout.
sandbox="$(mktemp -d)"
trap 'rm -rf -- "$sandbox"' EXIT
mkdir -p "$sandbox/work"
cp -a -- . "$sandbox/work/"

# No host HOME, credentials, /mnt, /root, /tmp, /run or socket mounts.
# --unshare-all also disconnects the network. Dependency provisioning must
# happen separately from verified trusted source material.
mounts=()
for path in /usr /bin /lib /lib64; do
  if [[ -d "$path" ]]; then
    mounts+=(--ro-bind "$path" "$path")
  fi
done

/usr/bin/bwrap \
  --unshare-all --die-with-parent --new-session --clearenv \
  --ro-bind "$TOOLCHAIN_ROOT" /toolchain \
  "${mounts[@]}" \
  --dir /work --bind "$sandbox/work" /work \
  --tmpfs /sandbox-home --tmpfs /tmp --proc /proc --dev /dev \
  --setenv HOME /sandbox-home \
  --setenv XDG_CACHE_HOME /sandbox-home/.cache \
  --setenv PATH /toolchain/bin:/usr/bin:/bin \
  --setenv GIT_CONFIG_NOSYSTEM 1 \
  --setenv GIT_CONFIG_GLOBAL /dev/null \
  --chdir /work \
  /usr/bin/bash -euc '
    python3 scripts/static_audit.py
    if [[ ! -f lake-manifest.json || ! -d .lake/packages/mathlib ]]; then
      echo "UNVERIFIED: reviewed lake-manifest.json and offline Mathlib required" >&2
      exit 2
    fi
    actual="$(lean --version)"
    if [[ "$actual" != "Lean (version 4.35.0"* ]]; then
      echo "UNVERIFIED: unexpected Lean version: $actual" >&2
      exit 2
    fi
    for module in Edgewalk.CRT Edgewalk.Phase Edgewalk.Monomial Edgewalk.GF2 Edgewalk; do
      echo "SANDBOXED_VERIFY_MODULE=$module"
      lake build "$module"
    done
    lake check --paranoid
    echo "KERNEL_CHECKED=PASS (sandboxed, all proof modules, paranoid check)"
  '

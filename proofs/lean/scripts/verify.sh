#!/usr/bin/env bash
# Explicit, local verification only. This script never forges a proof receipt.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 scripts/static_audit.py
command -v lean >/dev/null || { echo "UNVERIFIED: Lean unavailable" >&2; exit 2; }
command -v lake >/dev/null || { echo "UNVERIFIED: Lake unavailable" >&2; exit 2; }
command -v bwrap >/dev/null || { echo "UNVERIFIED: bubblewrap required for lake check sandbox" >&2; exit 2; }

EXPECTED="Lean (version 4.35.0"
ACTUAL="$(lean --version)"
if [[ "$ACTUAL" != "$EXPECTED"* ]]; then
  echo "UNVERIFIED: unexpected Lean toolchain: $ACTUAL" >&2
  exit 2
fi

# Explicit dependency resolution; the project pins Mathlib to a commit.
# Keep the generated lake-manifest.json as a reviewed release artifact.
lake update
lake exe cache get
lake build
lake check --paranoid
echo "KERNEL_CHECKED=PASS (Lean and bundled independent checkers)"

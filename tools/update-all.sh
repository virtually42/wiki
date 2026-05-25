#!/usr/bin/env bash
set -euo pipefail

root="/p/hg"

for dir in "$root"/*/; do
  if [ -d "$dir/.git" ]; then
    echo "==> Updating $(basename "$dir")"
    git -C "$dir" fetch && git -C "$dir" pull --rebase
    echo ""
  fi
done

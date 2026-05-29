#!/usr/bin/env bash
# Apply all WIP-process proposals to human-owned wiki pages.
# Idempotent — safe to re-run.
set -euo pipefail

cd "$(dirname "$0")"

echo "== ownership.md =="
python3 apply-wip-ownership.py
echo
echo "== schema.md =="
python3 apply-wip-schema.py
echo
echo "== POLICY.md =="
python3 apply-wip-policy.py
echo
echo "Done. Review:  git -C /p/wiki diff meta/ POLICY.md"

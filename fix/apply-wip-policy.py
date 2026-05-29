#!/usr/bin/env python3
"""Apply WIP proposal to POLICY.md. Idempotent.

Adds `session` page kind to the Page Kinds table and a freshness-check note.
"""
from pathlib import Path

PATH = Path("/p/wiki/POLICY.md")
text = PATH.read_text()

KIND_ROW = "| `session`     | `projects/*/wip.md`, top-level `wip.md`             | Session-bound handoff state. Overwritten each session. No compliance obligation. |"
KIND_ANCHOR = "| `stub`        | anywhere                                            | Placeholder. Lint surfaces these until filled in.          |"

FRESHNESS_OLD = "Normative pages are the only ones drift checks operate on. Descriptive pages get freshness and contradiction checks but no compliance enforcement."
FRESHNESS_NEW = FRESHNESS_OLD + " Session pages get freshness checks only — stale `wip.md` files surface in drift."


def insert_before(haystack: str, anchor: str, addition: str) -> tuple[str, bool]:
    if addition in haystack:
        return haystack, False
    if anchor not in haystack:
        raise SystemExit(f"anchor not found: {anchor[:60]}...")
    return haystack.replace(anchor, addition + "\n" + anchor, 1), True


def replace_once(haystack: str, old: str, new: str, label: str) -> tuple[str, bool]:
    if new in haystack and old not in haystack:
        return haystack, False
    if old not in haystack:
        raise SystemExit(f"{label}: anchor not found")
    return haystack.replace(old, new, 1), True


text, c1 = insert_before(text, KIND_ANCHOR, KIND_ROW)
text, c2 = replace_once(text, FRESHNESS_OLD, FRESHNESS_NEW, "freshness sentence")

PATH.write_text(text)
print(f"POLICY.md: kind-row={'added' if c1 else 'skip'}, "
      f"freshness={'updated' if c2 else 'skip'}")

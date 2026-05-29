#!/usr/bin/env python3
"""Apply WIP proposal to meta/schema.md. Idempotent."""
from pathlib import Path

PATH = Path("/p/wiki/meta/schema.md")
text = PATH.read_text()

CATALOG_ROW = "| wip | session | projects/\\*/wip.md or top-level wip.md | Rolling work-in-progress handoff for clean-session resumption |"
CATALOG_ANCHOR = "| log-entry | project | projects/\\*/log.md | Append-only session record (not a standalone file) |"

WIP_SECTION = '''### wip

Session handoff state. Single rolling file — overwritten each `wip` invocation.
History belongs in `log.md`, not here. One per project at `projects/<name>/wip.md`,
plus a top-level `wip.md` for cross-cutting work.

```yaml
---
id: wip-<project-or-cross-cutting>
title: WIP — <short goal>
kind: session
status: active | paused | abandoned
project: <name> | null
created: YYYY-MM-DD
updated: YYYY-MM-DD
branch: <git-branch>
related: []                        # tickets, plans, design docs
---

## Goal
What we are trying to accomplish.

## Status
Where we are right now. One paragraph.

## Files Touched
Files modified this session and why. Include uncommitted vs. committed.

## Decisions
Choices made this session, with reasoning.

## Blockers
Open questions, failing tests, missing inputs. Empty if none.

## Next Step
The single concrete next action. Phrased so a clean session can act on it
without rereading the prior conversation.

## Resume Instructions
Commands or pages to read first. Frame as: "Read X, then Y, then run Z."
```

'''

SECTION_NEXT = "### code-source\n"

KIND_OLD = "kind: normative | descriptive | stub"
KIND_NEW = "kind: normative | descriptive | stub | session"


def replace_once(haystack: str, old: str, new: str, label: str) -> tuple[str, bool]:
    if new in haystack and old not in haystack:
        return haystack, False
    if old not in haystack:
        raise SystemExit(f"{label}: anchor not found")
    return haystack.replace(old, new, 1), True


if CATALOG_ROW in text:
    c1 = False
else:
    if CATALOG_ANCHOR not in text:
        raise SystemExit("catalog anchor not found")
    text = text.replace(CATALOG_ANCHOR, CATALOG_ANCHOR + "\n" + CATALOG_ROW, 1)
    c1 = True

if "### wip\n" in text:
    c2 = False
else:
    if SECTION_NEXT not in text:
        raise SystemExit("section insertion anchor not found")
    text = text.replace(SECTION_NEXT, WIP_SECTION + SECTION_NEXT, 1)
    c2 = True

text, c3 = replace_once(text, KIND_OLD, KIND_NEW, "kind line")

PATH.write_text(text)
print(f"schema.md: catalog={'added' if c1 else 'skip'}, "
      f"section={'added' if c2 else 'skip'}, "
      f"kind={'updated' if c3 else 'skip'}")

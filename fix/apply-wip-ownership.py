#!/usr/bin/env python3
"""Apply WIP proposal to meta/ownership.md. Idempotent."""
from pathlib import Path

PATH = Path("/p/wiki/meta/ownership.md")
text = PATH.read_text()

ROW_TOP   = "| `wip.md`                      | llm       | no        |"
ROW_PROJ  = "| `projects/*/wip.md`           | llm       | no        |"
BULLET    = "- **wip.md (top-level and projects/*/wip.md) is llm**: session handoff state, overwritten each session. Like `log.md`, hand-edits will be lost on next `wip` invocation."

ANCHOR_TOP    = "| `index.md`                    | llm       | no        |"
ANCHOR_PROJ   = "| `projects/*/log.md`           | llm       | no        |"
ANCHOR_BULLET = "- **scratch/ is human**: personal working notes. Agent reads if asked, never writes, lint never enforces — outside the schema by design."


def insert_after(haystack: str, anchor: str, addition: str) -> tuple[str, bool]:
    if addition in haystack:
        return haystack, False
    if anchor not in haystack:
        raise SystemExit(f"anchor not found: {anchor[:60]}...")
    return haystack.replace(anchor, anchor + "\n" + addition, 1), True


text, c1 = insert_after(text, ANCHOR_TOP, ROW_TOP)
text, c2 = insert_after(text, ANCHOR_PROJ, ROW_PROJ)
text, c3 = insert_after(text, ANCHOR_BULLET, BULLET)

PATH.write_text(text)
print(f"ownership.md: wip-top={'added' if c1 else 'skip'}, "
      f"wip-proj={'added' if c2 else 'skip'}, "
      f"bullet={'added' if c3 else 'skip'}")

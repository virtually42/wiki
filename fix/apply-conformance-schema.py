#!/usr/bin/env python3
"""
Apply conformance-operation proposals to human-owned wiki files.

Targets:
  1. meta/schema.md — insert `## Conformance Block` section before
     the Promotion Metadata section.
  2. meta/ownership.md — add two rows to the defaults table:
       - meta/conformance.md (llm)
       - projects/*/adr/drafts/** (llm)

Idempotent: re-runs print `skip` for already-applied chunks.

See tech/guides/conformance.md for context.
"""

from pathlib import Path
import sys

WIKI = Path("/p/wiki")
SCHEMA = WIKI / "meta/schema.md"
OWNERSHIP = WIKI / "meta/ownership.md"


CONFORMANCE_BLOCK_MARKER = "## Conformance Block"

CONFORMANCE_BLOCK_SECTION = '''## Conformance Block

Normative pages (`tech/decisions/`, `tech/patterns/`, anti-patterns)
may carry an optional `## Conformance` section consumed by the
`conform` operation. Pages without one are skipped and surfaced as
"no fingerprint" in `meta/conformance.md`.

```yaml
## Conformance

verifiability: high | medium | low
verifiability_rationale: |
  One paragraph explaining what can and can't be mechanically
  verified for this pattern, and why.

hard_signals:
  - id: <kebab-id>                     # stable, unique within the page
    name: <one-line description>
    method: grep | ast | metric | shell
    # method-specific fields:
    pattern: <regex>                   # for method: grep
    rule: <ruleName>                   # for method: ast (Scalafix)
    config: { ... }                    # for method: ast
    measure: <name>                    # for method: metric
    threshold: { op: gte|lte|eq, value: <n> }   # for method: metric
    script: <path>                     # for method: shell — under tools/conformance/<pattern-id>/
    # common fields:
    scope: <glob>                      # default: project root
    verdict_on_match: violation | evidence
    rationale: <one-line why>

soft_signals:
  - id: <kebab-id>
    name: <one-line description>
    prompt: |
      Instructions for the evaluator. Should describe what evidence
      to look for and how to decide between verdict kinds.
    verdict_kinds: [present, partial, absent, unclear]
    scope: <glob>                      # default: project root
    rationale: <one-line why>

classification:
  adopts: |
    Conditions on signal outcomes that indicate full adoption.
  adopts_with_exceptions: |
    Conditions that indicate partial adoption with localized gaps.
  deviates: |
    Conditions that indicate a consistent alternative shape.
  ignores: |
    Conditions under which the pattern is out of scope for the project.

adr_template: |
  Optional. A per-pattern §Context / §Decision skeleton that
  generated drafts reuse, with placeholders like {project} and
  {evidence_summary}.
```

### Verifiability ratings

| Rating | Meaning | Typical patterns |
|--------|---------|------------------|
| `high` | Structural, mechanically decidable | `deps-single-file`, ADT-encoding shape |
| `medium` | Mechanical signals + soft judgement | `functional-domain-design`, `test-economics` |
| `low` | Process-not-artifact; weak code signals | `tdd-rhythm`, `symmetric-refactoring` |

A `low` rating with no soft signals means the pattern is not
mechanizable today — record this honestly rather than faking
high verifiability.

### Fingerprint storage

- `grep` and `metric` signals are inline in the page.
- `ast` signals reference Scalafix rule names; implementations live
  under `tools/conformance/<pattern-id>/scalafix/`.
- `shell` signals reference scripts under
  `tools/conformance/<pattern-id>/` returning JSON on stdout:
  `{"verdict": "...", "evidence": [...], "truncated": false}`.

See [[tech/guides/conformance]] for the full operation specification.

---

'''

SCHEMA_ANCHOR = "## Promotion Metadata\n"


OWNERSHIP_CONFORMANCE_ROW = (
    "| `meta/conformance.md`         | llm       | no        |"
)
OWNERSHIP_DRAFTS_ROW = (
    "| `projects/*/adr/drafts/**`    | llm       | no        |"
)

OWNERSHIP_DRIFT_ANCHOR = (
    "| `meta/drift.md`               | llm       | no        |"
)
OWNERSHIP_ADR_ANCHOR = (
    "| `projects/*/adr/**`           | shared    | yes       |"
)

OWNERSHIP_RATIONALE = """- **meta/conformance.md is llm**: mechanical output of the `conform` operation, regenerated each run. Same shape as `meta/drift.md`.
- **projects/*/adr/drafts/ is llm**: `conform` produces ADR drafts here for human review; humans move accepted drafts to `projects/*/adr/` (where they become `shared`).
"""

OWNERSHIP_RATIONALE_ANCHOR = (
    "- **scratch/ is human**:"
)


def patch(path: Path, changes: list[tuple[str, str | None]]) -> None:
    """Apply (description, transformed-text) tuples to path.

    Each tuple's second element is either the new full text after the
    edit, or None if the change was a no-op (already applied).
    """
    for desc, new_text in changes:
        if new_text is None:
            print(f"skip: {path.name} — {desc}")
            continue
        path.write_text(new_text)
        print(f"apply: {path.name} — {desc}")


def patch_schema() -> None:
    text = SCHEMA.read_text()
    changes: list[tuple[str, str | None]] = []

    if CONFORMANCE_BLOCK_MARKER in text:
        changes.append(("conformance block section", None))
    else:
        if SCHEMA_ANCHOR not in text:
            print(f"error: schema.md missing anchor '{SCHEMA_ANCHOR.strip()}'", file=sys.stderr)
            sys.exit(2)
        new = text.replace(SCHEMA_ANCHOR, CONFORMANCE_BLOCK_SECTION + SCHEMA_ANCHOR, 1)
        changes.append(("conformance block section inserted before Promotion Metadata", new))

    patch(SCHEMA, changes)


def patch_ownership() -> None:
    text = OWNERSHIP.read_text()
    changes: list[tuple[str, str | None]] = []

    # Row 1: meta/conformance.md after meta/drift.md
    if OWNERSHIP_CONFORMANCE_ROW in text:
        changes.append(("ownership row meta/conformance.md", None))
    else:
        if OWNERSHIP_DRIFT_ANCHOR not in text:
            print(f"error: ownership.md missing anchor for drift row", file=sys.stderr)
            sys.exit(2)
        new = text.replace(
            OWNERSHIP_DRIFT_ANCHOR,
            OWNERSHIP_DRIFT_ANCHOR + "\n" + OWNERSHIP_CONFORMANCE_ROW,
            1,
        )
        text = new
        changes.append(("ownership row meta/conformance.md inserted after drift.md", new))

    # Row 2: projects/*/adr/drafts/** after projects/*/adr/**
    if OWNERSHIP_DRAFTS_ROW in text:
        changes.append(("ownership row projects/*/adr/drafts/**", None))
    else:
        if OWNERSHIP_ADR_ANCHOR not in text:
            print(f"error: ownership.md missing anchor for adr row", file=sys.stderr)
            sys.exit(2)
        new = text.replace(
            OWNERSHIP_ADR_ANCHOR,
            OWNERSHIP_ADR_ANCHOR + "\n" + OWNERSHIP_DRAFTS_ROW,
            1,
        )
        text = new
        changes.append(("ownership row projects/*/adr/drafts/** inserted after adr/**", new))

    # Rationale paragraphs
    if "meta/conformance.md is llm" in text:
        changes.append(("ownership rationale paragraphs", None))
    else:
        if OWNERSHIP_RATIONALE_ANCHOR not in text:
            print(f"error: ownership.md missing anchor for rationale", file=sys.stderr)
            sys.exit(2)
        new = text.replace(
            OWNERSHIP_RATIONALE_ANCHOR,
            OWNERSHIP_RATIONALE + OWNERSHIP_RATIONALE_ANCHOR,
            1,
        )
        text = new
        changes.append(("ownership rationale paragraphs inserted before scratch/ rationale", new))

    patch(OWNERSHIP, changes)


def main() -> None:
    patch_schema()
    patch_ownership()


if __name__ == "__main__":
    main()

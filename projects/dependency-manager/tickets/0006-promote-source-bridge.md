---
id: DM-006
title: Promote dm source bridge from sources/tmp → sources/raw
status: done
project: dependency-manager
created: 2026-05-29
closed: 2026-05-29
related_adr: []
priority: medium
---

## Goal

Move `sources/tmp/code/dependency-manager.md` (the bridge file
staged for promotion) to `sources/raw/code/dependency-manager.md`,
updating the `commit:` field from `uninitialized-tree` to the actual
SHA produced by DM-005. After this ticket, dm joins the same
authoritative source-bridge tier as sourceline-manager and the other
properly-tracked sources.

This ticket is **agent-doable** post-DM-005 — `sources/raw/**` is
human-owned per `meta/ownership.md`, but the user has previously
permitted the agent to perform the promote operation on its behalf
once the prerequisite (commit SHA) exists. The agent should still
flag the move in conversation for review.

## Acceptance Criteria

- [ ] `sources/raw/code/dependency-manager.md` exists with valid
  schema-conforming frontmatter:
  - `type: code`
  - `repo: /p/hg/dependency-manager`
  - `last_observed:` ≥ DM-005's commit date
  - `commit: <full SHA>` (from DM-005)
  - `entry_points:` populated with at least `build.mill`, `dm/src/dm/Main.scala`
- [ ] `sources/tmp/code/dependency-manager.md` removed.
- [ ] Wiki links updated: every reference to
  `[[sources/tmp/code/dependency-manager]]` rewritten to
  `[[sources/raw/code/dependency-manager]]`. Likely sites:
  - `projects/dependency-manager/index.md`
  - `projects/dependency-manager/log.md` (older entries — append
    a "links updated post-promotion" log entry rather than
    rewriting historical entries in place).
  - `projects/dependency-manager/designs/dm-architecture.md`
  - `sources/summaries/dependency-manager.md`
- [ ] `meta/registry.md` updated if dm appears there.
- [ ] Log entry on `projects/dependency-manager/log.md` recording
  the promotion.
- [ ] Log entry on `meta/log.md` recording the bridge promotion
  (a `promote` verb operation).

## Notes

Use `grep -rln "sources/tmp/code/dependency-manager" /p/wiki/` to find
all references; sweep and rewrite.

The frontmatter format mirrors what's currently in the tmp version —
the agent should copy field-by-field, only updating `last_observed`
and `commit`, and confirming `entry_points` is still accurate
(re-check after the migrations in DM-001/DM-002 may have added or
moved files).

**Sequence with DM-008** (ADR debts) is not strict: the bridge
promotion is purely a sources-tier housekeeping operation; it does
not block normative ADR edits. They can run in either order.

## Implementation Log

### [2026-05-29] closed — bridge promoted, references rewritten

Triggered immediately after DM-005 landed the first commit.

**New file**: `sources/raw/code/dependency-manager.md`.
Frontmatter:

```yaml
id: source-dependency-manager
type: code
repo: /p/hg/dependency-manager
last_observed: 2026-05-29
commit: 5459ddb7dc4ceb882ea89b2054e5814b9383f313
branch: master
entry_points: [...34 entries — full v1 surface incl. catalog/*, mill/, test/*]
design_source_of_truth: /p/hg/dependency-manager/DESIGN.md (in-tree)
```

The body was refreshed from the tmp version to reflect post-v1
reality (5 verbs working, 12 catalog libraries, 3 migrated
consumers, 71 tests, first commit landed). The "Current state"
table flipped every row from `stub`/`error`/`not initialised`
to `working` / populated counts / commit SHA. The "Open Questions
for Triage" section split: 2 questions resolved (compile error,
git initialisation), 3 remain deferred (/p/factory/ interaction,
Native CLI target, platforms-in-catalog).

**Removed**: `sources/tmp/code/dependency-manager.md`.

### Live wiki references rewritten (7 sites)

- `projects/dependency-manager/index.md` §"Code Location" — now
  points at `sources/raw/code/dependency-manager` with the SHA.
- `sources/summaries/dependency-manager.md` frontmatter
  `sources:` + §"Links" updated.
- `projects/dependency-manager/adr/0001-deviate-deps-single-file.md` §"Links" updated.
- `projects/dependency-manager/adr/0002-adopt-functional-domain-design.md` §"Links" updated.
- `projects/dependency-manager/designs/dm-architecture.md` frontmatter `sources:` + §"Links" updated.

### References *not* rewritten (intentional)

- All historical log entries in
  `projects/dependency-manager/log.md` and `meta/log.md`. Log
  entries are append-only and document the state at write time;
  the tmp path is correct as the historical fact.
- This ticket and the DM-009 ticket — both describe the
  action itself; the procedural text references are correct.
- The MVP plan acceptance criteria text — describes the
  end-state to verify, and the verification ran successfully.
- `meta/drift.md` DRIFT-023 description — references the tmp
  path in the context of "expected pre-resolution state"; the
  closure of sub-finding #2 is noted via the body update.

### Verification

```
$ ls /p/wiki/sources/tmp/code/                  → no dependency-manager.md
$ ls /p/wiki/sources/raw/code/dependency-manager.md  → exists
$ grep -rln "sources/tmp/code/dependency-manager" /p/wiki/  → 7 historical/procedural hits only
```

`meta/log.md` carries a `promote` entry for the operation.

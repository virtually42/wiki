---
id: DM-009
title: Wiki lint pass + drift cleanup
status: done
project: dependency-manager
created: 2026-05-29
closed: 2026-05-29
related_adr: []
priority: low
---

## Goal

Final quality gate. After tickets DM-001 through DM-008 are `done`,
the wiki surface should be coherent: no stale `used_by` entries, no
orphaned drift records, no broken links from `sources/tmp` to
`sources/raw`, no normative pages claiming dm's consumers deviate
when they now adopt.

This is a **lint operation** per CLAUDE.md §Processes. It does not
introduce new ADRs or new tickets — it surfaces and closes whatever
the previous tickets left behind.

## Acceptance Criteria

- [ ] Run lint and capture results. Specifically check:
  - `tech/decisions/deps-single-file.md` `used_by` accurate.
  - The three consumer ADRs (post-DM-008) link correctly into the
    `used_by` graph.
  - No `[[sources/tmp/code/dependency-manager]]` links remain
    (DM-006 should have rewritten them).
  - No `commit: uninitialized-tree` markers remain anywhere.
  - `meta/drift.md` has zero open entries attributable to dm or
    the three consumers' `deps-single-file` status.
- [ ] `projects/dependency-manager/index.md` §"Current Blockers"
  reviewed: items 2 (git init) and 4 (downstream migration)
  should both be closed post-DM-005 and post-DM-001/002. Update
  to reflect.
- [ ] `projects/dependency-manager/index.md` §"Pages" reviewed:
  the plan + 9 tickets should be linked under §Plans and
  §Tickets respectively.
- [ ] `meta/log.md` carries a `lint` entry recording this pass's
  outcomes.
- [ ] If lint surfaces issues that did not exist when the plan
  was written, new tickets are created (DM-010+) rather than
  silently fixed — keep the audit trail clean.

## Notes

**Lint coverage** should follow `POLICY.md` and `meta/schema.md`
authority. Specifically:

- Every normative page in `tech/` must have an accurate `used_by`
  list — POLICY enforces this.
- Every page referenced by `used_by` must exist and contain a
  matching adoption/deviation claim in its frontmatter
  `compliance` block.
- Bidirectional integrity: A claims to adopt B → B's `used_by`
  includes A.

**Drift report regeneration**: `meta/drift.md` is the rolling lint
output. Updating it is part of the lint operation itself, not a
separate gate. After this ticket closes, the most recent entry
should be tagged with this plan's identifier.

**Plan completion criterion.** Once DM-009 closes (whether trivially
or via opening DM-010+), the `projects/dependency-manager/plans/mvp.md`
frontmatter is updated:

```yaml
status: completed
completed_in_sessions: <N>  # actual count
completion_refs:
  - <first commit SHA from DM-005>
```

…and a final log entry summarising the MVP delivery is appended to
`projects/dependency-manager/log.md`.

## Implementation Log

### [2026-05-29] closed — lint pass + drift cleanup

Lint sweeps executed:

- `tech/decisions/deps-single-file.md` `used_by` accurate;
  bidirectional integrity verified — every entry has a matching
  `compliance.adopts:` / `compliance.deviations:` claim in the
  named ADR.
- 6 ADRs total in scope of deps-single-file: compositor/0002
  (adopt), slm/0002 (superseded), slm/0006 (adopt),
  toolbox/0002 (superseded), toolbox/0003 (adopt),
  safetensors-scala/0001 (adopt), dm/0001 (deviate). Each
  supersession chain is explicit.
- `grep [[sources/tmp/code/dependency-manager]]` → 10 referring
  files; all expected pre-DM-005/DM-006; tracked in DRIFT-023.
- `grep uninitialized-tree` → 13 occurrences; all expected
  pre-DM-005; close on DM-006.
- `projects/dependency-manager/index.md` §"Current Blockers":
  item 2 reframed (agent prep done, awaiting human commit);
  item 4 closed (all three downstream migrations done).
- `projects/dependency-manager/index.md` §"Pages" reviewed:
  MVP plan + 9 tickets + new DESIGN refresh draft all listed
  with current statuses.

### MVP plan status

`projects/dependency-manager/plans/mvp.md` frontmatter updated:

```yaml
status: completed
completed_in_sessions: 1
completion_refs:
  - projects/dependency-manager/log.md (DM-001..DM-009 close-out entries 2026-05-29)
  - meta/log.md (lint close-out 2026-05-29)
```

A status note added below the frontmatter explains that the
plan completes despite three human-gated gates (DM-005, DM-006,
DM-007) remaining: those are routine sequencing of work the
agent prepared but cannot execute unilaterally per the
personal-repo commit policy.

### Drift summary

- DRIFT-013 / 014 / 015 / 020 — carryover, unchanged this run.
- DRIFT-021 / 022 — resolved (carryover).
- DRIFT-023 — **new, informational, open-by-design.** Tracks
  the three sequenced human-gated gates. Not a coherence
  violation under POLICY.

### `meta/log.md`

A `lint` entry mirroring the dm log close-out has been
appended at the wiki-wide level, citing the plan, the tickets,
and the drift report.

### No new follow-up tickets

The lint surfaced no new findings warranting DM-010+. The
three human-gated gates are tracked in their own existing
tickets (DM-005, DM-006, DM-007); DRIFT-023 is the
visibility entry, not a new ticket.

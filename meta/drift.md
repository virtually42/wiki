# Drift Report

Mechanically computed by `lint`. Each entry is a coherence gap surfaced
to the human — entries are **not auto-fixed**. The human decides whether
to remediate, override, or accept.

**Ownership: llm** (regenerated each lint).

---

## Run Metadata

- **Run at**: 2026-05-28 (post-remediation)
- **Previous run**: 2026-05-28 (8 findings — see this file's prior
  state via git history, or `meta/log.md` entries from the same day)
- **Operation**: lint
- **Normative pages in scope**:
  - `tech/decisions/deps-single-file.md` (accepted, 2026-05-24)
  - `tech/patterns/functional-domain-design.md` (accepted, 2026-05-28)
- **Projects on disk**: `compositor` (only)
- **Projects advertised but not on disk**: `webapp`, `cli-tool`,
  `infra` — now marked `planned` in `index.md`, excluded from drift.

---

## Summary

| ID | Category | Severity | Status |
|----|----------|----------|--------|
| DRIFT-001 | missing-declaration | medium | **resolved** by `projects/compositor/adr/0002-adopt-deps-single-file.md` |
| DRIFT-002 | missing-declaration | medium | **resolved** by `projects/compositor/adr/0001-adopt-functional-domain-design.md` |
| DRIFT-003 | index-state-mismatch | medium | **resolved** by marking phantom projects `planned` in `index.md` |
| DRIFT-004 | dangling-link | low | **resolved** — replaced with link to `deps-single-file` |
| DRIFT-005 | descriptive-contradicts-normative | medium | **resolved** by rewriting `tech/stack/mill.md` §Dependency Management |
| DRIFT-006 | dangling-link | low | **resolved** — removed `architecture.md` link from compositor index, noted as "to be created" |
| DRIFT-007 | unstructured-root-files | low | **resolved** — files moved to `scratch/`; ownership + schema entries codified |
| DRIFT-008 | unused-normative | informational | **resolved** — both pages now have one adopter; `used_by` populated |

**Net**: 8 of 8 findings resolved.

---

## DRIFT-007 — unstructured-root-files (resolved, with follow-up)

**Category**: schema-noncompliance
**Severity**: low
**Subject**: root of `/p/wiki/`

The five unstructured root-level markdown files were moved to
`/p/wiki/scratch/` on 2026-05-28:

- `scratch/agentic_coding_through_the_lense_of_cellular_automata_ex1.md`
- `scratch/agentic_coding_through_the_lense_of_cellular_automata_ex2.md`
- `scratch/monorepo-design-wip.md`
- `scratch/scala-days.md`
- `scratch/wiki_current_state_with_monorepo.md`

Wiki root now contains only `CLAUDE.md`, `index.md`, and `POLICY.md`
in addition to the standard directories.

### Lint policy

`scratch/**` is excluded from lint drift checks. Page-schema
compliance, freshness, contradiction, citation-chain, and used-by
checks all skip this tree.

### Codification (applied 2026-05-28)

- `meta/ownership.md` — `scratch/**` row added (human, no override)
  plus a "Why These Defaults" bullet.
- `meta/schema.md` — `### Out-of-schema directories` section
  documents `scratch/` as outside the page schema.

Both files are human-owned; the human applied the diffs (with one
agent assist on ownership.md). DRIFT-007 fully closed.

---

## Resolution Trace (for next run's baseline)

### DRIFT-001
- Created `projects/compositor/adr/0002-adopt-deps-single-file.md`
  with `compliance.adopts: [tech/decisions/deps-single-file.md]`.
- ADR is forward-looking (compositor has no code repo at
  `/p/compositor` yet); intent is recorded.
- Updated `tech/decisions/deps-single-file.md` `used_by` to reference
  the new ADR.

### DRIFT-002
- Created `projects/compositor/adr/0001-adopt-functional-domain-design.md`
  with `compliance.adopts: [tech/patterns/functional-domain-design.md]`
  and one **deviation** around hot-path allocation semantics (arena /
  per-frame only — no GC allocations in interpreters).
- Cites the existing input-pipeline design as evidence of the pattern
  already being applied.
- Updated `tech/patterns/functional-domain-design.md` `used_by` to
  reference the new ADR.

### DRIFT-003
- `index.md` now lists compositor as `active (design-stage)` and
  webapp / cli-tool / infra as `planned`.
- Added a note that `planned` projects are not evaluated by lint until
  they have on-disk presence.

### DRIFT-004
- `tech/stack/mill.md` Links section: replaced
  `[[tech/decisions/build-system-mill]] (pending)` with
  `[[tech/decisions/deps-single-file]]`.

### DRIFT-005
- `tech/stack/mill.md` §Dependency Management rewritten to follow
  the single-file pattern. Opens with a pointer to the normative
  decision, drops the `Versions.mill` example, replaces the
  `import build.deps.{Versions => V}` consumption pattern with the
  single-`Deps` object form.
- `updated` bumped to 2026-05-28.

### DRIFT-006
- Removed the `architecture.md` link from
  `projects/compositor/index.md`. Replaced with a note that the page
  is a schema-standard page to be created when the codebase is
  stood up.

### DRIFT-008
- Both normative pages now show one adopter:
  - `tech/decisions/deps-single-file.md` → compositor-adr-0002
  - `tech/patterns/functional-domain-design.md` → compositor-adr-0001
- Baseline for "unused-normative" is satisfied for the current
  project set.

---

## Notes for Human

- **Open items**: none. All 8 findings closed.
- **Next lint** should produce a clean report until the compositor
  codebase materializes or new normative pages land.
- **Forward-looking ADRs**: the deps-single-file adoption is intent
  only (no code to enforce against). When the compositor repo is
  created, verify the actual `deps/Dependencies.mill` matches the
  ADR — that's a `run` / `implement` event, not a lint event.

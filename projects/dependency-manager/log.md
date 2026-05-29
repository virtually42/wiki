# dependency-manager — project log

Append-only record of project-scoped events.

**Ownership: llm.**

---

## [2026-05-29] docs | DESIGN.md stripped to decisions archive (DM-007, option B)

Human chose option B over the original four-block refresh
proposal: keep only the *why* in DESIGN.md (architectural
decisions, tool/library choices, the 17 chronological
decisions, Renovate/Gradle clarification, open questions);
delete everything that rotted (where-we-stopped, next-steps,
verb-status, repo-layout, cross-platform suffix table).

### Stripped sections

- §"The problem we're solving" — duplicate of README.
- §"Path convention" — general /p/* layout; not dm-specific.
- §"Repo layout" tree — stale; covered by README and the
  source bridge.
- §"dm verb status" table — most rot-prone; current data
  lives in the wiki index.md.
- §"Cross-platform suffix handling" — no longer matches
  reality (dm preserves source-form `::` rather than
  reverse-engineering platform suffixes).
- §"Tool integration model" diagram — in README.
- §"Where we stopped" — entirely stale.
- §"Next steps when resuming" — every item closed.

### Kept (with light edits)

- §"Architectural decisions (locked in)" — 6 named decisions.
- §"Tool / library decisions (locked in)" — choice table.
- §"Decisions taken (1–17)" — chronological rationale archive.
  Decision 1 amended to note the post-DM-008 ADR realignment;
  Decision 14 amended to record the `.renovaterc.json` at
  repo root (vs. the originally-proposed `deps/`).
- §"Renovate / Gradle clarification" — kept and amplified to
  note the `customManagers` regex actually in use.
- §"Open questions" — kept, with one new entry:
  platforms-in-catalog (position: no; rationale captured).

### Wiki touch

- `projects/dependency-manager/designs/dm-architecture.md`
  rewritten to mirror the stripped in-tree file (with
  appropriate wiki-vs-in-tree cross-links).
- `projects/dependency-manager/designs/dm-architecture-2026q2-refresh.md`
  marked `status: superseded` with a banner explaining option B
  was chosen instead of the original four-block proposal.

### Commit

`/p/hg/dependency-manager@3482be3` — single follow-up commit
to the dm repo. Same personal-repo policy as the first commit.
Diff: 1 file changed, 33 insertions, 165 deletions.

### DRIFT-023 fully resolved

This entry closes the last open sub-finding (#3) of DRIFT-023.
DRIFT-023 is now fully resolved.

Refs:
[[projects/dependency-manager/tickets/0007-refresh-in-tree-design]],
[[projects/dependency-manager/designs/dm-architecture]],
[[projects/dependency-manager/designs/dm-architecture-2026q2-refresh]],
[[meta/drift]],
[[meta/log]]

---

## [2026-05-29] ops | branch rename master → main

Trivial follow-up to DM-005. Renamed `master` → `main` via
`git branch -m master main` to match the slm and toolbox
convention. No remote, no force-push concerns.

Live-state wiki references updated:

- `sources/raw/code/dependency-manager.md` frontmatter
  `branch: master` → `branch: main`; two body mentions of
  `(branch master)` updated.
- `projects/dependency-manager/index.md` §"Code Location" +
  DM-005 ticket bullet + §"Current Blockers" item 2.

Historical entries (commit log entry, DM-005 ticket
implementation log, meta/log commit entry, meta/drift
DRIFT-023 closure note, DM-006 implementation log) left
intact — they record the state at write time, and the
rename note above explains the transition.

Refs:
[[projects/dependency-manager/index]],
[[sources/raw/code/dependency-manager]]

---

## [2026-05-29] promote | source bridge tmp → raw (DM-006)

Triggered immediately after DM-005's first commit landed
(SHA `5459ddb7dc4ceb882ea89b2054e5814b9383f313`).

### What landed

- **New**: `sources/raw/code/dependency-manager.md` — bridge file
  with the real SHA in `commit:`, `branch: master`, and a
  refreshed `entry_points:` list covering the full v1 surface
  (catalog/*, mill/, all five verbs, test/*). The obsolete
  `git_init_state:` field is gone.
- **Body refresh**: every "Current state" row flipped from
  `stub`/`error`/`not initialised` to `working` / populated
  counts / commit SHA. "Open Questions for Triage" trimmed: 2
  resolved (compile error, git initialisation), 3 deferred to
  longer-horizon design conversations (/p/factory/ interaction,
  Native CLI target, platforms-in-catalog).
- **Removed**: `sources/tmp/code/dependency-manager.md`.

### Wiki references rewritten

7 live referrers:

| File | What changed |
|---|---|
| `projects/dependency-manager/index.md` | §"Code Location" now points at `sources/raw/code/dependency-manager` with the SHA inline; §"Current Blockers" item 2 marked resolved; §"Tickets" DM-005 + DM-006 marked done. |
| `sources/summaries/dependency-manager.md` | Frontmatter `sources:` + §"Links" updated. |
| `projects/dependency-manager/adr/0001-deviate-deps-single-file.md` | §"Links" updated. |
| `projects/dependency-manager/adr/0002-adopt-functional-domain-design.md` | §"Links" updated. |
| `projects/dependency-manager/designs/dm-architecture.md` | Frontmatter `sources:` + §"Links" updated. |

### References intentionally left alone

- All historical entries in this log file and `meta/log.md`
  (append-only; document state at write time).
- This ticket's procedural text + DM-009 close-out narrative
  (correct as descriptions of the action).
- MVP plan acceptance-criteria text (describes the end state
  that has now been verified).
- `meta/drift.md` DRIFT-023 narrative (references the tmp path
  in "expected pre-resolution state" context; the closure is
  noted via the status update at the head of the entry).

### Drift impact

- DRIFT-023 marked **partially resolved**:
  - Sub-finding #1 (DM-005 first commit) — closed.
  - Sub-finding #2 (DM-006 bridge promotion) — closed.
  - Sub-finding #3 (DM-007 in-tree apply) — still open by
    design; awaits human apply of
    [[projects/dependency-manager/designs/dm-architecture-2026q2-refresh]]
    against `/p/hg/dependency-manager/DESIGN.md`.

### MVP status

The MVP plan acceptance criteria are now fully met:

- ✓ Criterion 6: `git log --oneline | head -1` on
  `/p/hg/dependency-manager` → `5459ddb Initial dm v1 — …`.
- ✓ Criterion 7: `sources/raw/code/dependency-manager.md` exists
  with `commit:` matching dm's HEAD; tmp copy removed.

Plan stays at `status: completed`. DM-007 remains the single
in-flight human-gated item; not MVP-blocking.

Refs:
[[projects/dependency-manager/tickets/0006-promote-source-bridge]],
[[sources/raw/code/dependency-manager]],
[[meta/log]],
[[meta/drift]]

---

## [2026-05-29] commit | first commit landed (DM-005)

Per the personal-repo policy
([[feedback_hg_repo_commit_policy]]) the first commit is
human-gated. Human approved agent-on-behalf execution.

- **SHA**: `5459ddb7dc4ceb882ea89b2054e5814b9383f313`
- **Branch**: `master` (rename to `main` deferred)
- **Author**: `tigidar`
- **Unsigned**, no `Co-Authored-By` trailer
- **Subject**: `Initial dm v1 — catalog + 5 verbs + Renovate + Nix flake + 3 consumers migrated`
- **40 files changed, 2806 insertions(+)** — full v1 surface
  staged explicitly (no `git add -A`):
  - `.gitignore`, `.mill-version`, `.renovaterc.json`
  - `build.mill`, `bin/dm`, `DESIGN.md`, `README.md`
  - `deps/libs.versions.toml`, `deps/projects.yml`
  - `dm/src/**` (Main, Resolve, Extract, Regen, Verify, Promote, catalog/*, mill/, millq/)
  - `dm/test/src/**` (11 spec files, 71 tests)
  - `flake.nix`, `flake.lock`

The `git -c commit.gpgsign=false` override was used because the
global git config has signing enabled by default in some
accounts; the per-invocation override matches policy intent
without changing global config.

This unblocked DM-006 (bridge promotion), executed immediately
after — see the entry above.

Refs:
[[projects/dependency-manager/tickets/0005-git-init-first-commit]],
[[feedback_hg_repo_commit_policy]]

---

## [2026-05-29] lint | DM-009 MVP plan close-out

Final lint pass for the MVP plan. Six of nine tickets fully
closed (DM-001..DM-004, DM-008, DM-009); three sequenced
human-gated gates (DM-005, DM-006, DM-007) tracked as
DRIFT-023 (informational, open-by-design).

### Acceptance criteria check

Mapped against `plans/mvp.md` §"Acceptance Criteria":

| # | Criterion | Status |
|---|---|---|
| 1 | All 9 tickets `status: done` | 6/9 done; 3 sequenced/human-gated (DM-005, DM-006, DM-007) |
| 2 | `bin/dm verify` OK for all 3 projects | ✓ (`all 3 project(s) in sync`) |
| 3 | Each consumer `mill __.compile` + `__.test` green | ✓ (toolbox 3638 tasks; safetensors 141+164+186) |
| 4 | `dm extract --force --out=/tmp/x` byte-identical | ✓ (`diff -r` exit 0 across all consumers, twice) |
| 5 | At least one Renovate bump landed end-to-end | ✓ (three: os-lib, pprint, munit-cats-effect) |
| 6 | `git log --oneline | head -1` returns valid SHA | gated on DM-005 |
| 7 | `sources/raw/code/dependency-manager.md` exists with real SHA | gated on DM-005 → DM-006 |
| 8 | README has "Adopting dm in a downstream repo" section | ✓ |
| 9 | No outstanding drift attributable to dm/consumers | ✓ (DRIFT-023 is open-by-design, not a coherence violation) |

The plan flips to `status: completed` with the carryover gates
documented. Criteria 6 and 7 unblock on the human commit; the
plan does **not** need to re-open at that point — DM-006 (agent
post-DM-005) and DM-007 (agent re-ingest post-human-apply) are
straightforward and tracked by their own tickets.

### What this run touched

- `meta/drift.md` — full Run Metadata refresh; DRIFT-023 added;
  Notes for Human updated.
- `meta/log.md` — `lint` entry mirroring this summary at the
  wiki-wide level.
- `projects/dependency-manager/index.md` — §"Current Blockers"
  (items 2, 4 closed/reframed), §"Tickets" (statuses), §"Designs"
  (refresh draft listed).
- `projects/dependency-manager/plans/mvp.md` — `status: completed`,
  `completed_in_sessions: 1`, completion refs.
- Lint sweeps performed:
  - `grep [[sources/tmp/code/dependency-manager]]` → 10 referring
    files; all expected, all close on DM-006.
  - `grep uninitialized-tree` → 13 occurrences; all expected
    pre-DM-005, all close on DM-006 bridge promotion.
  - `tech/decisions/deps-single-file.md` `used_by`
    bidirectional integrity: ✓.
  - No `compliance.adopts:` entry pointing at a non-existent
    page. No fabricated `used_by`.

### What's left

Per DRIFT-023, the three sequenced gates:

1. Human triggers DM-005 commit; SHA recorded in the ticket
   log.
2. Agent runs DM-006: bridge file moved, `commit:` field
   updated to the SHA, 10 wiki references rewritten,
   `sources/tmp/code/dependency-manager.md` removed.
3. Human applies DM-007 refresh in-tree; agent re-ingests the
   wiki-side `designs/dm-architecture.md` mirror.

None of these change the v1 surface — they are housekeeping
that closes the wiki-side consistency gaps left open by the
"pre-first-commit" state.

### MVP summary

`dm` v1 is functionally complete:

- 5 verbs working end-to-end (resolve, extract, regen, verify,
  promote).
- 3 consumers migrated to the catalog
  (toolbox, sourceline-manager, safetensors-scala) with verified
  test passes across all platforms each consumer supports.
- Renovate config validated; 3 bumps landed end-to-end (os-lib,
  pprint, munit-cats-effect); 1 attempted and rolled back per
  documented-outcome rule (kyo RC2).
- README onboarding guide covering the 6-step adoption pattern
  including the Mill 1.x `deps/package.mill` anchor rule.
- 6 wiki ADRs on `deps-single-file` (3 adopts post-migration,
  1 dm-side deviate for bootstrap, 2 superseded deviations
  retained for history) all with coherent bidirectional
  `used_by` integrity.
- Wiki-side draft prepared for in-tree DESIGN.md refresh
  (DM-007).

Refs:
[[projects/dependency-manager/plans/mvp]],
[[projects/dependency-manager/tickets/0009-lint-and-drift-cleanup]],
[[meta/log]],
[[meta/drift]]

---

## [2026-05-29] adr | Consumer ADRs realigned (DM-008)

Three consumer ADRs realigned post-migration to reflect the
adopt-with-platforms-exception state. Picked the **supersede**
pattern uniformly for slm and toolbox; safetensors-scala had no
prior wiki ADR so the new one is its first.

### What was written

| Project | New ADR | Status of predecessor |
|---|---|---|
| sourceline-manager | `adr/0006-adopt-deps-single-file.md` | ADR-0002 → `superseded` |
| toolbox | `adr/0003-adopt-deps-single-file.md` | ADR-0002 → `superseded` |
| safetensors-scala | `adr/0001-adopt-deps-single-file.md` | (first wiki ADR; in-tree predecessor untouched) |

All three share the same exception shape: adopt for external
Maven library coordinates (via dm-generated
`deps/Dependencies.mill`), narrow exception for platform
versions (Scala / ScalaJS / ScalaNative remain inline), severity
`low`. The platforms boundary is principled (Renovate's Maven
manager model does not cover platform versions; conflating
shapes is wrong) and cross-references the open question in
[[projects/dependency-manager/designs/dm-architecture-2026q2-refresh]]
§"Open questions".

### Wiki touches

- `tech/decisions/deps-single-file.md` `used_by` block extended
  with the three new ADRs (alongside the superseded entries
  retained for history).
- `projects/{sourceline-manager,toolbox}/index.md` ADR lists
  updated: ADR-0002 marked superseded; new ADRs listed.
- `projects/toolbox/index.md` §"Embedding Path" rewritten —
  deviation-by-construction framing replaced with
  dm-migration-by-construction framing.
- `projects/safetensors-scala/index.md` §"ADRs" section
  reworked from "No wiki-side ADRs" to list the new one; notes
  the in-tree predecessor is unchanged and the optional in-tree
  rewrite is human-owned.
- Project log entries appended for all three consumers mirroring
  this entry's scope.

### Why supersede, not rewrite

The original deviations rested on a "monorepo embedding will
resolve this" reasoning chain specific to the timeline before
dm existed. The new adoptions rest on the dm-catalog mechanism
— a different reasoning chain. Two ADRs keep the history
legible; rewriting in place would have erased the load-bearing
historical context.

### Severity rationale

`low` (not `medium`) because:

1. The platforms exception is principled, not incidental — the
   Maven model boundary is a real and recurring constraint.
2. Renovate's coverage is at-spec for what dm manages.
3. The cross-consumer pattern is coherent (same template across
   all three v1 consumers), so future audits have a single
   pattern to recognise rather than three ad-hoc deviations.

### In-tree safetensors-scala ADR

`/p/hg/safetensors-scala/docs/adr/0001-inline-versions.md` was
left untouched per the ticket's wording (in-tree edit is
optional human follow-up; not required for the wiki ticket to
close).

### Next

DM-009 (lint pass) will surface a fresh drift run with the new
ADRs in place and confirm the `used_by` graph is bidirectionally
consistent.

Refs:
[[projects/dependency-manager/tickets/0008-resolve-adr-debts]],
[[projects/sourceline-manager/adr/0006-adopt-deps-single-file]],
[[projects/toolbox/adr/0003-adopt-deps-single-file]],
[[projects/safetensors-scala/adr/0001-adopt-deps-single-file]],
[[tech/decisions/deps-single-file]]

---

## [2026-05-29] docs | DESIGN.md refresh draft ready for human (DM-007)

Wrote
`projects/dependency-manager/designs/dm-architecture-2026q2-refresh.md`
covering four replacement blocks and one §"Open questions"
addition for `/p/hg/dependency-manager/DESIGN.md`. Each change
cites the wiki log entry that closed the originally-open item
so the human can verify before applying.

### Sections refreshed

- §"dm verb status" — every verb flipped `stub` → `working`,
  with the per-verb purpose strings sourced from the wiki-side
  `index.md` (which is current).
- §"Where we stopped" — replaced with the v1-complete state
  (71 tests green, 5 verbs working, 3 consumers migrated, Renovate
  validated, Nix apps functional). Lists the four pre-MVP gaps
  (git-init, bridge promotion, ADR realignment, lint pass) by
  ticket reference. Restates the deferrals.
- §"Next steps when resuming" — deleted; replaced with a 2-line
  pointer to the wiki plan (`plans/mvp.md`). Every original item
  is closed; keeping the list in-tree would just rot.
- §"Repo layout" `.renovaterc.json` line — move from `deps/`
  subfolder to repo root. (The in-tree note about the deviation
  becomes obsolete.)
- §"Open questions" — adds the platforms-in-catalog question
  with a recorded position ("no — Renovate's Maven model doesn't
  cover them; mixing shapes is wrong"). Re-visit clause: when a
  future Renovate manager gains platform-version awareness.

### Awaiting human apply

The in-tree DESIGN.md is outside the wiki's ownership claim. The
human reads the draft, applies the changes in-place, and
commits per the personal-repo policy. On confirmation, the
agent re-ingests the in-tree file into the wiki mirror
`projects/dependency-manager/designs/dm-architecture.md` and
closes DM-007.

Until then, the draft stays in `designs/` as a side-by-side
record of the proposed delta.

Refs:
[[projects/dependency-manager/tickets/0007-refresh-in-tree-design]],
[[projects/dependency-manager/designs/dm-architecture-2026q2-refresh]],
[[projects/dependency-manager/designs/dm-architecture]]

---

## [2026-05-29] ops | DM-005 pre-handoff sweep ready for human commit

Agent-side prep complete; commit itself awaits the human per the
personal-repo policy.

### State

- `/p/hg/dependency-manager/.git/` **already exists** (branch
  `master`, 0 commits). The "uninitialized-tree" framing in the
  earlier log entries reflected the moment of ingest; `git init`
  has since been done. Only the first commit remains.
- `.gitignore` present and covers `out/`, `.metals/`, `.bsp/`,
  `.bloop/`, `.idea/`, `*.iml`, `.scala-build/`, `.vscode/`.
- Sweep for transient files (`*.bak`, `*.swp`, `*.DS_Store`)
  returned zero hits.
- 12 untracked entries to stage explicitly:
  - `.gitignore`, `.mill-version`, `.renovaterc.json`
  - `build.mill`, `bin/`, `DESIGN.md`, `README.md`
  - `deps/` (libs.versions.toml + projects.yml)
  - `dm/` (src + test/src)
  - `flake.nix`, `flake.lock`

### Branch-name note

Current branch is `master`. The two other `/p/hg/` repos with
commits (toolbox, sourceline-manager) use `main`. The human may
want `git branch -m master main` before committing. Surfacing,
not enforcing.

### Proposed commit subject

```
Initial dm v1 — catalog + 5 verbs + Renovate + Nix flake + 3 consumers migrated
```

Captures the v1 scope: catalog (TOML + YAML), 5 working verbs
(resolve / extract / regen / verify / promote), Renovate
config validated, Nix flake apps (test / verify / check /
renovate-dryrun), and three downstream consumer migrations
landed (toolbox + slm + safetensors-scala).

### Post-commit follow-up

Once the human commits and the SHA exists:

1. DM-005 closes; SHA recorded in the ticket's implementation
   log.
2. DM-006 unblocks: promote `sources/tmp/code/dependency-manager.md`
   to `sources/raw/code/dependency-manager.md` with the real
   SHA.
3. Wiki bridge frontmatter `commit: uninitialized-tree` →
   `commit: <SHA>` in the promoted file.

Refs:
[[projects/dependency-manager/tickets/0005-git-init-first-commit]],
[[feedback_hg_repo_commit_policy]]

---

## [2026-05-29] docs | README adoption guide + decision-page anchor rule (DM-004)

### `/p/hg/dependency-manager/README.md`

New `## Adopting dm in a downstream repo` section, placed after
"Typical workflow". Covers the full onboarding script:

1. Bootstrap with `dm extract --force` (catalog learns about
   the new project).
2. Hand-author the `deps/package.mill` anchor (one line:
   `package build.deps`). Includes the rationale (Mill 1.x
   discovery requirement) and the precedent (Mill upstream's
   `example/large/multifile/13-subdir-with-helper/`).
3. `dm regen --project=<name>` to generate `Dependencies.mill`.
4. Rewrite `build.mill` mvnDeps with `build.deps.Deps.*`,
   including the kebab→camel naming table (`os-lib` →
   `osLib`, `munit-scalacheck` → `munitScalacheck` with the
   case-fold warning that bit slm and safetensors).
5. `projects.yml` registration (automatic via extract; how
   to keep it in sync).
6. `dm verify --project=<name>` as the CI gate.

Two bonus subsections: **Bumping a version** (the full
catalog-edit → verify → regen → test loop) and **When the
catalog and Mill drift** (the `dm promote` recovery path with
the `--apply` semantics). Closes with cross-links to
`tech/decisions/deps-single-file` and the slm log entry
(worked-example pointer).

The README explicitly codifies the boundary: catalog covers
**external Maven deps only**; platforms (Scala / ScalaJS /
ScalaNative), `organization`, `projectVersion`, `artifact`,
and `no.virtual-architect::*` self-references stay inline. This
is the platform-versions-exception rationale that DM-008 will
re-state in the per-consumer ADRs.

### `tech/decisions/deps-single-file.md`

Added `### Mill 1.x discovery pre-requisite` after `### Rules`.
Documents the `deps/package.mill` anchor with the one-line
content and the failure mode (Mill silently ignores
`Dependencies.mill` without it). Cross-linked
`[[projects/dependency-manager/index]]`.

The decision page's `applies_to` and `used_by` are unchanged
this round — the per-project ADR realignment (DM-008) handles
`used_by` updates.

### What this unblocks

- Any future repo joining the `/p/hg/` cohort can adopt via
  the README script rather than re-discovering the anchor
  rule. (One more piece of evidence that the slm anchor
  discovery, while unwelcome at the time, was load-bearing
  knowledge worth surfacing.)
- DM-008's per-consumer ADRs can cite the README as the
  canonical procedure and the decision page as the normative
  shape, with the adopt-with-platforms-exception pattern
  inheriting the rationale from this section.

Refs:
[[projects/dependency-manager/tickets/0004-consumer-adoption-readme]],
[[tech/decisions/deps-single-file]],
[[projects/sourceline-manager/log]]

---

## [2026-05-29] operate | Renovate bumps end-to-end (DM-003)

Three low-risk bumps landed; one larger bump (kyo RC2) attempted
and rolled back per the ticket's documented-outcome rule.

### Landed

| Library | Before → After | Consumer affected | Test result |
|---|---|---|---|
| `os-lib` | 0.11.7 → 0.11.8 | toolbox (procOslib jvm + native) | 249/249 + 311/311 |
| `pprint` | 0.9.4 → 0.9.6 | toolbox (example.jvm) | 576/576 |
| `munit-cats-effect` | 2.1.0 → 2.2.0 | toolbox (procFs2.jvm.test) | 302/302 |

For each: catalog edit → `dm verify` reports DRIFT at exact line
→ `dm regen --project=toolbox` → `dm verify` OK → consumer tests
green. End-to-end loop validated.

Full `mill __.test` sweep across toolbox (3638 tasks, JVM + JS +
Native) clean post-bumps.

### Rolled back

`kyo-core 1.0-RC1 → 1.0.0-RC2`: catalog accepted, regen produced
`Dependencies.mill` fine, but `mill procKyo.jvm[3.8.3].compile`
failed with 10 errors at `kyo.Process.Command`-type references —
the kyo Process API was refactored in RC2. Rollback: edit catalog
back to RC1, regen, verify green. Round trip from drift to clean
in under 2 minutes.

Outcome recorded as **deferred until kyo-core 1.0.0 stable** or
toolbox proc-kyo is ported to the new API. The decision belongs
to the toolbox project, not dm — a follow-up ticket against
toolbox is the natural home.

### What this validates

1. **Drift detection at the exact line** — `dm verify`'s
   line-level diff output points humans (or CI logs) at the
   library that needs attention. Tested on three real
   single-character bumps.
2. **Regen restores sync in one command** — `dm regen --project=<x>`
   is sufficient; the byte-for-byte equality verified by re-running
   `dm verify`.
3. **Mill picks up the change at next compile** — no caching layer
   between `Dependencies.mill` and Mill's mvnDeps resolution; the
   bump becomes effective immediately.
4. **Rollback is straightforward without git** — backup the TOML,
   restore on failure. Post-DM-005 the rollback simplifies to
   `git checkout deps/libs.versions.toml && dm regen …`.

### Renovate dry-run note

`nix run .#renovate-dryrun` requires a git-tracked tree; dm is
pre-DM-005 (no git yet), so the dry-run was skipped this round.
Used the previously-validated bump table (logged 2026-05-29 in
the "dm verify + Renovate config validated end-to-end" entry)
as the working list. The list itself proved accurate — all four
bumps existed on Maven Central and resolved through Mill.

Once DM-005 lands, the dry-run becomes routine.

### Catalog state after this session

```
os-lib              0.11.7 → 0.11.8
pprint              0.9.4  → 0.9.6
munit-cats-effect   2.1.0  → 2.2.0
kyo-core            1.0-RC1   (RC2 attempted, deferred)
```

Other libraries unchanged. `bin/dm verify` reports
`all 3 project(s) in sync`.

Refs:
[[projects/dependency-manager/tickets/0003-renovate-bumps-end-to-end]],
[[projects/dependency-manager/index]]

---

## [2026-05-29] implement | safetensors-scala migrated to dm catalog (DM-002)

Third (and final v1) consumer migration. Smallest surface — 3
external libraries — but exercises the cross-platform sweep
(JVM/JS/Native) and the scodec pin transfer.

### Mapping applied

| `V.<x>` (removed) | `Deps.<x>` (added) | Call site |
|---|---|---|
| `V.scodec` | `build.deps.Deps.scodecCore` | `SafeTensorsCommon.mvnDeps` |
| `V.munit` | `build.deps.Deps.munit` | `SafeTensorsTestSources.mvnDeps` |
| `V.munitScalaCheck` | `build.deps.Deps.munitScalacheck` | `SafeTensorsTestSources.mvnDeps` |

Note the case fold: project-local `munitScalaCheck` → catalog's
kebab `munit-scalacheck` → camel `munitScalacheck`. Same
naming-case tax slm hit; documented in DM-004's README guide.

`object V` retains platform versions + organisation + artifact +
projectVersion. Inline comment now states scodec-pin is held by
the central catalog (`/p/hg/dependency-manager/deps/libs.versions.toml`,
`scodec-core = "2.3.3"`) and that drift is caught by `dm verify`
/ `dm promote`.

### scodec pin transferred

Pre-migration: `V.scodec = "2.3.3"` inline (palladium resolution
pin per in-tree ADR-0001). Post-migration: catalog entry
`scodec-core = { module = "org.scodec::scodec-core", version = "2.3.3" }`
holds the pin. The version is unchanged; the *owner* of the pin
moved from inline `object V` to the central TOML. Renovate's
`packageRules` will surface any upstream bump as a PR rather than
silently mutating the pin (same Renovate model used for every
other library).

### `deps/package.mill` anchor

One-line file, third use of the pattern. All three v1 consumers
now carry it; the pattern is documented in DM-004.

### Verification

```
$ mill __.compile                                  → 342/342 SUCCESS
$ mill safetensors.jvm[3.8.3].test                 → 141/141 green
$ mill safetensors.js[3.8.3].test                  → 164/164 green
$ mill safetensors.native[3.8.3].test              → 186/186 green
$ cd /p/hg/dependency-manager
$ bin/dm verify --project=safetensors-scala
# safetensors-scala        OK
$ bin/dm extract --force --out=/tmp/dm-test … && diff -r /tmp/dm-test deps/  → 0
$ mill safetensors.jvm[3.8.3].publishLocal && jar tf …            → non-empty
```

The empty-jar sentinel (`jar tf` of the JVM publishLocal artefact)
returns 10+ classes under `no/virtual_architect/safetensors/` —
no regression from the migration.

### Status round-up

`Current Blockers` item 4 from
`projects/dependency-manager/index.md` ("Downstream build.mill
migration") is now **fully resolved**: all three v1 consumers
(slm, toolbox, safetensors-scala) on the catalog.

The in-tree ADR `/p/hg/safetensors-scala/docs/adr/0001-inline-versions.md`
now describes a state that no longer holds. The wiki-side ADR
adoption (with platforms-only deviation) is tracked in DM-008.

Refs:
[[projects/dependency-manager/tickets/0002-migrate-safetensors-to-deps]],
[[projects/dependency-manager/index]],
[[projects/safetensors-scala/index]],
[[tech/decisions/deps-single-file]]

---

## [2026-05-29] implement | toolbox migrated to dm catalog (DM-001)

Second consumer migration. Toolbox is the largest surface — 10
external libraries across 6 modules and 3 platforms (JVM/JS/Native).

### Mapping applied

| `V.<x>` (removed) | `Deps.<x>` (added) | Call sites |
|---|---|---|
| `V.munit` | `build.deps.Deps.munit` | `ToolboxTestSources.mvnDeps` (shared by every nested `test`) |
| `V.osLib` | `build.deps.Deps.osLib` | `procOslib.jvm` + `procOslib.native` |
| `V.kyoCore` | `build.deps.Deps.kyoCore` | `procKyo.jvm` + `procKyo.js` |
| `V.catsEffect` | `build.deps.Deps.catsEffect` | `procFs2.jvm` |
| `V.fs2` | `build.deps.Deps.fs2Core` + `build.deps.Deps.fs2Io` | `procFs2.jvm` (fans out 1→2) |
| `V.slm` | `build.deps.Deps.sourcelineManager` | `script.{jvm,js,native}` + `vfs.{jvm,js,native}` |
| `V.pprint` | `build.deps.Deps.pprint` | `example.jvm` |
| `V.sourcecode` | `build.deps.Deps.sourcecode` | `example.jvm` |
| `V.munitCatsEffect` | `build.deps.Deps.munitCatsEffect` | `procFs2.jvm.test` |

`object V` retains only `scalaVersions`, `scalaJS`, `scalaNative`,
`organization`, `projectVersion` — the platform-versions deferral
boundary from the design doc, codified in DM-008.

### `deps/package.mill` anchor

Added as the second per-consumer setup file (slm was the first).
One line: `package build.deps`. Without it, Mill 1.x ignores the
sibling `Dependencies.mill` and `mill resolve __` reports
unresolved `build.deps.Deps.*` paths.

### Verification

```
$ cd /p/hg/sourceline-manager && mill __.publishLocal      → SUCCESS
$ cd /p/hg/toolbox && mill resolve __                       → SUCCESS
$ cd /p/hg/toolbox && mill __.compile                       → 2659/2659 SUCCESS
$ cd /p/hg/toolbox && mill __.test                          → green across JVM/JS/Native
$ cd /p/hg/dependency-manager && bin/dm verify --project=toolbox
# toolbox                  OK

$ bin/dm extract --force --out=/tmp/dm-test /p/hg/toolbox \
                                            /p/hg/sourceline-manager \
                                            /p/hg/safetensors-scala
# toolbox                  10 unique coord(s)
# sourceline-manager       2 unique coord(s)
# safetensors-scala        3 unique coord(s)
# wrote 12 libraries → /tmp/dm-test/libs.versions.toml
# wrote 3 project(s)  → /tmp/dm-test/projects.yml

$ diff -r /tmp/dm-test /p/hg/dependency-manager/deps/ ; echo $?  → 0
```

Round-trip clean — re-extracting against the refactored toolbox
build.mill produces the same `(group, artifact, version)` tuples
the original inline-coords extract produced. The catalog is now
the single source of truth for toolbox's 10 external Maven deps.

### Observations

- **`fs2` fan-out** worked cleanly. The catalog already had
  `fs2-core` and `fs2-io` as separate entries (extracted from the
  initial bootstrap); the build.mill rewrite was a 1→2 textual
  expansion at one call site.
- **`V.slm` → `Deps.sourcelineManager`** crossed 6 call sites
  (script + vfs, JVM/JS/Native each); all replaced in a single
  `replace_all` sweep with no false positives because the
  surrounding `mvn"…"` pattern was identical.
- **`toolbox-script` / `toolbox-proc-oslib` / `toolbox-fluent`
  publish metadata untouched** — they are publishLocal'd artefacts,
  not Maven deps; catalog adoption is consumer-side only.

### Status round-up

`Current Blockers` item 4 from
`projects/dependency-manager/index.md` ("Downstream build.mill
migration") is now **mostly resolved**: slm + toolbox done,
safetensors-scala remaining (DM-002, next slice).

Refs:
[[projects/dependency-manager/tickets/0001-migrate-toolbox-to-deps]],
[[projects/dependency-manager/index]],
[[projects/toolbox/index]],
[[tech/decisions/deps-single-file]]

---

## [2026-05-29] implement | Consumer-side catalog loop closed (slm migrated to Deps)

First downstream `build.mill` switched from inline `object V` to
`build.deps.Deps.*` references — sourceline-manager picked as the
cheapest consumer (2 libraries, both munit-family). End-to-end
proof that the catalog flow works for a real consumer, not just
the producer-side regen/verify machinery.

### What changed

`/p/hg/sourceline-manager/build.mill`:

- Removed `V.munit` / `V.munitScalaCheck` (note: old code used
  capital-C `Check`; the catalog handle is `munit-scalacheck` which
  dm camel-cases to `munitScalacheck` — case difference is real and
  load-bearing for the import).
- `SlmTestSources.mvnDeps` rewritten from
  `Seq(mvn"org.scalameta::munit::${V.munit}", mvn"…scalacheck::${V.munitScalaCheck}")`
  to `Seq(build.deps.Deps.munit, build.deps.Deps.munitScalacheck)`.
- Added a one-line `deps/package.mill` anchor (`package build.deps`,
  nothing else) so Mill 1.x discovers `deps/Dependencies.mill` as a
  helper file. Without the anchor, Mill ignores sibling `.mill` files
  in folders that lack a `package.mill` or `build.mill` (verified
  against the upstream `mill/example/large/multifile/13-subdir-with-helper`
  pattern at `/p/gh/mill`).

### Verification

```
$ cd /p/hg/sourceline-manager
$ mill resolve __                  →  OK
$ mill __.compile                  →  338/338 SUCCESS (incl. test sources)
$ mill slm.jvm[3.8.3].test         →  140/140 tests green

$ cd /p/hg/dependency-manager
$ bin/dm verify                    →  all 3 project(s) in sync
$ bin/dm extract --force --out=/tmp/…  →  identical catalog to disk
                                          (12 libs, 3 projects unchanged)
```

The bidirectional verification is the important one: re-extracting
against the *refactored* build.mill produces the same `(group,
artifact, version)` tuples that the original inline-coords extract
produced, because Mill resolves `Deps.munit` back to its concrete
`mvn"…::1.0.3"` literal before exposing it via `mvnDeps`. The
catalog is now the single source of truth for slm's munit deps —
Renovate can bump `libs.versions.toml`, `dm regen` rewrites
`deps/Dependencies.mill`, next slm build picks up the new version.

### Anchor pattern observation

`deps/package.mill` is a **one-time per-project setup file**:

```scala
// Anchors the `deps/` folder so Mill 1.x discovers sibling `*.mill`
// helpers (notably `Dependencies.mill`, generated by `dm regen`).
package build.deps
```

It declares the package but defines no module, so `mill resolve __`
gains no spurious tasks. The file is hand-authored once per
consumer; dm doesn't (and shouldn't) generate it — generating an
anchor is a chicken-and-egg trap (dm would also need to know which
projects had been "opted in"). Possible follow-up: document the
anchor requirement in dm's README under "Adopting dm in a new repo".

This contradicts the wiki design page's implicit assumption that
`Dependencies.mill` alone is sufficient; the discovery requirement
should be reflected in [[tech/decisions/deps-single-file]] (which
shows the canonical `package build.deps` declaration but doesn't
flag the anchor pre-requisite).

### What this exposes

- **Naming case mismatch is a real adoption tax.** The slm code
  had `V.munitScalaCheck`; the dm catalog has `Deps.munitScalacheck`
  (matching the kebab `munit-scalacheck`). Other consumers will hit
  the same: any project that pre-dated dm and used different camel
  conventions must accept dm's kebab → camel transform. Acceptable
  but worth flagging.
- **The Mill discovery rule is non-obvious.** Took a detour into
  `/p/gh/mill/example/large/multifile/` examples to confirm the
  `package.mill` anchor requirement. The Mill llm-wiki at
  `mill/llm-wiki/patterns/build-file-structure.md` documents
  `package.mill` for *modules* but not for *helper-file discovery*.
  Worth a wiki edit pass over that page (separate operation).
- **Consumer-side validation was the missing piece.** Producer-side
  (extract / regen / verify) had been working since the earlier
  sessions, but until a `build.mill` actually imported `Deps`,
  there was no proof the generated file was usable. Now there is.

### Status round-up

`Current Blockers` item 4 from `projects/dependency-manager/index.md`
("Downstream `build.mill` migration") is **partially resolved**:
slm done, toolbox + safetensors-scala still inline. Updating
`index.md` to reflect that. Item 2 (initial git commit) still
human-gated. Items 1 and 3 already closed.

The four "Next implementation slice candidates" from the
*previous* implement entry are all addressed in production now —
extract / regen / verify / promote all working, Renovate config
validated, Mill DSL realised, three ADRs landed. The natural next
slices outside of dm itself are:

1. Migrate `toolbox/build.mill` to `Deps.*` (10 libraries — bigger
   surface; mention of `toolbox-script` etc. is via Maven coords
   not `Deps`, so the migration is purely on test/runtime deps and
   the kyo / fs2 / cats-effect surface).
2. Migrate `safetensors-scala/build.mill` to `Deps.*` (3 libraries).
3. Land the Renovate-proposed bumps (kyo RC1→RC2, fs2 3.12.0→3.13.0,
   munit 1.0.3→1.3.1, etc.) and observe the verify gate catch the
   drift before regen.
4. The dm in-tree `DESIGN.md` "Next steps when resuming" is stale;
   human-owned update.

Refs:
[[projects/dependency-manager/index]],
[[projects/dependency-manager/designs/dm-architecture]],
[[projects/sourceline-manager/index]],
[[projects/sourceline-manager/log]],
[[tech/decisions/deps-single-file]]

---

## [2026-05-29] adr | Land FDD, TDD-rhythm, symmetric-refactoring adoptions

Three deferred ADRs landed on now-substantial on-disk evidence:

- `adr/0002-adopt-functional-domain-design.md` — adopts
  [[tech/patterns/functional-domain-design]] unconditionally,
  declarative encoding. Cites two worked examples at different
  layers: `dm.catalog` (Coord / Library / Catalog ADTs + four
  format interpreters) and `dm.mill` (Cwd / Invocation DSL +
  three terminal interpreters `asText` / `asLines` / `asJson`).
- `adr/0003-adopt-tdd-rhythm.md` — adopts
  [[tech/patterns/tdd-rhythm]] with **one bounded exception**:
  Stage 2 *law-based* form not yet realised (no `forAll`
  quantified tests; the catalog algebra hasn't grown symmetric
  operators where they'd carry their weight). Exception closes
  when `merge` / `diff` / `union` operators on `Catalog` land.
  Stages 0, 1, 3, 4 all realised across 8 specs and 52 tests.
- `adr/0004-adopt-symmetric-refactoring.md` — adopts
  [[tech/patterns/symmetric-refactoring]] in the
  **parallel-module form** (distinct from sourceline-manager's
  operator-layer form). Three Reader / Writer dual pairs (TOML,
  YAML, Dependencies.mill); two verb pairs (Regen / Verify,
  Extract / Promote). The pair-of-pairs nesting (Writer/Reader
  *inside* Regen/Verify) is called out as pattern-on-pattern
  evidence.

`used_by` updated on all three tech pages.

Bounded exception declared in ADR-0003 with closing condition is
the only honest gap. Drift report should now show dm as
*declared* on FDD / TDD-rhythm / symmetric-refactoring (test
economics remains deferred — premature without `forAll` laws).

Refs:
[[projects/dependency-manager/adr/0002-adopt-functional-domain-design]],
[[projects/dependency-manager/adr/0003-adopt-tdd-rhythm]],
[[projects/dependency-manager/adr/0004-adopt-symmetric-refactoring]],
[[tech/patterns/functional-domain-design]],
[[tech/patterns/tdd-rhythm]],
[[tech/patterns/symmetric-refactoring]]

---

## [2026-05-29] implement | dm promote + Nix flake CI apps

Two slices in one session.

### `dm promote`

New `DependenciesMillReader`: walks a string and extracts every
`mvn"…"` literal via a simple regex, then delegates the
group/artifact/version split to `Coord.parse` (the longest-match
separator rule). Tolerant of hand-edits — `val` names, padding,
and surrounding context are all ignored. Five tests in
`DependenciesMillReaderSpec`: writer round-trip, all three
cross-kinds, ignoring non-mvn content, hand-edit tolerance,
empty input.

This **closes the third Writer/Reader pair** that
`adr/0004-adopt-symmetric-refactoring` cites
(`DependenciesMillWriter` ↔ `DependenciesMillReader`), removing
the bounded exception from the symmetric-refactoring adoption.

`Promote` verb:

- `Promote.collectDeltas(name, info, catalog)` — for one
  project: parse on-disk `Dependencies.mill`, build a
  `(group, artifact) → version` map, walk `catalog.libraries`
  restricted to `info.libraries` (the projects.yml whitelist),
  emit a `Delta(project, handle, group, artifact,
  catalogVersion, downstreamVersion)` whenever versions differ.
- `Promote.applyDeltas(catalog, deltas)` — pure: groups deltas
  by handle, warns on conflicting downstream versions across
  projects, returns the patched `Catalog`.
- `Promote.run(Options)` — orchestration. Catalog read, deltas
  collected per project. Without `--apply`: prints deltas, exits
  1. With `--apply`: prints deltas, rewrites `libs.versions.toml`
  via `TomlWriter.render(patched)`, exits 0. Missing catalog
  → 2. Empty filter → 2. No deltas → 0.

The whitelist rule (only consider libraries in the project's
`projects.yml` library list) is load-bearing: it stops a stray
`mvn"…"` line a human pasted in from being lifted into the
central catalog without an explicit projects.yml edit.

Seven tests in `PromoteSpec`: clean exits 0; dirty without
`--apply` exits 1; `--apply` rewrites catalog; non-listed
libraries are ignored; missing `Dependencies.mill` is skipped;
missing catalog exits 2; filter narrows scope.

**End-to-end verified** against the real catalog:

```
# Hand-edit toolbox: munit::1.0.3 → munit::1.0.4
$ bin/dm promote
# toolbox                  munit: 1.0.3 → 1.0.4
# 1 promotion(s) would be applied with --apply
$ echo $?  →  1

$ bin/dm promote --apply
# toolbox                  munit: 1.0.3 → 1.0.4
# applied 1 promotion(s) → /p/hg/dependency-manager/deps/libs.versions.toml
$ echo $?  →  0

$ bin/dm regen
# safetensors-scala        wrote 3 libraries ...
# sourceline-manager       wrote 2 libraries ...
# toolbox                  wrote 10 libraries ...

$ grep munit /p/hg/{toolbox,sourceline-manager,safetensors-scala}/deps/Dependencies.mill
# all three projects now report munit::1.0.4

$ bin/dm verify
# all 3 project(s) in sync
```

The catalog loop is now **machine-verified bidirectionally**:

- **Top-down**: Renovate / human edit catalog → regen → verify.
- **Bottom-up**: human edit downstream Mill → promote → regen
  (other projects) → verify.

Then restored to the source-of-truth versions via
`bin/dm extract --force` to leave the working tree clean.

### Nix flake apps

`flake.nix` grew an `apps.<system>.{test,verify,check,renovate-dryrun}`
attribute set. Each app is a `pkgs.writeShellApplication` with
its own `runtimeInputs` (the test/verify/check apps bundle
`jdk21 mill git`; the renovate app bundles `nodejs_22`). All
scripts trust the caller to invoke from inside the dm repo
(`cd "$PWD"`) — they're ergonomic shortcuts, not hermetic
derivations.

```bash
nix run .#test              # mill dm.test
nix run .#verify            # bin/dm verify against the on-disk catalog
nix run .#check             # test + verify back-to-back
nix run .#renovate-dryrun   # npx renovate --platform=local --dry-run=lookup
```

`nix flake check` passes (warnings about `lacks attribute 'meta'`
are cosmetic — adding meta to writeShellApplication outputs is a
follow-up if anyone cares). Verified all four apps work end-to-end
without dropping into `nix develop` first.

`nix run .#check` output ends with `==> all checks passed` and
exit 0; non-zero on the first failure (test or verify).

`devShells.default` also gained `mill` directly (was previously
only available via the system install), so a user inside `nix
develop` has the full toolchain without leaning on host PATH.

### `README.md` updated

- Verb table flipped from stub to working for all five verbs.
- Added a "CI shortcuts (Nix flake apps)" section.
- "Smoke test" section rewritten as "Typical workflow" covering
  extract → regen → verify → promote.

### Test count

| Spec | Tests |
|------|-------|
| `MainSmokeTest` | 2 |
| `CoordSpec` | 8 |
| `CatalogBuilderSpec` | 6 |
| `WritersSpec` | 7 |
| `ReadersSpec` | 11 |
| `DependenciesMillWriterSpec` | 9 |
| `RegenSpec` | 5 |
| `VerifySpec` | 5 |
| `MillSpec` | 6 |
| `DependenciesMillReaderSpec` | 5 |
| `PromoteSpec` | 7 |
| **Total** | **71** |

All green.

### Status round-up

Every numbered "Next steps" item from the original
`/p/hg/dependency-manager/DESIGN.md §"Next steps when resuming"`
list is now complete:

1. ✅ Compile error diagnosed + fixed (Scala 3 mixed-varargs syntax).
2. ✅ Smoke test: `bin/dm resolve /p/hg/toolbox` works.
3. ✅ `dm extract` against toolbox / slm / safetensors.
4. ✅ `dm regen` writes per-project Dependencies.mill.
5. ✅ `dm verify` CI-mode drift check.
6. ✅ `.renovaterc.json` + local Renovate dry-run validated.
7. ✅ `dm promote` ports hand-edits back into the catalog.

Outstanding items deferred to the in-tree `DESIGN.md §"Open
Questions"` are wiki-level architectural questions
(`/p/factory/` monorepo absorption, Native CLI target) and remain
deferred there. The in-tree `DESIGN.md` itself is now stale on
the "Where we stopped" / "Next steps" sections; due for an update
by the human (file is in-tree source-of-truth).

Refs:
[[projects/dependency-manager/index]],
[[projects/dependency-manager/adr/0002-adopt-functional-domain-design]],
[[projects/dependency-manager/adr/0003-adopt-tdd-rhythm]],
[[projects/dependency-manager/adr/0004-adopt-symmetric-refactoring]],
[[tech/patterns/symmetric-refactoring]]

---

## [2026-05-29] implement | Mill fluent DSL — toolbox dogfooding realised

User-directed slice. Background: dm declares
`toolbox-script` / `toolbox-proc-oslib` / `toolbox-fluent` as
dependencies (the dogfooding rationale in `DESIGN.md`) but until
now `MillQuery` shelled out via raw `os.proc("mill", args)` —
the deps were dead weight. User observation:

> "If the tools we use have a bit of options, probably we could
> wrap them using toolbox and have our own fluent api here in
> this project making code very easy on the eye."

Mill has half a dozen flags worth setting (`--ticker false`,
`--silent`, etc.) and we're about to grow more verbs
(`scalaBinaryVersion` queries for cross-platform suffix
canonicalisation, possibly `compile` for verify-then-build).
Verdict: write the wrapper.

### `dm.mill.Mill` — three-stage fluent DSL

```scala
Mill.in(projectDir)         // Stage 1: Cwd
   .resolve("__")            // Stage 2: Invocation (verb)
   .silently                 //          options...
   .asLines                  // Stage 3: execute + shape output
```

- **Stage 1** `Cwd(projectDir)`: directory locked; offers
  `resolve(pattern)` / `show(task)` / `raw(verb, args*)`.
- **Stage 2** `Invocation`: command built; opt-in `verbosely` or
  back to `silently` (the default). Both `derives CanEqual` for
  test ergonomics.
- **Stage 3** terminal exits: `asText` / `asLines` / `asJson` —
  each returns `Either[String, A]`. Mill failures bubble up as
  `Left` rather than uncaught exceptions.

Defaults: `--ticker false --silent`. Reason: dm parses Mill's
stdout; Mill's stderr progress indicators (`1] show`,
`1/1, SUCCESS]`) are noise when invoked non-interactively. The
defaults make `dm extract` output go from ~50 lines of interleaved
noise to:

```
# toolbox                  10 unique coord(s)
# sourceline-manager       2 unique coord(s)
# safetensors-scala        3 unique coord(s)
# wrote 12 libraries → ...
# wrote 3 project(s)  → ...
```

The `verbosely` toggle restores stderr noise for human debugging.

Implementation: ~80 lines on top of `proc.ProcessDescription` +
`proc.oslib.OsLibProcess`. Uses `OsLibProcess(desc).withCwd(d).call(stderr=os.Inherit)`
which mirrors the prior `os.proc` call exactly — same wire
behaviour, different type level.

### `MillQuery` collapsed to dm-glue

Before: 30 lines, threw on failure, no error context.

After: 18 lines, returns `Either[String, A]`, errors carry
"mill `<args>` (in `<dir>`): `<msg>`" context. Two methods
(`resolveAll` / `mvnDepsTaskPaths`) are a one-line `map` over
`Mill.in(...).resolve("__").asLines`; `show` is one line over
`.asJson`.

### Either threaded through callers

`Extract.extractCoords` was a side-effecting function returning
`Vector[Coord]` (silent on Mill failure). Now returns
`Either[String, Vector[Coord]]` via a for-comprehension over the
Mill calls. `Extract.run` `match`es on the outer aggregation
result: `Left` → exit 1 with `dm extract: <msg>`; `Right` → write
files.

`Resolve` (smoke verb) `match`es on `MillQuery.mvnDepsTaskPaths`
and per-task `MillQuery.show` — clean errors per call rather than
silent crashes.

### Tests

`MillSpec` adds 6 tests via the new `renderArgs` introspection
hook on `Invocation`:

- `resolve` renders `mill resolve <pattern>` with default flags.
- `show` renders `mill show <task>` with default flags.
- `verbosely` drops `--ticker false --silent`.
- `silently` restores defaults after `verbosely`.
- `raw` exposes arbitrary mill verbs.
- `Cwd` and `Invocation` are value-typed.

Pure-function tests; no real `mill` subprocess required at test
time. The end-to-end behaviour (extract + regen + verify against
toolbox / slm / safetensors) is what catches integration
regressions, not these unit tests.

Total: 54 tests across 9 specs, all green. End-to-end re-verified:
extract works, regen works, verify reports OK for all three
projects.

### Why this isn't over-engineering

Three independent signals:

1. **The toolbox deps were dead weight** — refactoring is the
   honest fix; the alternative was dropping the deps (and giving
   up the dogfooding pitch in `DESIGN.md`).
2. **Mill failure surfacing improved** — `Either` propagation is
   a correctness win on top of the readability win, not parallel
   to it.
3. **Foreshadowed growth** — the upcoming canonicalisation work
   needs `mill show <module>.scalaBinaryVersion` per platform per
   module. With `Mill.in(d).show(task).asText`, that's one line
   per query. With the old raw `os.proc`, each new query would
   have repeated the same try/catch/stderr-handling boilerplate.

### Wiki implications (queued)

The Mill DSL extends the declarative-encoding pattern of the
`dm.catalog` ADTs to the subprocess layer (`Cwd` and `Invocation`
are data; `as*` exits are interpreters). This strengthens the
on-disk evidence for the deferred
[[tech/patterns/functional-domain-design]] adoption ADR — when it
lands, it should cite both `dm.catalog` and `dm.mill` as worked
examples.

Refs:
[[projects/dependency-manager/index]],
[[projects/dependency-manager/designs/dm-architecture]],
[[sources/summaries/toolbox]],
[[tech/patterns/functional-domain-design]]

---

## [2026-05-29] implement | dm verify + Renovate config validated end-to-end

Picked up from the regen entry below. Two slices in one session.

### `dm verify` — CI-mode drift detection

`Verify.run(Options(catalogDir, projectFilter))`:

- Reads the catalog via `CatalogReader`.
- For each project, renders the expected `Dependencies.mill` via
  `DependenciesMillWriter.render` + `selectFor`.
- Compares byte-for-byte with the on-disk file. Missing file counts
  as drift.
- Prints OK / DRIFT per project. On drift, prints a line-level diff
  (paired walk with `<missing>` padding; first 10 differing pairs).
- Exit codes: 0 clean, 1 any drift, 2 setup error (missing catalog,
  empty filter match).

End-to-end verified:

```
$ bin/dm verify
# safetensors-scala        OK
# sourceline-manager       OK
# toolbox                  OK
# all 3 project(s) in sync

$ sed -i 's/1.0.3/1.0.4/' /p/hg/toolbox/deps/Dependencies.mill
$ bin/dm verify --project=toolbox
# toolbox                  DRIFT — /p/hg/toolbox/deps/Dependencies.mill
  L16: -   val munit             = mvn"org.scalameta::munit::1.0.3"
  L16: +   val munit             = mvn"org.scalameta::munit::1.0.4"
# 1 of 1 project(s) drifted
$ echo $?  →  1

$ bin/dm regen --project=toolbox  &&  bin/dm verify --project=toolbox
# toolbox                  OK  →  exit 0
```

CI integration is the obvious wrap: a workflow step runs
`bin/dm verify`; the build fails on exit 1 (drift) or exit 2 (the
catalog itself isn't readable). No additional flag handling needed.

`VerifySpec` adds 5 tests: all-in-sync→0, drifted→1, missing→1,
missing-catalog→2, filter-restricts + unknown-filter→2.

### `.renovaterc.json` — production Renovate config

Wrote a custom-managers regex config that:

- **Watches**: `^deps/libs\.versions\.toml$` only.
- **Scala-cross regex** (separator `::`): packageNameTemplate
  `{{groupId}}:{{artifactId}}_3` (the Scala 3 binary suffix needed
  for Maven Central lookups).
- **Java regex** (separator `:`): packageNameTemplate
  `{{groupId}}:{{artifactId}}` (no suffix).
- **`enabledManagers: ["custom.regex"]`** disables Renovate's native
  `gradle-version-catalogs` manager. The native manager auto-matches
  `libs.versions.toml` by filename and then chokes on our `::`
  Scala-cross syntax (which it doesn't recognise) — explicit override
  is necessary, not just nice-to-have.
- **packageRules**:
  - Disable `no.virtual-architect:**` (internal `publishLocal`
    artifacts not on Maven Central).
  - Skip `-SNAPSHOT` versions.
  - Group `io.getkyo:**`, `co.fs2:**`, MUnit family for lockstep
    bumps.

**File location deviation from `DESIGN.md`:** original design said
`deps/.renovaterc.json`. Renovate's auto-discovery only walks the
repo root for `.renovaterc.json` / `renovate.json` / etc., so the
file lives at `/p/hg/dependency-manager/.renovaterc.json`. Functional
equivalent: it still watches only the catalog file via `fileMatch`.
The wiki design page records the deviation; the in-tree `DESIGN.md`
should be touched up on the next ingest pass.

**Pitfalls hit and fixed:**

1. **Negative lookahead `(?!:)`** initially used to disambiguate the
   Java regex from `::` lines. Renovate uses **re2** (no
   lookaheads); config-validation rejected it with an "Invalid regExp"
   error. Resolved by relying on the character class
   `[a-zA-Z0-9._-]+` — `:` isn't in the class, so the engine cannot
   accidentally match the second `:` of a `::` line. Python
   pre-check confirmed 0 false positives on the Scala-cross lines.
2. **Native gradle manager double-extraction.** Renovate's
   gradle-version-catalogs manager auto-matches `libs.versions.toml`
   regardless of our config; it then emitted "Failed to look up
   maven package org.typelevel:" because the `::` group parsed as
   `org.typelevel` followed by an empty artifact. Fixed with
   `enabledManagers: ["custom.regex"]` — now only our regex extracts.

**Validated via `npx renovate --platform=local --dry-run=lookup`:**

| Library                | Current        | Renovate proposes |
|------------------------|----------------|-------------------|
| cats-effect            | 3.6.1          | 3.7-4972921       |
| fs2-core (grouped: fs2) | 3.12.0        | 3.13.0            |
| fs2-io   (grouped: fs2) | 3.12.0        | 3.13.0            |
| kyo-core (grouped: kyo) | 1.0-RC1       | 1.0.0-RC2         |
| munit (grouped: munit)  | 1.0.3         | 1.3.1             |
| munit-cats-effect       | 2.1.0         | 2.2.0             |
| munit-scalacheck        | 1.0.0         | 1.3.0             |
| os-lib                  | 0.11.7        | 0.11.8            |
| pprint                  | 0.9.4         | 0.9.6             |
| scodec-core             | 2.3.3         | (latest)          |
| sourcecode              | 0.4.4         | (latest)          |
| sourceline-manager      | 0.2.0-SNAPSHOT | **disabled**     |

All 12 libraries enumerated; Maven Central lookups succeeded; the
SNAPSHOT packageRule correctly disables the in-house artifact.
This is the upstream half of the catalog loop validated end-to-end.

### Catalog loop status

The full round-trip is now machine-verified:

```
Renovate (upstream)
   │
   │   patches libs.versions.toml
   v
dm extract / catalog  ←──────┐
   │                         │
   │   dm regen               │  dm promote (still stub)
   v                         │
<project>/deps/Dependencies.mill
   │                         │
   │   dm verify → CI gate   │
   v                         │
human hand-edits ────────────┘
```

Two boxes are stubs: `dm promote` (lowest-priority per design) and
the **downstream `build.mill` refactor** (per-project switch from
inline `object V.x` to `Deps.x` from the generated file). The
latter is out of scope for dm itself.

**Wiki implications (queued).** The four-deferred-ADRs situation
that was opened by the previous implement entry is now *more*
writable on on-disk evidence:

- `functional-domain-design` — `dm.catalog` ADTs unchanged.
- `tdd-rhythm` — 18 more tests added today, all written
  red-then-green. The pattern realisation is now broad enough to
  cite confidently.
- `symmetric-refactoring` — the Reader/Writer + Regen/Verify
  dual pairs are visible across the codebase (`TomlReader` ↔
  `TomlWriter`, `YamlReader` ↔ `YamlWriter`, `Regen` ↔ `Verify`).
  Three pair instances is enough evidence for adoption.
- `test-economics` — still premature in the strict sense (no
  property-based laws yet on the catalog algebra), but the
  Reader/Writer round-trip is a property-style test that
  amortises across every library/project shape. Borderline
  writable.

Total test count now: 53 across 8 specs, all green.

Refs:
[[projects/dependency-manager/index]],
[[projects/dependency-manager/designs/dm-architecture]],
[[tech/patterns/symmetric-refactoring]],
[[tech/patterns/functional-domain-design]],
[[tech/patterns/tdd-rhythm]]

---

## [2026-05-29] implement | dm regen working end-to-end via TOML+YAML readers

Picked up from the implement entry below (extract working). The session:

**TOML+YAML readers added.** Per-format AST walkers, no codec
derivation:

- `TomlReader.parse(src)` walks `toml.Value.Tbl` → reads
  `[libraries]`, extracts `module` + `version` strings per entry,
  splits the module string back into `(group, artifact, CrossKind)`
  using the same longest-separator rule as `Coord.parse`. Returns
  `Either[String, Vector[(String, Library)]]`.
- `YamlReader.parse(src)` walks `Node.MappingNode` / `SequenceNode`
  / `ScalarNode` → reads `projects.<name>.path` + `libraries`.
  Returns `Either[String, Vector[(String, ProjectInfo)]]`.
- `CatalogReader.read(tomlPath, ymlPath)` combines both and runs
  cross-file validation: every library handle a project references
  must exist in `[libraries]`. Dangling refs surface up-front as a
  single `String` error rather than silently rotting downstream.

Pitfall caught: `Node.MappingNode` / `SequenceNode` / `ScalarNode`
unapply only 2 fields (the `pos: Option[Range]` is excluded), so
pattern matches must be `(m, _)` not `(m, _, _)`. Easy fix once the
class file signatures were dumped via `javap`.

**`dm regen` verb implemented.** New module
`DependenciesMillWriter`:

- `render(Vector[(handle, Library)]): String` — emits the
  `package build.deps` / `import mill.*, scalalib.*` / `object Deps`
  shape with one `val` per library. Variable names are
  kebab→camelCase converted (`os-lib` → `osLib`,
  `munit-cats-effect` → `munitCatsEffect`,
  `sourceline-manager` → `sourcelineManager`). `=` columns are
  padded so vals align visually.
- `selectFor(libs, projectInfo)` — restricts the catalog libraries
  to the ones a project actually references, preserving sort order.

`Regen` verb takes `Options(catalogDir, projectFilter, dryRun)`:

- `dm regen` — write all projects' Dependencies.mill from the
  default catalog (`<dm-home>/deps/`).
- `dm regen --catalog=<dir>` — alternate catalog location.
- `dm regen --project=<name>` — restrict to one project.
- `dm regen --dry-run` — print what would be written instead.
- Filter-matches-nothing exits 2; missing catalog files exit 2.

**End-to-end verified.** Ran against the real catalog produced by
the previous `extract` session:

```
# safetensors-scala        wrote 3 libraries → /p/hg/safetensors-scala/deps/Dependencies.mill
# sourceline-manager       wrote 2 libraries → /p/hg/sourceline-manager/deps/Dependencies.mill
# toolbox                  wrote 10 libraries → /p/hg/toolbox/deps/Dependencies.mill
```

All three `deps/` directories surfaced as untracked in `git status`
— no pre-existing files were clobbered. The toolbox file in
particular round-trips the full 10-library catalog (`catsEffect`,
`fs2Core`, `fs2Io`, `kyoCore`, `munit`, `munitCatsEffect`,
`osLib`, `pprint`, `sourcecode`, `sourcelineManager`), each with
the `org::artifact::version` cross-source form preserved exactly.

`--dry-run --project=sourceline-manager` correctly prints to stdout
without writing.

**TDD.** Added two new specs:

- `ReadersSpec` (11 tests) — TOML round-trip via writer+reader,
  missing/malformed field rejection, empty `[libraries]`, missing
  `[libraries]`, YAML round-trip, missing `path`, empty / missing
  `libraries` lists, full Catalog round-trip via tmp files, dangling
  library reference error.
- `DependenciesMillWriterSpec` (9 tests) — `kebabToCamel`,
  determinism, banner presence, package/import lines, cross-kind
  separator rendering, camelCase val names, `=` column alignment,
  empty library list edge case, `selectFor` ordering preservation.
- `RegenSpec` (5 tests) — writes Dependencies.mill into each
  project's `deps/`, `--project=<name>` filter, unknown filter
  exits 2, missing catalog exits 2, project gets only its
  referenced libraries.

Total test count: 48 across 7 specs, all green.

**Symmetric structure detected (deferred-promotion candidate).**
The catalog round-trip is now closed: `Writer` (Catalog → file)
and `Reader` (file → Catalog) are dual. `WritersSpec` and
`ReadersSpec` cover this directly with `writer→reader` and
`reader→writer→reader` property checks (the latter via the
tmp-file Catalog round-trip). This is on-disk evidence of
[[tech/patterns/symmetric-refactoring]] — the pattern's
"preserve symmetric duplication, name the algebra" decision-tree
move 1, realised as parallel modules. Worth a follow-up ADR once
`verify` lands and adds a third paired op.

**Wiki implications (still queued).**

- ADRs against [[tech/patterns/functional-domain-design]],
  [[tech/patterns/tdd-rhythm]], [[tech/patterns/symmetric-refactoring]]
  are now all writable on on-disk evidence. Defer to a dedicated
  ADR session.
- The source bridge (`sources/tmp/code/dependency-manager.md`) and
  summary (`sources/summaries/dependency-manager.md`) "verb status"
  tables are stale. Update on next ingest pass.

**Next implementation slice candidates** (in priority order):

1. **`dm verify`** — easy now: read catalog, regen into a tmp dir,
   walk every project's `deps/Dependencies.mill` on disk, diff
   against the regen output. Exit 0 if clean, non-zero on first
   mismatch. Hooks straight into CI.
2. **`.renovaterc.json`** — customManagers regex against
   `libs.versions.toml`. Verify with `npx renovate
   --platform=local`. Closes the upstream half of the catalog
   loop.
3. **`dm promote`** — port a hand-edit in a downstream
   `Dependencies.mill` (or the `mvn"…"` inline in `build.mill`)
   back into a `libs.versions.toml` patch. Closes the downstream
   half. Lowest priority — only matters once humans hand-edit.

Refs:
[[projects/dependency-manager/index]],
[[projects/dependency-manager/designs/dm-architecture]],
[[tech/patterns/symmetric-refactoring]],
[[tech/patterns/functional-domain-design]],
[[tech/patterns/tdd-rhythm]]

---

## [2026-05-29] implement | Compile error resolved, dm extract working end-to-end

Picked up from the ingest entry below. The session:

**Compile error diagnosed and fixed.** Single Scala 3 issue in
`dm/src/millq/MillQuery.scala:38`:

```scala
val proc = os.proc("mill", args*)    // forbidden in Scala 3
```

Scala 3 disallows mixing a positional literal with a varargs spread
at the same call site — the spread must be the only argument to the
repeated parameter. Fix: pass `args` as a single Iterable[String]
Shellable, which os-lib's `os.proc(commands: os.Shellable*)`
accepts via its built-in Iterable conversion:

```scala
val proc = os.proc("mill", args)     // ✓
```

This was first in the design doc's "Likely causes" list as a
priority-4 guess; turned out to be priority-1 in actuality. The
toolbox / slm / safetensors-scala `publishLocal` precondition was
already satisfied (compile succeeded immediately after the syntax fix).

**Domain ADT introduced.** Created `dm.catalog` package:

- `CrossKind` — enum (`Java` / `Scala` / `Full`) capturing the
  Maven-coordinate separator (`:` / `::` / `:::`). `derives CanEqual`.
- `Coord(group, artifact, version, cross)` — case class with
  `parse: String => Either[String, Coord]`, `render`, and
  `moduleString` (drops version). Total functions, no exceptions.
  Round-trip property tested.
- `Library` — TOML library entry (group + artifact + version + cross).
- `ProjectInfo` — YAML project entry (path + sorted library handles).
- `Catalog(libraries, projects)` — top-level state, sorted by handle.
  `Catalog.empty` initial value.
- `CatalogBuilder.fromProjects(Vector[Input])` — pure function:
  inputs → `Catalog` with deterministic ordering, library-handle
  collisions disambiguated via group short-name prefix.
- `TomlWriter.render(Catalog)` and `YamlWriter.render(Catalog)` —
  pure, deterministic, no third-party serializer dependency
  (output is hand-rolled, kept small and diff-friendly).

This is the first real domain ADT in dm. All types are
`derives CanEqual`, all transformations are total functions, errors
are `Either[String, A]`. The pattern is the declarative encoding of
[[tech/patterns/functional-domain-design]] — same shape as
[[projects/sourceline-manager/adr/0001-adopt-functional-domain-design]]
and [[projects/toolbox/adr/0001-adopt-functional-domain-design]].

**`dm extract` verb implemented end-to-end.** New `Extract` object
takes `Options(projectDirs, outDir, force)`, runs `MillQuery` on each
project, parses coords, builds the catalog, writes both files. CLI
flags: `--force` (overwrite existing), `--out=<dir>` (override default).
Default output is `<dm-home>/deps/` resolved via the `dm.home` system
property (set by `bin/dm` via `-Ddm.home=$here`). Falls back to
`./deps` if invoked directly via `java -jar`.

End-to-end verified against the three v1 targets:

```
# toolbox                  10 unique coord(s)
# sourceline-manager       2 unique coord(s)
# safetensors-scala        3 unique coord(s)
# wrote 12 libraries → /p/hg/dependency-manager/deps/libs.versions.toml
# wrote 3 project(s)  → /p/hg/dependency-manager/deps/projects.yml
```

`munit` correctly deduped across all three projects (single library
entry, three project entries reference it). `munit-scalacheck`
deduped across sourceline-manager + safetensors. No drift detected
in shared versions. The `--force` guard works: re-running without
the flag prints a clear error and exits 2.

**TDD-driven.** 23 tests across 4 specs (all green):

- `CoordSpec` (8 tests) — parser correctness, edge cases (empty
  input, mixed separators, empty parts), round-trip property,
  `moduleString` projection.
- `CatalogBuilderSpec` (6 tests) — empty input, single-coord case,
  duplicate dedup, cross-project sharing, input-order-invariant
  determinism, group-prefixed collision disambiguation.
- `WritersSpec` (7 tests) — TOML scala-cross `::`, TOML java `:`,
  TOML determinism, TOML header presence, YAML structure, YAML empty
  libraries `[]`, YAML determinism.
- `MainSmokeTest` (2 tests, pre-existing) — help dispatch, no-args.

Each test class was written *before* the production code (red →
green → next test). This is the first dm code session driven by
TDD; the v1 scaffold smoke tests were not.

**Wiki implications.**

- The four deferred ADRs flagged in the original ingest log can be
  partially revisited:
  - `functional-domain-design` — adoption is now writable on
    on-disk evidence (Coord, Library, Catalog ADTs with the
    declarative-encoding shape). A future ADR session can land
    `adr/0002-adopt-functional-domain-design` citing
    `dm/src/catalog/` directly.
  - `tdd-rhythm` — every test in the new specs preceded its
    production code; the pattern fits the same rhythm
    sourceline-manager realises. A future ADR session can land
    `adr/0003-adopt-tdd-rhythm` on evidence (the test suite +
    the type-first ordering).
  - `test-economics` / `symmetric-refactoring` — still premature.
    No symmetric operators on the algebra yet (no `merge` /
    `union` / `diff` operators); test economics is favourable but
    the catalog hasn't grown enough to demonstrate amortisation.
    Defer until `regen` and `verify` introduce more types.
- The source bridge (`sources/tmp/code/dependency-manager.md`) and
  summary (`sources/summaries/dependency-manager.md`) should be
  updated on the next ingest pass — the "verb status" table is now
  stale, and the `extract` row in particular should reflect the
  on-disk evidence rather than the stub state. Deferred to keep
  this entry focused.

**Next implementation slice candidates** (in priority order — next
session picks one):

1. **`dm regen`** — read `libs.versions.toml` + `projects.yml`,
   write `<project>/deps/Dependencies.mill` per project. Requires
   TOML+YAML readers (parsers are dependencies already; the parsing
   itself lives in `dm.catalog.{TomlReader, YamlReader}`).
2. **`dm verify`** — easy once `regen` exists: regen into a tmp
   dir, walk both trees, diff each `Dependencies.mill`.
3. **`.renovaterc.json`** — customManagers regex against
   `libs.versions.toml`. Tested with `npx renovate
   --platform=local`.
4. **`dm promote`** — lowest priority; only matters once humans
   hand-edit a downstream Mill file.

Refs:
[[projects/dependency-manager/index]],
[[projects/dependency-manager/designs/dm-architecture]],
[[tech/patterns/functional-domain-design]],
[[tech/patterns/tdd-rhythm]],
[[sources/summaries/dependency-manager]]

---

## [2026-05-29] ingest | Project registered in wiki

Ingested `/p/hg/dependency-manager` as a wiki project. The repository
is **not git-initialised** at ingest time (no `.git` directory), so
no commit SHA exists yet — the source bridge records
`commit: uninitialized-tree`. Per the personal-repo commit policy
(`feedback_hg_repo_commit_policy`), `git init` and the first commit
are the human's call.

Created wiki-side artefacts:

- `projects/dependency-manager/index.md` — project landing page with
  stack, code-location pointer, embedding path, and verb status.
- `projects/dependency-manager/adr/0001-deviate-deps-single-file.md` —
  deviates from the global single-file deps decision *in dm's own
  `build.mill`*. Rationale: dm IS the tool that produces compliant
  single-file `Dependencies.mill` files in *other* repos; the
  bootstrap chicken-and-egg is resolved by hand-authoring `object V`
  once. Severity: medium (the dep count is non-trivial — six library
  coordinates plus platform versions — but the deviation is
  structurally honest).
- `projects/dependency-manager/designs/dm-architecture.md` — the
  in-tree `DESIGN.md` ingested as a `design-doc`. Covers the two-file
  canonical catalog (TOML + YAML), TOML-as-source-of-truth, per-repo
  `Dependencies.mill` committed downstream, Renovate-only-here, the
  drift loop (`verify` + `promote`), 17 chronological decisions, and
  the open questions about `/p/factory/` and a Native target.
- `sources/summaries/dependency-manager.md` — distilled summary
  covering verbs, build wiring, Mill metadata extraction, the
  TOML+YAML rationale, the toolbox dogfooding relationship, and a
  compliance scan.
- `sources/tmp/code/dependency-manager.md` — source bridge staged for
  human promotion to `sources/raw/code/dependency-manager.md` once
  the project is git-initialised and committed.

Populated `used_by` on [[tech/decisions/deps-single-file]] with the
new dm ADR.

Added a row to [[index]] §Projects between toolbox and the planned
webapp.

ADRs deliberately *not* written at this ingest:

- [[tech/patterns/functional-domain-design]] — no domain ADT exists
  yet at v1; an adoption ADR would claim evidence that is not on disk.
  Lands when `dm extract` introduces the TOML catalog model.
- [[tech/patterns/tdd-rhythm]],
  [[tech/patterns/symmetric-refactoring]],
  [[tech/patterns/test-economics]] — the v1 code surface is CLI
  plumbing with two trivial smoke tests; there is no algebra, no
  rhythm, no economics signal to record. Lands when behaviour
  materialises with extract / regen / verify / promote.

[[meta/drift]] will surface the four "missing declaration" entries
in the next lint pass; that is the intended mechanism — the ADRs
land when the code does.

Notable observations from the ingest:

- dm is the **fourth project** to land in the wiki and the **third
  in `/p/hg/` with a code presence** (after sourceline-manager and
  toolbox; safetensors-scala has its own folder under
  `/p/wiki/projects/`).
- dm is the **first wiki-managed project whose entire purpose is to
  automate a wiki-resident decision** — it implements a generalised
  version of [[tech/decisions/deps-single-file]] across the `/p/hg/`
  repos. If the wiki later grows a cross-project version-policy
  page, dm is its in-house implementation. Worth a synthesis once
  the catalog is populated and at least one downstream
  `Dependencies.mill` has been regenerated end-to-end.
- dm is the **first project ingested as `private / unlicensed`**.
  README states "Unlicensed. Not for distribution." The wiki itself
  does not enforce a licensing policy; this raises an open question
  flagged in the summary §"What this exposes that prior projects
  did not".
- dm is the **third project** to consume toolbox via Maven
  coordinates (after the future webapp and any other consumer to
  come). The `publishLocal` ordering documented in
  [[tech/stack/mill]] is the operational handle: toolbox must
  `publishLocal` before dm can compile.
- **Generated-output single-file conformance** — `dm regen` will
  produce per-project `Dependencies.mill` files in downstream repos
  that conform to [[tech/decisions/deps-single-file]] *by
  construction* (with a DO-NOT-EDIT banner). If the same shape
  recurs elsewhere (generated nix lockfiles, generated build
  manifests), it is a candidate for a tech-layer pattern page.
  Defer until it recurs.
- **Compile error not yet diagnosed.** `DESIGN.md` records this
  explicitly under §"Where we stopped". The wiki ingest does not
  attempt to fix it — the bridge documents the suspected causes;
  the next code session should reproduce, capture, and address.

Refs:
[[projects/dependency-manager/index]],
[[projects/dependency-manager/adr/0001-deviate-deps-single-file]],
[[projects/dependency-manager/designs/dm-architecture]],
[[sources/summaries/dependency-manager]],
[[sources/tmp/code/dependency-manager]],
[[tech/decisions/deps-single-file]],
[[sources/summaries/toolbox]],
[[sources/tmp/code/toml-scala]]

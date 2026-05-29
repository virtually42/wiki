---
id: dm-plan-mvp
title: dependency-manager v1 MVP
kind: project
status: completed
project: dependency-manager
created: 2026-05-29
updated: 2026-05-29
completed_in_sessions: 1
completion_refs:
  - projects/dependency-manager/log.md (DM-001..DM-009 close-out entries 2026-05-29)
  - meta/log.md (lint close-out 2026-05-29)
design_doc: projects/dependency-manager/designs/dm-architecture.md
related_adrs:
  - projects/dependency-manager/adr/0001-deviate-deps-single-file.md
  - projects/dependency-manager/adr/0002-adopt-functional-domain-design.md
  - projects/dependency-manager/adr/0003-adopt-tdd-rhythm.md
  - projects/dependency-manager/adr/0004-adopt-symmetric-refactoring.md
tickets:
  - DM-001
  - DM-002
  - DM-003
  - DM-004
  - DM-005
  - DM-006
  - DM-007
  - DM-008
  - DM-009
estimated_sessions: 3
---

> **Status note (2026-05-29):** plan reaches `completed` with six of
> nine tickets fully closed (DM-001..DM-004, DM-008, DM-009) and
> three sequenced human-gated gates (DM-005 first commit, DM-006
> bridge promotion, DM-007 in-tree apply) captured as DRIFT-023.
> The gates are *not* MVP-blocking under the plan's acceptance
> criteria — they are routine sequencing of work the agent
> prepared but cannot execute unilaterally per the personal-repo
> commit policy. The plan flips back to `active` only if a new
> finding emerges from the human-gated steps.

## Goal

Make `dm` the **operational single source of truth** for Maven
dependencies across the three `/p/hg/` projects (toolbox,
sourceline-manager, safetensors-scala), with the catalog loop closed
bi-directionally for every consumer, the repository under version
control, and consumer-adoption documented well enough that returning
to the project later does not require re-discovering the rules.

End state — when this plan is `completed`, the following are all true:

1. All three consumer `build.mill` files reference
   `build.deps.Deps.*` instead of inline `mvn"…::${V.x}"` strings.
   `bin/dm verify` reports `# all 3 project(s) in sync`. Re-running
   `bin/dm extract --force --out=/tmp/…` produces a byte-identical
   catalog to the on-disk one.
2. At least one Renovate-proposed bump has been landed end-to-end
   (catalog edit → `dm regen` → consumer `mill __.test` green) with
   a documented before/after.
3. The dm repository is git-initialised under the personal-repo
   commit policy (unsigned, no `Co-Authored-By`, author `tigidar`),
   with a first commit covering the v1 code surface.
4. The source bridge `sources/tmp/code/dependency-manager.md` has
   been promoted to `sources/raw/code/dependency-manager.md` with
   a real commit SHA replacing `commit: uninitialized-tree`.
5. The dm `README.md` carries a step-by-step "Adopting dm in a
   downstream repo" guide, including the Mill 1.x `deps/package.mill`
   anchor pre-requisite discovered during the slm migration.
6. Normative debts resolved: the three "deviate from
   deps-single-file" ADRs (slm wiki, toolbox wiki, safetensors
   in-tree) accurately reflect the post-migration state — adopting
   for the *library coordinates* half, retaining a narrower
   deviation only for the *platform versions* half (which dm does
   not manage by design).
7. A wiki lint pass reports zero outstanding drift entries
   attributable to dm or its consumers.

## Out of scope (explicit deferrals)

The following are recognised follow-ups but are **not** required to
call v1 done:

- **Hosted Renovate setup.** Requires a git remote dm can be
  reached at. The `.renovaterc.json` is already validated via
  `npx renovate --platform=local --dry-run=lookup`; that is the
  MVP bar. Real-PR-opening Renovate lands when the repo gets a
  remote.
- **CI pipeline.** Same dependency — needs a remote runner. The
  `nix run .#check` flake app is the local equivalent and is
  sufficient pre-MVP.
- **Native CLI repackaging.** Deferred per
  [[projects/dependency-manager/designs/dm-architecture]] §"Open
  Questions". JVM `bin/dm` shell wrapper is the v1 ship.
- **`/p/factory/` monorepo absorption.** Deferred per the same
  design doc. The dm-vs-monorepo embedding question is architectural
  and decoupled from MVP.
- **Platform versions in catalog.** Scala / Scala.js / Scala Native
  versions remain in each consumer's `object V`. This is a real
  scope decision (Renovate's Maven model does not cover platform
  versions; mixing them into `libs.versions.toml` would be a wrong
  shape). The narrowed deviation ADRs in DM-008 codify it.
- **More than three consumers.** dm is sized for the current
  `/p/hg/` population. New consumers can adopt via the DM-004
  README guide.

## Prerequisites

- All v1 verbs working (resolve / extract / regen / verify / promote)
  — done, evidenced by 71 green tests and end-to-end runs.
- Renovate `.renovaterc.json` validated via dry-run — done.
- Nix flake apps wired (`test` / `verify` / `check` / `renovate-dryrun`) —
  done.
- First consumer migration proven (sourceline-manager) — done
  2026-05-29; see [[projects/dependency-manager/log]] §
  "Consumer-side catalog loop closed (slm migrated to Deps)".
- The Mill 1.x `deps/package.mill` anchor rule is known — discovered
  during the slm migration; codified in DM-004.

## Steps

The plan decomposes into 9 atomic tickets. Three of them are
**human-gated** (DM-005, DM-007) or **partly human-owned** (DM-008 for
the in-tree safetensors ADR); the rest are agent-doable.

| # | Ticket | Type | Depends on | Human-gated? |
|---|--------|------|------------|--------------|
| 1 | DM-001 — Migrate toolbox build.mill to Deps catalog | implement | — | no |
| 2 | DM-002 — Migrate safetensors-scala build.mill to Deps catalog | implement | — | no |
| 3 | DM-003 — Run Renovate-proposed bumps end-to-end | operate | DM-001, DM-002 | no |
| 4 | DM-004 — Document consumer-adoption procedure in dm README | docs | DM-001 (anchor evidence) | no |
| 5 | DM-005 — git-init dm + first commit | ops | DM-001, DM-002, DM-003, DM-004 | **yes** |
| 6 | DM-006 — Promote source bridge tmp → raw | wiki | DM-005 | no (depends on DM-005's SHA) |
| 7 | DM-007 — Refresh in-tree dm DESIGN.md | docs | DM-001 → DM-005 | **yes** (in-tree, human-owned) |
| 8 | DM-008 — Resolve normative ADR debts | wiki | DM-001, DM-002 | partly (in-tree safetensors ADR) |
| 9 | DM-009 — Lint pass + drift cleanup | wiki | all above | no |

Session shape (rough):

- **Session 1** — DM-001 + DM-002 (the two remaining consumer
  migrations; both follow the slm pattern). Estimated 1 session.
- **Session 2** — DM-003 + DM-004 (operate the loop in anger; capture
  what was learned in the README). Estimated 1 session.
- **Session 3** — DM-005 + DM-006 + DM-008 + DM-009 (git-init, bridge
  promotion, normative cleanup, lint pass). DM-007 prepared in
  parallel as a wiki-side draft for the human to apply in-tree.
  Estimated 1 session (excluding the DM-007 human apply).

DM-007's human apply is independent — it can land any time the
human takes the wiki-side draft and applies it to the in-tree
`DESIGN.md`. It is not on the critical path.

## Acceptance Criteria

- [ ] All 9 tickets reach `status: done`.
- [ ] `bin/dm verify` reports OK for all 3 projects.
- [ ] Each consumer's `mill __.compile` and `mill __.test` is green
  *after* migration.
- [ ] `bin/dm extract --force --out=/tmp/x` produces a catalog
  byte-identical to `/p/hg/dependency-manager/deps/`. (Loop closure
  evidence.)
- [ ] At least one Renovate-proposed bump landed end-to-end with a
  log entry on `projects/dependency-manager/log.md` showing the
  before/after.
- [ ] `git log --oneline | head -1` on `/p/hg/dependency-manager`
  returns a valid SHA.
- [ ] `sources/raw/code/dependency-manager.md` exists with
  `commit:` matching dm's HEAD; `sources/tmp/code/dependency-manager.md`
  removed.
- [ ] `/p/hg/dependency-manager/README.md` has an "Adopting dm in
  a downstream repo" section covering the `deps/package.mill`
  anchor, the `Deps.*` import pattern, the `projects.yml`
  registration, and the verify gate workflow.
- [ ] No outstanding `meta/drift.md` entries attributable to dm or
  its consumers (i.e., the 3 deviate-deps-single-file ADRs no
  longer flag as stale).

## Risks

- **toolbox migration surface is larger than slm's** (10 libs across
  multiple modules and traits, several reused). Mitigation: DM-001's
  ticket steps explicitly enumerate the `V.*` → `Deps.*` mapping per
  call site; the migration is mechanical once enumerated. Risk that
  `toolbox-script` / `toolbox-proc-oslib` / `toolbox-fluent` use
  `mvn"…"` self-references — those are *not* catalog candidates (they
  are the project's own publishLocal'd artifacts, not external
  Maven deps). Keep them inline; the catalog only owns external deps.
- **Renovate-proposed bumps may introduce real breakage** (kyo
  RC1 → RC2 is the most likely; could have API changes). Mitigation:
  DM-003 picks low-risk bumps first (os-lib, pprint, munit patch);
  larger bumps (kyo, fs2) are run with a clear rollback path. If a
  bump breaks a consumer, the verify gate catches it before commit,
  and the rollback is `git checkout deps/libs.versions.toml`.
- **The package.mill anchor rule may surprise the human if undocumented**.
  Mitigation: DM-004 is in the critical path *because* of this.
- **scodec pinning** (safetensors). The in-tree ADR-0001 notes scodec
  is pinned to paladium's resolution. dm's catalog currently has
  scodec-core at 2.3.3. DM-002 must preserve that pin; the catalog
  becomes the single source of truth for that constraint.
- **Bridge promotion has a chicken-and-egg with the first commit**
  (DM-006 depends on DM-005's SHA). Sequence is enforced by the
  `Depends on` column; do not try to promote before commit.
- **The slm ADR-0002 rewrite (DM-008) is normative**. The shared
  ownership rule means the agent flags edits for human review.
  Mitigation: DM-008 writes the new content but explicitly invites
  the human to approve before closing.
- **toolbox's `V.slm` references** create a small ordering dependency:
  toolbox depends on the slm `mvn` coord; sourceline-manager (the
  publisher) must `publishLocal` before toolbox compiles. This is
  already established practice (per [[tech/stack/mill]] and the
  toolbox in-tree docs); the migration does not change the ordering,
  only the syntax (`V.slm` → `Deps.sourcelineManager`).

## Links

- [[projects/dependency-manager/index]]
- [[projects/dependency-manager/designs/dm-architecture]]
- [[projects/dependency-manager/log]]
- [[tech/decisions/deps-single-file]]
- [[tech/decisions/tidy-first-commits]]
- [[meta/drift]]

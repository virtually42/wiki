---
id: dm-architecture-2026q2-refresh
title: dm DESIGN.md refresh proposal (2026-Q2)
kind: descriptive
status: superseded
project: dependency-manager
created: 2026-05-29
updated: 2026-05-29
mirrors: /p/hg/dependency-manager/DESIGN.md
---

> **Superseded 2026-05-29.** The human chose **option B** (strip
> DESIGN.md to decisions + open questions) rather than the
> four-block in-place rewrite proposed below. The in-tree
> `/p/hg/dependency-manager/DESIGN.md` was rewritten to keep only
> the architectural decisions, tool/library decisions, the 17
> chronological decisions, the Renovate/Gradle clarification, and
> the open questions (incl. the new platforms-in-catalog entry).
> The wiki mirror at
> [[projects/dependency-manager/designs/dm-architecture]] was
> refreshed to match. This document is retained as the original
> proposal record.

## Purpose

The in-tree `/p/hg/dependency-manager/DESIGN.md` was authored during
the design conversation on 2026-05-29, before the v1 implementation
landed. Three sections are now stale:

1. §"Where we stopped" — claims a compile error not yet diagnosed;
   the error was diagnosed and fixed in the first implement
   session.
2. §"Next steps when resuming" — lists 8 items, all of which were
   closed during the 2026-05-29 implement sessions plus the
   DM-001..DM-004 work in this same date.
3. §"dm verb status" — lists 4 of 5 verbs as `stub`; all five are
   `working` now.
4. §"Repo layout" — `.renovaterc.json` shown at `deps/.renovaterc.json`;
   actual location is repo root (Renovate auto-discovery only
   walks the root).

This refresh document is a **wiki-side draft**. The in-tree file
is human-owned (in-tree, outside the wiki's ownership claim). The
human takes the §"Suggested in-tree apply" block below and edits
`DESIGN.md` directly; on confirmation, the wiki-side mirror at
`projects/dependency-manager/designs/dm-architecture.md` is
refreshed to match.

## Evidence

Each proposed rewrite below cites the wiki log entries that
captured the closure of the originally-open item:

| In-tree claim | Wiki log entry (date / heading) | Status |
|---|---|---|
| Compile error not yet diagnosed | 2026-05-29 implement — Compile error resolved, dm extract working | closed |
| Smoke test pending | same | closed |
| toolbox publishLocal pending | superseded — both toolbox and slm publishLocal'd in current session | closed |
| `dm extract` stub | 2026-05-29 implement — Compile error resolved, dm extract working | closed |
| `dm regen` stub | 2026-05-29 implement — dm regen working end-to-end via TOML+YAML readers | closed |
| `dm verify` stub | 2026-05-29 implement — dm verify + Renovate config validated end-to-end | closed |
| `.renovaterc.json` not yet written | same | closed |
| `dm promote` stub | 2026-05-29 implement — dm promote + Nix flake CI apps | closed |
| `.renovaterc.json` at `deps/.renovaterc.json` | same — note "File location deviation" | corrected: repo root |
| toolbox / safetensors-scala migration pending | 2026-05-29 implement — toolbox migrated to dm catalog (DM-001), safetensors-scala migrated (DM-002) | closed |

The verb status table needs the same flip every verb (`stub` →
`working`) and reuses the row text from the wiki-side
`projects/dependency-manager/index.md` §"Verb Status" table —
that one is current.

## Suggested in-tree apply

Replace the in-tree `DESIGN.md`'s §"dm verb status", §"Where we
stopped", §"Next steps when resuming", and §"Repo layout"
(the `.renovaterc.json` line) with the blocks below. Other
sections — Architectural decisions, Tool/library decisions, Path
convention, Cross-platform suffix handling, Tool integration
model, Decisions taken (1–17), Renovate/Gradle clarification,
Open questions — remain accurate and should be kept verbatim.

### §"dm verb status" (replacement)

```markdown
## dm verb status

| Verb | Status | Purpose |
|---|---|---|
| `resolve <project-dir>` | **working** | List `mvnDeps` tasks + JSON-decoded deps for a project — proves subprocess + JSON pipeline. Verified against toolbox. |
| `extract [--force] [--out=<dir>] <project-dir>...` | **working** | Bootstrap: read each project's `mill show __.mvnDeps` → canonicalize platform suffixes → build the `Catalog` ADT → write `libs.versions.toml` + `projects.yml`. End-to-end verified against toolbox / slm / safetensors-scala: 12 unique libraries, 3 projects, deterministic ordering. |
| `regen [--catalog=<dir>] [--project=<name>] [--dry-run]` | **working** | Read the catalog → write `<project>/deps/Dependencies.mill` per project. Handles kebab→camelCase val names (`os-lib` → `osLib`, `munit-cats-effect` → `munitCatsEffect`, `sourceline-manager` → `sourcelineManager`). DO-NOT-EDIT banner; aligned `=` columns; cross-source separator round-tripped via `CrossKind`. |
| `verify [--catalog=<dir>] [--project=<name>]` | **working** | CI mode: regen into memory, byte-for-byte against on-disk `<project>/deps/Dependencies.mill`. OK / DRIFT per project; on drift, line-level diff (first 10 differing pairs). Exit 0 clean, 1 drift, 2 input error. |
| `promote [--catalog=<dir>] [--project=<name>] [--apply]` | **working** | Parse `mvn"…"` literals in each project's `deps/Dependencies.mill`, match by `(group, artifact)`, report version deltas; with `--apply`, rewrite `libs.versions.toml`. Whitelist enforced via the project's `projects.yml` library list. Bootstrap → bump → regen round-trip verified end-to-end. |

Things explicitly OUT of scope for dm (unchanged from initial design):
- Opening PRs (Renovate / human does that)
- Running Mill builds (CI does that)
- Managing Nix flake inputs (`nix flake update` owns that)
- Managing non-Scala deps in any repo (Vite npm deps, etc. — let Renovate handle directly)

In-scope but **deferred** to a later iteration:
- Native CLI target (sub-100ms startup) — see §"Open questions".
- `/p/factory/` monorepo absorption decision — see §"Open questions".
- Platform versions in the catalog (Scala / ScalaJS / ScalaNative). Not
  in catalog by design: Renovate's Maven model does not cover platform
  versions, and mixing shapes is a wrong move. Per-consumer ADRs (see
  `projects/{sourceline-manager,toolbox,safetensors-scala}/adr/*-adopt-deps-single-file.md`)
  record the platforms-only deviation.
```

### §"Where we stopped" (replacement)

```markdown
## Where we stopped (v1 — 2026-05-29)

**v1 complete.** All five verbs working end-to-end against
toolbox + sourceline-manager + safetensors-scala. Three consumer
`build.mill` files migrated from inline `object V.x` to
`build.deps.Deps.*` references from the auto-generated
`deps/Dependencies.mill`. Renovate config validated via local
dry-run. Nix flake apps (`test` / `verify` / `check` /
`renovate-dryrun`) functional.

Test count: 71 tests across 11 specs, all green.

**Pre-MVP gaps** (tracked in `projects/dependency-manager/plans/mvp.md`):
- git-init + first commit (personal-repo policy: human-gated;
  agent prep complete, awaiting human trigger).
- Source bridge promotion (depends on the commit SHA).
- Normative ADR realignment across the three consumer projects.
- Final wiki lint pass.

**Out of MVP scope (deferred):**
- Hosted Renovate (requires git remote).
- CI pipeline (requires git remote).
- Native CLI repackaging.
- `/p/factory/` monorepo absorption.
- Platform versions in catalog (intentional non-feature; see
  per-consumer ADRs for the rationale).
- More than three consumers; new consumers adopt via the README
  guide.
```

### §"Next steps when resuming" (deletion)

This section is now obsolete. Every item it listed was closed in
the 2026-05-29 implement sessions plus DM-001..DM-004. Forward
work lives in
[`projects/dependency-manager/plans/mvp.md`](../../../../p/wiki/projects/dependency-manager/plans/mvp.md)
(replace the wiki-relative path with whatever your in-tree
DESIGN.md uses to point at the wiki) rather than here.

Suggested replacement block:

```markdown
## Next steps

Forward-looking work is decomposed in the wiki at
`projects/dependency-manager/plans/mvp.md` (the v1 MVP plan).
Tickets DM-001..DM-009 cover the remaining MVP surface; updates
to this in-tree `DESIGN.md` are tracked as DM-007.

For longer-horizon questions (Native target, monorepo absorption,
platforms-in-catalog), see §"Open questions" below.
```

### §"Repo layout" `.renovaterc.json` correction

In the §"Repo layout" tree, change:

```
├── deps/                        # canonical data managed by dm
│   ├── libs.versions.toml       # populated by `dm extract`
│   ├── projects.yml             # populated by `dm extract`
│   └── .renovaterc.json         # Renovate config       ← REMOVE THIS LINE
├── .renovaterc.json             # Renovate config       ← ADD THIS LINE at root
```

Rationale: Renovate auto-discovery only walks the repo root. The
file lives at `/p/hg/dependency-manager/.renovaterc.json`; the
deviation is already noted in the wiki log entry "dm verify +
Renovate config validated end-to-end" (2026-05-29).

### §"Open questions" — add one new entry

Insert at the end of the existing list:

```markdown
- Should the catalog also manage platform versions (`scala` /
  `scalaJS` / `scalaNative`)? **Position: no.** Renovate's Maven
  manager model does not cover platform versions, and mixing
  them into `libs.versions.toml` would conflate two distinct
  shapes (Maven coords vs. platform strings). The per-consumer
  ADRs in
  `projects/{sourceline-manager,toolbox,safetensors-scala}/adr/*-adopt-deps-single-file.md`
  record this as an explicit deviation. Revisit if a future
  Renovate manager (or replacement bot) gains platform-version
  awareness.
```

## Acceptance handoff

1. Human reads this draft.
2. Human opens `/p/hg/dependency-manager/DESIGN.md` and applies
   the four replacement blocks plus the §"Repo layout" line edit.
3. Human commits per the personal-repo policy (unsigned, no
   Co-Authored-By, author `tigidar`).
4. Human signals "applied"; agent re-ingests the in-tree file
   into the wiki mirror at
   `projects/dependency-manager/designs/dm-architecture.md` and
   marks DM-007 done.

## Links

- [[projects/dependency-manager/index]]
- [[projects/dependency-manager/designs/dm-architecture]]
- [[projects/dependency-manager/log]]
- [[projects/dependency-manager/plans/mvp]]
- [[projects/dependency-manager/tickets/0007-refresh-in-tree-design]]

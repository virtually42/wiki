# dependency-manager

Private build-tooling CLI (`dm`) that centralises Maven dependency
versions across the standalone repos under `/p/hg/`. Single Mill
project, JVM-only at v1, structured for Native repackaging later.

**Status:** active (pre-1.0 — **all five verbs working
end-to-end** (`resolve` / `extract` / `regen` / `verify` /
`promote`); `.renovaterc.json` validated via local Renovate
dry-run; Nix flake apps for `test` / `verify` / `check` /
`renovate-dryrun`; repo not yet under version control)

## Stack

- Language: Scala 3 (3.8.3)
- Platform: JVM (Native repackaging deferred)
- Build: Mill 1.1.2 (`mill dm.assembly` + `bin/dm` shell wrapper)
- Subprocess / process: toolbox-script + toolbox-proc-oslib + toolbox-fluent (dogfooded; see [[sources/summaries/toolbox]])
- TOML: `com.indoorvivants::toml::0.3.0` (see [[sources/tmp/code/toml-scala]])
- YAML: `org.virtuslab::scala-yaml::0.3.1`
- JSON: `com.lihaoyi::ujson::3.3.1` (for parsing `mill show` output)
- Tests: MUnit
- Dev shell: Nix flake (JDK 21, coursier, git, nodejs 22 for `npx renovate`)
- Update bot: Renovate (`gradle-version-catalog` manager — no Gradle runtime required)

## Code Location

`/p/hg/dependency-manager` — see [[sources/raw/code/dependency-manager]]
(bridge at commit `5459ddb`, branch `main`) and
[[sources/summaries/dependency-manager]] for the distilled view.

The architectural source of truth is in-tree at
`/p/hg/dependency-manager/DESIGN.md`; the wiki-side copy lives at
[[projects/dependency-manager/designs/dm-architecture]].

## Embedding Path

When `/p/factory/` (the future monorepo) is created, the open
question recorded in `DESIGN.md` is whether dm is absorbed (collapsed
into the monorepo's own deps machinery) or continues as a meta-tool
managing the monorepo plus any remaining standalone repos. Deferred.
Either way, the *single inline `object V`* in dm's own `build.mill`
gets replaced by references to the monorepo's `deps/Dependencies.mill`
(by construction), resolving the deviation recorded in
[adr/0001-deviate-deps-single-file.md](adr/0001-deviate-deps-single-file.md).

## Relation to Existing Wiki Knowledge

dm is the **implementation of a generalised version** of
[[tech/decisions/deps-single-file]]. The global decision targets the
per-project shape (one `deps/Dependencies.mill` per repo with inline
`mvn"…"` coordinates). dm keeps that shape *as the generated output*
per downstream project, but moves the source of truth one level up
to a TOML catalog shared across all `/p/hg/` repos:

```
deps/libs.versions.toml + deps/projects.yml   (Renovate target)
              │
              │ dm regen
              v
<project>/deps/Dependencies.mill              (DO NOT EDIT banner;
                                               committed downstream)
              │
              │ build.mill import
              v
        mill compile
```

This is *not* a supersession of `deps-single-file`. The single-file
shape remains the per-project contract. dm is the upstream automation
that produces files satisfying it.

## Pages

### ADRs (wiki-side; record stance on global normative pages)

- [adr/0001-deviate-deps-single-file.md](adr/0001-deviate-deps-single-file.md) —
  Deviate from [[tech/decisions/deps-single-file]] *in dm's own
  build.mill*. dm is the tool that produces compliant single-file
  Dependencies.mill in *other* repos; bootstrap chicken-and-egg is
  resolved by hand-authoring `object V` once.
- [adr/0002-adopt-functional-domain-design.md](adr/0002-adopt-functional-domain-design.md) —
  Adopt [[tech/patterns/functional-domain-design]] unconditionally,
  declarative encoding. Cites `dm.catalog` (Coord/Library/Catalog +
  Reader/Writer interpreters) and `dm.mill` (Cwd/Invocation DSL) as
  worked examples.
- [adr/0003-adopt-tdd-rhythm.md](adr/0003-adopt-tdd-rhythm.md) —
  Adopt [[tech/patterns/tdd-rhythm]] with one bounded exception
  (Stage 2 law-based not yet realised; closes when the catalog
  algebra grows symmetric operators). All four implement sessions
  ran red → green → refactor.
- [adr/0004-adopt-symmetric-refactoring.md](adr/0004-adopt-symmetric-refactoring.md) —
  Adopt [[tech/patterns/symmetric-refactoring]] in the
  **parallel-module form** (distinct from sourceline-manager's
  operator-layer form). Reader/Writer dual pairs + Regen/Verify dual
  + Extract/Promote dual.

The [[tech/patterns/test-economics]] ADR remains deferred — the
algebra has no symmetric operator surface yet, so the amortisation
case is premature. Lands when `merge` / `diff` / `union` operators
on `Catalog` materialise.

### Designs

- [designs/dm-architecture.md](designs/dm-architecture.md) — the
  in-tree `DESIGN.md` ingested as a `design-doc`. Covers the
  two-file canonical catalog choice, TOML-as-source-of-truth,
  per-repo `deps/Dependencies.mill` committed downstream,
  Renovate-only-here, drift detection via `verify` + `promote`,
  the 17 chronological decisions, and the open questions.
- [designs/dm-architecture-2026q2-refresh.md](designs/dm-architecture-2026q2-refresh.md) —
  **draft, 2026-05-29.** Wiki-side proposal for refreshing the
  in-tree `DESIGN.md` to match post-v1 reality (DM-007). Covers
  four replacement sections plus one new open question
  (platforms-in-catalog). Human applies in-tree; agent re-ingests
  on confirmation.

### Plans

- [plans/mvp.md](plans/mvp.md) — **draft, 2026-05-29.** dependency-manager
  v1 MVP — close the loop end-to-end across all 3 consumers, git-init,
  document, resolve normative debts. Decomposes into DM-001 …
  DM-009. Estimated 3 sessions. The "Next steps when resuming" list
  in the in-tree `DESIGN.md` has been fully consumed (every item
  closed in the 2026-05-29 sessions); this plan replaces it as the
  forward-looking work surface.

### Tickets

- [tickets/0001-migrate-toolbox-to-deps.md](tickets/0001-migrate-toolbox-to-deps.md) —
  DM-001, **done** 2026-05-29. Migrate `/p/hg/toolbox/build.mill`
  to consume `Deps.*` from dm catalog (10 libraries).
- [tickets/0002-migrate-safetensors-to-deps.md](tickets/0002-migrate-safetensors-to-deps.md) —
  DM-002, **done** 2026-05-29. Migrate
  `/p/hg/safetensors-scala/build.mill` to consume `Deps.*`
  (3 libraries).
- [tickets/0003-renovate-bumps-end-to-end.md](tickets/0003-renovate-bumps-end-to-end.md) —
  DM-003, **done** 2026-05-29. Three low-risk bumps landed
  (os-lib, pprint, munit-cats-effect); kyo-core RC2 attempted
  and rolled back per documented-outcome rule.
- [tickets/0004-consumer-adoption-readme.md](tickets/0004-consumer-adoption-readme.md) —
  DM-004, **done** 2026-05-29. Consumer-adoption README
  section + `deps-single-file` anchor pre-requisite docs
  written.
- [tickets/0005-git-init-first-commit.md](tickets/0005-git-init-first-commit.md) —
  DM-005, **done** 2026-05-29. First commit
  `5459ddb7dc4ceb882ea89b2054e5814b9383f313` on branch `main`
  (renamed from `master` post-commit), unsigned, no Co-Authored-By
  trailer, author `tigidar`. Agent executed on human approval
  (response "1)").
- [tickets/0006-promote-source-bridge.md](tickets/0006-promote-source-bridge.md) —
  DM-006, **done** 2026-05-29. Bridge promoted to
  `sources/raw/code/dependency-manager.md` at commit `5459ddb`;
  7 live wiki references rewritten; tmp copy removed.
- [tickets/0007-refresh-in-tree-design.md](tickets/0007-refresh-in-tree-design.md) —
  DM-007, **draft ready 2026-05-29; awaiting human in-tree
  apply.** Wiki-side proposal at
  `designs/dm-architecture-2026q2-refresh.md`.
- [tickets/0008-resolve-adr-debts.md](tickets/0008-resolve-adr-debts.md) —
  DM-008, **done** 2026-05-29. All three consumer ADRs
  realigned to adopt-with-platforms-exception (slm ADR-0006,
  toolbox ADR-0003, safetensors-scala ADR-0001).
- [tickets/0009-lint-and-drift-cleanup.md](tickets/0009-lint-and-drift-cleanup.md) —
  DM-009, **in progress 2026-05-29.** Final lint pass + drift
  cleanup; MVP plan completion record.

### Syntheses

*No syntheses yet.*

### Other

- [log.md](log.md)

## Verb Status

| Verb | Status | Purpose |
|------|--------|---------|
| `resolve <project-dir>` | **working** | List `mvnDeps` tasks + JSON-decoded deps for a project — proves subprocess + JSON pipeline. Verified against toolbox: 48 `mvnDeps` tasks enumerated. |
| `extract [--force] [--out=<dir>] <project-dir>...` | **working** | Bootstrap: `mill show __.mvnDeps` per project → parse source-form coords (`::` cross retained as-is) → build `Catalog` ADT → write `libs.versions.toml` + `projects.yml`. Verified end-to-end against toolbox / sourceline-manager / safetensors-scala: 12 unique libraries, `munit` correctly deduped across all three projects, deterministic ordering. |
| `regen [--catalog=<dir>] [--project=<name>] [--dry-run]` | **working** | Read catalog → write `<project>/deps/Dependencies.mill` per project. Handle kebab → camelCase `val` name (`os-lib` → `osLib`, `munit-cats-effect` → `munitCatsEffect`, `sourceline-manager` → `sourcelineManager`). DO-NOT-EDIT banner; aligned `=` columns; cross-source separator round-tripped via `CrossKind`. Verified end-to-end: 10 vals in toolbox/, 2 in slm/, 3 in safetensors/, all three `deps/` directories untracked (no pre-existing files clobbered). |
| `verify [--catalog=<dir>] [--project=<name>]` | **working** | CI mode: regen into memory, compare byte-for-byte with on-disk `<project>/deps/Dependencies.mill`. Prints OK / DRIFT line per project; on drift, prints line-level diff (first 10 differing pairs). Exit 0 clean, 1 drift, 2 input error. Verified end-to-end: catches a one-character version bump (`1.0.3` → `1.0.4`) at the exact line, restored by `dm regen --project=`. |
| `promote [--catalog=<dir>] [--project=<name>] [--apply]` | **working** | Parse every `mvn"…"` literal in each project's `deps/Dependencies.mill`, match by `(group, artifact)` against the catalog, report version deltas; with `--apply`, rewrite `libs.versions.toml` so the downstream version becomes canonical. Dry-run prints `# <project> <handle>: <catalogV> → <downstreamV>` per delta and exits 1; `--apply` patches and exits 0. Bootstrap → bump → regen round-trip verified end-to-end. |

The compile error noted in the previous ingest is resolved — it was
a single-source Scala 3 issue (`os.proc("mill", args*)` mixed a
positional literal with a varargs spread; Scala 3 requires the
spread be the *only* argument; fixed by passing `args` as a single
`Iterable[String]` Shellable).

## Renovate Configuration

`.renovaterc.json` sits at the **repo root** (not `deps/` as
`DESIGN.md` originally suggested — Renovate auto-discovery only
walks the repo root). Watches `^deps/libs\.versions\.toml$` via
two `customManagers` regex entries:

- **Scala-cross** (`::` separator) — packageNameTemplate
  `{{groupId}}:{{artifactId}}_3` (Scala 3 binary suffix). Maven
  datasource.
- **Java** (`:` separator) — packageNameTemplate
  `{{groupId}}:{{artifactId}}`. Currently zero matches in the
  catalog but kept for forward compatibility.

`enabledManagers: ["custom.regex"]` disables Renovate's native
`gradle-version-catalogs` manager, which mismatches our
Scala-cross `::` syntax. Without this, Renovate would emit
spurious lookups for malformed group IDs.

`packageRules` give us four behaviours:
- Disable `no.virtual-architect:**` (internal `publishLocal`
  artifacts not on Maven Central).
- Skip any `-SNAPSHOT` version.
- Group `io.getkyo:**`, `co.fs2:**`, and the MUnit family so
  each ecosystem bumps in lockstep.

Validated via `npx renovate --platform=local --dry-run=lookup`
(also wired as the `nix run .#renovate-dryrun` flake app): all 12
catalog libraries extracted, 8 updates surfaced (kyo RC1→RC2, fs2
3.12.0→3.13.0, munit 1.0.3→1.3.1, etc.), 2 already latest, 1
SNAPSHOT correctly skipped.

## Nix flake apps

```bash
nix run .#test              # mill dm.test
nix run .#verify            # bin/dm verify against the on-disk catalog
nix run .#check             # test + verify back-to-back; exit non-zero on first failure
nix run .#renovate-dryrun   # npx renovate --platform=local --dry-run=lookup
```

All scripts assume CWD is the dm repo and bundle their own
runtime deps (`jdk21`, `mill`, `git`, `nodejs_22` as appropriate)
via `pkgs.writeShellApplication`. `nix flake check` passes;
warnings are cosmetic (`lacks attribute 'meta'`). Use
`nix run .#check` as the pre-commit / pre-push gate.

## Toolbox dogfooding (realised)

`dm` declares `toolbox-script` / `toolbox-proc-oslib` /
`toolbox-fluent` as dependencies but, until 2026-05-29 (refactor
session), didn't actually use them — `MillQuery` shelled out
through raw `os.proc` directly. Now there's a small fluent DSL at
`dm/src/mill/Mill.scala` built on top of toolbox's
`ProcessDescription` algebra + `OsLibProcess` interpreter:

```scala
import dm.mill.Mill

Mill.in(projectDir).resolve("__").asLines       // Either[String, Vector[String]]
Mill.in(projectDir).show(task).asJson           // Either[String, ujson.Value]
Mill.in(projectDir).raw("inspect", t).asText    // escape hatch
Mill.in(projectDir).resolve("__").verbosely.asLines  // opt-in to progress
```

Three-stage builder (`Cwd` → `Invocation` → terminal `as*`).
Defaults `--ticker false --silent` for clean stdout (the extract
output now shows nothing but `# project   N coords` lines instead
of being interleaved with Mill's progress prefixes). All exits
return `Either[String, A]` — Mill subprocess failures stop being
uncaught exceptions and surface as clean error messages at the
caller. `MillQuery` shrank to four lines of dm-glue over the DSL.

This puts the toolbox deps to work and gives us free pipeline
composition (`Chain` / `AndThen` / `OrElse` on `ProcessDescription`)
if a future verb needs it.

## Domain ADT (functional-domain-design realised)

The `dm.catalog` package now carries the first real domain types in
this codebase: `CrossKind` / `Coord` / `Library` / `ProjectInfo` /
`Catalog` — all immutable, all `derives CanEqual`, parser returns
`Either[String, Coord]`, writers are total functions producing
deterministic output. `dm.mill.Mill` extends the declarative pattern
to the subprocess layer (`Cwd` / `Invocation` as data; `as*` as
interpreters). This is on-disk evidence of
[[tech/patterns/functional-domain-design]] in the declarative
encoding, and the four-deferred-ADRs situation should be revisited:

- `functional-domain-design` — adoption is now writable on evidence.
- `tdd-rhythm` — every type was driven by a test that came first
  (CoordSpec → Coord; CatalogBuilderSpec → CatalogBuilder; etc.).
- `test-economics` / `symmetric-refactoring` — still premature; the
  algebra has no symmetric operator surface yet.

The next ADR session can land 0002 (adopt
`functional-domain-design`) and possibly 0003 (adopt `tdd-rhythm`)
on real evidence rather than forward-looking intent.

Things explicitly out of scope (per `DESIGN.md`): opening PRs (Renovate /
human owns that), running Mill builds (CI owns that), managing Nix
flake inputs (`nix flake update` owns that), managing non-Scala deps
(Vite npm deps etc. — Renovate handles those directly in the
downstream repos).

## Current Blockers

1. ~~**Compile error.**~~ Resolved 2026-05-29. Root cause: Scala 3
   forbids `f(literal, xs*)` at varargs sites; fix: pass `args` as
   one `Iterable[String]` Shellable.
2. ~~**Initial git commit.**~~ Resolved 2026-05-29 (DM-005). First
   commit `5459ddb7dc4ceb882ea89b2054e5814b9383f313` on branch
   `main` (renamed from `master` post-commit to match slm/toolbox
   convention), unsigned, no Co-Authored-By, author `tigidar` —
   matching the personal-repo policy
   ([[feedback_hg_repo_commit_policy]]). Bridge promoted to
   `sources/raw/code/dependency-manager.md` via DM-006 the same
   day.
3. ~~**TOML/YAML readers not yet implemented.**~~ Resolved 2026-05-29.
   `TomlReader` walks `toml.Value.Tbl`/`Arr`/`Str`; `YamlReader` walks
   `Node.MappingNode`/`SequenceNode`/`ScalarNode`. `CatalogReader`
   combines both and validates project library refs against the
   `[libraries]` table — dangling handles surface up-front as a
   single error.
4. ~~**Downstream `build.mill` migration.**~~ Resolved 2026-05-29
   (DM-001 toolbox, DM-002 safetensors-scala). All three v1
   consumers — `sourceline-manager`, `toolbox`,
   `safetensors-scala` — consume `build.deps.Deps.*` from the
   auto-generated `deps/Dependencies.mill`. Each carries the Mill
   1.x `deps/package.mill` anchor (one line: `package build.deps`),
   discovered during the slm migration and now documented in
   [[tech/decisions/deps-single-file]] §"Mill 1.x discovery
   pre-requisite" and the dm README's "Adopting dm in a downstream
   repo" section. Bumps proven end-to-end via DM-003 (os-lib /
   pprint / munit-cats-effect landed; kyo-core RC2 rolled back per
   documented-outcome rule).

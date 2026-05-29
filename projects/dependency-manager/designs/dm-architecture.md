---
id: dependency-manager-design-architecture
title: dm architecture — TOML catalog, Mill-show extraction, Renovate round-trip
kind: descriptive
status: accepted
project: dependency-manager
created: 2026-05-29
updated: 2026-05-29
related_adrs:
  - projects/dependency-manager/adr/0001-deviate-deps-single-file.md
related_plans:
  - projects/dependency-manager/plans/mvp.md
sources:
  - sources/raw/code/dependency-manager.md
  - sources/summaries/dependency-manager.md
---

## Source

This design doc is a wiki-side mirror of the in-tree `DESIGN.md` at
`/p/hg/dependency-manager/DESIGN.md`. The in-tree document is the
source of truth and was stripped to a **decisions archive** on
2026-05-29 (option B; see
[[projects/dependency-manager/log]] for the rationale). What lived
in the original ingest as "where we stopped" / "next steps when
resuming" / "verb status" / "repo layout" is now elsewhere:

- Current state and verb status: [[projects/dependency-manager/index]]
- Chronological work record: [[projects/dependency-manager/log]]
- Forward-looking work: [[projects/dependency-manager/plans/mvp]]
- User-facing surface: `README.md` in-tree

What stays in the in-tree `DESIGN.md` (and is mirrored below):

- Architectural decisions (locked in)
- Tool / library decisions (locked in)
- The 17 chronological decisions from the original design conversation
- Renovate / Gradle clarification
- Open questions deferred to longer-horizon design work

## Architectural decisions (locked in)

### Two-file canonical catalog at `/p/hg/dependency-manager/deps/`

- `libs.versions.toml` — **the** version registry. Handle → coordinate.
  Uses Gradle Version Catalog format because Renovate has native support
  for it.
- `projects.yml` — project + module structure. Each module lists handles
  it consumes from the toml. Hand-authored / hand-edited.

### TOML as the source of truth, Mill files as regenerated output

We explicitly chose "yaml/toml is source of truth" over "Mill build is
source of truth" because no bot in the ecosystem patches *across* file
formats. Whoever the bot patches IS the source of truth, full stop.
Renovate patches the toml directly; `dm regen` overwrites
`deps/Dependencies.mill` in each downstream repo with a `DO NOT EDIT`
banner.

### Per-repo `deps/Dependencies.mill` is committed (not gitignored)

Each downstream repo carries its own generated `deps/Dependencies.mill`.
This means standalone clone-and-build of any repo still works without
needing access to `/p/hg/dependency-manager/`. The catalog is required
only when you want to *update*, not when you want to *build*.

### Renovate runs against `dependency-manager` only

Renovate watches `/p/hg/dependency-manager/deps/libs.versions.toml` and
opens PRs there. Downstream repos (toolbox, slm, safetensors) get
regenerated Mill files via `dm regen` — manual or scheduled CI.
Renovate never touches downstream repos directly. Source of truth stays
clean.

### Drift detection + promote, not bidirectional bot updates

Earlier we considered running both Scala Steward and Renovate, each
handling what the other can't. Rejected as over-engineering. What we
kept: `dm verify` (CI mode: regen into a tmp dir, diff against
committed Mill files, fail on mismatch) and `dm promote` (take a
hand-edit in a downstream Mill file, extract the version delta into a
toml patch). This closes the drift loop without inviting two bots to
race on the same files.

### Bootstrap

The catalog is initially seeded by `dm extract` — a one-shot bootstrap
that reads existing `build.mill` files (via Mill's own `show` command)
and emits the first toml + yml.

## Tool / library decisions (locked in)

| Concern | Choice | Reasoning |
|---|---|---|
| Update bot | **Renovate** | Native support for `libs.versions.toml` via the `gradle-version-catalog` manager. Local-runnable, no Gradle binary required. |
| TOML parser | **`com.indoorvivants::toml`** (0.3.0) | Cross-platform (JVM/JS/Native), maintained by Anton Sviridov; forked at `/p/gh/toml-scala/` for reference. |
| YAML parser | **`org.virtuslab::scala-yaml`** (0.3.1) | Cross-platform, type-safe, by VirtusLab. |
| Mill metadata extraction | **Shell out to `mill show __.mvnDeps`** | Mill's `show` emits pure JSON on stdout; everything else to stderr. Verified in `/p/gh/mill/libs/util/src/mill/util/MainModule.scala`. |
| Build tool for dm | **Mill** | Consistent with the rest of /p/hg. JVM-only v1; structured for Native v2. |
| Distribution | **`mill dm.assembly` + `bin/dm` shell wrapper** | Fat jar; wrapper auto-builds if missing. |
| Test framework | **munit** | Matches other projects. |
| toolbox modules dm depends on | **toolbox-script, toolbox-proc-oslib, toolbox-fluent** | Dogfooding. Toolbox must be publishLocal'd before dm compiles. |

## Decisions taken (in chronological order through the conversation)

1. The "current two-file split" in `deps-single-file.md` is hypothetical;
   actual projects used inline `object V`. Original deviation ADRs
   (`projects/toolbox/adr/0002`, `projects/sourceline-manager/adr/0002`)
   recorded the gap; superseded on 2026-05-29 by the dm-migration
   adopt-ADRs (toolbox/0003, slm/0006).
2. `/p/hg/` is not a git repo — it's a directory of independent repos.
   A centralized yaml/toml at `/p/hg/dependency-manager/deps/` lives
   outside every consumer, so the catalog is a *reconciler*, not a
   build-time input.
3. Chosen architecture is Shape C (catalog source of truth, Mill files
   regenerated) over Shape A (inline only) or Shape B (per-repo + sync
   script).
4. Catalog format is **TOML** (humans + Renovate-friendly), specifically
   the Gradle Version Catalogs `libs.versions.toml` shape.
5. Project/module structure goes in a separate **YAML** file
   (`projects.yml`) because YAML's nested form is more natural than
   TOML tables for this.
6. dm depends on toolbox-script + toolbox-proc-oslib + toolbox-fluent
   (dogfooding); JVM-only v1; structured for Native v2.
7. toml-scala consumption strategy: **Path A** — use the published Maven
   Central artifact. Fork at `/p/gh/toml-scala/` is reference-only until
   patching is needed.
8. YAML parser: `org.virtuslab::scala-yaml::0.3.1`.
9. Mill metadata extraction: shell out to `mill show __.mvnDeps`, parse
   JSON.
10. Mill version per target: query each project's `.mill-version` file;
    shell out to the system `mill` (which respects `.mill-version` via
    its launcher).
11. `dm extract` is one-shot: fail on existing `libs.versions.toml`
    unless `--force` is passed. After bootstrap, updates flow through
    Renovate-on-toml.
12. Repo layout: **single repo** at `/p/hg/dependency-manager/`
    containing both the tool source and `deps/` data.
13. CLI distribution: `mill dm.assembly` + `bin/dm` shell wrapper.
14. Renovate config: `.renovaterc.json` at the **repo root** (Renovate
    auto-discovery only walks the root). Watches only
    `deps/libs.versions.toml`. Downstream repos get changes via
    `dm regen`, NOT via direct bot action.
15. Drop the "use both bots bidirectionally" idea. Renovate alone is
    enough; `dm verify` + `dm promote` close the drift loop without
    bot races.
16. Path correction: `/p/gh/dependency-manager` was a typo across
    multiple turns; the correct location is `/p/hg/dependency-manager/`.
17. v1 extract scope: toolbox, sourceline-manager, safetensors-scala.
    Skip swc (no `object V`, would need a different parser path).

## Renovate / Gradle clarification (for future reference)

Renovate's `gradle-version-catalog` manager parses `libs.versions.toml`
files. It does NOT require Gradle to be installed anywhere — Renovate
runs as a Node.js bot. The "gradle" in the name refers to the format
origin, not a runtime dependency.

In practice we use Renovate's `customManagers` regex against the same
TOML rather than the native `gradle-version-catalog` manager — the
native manager chokes on the Scala-cross `::` separator and emits
malformed Maven lookups. The custom regex gives finer control and
explicit handling of the cross syntax. See `.renovaterc.json`.

## Open questions (deferred)

- Will the future `/p/factory/` monorepo absorb dependency-manager
  (collapsing it into the monorepo's own deps machinery), or will dm
  continue to exist as a meta-tool that manages the monorepo plus any
  remaining standalone repos?
- How will the monorepo track open-source projects without git
  submodules? Candidates discussed: `git subtree`, `git subrepo`,
  `josh`. Recommendation was `git subrepo` but final choice deferred.
- Should `dm` eventually grow a Native target for sub-100ms CLI
  startup, or is JVM startup acceptable for the use case? Deferred
  until JVM startup is observed to be real friction.
- Should the catalog also manage platform versions (`scala` / `scalaJS`
  / `scalaNative`)? **Position: no.** Renovate's Maven manager model
  does not cover platform versions; conflating them with Maven coords
  in `libs.versions.toml` would be a wrong shape. The per-consumer
  ADRs (slm/0006, toolbox/0003, safetensors-scala wiki/0001 + in-tree
  ADR-0002) record this as an explicit narrow exception. Revisit if a
  future Renovate manager (or replacement bot) gains platform-version
  awareness.

## Links

- [[projects/dependency-manager/index]]
- [[projects/dependency-manager/adr/0001-deviate-deps-single-file]]
- [[projects/dependency-manager/log]]
- [[projects/dependency-manager/plans/mvp]]
- [[sources/summaries/dependency-manager]]
- [[sources/raw/code/dependency-manager]]
- [[sources/summaries/toolbox]]
- [[sources/tmp/code/toml-scala]]
- [[tech/decisions/deps-single-file]]
- [[tech/guides/mill-dependency-management]]
- [[tech/stack/mill]]

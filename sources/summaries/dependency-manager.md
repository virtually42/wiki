---
id: summary-dependency-manager
title: dependency-manager (dm) — code summary
kind: descriptive
status: accepted
scope: global
created: 2026-05-29
updated: 2026-05-29
confidence: medium
sources:
  - sources/raw/code/dependency-manager.md
tags: [scala, mill, cli, dependency-management, toml, yaml, renovate, build-tooling, private]
---

## What it is

`dependency-manager` (CLI binary `dm`, artifact
`no.virtual-architect:dm:0.1.0-SNAPSHOT`, **unlicensed / not for
distribution**) is a private build-tooling JVM CLI that centralises
Maven dependency versions across the standalone repos under `/p/hg/`.
The canonical catalog lives in this same repo at
`/p/hg/dependency-manager/deps/` as a two-file pair:

- `libs.versions.toml` — Gradle Version Catalog format. **The** version
  registry. Renovate's `gradle-version-catalog` manager understands it
  natively, no Gradle binary required.
- `projects.yml` — hand-authored project + module structure mapping
  catalog handles to consuming modules.

`dm regen` reads both files and rewrites
`<project>/deps/Dependencies.mill` in each downstream repo with a
`DO NOT EDIT` banner. Downstream repos *commit* the generated file, so
standalone clone-and-build still works without access to dm. `dm verify`
(CI mode) re-runs regen into a tmp dir and diffs; `dm promote` ports
a hand-edit in a downstream Mill file back into a TOML patch. `dm extract`
is the one-shot bootstrap that reads existing `build.mill` files via
`mill show __.mvnDeps` and seeds the catalog.

The CLI ships as `mill dm.assembly` (fat jar) + a `bin/dm` shell wrapper
that auto-rebuilds the jar if missing. JVM-only at v1; the code is
structured for Native repackaging (os-lib paths only, no `java.io.File`)
should JVM startup later be observed as real friction.

## How it relates to existing wiki knowledge

dm is the **implementation of a generalised version** of
[[tech/decisions/deps-single-file]]. The global decision targets the
per-project `deps/Dependencies.mill` shape (one file, inline `mvn"…"`
coordinates, Renovate-friendly). dm keeps that shape *as the generated
output* per downstream project but moves the source of truth one
level up, to a TOML catalog shared across all `/p/hg/` repos:

```
catalog (toml + yml)  ──dm regen──>  per-project Dependencies.mill  ──>  mill compile
       ^                                      ^
       │                                      │
   Renovate                            committed; clone-builds work
                                       without dm being present
```

This is *not* a supersession of `deps-single-file`. The single-file
shape remains the per-project contract. dm is the upstream automation
that produces files satisfying it.

## Why TOML+YAML rather than Mill source as the catalog

`DESIGN.md` records the principle explicitly: **whichever file format
the bot patches is the source of truth.** No bot in the ecosystem
patches *across* file formats. Renovate's `gradle-version-catalog`
manager patches `libs.versions.toml`, so the toml *is* the catalog
even when the value seen by Mill resolution is the regenerated `.mill`
file. The "gradle" in the manager name is a misnomer — it's just a
TOML parser that understands the layout Gradle popularised, no runtime
Gradle dependency.

YAML (project + module structure) was picked over a second TOML table
because the nested-list shape of "project → modules → handles" reads
more naturally in YAML than in TOML's flat-key form. The split is
intentional: machines (Renovate) only need to look at the toml; humans
edit the yml when modules are added or restructured.

## Build wiring (Mill 1.1.2, JVM-only)

`build.mill` pins Mill 1.1.2 via the `//| mill-version:` header,
declares versions inline in `object V`, and contains one ScalaModule
called `dm` plus a `test` submodule:

```
V.scala     = 3.8.3
V.toolbox   = 0.1.0-SNAPSHOT  (publishLocal from /p/hg/toolbox)
V.tomlScala = 0.3.0           (com.indoorvivants — cross-platform TOML)
V.scalaYaml = 0.3.1           (org.virtuslab — pure-Scala YAML)
V.ujson     = 3.3.1           (com.lihaoyi — JSON for mill-show output)
V.munit     = 1.0.3
```

`mvnDeps` references three toolbox modules
(`toolbox-script`, `toolbox-proc-oslib`, `toolbox-fluent`) under
`no.virtual-architect`, the three above libraries, and munit at test
scope. `mainClass = Some("dm.Main")`. Scalac options include `-explain`
and `-Wunused:all`.

There is no `deps/Dependencies.mill` file in this project. The
`deps/` directory is reserved for the central TOML+YAML catalog,
not for a generated per-project deps file. Bootstrapping dm's own
deps via the catalog is a chicken-and-egg — resolved by hand-authoring
`object V` once. See
[[projects/dependency-manager/adr/0001-deviate-deps-single-file]] for
the full deviation rationale.

`flake.nix` provides the dev shell: JDK 21, coursier, git, nodejs 22
(the last for `npx renovate --platform=local` once the Renovate
config lands).

## Current code surface

| Source | Role |
|--------|------|
| `dm/src/Main.scala` | CLI dispatcher. Pattern-matches argv into verbs (`resolve`, `extract`, `regen`, `verify`, `promote`, `help`). Stubs `sys.exit(1)` rather than passing silently. |
| `dm/src/Resolve.scala` | The only implemented verb. Smoke test: prints every `.mvnDeps` task path in the target project and the JSON `mill show` emits for it. Proves the subprocess + JSON-parse pipeline before extract logic lands on top. |
| `dm/src/millq/MillQuery.scala` | Thin wrapper around `os.proc("mill", …)`. `resolveAll(dir)` runs `mill resolve __`; `mvnDepsTaskPaths(dir)` filters; `show(dir, task)` runs `mill show <task>` and parses with `ujson`. `stderr = os.Inherit` so Mill diagnostics reach the terminal while stdout stays parseable. |
| `dm/test/src/MainSmokeTest.scala` | Two MUnit tests — `help` dispatches without throwing, no-args prints help. |
| `bin/dm` | Bash wrapper: re-runs `mill dm.assembly` if the jar is missing, then `exec java -jar`. |

Verb status:

| Verb | Status | Purpose |
|------|--------|---------|
| `resolve <project-dir>` | **smoke** | List `mvnDeps` tasks + JSON deps for a project |
| `extract` | stub | Bootstrap: read mill metadata → write `libs.versions.toml` + `projects.yml` |
| `regen` | stub | toml + yml → per-project `deps/Dependencies.mill` (banner: DO NOT EDIT) |
| `verify` | stub | CI mode: regen into tmp, diff against committed Mill files, fail on mismatch |
| `promote` | stub | Hand-edited Mill → propose toml patch (or apply with `--apply`) |

## Mill metadata extraction (the load-bearing primitive)

`dm extract` and `dm regen` both depend on Mill's `show` command
emitting *pure* JSON to stdout, with all other output (logs, progress
indicators, errors) routed to stderr. This is the property that lets
`MillQuery.show` parse `proc.out.text()` with `ujson.read` directly.
The behaviour was verified against
`/p/gh/mill/libs/util/src/mill/util/MainModule.scala` during the design
conversation (see [[mill/llm-wiki/index]] for upstream API surface).

The full enumeration path:

```
mill resolve __                        → all task paths
filter ends-with(".mvnDeps")           → mvnDeps task paths
for each task: mill show <task>        → JSON array of resolved coords
canonicalise platform suffixes         → mvn"org::artifact" cross syntax
emit libs.versions.toml + projects.yml
```

Platform-suffix canonicalisation (`kyo-core_3` → `mvn"io.getkyo::kyo-core"`,
`kyo-core_sjs1_3` → same with the JS interpretation, `kyo-core_native0.5_3`
→ same with the Native interpretation) is **not** heuristic. Mill exposes
`<module>.scalaBinaryVersion` and the analogous Scala.js / Scala Native
binary versions through `show`, so the reverse-engineering is deterministic.

## Tool / library decisions (from DESIGN.md, locked in)

| Concern | Choice | Reasoning |
|---|---|---|
| Update bot | **Renovate** (`gradle-version-catalog` manager) | Native TOML support; runs as Node.js bot; no Gradle binary required despite the manager name |
| TOML parser | **`com.indoorvivants::toml::0.3.0`** | Cross-platform (JVM/JS/Native), maintained by Anton Sviridov; fork at `/p/gh/toml-scala/` is read-only reference |
| YAML parser | **`org.virtuslab::scala-yaml::0.3.1`** | Cross-platform, type-safe |
| Mill metadata extraction | **Shell out to `mill show __.mvnDeps`** | Verified pure JSON on stdout, everything else stderr |
| Build tool for dm | **Mill 1.1.2** | Consistent with the rest of /p/hg; JVM-only target for v1, structured for Native v2 (no `java.io.File`, only os-lib paths) |
| Distribution | **`mill dm.assembly` + `bin/dm` shell wrapper** | Fat jar; wrapper auto-builds if jar missing |
| Test framework | **MUnit** | Matches the rest of /p/hg |
| toolbox modules dm consumes | **toolbox-script + toolbox-proc-oslib + toolbox-fluent** | Dogfooding; toolbox must `publishLocal` before dm compiles |

## Cross-cutting type choices

Almost nothing at v1 — Main is a verb dispatcher, Resolve is a smoke
test, and MillQuery wraps subprocess calls. There is no domain ADT yet.
The intended algebra (TOML catalog model + project/module graph +
canonicalisation passes) is to be introduced when `extract` is
implemented; that is when the question of declarative vs executable
encoding (per
[[tech/patterns/functional-domain-design]]) will be answered with on-disk
evidence rather than intent.

The CLI dispatcher in `Main.scala` does use Scala 3 `match` on a
typed list of strings against literal patterns — there is no `enum Verb`
yet; introducing one as the catalog model lands is a candidate cleanup.

## Compliance scan against current accepted normative pages

| Page | In scope? | Stance | Evidence |
|------|-----------|--------|----------|
| [[tech/decisions/deps-single-file]] | Yes (Scala, any domain) | **Deviates** (medium severity) | `build.mill` has `object V` inline; no `deps/Dependencies.mill` in this project (the `deps/` dir holds the meta-catalog instead). dm itself is the *tool* that produces single-file Dependencies.mill in *other* repos. The chicken-and-egg requires hand-authoring once. See [[projects/dependency-manager/adr/0001-deviate-deps-single-file]]. |
| [[tech/patterns/functional-domain-design]] | Yes (Scala, any domain) | **Undecidable at v1 scaffold** — no domain ADT yet | Main / Resolve / MillQuery are CLI plumbing, not a domain. The TOML/YAML catalog model is the natural ADT and will land with `extract`. Drift report should track this; an adoption ADR is premature until the algebra exists. |
| [[tech/patterns/tdd-rhythm]] | Yes | **Premature** — 2 trivial smoke tests, no behaviour yet | Adoption ADR deferred until `extract` / `regen` introduce real behaviour to drive tests from |
| [[tech/patterns/test-economics]] | Yes | **Premature** — 2 smoke tests; no expensive setup; no economics to evaluate | Adoption ADR deferred. The future ADT-heavy code path (TOML round-trip, platform-suffix canonicalisation) is a candidate for property-based testing. |
| [[tech/patterns/symmetric-refactoring]] | Yes | **Premature** — no algebra surface yet | Adoption ADR deferred. The catalog `read` / `write` / `merge` / `diff` operators are a candidate site for symmetric realisation once they exist. |
| [[tech/stack/mill]] | Yes (descriptive) | **Adopts** | Mill 1.1.2 pinned via `//| mill-version:` header; JVM-only `ScalaModule`; `dm.assembly` for distribution |
| [[tech/guides/mill-cross-platform]] | No (descriptive) | **N/A** — JVM-only at v1 | Native repackaging deferred per `DESIGN.md`'s open questions |

The four "premature" rows are deliberate: writing forward-looking
adoption ADRs for code that does not yet exist would create
unenforceable claims. Drift surfacing is the right mechanism — the
ADRs land when the code lands.

## What this exposes that prior projects did not

- **A wiki-managed project whose entire purpose is to automate a
  wiki-resident decision.** dm exists to produce files conformant with
  [[tech/decisions/deps-single-file]] across the `/p/hg/` repos.
  Updating that decision (or any future cross-project version-policy
  page) has a direct downstream consumer in dm. This is the first
  case where a normative wiki page has an in-house *implementation*.
- **Generated-output single-file pattern.** Conformance with
  `deps-single-file` is achieved *by construction* in downstream repos
  via codegen with a DO-NOT-EDIT banner, not by human discipline. If
  the pattern recurs (e.g. generated nix lockfiles, generated build
  manifests), it is a candidate for a tech-layer pattern page.
- **Wiki ingest of a `private / unlicensed` project.** Prior projects
  (toolbox, sourceline-manager, safetensors-scala) are Apache-2.0.
  dm is explicitly *unlicensed and not for distribution*; the
  README states so directly. The wiki itself does not enforce any
  licensing policy today — this raises the open question of whether
  `meta/registry.md` or a future `tech/decisions/private-tooling.md`
  needs a licence-tracking dimension. Flagged.
- **Chicken-and-egg bootstrap in a single repo.** The catalog lives
  in the same repo as the tool that manages the catalog. Atomic
  commits across both (e.g. "dm 0.2 adds a new field; the catalog
  populates that field") are possible. This is structurally similar
  to compilers hosted in their own language; not a precedent yet but
  worth flagging.

## Open Questions

1. **Compile error not yet diagnosed.** `DESIGN.md` records that
   the scaffold did not compile at the end of the design session.
   Until that is resolved, dm cannot be said to *work*. Likely
   suspects: toolbox not publishLocal'd; toml-scala / scala-yaml
   not on Maven Central at the pinned versions; missing imports.
2. **Initial git commit.** The repo is not git-initialised at all
   as of 2026-05-29. The personal-repo policy
   (`feedback_hg_repo_commit_policy`) applies: unsigned, no
   Co-Authored-By, author `tigidar`. This is the human's call to
   make; the wiki bridge stays at `commit: uninitialized-tree` in
   the meantime.
3. **Should `DESIGN.md` be ingested as a `design-doc` under
   `projects/dependency-manager/designs/`?** Yes — the document is
   the architectural source of truth (chosen architecture, locked-in
   tool decisions, the 17 chronological decisions, the open
   questions). Decision: ingest now, since it is the only design
   artefact and lives in the source tree. See
   [[projects/dependency-manager/designs/dm-architecture]].
4. **`/p/factory/` interaction.** Per `DESIGN.md`'s open questions:
   will the future monorepo absorb dm? Deferred until the monorepo
   exists.
5. **Native CLI target.** Deferred until JVM startup is observed as
   real friction. The code is structurally Native-ready (no
   `java.io.File`).

## Project status

Pre-1.0 scaffold. Only the smoke-test verb (`resolve`) is wired;
`extract` / `regen` / `verify` / `promote` are stubs. The catalog
files (`libs.versions.toml`, `projects.yml`, `.renovaterc.json`) do
not yet exist — they will be created by `dm extract` once the
compile error is fixed and `toolbox` is `publishLocal`'d. The repo
is *not* under version control at the time of ingest.

## Links

- [[sources/raw/code/dependency-manager]] — source bridge (commit `5459ddb`)
- [[projects/dependency-manager/index]] — project landing page
- [[projects/dependency-manager/designs/dm-architecture]] — design doc (in-tree DESIGN.md)
- [[projects/dependency-manager/adr/0001-deviate-deps-single-file]] — deviation ADR
- [[sources/summaries/toolbox]] — dogfooded dependency (script + proc-oslib + fluent)
- [[sources/tmp/code/toml-scala]] — TOML parser reference (consumed as Maven Central artifact)
- [[tech/decisions/deps-single-file]] — the decision dm implements across repos
- [[tech/guides/mill-dependency-management]] — the guide that informed `deps-single-file`
- [[tech/stack/mill]] — the build tool
- [[mill/llm-wiki/index]] — Mill API surface (subprocess interface used by `MillQuery`)

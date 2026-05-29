---
id: source-dependency-manager
type: code
repo: /p/hg/dependency-manager
last_observed: 2026-05-29
commit: 5459ddb7dc4ceb882ea89b2054e5814b9383f313
branch: main
entry_points:
  - README.md
  - DESIGN.md
  - build.mill
  - flake.nix
  - flake.lock
  - .mill-version
  - .renovaterc.json
  - .gitignore
  - bin/dm
  - dm/src/Main.scala
  - dm/src/Extract.scala
  - dm/src/Regen.scala
  - dm/src/Verify.scala
  - dm/src/Promote.scala
  - dm/src/Resolve.scala
  - dm/src/catalog/Catalog.scala
  - dm/src/catalog/CatalogBuilder.scala
  - dm/src/catalog/CatalogReader.scala
  - dm/src/catalog/Coord.scala
  - dm/src/catalog/TomlReader.scala
  - dm/src/catalog/TomlWriter.scala
  - dm/src/catalog/YamlReader.scala
  - dm/src/catalog/YamlWriter.scala
  - dm/src/catalog/DependenciesMillReader.scala
  - dm/src/catalog/DependenciesMillWriter.scala
  - dm/src/mill/Mill.scala
  - dm/src/millq/MillQuery.scala
  - deps/libs.versions.toml
  - deps/projects.yml
design_source_of_truth: /p/hg/dependency-manager/DESIGN.md (in-tree)
---

## Structure Overview

`dependency-manager` (artifact `no.virtual-architect:dm:0.1.0-SNAPSHOT`,
unlicensed / not for distribution) is a private build-tooling CLI that
centralises Maven dependency versions across the standalone repos under
`/p/hg/` (toolbox, sourceline-manager, safetensors-scala). The canonical
catalog lives at `/p/hg/dependency-manager/deps/`:

- `libs.versions.toml` — Gradle-Version-Catalog-shaped TOML mapping
  handles to Maven coordinates. **The** source of truth; chosen because
  Renovate's `gradle-version-catalog` manager understands this format
  natively (and the name is a misnomer — no Gradle runtime is required).
  Actually used via `customManagers` regex per dm's
  `.renovaterc.json`, which gives finer control over the `::`
  Scala-cross separator.
- `projects.yml` — hand-authored project + module structure listing
  which handles each module consumes.

`dm regen` reads both files and rewrites `<project>/deps/Dependencies.mill`
in each downstream repo with a `DO NOT EDIT` banner. Downstream repos
commit the generated file so standalone clone-and-build keeps working
without access to dm. `dm verify` (CI mode) regenerates into a tmp dir
and diffs; `dm promote` extracts hand-edits in a downstream Mill file
back into a TOML patch.

The repository at `/p/hg/dependency-manager/` is the *home* of the
catalog and the CLI tool — both live in the same repo so atomic commits
across "tool change" and "catalog change" are possible.

### Current state (2026-05-29 — first commit `5459ddb`)

| Surface | Status |
|---------|--------|
| `build.mill` (Mill 1.1.2, JVM-only) | working |
| `flake.nix` (JDK 21 + coursier + git + nodejs + Mill) | working |
| `bin/dm` shell wrapper around `out/dm/assembly.dest/out.jar` | working |
| `dm.Main` CLI dispatcher (all five verbs + help) | working |
| `dm.Resolve` smoke verb | working |
| `dm.Extract` bootstrap verb | working |
| `dm.Regen` per-project Dependencies.mill writer | working |
| `dm.Verify` CI-mode drift detector | working |
| `dm.Promote` downstream→catalog porter | working |
| `dm.catalog.*` (Coord / Library / Catalog ADTs + readers + writers) | working |
| `dm.mill.Mill` fluent DSL (Cwd → Invocation → as*) | working |
| `dm.millq.MillQuery` thin wrapper over Mill DSL | working |
| `deps/libs.versions.toml` | populated; 12 libraries |
| `deps/projects.yml` | populated; 3 projects (toolbox, sourceline-manager, safetensors-scala) |
| `.renovaterc.json` (root) | wired; validated via local Renovate dry-run |
| Compile / test status | 71 tests across 11 specs, all green |
| Git | initialised; first commit `5459ddb7dc4ceb882ea89b2054e5814b9383f313` (branch `main`) |
| Nix flake apps | `nix run .#{test,verify,check,renovate-dryrun}` all working |

`bin/dm` re-runs `mill dm.assembly` if the jar is missing, so the
intended invocation is `bin/dm resolve /p/hg/toolbox` etc.

## Key Modules

Single Mill module today (`dm`), JVM-only, structured for future
Scala Native repackaging (no `java.io.File`, uses os-lib paths
through `toolbox-proc-oslib`).

| Source | Role |
|--------|------|
| `dm/src/Main.scala` | CLI dispatcher — pattern-matches argv into verbs |
| `dm/src/Resolve.scala` | Smoke verb: shells out via `MillQuery`, prints each `.mvnDeps` task path and its JSON output |
| `dm/src/Extract.scala` | Bootstrap: reads mill metadata from each project, builds `Catalog`, writes `libs.versions.toml` + `projects.yml`. `--force`, `--out=<dir>` |
| `dm/src/Regen.scala` | Reads catalog, writes `<project>/deps/Dependencies.mill` per project. `--catalog=<dir>`, `--project=<name>`, `--dry-run` |
| `dm/src/Verify.scala` | CI mode: regen into memory, compare byte-for-byte with on-disk file; on drift, line-level diff (first 10 differing pairs). Exit 0 clean, 1 drift, 2 input error |
| `dm/src/Promote.scala` | Parses every `mvn"…"` in downstream `Dependencies.mill`, matches by `(group, artifact)` against catalog, reports deltas; `--apply` rewrites the catalog |
| `dm/src/catalog/Catalog.scala` | Top-level `Catalog(libraries, projects)` state |
| `dm/src/catalog/Coord.scala` | `Coord(group, artifact, version, cross)` + parse/render; `CrossKind` enum (`Java` / `Scala` / `Full`); total functions, `Either[String, Coord]` returns |
| `dm/src/catalog/CatalogBuilder.scala` | Pure `(inputs: Vector[Input]) => Catalog` with deterministic ordering, collision disambiguation |
| `dm/src/catalog/CatalogReader.scala` | Combines TOML + YAML readers; validates project library refs against `[libraries]` table |
| `dm/src/catalog/TomlReader.scala` / `TomlWriter.scala` | Hand-rolled, no codec derivation; round-trip property tested |
| `dm/src/catalog/YamlReader.scala` / `YamlWriter.scala` | Same |
| `dm/src/catalog/DependenciesMillReader.scala` / `DependenciesMillWriter.scala` | Reader walks string and extracts every `mvn"…"` literal; writer emits `package build.deps` / `import mill.*, scalalib.*` / `object Deps` shape with aligned `=` columns |
| `dm/src/mill/Mill.scala` | Three-stage fluent DSL: `Mill.in(cwd).resolve(pat).asLines` / `.show(task).asJson` / `.raw(verb, args*).asText`. Defaults `--ticker false --silent`; opt-in `verbosely`; `Either[String, A]` returns |
| `dm/src/millq/MillQuery.scala` | Thin glue over `dm.mill.Mill` exposing `resolveAll`, `mvnDepsTaskPaths`, `show` |

Test surface (`dm/test/src/`):

| Spec | Tests |
|------|-------|
| `MainSmokeTest` | 2 |
| `CoordSpec` | 8 |
| `CatalogBuilderSpec` | 6 |
| `WritersSpec` | 7 |
| `ReadersSpec` | 11 |
| `DependenciesMillWriterSpec` | 9 |
| `DependenciesMillReaderSpec` | 5 |
| `RegenSpec` | 5 |
| `VerifySpec` | 5 |
| `MillSpec` | 6 |
| `PromoteSpec` | 7 |
| **Total** | **71** |

Dependencies (per `build.mill`):

- `no.virtual-architect:toolbox-script:0.1.0-SNAPSHOT`
- `no.virtual-architect:toolbox-proc-oslib:0.1.0-SNAPSHOT`
- `no.virtual-architect:toolbox-fluent:0.1.0-SNAPSHOT`
- `com.indoorvivants::toml::0.3.0` (cross-platform TOML)
- `org.virtuslab::scala-yaml::0.3.1`
- `com.lihaoyi::ujson::3.3.1` (JSON for `mill show` output)
- `org.scalameta::munit::1.0.3` (test scope)

The toolbox dependency is dogfooding — dm consumes the same
`script` / `proc-oslib` / `fluent` modules it manages versions
for. `toolbox publishLocal` must succeed before dm compiles.

## Build System

Mill 1.1.2, pinned via `//| mill-version: 1.1.2` header in `build.mill`.
Single Scala version (3.8.3). `object V` declared inline with every
version literal — this is the deliberate bootstrap exception captured
in [[projects/dependency-manager/adr/0001-deviate-deps-single-file]].
There is no `deps/Dependencies.mill` inside dm itself; the `deps/`
directory holds the central TOML+YAML catalog, not a generated
per-project deps file.

Distribution: `mill dm.assembly` produces a fat jar at
`out/dm/assembly.dest/out.jar`; `bin/dm` is a bash wrapper that
auto-rebuilds the jar if missing.

`flake.nix` provides the dev shell (JDK 21, coursier, git, nodejs 22,
mill) and four flake apps (`test`, `verify`, `check`, `renovate-dryrun`).

## Mill metadata extraction strategy

`dm extract` shells out to `mill show __.mvnDeps` in each target
project. Mill's `show` emits pure JSON to stdout and routes everything
else (logs, progress) to stderr; the subprocess pipeline is

```
mill resolve __                        → list all task paths
filter ends-with(".mvnDeps")           → mvnDeps task paths
for each task: mill show <task>        → JSON array of resolved coords
parse source-form coords (`::` retained as-is) → Coord ADT
build Catalog                          → emit libs.versions.toml + projects.yml
```

Cross-source forms are retained from Mill's source rendering — dm
does *not* normalise `kyo-core_sjs1_3` back to `mvn"io.getkyo::kyo-core"`
on its own. Instead the input is `mill show`'s source-string form
(e.g. `io.getkyo::kyo-core::1.0-RC1`), parsed once by `Coord.parse`
and round-tripped through the `CrossKind` enum.

## Round-trip / tool integration model

```
                ┌────────────────────────────────────────────────┐
  human edits   │   /p/hg/dependency-manager/deps/               │
  or Renovate ──┼──> libs.versions.toml  (handle → coord)        │
                │    projects.yml         (project → handles)    │
                └──────────────────────┬─────────────────────────┘
                                       │ dm regen
                                       v
                ┌────────────────────────────────────────────────┐
                │  /p/hg/<project>/deps/Dependencies.mill        │
                │  (generated; committed; banner says don't edit)│
                └──────────────────────┬─────────────────────────┘
                                       │ build.mill imports Deps
                                       v
                                  mill compile
```

Renovate watches only `deps/libs.versions.toml` in dependency-manager.
Downstream repos never receive direct bot updates. `dm verify` (CI mode)
catches drift between catalog and committed Mill files; `dm promote`
ports hand-edits the other way (downstream Mill → catalog patch),
closing the loop without inviting a second bot to race.

## Things explicitly out of scope for dm

Per `DESIGN.md`:

- Opening PRs (Renovate / human does that).
- Running Mill builds (CI does that).
- Managing Nix flake inputs (`nix flake update` owns that).
- Managing non-Scala deps in any repo (Vite npm deps etc. — Renovate
  handles those directly in the downstream repos).
- Managing platform versions (Scala / ScalaJS / ScalaNative) —
  Renovate's Maven model doesn't cover them; conflating shapes
  in `libs.versions.toml` would be a wrong move. See
  [[projects/dependency-manager/designs/dm-architecture-2026q2-refresh]]
  §"Open questions" for the recorded position.

## Relationship to Other Wiki Knowledge

- **Toolbox dogfooding.** `dm` consumes
  `toolbox-script` / `toolbox-proc-oslib` / `toolbox-fluent` — see
  [[sources/summaries/toolbox]] and
  [[projects/toolbox/adr/0001-adopt-functional-domain-design]].
  Toolbox must be `publishLocal`'d before dm compiles.
  `dm.mill.Mill` exercises `toolbox-proc-oslib`'s `OsLibProcess`
  interpreter and `proc.ProcessDescription` algebra, putting the
  dogfooding rationale on actual code.
- **toml-scala consumption.** Path A: use the Maven-Central artifact
  `com.indoorvivants::toml::0.3.0` directly; the fork at
  `/p/gh/toml-scala` is reference-only. See
  [[sources/tmp/code/toml-scala]] (bridge file, staged for promotion).
- **deps-single-file decision.** `dm` is the *implementation* of a
  generalised version of [[tech/decisions/deps-single-file]]. The
  per-project `deps/Dependencies.mill` is the regenerated output of
  the TOML catalog. The decision itself remains scoped to the
  per-project shape (single file, inline coords); dm extends the model
  to a cross-repo catalog without superseding the decision. See
  [[projects/dependency-manager/adr/0001-deviate-deps-single-file]]
  for dm's own bootstrap deviation, and the three consumer adopt-ADRs
  (slm/0006, toolbox/0003, safetensors-scala/0001) for the
  platforms-only-exception pattern across the v1 consumers.
- **Mill metadata extraction.** Verified against the upstream source
  in `/p/gh/mill/libs/util/src/mill/util/MainModule.scala`. See
  [[mill/llm-wiki/index]] for the Mill API surface.

## Open Questions for Triage (deferred)

Resolved during the 2026-05-29 MVP execution:

- ~~Compile error (Scala 3 mixed-varargs syntax).~~ Fixed: pass `args`
  as a single `Iterable[String]` Shellable.
- ~~Git initialisation.~~ First commit `5459ddb` on branch `main`
  per the personal-repo policy (unsigned, no Co-Authored-By, author
  `tigidar`).

Still deferred to longer-horizon design conversations:

- **`/p/factory/` interaction.** Will the future monorepo absorb dm
  (collapsing it into the monorepo's own deps machinery), or will dm
  continue as a meta-tool managing the monorepo plus any remaining
  standalone repos? Captured as an open question in DESIGN.md.
- **Native CLI target.** Deferred until JVM startup is observed to be
  real friction. Structurally the code is Native-ready (no
  `java.io.File`, only os-lib paths via toolbox-proc-oslib).
- **Platform versions in catalog.** Position recorded: no — Renovate's
  Maven manager doesn't cover them; mixing shapes would be wrong.
  Revisit if a future Renovate manager (or replacement bot) grows
  platform-version awareness. The three consumer adopt-ADRs all
  carry this as their declared exception.

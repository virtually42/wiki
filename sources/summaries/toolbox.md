---
id: summary-toolbox
title: toolbox (composable shell pipelines + process execution) — code summary
kind: descriptive
status: accepted
scope: global
created: 2026-05-29
updated: 2026-05-29
confidence: high
sources:
  - sources/tmp/toolbox.md
tags: [scala, scala-js, scala-native, mill, kyo, fs2, cats-effect, os-lib, shell, process-execution, dsl, library]
---

## What it is

`toolbox` (artifacts under `no.virtual-architect:toolbox-<module>`,
version `0.1.0-SNAPSHOT`, Apache-2.0) is a ten-module Mill build that
splits *composable shell pipelines* and *process execution* into
single-concern artifacts. A consumer that only wants the `Cmd` /
`Pipeline` ADT pulls `toolbox-core` and gets neither the 25 fluent
command builders, nor a process runtime, nor the bash-script renderer.

The repository at `/p/hg/toolbox` is the destination of the
re-layout designed at `/p/v42/toolbox/new-design.md`. At
2026-05-29 it holds ~75 Scala files across the ten target modules
(the README's "Phase A — no sources" wording is stale; sources are
already present). A `git init` was performed during this ingest;
no initial commit has been recorded yet.

## The ten modules and what they do

| Module | Platforms | Deps | What it owns |
|--------|-----------|------|--------------|
| `core` | JVM + JS + Native | none | `Cmd`, `Pipeline`, `CoreCmd`, `Opt`, `Arg`, `Show`, `ArgParser`, 28 `StringContext` interpolators, `toShell` |
| `fluent` | JVM + JS + Native | `core` | 25 builders: `Find`, `Grep`, `Sed`, `Awk`, `Tar`, `Rsync`, `Curl`, `Wget`, `Ssh`, `Scp`, `Jq`, `Yq`, `Fzf`, `Parallel`, `Zip`, `Unzip`, `Ffmpeg`, `NixBuild`, `NixCopy`, `NixRun`, `NixFlakeCheck`, `NixFlakeUpdate`, `NixosRebuild`, plus `FluentCmd` |
| `script` | JVM + JS + Native | `core` + `slm` | `ToScript`, `ScriptConfig`, `SetOptions` — pipeline → bash via `SourceFile` |
| `proc` | JVM + JS + Native | `core` | `ProcessDescription` (Single, Chain, ChainAll, AndThen, OrElse), `ProcessSpec`, `StreamTarget`, `ToProcessDescription[A]`, `ProcessRunner[F]`, `ProcessError` |
| `proc-oslib` | JVM + Native | `proc` + os-lib | `OsLibProcess`, `OsLibRunner` — one shared `src/`, platform-specific `src-jvm/` / `src-native/` for divergences |
| `proc-node` | JS | `proc` | `JsProcess`, `JsRunner`, `JsCommandResult`, `ChildProcess` facade over `node:child_process` — ES module output required |
| `vfs` | JVM + JS + Native | `slm` | `VirtualFileSystem`, `VPath`, `VEntry`, `VfsError`, `EmulatedCmd`, `EmulatedInterpreter` — pure immutable file system, files keyed by `SourceFile` content |
| `proc-fs2` | JVM | `proc` + `vfs` + fs2-core + fs2-io + cats-effect | `SandboxRunner` (real-process interception) + `VfsSandboxRunner` (VFS emulation), both with event streams |
| `proc-kyo` | JVM + JS | `proc` + kyo-core + (`proc-oslib` JVM / `proc-node` JS) | `KyoProcess`, `KyoRunner`, `KyoCommandResult` — Kyo wrapper over the platform interpreter |
| `example` | JVM + JS + Native | per-platform mix | Demos. Native target has a `dist` task that places an optimized binary at `toolbox-example` in the repo root |

The dependency graph is rooted at `core` (the pipeline algebra) and
`slm` (used by `script` and `vfs`). `proc` is the algebra base for all
four `proc-*` interpreter modules — the `proc-*` naming convention
makes the "algebra plus N interpreters" pattern legible from `ls`
alone, and slots in future runners (`proc-zio`, `proc-direct`, …)
without surprise.

## Why this layout

The design at `/p/v42/toolbox/new-design.md` (the source of truth
outside the wiki) records seven problems the re-layout addresses:

1. The old `shell` module was overloaded (162 LOC of `Cmd`/`Pipeline`
   algebra + 481 LOC of `Coreutils` + 25 fluent builders, all in one
   artifact).
2. The old `ops` mixed pure process algebra with platform interpreters
   (os-lib + Node) in the same module.
3. `ops` declared a stale `moduleDeps = Seq(shell, dsl)` despite no
   `dsl.*` imports.
4. The os-lib JVM and Native copies were near-duplicates with no
   shared source tree.
5. The pure VFS was trapped inside `sandbox` and could not be reused
   without pulling fs2 + cats-effect.
6. `sandbox` was two interpreters (real-process interception +
   emulated execution) sharing one module.
7. The planned `stdio` / `pty` / `terminal` stack had no clean slot
   parallel to the existing process layer.

The new layout is one-module-one-concern: pulling just the pipeline
ADT no longer drags in 25 builders, the os-lib code lives in one
shared tree, and the VFS is independently consumable. The migration
is also a behaviour-preserving refactor by design — the README and
new-design §9 call out "no new functionality, no build-tool change,
no effect-system change, no public-API redesign."

## Build wiring (Mill 1.1.2)

Single `build.mill` with `object V` declaring versions inline:

```
scalaVersions = Seq("3.8.3")     # cross-publish wiring in place,
                                 # pinned to one version today
scalaJS     = 1.20.1
scalaNative = 0.5.12
osLib       = 0.11.7
kyoCore     = 1.0-RC1
catsEffect  = 3.6.1
fs2         = 3.12.0
slm         = 0.2.0-SNAPSHOT
munit       = 1.0.3
munitCatsEffect = 2.1.0
```

This matches the `object V` inline-versions convention from
[[sources/summaries/sourceline-manager]] and deviates from
[[tech/decisions/deps-single-file]] on the same grounds (small,
single-file build; per-module `mvnDeps` are clearer than a redirect
through `deps/Dependencies.mill`).

**Module-name encoding** (README §Module-name encoding): on-disk
directories are kebab (`proc-oslib`, `proc-node`, `proc-fs2`,
`proc-kyo`); Mill identifiers in `build.mill` are camelCase
(`procOslib`, `procNode`, …) and each `proc-*` object overrides
`def moduleDir = super.moduleDir / os.up / "<kebab>"` to bind the
camel identifier to the kebab directory. Each module overrides
`def artifactName` to the kebab form, so published coordinates are
`no.virtual-architect:toolbox-<kebab>`.

**Cross-platform layout.** Uses the `Cross[]` + manual `sharedSources`
hybrid catalogued in [[tech/guides/mill-cross-platform]]:

```
<module>/src/                     shared sources, all platforms
<module>/<platform>/              Cross-variant moduleDir (jvm/js/native)
<module>/src-jvm/  src-js/  src-native/    platform divergences
<module>/test/src/                shared test sources
<module>/test-jvm/src/            proc-kyo: JVM-only integration tests
```

Path math: `Task.Sources(moduleDir / os.up / "src")` from a Cross
variant lands on `<module>/src/`; tests use two `os.up` hops to reach
`<module>/test/src/`. This is the same shape that produced the
silent-empty-jar incident in sourceline-manager 0.1.0 and is the
load-bearing example in
[[tech/guides/mill-cross-platform]] §Pitfalls — the lesson there
("`mill show <module>.sources` + `jar tf` is the only honest
check") applies here directly.

**ES modules.** `proc-node`, `proc-kyo` JS, and `example` JS all set
`moduleKind = ModuleKind.ESModule`. This is mandatory because those
modules import Node built-ins via
`@JSImport("node:child_process", JSImport.Namespace)`; the default
CommonJS output cannot resolve `node:` scheme imports.

`flake.nix` provides the dev shell — JDK, Mill, Scala Native
toolchain.

## Cross-cutting type choices

A scan of the source confirms the same functional-domain shape used in
sourceline-manager:

- `enum Cmd derives CanEqual` with 15 constructors plus a `Raw(String)`
  escape hatch. `def toShell: String` is a total pattern match.
  Operators `>` / `>>` lift a `Cmd` into a `Pipeline` with stdout
  redirection.
- `enum StreamTarget derives CanEqual` with `Inherit`, `Pipe`,
  `DevNull`, `ToFile(path, append)`, `FromFile(path)`.
- `final case class ProcessSpec(command, args: Vector[String],
  stdin, stdout, stderr: StreamTarget) derives CanEqual`.
- `final case class VirtualFileSystem(entries: Map[VPath, VEntry],
  cwd: VPath) derives CanEqual` with read operations returning
  `Either[VfsError, A]` instead of throwing.
- `KyoCommandResult` carries `exitCode` / `stdout` / `stderr` and
  exposes `isSuccess` / `text` / `lines` / `toEither` — total
  functions over the value, no exceptions.

This matches [[tech/patterns/functional-domain-design]] in its
declarative encoding: ADTs + smart constructors + operators + explicit
rendering, with `Either` for error returns.

## Compliance scan against current normative pages

| Page | In scope? | Stance | Evidence |
|------|-----------|--------|----------|
| [[tech/patterns/functional-domain-design]] | Yes (Scala, any domain) | **Adopts**, declarative encoding | `enum Cmd` / `enum StreamTarget` ADTs, `derives CanEqual`, total `toShell`, smart-constructor `ProcessSpec.apply`, `Either[VfsError, A]` returns, `KyoCommandResult.toEither` |
| [[tech/decisions/deps-single-file]] | Yes (Scala, any domain) | **Deviates** (same reasons as sourceline-manager) | `build.mill` has `object V` inline; multiple external deps but the file remains the single source of truth |
| [[tech/guides/mill-cross-platform]] | Yes | **Adopts**, hybrid Pattern B + platform-specific dirs | `sharedSrc = Task.Sources(moduleDir / os.up / "src")` in `ToolboxCommon`; `platformSrc` for `src-jvm/` / `src-native/` / `src-js/` on `proc-oslib`, `proc-node`, `proc-kyo`, `example` |
| [[tech/stack/mill]] | Yes | **Adopts** | Mill 1.1.2 pinned via `//| mill-version:` header; `Cross[]` wired but single Scala version (3.8.3); SNAPSHOT workflow note from sourceline-manager applies because `script` and `vfs` consume `slm:0.2.0-SNAPSHOT` |
| [[tech/stack/kyo]] | Partially (only `proc-kyo`) | **Adopts** | `proc-kyo` is the Kyo-effect wrapper module; consumes `io.getkyo::kyo-core::1.0-RC1` |

No other accepted normative pages currently apply.

## What this exposes that sourceline-manager did not

- **Platform-specific source directories at scale.** sourceline-manager
  had zero platform surface and never used `src-jvm/` / `src-native/`
  / `src-js/`. `toolbox` uses all three across `proc-oslib`,
  `proc-node`, `proc-kyo`, and `example`. This is the second worked
  example for [[tech/guides/mill-cross-platform]] and the first to
  exercise the JS-side ES-module requirement for `@JSImport` of
  Node built-ins.
- **Interpreter family pattern.** One algebra (`proc`) plus N
  interpreters (`proc-oslib`, `proc-node`, `proc-fs2`, `proc-kyo`)
  named so the relationship is visible in the directory listing. This
  is a candidate promotion to [[tech/patterns/]] if it recurs in other
  projects.
- **SNAPSHOT consumption from a sibling repo.** `script` and `vfs`
  depend on `no.virtual-architect:sourceline-manager:0.2.0-SNAPSHOT`,
  not on a Mill `moduleDeps` reference. The publishLocal workflow
  documented in [[tech/stack/mill]] is the operational handle here.

## Open Questions for triage

1. ~~Should `toolbox` become a wiki project?~~ **Resolved
   2026-05-29:** Yes — registered in [[index]] §Projects with a
   `projects/toolbox/` directory and two ADRs recording stance on
   [[tech/patterns/functional-domain-design]] (adopt) and
   [[tech/decisions/deps-single-file]] (deviate).
2. Should `/p/v42/toolbox/new-design.md` be ingested as a
   `design-doc`? If yes, it should land under
   `projects/toolbox/designs/`. Open.
3. README still claims "no sources" while ~75 Scala files exist.
   Documentation drift on the source repo; should be corrected on a
   future README edit pass.
4. The bridge file lives at `sources/tmp/` and needs an initial git
   commit before it can graduate to `sources/raw/code/toolbox.md`
   with a real `commit:` SHA. `git init` was performed during the
   ingest but no commit has been recorded.

## Project status

Pre-1.0. Module skeleton complete and populated with ~75 Scala files.
Mill 1.1.2 build wired with `Cross[]` over a single Scala version
(3.8.3). One published artifact per module under
`no.virtual-architect:toolbox-<kebab>`. License Apache-2.0. The
working tree is under version control as of 2026-05-29 but the
initial commit has not been made.

## Links

- [[sources/tmp/toolbox]] — source pointer (bridge file, staged for triage)
- [[projects/toolbox/index]] — project page (wiki-side artefacts)
- [[projects/toolbox/adr/0001-adopt-functional-domain-design]] — adoption ADR
- [[projects/toolbox/adr/0002-deviate-deps-single-file]] — deviation ADR
- [[sources/summaries/sourceline-manager]] — sibling foundation library used by `script` and `vfs`
- [[tech/patterns/functional-domain-design]] — the pattern this code adopts
- [[tech/decisions/deps-single-file]] — the decision this code deviates from
- [[tech/guides/mill-cross-platform]] — the cross-platform build pattern in use
- [[tech/stack/mill]] — the build tool
- [[tech/stack/kyo]] — used by `proc-kyo`

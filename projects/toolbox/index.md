# toolbox

Composable shell pipelines + platform-agnostic process execution.
Ten Mill modules — pipeline algebra (`core`), fluent builders
(`fluent`), bash-script renderer (`script`), process algebra
(`proc`) with four interpreters (`proc-oslib`, `proc-node`,
`proc-fs2`, `proc-kyo`), pure virtual filesystem (`vfs`), and
per-platform demos (`example`). Published per-module under
`no.virtual-architect:toolbox-<kebab>`.

**Status:** active

## Stack

- Language: Scala 3 (3.8.3, cross-publish-wired for next LTS)
- Platforms: JVM, Scala.js, Scala Native (varies per module — see
  [[sources/summaries/toolbox]] for the platform matrix)
- Effects: Kyo (only in `proc-kyo`); fs2 + cats-effect (only in
  `proc-fs2`)
- Build: Mill 1.1.2, Nix dev shell (JDK + Mill + Scala Native toolchain)
- Tests: MUnit; munit-cats-effect for `proc-fs2`
- Depends on: [[sources/summaries/sourceline-manager]] (used by
  `script` and `vfs`)

## Code Location

`/p/hg/toolbox` — see [[sources/tmp/toolbox]] (bridge, staged for
human promotion to `sources/raw/code/`) and
[[sources/summaries/toolbox]] for the distilled view.

The repository lives outside `projects/toolbox/`; this wiki folder
holds only the project's wiki-side artefacts (ADRs, plans, syntheses,
log). The design source of truth lives **outside this wiki** at
`/p/v42/toolbox/new-design.md`; if/when that document is ingested it
should land under `projects/toolbox/designs/`. There are no in-tree
ADRs in `/p/hg/toolbox` — design decisions live in `new-design.md`
and the README.

## Embedding Path

`new-design.md` and the README treat `/p/hg/toolbox` as a standalone
repository today. When it joins the monorepo, the per-module
`build.mill` becomes a `package.mill` under the toolbox subtree.

External Maven library coordinates are already managed via dm
(see [[projects/dependency-manager/index]]); the original
deviation against [[tech/decisions/deps-single-file]] (recorded
in [adr/0002-deviate-deps-single-file.md](adr/0002-deviate-deps-single-file.md))
was superseded on 2026-05-29 by
[adr/0003-adopt-deps-single-file.md](adr/0003-adopt-deps-single-file.md)
once toolbox migrated to consume `build.deps.Deps.*` from the
catalog. The remaining narrow exception is the platform-versions
half of the decision (Scala / ScalaJS / ScalaNative stay inline
in `object V`).

## Pages

### ADRs (wiki-side; record stance on global normative pages)

- [adr/0001-adopt-functional-domain-design.md](adr/0001-adopt-functional-domain-design.md) — Adopt [[tech/patterns/functional-domain-design]] (declarative encoding; evidence: `enum Cmd`, `enum StreamTarget`, `ProcessSpec`, `VirtualFileSystem`, `KyoCommandResult` — all ADTs with `derives CanEqual`, total functions, `Either` returns)
- [adr/0002-deviate-deps-single-file.md](adr/0002-deviate-deps-single-file.md) — **superseded** by adr/0003 after the dm migration; retained for reasoning history
- [adr/0003-adopt-deps-single-file.md](adr/0003-adopt-deps-single-file.md) — Adopt [[tech/decisions/deps-single-file]] for library coordinates (via dm-generated `deps/Dependencies.mill`); narrow platforms-only exception

### Designs
*No wiki-side designs yet. Design source of truth is
`/p/v42/toolbox/new-design.md` (not yet ingested).*

### Plans
*No plans yet. The migration plan in `/p/v42/toolbox/new-design.md` §7
covers the source-of-truth sequencing.*

### Tickets
*No tickets yet.*

### Syntheses
*No syntheses yet.*

### Other
- [log.md](log.md)

*Note: `architecture.md` is a schema-standard page but does not yet
exist for this project — the design source `new-design.md` covers the
same material until a wiki-side architecture page is needed.*

## Module Summary

| Module | Platforms | Deps | Owns |
|--------|-----------|------|------|
| `core` | JVM + JS + Native | (none) | `Cmd`, `Pipeline`, `Coreutils`, 28 interpolators |
| `fluent` | JVM + JS + Native | `core` | 25 builders (Find, Grep, Sed, …, Ffmpeg) |
| `script` | JVM + JS + Native | `core` + slm | `ToScript` — pipeline → bash via `SourceFile` |
| `proc` | JVM + JS + Native | `core` | `ProcessDescription` / `ProcessSpec` / `StreamTarget` / `ProcessRunner[F]` |
| `proc-oslib` | JVM + Native | `proc` + os-lib | `OsLibProcess` / `OsLibRunner` (shared `src/`, divergences in `src-jvm/` / `src-native/`) |
| `proc-node` | JS | `proc` | `JsProcess` / `JsRunner` / `ChildProcess` facade (ES modules required) |
| `vfs` | JVM + JS + Native | slm | `VirtualFileSystem` / `VPath` / `VEntry` — pure immutable FS |
| `proc-fs2` | JVM | `proc` + `vfs` + fs2 + CE | `SandboxRunner` + `VfsSandboxRunner` |
| `proc-kyo` | JVM + JS | `proc` + kyo-core + (`proc-oslib` JVM / `proc-node` JS) | `KyoProcess` / `KyoRunner` / `KyoCommandResult` |
| `example` | JVM + JS + Native | per-platform | Demos; Native `dist` task produces a binary at repo root |

The full table including dependencies, exclusions, and the rationale
for each module is in [[sources/summaries/toolbox]].

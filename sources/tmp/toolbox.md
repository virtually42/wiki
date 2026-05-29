---
id: source-toolbox
type: code
repo: /p/hg/toolbox
last_observed: 2026-05-29
commit: uninitialized-tree
branch: main
git_init_state: fresh — `git init` on 2026-05-29, no commits yet
entry_points:
  - README.md
  - build.mill
  - flake.nix
  - core/src/core/Bash.scala
  - core/src/core/Coreutils.scala
  - fluent/src/fluent/
  - script/src/script/ToScript.scala
  - proc/src/proc/ProcessDescription.scala
  - proc/src/proc/ProcessRunner.scala
  - proc-oslib/src/proc/oslib/
  - proc-node/src/proc/node/
  - vfs/src/vfs/VirtualFileSystem.scala
  - proc-fs2/src/proc/fs2/
  - proc-kyo/src/proc/kyo/KyoCommandResult.scala
  - example/src/example/Example.scala
design_source_of_truth: /p/v42/toolbox/new-design.md
---

## Structure Overview

`toolbox` is the destination of the module re-layout described in
`/p/v42/toolbox/new-design.md`. It collects composable shell-pipeline
algebra, fluent command builders, a bash-script renderer, a
platform-agnostic process-execution algebra with three interpreters
(os-lib, Node, Kyo), a pure virtual filesystem, and an fs2/CE
sandboxing layer — published under `no.virtual-architect` with a
kebab-case `toolbox-<module>` artifact-name convention.

The README labels the repo "**pre-migration scaffold** (Phase A —
module layout only, no sources)", but the on-disk state at
`last_observed` already contains ~75 Scala files across the ten target
modules; treat that line as documentation drift, not as a description
of the current tree. A `git init` was performed during this ingest
(branch `main`, unsigned-commit config, author tigidar) so the tree
is now under version control, but no initial commit has been made
yet — that is a separate decision left for the human.

## Key Modules

Ten Mill modules, each with kebab-case on-disk directory and a
`toolbox-<kebab>` published artifact name:

| Module        | Platforms        | Deps                                        | Role |
|---------------|------------------|---------------------------------------------|------|
| `core`        | JVM + JS + Native | (none)                                      | `Cmd` / `Pipeline` ADTs + `Coreutils` (Show, Opt, Arg, ArgParser, 28 interpolators) |
| `fluent`      | JVM + JS + Native | `core`                                       | 25 fluent builders — Find/Grep/Sed/Awk/Tar/Rsync/Curl/Wget/Ssh/Scp/Jq/Yq/Fzf/Parallel/Zip/Unzip/Ffmpeg + 5 Nix builders |
| `script`      | JVM + JS + Native | `core` + `slm`                              | `ToScript` — pipeline → bash via SourceFile |
| `proc`        | JVM + JS + Native | `core`                                       | `ProcessDescription` / `ProcessSpec` / `StreamTarget` / `ToProcessDescription` / `ProcessRunner[F]` / `ProcessError` |
| `proc-oslib`  | JVM + Native (no JS) | `proc` + os-lib                          | `OsLibProcess` / `OsLibRunner` — shared `src/`, platform-specific `src-jvm/` and `src-native/` |
| `proc-node`   | JS only          | `proc`                                      | `JsProcess` / `JsRunner` / `JsCommandResult` / `ChildProcess` facade — `node:child_process` via `@JSImport`, requires ES module output |
| `vfs`         | JVM + JS + Native | `slm`                                       | `VirtualFileSystem` / `VPath` / `VEntry` / `VfsError` / `EmulatedCmd` / `EmulatedInterpreter` — pure immutable filesystem keyed by `SourceFile` content |
| `proc-fs2`    | JVM only         | `proc` + `vfs` + fs2-core + fs2-io + cats-effect | `SandboxRunner` (real-process interception) + `VfsSandboxRunner` (VFS-backed emulation) — both `SandboxEvent` / `VfsEvent` streams |
| `proc-kyo`    | JVM + JS (no Native) | `proc` + kyo-core + (`proc-oslib` JVM / `proc-node` JS) | `KyoProcess` / `KyoRunner` / `KyoCommandResult` — Kyo wrapper over the platform interpreter |
| `example`     | JVM + JS + Native | per-platform mix                           | Demos; the Native target has a `dist` task that produces an optimized binary at `toolbox-example` in the repo root |

The dependency graph (new-design §3.1) is a DAG rooted at `core` /
`slm` with `proc` as the algebra base for all `proc-*` interpreter
modules.

## Build System

Mill 1.1.2, pinned via `//| mill-version: 1.1.2` header in `build.mill`.
Single Scala version today (`3.8.3`); `V.scalaVersions = Seq("3.8.3")`
is the only knob to bump for cross-publishing.

Module-name encoding (verbatim from README §Module-name encoding):
- On-disk directories use kebab: `proc-oslib/`, `proc-node/`, `proc-fs2/`, `proc-kyo/`.
- `build.mill` identifiers use camelCase: `object procOslib`, `object procNode`, …
- Each `proc-*` Mill object overrides `def moduleDir = super.moduleDir / os.up / "<kebab>"` so Mill resolves the camel identifier to the kebab directory.
- Each module overrides `def artifactName` to its kebab form (`toolbox-proc-oslib`, …).

Cross-platform layout (see [[tech/guides/mill-cross-platform]]):
- Shared sources at `<module>/src/`, picked up via
  `Task.Sources(moduleDir / os.up / "src")` on every Cross variant.
- Platform divergences at `<module>/src-jvm/`, `<module>/src-native/`,
  `<module>/src-js/` (used in `proc-oslib`, `proc-node`, `proc-kyo`,
  `example`).
- Tests share `<module>/test/src/` via `Task.Sources(moduleDir / os.up / os.up / "test" / "src")`.
  `proc-kyo` JVM additionally pulls a JVM-only suite from
  `<module>/test-jvm/src/`.

JS modules that import Node built-ins (`proc-node`, `proc-kyo` JS,
`example` JS) set `moduleKind = ModuleKind.ESModule` — required for
`@JSImport("node:child_process", JSImport.Namespace)` to resolve.

`flake.nix` provides the dev shell — JDK, Mill, and the Scala Native
toolchain.

## Relationship to Other Wiki Knowledge

- **Design source of truth.** Lives outside this wiki at
  `/p/v42/toolbox/new-design.md`. That document captures the
  module-by-module rationale (10 sections + migration plan + open
  questions) and is the authority for *why* the layout looks like
  this. The wiki has not ingested this design doc yet — that is a
  separate ingest, gated on human triage of where it should land.
- **`slm` dependency.** `script` and `vfs` consume
  `no.virtual-architect:sourceline-manager:0.2.0-SNAPSHOT`
  (see [[sources/summaries/sourceline-manager]]).
- **Cross-platform Mill pattern.** The `Cross[]` + manual
  `sharedSources` hybrid documented in
  [[tech/guides/mill-cross-platform]] is the pattern used throughout
  `build.mill`, including the platform-specific `src-jvm/` / `src-native/`
  / `src-js/` directories on `proc-*`.
- **Kyo wrapper.** `proc-kyo` is a candidate consumer-side example of
  [[tech/stack/kyo]] effect wrapping over a non-Kyo runner.

## Open Questions for Triage

These should be answered by a human before this bridge graduates from
`sources/tmp/` to `sources/raw/code/`:

1. **Is `toolbox` a wiki project?** It is not listed in
   [[index.md]] under Projects. If yes, it needs a
   `projects/toolbox/` directory (index, ADRs, design link) and an
   entry in the Projects table. If it is purely a code source
   referenced from other projects, leave it as a source only.
2. **Should the design doc at `/p/v42/toolbox/new-design.md` be
   ingested?** It is a forward-looking architectural exploration —
   `design-doc` shape per [[meta/schema]]. Either copy it into
   `projects/toolbox/designs/` (if toolbox becomes a project) or keep
   it external and reference it from the bridge.
3. **README states "pre-migration scaffold, no sources" but sources
   exist.** Either Phase A has progressed past the README's claim, or
   the visible sources are pre-existing. Document the actual state in
   the README, or update this bridge once clarified.
4. **Initial commit.** `git init` was run on 2026-05-29 (branch
   `main`, signing disabled, author tigidar per the personal-repo
   policy), but no initial commit has been recorded. Once committed,
   the bridge's `commit:` field should be updated from
   `uninitialized-tree` to the SHA, and the bridge can graduate from
   `sources/tmp/` to `sources/raw/code/toolbox.md`.

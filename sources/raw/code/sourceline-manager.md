---
id: source-sourceline-manager
type: code
repo: /p/hg/sourceline-manager
last_observed: 2026-05-29
commit: e4c15c2bf689148ec6a26cc5f91881e93906afcb
entry_points:
  - build.mill
  - slm/src/slm/SourceLine.scala
  - slm/src/slm/SourceFile.scala
  - slm/test/src/slm/
  - docs/adr/0001-adt-source-code-representation.md
  - docs/adr/0002-functional-domain-design.md
  - docs/adr/0003-cross-platform-via-shared-sources.md
  - docs/adr/0004-scala-version-policy.md
  - flake.nix
---

## Structure Overview

`sourceline-manager` is a foundation library that models source code as
an algebraic data type — `Token` / `SourceLine` / `SourceFile` — and
renders it to text as the last step. Maven coordinates
`no.virtual-architect:sourceline-manager:0.2.0-SNAPSHOT`; base package
`slm`. License Apache-2.0.

The library has no platform surface: it depends only on
`scala.collection.immutable`, `Option`, `String`, `Int`, and
`derives CanEqual`. Three Mill modules — `slm.jvm`, `slm.js`,
`slm.native` — compile the same `slm/src/` tree against one Scala
version today (3.8.3), wired for `Cross[]` to drop in the next LTS
without a code change.

In-tree ADRs (`docs/adr/`) record the four decisions that shape the
library:

| # | Decision | Maps to wiki page |
|---|----------|-------------------|
| 0001 | Source code is data, not strings | (project-local; no global counterpart) |
| 0002 | Functional domain design | [[tech/patterns/functional-domain-design]] |
| 0003 | Cross-platform via shared sources | [[tech/guides/mill-cross-platform]] (Pattern B/hybrid; see Pitfalls) |
| 0004 | Scala version policy | (project-local; no global counterpart yet) |

## Key Modules

- `slm/src/slm/SourceLine.scala` — `enum Token`, `final case class SourceLine` (private ctor + smart constructors), monoidal `++` / `|+|` / `combine`, `indent`, `map`, `flatMap`, `filter`, `render`.
- `slm/src/slm/SourceFile.scala` — `final case class SourceFile`, monoidal `++`, inline-merge `joinLines` / `|++|`, line-level transformations, `SourceFileBuilder` fluent DSL, `render` with parameterized indent / token / line separators.
- `slm/test/src/slm/` — shared MUnit suite asserting the monoid laws (left identity, right identity, associativity) on both `SourceLine` and `SourceFile`.

## Build System

Mill 1.1.2 pinned via `.mill-version`. `build.mill` defines `object V`
inline (single dependency: `munit`; platform versions for Scala /
Scala.js / Scala Native; organization / artifact / version constants)
and three `Cross[]` modules over `V.scalaVersions`.

Cross-platform layout uses the `Cross[]` + manual `Task.Sources(moduleDir / os.up / "src")` hybrid documented under
[[tech/guides/mill-cross-platform]] §Pitfalls. The 0.1.0 release of this
library was the source of the silent-empty-jar incident captured in that
section.

Nix flake (`flake.nix`) provides the dev shell: JDK 21, Mill,
Scala Native toolchain.

## Embedding Path

The README documents a clean move into the monorepo: rename
`build.mill` → `package.mill`, replace the header with
`//| mill-allow-nested-build-mill: true` + `package build.sourceline-manager`.
No source or test changes are required.

## Related Wiki Pages

- [[tech/patterns/functional-domain-design]] — the global pattern this library exemplifies (ADR-0001 + ADR-0002 together).
- [[tech/guides/mill-cross-platform]] — Pitfalls section uses sourceline-manager 0.1.0 as its load-bearing example.
- [[tech/stack/mill]] — SNAPSHOT workflow note that emerged from the publishLocal incident.
- [[projects/sourceline-manager/index]] — wiki-side project page.

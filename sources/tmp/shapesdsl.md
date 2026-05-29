---
id: source-shapesdsl
type: code
repo: /p/hg/shapesdsl
last_observed: 2026-05-29
commit: uninitialized-tree
branch: main
git_init_state: fresh — `git init` on 2026-05-29, no commits yet
entry_points:
  - README.md
  - build.mill
  - flake.nix
  - core/src/shapesdsl/Shape.scala
  - core/src/shapesdsl/ShapeScene.scala
  - core/src/shapesdsl/ShapeStyle.scala
  - core/src/shapesdsl/ColorScale.scala
  - core/src/shapesdsl/Effect.scala
  - core/src/shapesdsl/dsl.scala
  - heatmap/src/shapesdsl/Heatmap.scala
  - heatmap/src/shapesdsl/Heatmaps.scala
  - heatmap/src-jvm/shapesdsl/HeatmapImage.scala
  - heatmap/src-jvm/shapesdsl/HeatmapDemo.scala
  - svg/src/shapesdslsvg/SvgShapeInterpreter.scala
source_repo: /p/v42/tagless
design_source_of_truth: (none — module boundaries derived from existing
                       shapesdsl + shapesdslsvg modules in /p/v42/tagless)
---

## Structure Overview

`shapesdsl` is the destination of a sibling breakout from the same
monolithic source as `tagless` (see [[sources/raw/code/tagless]]).
It hosts a declarative 2D shape ADT, a heatmap built on top of it,
and an SVG interpreter that bridges shapes into the `tagless-core`
HTML DSL.

The breakout split the source's two-module structure
(`shapesdsl`, `shapesdslsvg`) into **three** modules so that:

- `shapesdsl-core` is dep-free; useful as a portable shape algebra.
- `shapesdsl-heatmap` carries the `Heatmap` ADT and its Java2D PNG
  renderer; consumers that only want shapes don't pull `java.awt`.
- `shapesdsl-svg` carries the `SvgShapeInterpreter` which depends on
  `tagless-core` (consumed via publishLocal SNAPSHOT). Consumers
  rendering to non-SVG targets don't pull tagless.

A `git init` was performed (branch `main`, unsigned-commit config,
author `tigidar`); no initial commit has been recorded yet.

## Modules

| Module | Platforms | Deps | Artifact |
|--------|-----------|------|----------|
| `core` | JVM, JS | — | `shapesdsl-core` |
| `heatmap` | JVM, JS | `core` | `shapesdsl-heatmap` |
| `svg` | JVM, JS | `core` + `no.virtual-architect:tagless-core` (Maven) | `shapesdsl-svg` |

### One structural code change during the breakout

The source's `core/dsl.scala` (in the monolithic `shapesdsl` module)
had a `heatmap[T]` factory inside `object dsl` that returned the
`Heatmap` ADT. Splitting `Heatmap` into its own module would have
created a back-edge from `core` → `heatmap`. Moved the factory to
`heatmap/src/shapesdsl/Heatmaps.scala` (`object Heatmaps` in
`package shapesdsl`). Consumers `import shapesdsl.Heatmaps.heatmap`
to use it. The original two call sites (HeatmapDemo, HeatmapSpec)
were updated to add this import.

(I first tried a sub-package `package shapesdsl.heatmap`, but
Scala.js compilation rejected it with "Trying to define package
with same name as class heatmap". Falling back to a top-level
`object Heatmaps` in `package shapesdsl` avoided the conflict.)

## Build

- Mill 1.1.2, JDK 21, Scala 3.8.3, Scala.js 1.20.1
- `object V` inline; `tagless = "0.1.0-SNAPSHOT"` (publishLocal coord)
- `no.virtual-architect` group · `0.1.0-SNAPSHOT` version
- `mill __.compile` ✓ across 3 modules × 2 platforms
- `mill __.fastLinkJS` ✓
- `mill __.publishLocal` ✓ (all six artifacts pushed to `~/.ivy2/local`)

## Tests

Distributed per concern. JVM-only (matches source).

| Module | Specs |
|--------|-------|
| `core` | DslSpec, EffectSpec, ShapeSpec, ShapeStyleSpec |
| `heatmap` | HeatmapSpec |
| `svg` | SvgShapeInterpreterSpec |

All `mill <m>.jvm[3.8.3].test.testForked` ✓.

## Skipped during breakout

- The rest of `/p/v42/tagless` (tagless, animdsl, presenter, demo
  apps) — out of scope for *this* breakout.
- No other working files; the shapesdsl + shapesdslsvg subtrees
  contained only source + tests.

## Compliance scan

| Norm | Stance |
|------|--------|
| `tech/patterns/functional-domain-design` | **adopts** — `enum Shape`, `final case class Heatmap`, `ShapeScene` ADT, pure builder methods, `derives CanEqual` |
| `tech/decisions/deps-single-file` | **deviates** — versions inline in `object V` (standalone breakout) |
| `tech/guides/mill-cross-platform` | **adopts** — `sharedSrc` + `os.up` pattern, kebab-only module names |

## Related

- [[sources/raw/code/tagless]] — sibling repo (HTML DSL family;
  `shapesdsl-svg` consumes `tagless-core`)
- [[tech/guides/breakout]] — procedure followed

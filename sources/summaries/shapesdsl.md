---
id: summary-shapesdsl
title: shapesdsl (declarative 2D shape + heatmap DSL) — code summary
kind: descriptive
status: accepted
scope: global
created: 2026-05-29
updated: 2026-05-29
confidence: high
sources:
  - sources/tmp/shapesdsl.md
tags: [scala, scala-js, mill, dsl, shape, heatmap, svg, java2d, library, breakout]
---

## What it is

`shapesdsl` (artifacts under `no.virtual-architect:shapesdsl-<module>`,
version `0.1.0-SNAPSHOT`, Apache-2.0) is a three-module Mill build
that decomposes a declarative 2D shape DSL into **focused artifacts**:

- `shapesdsl-core` — the shape algebra (`Shape` ADT, `ShapeStyle`,
  `ShapeScene`, `ColorScale`, `Effect`, builder DSL). No deps.
- `shapesdsl-heatmap` — `Heatmap` ADT (rectangular grid of cells with
  color-scale mapping) plus a JVM-only Java2D `HeatmapImage` PNG
  renderer and `HeatmapDemo`. Depends on `shapesdsl-core`.
- `shapesdsl-svg` — `SvgShapeInterpreter` rendering shapes/scenes
  to SVG via the `tagless-core` HTML DSL. Depends on
  `shapesdsl-core` and (cross-repo, via `publishLocal`)
  `no.virtual-architect:tagless-core:0.1.0-SNAPSHOT`.

A consumer rendering shapes to a non-SVG target (canvas, raw
geometry) pulls only `shapesdsl-core` and gets none of the heatmap
weight or the tagless dependency. A consumer producing PNG heatmaps
without SVG pulls `shapesdsl-core` + `shapesdsl-heatmap`. Three
separate flips on the open-source / internal axis.

The repository at `/p/hg/shapesdsl` is the destination of a sibling
breakout from `/p/v42/tagless`, executed on 2026-05-29 after the
`tagless` breakout. `git init` was performed; no initial commit
recorded.

## The three modules

| Module | Platforms | Deps | What it owns |
|--------|-----------|------|--------------|
| `core` | JVM + JS | none | `enum Shape derives CanEqual` (`Box`, `Circle`, `Ellipse`, `Line`, `Path`, `Polygon`, `Group`, `Text` plus a `Style` wrapper); `ShapeStyle` immutable config; `ShapeScene` as a `Vector[Shape]` with scene-level styling; `ColorScale` (named gradients + custom stops); `Effect` (rotate / translate / scale / opacity); `dsl` (`box`, `circle`, `text`, `path`, `group`, …) |
| `heatmap` | JVM + JS | `core` | `final case class Heatmap derives CanEqual` (`data`, `colorScale`, `cellSize`, `showValues`, row/col labels, border, font); builder methods (`withColorScale`, `withCellSize`, `withValues`, `withCellLabels`, `withRowLabels`, `withColLabels`); `toScene` projects to a `ShapeScene`. **JVM only**: `HeatmapImage.toPng(Heatmap): Array[Byte]` via Java2D + `javax.imageio`, plus a `@main` `heatmapDemo` |
| `svg` | JVM + JS | `core` + `tagless-core` | `SvgShapeInterpreter.toSvg(scene: ShapeScene): tags.Node` — pure fold over the scene producing tagless-core `Node` values; the SVG element/attribute names come from raw strings (no dep on `tagless-svg` — only the `Node`/`Attr` types from `tagless-core`) |

Dependency graph: `core` ← `heatmap` ← (cross-repo) `tagless-core`
← `svg`. Three roots; only `svg` reaches out of repo.

## Why this layout

The user's general principle (granular focused artifacts so each
can be independently open- or closed-sourced; mill `publishLocal`
SNAPSHOTs wire downstream consumers) applies the same way as for
`tagless`. The specific calls for this repo:

1. **Heatmap is its own module.** The Java2D PNG renderer pulls
   in `java.awt` and `javax.imageio` on the JVM jar — a non-trivial
   classpath surface. A consumer that wants shape geometry only
   shouldn't pay that price.
2. **SVG is its own module.** The cross-repo dep on `tagless-core`
   means publishLocal consumers must have tagless built locally.
   Splitting svg out lets a non-rendering consumer skip the
   coordination cost entirely.
3. **`core` is dep-free.** A clean entry point: ~6 files, pure ADTs
   and builders, no platform escape.

## Build wiring

- Mill 1.1.2, JDK 21, Scala 3.8.3, Scala.js 1.20.1
- `object V` declares all versions inline; `V.tagless` carries the
  cross-repo coordinate (`"0.1.0-SNAPSHOT"`)
- Shared trait `ShapesCommon extends CrossScalaModule with ShapesPublish`
  mirrors the tagless / toolbox pattern (`sharedSrc` via `os.up`)
- `HasSrcJvm` trait added for `heatmap` (Java2D `src-jvm/`)
- The `svg` JVM and JS modules both pull `tagless-core` via:
  ```scala
  override def mvnDeps = super.mvnDeps() ++ Seq(
    mvn"${V.organization}::tagless-core::${V.tagless}"
  )
  ```
  (Mill resolves the `_sjs1_3` artifact automatically inside a
  `ScalaJSModule`.)
- `mill __.compile` ✓ across 3 modules × 2 platforms
- `mill __.fastLinkJS` ✓
- `mill __.publishLocal` ✓ (6 artifacts → `~/.ivy2/local`)

## Cross-cutting type choices

- **Immutable shape algebra.** `enum Shape` with leaf cases for each
  primitive plus a `Style` decorator wrapper. `ShapeScene` is a
  `Vector[Shape]` with optional scene-level style. All builders
  return new values; no mutable state.
- **`derives CanEqual` throughout.** Strict equality is on for the
  whole build; pattern matching on shape leaves requires the
  derivation.
- **Heatmap as projection.** `Heatmap.toScene: ShapeScene` is a
  total function. The Java2D renderer (`HeatmapImage.toPng`)
  ignores the scene projection and rasterizes the heatmap
  directly — a parallel renderer to the SVG path.
- **Interpreter pattern.** `SvgShapeInterpreter.toSvg(scene): Node`
  is a pure fold; same shape as the toolbox `ToScript` /
  `ProcessRunner` interpreters, same shape as the tagless
  `Html.toHtml` renderer.

## Compliance scan against current normative pages

| Norm | Stance |
|------|--------|
| `tech/patterns/functional-domain-design` | **adopts** — `enum Shape`, `final case class Heatmap`, immutable builders, total `toScene` / `toSvg` / `toPng` interpreters, no mutable state. Third worked example after sourceline-manager, toolbox, tagless. |
| `tech/decisions/deps-single-file` | **deviates while standalone** — `object V` inline. Same trajectory expected as tagless / toolbox-pre-DM. Fourth consecutive breakout to deviate; the carve-out hypothesis from [[meta/log]] is now stronger evidence-supported. |
| `tech/guides/mill-cross-platform` | **adopts** — `sharedSrc` task pattern, kebab-only module names, JVM + JS Cross variants, src-jvm for Java2D divergence. |

## Observations worth flagging

1. **Fourth consecutive breakout to deviate from
   [[tech/decisions/deps-single-file]].** After sourceline-manager,
   toolbox (pre-DM), tagless, and now shapesdsl. The pattern is
   stable enough that a carve-out in the decision itself
   ("granular standalone breakouts may inline versions until
   monorepo embedding") is worth drafting.
2. **Cross-repo publishLocal coordination.** Building `shapesdsl-svg`
   requires `tagless-core` to be in `~/.ivy2/local` first. Without
   automation this creates an ordering dependency at build time.
   Worth recording as a project-log entry; the breakout sequencing
   (tagless → shapesdsl → animdsl → presenter) implicitly handles it.
3. **`package shapesdsl.heatmap` Scala.js conflict.** During the
   split I first tried to put the new `heatmap` factory in a sub-
   package `shapesdsl.heatmap`. The JS compilation rejected it
   ("Trying to define package with same name as class heatmap").
   Fell back to a top-level `object Heatmaps` in `package shapesdsl`.
   Root cause is unclear (Heatmap vs heatmap case-sensitivity
   should not collide); worth investigating if a similar split
   recurs elsewhere.
4. **No JS-specific source divergences.** Unlike `tagless` and
   `toolbox`, no module in shapesdsl needs `src-js/`. The Java2D
   surface is the only platform divergence; everything else is
   portable.

## Reachability

This page is reachable from:

- [[index]] §Projects (added in this ingest)
- [[projects/shapesdsl]] §Code Location
- [[sources/tmp/shapesdsl]] (bridge)
- [[meta/log]] (ingest entry on 2026-05-29)

## Related Pages

- [[tech/guides/breakout]] — the procedure this breakout follows
- [[tech/guides/mill-cross-platform]] — the build pattern used
- [[tech/decisions/deps-single-file]] — the decision this breakout deviates from
- [[tech/patterns/functional-domain-design]] — the pattern this codebase adopts
- [[projects/tagless]] — sibling repo (HTML DSL family; consumed by
  `shapesdsl-svg`)
- [[projects/toolbox]] — sibling fine-grained breakout
- [[projects/sourceline-manager]] — minimum-shape breakout

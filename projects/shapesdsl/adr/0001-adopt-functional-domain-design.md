---
id: shapesdsl-adr-0001
title: Adopt Functional Domain Design (declarative encoding)
kind: normative
status: accepted
project: shapesdsl
created: 2026-05-29
compliance:
  adopts:
    - tech/patterns/functional-domain-design.md
  exceptions: []
  deviations: []
  ignores: []
supersedes: []
---

## Context

[[tech/patterns/functional-domain-design]] is in scope for
`shapesdsl` — every module compiles on JVM and Scala.js, modeling
2D geometry as immutable algebraic data.

Scan of the three-module tree:

| Module | ADT / value type | Evidence of pattern |
|--------|------------------|---------------------|
| `core` | `enum Shape derives CanEqual` (`Box`, `Circle`, `Ellipse`, `Line`, `Path`, `Polygon`, `Group`, `Text`, `Style`) | Closed sum type; constructor parameters carry typed values; `Style(Shape, ShapeStyle)` wraps decoration; no mutable builders |
| `core` | `final case class ShapeStyle(fill, stroke, strokeWidth, opacity, ...)` | Immutable; smart copy via per-field `with*` extensions |
| `core` | `final case class ShapeScene(shapes: Vector[Shape], sceneStyle: Option[ShapeStyle])` | Pure container; total `toSvg` fold in `shapesdsl-svg` |
| `core` | `enum ColorScale` (`WhiteToBlue`, `BlueToRed`, `Viridis`, `Custom(stops)`) | Sum type with constructor-encoded options; pure `apply(t: Double): String` projection |
| `core` | `enum Effect` (`Rotate`, `Translate`, `Scale`, `Opacity`) | Pure transformation values applied via `Shape.styled(effects: Effect*)` |
| `heatmap` | `final case class Heatmap derives CanEqual` | Pure record; `with*` builders return new values; `toScene: ShapeScene` is total |
| `heatmap` (JVM) | `HeatmapImage.toPng(Heatmap): Array[Byte]` | Pure interpreter — Java2D + ImageIO are called inside the function, never escape its body |
| `svg` | `SvgShapeInterpreter.toSvg(scene: ShapeScene): tags.Node` | Pure fold over the scene producing `tagless-core` Node values; pattern-matches every `Shape` constructor totally |

Cross-cutting shape: every domain type is `enum` or `final case class`
with `derives CanEqual`, builder helpers return new values, and every
interpreter (`toScene`, `toSvg`, `toPng`) is a total function whose
side-effects (Java2D rasterization) are contained inside its body.

Third worked example after [[projects/tagless/adr/0001-adopt-functional-domain-design]]
and [[projects/toolbox/adr/0001-adopt-functional-domain-design]]; the
new patterns this case study adds:

- **Parallel interpreters over the same algebra.** `Heatmap.toScene`
  projects to the shared `ShapeScene` algebra; `HeatmapImage.toPng`
  rasterizes the heatmap directly. Both are total and pure.
- **Cross-repo interpreter boundary.** `SvgShapeInterpreter` lives
  in this repo but produces values typed in `tagless-core`'s `Node`
  ADT. The pattern flows across artifact boundaries without
  introducing effects.

## Decision

Adopt [[tech/patterns/functional-domain-design]] unconditionally as
the design baseline for every module in `/p/hg/shapesdsl`. Any new
domain type or interpreter in this repository must:

1. be expressed as an `enum` or `final case class`, immutable;
2. expose smart constructors / `with*` builders, not mutable
   setters;
3. derive `CanEqual` for any type that appears in patterns
   (strict equality is on for the whole build);
4. confine any platform-specific machinery (Java2D, file I/O) to
   the body of a single interpreter function — never let it
   escape via abstract types or return values.

## Consequences

- The three-way module split is *enabled* by the pattern. Because
  every module owns a closed algebra, a consumer can pull
  `shapesdsl-core` + `shapesdsl-svg` and get exactly the algebra
  they need — no accidental coupling to `Heatmap` or `Java2D`.
- The `tagless` cross-repo interpreter precedent makes future
  interpreters (`shapesdsl-canvas` for browser canvas,
  `shapesdsl-png` for headless servers, …) easy to add as new
  modules without touching `core`.

## Related

- [[tech/patterns/functional-domain-design]] — global pattern
- [[projects/tagless/adr/0001-adopt-functional-domain-design]] — sibling
- [[projects/toolbox/adr/0001-adopt-functional-domain-design]] — sibling
- [[projects/sourceline-manager/adr/0001-adopt-functional-domain-design]] — minimum precedent
- [[sources/summaries/shapesdsl]]

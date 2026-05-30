---
id: summary-animdsl
title: animdsl (declarative animation DSL with SVG/SMIL + OOXML backends) — code summary
kind: descriptive
status: accepted
scope: global
created: 2026-05-30
updated: 2026-05-30
confidence: high
sources:
  - sources/tmp/animdsl.md
tags: [scala, scala-js, mill, dsl, animation, svg, smil, ooxml, presentationml, library, breakout]
---

## What it is

`animdsl` (artifacts under `no.virtual-architect:animdsl-<module>`,
version `0.1.0-SNAPSHOT`, Apache-2.0) is a three-module Mill build
that decomposes a declarative animation DSL into **a shared
`Timeline` ADT plus two backend interpreters**:

- `animdsl-core` — `Timeline` ADT (`Atom`, `Seq`, `Par`, `Delayed`,
  `Repeated`), animatable property enum (`Prop`), easing functions
  (`Easing`), triggers (`Trigger`), fill semantics (`Fill`),
  keyframes (`KF`), repeat counts (`RepeatCount`), and the
  `AnimBackend[A]` typeclass. No deps.
- `animdsl-svg` — `SvgBackend` folding a `Timeline` to tagless
  `Node` values that represent SMIL `<animate>` / `<animateTransform>` /
  `<animateMotion>` elements. Depends on `animdsl-core` and (cross-
  repo, via `publishLocal`) `tagless-core`.
- `animdsl-ooxml` — `OoxmlBackend` folding a `Timeline` to an OOXML
  `<p:timing>` tree (PresentationML). Threads a `State[Int, _]`
  counter for node IDs via `IdCounter`. **JVM only.** Depends on
  `animdsl-core` and `tagless-core`.

A single user-authored `Timeline` expression compiles to either
SVG/SMIL or OOXML PresentationML with no per-target branching in
the author's code. The design document at
`/p/v42/tagless/animdsl_specification_and_design.md` is the
authoritative spec for the semantic mapping (§5) and module layout
(§6).

A consumer producing only web animations pulls `animdsl-core` +
`animdsl-svg`. A consumer producing only PowerPoint timing
(presentation export) pulls `animdsl-core` + `animdsl-ooxml`. A
consumer doing both pulls all three.

## The three modules

| Module | Platforms | Deps | What it owns |
|--------|-----------|------|--------------|
| `core` | JVM + JS | none | `enum Timeline` (5 cases — `Atom`, `Seq`, `Par`, `Delayed`, `Repeated`); `enum Prop` (X/Y/W/H/Opacity/Rotate/ScaleX/ScaleY/MotionPath/Color/Raw); `enum Easing` (Linear/Step/Spline); `enum Trigger` (WithPrev/AfterPrev/OnClick/OnSlideStart); `enum Fill` (Freeze/Remove); `enum RepeatCount` (Times/Infinite); `final case class KF`; `opaque type ShapeRef`; `AnimBuilder` constructor for `~>`; `AnimBackend[A]` typeclass; `dsl` operators (`~>`, `>>`, `\|\|`, `@`, `*`, `over`, `via`, `on`, `+!`, `~freeze`, `~remove`); `Nel` (NonEmptyList helper) |
| `svg` | JVM + JS | `core`, `tagless-core` | `SvgBackend: AnimBackend[Node]` — folds the `Timeline` tree to SMIL element values; `SmilTiming` resolves cross-element begin-time references (`shapeId.click`, `id.end`); `SvgAnimAttrs` is the type-safe attribute builder for SMIL animation elements |
| `ooxml` (JVM only) | JVM | `core`, `tagless-core` | `OoxmlBackend: AnimBackend[Node]` — folds the `Timeline` to a `<p:timing>` tree; `IdCounter` threads `State[Int, *]` for unique time-node IDs; `PTimingBuilder` assembles the nested `<p:par>` / `<p:seq>` / `<p:cTn>` structure; `OoxmlRender` glues the pieces |

Dependency graph: `core` ← (cross-repo) `tagless-core` ← `svg`,
`ooxml`. The two backends are independent of each other — neither
imports the other.

## Why this layout

The layout follows the design document's §6 verbatim, with one
naming adjustment (kebab/camel encoding for Mill artifact names —
the design doc didn't pre-decide `animdsl-svg` vs `animdsl_svg`).
The fine-grained split rationale also applies:

1. **`core` is dep-free.** A consumer can use the `Timeline` ADT
   programmatically (e.g. to serialize to JSON, generate stub
   timing data, lint a deck) without pulling tagless.
2. **`svg` and `ooxml` are siblings, not a chain.** Adding a future
   third backend (`css` for `@keyframes`, mentioned in the design
   doc §8 as future work) drops in as a new peer module without
   touching the existing two.
3. **`ooxml` is JVM only.** PresentationML is an XML format produced
   for `.pptx` export, which is a server-side concern. No JS
   variant is built.

## Build wiring

- Mill 1.1.2, JDK 21, Scala 3.8.3, Scala.js 1.20.1
- `object V` declares all versions inline; `V.tagless = "0.1.0-SNAPSHOT"`
- Shared trait `AnimCommon extends CrossScalaModule with AnimPublish`
  mirrors tagless / shapesdsl (`sharedSrc` via `os.up`)
- No `HasSrcJvm` or `HasSrcJs` traits needed — no platform
  divergences
- `mill __.compile` ✓ across 5 compile targets (core+svg × 2
  platforms, ooxml × 1 platform)
- `mill __.fastLinkJS` ✓
- `mill __.publishLocal` ✓ (5 artifacts → `~/.ivy2/local`)

## Cross-cutting type choices

- **Single Timeline ADT, two interpreters.** The design doc §5
  records the SMIL ↔ OOXML mapping table. Each row is a pure
  function from a `Timeline` constructor to a backend element. No
  shared mutable state across the two backends.
- **`AnimBackend[A]` typeclass.** Both backends implement
  `AnimBackend[Node]` where `Node` is the tagless ADT. Same shape
  as the toolbox `ProcessRunner[F]` / shapesdsl `SvgShapeInterpreter`
  pattern — interpreter-as-typeclass with the target as the type
  parameter.
- **`Nel` instead of `cats.data.NonEmptyList`.** The design doc §7
  suggests `cats-core`; the implementation rolls a tiny in-tree
  `Nel` to keep core dep-free. Trade-off: ~50 LOC of helpers vs a
  cats-core dep that drags in cats-kernel.
- **`Output: tags.Node` instead of `scala.xml.Elem`.** The design
  doc §7 recommends `scala-xml`; the implementation uses tagless's
  `Node` ADT to share rendering infrastructure with the rest of the
  family. Backends produce `Node` values that an upstream consumer
  serializes via tagless's `Html.toHtml`.

## Compliance scan against current normative pages

| Norm | Stance | Why |
|------|--------|-----|
| `tech/patterns/functional-domain-design` | **adopts** | `enum Timeline` with 5 algebraic cases; `enum Prop`, `Easing`, `Trigger`, `Fill`, `RepeatCount` — every domain type is an ADT; `AnimBackend[A]` typeclass for declarative interpreters; `derives CanEqual` throughout. **Cleanest expression** of the pattern in the breakout family so far (no operator-on-typeclass surface; everything is a sum type or product). |
| `tech/decisions/deps-single-file` | **deviates while standalone** | `object V` inline. Fifth consecutive breakout to deviate (slm/0002, toolbox/0002-superseded, tagless/0002, shapesdsl/0002, animdsl/0002). |
| `tech/guides/mill-cross-platform` | **adopts** | `sharedSrc` task pattern, kebab-only module names. No platform divergences this time. |

## Observations worth flagging

1. **Fifth consecutive breakout deviating from `deps-single-file`.**
   The pattern is now load-bearing in five projects. The
   ADR-vs-carve-out tension surfaced in
   [[projects/tagless/log]] and [[projects/shapesdsl/log]] is
   approaching critical mass. Strong recommendation: extend
   [[tech/decisions/deps-single-file]] with a "fine-grained
   standalone breakout" exception, marking the existing per-project
   deviation ADRs as `superseded` once that lands.
2. **Cross-repo publishLocal works the second time too.** Same
   wiring as shapesdsl: `V.tagless: String = "0.1.0-SNAPSHOT"`,
   `mvn"${V.organization}::tagless-core::${V.tagless}"`. Mill
   resolves `_3` vs `_sjs1_3` from the consuming variant. Worth
   promoting into [[tech/guides/breakout]] §Phase 4.
3. **Cleanest ADT-only codebase yet.** No phantom types, no type-
   state, no extension-method-heavy DSL — `Timeline` + four
   `enum`s + one typeclass. Reads as the canonical "small functional
   domain" example. Worth using as the new minimum-shape exemplar
   alongside sourceline-manager.
4. **Zero structural code changes during the breakout.** No back-
   edges in the source between core / svg / ooxml. Compare with
   tagless (3 moves) and shapesdsl (1 move). The design doc
   structure was followed during initial development; the breakout
   just reified the boundaries as artifacts.
5. **Missing tests for core and ooxml.** Only `SvgAnimAttrsSpec`
   exists upstream. Both modules would benefit from property-based
   round-trip tests (e.g. `Timeline → SmilDoc → parseSmil → Timeline`
   for the svg backend; `Timeline → OoxmlTimingTree → parseOoxml →
   Timeline` for ooxml). Flagged as a follow-up.

## Reachability

This page is reachable from:

- [[index]] §Projects
- [[projects/animdsl]] §Code Location
- [[sources/tmp/animdsl]] (bridge)
- [[meta/log]] (ingest entry on 2026-05-30)

## Related Pages

- [[tech/guides/breakout]] — procedure followed
- [[tech/guides/mill-cross-platform]] — build pattern used
- [[tech/decisions/deps-single-file]] — decision deviated from
- [[tech/patterns/functional-domain-design]] — pattern adopted
- [[projects/tagless]] — sibling repo (animdsl-svg + animdsl-ooxml
  consume `tagless-core`)
- [[projects/shapesdsl]] — sibling fine-grained breakout
- [[projects/toolbox]] — sibling fine-grained breakout

---
id: tagless-adr-0001
title: Adopt Functional Domain Design (declarative encoding)
kind: normative
status: accepted
project: tagless
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

[[tech/patterns/functional-domain-design]] is in scope for `tagless`
— every module compiles on JVM and Scala.js, modeling HTML/SVG
trees as immutable algebraic data. The codebase realises the pattern
in its declarative form across the entire surface.

A scan of the fourteen-module tree:

| Module | ADT / value type | Evidence of pattern |
|--------|------------------|---------------------|
| `htmlid` | `opaque type HtmlId[S <: String] = String` | Singleton-typed value wrapper; no runtime overhead; `IdScope[P]` composes paths via `compiletime.ops.string.+` |
| `core` | `enum Node` (`Element`, `VoidElement`, `Text`) | Pure ADT; `Cursor[D <: Depth, K <: ElementKind]` is a phantom-typed immutable zipper with explicit `List[Context]` stack; rebuilding via `seal` is a total fold |
| `core` | `enum Attr` (`Id`, `Class`, `Href`, `Src`, …, `Data`, `Aria`) | Closed sum type; constructor parameters carry typed values; no string-typed escape hatches in the public surface |
| `core` | `case class Tag[K <: ElementKind](name, kind, attrs)` | Smart constructors `Tag.normal` / `Tag.void`; phantom `K` prevents adding children to `<img>` / `<br>` / `<input>` |
| `core` | `sealed trait Depth { D0 ; Succ[D <: Depth] }` | Peano-encoded depth tracking, used by every cursor operator's signature to make ascent-past-root a compile-time error |
| `core` | `Fragment` (immutable `Vector[Node]`) | Pure builder helpers; combinators (`+`, `*`) lift cardinality into the type |
| `i18n` | `opaque type I18n[K <: String]` | Singleton-typed translation key; `TextScope[K]` nests scopes the same way `IdScope` does; `Lang` is a value type |
| `md` | `enum InlineMarkdown` (`Text`, `Bold`, `Italic`, `Underline`, `Code`, `Math`, `MathBlock`, `Link`, `Image`, `Sequence`, `Bilingual`) | Pure ADT walked by `MarkdownConverter` to produce `Node` values; `Markdown` block DSL operators (`<#`, `<*`, `<\|`, …) construct `Tree` values declaratively |
| `meta` | `case class Meta(...)` with predefined constructors | All accessors are total projections; no platform escape |
| `page` | `case class Page(...)` | Composes immutable `Head` + `Body` parts; rendering is a total `toNode` fold |
| `form` | `Form[S <: FormState] derives CanEqual`; `FormState` phantom hierarchy (`Init`, `Fields`, `InFieldset`, `Done`) | Type-state grammar; every operator (`\|>`, `\|\|`, `\|*`, `\|@`, `\|>>`, `\|<<`, `\|!`) carries the legal predecessor in its signature. `FormInterpreter.toNode` is a total fold |
| `table` | `Table[S <: TableState]`; `TableState` phantom hierarchy (`Init`, `Caption?`, `ColGroup?`, `Head`, `Body`, `Footer?`) | Same type-state pattern; same total-interpreter design |
| `crud` | `CrudView[A]` | Toggle between read view and form-edit form, both pure `Node` constructions; no mutable state in the algebra |
| `route` | `case class Route(...)`; `RouteExtractor` | Pure walk over a rendered tree extracting `data-route` attributes; total `Map[String, String]` result |
| `viz` | `TreeVisualization`, `TreeNode`, `ComponentMeta` | Pure ADT renderers (`AsciiTreeRenderer`, `D3Serializer`, `MermaidRenderer`) — each a total fold over the visualization tree |
| `htmx` | extensions producing `Attr.Custom(...)` values | Type-safe attribute construction; no mutable builder |
| `svg` | extensions producing namespaced `Attr` values | Same shape as `core` attribute surface, adjusted for the SVG namespace |
| `events` | `enum DomEvent` (`Click`, `Change`, `CheckboxChange`, `SelectChange`, `Submit`, `Input`, `KeyDown`, `KeyUp`, `Focus`, `Blur`) | Pure ADT layered over Airstream `EventStream[DomEvent]`; `EventFilter` extensions (`forId`, `forPrefix`, …) are pure stream operators |

The cross-cutting shape: every domain type is an `enum` or
`final case class`; phantom-typed parameters track depth, element
kind, form state, table state, and ID/i18n key paths; every operator
returns a new value (no mutation); rendering is a total fold to
`Node` or `String`; `Either[E, A]` for fallible reads (e.g.
`RouteExtractor`).

This is the same encoding [[projects/sourceline-manager/adr/0001-adopt-functional-domain-design]]
and [[projects/toolbox/adr/0001-adopt-functional-domain-design]]
record. `tagless` is the third worked example, and adds two
patterns the prior two did not exercise:

- **Phantom-typed cursor algebra** — `D <: Depth, K <: ElementKind`
  in every operator's signature.
- **Type-state grammar** — `Form[S <: FormState]` / `Table[S <: TableState]`
  encode legal builder transitions in the type system.

## Decision

Adopt [[tech/patterns/functional-domain-design]] unconditionally as
the design baseline for every module in `/p/hg/tagless`. Any new
domain type or operator in this repository must:

1. be expressed as an `enum` or `final case class`, immutable;
2. expose smart constructors / combinator operators, not mutable
   builders;
3. compile on JVM and Scala.js without effect machinery (`events`
   is the only exception — it consumes Airstream streams, which
   are themselves declarative);
4. derive `CanEqual` where the type is compared (strict equality is
   on for the whole build).

## Consequences

- The fine-grained module split is *enabled* by the pattern.
  Because every module owns a closed algebra with no escape
  hatches, a consumer can pull `tagless-core` + `tagless-form` and
  get exactly the algebra they need — no accidental coupling to
  table, crud, or viz.
- The cursor/zipper encoding sets a precedent for future tree-shaped
  DSLs in sibling repos (`shapesdsl`, `animdsl`, `presenter`). Each
  is expected to ship the same phantom-typed-algebra shape.
- Strict equality is `-language:strictEquality` for the whole build;
  the `derives CanEqual` clauses are load-bearing for pattern
  matching to compile.

## Related

- [[tech/patterns/functional-domain-design]] — global pattern this
  ADR adopts
- [[projects/sourceline-manager/adr/0001-adopt-functional-domain-design]]
  — minimum-shape precedent
- [[projects/toolbox/adr/0001-adopt-functional-domain-design]] —
  multi-module precedent
- [[sources/summaries/tagless]] — distilled view of the codebase

---
id: animdsl-adr-0001
title: Adopt Functional Domain Design (declarative encoding)
kind: normative
status: accepted
project: animdsl
created: 2026-05-30
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
`animdsl`. The codebase realises the pattern's *declarative*
encoding in its purest form across the breakout family: a single
ADT (`Timeline`) plus four orthogonal sum types (`Prop`, `Easing`,
`Trigger`, `Fill`, `RepeatCount`) plus one typeclass
(`AnimBackend[A]`) — no phantom types, no type-state, no extension-
method-heavy DSL. The design document at
`/p/v42/tagless/animdsl_specification_and_design.md` (the spec
source of truth) is structured around the same shape.

Scan of the three-module tree:

| Module | ADT / value type | Evidence of pattern |
|--------|------------------|---------------------|
| `core` | `enum Timeline derives CanEqual` (`Atom`, `Seq`, `Par`, `Delayed`, `Repeated`) | Five cases cover the entire temporal-composition algebra; no escape hatches. Operators `>>`, `\|\|`, `@`, `*` are pure constructors over the ADT. |
| `core` | `enum Prop` (`X`, `Y`, `W`, `H`, `Opacity`, `Rotate`, `ScaleX`, `ScaleY`, `MotionPath`, `Color`, `Raw`) | Closed sum over animatable properties; `Raw` is a typed escape hatch (not an `Any` opening). |
| `core` | `enum Easing` (`Linear`, `Step`, `Spline`) + smart constructors (`EaseIn`, `EaseOut`, `EaseInOut`) | Pure data; pattern-matched by both backends in their `applySpline` helpers. |
| `core` | `enum Trigger` (`WithPrev`, `AfterPrev`, `OnClick`, `OnSlideStart`) | The OOXML "interactive seq wrapper" detour for `OnClick` lives in the backend, not in the ADT — the user writes `t on OnClick(id)` for both targets. |
| `core` | `enum Fill` (`Freeze`, `Remove`); `enum RepeatCount` (`Times`, `Infinite`) | Two-case sums; both pattern-matched totally in each backend. |
| `core` | `final case class KF(t, v, easing)` | Pure record; `derives CanEqual`. |
| `core` | `opaque type ShapeRef` + `AnimBuilder` | Smart constructor pattern: `ShapeRef("logo")` returns a typed reference; `~>` operator on it returns a `Timeline`. |
| `core` | `trait AnimBackend[A] { def render(t: Timeline): A }` | The interpreter typeclass; each backend is a single `given` instance. |
| `svg` | `SvgBackend: AnimBackend[Node]` | Total fold over `Timeline`; produces tagless `Node` values that render to SMIL `<animate>` / `<animateTransform>` / `<animateMotion>`. |
| `svg` | `SmilTiming` | Pure begin-time-expression resolver; pattern-matches `Trigger` totally. |
| `ooxml` | `OoxmlBackend: AnimBackend[Node]` | Total fold producing PresentationML `<p:timing>` tree; threads `State[Int, _]` for node-id allocation via `IdCounter`. |

Cross-cutting shape: every domain type is `enum` or `final case class`
with `derives CanEqual`; every backend is a total interpreter
implementing the same typeclass; effects are confined to the body
of the interpreter (none in this case — both backends are pure).

This case study makes a **specific contribution** to the pattern's
evidence base that prior breakouts did not: **two independent
backends targeting the same ADT**. The SMIL ↔ OOXML mapping (design
doc §5) is the working example of "Free to add new interpreter" —
adding the OOXML backend required *zero* changes to the core
algebra.

Compared to sibling adoptions:

- [[projects/sourceline-manager/adr/0001-adopt-functional-domain-design]]
  — minimum-shape ADT, single domain
- [[projects/toolbox/adr/0001-adopt-functional-domain-design]] —
  multi-module algebra (`Cmd`, `Pipeline`, `ProcessDescription`,
  `VirtualFileSystem`) with multiple interpreters
- [[projects/tagless/adr/0001-adopt-functional-domain-design]] —
  phantom-typed cursor algebra + type-state grammars
- [[projects/shapesdsl/adr/0001-adopt-functional-domain-design]] —
  parallel interpreters over a shared scene algebra (`toScene` /
  `toSvg` / `toPng`)
- **animdsl (this)** — single ADT, two siblings interpreters
  exercising the *expression-problem inverse* (the case where
  adding new interpreters is cheap)

## Decision

Adopt [[tech/patterns/functional-domain-design]] unconditionally as
the design baseline for every module in `/p/hg/animdsl`. Any new
backend or domain refinement must:

1. be expressed as an `enum` or `final case class`, immutable;
2. derive `CanEqual` (strict equality is on for the whole build);
3. implement `AnimBackend[A]` for some new target type `A` if it
   is a backend — never add backend-specific cases to the `Timeline`
   ADT;
4. confine any platform-specific machinery (XML serialization,
   id-counter state) to the body of a single interpreter function.

## Consequences

- Adding a future `css` backend (mentioned in the design doc §8 as
  future work — `@keyframes` + `animation:` shorthand) drops in as
  a new peer module without touching `core`.
- The `tags.Node` output type (vs the design doc's recommended
  `scala-xml`) means animdsl consumers serialize via tagless's
  `Html.toHtml` — a small ergonomic win for the `presenter` repo
  which already pulls tagless.
- The cleanliness comes at a cost: `core` currently has no tests
  (only `svg` does). Property-based tests for `Timeline`
  constructor laws (sequence associativity, identity of
  `Par(t, Atom.empty)`) would round out the pattern adoption.

## Related

- [[tech/patterns/functional-domain-design]] — global pattern
- [[projects/tagless/adr/0001-adopt-functional-domain-design]] — sibling
- [[projects/shapesdsl/adr/0001-adopt-functional-domain-design]] — sibling
- [[projects/toolbox/adr/0001-adopt-functional-domain-design]] — sibling
- [[projects/sourceline-manager/adr/0001-adopt-functional-domain-design]] — minimum precedent
- [[sources/summaries/animdsl]]

---
id: sourceline-manager-adr-0001
title: Adopt Functional Domain Design (declarative encoding)
kind: normative
status: accepted
project: sourceline-manager
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

[[tech/patterns/functional-domain-design]] was promoted to `accepted`
on 2026-05-28 with `scope: global` and `applies_to.languages: [scala,
scala-native, scala-js]`. The `sourceline-manager` library targets all
three platforms, so it is in scope.

Independently of the promotion, the library already realises the
pattern in its declarative form. Two in-tree ADRs encode this:

- `/p/hg/sourceline-manager/docs/adr/0001-adt-source-code-representation.md` — "Source code is data, not strings". Models source code as an ADT (`Token` / `SourceLine` / `SourceFile`) with rendering as an explicit pure function. That is exactly the *immutable model* + *interpreter* split the pattern prescribes.
- `/p/hg/sourceline-manager/docs/adr/0002-functional-domain-design.md` — Codifies the same seven principles the global pattern centres on: immutable model, private primary constructors with public smart constructors, operators encoding algebra, derived `CanEqual`, explicit encoding (no `Product`-introspection), total functions, and *testable monoid laws*.

The library's algebra (`++` / `|+|` / `combine` on both `SourceLine`
and `SourceFile`, plus the inline-merge `joinLines` / `|++|` on
`SourceFile`) is the concrete realisation of the "small, orthogonal
operator set" the pattern requires, and its MUnit suite enforces left
identity, right identity, and associativity as part of the public
contract — the pattern's "algebraic laws are the target" principle
made executable.

## Decision

Adopt `tech/patterns/functional-domain-design.md` unconditionally.
The encoding is **declarative**:

- `Token` is a sealed `enum` with three cases (`Value`, `Indent`,
  `Ref`); the model stores arguments as data.
- `SourceLine` and `SourceFile` are `final case class`es whose
  constructors and operators store their arguments and are walked by
  a separate interpreter (`render`, `renderTokens`, `renderLines`).
- Adding a new interpreter (a Bash renderer, a JSON serializer, a
  rewrite engine for `Ref` resolution, a static analyser) is free —
  the expression-problem trade-off the pattern names is exactly the
  trade-off chosen here.
- Adding a new constructor would mean touching every interpreter, by
  design.

Future constructors / operators must continue to be both
*orthogonal* (not expressible in terms of the existing set) and
*expressive* (necessary for some real downstream generator).

## Consequences

- The library is a reference implementation of the global pattern in
  its declarative form. Other projects looking for a worked example
  should land here first.
- Monoid law tests are mandatory for any new combine operation added
  to `SourceLine` or `SourceFile`.
- Persistence / serialization of source-code values is naturally
  supported: the ADT is plain data. A future `Codec[SourceFile]`
  would add a new interpreter rather than perturb the core.
- Allocation cost is accepted, as ADR-0002 (in-tree) records — this
  is not a hot path. (Contrast: the compositor adopts the same
  pattern with an *allocation deviation*; see
  [[projects/compositor/adr/0001-adopt-functional-domain-design]].)

## Alternatives Considered

- **Executable encoding** — rejected by in-tree ADR-0002: the model
  must support inspection, substitution (`Ref` resolution), and
  alternative renderers without opaque function carriers.
- **Pretty-printer combinators (Wadler-style)** — deferred by in-tree
  ADR-0001; revisit when line-wrapping or budget-aware layout becomes
  a requirement. That would be a separate *interpreter*, still over
  the same ADT.
- **Not declaring and remaining silent** — would be flagged as drift
  per `POLICY.md` (missing declaration).

## Links

- [[tech/patterns/functional-domain-design]]
- [[sources/summaries/sourceline-manager]]
- [[sources/raw/code/sourceline-manager]]
- `/p/hg/sourceline-manager/docs/adr/0001-adt-source-code-representation.md`
- `/p/hg/sourceline-manager/docs/adr/0002-functional-domain-design.md`
- [[sources/summaries/introduction_to_functional_design_john_de_goes]]
- [[sources/summaries/functional_domain_modeling_zio2_debasish_ghosh]]

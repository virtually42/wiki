---
id: compositor-adr-0001
title: Adopt Functional Domain Design as the default pattern
kind: normative
status: accepted
project: compositor
created: 2026-05-28
compliance:
  adopts:
    - tech/patterns/functional-domain-design.md
  exceptions: []
  deviations:
    - page: tech/patterns/functional-domain-design.md
      rationale: |
        The compositor has hard real-time and zero-allocation constraints
        in the input/render hot paths. A pure declarative model whose
        interpreter allocates per event is unacceptable. We adopt the
        pattern but constrain interpreters to allocate only from arena /
        per-frame scratch memory, never from the GC heap.
      severity: low
      mitigated_by: |
        Arena allocator pattern (see
        projects/compositor/designs/input-pipeline.md §"Proposed Approach")
        and interpreter design rules enforced in code review.
  ignores: []
supersedes: []
---

## Context

`tech/patterns/functional-domain-design.md` was promoted to `accepted`
on 2026-05-28 with `scope: global`, declaring Scala / Scala Native /
Scala JS in scope. The compositor is built in Scala Native and is
therefore in scope.

Independently of the promotion, the existing design work for the
input-pipeline already follows the pattern:

> "Each stage is a pure function `(Event, State) => (Event, State)`
> that can be property-tested independently."
> ([[projects/compositor/designs/input-pipeline]] §"Proposed Approach")

The pipeline `coalesce -> resolve_focus -> check_grab -> dispatch` is
the *operators* of an input-event domain whose *model* is `(Event, State)`
and whose constructors are the libinput event ingestors. The plan
([[projects/compositor/plans/input-pipeline]]) calls for property
tests over the pure core — the definition of "multiple interpreters
over a declarative model".

## Decision

Adopt `tech/patterns/functional-domain-design.md` as the default design
pattern for all compositor modules with one explicit deviation around
allocation semantics (see frontmatter).

For each compositor module:

1. Identify the domain (input, surfaces, output configuration,
   protocol state, scene graph, …).
2. Define an immutable model — ADTs and value types.
3. Provide constructors and a small, orthogonal set of operators.
4. Provide interpreters; interpreters allocate only from arena /
   per-frame scratch (see deviation).
5. Test the model and interpreters in isolation on JVM where possible.

Default encoding choice for the compositor: **declarative** for
pipeline domains (input, scene, protocol), **executable** only where
wrapping an opaque wlroots/libinput callback API leaves no clean
declarative shape.

## Consequences

- New compositor modules must justify departures from the pattern in
  follow-up ADRs.
- Property-based tests become the default validation approach for
  pure-core logic. (Skill: `devtools:property-based-testing`.)
- The deviation around allocation is the load-bearing constraint —
  if a future module cannot honor arena-only allocation, that's an
  ADR-level event, not a code review note.

## Alternatives Considered

- **Pure object-oriented compositor design** — rejected; mixes
  description with execution and defeats the testable-pure-core goal.
- **Tagless-final** — deferred; adds typeclass plumbing without
  clear payoff for a single-project compositor with concrete Kyo
  effects.
- **Not adopting and remaining silent** — would be flagged as drift
  per `POLICY.md` (missing declaration).

## Links

- [[tech/patterns/functional-domain-design]]
- [[projects/compositor/designs/input-pipeline]]
- [[projects/compositor/plans/input-pipeline]]
- [[sources/summaries/introduction_to_functional_design_john_de_goes]]

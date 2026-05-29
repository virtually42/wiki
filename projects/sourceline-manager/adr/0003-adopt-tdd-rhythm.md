---
id: sourceline-manager-adr-0003
title: Adopt TDD Rhythm (type-first, red/green/refactor, law-and-example)
kind: normative
status: accepted
project: sourceline-manager
created: 2026-05-29
compliance:
  adopts:
    - tech/patterns/tdd-rhythm.md
  exceptions: []
  deviations: []
  ignores: []
supersedes: []
---

## Context

[[tech/patterns/tdd-rhythm]] was promoted to `accepted` on 2026-05-29
(`confidence: medium`) and raised to `confidence: high` the same day
once `MonoidLawsSuite[A]` landed in this codebase, closing the open
DRIFT-015h sub-flag on PBT-as-peer-to-example-based.

The library is in scope (Scala / Scala.js / Scala Native, any domain).
It is also the codebase whose evidence the pattern cites: the synthesis
[[projects/sourceline-manager/syntheses/monoid-laws-as-pbt-evidence]]
is the page's `promoted_from`.

## Decision

Adopt `tech/patterns/tdd-rhythm.md` unconditionally. All five stages
of the rhythm are realised in this codebase:

- **Stage 0 (type / algebra first)**. In-tree ADR-0001 ("Source code
  is data, not strings") and ADR-0002 ("Functional domain design")
  fix the algebra — `Token` / `SourceLine` / `SourceFile` ADT, seven
  principles including testable monoid laws — *before* any test was
  written. New work in the library extends the algebra first, then
  writes laws and examples against the extension.
- **Stage 1 (test list)**. The two MUnit specs
  (`SourceLineSpec`, `SourceFileSpec`) function as a narrating test
  list: each `test("...")` name reads as a sentence about behaviour
  (Desideratum *readable* + *behavioural*).
- **Stage 2 (red, both forms)**.
  - *Example-based*: `SourceLineSpec` and `SourceFileSpec` carry
    behavioural examples.
  - *Law-based / quantified*: `MonoidLawsSuite[A]` (MUnit-ScalaCheck
    `ScalaCheckSuite` with `forAll`) is consumed by
    `SourceLineMonoidLawsSpec` and `SourceFileMonoidLawsSpec`;
    `SourceLinePrimitivesLawsSpec` carries 46 `forAll` properties
    grouped by primitive family (slicing duality, predicate
    saturation, De Morgan, partition, pattern-match biconditionals,
    closure laws). Examples and laws sit as peers, addressing
    DRIFT-015h.
- **Stage 3 (green)**. Beck's three green-strategies are all visible
  in the codebase's git history (in-tree ADR-0002 records the
  algebra-first → tests → implementation discipline): Obvious
  Implementation for the wrap-`Vector[Token]` primitives; Fake It
  for early constructors; Triangulation for the operator catalogue
  refinement.
- **Stage 4 (refactor on green, symmetry-aware)**. The clean
  symmetric operator catalogue (see ADR-0004) is the *result* of
  refactoring on green over multiple iterations. The library does
  not carry the asymmetric intermediate forms; they were removed in
  passes that kept all tests green.
- **Stage 5 (call the shot)**. Honoured culturally rather than
  mechanically — there is no in-codebase artefact for this stage
  beyond commit messages, which is the form Beck describes.

Cross-platform parity holds: laws and examples pass on JVM (227+),
Scala.js, and Scala Native.

## Consequences

- New algebraic primitives added to `SourceLine` / `SourceFile` /
  `Token` carry both an example test (in the `*Spec` file) and a
  law in `SourceLinePrimitivesLawsSpec` or a new dedicated
  `*LawsSpec` file. The cost of adding a new primitive is bounded
  by "one composition + one or two properties" — see ADR-0005 for
  the economics.
- New monoid instances (a future `Codec[SourceFile]`, a
  `SourceTree` aggregate, etc.) get their three laws by consuming
  `MonoidLawsSuite[A]` and implementing `empty` / `combine` / `gen`
  — three lines plus generators.
- Refactors that break a primitive's contract surface as red in a
  law before they surface as red in any consumer. Refactor-resistance
  is the maintenance contract this adoption purchases.
- Test names continue to narrate behaviour and label algebraic
  invariants (e.g. `"empty is left identity"`, `"take(n) ++ drop(n) == self"`).
  Replacing law-style names with "should" / "must" prose would
  drift from the pattern.

## Alternatives Considered

- **Example-based only** (status quo before MonoidLawsSuite landed) —
  realised Stage 0 / Stage 4 / behavioural Stage 2 but left Stage 2
  quantification unmet. Already deemed insufficient by the
  synthesis; the suite landing closes that gap.
- **Property-based only** — would lose the readable, sentence-shaped
  example tests that double as documentation. Beck's *Test
  Desiderata* (`readable`, `behavioural`) argues against this; the
  library carries both forms as peers.
- **Ignore** — not admissible; the library is in scope and the
  evidence for adoption is direct (it is the page's own
  `promoted_from`).
- **Deviate on a specific stage** — none identified. All five stages
  hold unmodified.

## Links

- [[tech/patterns/tdd-rhythm]]
- [[projects/sourceline-manager/syntheses/monoid-laws-as-pbt-evidence]] — promotion evidence
- [[projects/sourceline-manager/adr/0001-adopt-functional-domain-design]] — Stage 0 carrier
- [[projects/sourceline-manager/adr/0004-adopt-symmetric-refactoring]] — Stage 4 carrier
- [[projects/sourceline-manager/adr/0005-adopt-test-economics]] — Stage 2 cost/benefit framing
- `/p/hg/sourceline-manager/slm/test/src/slm/MonoidLawsSuite.scala`
- `/p/hg/sourceline-manager/slm/test/src/slm/Generators.scala`
- `/p/hg/sourceline-manager/slm/test/src/slm/SourceLineMonoidLawsSpec.scala`
- `/p/hg/sourceline-manager/slm/test/src/slm/SourceFileMonoidLawsSpec.scala`
- `/p/hg/sourceline-manager/slm/test/src/slm/SourceLinePrimitivesLawsSpec.scala`
- `/p/hg/sourceline-manager/docs/adr/0001-adt-source-code-representation.md`
- `/p/hg/sourceline-manager/docs/adr/0002-functional-domain-design.md`

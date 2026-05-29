---
id: test-economics
title: Test Economics — every test, and every skipped test, is a transaction
kind: normative
status: accepted
scope: global
created: 2026-05-29
updated: 2026-05-29
confidence: high
applies_to:
  languages: [scala, scala-native, scala-js]
  domains: [any]
  excludes: [shell-scripts]
used_by:
  - projects/sourceline-manager/adr/0005-adopt-test-economics.md
promoted_from:
  - projects/sourceline-manager/syntheses/monoid-laws-as-pbt-evidence.md
promotion_reason: |
  FP-stack amortisation case realised at two layers in
  `sourceline-manager`: MonoidLawsSuite[A] amortises three monoid
  properties across N=2 instances; SourceLinePrimitivesLawsSpec
  amortises 46 properties across 16 primitives, themselves
  certifying 23 derived StringUtils-equivalent functions in
  StringUtilsCompositionSpec. The original draft's amortisation
  subjunctive ("would, if extracted, pay for itself") is no longer
  subjunctive — it is realised, twice, and the per-derived-function
  cost is now near zero.
sources:
  - sources/summaries/tdd_course_notes_kent_beck_pierodibello.md
tags: [tdd, testing, kent-beck, test-desiderata, property-based-testing, decision-framework]
---

## Problem

Two failure modes around test investment:

- **Over-testing** — every line covered by some assertion, suites
  growing into minutes-long monsters, brittle tests breaking on
  benign refactors, *coverage* mistaken for *confidence*.
- **Under-testing** — "we'll write tests later," skipped tests
  accumulating as silent risk, regressions discovered in production,
  fear of refactoring spreading because nothing protects the
  baseline.

Both come from treating "do we write this test?" as a yes/no virtue
question. It is not. It is an investment decision.

This page was promoted from `draft` to `accepted` on 2026-05-29 on
the strength of
[[projects/sourceline-manager/syntheses/monoid-laws-as-pbt-evidence]]
§"Status Update — 2026-05-29 (post-primitives + StringUtils
composition)", which realises the FP-stack amortisation case at two
layers. Confidence raised to `high` in the same pass. The Di Bello
summary remains the upstream single source
([[sources/summaries/tdd_course_notes_kent_beck_pierodibello]] Theme
10, citing Beck's *Test Desiderata*); the project synthesis
satisfies the second-source requirement via realised evidence.

## Solution

Every test is a **transaction** with costs and benefits over a time
horizon. Every *skipped* test is also a transaction — its cost is a
risk premium paid over the same horizon. Both directions of the
decision deserve the same accounting.

### Cost / benefit of a test that exists

| Side | Items |
|------|-------|
| **Costs** | Time to write. Maintenance over the life of the code (renames, refactors, signature changes break tests). Suite runtime (a 50-test suite at 200 ms each is 10 s; at the end of the cycle that's an attention slice every minute). Brittleness — false reds during refactor. Cognitive load on readers of the suite. |
| **Benefits** | Information about correctness right now. Regression protection on future change. Executable documentation (the test reads as a sentence about behaviour — Desideratum *behavioural* + *readable*). Emotional safety: the bar is there to catch you if you slip. |

### Cost / benefit of a test that is *not* written

| Side | Items |
|------|-------|
| **Costs (risk premium)** | A regression in this region won't be caught locally. Future change in this code is slower because there is less confidence. The reader of the suite cannot tell whether this behaviour was deliberately not exercised or just forgotten. |
| **Benefits (savings)** | All the costs of the existing-test column, not incurred. |

The decision is symmetric. Skipping a test is itself a positive act
with measurable consequences — not the absence of an act.

### Decision rule

Write the test when, over your time horizon:

```
benefit_of_writing > cost_of_writing + risk_premium_avoided
```

Skip it when the inequality flips.

The horizon matters: a one-shot migration script and a foundation
library do not share the same horizon. The library carries decades
of regression risk; the migration carries hours.

### FP-stack amortisation: one law, N implementations

In our stack a single **law-based test** runs against every
implementation of the algebra it constrains. A monoid-law suite
over `Combine[A]` runs against `String`, `List[A]`, `SourceLine`,
`SourceFile`, `Vector[A]`, and every new monoid instance that lands
later — at zero marginal authoring cost per new instance.

```
amortised_cost_per_instance = cost_of_writing / N_instances
```

For widely-implemented typeclasses, *N* is large and growing,
collapsing the per-instance cost toward zero. The cost / benefit
inequality flips harder than for example-based tests because the
denominator on the cost side grows over time.

[[projects/sourceline-manager]] realises this at two layers:

- **Monoid layer.** A shared `MonoidLawsSuite[A]` quantifies three
  properties (left identity, right identity, associativity) under
  `forAll`. Two consumers (`SourceLineMonoidLawsSpec`,
  `SourceFileMonoidLawsSpec`) supply `empty` / `combine` / `gen`
  in three lines each. A third monoid instance anywhere in the
  wiki costs three more lines.
- **Primitive layer.** `SourceLinePrimitivesLawsSpec` quantifies
  46 properties across 16 orthogonal primitives — slicing,
  search, predicates, pattern matching, joining. The same suite
  certifies 23 derived StringUtils-equivalent functions in
  `StringUtilsCompositionSpec` *transitively*: each derived
  function is a one-`def` composition over primitives, and the
  primitive laws are the maintenance guarantee. The per-derived-
  function cost is near zero — the suite was written once.

See [[projects/sourceline-manager/syntheses/monoid-laws-as-pbt-evidence]]
§"Status Update — 2026-05-29 (post-primitives + StringUtils
composition)" for the realisation evidence and the law-by-law
catalogue.

See [[tech/patterns/tdd-rhythm]] §Stage 2 for where laws sit in the
cycle, and `devtools:property-based-testing` for the mechanics.

## Structure

```
                Decision: write this test?
                          |
                          v
        +---------------------------------+
        |     Compute over horizon H:     |
        |  benefit_write =                |
        |     correctness_info_now        |
        |   + regression_protection_H     |
        |   + executable_doc_value        |
        |   + emotional_safety            |
        |                                 |
        |  cost_write =                   |
        |     authoring_time              |
        |   + maintenance_H               |
        |   + runtime_H                   |
        |   + brittleness_H               |
        |                                 |
        |  risk_premium =                 |
        |     P(regression) * impact_H    |
        +---------------------------------+
                          |
              ----------------------
              |                    |
              v                    v
   benefit > cost + premium?      no?
              |                    |
              v                    v
        Write the test       Skip — and record
                              in test list that
                              skip is deliberate
```

## When To Use

- Any decision to add, skip, or delete a test (yes, deletion is a
  test-economics decision too — see below).
- Suite-level investment questions: is the integration suite earning
  its 4-minute runtime? Is the property-based generator coverage
  worth the development time?
- Code reviews where the question is "should this PR have a test
  for X?" Treat the answer as an inequality, not a virtue check.

### Deletion as a test-economics decision

Tests can be deleted when:

- The behaviour they assert has moved elsewhere (delete here, keep
  there).
- The test is structure-sensitive and constantly breaking on
  refactors that don't change behaviour (Desideratum
  *structure-insensitive* violated — the test is fighting the rule,
  delete it and write a behavioural replacement if the behaviour
  still needs covering).
- The test was scaffolding for now-stabilised internal helpers.
  Beck does **not** endorse "private-method scaffolding tests"
  as a daily practice (see [[meta/drift]] §DRIFT-014b for the
  attribution issue), but a *handful* of helper-level tests written
  during construction may genuinely become surplus when the
  top-level behaviour is well covered.

The economics frame stops "should I delete this test?" from being
a courage question — it makes it the same inequality, evaluated in
the opposite direction.

## When Not To Use

- Don't apply this frame to *contract tests at module boundaries*
  — those are load-bearing for cross-module trust and the
  "is this test worth it?" calculation is a category error. They
  are part of the module's public surface, like its type
  signatures.
- Don't apply this to *law-based tests on a published algebra* —
  monoid laws on a public `Combine[A]` instance are part of the
  contract, not an optional verification.
- Don't apply this to *regression tests written for a real bug
  that landed in production*. The risk-premium term in those cases
  is "the bug already cost X, the test prevents recurrence." The
  inequality is rarely close.

## Related Patterns

- [[tech/patterns/tdd-rhythm]] — Stage 1 (test list) is where most
  test-economics decisions get made.
- [[tech/decisions/tidy-first-commits]] — structural commits are
  the cheapest kind of "test the test economics in practice":
  refactoring on green tells you which tests are
  structure-sensitive (i.e. expensive over the maintenance
  horizon).
- [[tech/patterns/functional-domain-design]] — type-level error
  encoding eliminates entire classes of tests by making the bug
  *impossible* rather than *tested for*. The cheapest test is the
  one the type already rules out.

## Skills Cross-Reference

- `devtools:tdd` — local discipline, encodes "fakes over mocks"
  which is itself a test-economics decision (mocks are
  structure-sensitive, fakes are behavioural).
- `devtools:property-based-testing` — the mechanics behind the
  one-law-N-instances amortisation case.

## Open Questions / Drift Signals

- Single-sourced on Di Bello's notes on Beck. Promotion to
  `accepted` was satisfied via project synthesis
  ([[projects/sourceline-manager/syntheses/monoid-laws-as-pbt-evidence]])
  per `POLICY.md` §"second corroborating source *or* internal
  project synthesis". Beck's *Test Desiderata* itself remains the
  natural second textual source and would also reinforce
  [[tech/patterns/tdd-rhythm]] §Test Desiderata.
- ~~The amortisation formula assumes shared law-suites can be
  extracted into a reusable shape. No project currently exposes
  one.~~ **Resolved 2026-05-29** — both `MonoidLawsSuite[A]` and
  `SourceLinePrimitivesLawsSpec` realise the amortisation case
  in `sourceline-manager`. See [[meta/drift]] §DRIFT-015h
  (closed) and the linked synthesis §"Status Update" for the
  realisation evidence.

## Adopters

| Project | ADR | Stance | Notes |
|---------|-----|--------|-------|
| sourceline-manager | [[projects/sourceline-manager/adr/0005-adopt-test-economics]] | Adopts unconditionally | Two-layer realisation of the FP-stack amortisation case: monoid-law suite (3 properties × N instances) + primitive-law suite (46 properties × 16 primitives certifying 23 derived StringUtils-equivalent functions). Citation for confidence raise from `medium` to `high`. |

## Links

- [[sources/summaries/tdd_course_notes_kent_beck_pierodibello]]
- [[tech/patterns/tdd-rhythm]]
- [[tech/decisions/tidy-first-commits]]
- [[tech/patterns/functional-domain-design]]
- [[projects/sourceline-manager]] — two-layer amortisation example
- [[projects/sourceline-manager/syntheses/monoid-laws-as-pbt-evidence]] — citation for the confidence raise

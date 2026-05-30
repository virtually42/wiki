---
id: tdd-rhythm
title: TDD Rhythm — type-first, red/green/refactor, law-and-example
kind: normative
status: accepted
scope: global
created: 2026-05-29
updated: 2026-05-29
confidence: high
applies_to:
  languages: [scala, scala-native, scala-js]
  domains: [any]
  excludes: [shell-scripts, nix-modules]
used_by:
  - projects/sourceline-manager/adr/0003-adopt-tdd-rhythm.md
  - projects/dependency-manager/adr/0003-adopt-tdd-rhythm.md
promoted_from:
  - projects/sourceline-manager/syntheses/monoid-laws-as-pbt-evidence.md
promotion_reason: |
  `sourceline-manager` realises Stages 0 (type / algebra first) and 4
  (refactor on green, symmetry-aware) directly, and Stage 2 in both
  its named-laws form (test names narrate behaviour and label
  algebraic invariants) **and** its quantified / `forAll` form (a
  reusable `MonoidLawsSuite[A]` consumed by
  `SourceLineMonoidLawsSpec` and `SourceFileMonoidLawsSpec`,
  cross-platform JVM / Scala.js / Scala Native — landed 2026-05-29,
  closing DRIFT-015h). The page was accepted 2026-05-29 at
  `confidence: medium` with DRIFT-015h flagged open; confidence
  raised to `high` 2026-05-29 once the suite landed and PBT-as-peer
  became a demonstrated in-repo realisation, not just an argument
  from the draft.
promoted_at: 2026-05-29
sources:
  - sources/summaries/tdd_course_notes_kent_beck_pierodibello.md
  - sources/summaries/tdd_how_to.md
  - projects/sourceline-manager/syntheses/monoid-laws-as-pbt-evidence.md
tags: [tdd, testing, red-green-refactor, test-list, property-based-testing, kent-beck, test-desiderata, type-first, fakes-over-mocks]
---

## Problem

How do we write code that is correct, evolvable, and inspectable as
the requirements change underneath us, **without** doing big-design-
up-front and **without** drifting away from a working baseline?

Two failure modes the rhythm guards against:

- *Speculative design* — committing to abstractions before the code
  needs them, then having to dismantle them when the next requirement
  arrives at a different angle.
- *Stop-the-world refactor cycles* — letting structural debt compound
  until it can only be paid down by a multi-week rewrite that nobody
  can review.

The discipline below is Kent Beck's, with one modification for our
FP-heavy stack: a **type-first** opening move that names the algebra
before any test is written. Beck's *Detroit / Chicago-school* TDD
(state-based, classicist, minimal-mock) is the strict ancestor;
the *London-school* (mock-heavy, outside-in, GOOS) is named here only
to be set out of scope per our `devtools:tdd` skill ("fakes over
mocks").

## Solution

The rhythm has **five** stages, not three. Stage 0 prepends type-level
design before the red/green/refactor cycle.

### Stage 0 — Type / algebra first (FP-stack specific)

Before any test:

1. Name the **domain**. Identify what the module *describes*.
2. Choose the **encoding** (declarative vs executable) per
   [[tech/patterns/functional-domain-design]]. Pick deliberately;
   don't drift between them in one module.
3. Sketch the **immutable model** — ADTs, opaque types, sealed sums.
4. Encode **error cases at the type level**: `Either[E, A]`,
   `Result`, sealed error sums. The decision is in the signature,
   not in the test list. Many runtime error-paths disappear at this
   stage and need no test.

Stage 0 makes the test list shorter and the tests sharper: with the
algebra in hand, the test list captures *what the operators must
satisfy*, not *what the code must defend against*.

### Stage 1 — Test list as a planning artefact

Write a TODO list of tests you want to see green. Treat it as a
living document — add entries as ideas surface. The list is the
agenda, not just a backlog. [[sources/summaries/tdd_how_to]] codifies
this as a `plan.md` file that the developer (or agent) advances one
unmarked bullet at a time.

### Stage 2 — Red (simplest failing test first)

Write the simplest test that fails for the right reason. Test names
narrate behaviour — `shouldSumTwoPositiveNumbers`, not
`testAddMethod`. Make the failure message tell you what is wrong;
unhelpful failure messages are tech debt.

**Two kinds of test** sit at equal rank in this stage:

- **Example-based** — concrete inputs, concrete expected outputs.
  Beck's canon. Best for behaviour at the boundary, for
  documentation-by-example, and when expected outputs are easier to
  state than properties.
- **Property-based / law-based** — universally-quantified
  statements about the algebra. Generators produce inputs;
  invariants are asserted. In our stack, *monoid laws*,
  *functor laws*, *idempotence*, *round-trip*, *associativity*, and
  domain-specific algebraic properties are the lingua franca. One
  law-based test pays for itself across every implementation of the
  algebra. [[projects/sourceline-manager]] tests `SourceLine` and
  `SourceFile` monoid laws this way; the skill
  `devtools:property-based-testing` carries the mechanics.

Choose by what the test is about: an end-user-visible scenario →
example. An algebraic invariant the type promises → law.

### Stage 3 — Green (minimum code to pass)

Beck's *TDD by Example* names three strategies. Use the one that
fits; don't reach for fakes when the obvious shape is right there.

| Strategy | When to use |
|----------|-------------|
| **Obvious Implementation** | The implementation is so clear that not writing it would be a waste of a test cycle. Default for our FP-stack: when the type forces the shape, the implementation is often obvious. |
| **Fake It (till you make it)** | The real implementation is non-obvious. Hard-code a value that turns the test green. Force generalisation by **triangulation** (next strategy) or by writing a second test. |
| **Triangulation** | Drive generalisation by adding a second example that the fake can't satisfy. Two examples are usually enough to force the real shape; three is a smell that the abstraction is wrong. |

Refactoring is **out of bounds** here. Red → green is a behaviour-
preserving move. If you spot a refactoring opportunity, write it on
the test list — it belongs in Stage 4.

### Stage 4 — Refactor (only on green)

On a green bar:

- Run **one** named refactoring at a time (Fowler catalogue: Extract
  Function, Inline Variable, Replace Conditional with Polymorphism…).
- Run the full test suite after each step. Red after a refactor means
  the refactor changed behaviour — revert and try again.
- Prefer refactorings that **remove duplication** or **clarify
  intent**.

Beck's four rules of simple design (paraphrased): passes the tests,
reveals intention, no duplication, fewest elements. Refactor toward
those.

**Symmetry is a refactoring signal**, not just an aesthetic. See
[[tech/patterns/symmetric-refactoring]] — symmetric duplication is
often an algebra waiting to be discovered; destroying the symmetry
by an asymmetric extraction loses the signal.

Commits at this stage are **structural** in the sense of
[[tech/decisions/tidy-first-commits]]. Behavioural commits live at
Stage 3.

### Stage 5 — Call the shot

Before running the suite, *predict* the outcome — which tests pass,
which fail, what the error message will be. The cost is zero; the
information return is high. Being right reinforces the mental model;
being wrong is a learning event. (Theme 8 in
[[sources/summaries/tdd_course_notes_kent_beck_pierodibello]].)

## Structure

```
              [Stage 0]
        Type / algebra first
       (FP-stack-specific)
                 |
                 v
              [Stage 1]
           Test list / plan.md
                 |
                 v
   +-----------------------------+
   |          [Stage 2]          |
   |  Red — simplest failing     |
   |  test first; example *or*   |
   |  law-based, peer rank       |
   +-----------------------------+
                 |
                 v
   +-----------------------------+
   |          [Stage 3]          |
   |  Green — Obvious / Fake It  |
   |  / Triangulation; minimum   |
   |  code, no refactor          |
   +-----------------------------+
                 |
                 v
   +-----------------------------+
   |          [Stage 4]          |
   |  Refactor — one named step  |
   |  at a time, run suite after |
   |  each, symmetry as signal   |
   +-----------------------------+
                 |
                 v
              [Stage 5]
         Call the shot, repeat
                 |
                 v
            (back to Stage 1)
```

## Test Desiderata (Beck)

Beck enumerates the properties a good test should have. They are
referenced throughout the stages above but warrant their own list:

| Desideratum | What it means |
|-------------|---------------|
| Isolated | Tests don't depend on each other's order or shared state |
| Composable | Isolated tests can run in any subset |
| Fast | Feedback in the time it takes to think |
| Inspiring | Reading the test motivates the implementation |
| Writable | The test is cheap to write |
| Readable | The test reads like a sentence about behaviour |
| Behavioural | The test asserts what the code *does*, not how it's structured |
| Structure-insensitive | Refactoring should not break the test |
| Automated | No human in the loop |
| Predictive | Same input → same output |
| Deterministic | Sources of non-determinism explicitly controlled |

In our pure-FP-leaning stack, *isolated / composable / deterministic*
come for free wherever the code under test is referentially
transparent. They reappear as concerns at the IO boundary, where
Kyo's `Scope` (bracket semantics) takes the place of test-discipline
cleanup.

## Code Example

```scala
// Stage 0 — Type / algebra first
// Domain: a small money algebra.
opaque type Money = (BigDecimal, Currency)
enum Currency derives CanEqual:
  case USD, EUR, NOK
enum AddError derives CanEqual:
  case CurrencyMismatch(left: Currency, right: Currency)

object Money:
  def apply(amount: BigDecimal, c: Currency): Money = (amount, c)
  extension (m: Money)
    def amount: BigDecimal = m._1
    def currency: Currency = m._2
    def +(that: Money): Either[AddError, Money] =
      if m.currency == that.currency then Right(Money(m.amount + that.amount, m.currency))
      else Left(AddError.CurrencyMismatch(m.currency, that.currency))

// Stage 1 — Test list (plan.md, abbreviated)
// - [ ] adds two amounts in the same currency
// - [ ] mismatched currencies fail with CurrencyMismatch
// - [ ] addition is associative within one currency  (law)
// - [ ] zero is right identity within one currency   (law)

// Stage 2/3 — Example + Obvious Implementation
test("adds two USD amounts"):
  val r = Money(2, USD) + Money(3, USD)
  assertEquals(r, Right(Money(5, USD)))

// Stage 2 — Law-based test
property("addition is associative within one currency"):
  forAll(genMoneyUSD, genMoneyUSD, genMoneyUSD): (a, b, c) =>
    val left  = (a + b).flatMap(_ + c)
    val right = (b + c).flatMap(a + _)
    assertEquals(left, right)

// Stage 4 — Refactor (only after both tests are green)
// Notice the duplication: + currency check is also needed by -,
// *, etc. The right move is to extract a single sameCurrency
// guard — but only after every operator has at least one example
// test that locks in the behaviour.
```

The error case (`AddError.CurrencyMismatch`) was decided at Stage 0
and exists in the signature. The test list at Stage 1 reflects that
decision; no defensive runtime test for "what if I pass a null
currency" is needed because the type forbids it.

## When To Use

- Any new module or feature where the algebra is not yet stable.
- Refactors that touch behaviour-bearing code (re-establish the
  rhythm with a test list before the first change).
- Bug fixes — write the failing test that reproduces the bug *first*.

## When Not To Use

- One-shot scripts and tooling glue where the cost of a test list
  outweighs the value (apply test economics — see
  [[tech/patterns/test-economics]]).
- Exploration spikes where the goal is to learn the shape of the
  problem; tests presume you know what the right shape is.
- Pure-data migrations or data-shape changes that are easier to
  validate by running the migration than by writing assertions
  about it.

## Related Patterns

- [[tech/patterns/functional-domain-design]] — Stage 0's encoding
  choice lives here; the type-level error decision lives here.
- [[tech/decisions/tidy-first-commits]] — commit-discipline counterpart
  to Stage 4's refactor moves.
- [[tech/patterns/test-economics]] — when to write a test, when to
  skip one, when to delete one.
- [[tech/patterns/symmetric-refactoring]] — symmetry as the
  load-bearing refactoring signal at Stage 4.
- *TDD as if you meant it* (Braithwaite, 2009) — adjacent but
  **distinct**. Braithwaite's expand-inside-the-test-then-extract
  drill is a training exercise, not Beck's daily rhythm. Sometimes
  attributed to Beck (see [[meta/drift]] §DRIFT-014a). Useful as a
  warm-up; do not adopt as standing practice.
- *London-school TDD* (Freeman & Pryce, *Growing Object-Oriented
  Software, Guided by Tests*) — outside-in, mock-heavy. Out of scope
  for this stack per `devtools:tdd` ("fakes over mocks"). Listed for
  awareness, not adoption.

## Skills Cross-Reference

- `devtools:tdd` — local discipline, fakes-over-mocks.
- `devtools:property-based-testing` — Stage 2 law-based testing.
- `scala:functional-patterns` — algebra construction for Stage 0.

## Open Questions / Drift Signals

- **Adoption matrix (post-2026-05-29 fan-out).** In-scope
  projects: `compositor`, `sourceline-manager`, `toolbox`,
  `safetensors-scala`, `dependency-manager`, `tagless`,
  `shapesdsl` (`deploymentbox` excluded — `nix-modules` exclude
  applies). Current state:
  - **Adopts**: `sourceline-manager`
    ([[projects/sourceline-manager/adr/0003-adopt-tdd-rhythm]],
    full PBT realisation); `dependency-manager`
    ([[projects/dependency-manager/adr/0003-adopt-tdd-rhythm]],
    bounded exception on Stage 2 law-based pending symmetric
    operators).
  - **Missing**: compositor, toolbox, safetensors-scala, tagless,
    shapesdsl. Tracked as cells of [[meta/drift]] §DRIFT-024.
- **DRIFT-015h closed 2026-05-29.** `sourceline-manager` now ships
  a reusable `MonoidLawsSuite[A]` (MUnit-ScalaCheck `ScalaCheckSuite`
  + `forAll`) parameterised by generator + `empty` + `combine`;
  `SourceLineMonoidLawsSpec` and `SourceFileMonoidLawsSpec` each
  consume it. The six prior hand-written law tests were deleted.
  Stage 2 law-based-as-peer claim is now realised in a live
  cross-platform project (JVM / Scala.js / Scala Native);
  `confidence` raised from `medium` to `high`.
- The Stage 0 prepend is our deviation from Beck-canonical TDD. If
  the deviation proves load-bearing across multiple project ADRs,
  consider lifting it into a separate `tech/decisions/type-first-tdd`
  page rather than carrying it inside this pattern.
- A *third* TDD source — Beck's *TDD by Example* (book) — would
  close DRIFT-014a / 014c / 014d / 014f in
  [[sources/summaries/tdd_course_notes_kent_beck_pierodibello]] at
  once. `confidence: high` already reached via DRIFT-015h closure;
  the book would broaden the source base rather than raise
  confidence further.

## Links

- [[sources/summaries/tdd_course_notes_kent_beck_pierodibello]]
- [[sources/summaries/tdd_how_to]]
- [[tech/patterns/functional-domain-design]]
- [[tech/decisions/tidy-first-commits]]
- [[tech/patterns/test-economics]]
- [[tech/patterns/symmetric-refactoring]]
- [[projects/sourceline-manager]] — monoid-law tests as live example

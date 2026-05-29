---
id: symmetric-refactoring
title: Symmetric Refactoring — symmetry is the signal an algebra wants to be born
kind: normative
status: accepted
scope: global
created: 2026-05-29
updated: 2026-05-29
confidence: high
applies_to:
  languages: [scala, scala-native, scala-js]
  domains: [any]
  excludes: []
used_by:
  - projects/sourceline-manager/adr/0004-adopt-symmetric-refactoring.md
  - projects/dependency-manager/adr/0004-adopt-symmetric-refactoring.md
promoted_from:
  - projects/sourceline-manager/syntheses/monoid-laws-as-pbt-evidence.md
promotion_reason: |
  `sourceline-manager`'s operator catalogue (`++` / `|+|` / `combine`,
  `:+` / `+:`, `appendLine` / `prependLine`, `appendLines` /
  `prependLines`, `appendToken` / `prependTokenToLast`, `appendAll` /
  `prependAll`) is a direct realisation of the pattern's
  decision-tree moves 1 and 2 — preserve symmetric duplication, name
  the algebra. Synthesis confidence is high; user accepted on
  2026-05-29.
promoted_at: 2026-05-29
sources:
  - sources/summaries/tdd_course_notes_kent_beck_pierodibello.md
  - projects/sourceline-manager/syntheses/monoid-laws-as-pbt-evidence.md
tags: [refactoring, kent-beck, implementation-patterns, symmetry, algebra-discovery, functional-domain-design]
---

## Problem

Two near-parallel methods. Maybe `appendToken` and `prependToken`,
or `validateUser` and `validateOrder`, or `renderJson` and
`renderXml`. The instinct on "remove duplication, ruthlessly" is to
extract — pull the shared bit into a helper, leave the differences
in place.

The instinct is sometimes wrong. The two methods are *almost*
parallel; an asymmetric extraction makes one of them call into the
helper while the other doesn't, or makes the helper carry a flag
to switch behaviours, or moves shared lines without moving the
matching unshared lines around them.

The result: the **symmetry is destroyed**. Whatever pattern was
visible in the duplication — the algebra the code was *almost*
expressing — becomes invisible to the next reader. The refactor
"removed duplication" but lost information.

Originally single-sourced
([[sources/summaries/tdd_course_notes_kent_beck_pierodibello]]
Theme 7, citing Beck's *Implementation Patterns*). Promoted to
`accepted` 2026-05-29 on the strength of a project synthesis
([[projects/sourceline-manager/syntheses/monoid-laws-as-pbt-evidence]])
demonstrating direct realisation in `sourceline-manager`'s operator
catalogue.

## Solution

Read symmetry **before** you read duplication. Symmetry is a
*positive signal* about the underlying algebra; duplication is a
*negative signal* about local code shape. They can point in opposite
directions.

### Three moves the pattern endorses

1. **Preserve symmetric duplication** when the two near-parallel
   shapes are likely to evolve in lockstep. Duplication that drifts
   apart is a problem; duplication that stays in step is honest.

2. **Refactor toward an algebra** when the symmetry is strong
   enough to give the operations a shared algebraic name (monoid,
   functor, fold, lens…). The extraction is then not "pull the
   shared bit out" but "name the algebra and have both methods
   instantiate it."

3. **Reject asymmetric extraction** when the only available
   extraction breaks the parallel shape. The cost — losing the
   algebra signal — is rarely worth the line-count saving.

### The decision tree

```
Two near-parallel methods. Should I refactor?
                |
                v
   Are they truly parallel  --- No --->  Don't refactor.
   (same shape, different                Duplication is coincidental,
    arguments)?                          not symmetry.
                |
                v
   Yes.
                |
                v
   Do they share an algebra  --- Yes --->  Name the algebra,
   (monoid, functor, fold,                 have both instantiate.
    fmap, traversal, …)?                   Symmetry preserved
                |                          and named.
                v
   No (or not obviously).
                |
                v
   Would extracting a helper  --- Yes --->  Preserve the duplication.
   destroy the visual                       The symmetry IS the
   parallel?                                value.
                |
                v
   No, the helper preserves
   the parallel.
                |
                v
   Extract the helper.
   Both methods now read as
   "the algebra step, plus
   their distinguishing bit."
```

### Why this works under TDD

In [[tech/patterns/tdd-rhythm]], Stage 4 (refactor on green) is
where extraction decisions get made. Symmetry is visible to a TDD
practitioner because *the same kind of test exists for both
methods* — and the tests themselves are symmetric. If
`shouldAppendTokenToLastLine` and `shouldPrependTokenToFirstLine`
both pass and read in mirror, you have evidence that the methods
should also read in mirror. An asymmetric extraction usually breaks
*test* symmetry before it breaks *code* symmetry — which is the
practical detection signal.

## Structure

```
   Two near-parallel    +----------------+
   methods or shapes    |  Symmetry?     |
                        |                |
                        |  - shape       |
                        |  - argument    |
                        |    count       |
                        |  - flow        |
                        +----------------+
                                |
                  ---------------------------
                  |                         |
                  v                         v
            Asymmetric                 Symmetric
            (coincidental                  |
             overlap)                      v
                  |                  +----------------+
                  |                  | Algebra        |
                  v                  | nameable?      |
            Leave alone              +----------------+
                                            |
                              ---------------------------
                              |                         |
                              v                         v
                       Yes (monoid /            No (or premature)
                        functor / fold / …)             |
                              |                         v
                              v                  Preserve
                       Name the algebra,         duplication;
                       both methods              extract only if
                       instantiate.              the helper keeps
                       Symmetry both             parallel reading
                       visible AND named.        order intact.
```

## Code Example

### The bad asymmetric extraction (rejected)

```scala
// Before
def appendToken(t: Token): SourceFile =
  lines.lastOption match
    case Some(last) => copy(lines.init :+ (last :+ t))
    case None       => copy(Vector(SourceLine(t)))

def prependTokenToLast(t: Token): SourceFile =
  lines.lastOption match
    case Some(last) => copy(lines.init :+ (t +: last))
    case None       => copy(Vector(SourceLine(t)))

// Tempting bad refactor — extract the "either modify last line or
// seed a new file" shape into a helper that takes a flag:
private def modifyLastOrSeed(t: Token, prepend: Boolean): SourceFile =
  lines.lastOption match
    case Some(last) => copy(lines.init :+ (if prepend then t +: last else last :+ t))
    case None       => copy(Vector(SourceLine(t)))

def appendToken(t: Token) = modifyLastOrSeed(t, prepend = false)
def prependTokenToLast(t: Token) = modifyLastOrSeed(t, prepend = true)
```

The flag parameter (`prepend: Boolean`) is the smell. The two
methods used to read in mirror; now they read as two calls into a
flag-toggled helper. The reader has to *decode the flag* to recover
what was visible at a glance before.

### The symmetric preservation (endorsed)

Keep the two methods as-is. They are short, they read in mirror,
they evolve in lockstep because they target the same data shape.
The duplication is honest about the symmetry.

This is exactly the choice
[[projects/sourceline-manager]] makes in
`SourceFile.appendToken` / `SourceFile.prependTokenToLast`. The
in-tree ADR-0002 (functional domain design) puts symmetric naming
in its operator catalogue:
`++` / `|+|` / `combine` for the canonical combine,
`:+` / `+:` for the append / prepend pair,
`appendLine` / `prependLine` (and the *all* variants). The pairs
read in mirror because the algebra is symmetric.

### The algebra-naming refactor (endorsed when the algebra is real)

```scala
// When you have many near-parallel pairs and the shared shape IS a
// monoid, name the algebra:
given Monoid[SourceFile] with
  def empty: SourceFile = SourceFile.empty
  def combine(a: SourceFile, b: SourceFile): SourceFile = a ++ b

// Now every "two methods doing combine-shaped things" pair is
// expressed by reaching for the monoid, not by extracting a flag-
// toggled helper. The symmetry is preserved AND named.
```

## When To Use

- You're about to extract a helper from two near-parallel methods.
- A code review surfaces "this is duplicated, can we DRY it up?"
- You're refactoring on green (TDD Stage 4) and the suite's
  test names read in mirror across two operations.
- You're surveying a module for algebra-discovery candidates —
  paired operations that turn out to be a monoid / functor / lens /
  fold are first-class evidence.

## When Not To Use

- The duplication is *coincidental* — two methods happen to share
  three lines that mean different things in their respective
  contexts. No symmetry; extract freely if it clarifies the
  intent.
- The shared algebra is *premature* — you have one pair today and
  no third instance on the horizon. Don't promote a flag-bearing
  helper to a typeclass on the strength of one pair; wait for the
  second pair to either confirm the algebra or kill the hypothesis.
- A genuine performance constraint *demands* the asymmetric
  extraction (e.g. one path is in a hot inner loop and the helper
  enables a critical specialisation). Trade-off explicitly; record
  the trade-off.

## Related Patterns

- [[tech/patterns/functional-domain-design]] — naming the shared
  algebra (move 2 in the decision tree) instantiates this pattern.
  Monoid laws, functor laws, fold-based combinators are the
  end-state symmetric refactoring is reaching for.
- [[tech/patterns/tdd-rhythm]] §Stage 4 — symmetry is the signal
  the refactor stage is supposed to read. Symmetric test names
  are the practical detection mechanism.
- [[tech/patterns/test-economics]] — the cost of losing the
  symmetry signal is real but invisible; symmetric refactoring is
  partly an economics decision (preserve information vs. save
  lines).

## Open Questions / Drift Signals

- **In-scope projects must now declare stance.** Promotion to
  `accepted` 2026-05-29 means `compositor` and `sourceline-manager`
  are in scope and must adopt, except, deviate, or ignore in an
  ADR. `sourceline-manager`'s synthesis evidence is already strong;
  an `adopts` ADR is a short follow-up.
- The "name the algebra" move (decision-tree branch 2) overlaps
  with [[tech/patterns/functional-domain-design]]. If the algebra
  pre-exists (the project has already decided "we use monoids
  here"), this pattern collapses into "find the monoid instance."
  If it doesn't, this pattern is *upstream* of the decision to
  introduce an algebra at all. Worth disentangling in a follow-up.
- The page's claims about pairs in `sourceline-manager` are
  current as of 2026-05-29; future refactors that break the
  symmetry without an ADR would be drift visible against this page.

## Links

- [[sources/summaries/tdd_course_notes_kent_beck_pierodibello]]
- [[tech/patterns/functional-domain-design]]
- [[tech/patterns/tdd-rhythm]]
- [[tech/patterns/test-economics]]
- [[projects/sourceline-manager]] — the live example of symmetric pairs preserved by design

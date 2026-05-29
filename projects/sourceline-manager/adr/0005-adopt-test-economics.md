---
id: sourceline-manager-adr-0005
title: Adopt Test Economics (every test, and every skipped test, is a transaction)
kind: normative
status: accepted
project: sourceline-manager
created: 2026-05-29
compliance:
  adopts:
    - tech/patterns/test-economics.md
  exceptions: []
  deviations: []
  ignores: []
supersedes: []
---

## Context

[[tech/patterns/test-economics]] was promoted from `draft` to
`accepted` (`confidence: high`) on 2026-05-29 on the strength of this
codebase's two-layer amortisation realisation. The synthesis
[[projects/sourceline-manager/syntheses/monoid-laws-as-pbt-evidence]]
is the page's `promoted_from`; the §"Status Update — 2026-05-29
(post-primitives + StringUtils composition)" subsection records the
realisation evidence.

The library is in scope (Scala / Scala.js / Scala Native, any
domain). It is the codebase that lifted the pattern's FP-stack
amortisation claim from a draft-time subjunctive ("would, if
extracted, pay for itself") to a demonstrated realisation at two
layers.

## Decision

Adopt `tech/patterns/test-economics.md` unconditionally. Test
investment in this codebase is governed by the pattern's
cost/benefit framing, and the amortisation case is structurally
load-bearing — neither aspirational nor optional.

### Per-test framing (realised at the named-example layer)

The monoid-law tests (left identity, right identity, associativity
on both `SourceLine` and `SourceFile`) are intentionally minimal:
each is three lines, asserts what the operator *does* without
encoding *how* it is implemented (Desideratum *structure-insensitive*),
and reads as a sentence (Desideratum *readable*). They survive
refactor without churn. Skipping them would leave the public
contract claim ("algebraic invariants are part of the public
contract", in-tree ADR-0002) unverifiable — the risk premium of
*not* writing them is measurable.

### FP-stack amortisation (realised at two layers)

| Layer | Suite | Authoring cost | Amortisation |
|-------|-------|----------------|--------------|
| Monoid | `MonoidLawsSuite[A]` (3 `forAll` properties) | One trait + generators | 3 properties × N instances; N = 2 today (`SourceLine`, `SourceFile`); next instance adds 1 spec file with 3 trivial member implementations |
| Primitives | `SourceLinePrimitivesLawsSpec` (46 `forAll` properties across 16 primitives) | One spec file | 46 properties certify the algebraic contract of every existing primitive; new StringUtils-equivalent functions in `StringUtilsCompositionSpec` (23 derived today) inherit the contract by composition with no per-function authoring |

The cost-per-derived-function of `StringUtils`-equivalent surface
area is now near zero: each new entry in `StringUtilsCompositionSpec`
is one `def` composing primitives the laws already cover. The
pattern's "one law, N implementations" decision rule operates here
on two axes (N monoid instances, N derived primitives).

### Cross-platform parity multiplies the payoff

The same suites run on JVM (227+), Scala.js, and Scala Native.
Without the amortisation case, this would mean 3 × the
hand-written tests. With it, the platform multiplication is free.

## Consequences

- New monoid instances cost three trivial members (`empty`, `combine`,
  `gen`) plus a one-line `class ... extends MonoidLawsSuite[A]`. The
  decision rule "write the law-based test" is effectively automatic
  for any new combine operation; the cost is below the threshold of
  deliberation.
- New `SourceLine` / `SourceFile` primitives must either fit an
  existing law family in `SourceLinePrimitivesLawsSpec` or extend
  the spec with the new family's properties. A primitive that
  resists property statement is a signal to question its
  orthogonality (see [[projects/sourceline-manager/adr/0001-adopt-functional-domain-design]]
  §Decision).
- New StringUtils-equivalent derivations land as one `def` in
  `StringUtilsCompositionSpec`; their algebraic contract is
  inherited from the primitive layer. The cost/benefit calculation
  for each new derived function is dominated by the benefit side
  (one more demonstration that the primitive set is sufficient).
- Suite runtime stays under the threshold where it would itself
  become an attention slice. If `forAll` ScalaCheck shrinking ever
  pushes per-property runtime past a few hundred milliseconds, the
  pattern's cost column re-engages: prune generator complexity, not
  properties.
- Test deletion is a deliberate transaction. The six hand-written
  monoid-law tests deleted on 2026-05-29 (replaced by
  `MonoidLawsSuite[A]` consumers) are the only deletion event in
  the test corpus to date; the rationale ("the laws are subsumed by
  the new suite") is recorded in `meta/log.md`.

## Alternatives Considered

- **Skip law-based tests, keep only example-based** — rejected; the
  per-test cost-of-skip (unverified public contract) outweighs the
  cost-of-write (three lines per law) at any horizon longer than a
  few weeks. The library's horizon is years.
- **One canonical suite per platform, hand-written** — rejected;
  3 platforms × 2 instances × 3 laws = 18 hand-written tests today;
  the existing 2 × 3 = 6 already exposed the duplication, and the
  cross-platform multiplier compounds it. Amortisation purchases
  back-of-envelope ~6× authoring cost reduction at today's N, with
  the multiplier growing as N grows.
- **Ignore the pattern, decide per-test ad hoc** — rejected; the
  pattern is realised; ignoring would oblige re-deriving the same
  conclusions on every PR.
- **Deviate** — none identified. The pattern holds unmodified; the
  realisation is the strongest in the wiki today.

## Links

- [[tech/patterns/test-economics]]
- [[projects/sourceline-manager/syntheses/monoid-laws-as-pbt-evidence]] — promotion evidence
- [[projects/sourceline-manager/adr/0001-adopt-functional-domain-design]] — algebra-naming carrier
- [[projects/sourceline-manager/adr/0003-adopt-tdd-rhythm]] — Stage 2 cost/benefit lives here
- [[projects/sourceline-manager/adr/0004-adopt-symmetric-refactoring]] — symmetric pairs underwrite the per-pair authoring cost
- `/p/hg/sourceline-manager/slm/test/src/slm/MonoidLawsSuite.scala`
- `/p/hg/sourceline-manager/slm/test/src/slm/SourceLinePrimitivesLawsSpec.scala`
- `/p/hg/sourceline-manager/slm/test/src/slm/StringUtilsCompositionSpec.scala`

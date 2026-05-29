---
id: slm-synthesis-monoid-laws-as-pbt-evidence
title: Monoid-law tests in sourceline-manager — algebra-naming evidence, partial PBT evidence
kind: descriptive
status: accepted
scope: project:sourceline-manager
confidence: high
created: 2026-05-29
updated: 2026-05-29
last_status_update: 2026-05-29
sources:
  - /p/hg/sourceline-manager/slm/src/slm/SourceLine.scala
  - /p/hg/sourceline-manager/slm/src/slm/SourceFile.scala
  - /p/hg/sourceline-manager/slm/test/src/slm/SourceLineSpec.scala
  - /p/hg/sourceline-manager/slm/test/src/slm/SourceFileSpec.scala
  - /p/hg/sourceline-manager/docs/adr/0002-functional-domain-design.md
  - sources/raw/code/sourceline-manager.md
  - tech/patterns/functional-domain-design.md
  - tech/patterns/tdd-rhythm.md
  - tech/patterns/test-economics.md
  - tech/patterns/symmetric-refactoring.md
  - meta/drift.md
tags: [monoid, laws, property-based-testing, test-economics, tdd-rhythm, symmetric-refactoring, functional-domain-design, algebra-naming, partial-evidence]
---

## Observation

`sourceline-manager`'s test suite **names** the monoid laws for both
`SourceLine` and `SourceFile`, but **asserts them as single concrete
examples**, not as `forAll`-style properties over generated inputs.

The code goes one decisive step toward "algebra as testable
contract" (the laws are labelled by name, not buried inside
behavioural tests) and stops one decisive step short of the FP-stack
endgame (the laws are not actually quantified — a single triple
`(a, b, c)` is the entire input space the associativity test
explores).

This partial state is **rich evidence** for some of the new draft
patterns and **weak evidence** for others. The synthesis below
maps each draft to what it can and cannot claim from this codebase
today.

## Evidence

### The named-law tests, verbatim

`/p/hg/sourceline-manager/slm/test/src/slm/SourceLineSpec.scala`:

```scala
test("empty is left identity"):
  val line = SourceLine.fromWords("a", "b")
  assertEquals(SourceLine.empty ++ line, line)

test("empty is right identity"):
  val line = SourceLine.fromWords("a", "b")
  assertEquals(line ++ SourceLine.empty, line)

test("++ is associative"):
  val a = SourceLine.value("a")
  val b = SourceLine.value("b")
  val c = SourceLine.value("c")
  assertEquals((a ++ b) ++ c, a ++ (b ++ c))
```

`/p/hg/sourceline-manager/slm/test/src/slm/SourceFileSpec.scala`
mirrors the structure on lines 506–518:

```scala
test("empty is left identity"):
  val file = SourceFile.fromStrings("a", "b")
  assertEquals(SourceFile.empty ++ file, file)

test("empty is right identity"):
  val file = SourceFile.fromStrings("a", "b")
  assertEquals(file ++ SourceFile.empty, file)

test("++ is associative"):
  val a = SourceFile.fromStrings("a")
  val b = SourceFile.fromStrings("b")
  val c = SourceFile.fromStrings("c")
  assertEquals((a ++ b) ++ c, a ++ (b ++ c))
```

### What is *not* in the test suite

- No `forAll` calls.
- No scalacheck / MUnit-ScalaCheck / Hedgehog dependency in
  `build.mill` (only `munit`).
- No generators for `SourceLine` or `SourceFile`.
- No reusable `MonoidLawsSuite[A]` trait factored out for reuse by
  future monoid instances.

### The aliases the laws cover (and don't cover)

The combine operators come in three aliases — `++`, `|+|`, and
`combine` — and the suite asserts they are aliases:

```scala
test("|+| is alias for ++"):
  ...
  assertEquals(line1 |+| line2, line1 ++ line2)

test("combine is alias for ++"):
  ...
  assertEquals(line1.combine(line2), line1 ++ line2)
```

The three laws are stated only against `++`. By the aliasing-test
they hold transitively for `|+|` and `combine` too — but this is a
proof-by-substitution, not an asserted law on each operator
directly. Mechanically defensible; a property-based suite would
state the laws against the canonical operator and let the aliasing
test do the bridging.

### The associated documentation

`/p/hg/sourceline-manager/docs/adr/0002-functional-domain-design.md`
explicitly commits to this shape:

> "**Monoid laws are testable.** The test suite includes left
> identity, right identity, and associativity properties for `++`
> on both `SourceLine` and `SourceFile`. Algebraic invariants are
> part of the public contract."

The ADR calls them "properties." The implementation calls them
"properties" by intent but realises them as examples. The naming
gap is small but real, and worth recording rather than papering
over.

## Analysis — which drafts this codebase corroborates

### [[tech/patterns/functional-domain-design]] (already `accepted`)

**Strong evidence; already an adopter.** This synthesis adds no new
evidence the existing
[[projects/sourceline-manager/adr/0001-adopt-functional-domain-design]]
ADR doesn't already carry. Recorded here for completeness.

### [[tech/patterns/symmetric-refactoring]] (currently `draft`)

**Strong evidence.** The codebase makes decision-tree move 2 of the
draft (*name the algebra*) extensively:

| Symmetric pair | Algebra name |
|----------------|--------------|
| `++` / `|+|` / `combine` | Monoid combine |
| `:+` / `+:` | Postfix / prefix (algebra of insertion at the two ends) |
| `appendLine` / `prependLine`; `appendLines` / `prependLines` | Same algebra lifted to lines |
| `appendToken` / `prependTokenToLast` | Same algebra at the token level |
| `appendAll` / `prependAll` | Same algebra lifted to vectors |

Every pair preserves the visual parallel; none is refactored away
into a flag-bearing helper. The codebase is *exactly* the
"preserve symmetric duplication, name the algebra" endgame the draft
prescribes. The pairs read in mirror in `SourceFile.scala` and the
tests for them read in mirror in `SourceFileSpec.scala`.

**Recommendation**: this codebase is sufficient evidence to promote
[[tech/patterns/symmetric-refactoring]] from `draft` to `accepted`
with `confidence: high`. The `promoted_from` field on the page
should cite this synthesis.

### [[tech/patterns/tdd-rhythm]] (currently `draft`)

**Partial evidence — corroborates Stage 0 and the *naming* half of
Stage 2; does not corroborate the *quantification* half of Stage 2.**

What the codebase corroborates:

- **Stage 0 (type / algebra first).** ADR-0001 (in-tree) says
  "Source code is data, not strings" — the algebra was named before
  any test was written. ADR-0002 (in-tree) records the encoding
  choice (declarative) and the operator catalogue at the type
  level. The codebase is a textbook Stage-0 result.
- **Stage 2 naming as behavioural narration.** Test names read as
  sentences about behaviour — "empty is left identity", "++ is
  associative" — exactly the rhythm draft's Desideratum *readable*
  + *behavioural*. The test list narrates the algebra.
- **Stage 4 (refactor on green).** The operator catalogue's
  symmetry is the *result* of refactoring on green over multiple
  iterations of the library; the pairs would not be this clean
  otherwise.

What the codebase **does not** corroborate:

- **Stage 2 law-based-as-peer-to-example-based.** The codebase
  treats laws as *named examples*, not as quantified properties.
  This is the gap that prevents this codebase from being the
  satisfying second-source-via-project-synthesis for DRIFT-015h
  (PBT as peer).

**Recommendation**: this synthesis is *sufficient* to promote
[[tech/patterns/tdd-rhythm]] from `draft` to `accepted` on the
strength of the Stage 0 / Stage 4 / behaviour-named-Stage-2
evidence, but the promotion notes must be honest about
DRIFT-015h remaining open — the PBT-as-peer claim still rests
only on the draft's own argument from the type system, not on a
demonstrated in-repo realisation. A property-based realisation in
*any* project would close DRIFT-015h properly.

### [[tech/patterns/test-economics]] (currently `draft`)

**Partial evidence — corroborates the cost-of-named-example case;
does not yet corroborate the FP-stack amortisation case.**

What the codebase corroborates:

- **Named example tests are cheap to write and cheap to read.**
  The three-line laws (`empty ++ x == x` etc.) are minimal,
  documentation-shaped, and survive refactor without churn.
  Desideratum *structure-insensitive* holds: the test asserts what
  the operator *does*, not how it's implemented.
- **The cost of *not* writing them would be measurable.** The
  library's whole public-contract claim ("algebraic invariants are
  part of the public contract") would be unverifiable without
  these tests.

What the codebase **does not** corroborate:

- **One law, N implementations amortisation.** The current laws
  are stated separately for `SourceLine` and `SourceFile`; nothing
  is factored into a reusable `MonoidLawsSuite[A]`. The draft's
  cost-divided-by-N argument is sound but not realised — the
  codebase has N = 2 instances and 2 × 3 = 6 hand-written law
  tests, which is the limit case of the amortisation, not its
  payoff.

**Recommendation**: this synthesis can corroborate
[[tech/patterns/test-economics]] *only* on the per-test
cost/benefit framing, not on the amortisation case. Promotion to
`accepted` is admissible with `confidence: medium`. The
amortisation case stays as an open question that a future
`MonoidLawsSuite[A]` extraction would close.

### [[tech/decisions/tidy-first-commits]] (currently `draft`)

**No evidence in this codebase.** The library's commit history is
in `/p/hg/sourceline-manager/.git/`; it is not analysed here. This
synthesis is silent on Tidy First. If the human wants to
corroborate that draft, a separate synthesis over the actual
commit history is needed — or a deliberate adoption ADR on
`sourceline-manager` from this point forward.

## Recommendations

### Immediate (no code change required)

1. **Promote [[tech/patterns/symmetric-refactoring]] from `draft`
   to `accepted`.** This synthesis is sufficient evidence.
   Confidence: high.

2. **Promote [[tech/patterns/tdd-rhythm]] from `draft` to
   `accepted`** with a note that DRIFT-015h (PBT as peer) remains
   open — the Stage 0 / Stage 4 evidence is strong, the Stage 2
   law-based-quantified evidence is partial. Confidence: medium.

3. **Promote [[tech/patterns/test-economics]] from `draft` to
   `accepted`** with a note that the FP-stack amortisation case is
   not yet realised in any project. Confidence: medium.

4. **Leave [[tech/decisions/tidy-first-commits]] as `draft`.** This
   synthesis is silent on it.

5. **Update `promoted_from:` and `promotion_reason:` on the three
   promoted pages** to cite this synthesis.

### Follow-up work in `sourceline-manager` (would strengthen evidence)

6. **Extract a `MonoidLawsSuite[A]` trait** that takes a generator
   for `A` and an instance of `Monoid[A]` (or the project's
   informal "combine + empty" shape) and asserts left identity,
   right identity, and associativity via `forAll`. Use MUnit-
   ScalaCheck (`org.scalameta::munit-scalacheck`) on JVM at first;
   add the JS / Native targets once the JVM suite is stable.

7. **Replace the six hand-written law tests** with two calls into
   the shared suite. This realises the amortisation case
   ([[tech/patterns/test-economics]] §"One law, N implementations")
   and closes DRIFT-015h.

8. **Promote the laws to all three aliases.** Either state them
   against the canonical `++` and rely on aliasing tests
   (current), or state them via the shared suite parameterised by
   the canonical combine operation (cleaner).

### Wiki bookkeeping

9. **Update [[meta/drift]]**:
   - Three sub-flags can be reconsidered when their pages are
     promoted: DRIFT-014a/c/d (already addressed in
     [[tech/patterns/tdd-rhythm]]), DRIFT-015c/g (Stage 0 + cross-
     link to type-level errors).
   - DRIFT-015h stays open; this synthesis records it as
     "partially mitigated by `symmetric-refactoring` adoption,
     fully closed only when a `MonoidLawsSuite[A]` lands in any
     project."

10. **Update [[tech/patterns/functional-domain-design]] §Adopters**
    if the synthesis is cited there. (Not required — the §Adopters
    table already captures `sourceline-manager`'s shape.)

## Confidence Assessment

| Claim | Confidence | Why |
|-------|-----------|-----|
| The codebase exemplifies algebra-naming refactoring | High | Direct visual evidence in `SourceFile.scala`'s operator catalogue + matching tests |
| The codebase exemplifies Stage 0 type-first design | High | ADR-0001 + ADR-0002 in-tree explicitly commit to this |
| The codebase exemplifies the FP-stack amortisation case for test-economics | Low | The pattern is named but not realised; 2 × 3 = 6 hand-written tests, no shared suite |
| The codebase exemplifies law-based testing as a peer to example-based | Low | Laws are named as examples, not quantified |
| Promoting `symmetric-refactoring` on this evidence is justified | High | Decision-tree moves 1 and 2 both directly realised |
| Promoting `tdd-rhythm` on this evidence is justified | Medium | Stages 0/4 strongly corroborated; Stage 2 partial |
| Promoting `test-economics` on this evidence is justified | Medium | Per-test framing strong; amortisation argument unrealised |

## Status Update — 2026-05-29 (post-MonoidLawsSuite landing)

Recommendations 6 and 7 of this synthesis are **realised**:

- A reusable `MonoidLawsSuite[A]` (MUnit-ScalaCheck `ScalaCheckSuite`
  with `forAll`-quantified left identity, right identity, and
  associativity) lives at
  `/p/hg/sourceline-manager/slm/test/src/slm/MonoidLawsSuite.scala`.
  It takes the algebra name as a constructor parameter and abstract
  members `empty`, `combine(x, y)`, and `gen: Gen[A]`.
- `SourceLineMonoidLawsSpec` and `SourceFileMonoidLawsSpec` each
  consume the suite in one line plus three trivial member
  implementations. The six prior hand-written law tests (3 in
  `SourceLineSpec`, 3 in `SourceFileSpec`) are removed.
- Tests pass on JVM (140/140), Scala.js (163/163), and Scala Native
  (184/184).

Effects on the analyses above:

- **`tech/patterns/tdd-rhythm`** — the Stage 2 *quantified* /
  `forAll` claim is now realised in this codebase. The "partial
  evidence" verdict in this synthesis becomes **strong evidence**
  for the full Stage 2. DRIFT-015h is **closed**. `tdd-rhythm`
  `confidence` raised from `medium` to `high` in the same lint
  cycle.
- **`tech/patterns/test-economics`** — the FP-stack amortisation
  case is now realised. The previous "limit case of amortisation,
  not its payoff" verdict no longer holds: a third monoid in this
  codebase would cost three lines, not three more test files. The
  `confidence: medium` on `test-economics` is a candidate for raise
  to `high`, but a separate synthesis is needed (this one's body is
  already published and the update belongs in its own pass).
- **`tech/patterns/symmetric-refactoring`** — no change. Still
  strong evidence; still `confidence: high`.
- **Recommendation 8** (state the laws against all three aliases)
  is *partly* realised: the suite is parameterised by `combine`, so
  asserting the laws against `|+|` or `combine.combine` would be
  one-line cheap. The current specs run against the canonical `++`
  and rely on the existing aliasing tests (`|+| is alias for ++`,
  `combine is alias for ++` in `SourceLineSpec` / `SourceFileSpec`)
  to bridge to the other two operators. The cost/benefit of three
  more spec files for the same algebra is currently negative; the
  recommendation is downgraded from "do" to "available cheaply if
  ever needed".

Recommendation 1–5 (promotions and `promoted_from` updates) were
completed at synthesis-creation time on 2026-05-29; recommendation 9
(meta/drift bookkeeping) is folded into the same 2026-05-29 lint
augmentation that closed DRIFT-015h.

## Status Update — 2026-05-29 (post-primitives + StringUtils composition)

A second wave of evidence landed in the same codebase, extending
the algebraic-contract claim from the monoid layer to the full
operator catalogue.

### What landed

1. **Primitive operator set on `SourceLine`** (`SourceLine.scala`).
   Sixteen orthogonal primitives in five families: slicing
   (`take` / `drop` / `splitAt` / `takeWhile` / `dropWhile`), search
   (`indexWhere` / `lastIndexWhere` / `indexOfSlice`), predicates
   (`exists` / `forall` / `count` / `find`), pattern matching
   (`startsWith` / `endsWith` / `contains`), and joining
   (`intersperse`). Each one wraps a single `Vector[Token]` method;
   the set was chosen by the orthogonality / expressivity /
   composability principles of
   [[tech/patterns/functional-domain-design]] §"Design Principles
   for the Primitive Set".
2. **Expressivity-sufficiency proof** —
   `slm/test/src/slm/StringUtilsCompositionSpec.scala`. Twenty-three
   Apache Commons `StringUtils`-equivalent functions
   (`left`, `right`, `mid`, `substring`, `trim`, `strip`, `chop`,
   `chomp`, `repeat`, `wrap`, `padLeft`, `padRight`, `center`,
   `countMatches`, `countMatchesSlice`, `containsAny`,
   `defaultIfEmpty`, `appendIfMissing`, `prependIfMissing`,
   `replaceAll`, `replaceSlice`, `abbreviate`, `join`) are each
   defined as a local `def` composing only existing operators — no
   new methods added to `SourceLine`. The primitive set is shown
   *sufficient*; the imperative `StringUtils` surface is shown
   *derivable*.
3. **Algebraic contract for the primitives** —
   `slm/test/src/slm/SourceLinePrimitivesLawsSpec.scala`. Forty-six
   `forAll`-quantified properties grouped by primitive family:
   slicing duality (`take(n) ++ drop(n) == self`), `take`
   monotone-idempotence, `drop` composition, predicate-slicing
   saturation, search-result correctness
   (`drop(i).take(sub.length) == sub` when found), De Morgan
   (`forall(p) == !exists(!p)`), partition
   (`count(p) + count(!p) == length`),
   `find(p) == filter(p).head`, pattern-match biconditionals
   (`startsWith(p) ⇔ take(p.length) == p`), intersperse length
   (`2n − 1`), and closure laws for the existing operators
   (`reverse` involution + anti-distributivity, `map(identity)`,
   `filter` constant predicates). Tests pass on JVM (227/227).

### What this proves that the monoid laws alone did not

The monoid-law suite proves `(empty, ++)` is a monoid — three
properties on two instances. The new primitive-law suite proves
that the *entire operator catalogue* is law-bearing: 46 properties
across 16 primitives, each one stated against the primitive itself,
each one closed under the existing monoid. Together they convert
the static "expressivity is sufficient" snapshot from
`StringUtilsCompositionSpec` into a quantified contract — any
refactor that breaks a primitive's semantics breaks one of these
laws, and breaking a law breaks every derived combinator
transitively. The composition spec is the demonstration; the laws
spec is the maintenance guarantee.

### Effects on the analyses above

- **[[tech/patterns/functional-domain-design]]**. The §"Design
  Principles for the Primitive Set" triplet (orthogonality,
  expressivity, composability) was previously realised only in the
  monoid layer. It is now realised across the *full* primitive set
  — orthogonality is visible in the 16 single-purpose methods,
  expressivity is `StringUtilsCompositionSpec`, composability is
  the laws spec asserting the operators close cleanly. The
  §Adopters note for `sourceline-manager` can be sharpened from
  "monoid laws tested as part of the public contract" to "monoid
  and primitive laws tested as part of the public contract;
  expressivity sufficiency proven against Apache Commons
  `StringUtils`" — this synthesis is the citation.
- **[[tech/patterns/test-economics]]**. The amortisation case is
  now realised at **two** layers: the monoid `MonoidLawsSuite[A]`
  amortises three properties across N instances (2 today), and
  `SourceLinePrimitivesLawsSpec` amortises ~46 properties across
  ~16 primitives certifying 23 derived StringUtils-equivalent
  functions. The "limit case of amortisation, not its payoff"
  framing from the original synthesis no longer holds at all —
  the cost-per-derived-function is now near zero, since each new
  StringUtils-equivalent function is a one-`def` composition
  protected by the existing law suite. **Recommendation**:
  promote `test-economics` from `draft` to `accepted`, raise
  `confidence: medium` → `high`. The amortisation claim is no
  longer an "if extracted" subjunctive — it is realised twice.
- **[[tech/patterns/tdd-rhythm]]**. Stage 2 (law-based as peer to
  example-based) was raised to `confidence: high` on the monoid-
  laws landing. The new primitives-laws layer is additional
  evidence in the same direction — no further status change, but
  the in-codebase realisation is now an order of magnitude
  stronger.
- **[[tech/patterns/symmetric-refactoring]]**. Additional symmetric
  pairs landed: `take` / `drop`, `takeWhile` / `dropWhile`,
  `indexWhere` / `lastIndexWhere`, `startsWith` / `endsWith`,
  `prefix` / `postfix` (already there). No status change; the page
  already cites this codebase as the strong-evidence reference.

### Recommendations realised by this update

- **R-2026-05-29-a** — Promote [[tech/patterns/test-economics]]:
  `status: draft` → `accepted`, `confidence: medium` → `high`.
  `promoted_from` cites this synthesis; `promotion_reason` cites
  the two-layer amortisation realisation
  (`MonoidLawsSuite[A]` + `SourceLinePrimitivesLawsSpec`). §Open
  Questions §"No project currently exposes one" is rewritten as
  closed. §"FP-stack amortisation" paragraph removes the
  subjunctive ("would, if extracted") and points at this
  synthesis.
- **R-2026-05-29-b** — `used_by` on `test-economics` populated
  with `projects/sourceline-manager/adr/0001-adopt-functional-
  domain-design.md` (transitive: the project's FDD adoption is
  the carrier for its test-economics adoption; a separate
  test-economics adoption ADR is not warranted at this scale).

### What remains open

- **A `compositor`-side adoption of the same law-based discipline.**
  The compositor project has its own arena-allocator constraint
  (see `projects/compositor/adr/0001`), but the algebra layer
  could in principle carry the same property-based law suites.
  Synthesis-pending.
- **A second source for `test-economics`** independent of the Di
  Bello / Beck single-source. The realisation evidence is strong
  but Source Sufficiency Rule (POLICY.md) was satisfied earlier
  via the project synthesis. This update strengthens that
  satisfaction; it does not replace it.

## Links

- [[sources/raw/code/sourceline-manager]]
- [[projects/sourceline-manager/index]]
- [[projects/sourceline-manager/adr/0001-adopt-functional-domain-design]]
- [[tech/patterns/functional-domain-design]] — already accepted; new adopter
- [[tech/patterns/symmetric-refactoring]] — promoted to `accepted` (high) 2026-05-29
- [[tech/patterns/tdd-rhythm]] — promoted to `accepted` 2026-05-29; raised to `confidence: high` 2026-05-29 once DRIFT-015h closed
- [[tech/patterns/test-economics]] — promoted to `accepted` (medium) 2026-05-29; amortisation case now realised in-repo
- [[tech/decisions/tidy-first-commits]] — synthesis is silent
- [[meta/drift]] §DRIFT-015h — **resolved** 2026-05-29 by the realisation recorded in §Status Update

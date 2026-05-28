---
id: summary-throw-away-the-irrelevant-de-goes-podcast
title: "Summary: Throw Away the Irrelevant (John De Goes on CoRecursive)"
kind: descriptive
status: accepted
scope: global
created: 2026-05-28
updated: 2026-05-28
confidence: high
sources:
  - sources/raw/docs/throw_away_the_irrelevant_john_de_goes_podcast.txt
tags:
  - polymorphism
  - type-classes
  - principled-type-classes
  - effects
  - io-monad
  - monad-transformers
  - jvm-performance
  - scala
  - scalaz
  - cats
  - functional-design
---

## Source

- **Title**: Throw Away the Irrelevant (a.k.a. "When Your Variable Names Tell on You")
- **Speaker**: John A De Goes (CTO, SlamData at time of recording)
- **Interviewer**: Adam Gordon Bell (CoRecursive podcast)
- **Era**: circa 2018 — Scalaz 8 actively in development, Cats just at 1.0
- **Raw**: [[sources/raw/docs/throw_away_the_irrelevant_john_de_goes_podcast.txt]]
- **Domain**: Scala FP, type system design, effect systems, runtime performance

## Thesis

A good functional program is one in which you have **thrown away every
detail the solution does not require**. Polymorphism is the chief tool
for throwing things away; **principled type classes** add back only the
structure actually needed. Concrete types, concrete data structures,
and effect leakage are all symptoms of *premature specialization*. On
the JVM specifically, naive imitation of Haskell idioms — particularly
monad transformer stacks — destroys performance, so Scala FP must
evolve its own idioms that preserve the reasoning benefits without the
cost.

## Key Positions

### 1. Descriptive variable names as a code smell

If a variable name like `ofBeanProxyFactory` perfectly describes the
value, the type is monomorphic and the implementation space is huge —
"string to string" has infinite implementations, `for all A. A => A`
has one. **Strip names of meaning by stripping types of structure**;
the compiler then constrains the solution.

Even when reuse never materializes, polymorphism still pays off:

- The initial implementation is more likely to be correct.
- The function is harder to break in future edits.
- The reader's intuition strengthens over time ("muscle memory").

### 2. Principled type classes add back only what's necessary

Pure parametricity is often *too little* structure. The right move is
a type class that:

- Adds the **minimum** capability needed.
- Is governed by **algebraic laws** (associativity, identity, …) so
  reasoning is by law, not by instance.

The slogan: *polymorphism throws structure away; principled type
classes add back just enough to solve the problem*. Adding more than
needed re-enlarges the implementation space.

The same principle exists in OO ("require the smallest interface, provide
the largest"); FP just makes it sharper.

### 3. Data structures are antithetical to FP (deferred decisions)

A function returning `Either[Error, Response]` has prematurely
specialized. The caller likely lifts it into a richer monad
(`IO`, a transformer stack, a free structure). The function only
needed *something with a success and failure constructor*. Today's
languages make true polymorphism over data structures painful, but
the principle stands: where you can, return an abstraction over
"has the shape I need," not a concrete container.

Side benefits:

- Less mind-numbing lift/conversion boilerplate.
- **Performance**: each manual conversion allocates and copies.
- Reuse in unanticipated contexts.

### 4. Type class laws must include performance

Haskell-style type classes that abstract `random access` over linked
lists are a mistake — the laws hold but the cost model is
pathological. Performance characteristics (`O(1)`, `O(log n)`) should
be **first-class** parts of a type class contract, mechanically
verifiable in the same vein as QuickCheck. Today they're comments,
unenforced; that should change.

### 5. Type classes beat OO traits in Scala — almost always

- Type classes work for types you don't own; traits require control
  of the hierarchy.
- Subtype hierarchies poison type inference in subtle ways.
- The standard library already concedes this (`Ordered`, `Numeric`).
- The small extra boilerplate is **constant**, paid once per data type.

De Goes can think of essentially **no** case where he'd reach for a
trait over a type class.

### 6. Purely functional effects — the case for `IO` everywhere

Mixing imperative and functional code forces the reader to switch
reasoning modes (equational substitution vs. simulating a machine).
**One uniform mode** across the codebase is a force multiplier.

Functional effects deliver:

- Type-signature-as-contract — `Bool` cannot do socket I/O; you can
  *stop drilling into callees*.
- Reified effects — programs become values, manipulable like any
  other value.
- Testability — pure, total, deterministic.

`IO[Int]` is admittedly under-specified ("could do anything"). The
remedy is to **split capabilities** with type classes: `MonadRandom`,
`MonadSocketIO`, etc. — recovering precision without losing the
reified-program benefit.

### 7. Three generations of Scala effect monads

| Gen | Examples | Notes |
|-----|----------|-------|
| 1 | `Future` | Not really a monad; learned a lot from its mistakes |
| 2 | Scalaz 7 `Task` | First real attempt at IO-as-value |
| 3 | Monix `Task`, Scalaz 8 `IO` | Fast, rich, semantically clean |

Plurality is painful (incompatible libraries) but valuable
(parallel exploration). Standardizing too early bakes mistakes in
forever — once it's in a standard library, it never really leaves.

### 8. Monad transformers do not scale on the JVM

Twin failure modes:

1. **Heap churn** — every `flatMap` rebuilds the entire nested data
   structure; every Scala lambda is an object allocation.
2. **Megamorphism** — each transformer layer adds a virtual dispatch
   level. A 5-deep stack means megamorphic calls into megamorphic
   calls into megamorphic calls. The JIT cannot inline through it.

You can get away with this at ~10 req/s. At hundreds or thousands
of req/s, latency, GC pressure, and throughput collapse. Many Scala
shops blindly copied Haskell transformer patterns and gave FP a
bad reputation it deserved in that form.

### 9. The fix: type-class capabilities + a `newtype` over `IO`

Instead of `EitherT[StateT[IO, S, *], E, *]`, write:

```scala
opaque type MyIO[A] = IO[A]
```

with hand-written instances of `MonadError[MyIO, E]`,
`MonadState[MyIO, S]`, etc., implemented in terms of plain `IO`.

Result:

- The program is still polymorphic in `M[_]: MonadError[*, E]: MonadState[*, S]`.
- At the top of the world, the concrete type is one layer of
  indirection over `IO`. **Monomorphic, no nesting, no virtual
  dispatch.**
- Performance approaches raw `IO`; handles ~80% of transformer
  use cases. The remaining 20% (locally-eliminated effects) needs a
  separate trick.

### 10. Scala FP must diverge from Haskell

"FP in Scala" cannot be "Haskell on the JVM". Idioms that are free in
GHC are catastrophic under HotSpot. Healthy progress requires
inventing Scala-native patterns (the `newtype`-over-`IO` trick above,
fiber-based interruption in Scalaz 8, etc.) rather than transliterating.

### 11. Cats vs Scalaz 8 (era-specific)

- Pre-Scalaz-8: Cats and Scalaz 7 were architecturally similar; no
  compelling reason to use one over the other.
- At time of recording: Cats targets a minimal, stable surface
  (locked at 1.0). Scalaz 8 is a rethink — different effect semantics,
  faster runtime, more aggressive abstractions. The two can plausibly
  coexist serving different audiences.

*(Historical note: post-recording, Scalaz 8 IO effectively became ZIO.
Cats Effect 2/3 absorbed many of the runtime lessons. The
generational arc described continues into Kyo and other modern
effect systems.)*

### 12. Writing style: flow > facts

Closing meta-commentary on why his blog posts work:

- Know your audience and what they already believe.
- Maintain a clear arc; flow is underrated.
- A clickbait title is acceptable when it sets up an "aha" — the
  payoff is the reader's perspective shift, not the title itself.

## Cross-References

### Relation to existing wiki summaries

- [[sources/summaries/introduction_to_functional_design_john_de_goes]]
  — same author, *encoding* axis (executable vs declarative). This
  podcast complements it on the *constraint* axis (polymorphism +
  principled type classes) and on the *runtime* axis (JVM-specific
  performance pitfalls).
- [[sources/summaries/functional_domain_modeling_zio2_debasish_ghosh]]
  — Ghosh argues *concrete* `IO[E, A]` in repository/service
  contracts is a feature (visible failure + environment). De Goes
  argues for *polymorphic* `M[_]` with capability type classes.
  These positions appear to disagree but are actually about
  different boundaries: Ghosh is talking about **public service
  contracts** (where concreteness is documentation), De Goes is
  talking about **internal helper functions** (where polymorphism
  constrains implementations). Worth flagging as an open tension
  for any future `functional-domain-layering` synthesis.

### Relation to accepted normative pages

- [[tech/patterns/functional-domain-design]] — the encoding pattern
  is one face of "throw away the irrelevant." Polymorphism + type
  classes is another face, on the parameter side rather than the
  data-type side. A future tech-layer pattern (`principled-polymorphism`
  or similar) could be promoted once a second source or a project
  synthesis corroborates.

### Relation to our stack

- **Kyo**: solves the monad-transformer problem differently — effect
  composition is intersection (`A < Abort[E] & Async`), not stacking,
  so neither megamorphism nor heap-nesting accumulates. The
  performance argument in this transcript is one of the strongest
  prior-art justifications for that design choice. Skills:
  `scala:kyo-effects-sync-async-abort`,
  `scala:kyo-data-env-scope`.
- **ZIO** (descended from Scalaz 8 IO): the "monad error + monad
  state via a newtype over IO" idea here is essentially the
  intellectual ancestor of `ZIO[R, E, A]`. ZLayer is the
  environment plumbing that fell out of taking R seriously.

## Candidate Follow-ups

- **`tech/patterns/principled-polymorphism`** (draft only) — capture
  "polymorphism throws away structure; principled type classes add
  back the minimum." Currently single-source, so per `POLICY.md`
  promotion needs a second corroborating source or a project
  synthesis. Co-sources could be the Haskell typeclass literature
  or Kyo's effect-set design.
- **`tech/patterns/anti/monad-transformer-stacks-on-jvm`** — anti-pattern
  page. Strong single-source evidence; combine with any second source
  (e.g., ZIO motivation docs, Kyo design notes) before promotion.
- **Open tension to synthesize**: concrete `IO[E,A]` in public
  contracts (Ghosh) vs polymorphic `M[_]` with capabilities
  (De Goes). Both authorities, different boundaries. Belongs in
  a future `functional-domain-layering` page.

## Caveats

- Transcript-only source; no slides or code to cross-check.
- Time-specific: Scalaz 8, Cats 1.0, Monix Task era. The strategic
  positions remain relevant; specific library status does not.
- Two of De Goes' major projects post-date this recording (ZIO,
  later work). Treat library names as illustrative, not current.

## Links

- Raw: [[sources/raw/docs/throw_away_the_irrelevant_john_de_goes_podcast.txt]]
- Related summary: [[sources/summaries/introduction_to_functional_design_john_de_goes]]
- Related summary: [[sources/summaries/functional_domain_modeling_zio2_debasish_ghosh]]
- Related pattern: [[tech/patterns/functional-domain-design]]
- Schema: [[meta/schema]]
- Policy: [[POLICY]]

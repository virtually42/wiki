---
id: functional-domain-design
title: Functional Domain Design
kind: normative
status: accepted
scope: global
created: 2026-05-28
updated: 2026-05-28
confidence: high
applies_to:
  languages: [scala, scala-native, scala-js]
  domains: [any]
  excludes: [shell-scripts, nix-modules]
used_by:
  - projects/compositor/adr/0001-adopt-functional-domain-design.md
promoted_from: []
sources:
  - sources/summaries/introduction_to_functional_design_john_de_goes.md
  - sources/summaries/functional_domain_modeling_zio2_debasish_ghosh.md
tags: [functional-design, dsl, encoding, executable, declarative, initial, final, algebra]
---

## Problem

How do we build software that solves the many problems in a domain
(parsing, scheduling, validation, filtering, persistence, retry…) in a
way that is:

- **Testable** without spinning up the world,
- **Composable** — small pieces combine into solutions to big problems,
- **Maintainable** — adding a new requirement does not cascade,
- **Inspectable** — we can reason about, optimize, serialize, or render
  what the program will do?

Object-oriented design tends to scatter behavior across many classes
and mix description with execution, making the above hard. Ad-hoc
imperative pipelines tend to grow inconsistent vocabularies per
sub-problem.

## Solution

For each domain of interest:

1. Define an **immutable data type** that *models* solutions to problems
   in that domain. The model **describes**, it does not **do**.
2. Provide a small set of **constructors** that build models of simple
   problems.
3. Provide a small set of **composable operators** that combine and
   transform models into solutions to larger problems.
4. Provide one or more **interpreters** that execute the model
   (`Model => Result`, possibly effectful).

A *functional domain* is the tuple `(domain, model, constructors, operators)`.
The result is an embedded DSL with the smallest possible primitive set
covering the domain.

### Choose an Encoding

Two duals exist for the model:

- **Executable encoding (final)** — `case class` storing functions; each
  constructor and operator is expressed in terms of execution.
- **Declarative encoding (initial)** — `sealed trait` / `enum` ADT; each
  constructor and operator stores its arguments as data. Execution is a
  separate interpreter walking the tree.

| Concern | Executable | Declarative |
|---------|-----------|-------------|
| Add new constructor/operator | Free | Touch every interpreter |
| Add new interpreter | Touch every constructor/operator | Free |
| Optimization, rewriting, inspection | Hard (opaque functions) | Easy (data tree) |
| Persistence / serialization | Hard | Natural |
| Wrapping impure legacy APIs | Strong | Weaker |
| Reader cost | Low (obvious) | Higher (indirection) |

The two encodings are **mirror images** along the expression-problem
axis. Pick deliberately; don't drift between them within one domain.

## Structure

```
        Domain of Interest
                |
                v
   +-----------------------------+
   |   Immutable Model (ADT)     |   <-- describes solutions
   +-----------------------------+
       ^               ^
       |               |
   constructors    operators
   (atoms)         (composition: &&, ||, map, andThen, …)
       ^               ^
       |               |
       +------ users ---+
                |
                v
   +-----------------------------+
   |       Interpreter(s)        |   <-- run / render / serialize / …
   +-----------------------------+
```

### Design Principles for the Primitive Set

- **Orthogonality** — no constructor or operator is expressible in terms
  of the others. Minimize the primitive set; build everything else as
  derived combinators.
- **Expressivity** — the primitive set must cover every problem in the
  domain.
- **Composability** — operators must combine *predictably*. Algebraic
  laws (associativity, identity, distributivity) are the target.

## Code Example

Domain: **email filtering**.

### Executable encoding

```scala
final case class EmailFilter(matches: Email => Boolean):
  def &&(that: EmailFilter): EmailFilter =
    EmailFilter(e => matches(e) && that.matches(e))
  def ||(that: EmailFilter): EmailFilter =
    EmailFilter(e => matches(e) || that.matches(e))
  def unary_! : EmailFilter =
    EmailFilter(e => !matches(e))

def subjectContains(p: String): EmailFilter =
  EmailFilter(_.subject.contains(p))

val filter =
  (subjectContains("discount") || subjectContains("clearance"))
    && !subjectContains("liquidation")
```

### Declarative encoding

```scala
enum EmailFilter:
  case SubjectContains(phrase: String)
  case And(l: EmailFilter, r: EmailFilter)
  case Or(l: EmailFilter, r: EmailFilter)
  case Not(v: EmailFilter)

  def &&(that: EmailFilter): EmailFilter = And(this, that)
  def ||(that: EmailFilter): EmailFilter = Or(this, that)
  def unary_! : EmailFilter               = Not(this)

import EmailFilter.*

def matches(f: EmailFilter, e: Email): Boolean = f match
  case And(l, r)          => matches(l, e) && matches(r, e)
  case Or(l, r)           => matches(l, e) || matches(r, e)
  case Not(v)             => !matches(v, e)
  case SubjectContains(p) => e.subject.contains(p)

def describe(f: EmailFilter): String = f match
  case And(l, r)          => s"(${describe(l)} && ${describe(r)})"
  case Or(l, r)           => s"(${describe(l)} || ${describe(r)})"
  case Not(v)             => s"!${describe(v)}"
  case SubjectContains(p) => s"(subject contains $p)"
```

Same surface API; `describe` was free to add in declarative form but
would have meant editing every constructor/operator in the executable
form.

## When To Use

- The domain has **many** distinct problems with a recognizable family
  resemblance (parsing variants, schedule variants, filter variants,
  validation variants, …).
- You want to write user-facing logic in domain vocabulary, not
  framework vocabulary.
- You expect the rules to change — a small algebra absorbs change
  better than ad-hoc functions.
- You need at least one of: testability without IO, persistence of
  rules, multiple renderings (run / explain / preview), optimization.

### Prefer **declarative** when

- The rules need to be persisted, serialized, sent over the wire, or
  inspected by tooling.
- You will likely add more interpreters than primitives (render,
  optimize, statically analyze, dry-run).
- Performance demands rewrite-based optimizations.

### Prefer **executable** when

- The model needs to wrap a substantial impure legacy API cleanly
  (e.g. an existing `InputStream` ecosystem).
- The primitive set will keep growing but the interpreters stay few.
- A casual reader's first encounter with the type should make
  "what does it do" obvious.

## When Not To Use

- The domain is small enough that a few plain functions suffice. Don't
  invent an algebra for three rules that will never grow.
- There is no recognizable composition — if problems in the "domain"
  don't combine, you don't have a domain, you have a list of features.
- The expected primitive set is unstable and you have no time budget
  to refactor — both encodings punish the wrong choice when growth
  pivots to the other axis.

## Related Patterns

- **Algebra / Program / Interpreter** — the underlying triplet this
  pattern instantiates. (Skill: `scala:functional-dsl-design`.)
- **Tagless-final** — a third encoding intermediate between executable
  and declarative; trades some clarity for late-bound interpretation
  via typeclass instances. Cited as further reading by
  [[sources/summaries/introduction_to_functional_design_john_de_goes]].
- **Object algebras** — another solution to the expression problem,
  same axis.
- **Functional Domain Layering** (future page, candidate) — orthogonal
  to encoding; concerns *how* a functional domain composes with
  effects, repositories, and services at the application boundary.
  See [[sources/summaries/functional_domain_modeling_zio2_debasish_ghosh]]
  for one realization in ZIO 2.

## Examples In The Wild

- **ZIO Schedule** — declarative; constructors like `dayOfWeek`,
  `hourOfDay`; operators like intersection (`&&`), `map`.
- **Parser combinators** — both encodings exist in the literature.
- **Optics (Monocle)** — declarative algebra over data access.
- **Streams (ZIO Stream, fs2)** — declarative algebra over concurrent
  data flow.
- **Tapir endpoints** — declarative HTTP endpoint algebra
  (matches, codecs, errors).
- **Kyo effects** — declarative algebra of suspensions (relevant to
  our stack).
- **Tagless HTML DSL** (our frontend) — declarative algebra over
  HTML structure; see `frontend:tagless-html-dsl`.

## Open Questions / Drift Signals

- We have no project ADR yet citing this page. Until a project adopts,
  excepts, or ignores it, lint will surface it under
  *unused normative pages* in `meta/drift.md`.
- Status is `accepted` (promoted by human 2026-05-28). In-scope projects
  must now adopt, except, deviate from, or ignore this pattern in an
  ADR per `POLICY.md`.

## Links

- [[sources/summaries/introduction_to_functional_design_john_de_goes]]
- [[sources/summaries/functional_domain_modeling_zio2_debasish_ghosh]]
- [[meta/schema]]
- [[POLICY]]

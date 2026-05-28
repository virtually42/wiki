---
id: summary-functional-design-de-goes
title: "Summary: An Introduction to Functional Design (John A De Goes, 2020)"
kind: descriptive
status: accepted
scope: global
created: 2026-05-28
updated: 2026-05-28
confidence: high
sources:
  - sources/raw/docs/introduction_to_functional_design_john_de_goes.txt
tags: [functional-design, encoding, dsl, executable, declarative, initial, final, zio, scala]
---

## Source

- **Title**: An Introduction to Functional Design
- **Author**: John A De Goes
- **Published**: 2020-08-18
- **Raw**: [[sources/raw/docs/introduction_to_functional_design_john_de_goes.txt]]
- **Domain**: functional design, DSL construction, Scala

## Thesis

Functional design is an alternative to object-oriented design. It models
solutions to problems in a *domain of interest* using **immutable data
types**, equipped with:

- **Constructors** — build simple solutions
- **Composable operators** — combine/transform solutions into larger ones

A small set of primitive constructors and operators should suffice to
solve all problems in the domain. The data type is a *model* (describes,
does not act); execution happens later via an interpreter.

## Key Concepts

### Functional Domain
Shorthand for: a domain of interest + its immutable model + the model's
constructors and operators.

### Model vs Execution
Models describe, they don't do. Execution is a separate phase, performed
by interpreters that walk the model.

### Two Encodings

| Aspect | Executable (final) | Declarative (initial) |
|--------|-------------------|----------------------|
| Representation | `case class` storing functions | `sealed trait` / `enum` ADT |
| Constructors & operators | Express in terms of execution | Store arguments as data |
| Interpreter | Built-in (just call the function) | Separate function pattern-matching on cases |
| Add new constructor/operator | Free (no existing code changes) | Must update all interpreters |
| Add new interpreter | Must update all constructors/operators | Free (just add a new function) |
| Optimization (rewrite, inspect) | Hard (opaque functions) | Easy (pure data tree) |
| Persistence | Hard | Easy (data is serializable) |
| Legacy interop | Strong (wraps impure interfaces cleanly) | Weaker |

The two encodings are **duals** — mirror images of each other along the
expression-problem axis.

## Worked Example: Email Filter

Both encodings expose `&&`, `||`, `unary_!`, and `subjectContains`:

**Executable**:
```scala
final case class EmailFilter(matches: Email => Boolean) { self =>
  def &&(that: EmailFilter): EmailFilter =
    EmailFilter(e => self.matches(e) && that.matches(e))
  def ||(that: EmailFilter): EmailFilter =
    EmailFilter(e => self.matches(e) || that.matches(e))
  def unary_! : EmailFilter =
    EmailFilter(e => !self.matches(e))
}
def subjectContains(p: String): EmailFilter =
  EmailFilter(_.subject.contains(p))
```

**Declarative**:
```scala
sealed trait EmailFilter { self =>
  def &&(that: EmailFilter): EmailFilter = And(self, that)
  def ||(that: EmailFilter): EmailFilter = Or(self, that)
  def unary_! : EmailFilter = Not(self)
}
final case class SubjectContains(phrase: String) extends EmailFilter
final case class And(l: EmailFilter, r: EmailFilter) extends EmailFilter
final case class Or(l: EmailFilter, r: EmailFilter)  extends EmailFilter
final case class Not(v: EmailFilter)                  extends EmailFilter

def matches(f: EmailFilter, e: Email): Boolean = f match {
  case And(l, r)            => matches(l, e) && matches(r, e)
  case Or(l, r)             => matches(l, e) || matches(r, e)
  case Not(v)               => !matches(v, e)
  case SubjectContains(p)   => e.subject.contains(p)
}
```

Adding a `describe: String` interpreter is trivial in the declarative
form (new function) and invasive in the executable form (extra field on
every constructor).

## Example Domains Cited

- **Parser combinators** — parsing text to data structures
- **Functional effects (ZIO)** — concurrent, safe effects
- **Optics (Monocle)** — immutable data access/modification
- **Streams (ZIO Stream)** — concurrent data pipelines
- **ZIO Schedule** — recurring schedule specification (worked through)

## Choosing an Encoding

- **Performance-critical / optimizable** → declarative (data permits rewrite passes)
- **Persistence required** → declarative (serializable)
- **Heavy legacy interop, impure underlying API** → executable (wraps cleanly)
- **Many future interpreters** → declarative
- **Many future operators** → executable

## Related Concepts (Author Points To)

- Expression problem
- Object algebras
- Tagless-final style
- Phantom types / type-level programming for type-safe domains
- Principles of orthogonality, expressivity, composability for designing
  good primitive sets

## Relevance To Our Wiki

This material is a candidate for elevation to a `tech/pattern` page on
**functional-domain-design** (executable vs declarative encoding
tradeoffs). Several existing tools we use exhibit this shape:

- Kyo (effect system) — declarative encoding underneath
- Tapir endpoint descriptions — declarative
- Tagless HTML DSL (in our frontend skills) — algebra/program/interpreter

Citing this summary from a future pattern page satisfies the provenance
chain required by [[POLICY]].

## Links

- Raw: [[sources/raw/docs/introduction_to_functional_design_john_de_goes.txt]]
- Schema: [[meta/schema]]
- Related skill: `scala:functional-dsl-design`

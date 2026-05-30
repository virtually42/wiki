---
id: functional-domain-design
title: Functional Domain Design
kind: normative
status: accepted
scope: global
created: 2026-05-28
updated: 2026-05-29
confidence: high
applies_to:
  languages: [scala, scala-native, scala-js]
  domains: [any]
  excludes: [shell-scripts, nix-modules]
used_by:
  - projects/compositor/adr/0001-adopt-functional-domain-design.md
  - projects/sourceline-manager/adr/0001-adopt-functional-domain-design.md
  - projects/toolbox/adr/0001-adopt-functional-domain-design.md
  - projects/dependency-manager/adr/0002-adopt-functional-domain-design.md
  - projects/tagless/adr/0001-adopt-functional-domain-design.md
  - projects/shapesdsl/adr/0001-adopt-functional-domain-design.md
  - projects/animdsl/adr/0001-adopt-functional-domain-design.md
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

## Adopters

Six project ADRs currently cite this page, all with the declarative
encoding:

| Project | ADR | Stance | Notes |
|---------|-----|--------|-------|
| compositor | [[projects/compositor/adr/0001-adopt-functional-domain-design]] | Adopts with one deviation | Deviation on allocation semantics — interpreters must allocate only from arena / per-frame scratch, never from the GC heap. Default encoding **declarative** for pipeline domains, **executable** only where wrapping opaque wlroots/libinput callbacks leaves no clean declarative shape. |
| sourceline-manager | [[projects/sourceline-manager/adr/0001-adopt-functional-domain-design]] | Adopts unconditionally | Declarative encoding throughout. Reference implementation — `Token` / `SourceLine` / `SourceFile` ADT with monoid laws tested as part of the public contract. |
| toolbox | [[projects/toolbox/adr/0001-adopt-functional-domain-design]] | Adopts unconditionally | Multi-module realisation across 10 modules; `enum Cmd`, `enum Pipeline`, `enum ProcessDescription`, `VirtualFileSystem`. Effects confined to the `proc-*` interpreter family; algebra modules carry no effect machinery. |
| dependency-manager | [[projects/dependency-manager/adr/0002-adopt-functional-domain-design]] | Adopts unconditionally | Two worked layers — `dm.catalog` (data: `Coord`/`Library`/`Catalog`) + `dm.mill` (subprocess DSL: `Mill.Cwd`/`Invocation`). One catalog model + N format interpreters (TOML/YAML/Dependencies.mill). |
| tagless | [[projects/tagless/adr/0001-adopt-functional-domain-design]] | Adopts unconditionally | Type-safe HTML DSL family — 14 modules with phantom-typed cursor algebra (`Cursor[D <: Depth, K <: ElementKind]`) and type-state grammars (`Form[S <: FormState]`, `Table[S <: TableState]`). Compile-time-validated builder transitions. |
| shapesdsl | [[projects/shapesdsl/adr/0001-adopt-functional-domain-design]] | Adopts unconditionally | `enum Shape`, `final case class Heatmap`, `ShapeScene` ADT; pure builders; total `toSvg` / `toPng` / `toScene` interpreters. Cross-repo SNAPSHOT consumer of `tagless-core`. |

In-scope project still missing a stance: **safetensors-scala** (see
[[meta/drift]] §DRIFT-024).

The six realisations span four orthogonal shapes — real-time
allocation-constrained system (compositor), foundation algebra with
laws (sourceline-manager), multi-module process/effects family
(toolbox), data+DSL twin algebras (dependency-manager), phantom-typed
cursor + type-state grammar (tagless / shapesdsl). A future adopter
that fits none of these shapes without explanation is a signal worth
a synthesis.

## Conformance

verifiability: medium
verifiability_rationale: |
  Structural signals (immutability, ADT encoding, presence of
  composable operators) are mechanically detectable in source.
  Whether the model *describes* vs *does*, and whether interpreters
  are properly separated, requires reading code to judge — that's
  the soft-signal half. A purely structural verdict over-rates
  shape adherence; a purely judgement-based verdict under-uses
  cheap mechanical signals. Both halves are needed.

hard_signals:
  - id: no-var-in-domain
    name: No `var` declarations in domain code
    method: grep
    pattern: '\bvar\s+\w+\s*[:=]'
    scope: 'src/main/scala/**/{domain,model,algebra}/**.scala'
    verdict_on_match: violation
    rationale: |
      FDD's first principle is an immutable data type. `var` in the
      domain layer breaks the "describes, doesn't do" stance even
      when surrounded by case classes.

  - id: adt-encoding-present
    name: Domain code uses case class / enum / sealed trait
    method: grep
    pattern: '(?m)^\s*(?:final\s+)?(?:case\s+class|enum|sealed\s+trait)\b'
    scope: 'src/main/scala/**/{domain,model,algebra}/**.scala'
    verdict_on_match: evidence
    rationale: |
      FDD requires an immutable data type. Without at least one ADT
      constructor in the domain layer the pattern isn't realised at
      all. Count and listing of matches is part of the report row.

  - id: composable-operators-present
    name: Operators on the domain ADT that combine values
    method: grep
    pattern: 'def\s+(&&|\|\||andThen|orElse|unary_!|map|flatMap|combine)\b'
    scope: 'src/main/scala/**/{domain,model,algebra}/**.scala'
    verdict_on_match: evidence
    rationale: |
      Composability is the third pillar. Absence of these names
      isn't conclusive (operators may be named differently per
      domain), but presence is strong positive evidence.

  - id: no-runtime-effects-in-algebra
    name: No effect-type signatures in the domain layer
    method: grep
    pattern: '\b(?:IO|Future|Kyo|Async|Resource)\s*\['
    scope: 'src/main/scala/**/{domain,model,algebra}/**.scala'
    verdict_on_match: violation
    rationale: |
      The algebra is meant to be pure data. Effects belong in
      interpreters. Leaking effect type constructors into the
      domain types couples description and execution — explicitly
      the failure mode this pattern exists to prevent.

soft_signals:
  - id: describes-not-does
    name: Encoding is consistent (declarative or executable, not drifting)
    prompt: |
      Inspect the ADTs in the project's domain layer (scope below).
      Decide which encoding the project uses:
        - declarative: constructors store their arguments as data
          (`enum` / sealed-trait variants holding fields); execution
          happens in separate `match` interpreters.
        - executable: case classes store functions (`val matches: A => B`);
          constructors return values that already know how to execute.
        - mixed: the same model uses both shapes inconsistently.
        - neither: no recognisable encoding — methods execute IO
          directly without an intermediate data shape.
      Cite 2-3 file:line pairs supporting the verdict.
    verdict_kinds: [declarative, executable, mixed, neither, unclear]
    scope: 'src/main/scala/**/{domain,model,algebra}/**.scala'
    rationale: |
      Either pure encoding is FDD-compliant. Drift between them
      within one model is the violation worth catching — and is
      what a grep can't see.

  - id: interpreter-separation
    name: Interpreter is a distinct site, not baked into the model
    prompt: |
      Find where the domain ADT is *consumed* — the code that
      pattern-matches it and produces an outcome (rendering, IO,
      a computed value). Is the interpreter a clearly separate
      module / file / object? Or are the operations baked into
      the model (methods on the ADT that immediately execute)?
      Cite the interpreter file(s) or, if baked-in, an example
      method whose body performs effects.
    verdict_kinds: [separated, baked-in, mixed, no-interpreter-found, unclear]
    scope: 'src/main/scala/**'
    rationale: |
      "Model describes, interpreter executes" is the structural
      consequence of the pattern. Baked-in operations indicate a
      partial / drifting adoption.

classification:
  adopts: |
    All hard signals pass (no `var` in domain; ADTs present;
    operators present; no effect types in algebra). Soft signals
    return `describes-not-does ∈ {declarative, executable}` AND
    `interpreter-separation = separated`.
  adopts_with_exceptions: |
    All hard signals pass OR one violation pinned to a named
    file/module (e.g. `var` in a single Buffer.scala for arena
    reuse). Soft signals positive overall. Exceptions list the
    pinned spots with file paths and rationale.
  deviates: |
    Project consistently uses a non-FDD shape — e.g. classes whose
    methods directly execute IO with no intermediate data model.
    Hard signals fail consistently; soft signals return `neither`
    or `baked-in`.
  ignores: |
    Project's language stack falls outside applies_to (e.g. a
    Nix-only project; covered by excludes). Pattern-specific
    additional case: project is a pure thin wrapper around an
    external API with no domain modelling of its own.

adr_template: |
  ## Context

  {project} models {evidence_summary.adts_named_top_3} in
  {evidence_summary.domain_paths}. The encoding observed is
  {soft.describes_not_does}; interpreters live in
  {soft.interpreter_locations}.

  ## Decision

  {project} adopts [[tech/patterns/functional-domain-design]]
  with the {soft.describes_not_does} encoding.
  {if exceptions: "One exception: {exceptions[0].file}
  ({exceptions[0].rationale})."}

  ## Consequences

  - The domain layer remains testable without IO.
  - Adding a new interpreter is {free if declarative else "touches every constructor"}.
  - Adding a new constructor is {free if executable else "touches every interpreter"}.

  ## Links

  - [[tech/patterns/functional-domain-design]]
  - Evidence: {evidence_summary.citations}

## Open Questions / Drift Signals

- **Functional-domain-layering as a separate page.** Ghosh's source
  ([[sources/summaries/functional_domain_modeling_zio2_debasish_ghosh]])
  covers an axis this page does not — architectural layering of a
  functional domain into entities / value objects / repositories /
  domain services. Cited under Related Patterns; a separate
  `tech/patterns/functional-domain-layering.md` is a standing
  candidate, awaiting either a second corroborating source or a
  project synthesis (per `POLICY.md`).
- **PBT-as-peer realised, recorded elsewhere.** The 2026-05-29
  promotion of [[tech/patterns/tdd-rhythm]] (confidence `high`) and
  [[tech/patterns/test-economics]] (confidence `high`) closed the
  prior PBT-as-peer question against the
  `sourceline-manager` `MonoidLawsSuite[A]` realisation. The two
  pages now carry the law-based-as-peer position explicitly; nothing
  for FDD-the-page to add.

## Links

- [[sources/summaries/introduction_to_functional_design_john_de_goes]]
- [[sources/summaries/functional_domain_modeling_zio2_debasish_ghosh]]
- [[meta/schema]]
- [[POLICY]]

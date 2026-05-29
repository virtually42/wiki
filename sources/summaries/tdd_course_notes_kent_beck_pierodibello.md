---
id: summary-tdd-course-notes-kent-beck-pierodibello
title: My notes on Kent Beck's TDD course (Pietro Di Bello, 2021)
kind: descriptive
status: accepted
scope: global
created: 2026-05-29
updated: 2026-05-29
confidence: medium
sources:
  - sources/tmp/tdd_course_notes_kent_beck_pierodibello.md
tags: [tdd, testing, kent-beck, refactoring, design, rhythm, feedback, test-economics, secondary-source]
---

## Source

A short, structured set of notes by Pietro Di Bello (Medium,
2021-04-02) on Kent Beck's 2010 Pragmatic Screencasts TDD course — a
four-part video series in which Beck develops a Java client for
Tyrant DB (a key-value store) across roughly two hours of screencast.
Di Bello's notes follow Beck's narration and organise the material
into ~20 themes.

This is a **secondary source**. The primary sources behind it are
Beck's screencast itself, Beck's *Implementation Patterns* (book),
and Beck's *Test Desiderata* article — all referenced by Di Bello
but not yet ingested into this wiki.

## Themes (Di Bello's structuring of Beck's material)

### 1. Test list as a planning artefact

Start a TDD session by writing a TODO list of tests you want to see
green. Treat it as a living artefact — add new entries as ideas and
issues surface mid-flow. The list is the agenda, not just a backlog.

### 2. End-to-end first, for feedback speed

Get a thin end-to-end test running early. The rapid feedback loop is
what makes the rest of TDD work; everything later builds on the
infrastructure stood up here. Test names narrate behaviour and intent
(they read as sentences about what the system does), not as labels
for the code under test.

### 3. Small steps, deterministic isolation

- Keep test increments small so a failure points at a single change.
- Tests must leave the world unchanged. Clean up *after* a test, not
  *before* — relying on "the next test cleans up first" introduces
  order coupling.
- A test suite that passes individually, grouped, and in random order
  is the practical definition of *isolated*.

### 4. Two-phase implementation ("TDD as if you meant it")

Beck's expand-then-extract pattern:

1. Write the initial implementation **inside the test method** to keep
   the loop tight.
2. **Extract** to a method inside the test class once the shape
   stabilises.
3. **Move** to the production class once the abstraction is clear.
4. Inner classes may live briefly before being promoted to top-level —
   intermediate steps are not just allowed but desirable for feedback
   speed.

### 5. Design happens during refactoring, not during test writing

Defer non-trivial design decisions to the green → refactor step.
While red, write the minimum code needed to flip the light. The
discipline is *delaying commitment*: the refactor step is where you
make the design call from a position of full knowledge of the failing
case.

### 6. "Fake it till you make it"

When the real implementation is non-obvious, hard-code a value that
turns the test green. Then either:

- write further tests that force the fake to generalise, or
- gradually replace the constant with computed logic.

Temporary duplication on the green path is acceptable; the rule is
that the bar must be green before any refactor moves.

### 7. Symmetry as a refactoring guide

Avoid extractions that introduce asymmetry across methods. If two
methods are *almost* parallel, the right move is often to preserve
the duplication and keep the symmetry — *not* to extract one and
leave the other dangling. Symmetric duplication signals an algebra
waiting to be discovered; asymmetric extraction destroys the signal.

### 8. Predictive testing ("Call the shot")

Before running the suite, predict the outcome — which tests pass,
which fail, what the error message will be. Being wrong is a learning
event; being right reinforces the mental model. The cost is zero, the
information return is high.

### 9. Macro and micro rhythms

TDD has nested rhythms:

- **Micro** — red / green / refactor in seconds-to-minutes.
- **Macro** — problem framing / development / cleanup over hours,
  days, and longer.

The temporal structure of a TDD session mirrors storytelling pacing:
small beats nested inside larger arcs. Awareness of the rhythm is
itself a TDD skill.

### 10. Test economics

Every test is a *transaction*:

- Costs: writing time, maintenance over the life of the code, slowdown
  of the suite, brittleness under refactor.
- Benefits: information about correctness, regression protection,
  documentation, emotional safety while making changes.

The same logic applies to skipped tests: every test you *don't* write
creates a risk debt. The balance depends on confidence in the code
and the likelihood of future change. There is no universal rule; the
practitioner judges per case.

### 11. Beck-vs-Mancuso: when does design happen

Two viable TDD styles diverge on the timing of design:

- **Beck-style** — minimal test setup, design decisions deferred to
  refactor.
- **Mancuso-style** (mock-heavy outside-in) — design decisions
  encoded in the test as collaborators are invented at the boundary.

Same outcome (green tested code), different stage of the cycle owns
the design call. Choice is contextual, not doctrinal.

### 12. Problem slicing & task order

Break a problem into smaller bottom-up operations whose tests run
fast. The *order* in which you tackle slices affects the resulting
architecture — not just the path you take to it. Beck's recommended
exercise: solve the same problem multiple times in different orders
and compare the resulting designs and feedback velocity.

### 13. Private-method tests as scaffolding

Tests written to drive bottom-up implementation may target private
methods. Once the top-level behaviour is verified, the
private-method tests can be deleted — they were scaffolding for
construction, not load-bearing protection. Leaving them in place
ossifies the internal structure.

### 14. Error handling is a *choice*, not a default

Whether to write tests for error conditions is a design decision, not
a hygiene rule:

- Public APIs facing untrusted callers warrant null-checks and
  error-path tests.
- Internal code with enforceable invariants can skip defensive tests.

The wiki page on [[tech/patterns/functional-domain-design]] points the
same way at a different angle: in a closed algebra, many error cases
disappear at the type level and need no test.

### 15. TDD maturity = managing two axes

A practitioner becomes good at TDD by managing two things at once:

- **Management** — which test next, in what order.
- **Design** — which design decision next, at which point in the
  cycle.

Both axes interact. Experience is largely about feeling the
interaction without having to reason about it explicitly.

## Open questions / drift signals

- This is the wiki's first source on TDD. Per `POLICY.md`, promotion
  of any of these themes to a `tech/patterns/` page requires either a
  second corroborating source or a project synthesis.
- Candidate normative pages once a second source lands:
  - `tech/patterns/tdd-rhythm` (themes 1, 4, 5, 9) — the
    test-list → expand → extract → refactor loop.
  - `tech/patterns/test-economics` (theme 10) — cost / benefit framing
    for individual tests and skipped tests.
  - `tech/patterns/symmetric-refactoring` (theme 7) — symmetry as
    refactoring signal.
- Plausible second sources to ingest later: Beck's *Test-Driven
  Development: By Example* (book), Beck's *Test Desiderata* article,
  Freeman & Pryce's *Growing Object-Oriented Software, Guided by
  Tests*.
- Tension with the existing `devtools:tdd` agent skill — that skill
  already encodes a TDD posture for this codebase. Worth a short
  synthesis once a second source corroborates whether Beck's
  refactor-time-design framing or Mancuso's outside-in framing fits
  better with our FP-heavy stack.

## Links

- [[sources/tmp/tdd_course_notes_kent_beck_pierodibello]] — staged raw extraction (pending promotion to `sources/raw/docs/`)
- [[tech/patterns/functional-domain-design]] — Theme 14 cross-refs the closed-algebra angle on error handling
- External (cited by Di Bello, not yet ingested):
  - Kent Beck — *Implementation Patterns* (book)
  - Kent Beck — *Test Desiderata* (article)
  - Kent Beck — Pragmatic Screencasts TDD course (2010)
  - Sandro Mancuso — TDD video series

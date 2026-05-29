# Raw extraction — "My notes on Kent Beck's TDD course"

**Source URL:** https://pierodibello.medium.com/my-notes-on-kent-becks-tdd-course-8a1a7c8b7a95
**Author:** Pietro (Piero) Di Bello
**Publication date:** 2021-04-02
**Fetched:** 2026-05-29
**Method:** WebFetch (Medium HTML → structured outline). No verbatim
passages reproduced — only structure and claims. The page is staged
here for human triage; promote to `sources/raw/docs/` if the human
wants the article preserved as raw source.

---

## Subject

Notes taken by Di Bello while watching Kent Beck's 2010 Pragmatic
Screencasts TDD course (a 4-part video series in which Beck develops
a Java client for Tyrant DB — a key-value store — across roughly two
hours of screencast).

Author framing: test names quoted as direct narration of behaviour
and intent.

---

## Course outline (Di Bello's structuring of Beck's material)

### Test list & initial planning
- Begin TDD by creating a TODO list of desired passing tests.
- Add new ideas / issues as they emerge during development.

### Feedback speed
- Prioritise rapid feedback by testing end-to-end functionality early.
- Test names should narrate behaviour and intent.

### Test granularity & steps
- Small incremental test steps reduce debugging complexity when
  failures occur.
- Cascade failures make root causes harder to identify.

### "TDD as if You Meant It" — implementation approach
- Write initial implementations directly within test code.
- Extract methods to clarify tests, then move to application classes.
- Maintain inner classes briefly before full extraction (supports
  faster feedback).

### Test isolation & determinism
- Tests should leave the world unchanged after execution.
- Clean up *after* test runs, not before.
- Ensure tests pass individually, grouped, and in random order.
- Tests become deterministic through proper isolation.

### Guard clauses & style
- Prefer guard-clause patterns for handling conditions (detailed in
  Beck's "Implementation Patterns" book).

### Design timing
- Defer substantial design work until tests pass.
- Refactoring phase is the primary design opportunity.

### "Fake it till you make it"
- Implement placeholder solutions initially.
- Replace gradually or write additional tests to force real
  implementations.
- Tolerate duplication temporarily to maintain green status.

### Test-case decisions
- Context matters: testing client behaviour differs from testing
  database behaviour.
- Avoid redundant test cases where existing tests sufficiently verify
  functionality.

### Test organisation
- Order tests by behavioural relationship.
- Test classes should read narratively.

### Symmetry as a design driver
- Avoid extractions that create asymmetry across methods.
- Preserve consistent patterns even if duplication results.

### Feedback frequency
- Red → Green → Refactor cycle creates a development rhythm.
- Early error detection prevents cascading issues.

### Predictive testing ("Calling the Shot")
- Predict test outcomes before execution.
- Strengthens understanding of code behaviour.

### TDD style variations (Beck vs. Mancuso)
- Beck's approach: design primarily during refactoring with minimal
  test setup.
- Mancuso's approach (mocking-heavy): design decisions embedded in
  test writing.
- Different styles trade off **when** design decisions occur.

### Problem slicing
- Break large problems into smaller, faster-feedback tasks.
- Bottom-up approach: test small operations, compose into complete
  solutions.
- Task ordering affects design direction and feedback speed.

### Private-method testing
- Use tests during bottom-up implementation to drive design.
- Delete tests for private methods once implementation completes
  (analogous to removing scaffolding).

### Error handling vs. happy path
- Choice-based: design determines what to test.
- Public APIs warrant null-checks and error conditions.
- Internal code can omit defensive tests if invariants are guaranteed.

### Incremental design
- Gradually differentiate design complexity.
- Task-order permutation affects resulting architecture and feedback
  quality.
- Awareness of *when* design decisions occur improves the process.

### Beck's design exercise
- Solve the same problem multiple times using different decision
  orders.
- Compare resulting designs and feedback velocity.
- Identifies the most efficient approach.

### Rhythm & temporal structure
- Micro-rhythm: test → code → refactor cycles.
- Macro-rhythm: problem → development → cleanup at multiple time
  scales.
- Mirrors storytelling pacing (two-hour, daily, weekly, monthly
  cycles).

### Test economics
- Every test incurs costs (short and long term) that must yield
  informational / emotional benefits.
- Every skipped test creates risk (feedback loss, regression
  potential).
- Balance depends on confidence level and change likelihood.

### TDD maturity requirements
- Management tasks: selecting which tests to write and sequencing.
- Design tasks: choosing design decisions and their order.
- Requires experience to navigate this complexity effectively.

---

## Referenced resources (cited by Di Bello)

- Kent Beck — *Implementation Patterns* (book).
- Kent Beck — *Test Desiderata* (article on test properties).
- Sandro Mancuso — TDD video series (alternative-approach comparison).
- Additional course reviews linked at the article conclusion (not
  enumerated in this extraction).

---

## Notes for the human

- This is a *secondary source* — Di Bello's structured notes on
  Beck's course, not Beck's primary material. If the wiki later wants
  primary sources, candidates include Beck's *Test-Driven Development:
  By Example* (book), the Pragmatic Screencasts series itself, and
  *Test Desiderata*.
- The article is short (notes form) and the outline above captures
  its structure. No long verbatim passages were extracted; promoting
  to `sources/raw/docs/` is optional rather than load-bearing.
- The summary at `sources/summaries/tdd_course_notes_kent_beck_pierodibello.md`
  is written against this outline. If you discard the staging file,
  update the summary's `sources:` frontmatter accordingly.

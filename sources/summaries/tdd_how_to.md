---
id: summary-tdd-how-to
title: TDD How-To (Beck + Tidy First, agent-prompt-form codification)
kind: descriptive
status: accepted
scope: global
created: 2026-05-29
updated: 2026-05-29
confidence: high
sources:
  - sources/raw/docs/TDD_HOW_TO.md
  - https://gist.github.com/spilist/8bbf75568c0214083e4d0fbbc1f8a09c
provenance:
  upstream_author: spilist (GitHub)
  upstream_url: https://gist.github.com/spilist/8bbf75568c0214083e4d0fbbc1f8a09c
  upstream_kind: public-gist
  introduced_to_wiki_by: user
  confirmed_at: 2026-05-29
tags: [tdd, tidy-first, kent-beck, refactoring, commit-discipline, structural-vs-behavioral, agent-prompt, scala, fp, third-party-codification]
---

## Source

`sources/raw/docs/TDD_HOW_TO.md` is a prescriptive, agent-prompt-form
codification of Kent Beck's Test-Driven Development methodology fused
with Beck's later **Tidy First** approach. The document is written in
the second person ("You are a senior software engineer who follows
Kent Beck's TDD and Tidy First principles") and structured for use as
an instruction set fed to a coding agent — references to a `plan.md`
test list and a "When I say 'go'" trigger phrase identify it as an
agentic workflow prompt.

**Provenance (confirmed 2026-05-29)**: copied from
`https://gist.github.com/spilist/8bbf75568c0214083e4d0fbbc1f8a09c` —
public gist authored by GitHub user **spilist**. The user introduced
the text into this wiki by placing it in `sources/raw/docs/`; the
content itself is third-party. Treat it as a community codification
of Beck + Tidy First, not as Beck's own writing. Beck's primary
sources (*Test-Driven Development: By Example*, *Implementation
Patterns*, *Tidy First*) remain authoritative for any normative
claim made against the methodology.

A short Scala-specific coda at the end ("Prefer functional
programming style over imperative style in Scala") anchors the
document to our stack.

## Comparison with the other TDD source already in the wiki

| Concern | Di Bello notes (secondary, Beck screencast) | TDD_HOW_TO (canonical Beck + Tidy First) |
|---------|---------------------------------------------|------------------------------------------|
| Red → Green → Refactor | Theme 9 (rhythm) | Core principle, stated upfront |
| Simplest failing test first | Implicit | Explicit |
| Minimum code to pass | Theme 6 (Fake It) | "Just enough" / "simplest solution that could possibly work" — closer to **Obvious Implementation** |
| Refactor only on green | Theme 5 | Explicit rule |
| Tidy First (structural vs behavioural) | **Absent** | **Centrepiece** |
| Commit discipline | **Absent** | All tests green + zero warnings + single logical unit + message tagged structural/behavioural |
| Four rules of simple design (Beck) | Implicit | "Eliminate duplication, express intent, explicit deps, single responsibility, minimal side effects, simplest possible" — direct enumeration |
| Refactoring: one named change at a time | Theme 12 (problem slicing) | "Use established refactoring patterns with their proper names; one at a time; run tests after each" |
| Test naming narrates behaviour | Theme 2 | "shouldSumTwoPositiveNumbers" example |
| Run all tests each cycle | **Absent** | "Always run all the tests (except long-running tests)" |
| FP / Scala coda | **Absent** | Present (one line, no expansion) |

## Codified rules

### Cycle

- **Red → Green → Refactor**, in that order. No refactoring on red.
- Write the simplest failing test first.
- Implement the minimum code that turns the test green. *No more.*
- Once green, decide whether refactoring is needed.

### Tidy First — structural vs behavioural changes

Every code change is exactly one of:

| Type | Examples |
|------|----------|
| Structural | renaming, extracting methods, moving code, reorganisation |
| Behavioural | adding or modifying actual functionality |

Rules:

1. **Never mix** structural and behavioural changes in the same
   commit.
2. **Structural first** when both are needed.
3. **Verify** structural changes are behaviour-preserving by running
   tests before and after.

This is the load-bearing addition over Di Bello's notes — Tidy First
gives the *commit unit* a clear type, and the type goes in the commit
message.

### Commit discipline

A commit is admissible only when **all** of:

1. All tests pass.
2. All compiler / linter warnings are resolved.
3. The change is a single logical unit of work.
4. The commit message states whether it is **structural** or
   **behavioural**.

Prefer small, frequent commits.

### Code-quality rules (Beck's four rules of simple design, expanded)

- Eliminate duplication ruthlessly.
- Express intent clearly through naming and structure.
- Make dependencies explicit.
- Keep methods small and focused on a single responsibility.
- Minimise state and side effects.
- Use the simplest solution that could possibly work.

### Refactoring guidelines

- Refactor only on green.
- Use established refactoring patterns *by name* (Fowler catalogue
  implied).
- One refactoring change at a time.
- Run tests after each step.
- Prioritise refactorings that remove duplication or improve clarity.

### Workflow as an agent instruction

The opening line — *"Always follow the instructions in plan.md. When
I say 'go', find the next unmarked test in plan.md, implement the
test, then implement only enough code to make that test pass."* —
ties the methodology to a concrete artefact (`plan.md`) and a concrete
trigger word (`go`). This is the agent-prompt-shape of Beck's "test
list" (Di Bello Theme 1). The plan file is the durable test list; the
"go" command advances one bullet at a time.

## Effect on prior wiki state

### Promotion-threshold status

POLICY requires either a second corroborating source or a project
synthesis before a candidate pattern is promoted. With this ingest:

- We now hold **two** TDD sources:
  - [[sources/summaries/tdd_course_notes_kent_beck_pierodibello]] (secondary, screencast-derived)
  - This page (canonical Beck + Tidy First, prescriptive)
- The two sources agree on: red/green/refactor, simplest-first,
  refactor-only-on-green, intent-revealing names, narrative test
  ordering, behaviour-focused test names, small frequent commits.
- They diverge on / differ in coverage:
  - This source codifies **Tidy First** (structural vs behavioural)
    and **commit discipline**, neither present in Di Bello.
  - Di Bello has **test economics** (Theme 10) and the
    **Beck-vs-Mancuso style axis** (Theme 11), neither present here.

The promotion threshold for a `tech/patterns/tdd-rhythm` page is met
on the *core cycle* (red / green / refactor + simplest-first +
refactor-only-on-green + small commits). It is **not yet met** for
themes that appear in only one source — those still need a second
source or a project synthesis.

### Reconciliation with DRIFT-014 / DRIFT-015

(Manual-review flags raised against the Di Bello summary on
2026-05-29. See [[meta/drift]].)

- **DRIFT-014a** (TDD-as-if-you-meant-it misattributed to Beck) —
  *reinforced*. This source describes Beck's actual workflow as
  "implement the minimum code", not "expand inside the test." The
  misattribution flag stands.
- **DRIFT-014b** (private-method scaffolding not Beck) — *reinforced*.
  This source, claiming to codify Beck, does not mention
  private-method tests at all.
- **DRIFT-014c** (end-to-end-first overgeneralised) — *reinforced*.
  This source says "small increment of functionality", not "thin
  end-to-end slice." Confirms Beck's canonical move is inside-out.
- **DRIFT-014d** (Fake It alone; Triangulation + Obvious
  Implementation missing) — *partly answered*. "Just enough" / "the
  simplest solution that could possibly work" is **Obvious
  Implementation** under another name. Triangulation still absent
  here.
- **DRIFT-014e** (Beck-vs-Mancuso peers) — *unchanged*. This source
  is silent on Mancuso.
- **DRIFT-014f** (*Test Desiderata* underused) — *unchanged*. This
  source also does not cite *Test Desiderata*.

- **DRIFT-015a** (OO refactoring vocabulary) — *partly mitigated*.
  This source uses "methods" and "extract methods" (OO vocabulary)
  but adds "Minimise state and side effects" + a Scala / FP coda. The
  flag is reduced but not closed: the vocabulary remains OO, the FP
  posture is asserted only as one line of guidance.
- **DRIFT-015b** (deterministic isolation a non-problem under purity)
  — *partly mitigated*. This source doesn't dwell on isolation; the
  "minimise side effects" rule already moves toward purity.
- **DRIFT-015c** (design happens during refactoring — missing
  type-first) — *unchanged*. This source says "refactor only after
  tests are passing" without naming any type-level design stage. The
  gap remains.
- **DRIFT-015d** (Fake It vs type-driven derivation) — *partly
  mitigated*. "Simplest solution that could possibly work" is
  compatible with type-driven derivation.
- **DRIFT-015e** (mocks vs fakes-over-mocks) — *unchanged*. This
  source is silent on mocks.
- **DRIFT-015f** (private-method encapsulation) — *partly mitigated
  by silence*. Neither this source nor canonical Beck endorses
  private-method tests; the Di Bello summary's "scaffolding then
  delete" framing is the outlier.
- **DRIFT-015g** (error handling at type level) — *unchanged*. This
  source does not address error handling.
- **DRIFT-015h** (property-based / law-based testing missing) —
  *unchanged*. This source does not mention property-based testing.
  A third source — or a project synthesis citing the
  `sourceline-manager` monoid-law tests — would be needed to add PBT
  as a peer to example-based TDD.

### What this source *does not* answer (post-provenance resolution)

- ~~Whether the agent-prompt-form codification was authored by the
  user or copied from an external prompt template.~~ **Resolved
  2026-05-29**: copied from a public gist by user `spilist`. See
  the §Source provenance block.
- Whether `plan.md` (the test list file) is a wiki concept or a
  per-project file. If the former, it would deserve a schema entry.
- How Tidy First interacts with the
  [[feedback_hg_repo_commit_policy]] (unsigned commits, no
  Co-Authored-By, author tigidar) — Tidy First's structural /
  behavioural tag would join the existing commit-policy rules.
  Addressed in [[tech/decisions/tidy-first-commits]] §"How this
  interacts with the existing repo-commit policy".

## Promotion candidates — status as of 2026-05-29

All four candidates were drafted 2026-05-29 per user direction
("promote all"); the user explicitly waived POLICY's
"second corroborating source" requirement for the three
single-sourced candidates. Drafts written as `status: draft`
pending user acceptance pass.

| Layer-2 page | Sources backing it | Lifecycle status |
|--------------|---------------------|------------------|
| [[tech/patterns/tdd-rhythm]] (red/green/refactor + simplest-first + small commits + refactor-only-on-green, with FP-stack Stage 0 prepend) | Di Bello + TDD_HOW_TO | **draft** — corroborated cycle core |
| [[tech/decisions/tidy-first-commits]] (structural vs behavioural separation, commit message tagging) | TDD_HOW_TO only | **draft** — single-sourced (user-waived) |
| [[tech/patterns/test-economics]] (cost / benefit per test and per skipped test) | Di Bello only | **draft** — single-sourced (user-waived) |
| [[tech/patterns/symmetric-refactoring]] (symmetry as refactoring signal) | Di Bello only | **draft** — single-sourced (user-waived) |

A future `tech/patterns/tdd-rhythm` draft must address DRIFT-015c
(prepend type-first), DRIFT-015h (PBT as peer), and DRIFT-014a
(Braithwaite split-out) before reaching `accepted`.

## Links

- [[sources/raw/docs/TDD_HOW_TO.md]]
- [[sources/summaries/tdd_course_notes_kent_beck_pierodibello]] — the other TDD source
- [[meta/drift]] §DRIFT-014, §DRIFT-015 — manual-review flags this ingest partially reconciles
- [[tech/patterns/functional-domain-design]] — the FP posture this TDD ruleset's Scala coda points at
- [[projects/sourceline-manager]] — already practises monoid-law testing (relevant to the DRIFT-015h gap)

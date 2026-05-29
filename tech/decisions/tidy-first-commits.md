---
id: tidy-first-commits
title: Tidy First — structural and behavioural commits never mix
kind: normative
status: draft
scope: global
created: 2026-05-29
updated: 2026-05-29
confidence: medium
applies_to:
  languages: [scala, scala-native, scala-js]
  domains: [any]
  excludes: []
used_by: []
sources:
  - sources/summaries/tdd_how_to.md
supersedes: []
superseded_by: null
---

## Context

Kent Beck's *Tidy First* approach (2023) separates code changes into
two types and forbids mixing them in a single commit:

| Type | What it does |
|------|--------------|
| **Structural** | Rearranges code without changing behaviour — renaming, extracting methods/functions, moving code, reorganising files, deleting dead code |
| **Behavioural** | Adds or modifies what the code actually does — new tests turning green, bug fixes, feature additions |

The problem the rule solves: a mixed commit hides two questions
behind one diff. Reviewers can't tell which lines changed *what the
code does* and which lines just *moved*. Bisecting a regression
across mixed commits is correspondingly harder — you cannot tell
whether a structural step accidentally changed behaviour, because
the same commit also changed behaviour deliberately.

The rule is also the load-bearing precondition for safe automated
refactoring: a structural commit that passes the same tests as its
parent is *by definition* behaviour-preserving. The discipline turns
the commit graph into a trustable record of behavioural change.

This page is single-sourced
([[sources/summaries/tdd_how_to]]) and a `draft` per `POLICY.md`. A
second corroborating source (Beck's *Tidy First* book) or a project
synthesis is needed for promotion to `accepted`.

## Decision

Every commit is exactly one of: **structural** or **behavioural**.
No commit mixes the two.

### Rules

1. **Tag the commit message** with its type.
   - `tidy: rename FooBar to FooQux` — structural
   - `feat: parse Authorization header` — behavioural
   - `fix: handle empty headers` — behavioural
   - `refactor: extract sameCurrency guard` — structural

   The existing conventional-commit prefixes
   ([[devtools:conventional-commits]] skill) already distinguish
   `feat` / `fix` (behavioural) from `refactor` / `tidy`
   (structural). This decision codifies the rule, not the
   vocabulary.

2. **Structural commits run the test suite before and after, with
   identical results.** A structural commit that turns a test red
   is *by construction* not structural — revert and re-categorise.

3. **Structural changes go first** when both are needed. If you can
   only make the behavioural change easily after a rename, do the
   rename in its own commit, push or stage it, then do the
   behavioural change in a second commit.

4. **No half-finished structural changes shipped with behavioural
   ones.** If you start extracting a helper and the extraction is
   only half-done when the feature lands, finish the extraction in
   its own commit before the behavioural one.

5. **Admissible commit predicates** (from
   [[sources/summaries/tdd_how_to]] §Commit discipline):
   - All tests pass.
   - All compiler / linter warnings resolved.
   - Single logical unit of work.
   - Commit message states whether structural or behavioural.

### How this interacts with the existing repo-commit policy

[[feedback_hg_repo_commit_policy]] already sets the *form* of
commits in `/p/hg/*` and `/p/v42/toolbox/`: unsigned, no
Co-Authored-By, author `tigidar`. This decision adds the *type*
discipline on top of the form. The two are orthogonal — the form
rules apply to every commit; the type rule says every commit must
be exactly one type.

## Consequences

### Positive

- **Reviewable diffs**: a structural diff and a behavioural diff are
  *visually distinguishable* — one renames identifiers across many
  files, the other changes a small number of expressions.
- **Trustable `git bisect`**: a regression caught by bisect lands on
  a behavioural commit, not on a structural one that "shouldn't
  have changed behaviour" but did.
- **Safer revert**: undoing a behavioural change does not require
  also undoing the rename it depended on.
- **Aligned with TDD Stage 4**: refactor-on-green produces
  structural commits by construction. See [[tech/patterns/tdd-rhythm]]
  §Stage 4.

### Negative

- More commits per feature than the "one big commit per feature"
  habit. Mitigated by the small-frequent-commits practice already
  endorsed by [[sources/summaries/tdd_how_to]].
- Requires the rename-and-then-change workflow to be muscle memory.
  When deadline pressure is high, the temptation to mix is high.
  The cost of mixing later is higher than the cost of separating
  now — but the cost of mixing is not paid immediately, which is
  why this needs to be a rule and not a guideline.

### Implications for our stack

- Mill build files (`build.mill`, `package.mill`) follow the same
  rule. Bumping a version in `Dependencies.mill` is *behavioural*
  (changes what gets resolved). Renaming a module is *structural*.
- ScalaJS/Scala Native splits often start as structural rearrangement
  (move shared code to `src/`, set up `Cross[]`) followed by
  behavioural work. The structural commit lands first, tests stay
  green throughout (see
  [[tech/guides/mill-cross-platform]] §Pitfalls for the empty-jar
  failure mode that this rule's "tests pass before and after" would
  have caught).

## Alternatives Considered

- **Mix freely and trust the diff** — rejected. Standard practice
  in many teams and the rule we are deviating from. Hides type
  information in commit history; defeats `git bisect`.
- **Type-tag only behavioural commits, leave structural untagged**
  — rejected. Asymmetric tagging makes it ambiguous what an
  untagged commit is. The two-way tag is cheap and unambiguous.
- **Type-tag in the diff, not the message** — rejected as
  ergonomically worse. Reviewers see the message before the diff.

## Code Example

### Behavioural-only commit

```
feat: addition between Money values returns Either[AddError, Money]

Money.+ now returns Either to encode the currency-mismatch case.
The error type is added to the public surface (AddError sealed sum).

Test list advanced:
- [x] adds two amounts in the same currency
- [x] mismatched currencies fail with CurrencyMismatch
```

The diff: signature change on `+`, new `AddError` enum, new tests.
No renames, no extractions.

### Structural-only commit

```
tidy: extract sameCurrency guard helper

Both Money.+ and the upcoming Money.- need an identical
"currencies match, return mismatch error otherwise" guard. Extracted
to a private helper. Behaviour unchanged — same tests pass.
```

The diff: new private function, two call sites updated.
No new tests; no test failures introduced.

### What this rule *forbids*

A diff that both extracts the `sameCurrency` guard *and* adds the
new `Money.-` operator is illegal under this decision. Split it:
structural commit first (extract guard, only `+` uses it),
behavioural commit second (add `-`, both use it).

## Links

- [[sources/summaries/tdd_how_to]]
- [[tech/patterns/tdd-rhythm]] — Stage 3 produces behavioural commits, Stage 4 produces structural ones
- [[tech/patterns/test-economics]] — the "tests pass before and after" precondition has a non-trivial cost; test-economics tells us when to invest in the underlying test
- `devtools:conventional-commits` — the vocabulary this decision rides on
- [[feedback_hg_repo_commit_policy]] — form rules; this decision adds type rules on top

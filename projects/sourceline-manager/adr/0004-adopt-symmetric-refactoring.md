---
id: sourceline-manager-adr-0004
title: Adopt Symmetric Refactoring (symmetry is the signal an algebra wants to be born)
kind: normative
status: accepted
project: sourceline-manager
created: 2026-05-29
compliance:
  adopts:
    - tech/patterns/symmetric-refactoring.md
  exceptions: []
  deviations: []
  ignores: []
supersedes: []
---

## Context

[[tech/patterns/symmetric-refactoring]] was promoted from `draft` to
`accepted` (`confidence: high`) on 2026-05-29 on the strength of this
codebase's evidence. The synthesis
[[projects/sourceline-manager/syntheses/monoid-laws-as-pbt-evidence]]
is the page's `promoted_from`.

The library is in scope (Scala / Scala.js / Scala Native, any
domain). The page's decision-tree moves 1 (*preserve symmetric
duplication*) and 2 (*name the algebra*) are realised directly in
the operator catalogue. Move 3 (*reject asymmetric extraction*) is
realised by absence — the codebase carries no flag-bearing helper
that collapses a symmetric pair.

## Decision

Adopt `tech/patterns/symmetric-refactoring.md` unconditionally. The
following symmetric pairs are part of the library's public surface
and must be preserved (not flattened into a flagged helper):

### Monoid layer

| Symmetric pair | Algebra name |
|----------------|--------------|
| `++` / `|+|` / `combine` | Monoid combine (three aliases by intent) |
| `:+` / `+:` | Postfix / prefix insertion |
| `appendLine` / `prependLine` | Same algebra lifted to lines |
| `appendLines` / `prependLines` | Vector form of the same |
| `appendToken` / `prependTokenToLast` | Token-level form |
| `appendAll` / `prependAll` | Vector-of-lines form |

### Primitive layer (added 2026-05-29 with the SourceLine primitives)

| Symmetric pair | Algebra name |
|----------------|--------------|
| `take` / `drop` | Slicing duality (`take(n) ++ drop(n) == self`) |
| `takeWhile` / `dropWhile` | Predicate-driven slicing duality |
| `indexWhere` / `lastIndexWhere` | Directional search |
| `startsWith` / `endsWith` | Directional pattern match |

The decision-tree moves operate at both layers:

- **Move 1 (preserve duplication)**: the three aliases on combine
  (`++`, `|+|`, `combine`) are not abstracted away into one method
  with a "style" parameter — each name carries different
  connotations (symbolic / typeclass-suggestive / English) and the
  cost of three two-line definitions is repaid by readability at
  every call site.
- **Move 2 (name the algebra)**: each pair has a stated algebra
  (Monoid, Slicing Duality, Directional Search). When a future
  primitive lands, the test "does this fit an existing algebra?"
  is asked before "is this orthogonal?".
- **Move 3 (reject asymmetric extraction)**: no `appendOrPrepend(Side,
  …)` helper exists. The library would rather carry the duplication
  than carry the flag.

Renderer and search functions that are *inherently* asymmetric
(e.g. `render`, `indexOfSlice`) are not affected by this decision —
they have no symmetric partner to preserve.

## Consequences

- Adding a new operator that fits an existing symmetric pair
  requires landing both halves of the pair, even if only one is
  immediately needed by callers. (E.g. landing `cohereFirst` would
  oblige landing `cohereLast`.)
- The operator catalogue's growth is bounded by the algebras it
  names. New algebras require a synthesis-level argument; new
  members of an existing algebra do not.
- Refactor reviews use "did the symmetry survive?" as a first-pass
  signal. A diff that collapses a pair into a flagged helper is a
  red flag, regardless of LOC savings.
- New primitive families (e.g. a future regex / pattern layer)
  inherit the same discipline: symmetric pairs over `_` /
  `Reverse[_]` axes, preserved.

## Alternatives Considered

- **Collapse aliases into one canonical method** — rejected; loses
  the call-site readability gain that motivates the three aliases.
- **Flag-bearing `appendOrPrepend(side, …)` helper** — rejected;
  the pattern's move 3 directly prohibits it. The flag would
  reintroduce a runtime branch where the original methods carry the
  decision at the type level (method name).
- **Adopt only at the monoid layer, ignore at the primitive layer** —
  rejected as inconsistent; the same discipline applied to monoids
  applies to slicing, search, and pattern-match primitives.
- **Ignore** — not admissible; the library is the page's
  `promoted_from` evidence and the decision-tree moves are
  realised today.
- **Deviate** — none identified. The pattern holds unmodified.

## Links

- [[tech/patterns/symmetric-refactoring]]
- [[projects/sourceline-manager/syntheses/monoid-laws-as-pbt-evidence]] — promotion evidence
- [[projects/sourceline-manager/adr/0001-adopt-functional-domain-design]] — algebra-naming endgame is FDD
- [[projects/sourceline-manager/adr/0003-adopt-tdd-rhythm]] — Stage 4 carries this discipline
- `/p/hg/sourceline-manager/slm/src/slm/SourceLine.scala`
- `/p/hg/sourceline-manager/slm/src/slm/SourceFile.scala`
- `/p/hg/sourceline-manager/slm/test/src/slm/SourceLinePrimitivesLawsSpec.scala`

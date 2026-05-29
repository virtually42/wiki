---
id: dependency-manager-adr-0003
title: Adopt TDD Rhythm (type-first, red/green/refactor)
kind: normative
status: accepted
project: dependency-manager
created: 2026-05-29
compliance:
  adopts:
    - tech/patterns/tdd-rhythm.md
  exceptions:
    - page: tech/patterns/tdd-rhythm.md
      rationale: |
        Stage 2 (red, both forms) is currently realised in its
        **example-based** form only. There are no property-based /
        `forAll` law tests yet — the catalog algebra hasn't grown
        the symmetric operators (`merge`, `diff`) where
        `forAll`-quantified laws would carry their weight, and the
        Coord round-trip is example-tested across all three
        cross-kinds rather than `forAll`-generated. The exception
        will close when those operators land.
      risk: low
  deviations: []
  ignores: []
supersedes: []
---

## Context

[[tech/patterns/tdd-rhythm]] (accepted 2026-05-29, `confidence:
high`, `scope: global`, `applies_to.languages: [scala,
scala-native, scala-js]`) is in scope for dm.

When this project was first ingested (2026-05-29 morning) the
code was a v1 scaffold with two trivial smoke tests
(`MainSmokeTest`). Writing a TDD-rhythm adoption ADR on that
evidence would have been claim-without-substance.

By end of 2026-05-29 four implementation sessions had added
**52 tests across 8 specs**, every single one written
red-then-green. The pattern's five stages are all visible on
disk:

### Stage 0 — type / algebra first

Every domain type came before its tests:

- `CrossKind` enum, then `CoordSpec` started writing tests
  against `Coord.parse`.
- `Catalog` case class, then `CatalogBuilderSpec` exercised
  `fromProjects`.
- `Mill.Cwd` and `Mill.Invocation` case classes, then `MillSpec`
  asserted `renderArgs` shapes.

The algebra-first ordering is preserved in the wiki log entries
(`[2026-05-29] implement` entries cite "added types T, then
spec S"). No type was retro-fitted into a test that already
expected it.

### Stage 1 — test list

Each `test("...")` name reads as a sentence about behaviour, not
about implementation:

- `"parse scala-cross coord"` — a behaviour the user sees.
- `"render round-trips for all cross kinds"` — an algebraic
  property.
- `"deterministic ordering regardless of input order"` — a
  catalog-builder guarantee.
- `"toml reader rejects malformed module string"` — an error
  contract.
- `"regen writes only library handles a project actually uses"`
  — a `selectFor` contract.
- `"verify returns 0 when every project's Dependencies.mill
  matches catalog"` — a CI-mode contract.

The test files function as readable test lists.

### Stage 2 — red, example-based form only (exception declared)

`Stage 2 - law-based` is **not yet** realised in dm. The
exception above records this honestly: the catalog algebra hasn't
grown the symmetric operators (`merge` / `diff` / `union`) where
`forAll`-quantified laws carry their weight, and the Coord
round-trip is example-tested across all three cross-kinds rather
than `forAll`-generated. PBT lands when those operators land.

Example-based red-then-green is the universal form across all 8
specs: every test was written failing first, then production code
was added to flip it green. The refactor-on-green moves
(`MillQuery` reshape today, `partitionMap` swap last week) ran
against the existing green suite — no test ever stayed red across
a session boundary.

### Stage 3 — green, minimal step

Every spec runs in under a second. The slowest is `RegenSpec`
(0.144s for the multi-project case) because it touches the file
system; the next-slowest is `ReadersSpec` (0.037s, full round-trip
via tmp files). Pure-data specs (`CoordSpec`,
`CatalogBuilderSpec`, `WritersSpec`, `MillSpec`,
`DependenciesMillWriterSpec`) total under 0.1s each.

### Stage 4 — refactor on green, symmetry-aware

Two refactor moves on disk:

- **The `partitionMap` swap.** `Extract.extractCoords` initially
  destructured `partitionMap(Coord.parse)` as `(parsed, failed)`,
  which Scala 3 inferred to `Vector[String]` and rejected. Fix
  was to swap to `(failed, parsed)` (Left first, Right second).
  Pure refactor; spec stayed green.
- **The `MillQuery` reshape.** `MillQuery` initially wrapped
  `os.proc` directly. The refactor (this morning) routed
  everything through the new `dm.mill.Mill` DSL and switched the
  return type from `Vector[A]` (throwing) to `Either[String, A]`.
  All callers (`Extract`, `Resolve`) were updated; the existing
  suite stayed green throughout. No test had to change to
  describe the new contract; the contract was the same, the
  implementation moved.

Symmetry-aware extension: the Writer/Reader pair was added as a
pair (`TomlWriter` ↔ `TomlReader`, `YamlWriter` ↔ `YamlReader`),
covered by round-trip tests in `ReadersSpec`, in the same
session — symmetry preserved at the test surface.

## Decision

Adopt [[tech/patterns/tdd-rhythm]] with one exception (Stage 2
law-based, declared above and bounded — closes when the catalog
algebra grows symmetric operators).

All future code in dm targets the same rhythm:

- New types start as `enum` / `case class` definitions, then a
  spec is added with at least one failing test against the type's
  contract.
- New operators get example-based tests at minimum; when an
  operator participates in a symmetric pair (current candidate:
  `Reader` ↔ `Writer` already paired; future: `merge` / `diff`
  on `Catalog`), at least one law-based property test joins the
  example-based tests.
- Refactors run against a green suite. A red suite during a
  refactor is a stop-and-fix signal, not a tracked TODO.

## Consequences

- The exception on Stage 2 law-based is **bounded** — it closes
  when the algebra grows symmetric operators that would carry
  `forAll` weight. Until then, dm is honestly half-realising the
  pattern, and the wiki records that honestly rather than
  claiming full adoption.
- The test pace (52 tests in four implementation sessions, all
  red-then-green) is the rhythm itself. Any future session that
  ships production code without ≥1 prior failing test should be
  flagged in the project log as a deviation.
- The refactor-on-green discipline is now load-bearing for
  collaboration: a future session may add a Native target, an
  alternate process runner, or a Kyo-effect wrapper around
  `Mill.Invocation.exec`. Each of those is a refactor (or
  refactor + extension) the existing green suite must continue
  to support.

## Alternatives Considered

- **Adopt unconditionally, ignore the PBT gap.** Rejected: would
  overclaim. Sourceline-manager carries `MonoidLawsSuite[A]` and
  46 quantified property assertions — that's the bar the global
  pattern was raised to. dm hasn't reached it; the exception is
  the honest label.
- **Defer the ADR until PBT lands.** Rejected: the
  example-based-only realisation is real on-disk evidence of
  Stages 0 / 1 / 3 / 4; deferring would leave dm flagged as
  missing-declaration in drift while the bulk of the pattern is
  already realised.
- **Mark Stage 2 as a deviation rather than an exception.**
  Considered. Rejected because deviation implies a violation in
  flight; what we have is a bounded gap with a clear closing
  condition. Exception with low risk is the right label per
  POLICY.

## Links

- [[tech/patterns/tdd-rhythm]]
- [[sources/summaries/dependency-manager]]
- [[projects/dependency-manager/log]] — the four `[2026-05-29] implement` entries are the rhythm itself
- [[projects/sourceline-manager/adr/0003-adopt-tdd-rhythm]] — sibling adoption (with full PBT coverage)
- `/p/hg/dependency-manager/dm/test/src/` — the 8 specs cited above

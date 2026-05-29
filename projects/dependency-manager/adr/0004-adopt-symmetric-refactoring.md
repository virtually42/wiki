---
id: dependency-manager-adr-0004
title: Adopt Symmetric Refactoring (parallel-module form)
kind: normative
status: accepted
project: dependency-manager
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

[[tech/patterns/symmetric-refactoring]] (accepted 2026-05-29,
`confidence: high`, `scope: global`) is in scope for dm.

Where sourceline-manager realises the pattern at the **operator**
layer (`++` / `:+` / `+:` / `appendLine` / `prependLine` etc.),
dm realises it at the **module / file** layer. The decision-tree
moves are the same; the surface where symmetry is preserved is
different.

### Reader / Writer dual pairs

Three Writer modules ship with their dual Reader (or are about to):

| Writer | Reader | Algebra name |
|--------|--------|--------------|
| `TomlWriter.render(Catalog) → String` | `TomlReader.parse(String) → Either[String, Vector[(handle, Library)]]` | Catalog-libraries-to-TOML |
| `YamlWriter.render(Catalog) → String` | `YamlReader.parse(String) → Either[String, Vector[(name, ProjectInfo)]]` | Catalog-projects-to-YAML |
| `DependenciesMillWriter.render(Vector[(handle, Library)]) → String` | (about to land with `dm promote`) | Project-deps-to-Mill |

The first two pairs round-trip in `ReadersSpec`:

```scala
test("toml reader round-trips libraries") {
  val out = TomlWriter.render(sample)
  val back = TomlReader.parse(out)
  assertEquals(back, Right(sample.libraries))
}

test("catalog reader full round-trip via writers + tmp files") {
  os.write(tmp / "libs.versions.toml", TomlWriter.render(sample))
  os.write(tmp / "projects.yml",       YamlWriter.render(sample))
  val back = CatalogReader.read(tmp / "libs.versions.toml", tmp / "projects.yml")
  assertEquals(back, Right(sample))
}
```

The round-trip *is* the symmetric-pair contract: the algebra named
"Catalog-to-TOML" is whatever set of `(Writer, Reader)` makes that
test pass.

### Regen / Verify dual pair

`dm regen` and `dm verify` form a higher-level symmetric pair:

| Module | Direction | Output |
|--------|-----------|--------|
| `Regen.run` | catalog → on-disk Dependencies.mill | side effect (writes file) |
| `Verify.run` | catalog vs on-disk Dependencies.mill | difference report + exit code |

Both consume the same `Catalog` and the same project layout. The
contract is *Regen produces files Verify recognises as
in-sync* — tested end-to-end via the `dm extract` →
`dm regen` → `dm verify` sequence (currently 3 projects, 12
libraries, all reporting OK after each refresh).

### Pattern-on-pattern: the Writer/Reader pair INSIDE the Regen/Verify pair

`Verify` re-renders the catalog into `DependenciesMillWriter`
output and compares against the on-disk file — the inner
Writer/Reader pair (here, Writer-and-byte-comparison, the Reader
being trivial: `os.read`) becomes the engine of the outer
Regen/Verify pair. Move 2 (*name the algebra*) applies at both
nesting levels.

## Decision

Adopt [[tech/patterns/symmetric-refactoring]] unconditionally.
The following symmetric pairs are part of dm's public surface
and must be preserved (not collapsed into a flag-bearing helper
or an asymmetric "one-direction-only" alternative):

### Format pairs

- `TomlWriter` / `TomlReader` — catalog libraries ↔ TOML.
- `YamlWriter` / `YamlReader` — catalog projects ↔ YAML.
- `DependenciesMillWriter` / *promote-reader* (landing with
  `dm promote`) — project deps ↔ Mill.
- `CatalogReader` (and its dual `Catalog → (toml+yml on disk)`
  via the two Writers) — the full Catalog round-trip.

### Verb pairs

- `dm regen` / `dm verify` — catalog → downstream / downstream
  compared to catalog.
- `dm extract` / `dm promote` (landing alongside this ADR) —
  bootstrap catalog from sources / port a downstream edit back
  to the catalog.

### Move discipline

- **Move 1 (preserve duplication)**: every new on-disk format
  added to dm grows as a *pair* — a Writer and a Reader added in
  the same session, covered by round-trip tests. The
  Dependencies.mill format is the standing exception (Writer
  shipped before the Reader, with the Reader landing as part of
  `dm promote`), bounded by that one verb implementation.
- **Move 2 (name the algebra)**: each format pair is named after
  the format, not after one direction (e.g.
  `DependenciesMillWriter` — Writer-as-direction is in the name,
  but it's parallel to `DependenciesMillReader`, not to an
  asymmetric "DepsBuilder"). The verb pairs (`regen` / `verify`,
  `extract` / `promote`) are similarly named after their roles
  in the catalog loop, not after a single direction.
- **Move 3 (reject asymmetric extraction)**: no
  "convenience helper" may collapse a writer/reader pair into a
  parameterised single function. The forces that justify each
  direction (TOML emitter vs TOML walker, catalog→Mill render vs
  Mill→catalog parse) are different enough that flattening loses
  information.

## Consequences

- dm is the **second project** to adopt this pattern after
  [[projects/sourceline-manager/adr/0004-adopt-symmetric-refactoring]],
  with a distinct realisation (parallel-module form rather than
  operator-layer form). The orthogonal-shape spread is intended
  evidence that the pattern is broad: it applies at the operator
  layer, the module layer, and the verb layer simultaneously.
- The wiki has a standing candidate
  ([[tech/patterns/symmetric-refactoring]] Open Questions §):
  promote a separate page for *parallel-module* form once a
  second project realises it independently. dm is now that
  second project; whether the page splits is a wiki-side
  question for a future synthesis, not a code change.
- The Regen / Verify symmetry directly enables CI integration:
  `dm verify` is the contrapositive proof that `dm regen` did
  what the catalog says, run as a check on every PR. Without
  the symmetric structure, CI would have to re-derive the
  expected content from scratch each time.
- The Extract / Promote pair completes the round-trip
  diagnostically. Any sequence of `dm extract` followed by
  manual catalog edits followed by `dm regen` is checkable by
  `dm verify`; any sequence of human hand-edits to downstream
  Mill files is portable back via `dm promote`.

## Alternatives Considered

- **Adopt at operator layer only (decline the parallel-module
  form).** Rejected: would miss the most prominent symmetric
  structure in dm. The catalog has no `++` / `|+|` operator
  layer to which the operator-only form applies; the Reader /
  Writer / Regen / Verify pairs are where symmetry actually
  lives.
- **Defer until `dm promote` exists and the
  DependenciesMillReader half is on disk.** Rejected: the
  Writer / Reader pairs for TOML and YAML are already on disk
  with round-trip tests; the third pair is in flight and
  bounded by one verb implementation. Adopting now and
  recording the bounded gap as a "Move 1 exception" is more
  honest than waiting.
- **Promote the parallel-module form to its own tech page now.**
  Rejected for this ADR — that's a wiki-side question requiring
  the synthesis flagged in [[tech/patterns/symmetric-refactoring]]
  Open Questions §. This ADR records dm's stance; the synthesis
  is the human's call.

## Links

- [[tech/patterns/symmetric-refactoring]]
- [[sources/summaries/dependency-manager]]
- [[projects/dependency-manager/log]] — the `[2026-05-29] implement` entries trace each pair landing as a pair
- [[projects/sourceline-manager/adr/0004-adopt-symmetric-refactoring]] — sibling adoption (operator-layer form)
- `/p/hg/dependency-manager/dm/src/catalog/{Toml,Yaml,Catalog}{Reader,Writer}.scala` — format-pair evidence
- `/p/hg/dependency-manager/dm/src/{Regen,Verify}.scala` — verb-pair evidence
- `/p/hg/dependency-manager/dm/test/src/catalog/ReadersSpec.scala` — round-trip tests

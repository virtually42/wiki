---
id: dependency-manager-adr-0002
title: Adopt Functional Domain Design (declarative encoding)
kind: normative
status: accepted
project: dependency-manager
created: 2026-05-29
compliance:
  adopts:
    - tech/patterns/functional-domain-design.md
  exceptions: []
  deviations: []
  ignores: []
supersedes: []
---

## Context

[[tech/patterns/functional-domain-design]] (accepted 2026-05-28,
`scope: global`, `applies_to.languages: [scala, scala-native,
scala-js]`) is in scope for dm — the project is Scala 3 on JVM
with structural readiness for a Native target.

When this project was first ingested (2026-05-29 morning), the
codebase was CLI plumbing — `Main` (verb dispatcher), `Resolve`
(smoke test), `MillQuery` (subprocess wrapper). There was no
domain ADT and the adoption ADR was deliberately deferred to
avoid claiming evidence that did not exist on disk.

By end of 2026-05-29 the picture inverted. Two packages now carry
the pattern in its declarative encoding:

### `dm.catalog` — the catalog model

| Type | Shape | Evidence |
|------|-------|----------|
| `CrossKind` | `enum derives CanEqual` (`Java` / `Scala` / `Full`) | Pure data; `render` is a total pattern match |
| `Coord(group, artifact, version, cross)` | `final case class derives CanEqual` | `parse: String => Either[String, Coord]`; `render` round-trips; `moduleString` projection; longest-separator parse is total |
| `Library(group, artifact, version, cross)` | `final case class derives CanEqual` | `fromCoord` lifts a `Coord`; `coord` projects back |
| `ProjectInfo(path, libraries: Vector[String])` | `final case class derives CanEqual` | Pure data; library handles sorted at construction |
| `Catalog(libraries, projects)` | `final case class derives CanEqual` | `Catalog.empty` initial value; deterministic ordering |
| `CatalogBuilder.fromProjects(Vector[Input])` | Pure function | Same input set → same Catalog, regardless of input order |

The split between *data* (`Catalog` and its parts) and
*interpreters* (`TomlWriter`, `YamlWriter`, `TomlReader`,
`YamlReader`, `DependenciesMillWriter`) is the algebra-program-
interpreter split the pattern prescribes. Adding a new
interpreter (e.g. a future JSON serializer for an LSP) does not
touch any of the existing ones — exactly the trade-off the
declarative encoding optimises for.

### `dm.mill` — the subprocess DSL

| Type | Shape | Evidence |
|------|-------|----------|
| `Mill.Cwd(projectDir)` | `final case class derives CanEqual` | `resolve` / `show` / `raw` build an `Invocation` |
| `Mill.Invocation(projectDir, args, noisy)` | `final case class derives CanEqual` | `silently` / `verbosely` operators return new values; `as*` exits run the description |

`Mill.in(dir).resolve("__").silently.asLines` reads as prose
because the algebra is data — `Cwd`, `Invocation`, the `noisy`
flag — and the `as*` exits are the interpreters. Composition for
free: `verbosely.silently` and `silently.silently` produce equal
values (tested via `derives CanEqual`).

### Cross-cutting type choices

A scan of the codebase confirms the pattern's full discipline:

- Every domain type is an `enum` or `final case class` with
  `derives CanEqual`.
- Total functions everywhere: `Coord.render`, `Coord.parse`
  (`Either` for failure), `TomlWriter.render`, `YamlWriter.render`,
  `DependenciesMillWriter.render`, `CatalogBuilder.fromProjects`.
- Errors are `Either[String, A]` end-to-end (`Coord.parse`,
  `TomlReader.parse`, `YamlReader.parse`, `CatalogReader.read`,
  `Mill.Invocation.asText` / `asLines` / `asJson`,
  `MillQuery.mvnDepsTaskPaths` / `show`, threaded through
  `Extract.extractCoords` via for-comprehension).
- No `Product`-introspection: handle generation is explicit
  `kebab(artifact)` with explicit collision rules; val-name
  rendering is explicit `kebabToCamel`; module-string splitting
  uses an explicit longest-match table.

## Decision

Adopt [[tech/patterns/functional-domain-design]] unconditionally.
The encoding is **declarative**: ADTs (`enum` / sealed case-class
hierarchies) carry data; operators (`silently`, `withTicker`,
`Coord.render`) construct new values; interpretation is a
separate pass (`TomlWriter.render`, `Mill.Invocation.asText`,
etc.).

Future work must continue to keep:

- Constructors and operators **orthogonal** (no two synthesisable
  from each other). The current handle-generation rule, for
  instance, is one rule; not two with overlap.
- Domain types **effect-free**. Effects live in `Mill.exec`,
  `os.write`, `os.read`, `Console.err.println` — never inside
  `Coord`, `Library`, `Catalog`, or their builders.
- Failure surfaced as `Either[String, A]` at module boundaries.
  Internal helpers (e.g. `splitExact`) may return `Option` when
  the call site only needs a yes/no signal, but a public API
  carrying error context must use `Either`.

The pattern's `excludes: [shell-scripts, nix-modules]` clause
does not apply here. `bin/dm` is a thin wrapper (auto-rebuild +
`exec java -jar`) and `flake.nix` is dev-shell glue; neither
qualifies as a "shell-script domain" the exclusion targets.

## Consequences

- dm is the **fourth project** to adopt this pattern after
  [[projects/compositor/adr/0001-adopt-functional-domain-design]]
  (declarative + allocation deviation),
  [[projects/sourceline-manager/adr/0001-adopt-functional-domain-design]]
  (declarative, monoid-law evidence), and
  [[projects/toolbox/adr/0001-adopt-functional-domain-design]]
  (declarative across ten modules).
- The codebase has **two** worked examples of the declarative
  encoding at different layers — `dm.catalog` (data) and
  `dm.mill` (subprocess DSL). Future projects looking for a
  multi-domain realisation should land here. The toolbox
  precedent of one algebra (`proc`) + N interpreters (`proc-*`)
  is now matched by dm's one catalog model + N format
  interpreters (TOML, YAML, Dependencies.mill, and the implicit
  reverse-reader pair for each writer).
- Adding a new constructor to `CrossKind` (e.g. `Full2_13` for
  cross-Scala-2.13 / Scala-3 artifacts) requires updating every
  interpreter — by design. The compiler's exhaustiveness check
  flags every missing case.
- Adding a new interpreter (e.g. a `JsonWriter` for a future LSP
  or a `MarkdownWriter` for human-facing docs) is free at the
  algebra level. Same shape, no algebra change.
- Effects must continue to be confined to subprocess / IO
  modules. Any future `dm.catalog` change introducing
  `IO[_]` / `Kyo[_]` parameters would be a pattern violation; the
  effectful work belongs in `Extract`, `Regen`, `Verify`, or the
  Mill DSL exit functions.

## Alternatives Considered

- **Executable encoding** (operators carry functions, not data).
  Rejected: would defeat round-tripping — the
  Writer→Reader→Writer property tests rely on `Catalog` being
  inspectable data, not opaque function values. Same argument
  applies to `Mill.Invocation` — the `renderArgs` introspection
  hook used in tests presumes data.
- **Tagless-final on `Mill.Invocation`**. Considered for
  abstracting over the subprocess execution monad (future Kyo
  port, fs2-based testing). Rejected for v1 — the `Either`
  return type already abstracts enough, and tagless-final would
  add a type parameter to every call site for a benefit we
  cannot currently demonstrate. Keep it on the table for when a
  real fake-runner test arrives.
- **Not declaring and remaining silent**. Would be flagged as
  drift per `POLICY.md` (missing declaration for an in-scope
  pattern) since the on-disk evidence is now substantial.

## Links

- [[tech/patterns/functional-domain-design]]
- [[sources/summaries/dependency-manager]]
- [[sources/raw/code/dependency-manager]]
- [[projects/dependency-manager/designs/dm-architecture]]
- [[projects/sourceline-manager/adr/0001-adopt-functional-domain-design]] — sibling adoption (foundation library shape)
- [[projects/toolbox/adr/0001-adopt-functional-domain-design]] — sibling adoption (ten-module library shape)
- [[projects/compositor/adr/0001-adopt-functional-domain-design]] — sibling adoption with allocation deviation
- `/p/hg/dependency-manager/dm/src/catalog/` — `Coord`, `Library`, `Catalog`, `CatalogBuilder` (data + builder)
- `/p/hg/dependency-manager/dm/src/mill/Mill.scala` — subprocess DSL
- `/p/hg/dependency-manager/dm/src/catalog/{Toml,Yaml,DependenciesMill}Writer.scala` — interpreters
- `/p/hg/dependency-manager/dm/src/catalog/{Toml,Yaml,Catalog}Reader.scala` — dual interpreters

# tagless

A type-safe HTML DSL family for Scala 3, split into fourteen focused
artifacts. Cursor/Zipper algebra at the core; specialized DSLs for
forms, tables, markdown, CRUD, pages, HTMX, SVG, tree visualization,
client-side routing, internationalization, and ScalaJS event handling.
Published per-module under `no.virtual-architect:tagless-<kebab>`.

**Status:** active

## Stack

- Language: Scala 3 (3.8.3)
- Platforms: JVM and Scala.js for thirteen modules; `events` is
  Scala.js-only (Airstream has no JVM target).
- Effects: none in the core DSL (pure construction). `events`
  consumes Airstream's `EventStream` / `Var` primitives.
- Build: Mill 1.1.2, Nix dev shell (JDK + Mill + Node for Vite
  consumers).
- Tests: MUnit; one shared `TestI18n` test fixture duplicated per
  test module that uses the `.i18n` extension.
- External libs: `com.raquo::domtypes` (19.0.0) — shared HTML/CSS
  attribute keys; `com.raquo::airstream` (17.2.1) — for `events`;
  `com.raquo::ew` (0.2.0) — JS-only optimization layer for `core.js`.

## Code Location

`/p/hg/tagless` — see [[sources/raw/code/tagless]] (bridge) and
[[sources/summaries/tagless]] for the distilled view.

The repository lives outside `projects/tagless/`; this wiki folder
holds only the project's wiki-side artefacts (ADRs, plans, syntheses,
log). The breakout source is `/p/v42/tagless` (a monolith that also
hosts shapesdsl, animdsl, presenter, and several demo apps — none
of those landed in this breakout).

## Embedding Path

`tagless` is intended as a standalone repository today. When/if it
joins a larger monorepo, the per-module `build.mill` becomes a
`package.mill` under a `tagless/` subtree, and `object V` collapses
into the monorepo's central `deps/Dependencies.mill` (cf. the toolbox
trajectory in [[projects/toolbox]]).

The fine-grained module split was a deliberate up-front cost so that
each artifact can be open- or closed-sourced individually as
internal-vs-public visibility decisions land.

## Sibling breakouts (planned)

The source monolith at `/p/v42/tagless` also contains:

- `shapesdsl` + `shapesdslsvg` → planned `/p/hg/shapesdsl`
- `animdsl` + `animdslsvg` + `animdslooxml` → planned `/p/hg/animdsl`
- `presenter` → planned `/p/hg/presenter` (consumes
  `tagless-core`, `tagless-events`, `shapesdsl`)

Each is its own breakout operation; this one covers only the
HTML-DSL family.

## Pages

### ADRs (wiki-side; record stance on global normative pages)

- [adr/0001-adopt-functional-domain-design.md](adr/0001-adopt-functional-domain-design.md) — Adopt [[tech/patterns/functional-domain-design]] (declarative encoding; evidence: `enum Node`, `enum Attr`, `Cursor[D, K]` immutable zipper with explicit `List[Context]` stack, phantom-typed depth and element kind, `Form[S <: FormState]` and `Table[S <: TableState]` type-state grammars, all operator algebra exposed as extensions on the ADT — no mutable builders)
- [adr/0002-deviate-deps-single-file.md](adr/0002-deviate-deps-single-file.md) — Deviate from [[tech/decisions/deps-single-file]] while standalone (versions inline in `object V` per breakout convention; revisit when/if tagless joins a monorepo)

### Designs
*No wiki-side designs yet. Two design notes live in the source repo
(`view_router_design_sketch.md`, `animdsl_specification_and_design.md`)
— the latter is out of scope for this breakout; the former may become
a `route` module proposal.*

### Plans
*No plans yet.*

### Tickets
*No tickets yet.*

### Syntheses
*No syntheses yet.*

### Other
- [log.md](log.md)

## Module Summary

| Module | Platforms | Deps | Artifact |
|--------|-----------|------|----------|
| `htmlid` | JVM, JS | — | `tagless-htmlid` |
| `core` | JVM, JS | `htmlid`, `i18n`, domtypes | `tagless-core` |
| `i18n` | JVM, JS | — | `tagless-i18n` |
| `md` | JVM, JS | `core`, `i18n` | `tagless-md` |
| `meta` | JVM, JS | `core` | `tagless-meta` |
| `page` | JVM, JS | `core`, `i18n`, `meta` | `tagless-page` |
| `form` | JVM, JS | `core`, `i18n` | `tagless-form` |
| `table` | JVM, JS | `core`, `i18n` | `tagless-table` |
| `crud` | JVM, JS | `core`, `i18n`, `form` | `tagless-crud` |
| `route` | JVM, JS | `core` | `tagless-route` |
| `viz` | JVM, JS | `core` | `tagless-viz` |
| `htmx` | JVM, JS | `core` | `tagless-htmx` |
| `svg` | JVM, JS | `core` | `tagless-svg` |
| `events` | JS only | `htmlid` (+ Airstream) | `tagless-events` |

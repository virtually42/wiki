# animdsl

A declarative animation DSL for Scala 3 with SVG/SMIL and OOXML
PresentationML backends. A single `Timeline` expression compiles to
either format with no per-target branching. Three focused artifacts
under `no.virtual-architect:animdsl-<kebab>`.

**Status:** active

## Stack

- Language: Scala 3 (3.8.3)
- Platforms: JVM and Scala.js for `core` and `svg`; **JVM only** for
  `ooxml` (PresentationML is a server-side export concern)
- Effects: none in the algebra; backends are pure folds
- Build: Mill 1.1.2, Nix dev shell (JDK + Mill)
- Tests: MUnit; only `svg/SvgAnimAttrsSpec` exists upstream — `core`
  and `ooxml` tests are a follow-up
- External libs: none in `core`. `svg` and `ooxml` depend on
  `no.virtual-architect:tagless-core:0.1.0-SNAPSHOT` (cross-repo
  publishLocal SNAPSHOT)

## Code Location

`/p/hg/animdsl` — see [[sources/tmp/animdsl]] (bridge, staged for
human promotion to `sources/raw/code/`) and
[[sources/summaries/animdsl]] for the distilled view.

The repository lives outside `projects/animdsl/`; this wiki folder
holds only the project's wiki-side artefacts. The breakout source is
`/p/v42/tagless`; the **design source of truth** is the file
`/p/v42/tagless/animdsl_specification_and_design.md` (preserved
alongside the source repo, not in this repo).

## Embedding Path

Standalone repository today. The design doc's §6 "Module Layout"
matches the on-disk structure 1:1. When/if animdsl joins a larger
monorepo, per-module `build.mill` becomes `package.mill` under an
`animdsl/` subtree, and `object V` collapses into the central
`deps/Dependencies.mill`.

## Sibling breakouts

| Repo | Purpose | Status |
|------|---------|--------|
| [[projects/tagless]] | Type-safe HTML DSL family | landed 2026-05-29 |
| [[projects/shapesdsl]] | 2D shape + heatmap DSL | landed 2026-05-29 |
| `animdsl` (this) | Animation timeline DSL | landed 2026-05-30 |
| `presenter` (planned) | Slide deck DSL | consumes `tagless-core`, `tagless-events`, `shapesdsl`; may consume animdsl |

## Pages

### ADRs (wiki-side; record stance on global normative pages)

- [adr/0001-adopt-functional-domain-design.md](adr/0001-adopt-functional-domain-design.md) — Adopt [[tech/patterns/functional-domain-design]] (cleanest expression in the breakout family: `enum Timeline` + four `enum` axes + `AnimBackend[A]` typeclass; no phantom types, no type-state, no extension-method DSL)
- [adr/0002-deviate-deps-single-file.md](adr/0002-deviate-deps-single-file.md) — Deviate from [[tech/decisions/deps-single-file]] while standalone

### Designs

- The design source of truth is `/p/v42/tagless/animdsl_specification_and_design.md`
  (preserved in the source monolith, not yet ingested into the wiki).
  Once ingested, it will live at `projects/animdsl/designs/specification-and-design.md`.

### Plans
*No plans yet. Open follow-ups recorded in [[projects/animdsl/log]]:
property-based round-trip tests for `core` and `ooxml`; refresh the
design doc to reflect actual `tagless.Node` output type (vs the
`scala-xml` recommendation in the original §7).*

### Tickets
*No tickets yet.*

### Syntheses
*No syntheses yet.*

### Other
- [log.md](log.md)

## Module Summary

| Module | Platforms | Deps | Artifact |
|--------|-----------|------|----------|
| `core` | JVM, JS | — | `animdsl-core` |
| `svg` | JVM, JS | `core`, `tagless-core` (cross-repo) | `animdsl-svg` |
| `ooxml` | **JVM only** | `core`, `tagless-core` (cross-repo) | `animdsl-ooxml` |

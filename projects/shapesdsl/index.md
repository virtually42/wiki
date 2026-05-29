# shapesdsl

A declarative 2D shape and heatmap DSL for Scala 3, split into three
focused artifacts. Pure shape algebra at the core, a heatmap built on
top, and an SVG interpreter bridge that consumes `tagless-core` to
produce SVG output. Published per-module under
`no.virtual-architect:shapesdsl-<kebab>`.

**Status:** active

## Stack

- Language: Scala 3 (3.8.3)
- Platforms: JVM and Scala.js for all three modules
- Effects: none (pure construction; Java2D rendering is direct)
- Build: Mill 1.1.2, Nix dev shell (JDK + Mill)
- Tests: MUnit (JVM-only, matches source layout)
- External libs: none in `core` or `heatmap`. `svg` depends on
  `no.virtual-architect:tagless-core:0.1.0-SNAPSHOT` (cross-repo
  publishLocal SNAPSHOT — build `tagless` before this repo).

## Code Location

`/p/hg/shapesdsl` — see [[sources/tmp/shapesdsl]] (bridge, staged
for human promotion to `sources/raw/code/`) and
[[sources/summaries/shapesdsl]] for the distilled view.

The repository lives outside `projects/shapesdsl/`; this wiki folder
holds only the project's wiki-side artefacts. The breakout source is
`/p/v42/tagless` (a monolith that also hosts tagless, animdsl,
presenter, and demo apps).

## Embedding Path

`shapesdsl` is intended as a standalone repository today. When/if it
joins a larger monorepo, per-module `build.mill` becomes
`package.mill` under a `shapesdsl/` subtree, and `object V` collapses
into the monorepo's central `deps/Dependencies.mill`. Same
trajectory as toolbox / tagless.

## Sibling breakouts

The source monolith at `/p/v42/tagless` is being decomposed into
multiple sibling repos:

| Repo | Purpose | Status |
|------|---------|--------|
| [[projects/tagless]] | Type-safe HTML DSL family | landed 2026-05-29 |
| `shapesdsl` (this) | 2D shape + heatmap DSL | landed 2026-05-29 |
| `animdsl` | Animation timeline ADT | planned |
| `presenter` | Slide deck DSL | planned (consumes shapesdsl) |

## Pages

### ADRs (wiki-side; record stance on global normative pages)

- [adr/0001-adopt-functional-domain-design.md](adr/0001-adopt-functional-domain-design.md) — Adopt [[tech/patterns/functional-domain-design]] (`enum Shape`, `final case class Heatmap`, `ShapeScene` ADT, pure builders, total `toSvg` / `toPng` / `toScene` interpreters)
- [adr/0002-deviate-deps-single-file.md](adr/0002-deviate-deps-single-file.md) — Deviate from [[tech/decisions/deps-single-file]] while standalone (versions inline in `object V` per breakout convention)

### Designs
*No wiki-side designs yet.*

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
| `core` | JVM, JS | — | `shapesdsl-core` |
| `heatmap` | JVM, JS (Java2D on JVM) | `core` | `shapesdsl-heatmap` |
| `svg` | JVM, JS | `core`, `tagless-core` (cross-repo) | `shapesdsl-svg` |

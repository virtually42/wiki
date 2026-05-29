# shapesdsl — project log

Append-only record of project-scoped events.

**Ownership: llm.**

---

## [2026-05-29] ingest | Initial breakout from /p/v42/tagless

Executed `breakout` as the second of four sibling breakouts from
the monolithic source at `/p/v42/tagless`. Sequencing: tagless
(2026-05-29 earlier) → shapesdsl (this entry) → animdsl → presenter.
The sequencing is forced by `shapesdsl-svg`'s `tagless-core`
dependency, which had to be available in `~/.ivy2/local` before
shapesdsl could compile.

### Module decomposition (3 modules)

| Module | Platforms | Deps | Artifact |
|--------|-----------|------|----------|
| `core` | JVM, JS | — | `shapesdsl-core` |
| `heatmap` | JVM, JS (Java2D on JVM) | `core` | `shapesdsl-heatmap` |
| `svg` | JVM, JS | `core` + `tagless-core` (cross-repo) | `shapesdsl-svg` |

The source had two modules (`shapesdsl`, `shapesdslsvg`). The
breakout split `shapesdsl` further into `core` + `heatmap` so that
consumers wanting shape geometry don't pull in the Java2D
HeatmapImage renderer (or the Heatmap ADT itself).

### Wiki artefacts created

- [[sources/tmp/shapesdsl]] — bridge (uncommitted-tree state; human
  promotes after initial commit)
- [[sources/summaries/shapesdsl]] — distilled summary
- `projects/shapesdsl/index.md` — this folder's index
- `projects/shapesdsl/log.md` — this file
- `projects/shapesdsl/adr/0001-adopt-functional-domain-design.md`
- `projects/shapesdsl/adr/0002-deviate-deps-single-file.md`

### Normative pages touched

- `tech/patterns/functional-domain-design` — added
  `projects/shapesdsl/adr/0001` to `used_by`
- `tech/decisions/deps-single-file` — added
  `projects/shapesdsl/adr/0002` to `used_by` (deviation)

### One structural code change during the breakout

The source's `shapesdsl/src/shapesdsl/dsl.scala` contained a
`heatmap[T]` factory inside `object dsl`:

```scala
def heatmap[T](data: IndexedSeq[IndexedSeq[T]])(using Numeric[T]): Heatmap =
  Heatmap.of(data)
```

This referenced the `Heatmap` ADT which the breakout moved to the
`heatmap` module — a `core` → `heatmap` back-edge. The factory
moved to `heatmap/src/shapesdsl/Heatmaps.scala` as `object Heatmaps`
in `package shapesdsl`. Two call sites (`HeatmapDemo`, `HeatmapSpec`)
were updated with `import shapesdsl.Heatmaps.heatmap`. This is the
*only* structural code change made during the breakout; everything
else is verbatim relocation.

### Detour worth recording

First attempt put the factory in a sub-package
`package shapesdsl.heatmap`. Scala.js compilation rejected it with:

> Trying to define package with same name as class heatmap

The root cause is unclear (the only `Heatmap`-shaped name in scope
is the uppercase case class). JVM compilation accepted the
sub-package; only the JS target failed. Fell back to a top-level
`object Heatmaps` in `package shapesdsl`. Flagged in
[[sources/summaries/shapesdsl]] §Observations as an issue to
investigate if it recurs in a sibling split.

### Build verification

- `mill resolve __` ✓
- `mill __.compile` ✓ across 3 modules × 2 platforms
- `mill __.fastLinkJS` ✓
- Per-module JVM `testForked` ✓ for all three modules (`core`,
  `heatmap`, `svg`)
- `mill __.publishLocal` ✓ — six artifacts published to
  `~/.ivy2/local`:
  - `no.virtual-architect:shapesdsl-core_3:0.1.0-SNAPSHOT`
  - `no.virtual-architect:shapesdsl-core_sjs1_3:0.1.0-SNAPSHOT`
  - `no.virtual-architect:shapesdsl-heatmap_3:0.1.0-SNAPSHOT`
  - `no.virtual-architect:shapesdsl-heatmap_sjs1_3:0.1.0-SNAPSHOT`
  - `no.virtual-architect:shapesdsl-svg_3:0.1.0-SNAPSHOT`
  - `no.virtual-architect:shapesdsl-svg_sjs1_3:0.1.0-SNAPSHOT`

### Cross-repo dependency

`shapesdsl-svg` depends on `no.virtual-architect:tagless-core` via
publishLocal SNAPSHOT (`V.tagless = "0.1.0-SNAPSHOT"`). Mill
resolves the right `_3` / `_sjs1_3` artifact automatically from the
context (`ScalaJSModule` context picks `_sjs1_3`).

This is the first cross-repo dependency between `/p/hg/` projects
in the fine-grained-breakout series. The build pattern works
cleanly with no special configuration beyond ensuring
`mill __.publishLocal` ran in the upstream repo first.

### Observations worth flagging for synthesis

- **Fourth consecutive breakout deviating from
  [[tech/decisions/deps-single-file]].** The carve-out hypothesis
  from [[meta/log]] §tagless ingest is now well-supported. Worth
  drafting an addendum to the decision rather than continuing per-
  project ADRs.
- **Cross-repo publishLocal pattern works.** No build-time
  coordination beyond ordering. If the four breakouts converge on
  this pattern, [[tech/guides/breakout]] could be extended with a
  §"cross-repo publishLocal" section documenting the
  `V.<other>: String = "0.1.0-SNAPSHOT"` + `mvn"${V.organization}::<other-module>::${V.<other>}"`
  recipe.
- **`Scala.js sub-package + class conflict`.** The detour above
  (heatmap package/class collision under Scala.js) is worth a
  reproduction case in [[tech/guides/mill-cross-platform]] §Pitfalls
  if it recurs.

### Open questions surfaced to human

1. **Initial commit.** Tree at `/p/hg/shapesdsl` is uncommitted.
2. **Promote bridge after initial commit.** Same pattern as
   tagless — `sources/tmp/shapesdsl.md` → `sources/raw/code/shapesdsl.md`
   with the commit SHA filled in.
3. **Next breakout: animdsl.** Animation timeline ADT plus three
   backends (SVG/SMIL, OOXML, animdsl pure). Has its own design doc
   (`animdsl_specification_and_design.md`) which serves as the
   source of truth.

Refs: [[sources/tmp/shapesdsl]] · [[sources/summaries/shapesdsl]] ·
[[tech/guides/breakout]]

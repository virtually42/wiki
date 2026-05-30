# animdsl — project log

Append-only record of project-scoped events.

**Ownership: llm.**

---

## [2026-05-30] ingest | Initial breakout from /p/v42/tagless

Third of four sibling breakouts. Sequencing:
tagless (2026-05-29) → shapesdsl (2026-05-29) → animdsl (this) →
presenter (next).

The design document at
`/p/v42/tagless/animdsl_specification_and_design.md` is the
authoritative spec — its §6 "Module Layout" matches the on-disk
structure 1:1. The breakout reifies those boundaries as artifacts.

### Module decomposition (3 modules)

| Module | Platforms | Deps | Artifact |
|--------|-----------|------|----------|
| `core` | JVM, JS | — | `animdsl-core` |
| `svg` | JVM, JS | `core`, `tagless-core` (cross-repo) | `animdsl-svg` |
| `ooxml` | **JVM only** | `core`, `tagless-core` (cross-repo) | `animdsl-ooxml` |

### Wiki artefacts created

- [[sources/tmp/animdsl]] — bridge (uncommitted-tree state)
- [[sources/summaries/animdsl]] — distilled summary
- `projects/animdsl/index.md`
- `projects/animdsl/log.md` (this file)
- `projects/animdsl/adr/0001-adopt-functional-domain-design.md`
- `projects/animdsl/adr/0002-deviate-deps-single-file.md`

### Normative pages touched

- `tech/patterns/functional-domain-design` — added
  `projects/animdsl/adr/0001` to `used_by`
- `tech/decisions/deps-single-file` — added
  `projects/animdsl/adr/0002` to `used_by` (deviation)
- `tech/guides/breakout` §Existing Breakouts — added animdsl row

### Zero structural code changes during the breakout

Unlike tagless (3 moves) and shapesdsl (1 move), animdsl had **no
intra-module cycles** in the source. `core` has zero references to
`svg` or `ooxml`. The breakout is a pure relocation; no source
edits were necessary.

This matches the cleanliness expected from a codebase whose layout
was designed up-front in the spec document — versus tagless and
shapesdsl which grew organically and accumulated back-edges.

### Design-doc vs implementation divergences

The design document §7 (Dependency Notes) recommends:

- `cats-core` for `NonEmptyList` and tree-fold typeclasses
- `scala-xml` for backend output type (`scala.xml.Elem`)

The actual implementation:

- Rolls a tiny in-tree `Nel` (~50 LOC) in `core/Nel.scala` instead
  of pulling cats-core into core
- Returns `tags.Node` from both backends (reusing the tagless
  `Node` ADT) instead of `scala.xml.Elem`

These are pragmatic choices that keep `animdsl-core` dep-free and
align the family on a shared rendering infrastructure
(`tagless.Node`). Worth refreshing the design doc to reflect
reality.

### Build verification

- `mill resolve __` ✓
- `mill __.compile` ✓ across 5 compile targets (core+svg × 2
  platforms, ooxml × 1 JVM platform)
- `mill __.fastLinkJS` ✓ (core, svg only)
- `mill svg.jvm[3.8.3].test.testForked` ✓ (SvgAnimAttrsSpec — the
  only test upstream)
- `mill __.publishLocal` ✓ — five artifacts published to
  `~/.ivy2/local`:
  - `no.virtual-architect:animdsl-core_3:0.1.0-SNAPSHOT`
  - `no.virtual-architect:animdsl-core_sjs1_3:0.1.0-SNAPSHOT`
  - `no.virtual-architect:animdsl-svg_3:0.1.0-SNAPSHOT`
  - `no.virtual-architect:animdsl-svg_sjs1_3:0.1.0-SNAPSHOT`
  - `no.virtual-architect:animdsl-ooxml_3:0.1.0-SNAPSHOT`

### Cross-repo dependency pattern (second use)

Same wiring as shapesdsl-svg: `V.tagless = "0.1.0-SNAPSHOT"` in
`object V`, `mvn"${V.organization}::tagless-core::${V.tagless}"` in
the consuming module's `mvnDeps`. Mill resolves `_3` vs `_sjs1_3`
from the consuming Cross variant context.

Two breakouts in a row using this pattern; worth promoting into
[[tech/guides/breakout]] §Phase 4 as a documented recipe.

### Observations worth flagging for synthesis

- **Fifth consecutive deviation from `deps-single-file`.** The
  pattern is universal for fine-grained standalone breakouts. The
  carve-out hypothesis is over-determined; opening an addendum to
  [[tech/decisions/deps-single-file]] is the right next step.
- **Cleanest ADT-only codebase yet.** `core` is 12 source files of
  pure ADTs + a typeclass + the dsl operator file. No phantom
  types, no type-state, no extension-method-heavy surface — just
  algebraic sums, products, and total interpreters. Worth using as
  the new exemplar for [[tech/patterns/functional-domain-design]]
  "declarative encoding" alongside sourceline-manager (which is
  similarly minimal).
- **Missing tests.** Only `SvgAnimAttrsSpec` exists. `core` should
  have property-based tests for `Timeline` constructor laws
  (sequence associativity, identity); `ooxml` should have round-
  trip tests against a representative `<p:timing>` corpus. Flagged
  as a high-value first follow-up.
- **No platform divergences this time.** Every shared source
  compiles to JVM and JS (for core and svg). No `src-jvm/` or
  `src-js/` directories. Cleanest cross-platform setup in the
  family.

### Open questions surfaced to human

1. **Initial commit.** Tree at `/p/hg/animdsl` is uncommitted.
2. **Promote bridge after initial commit.** Same pattern as
   tagless — `sources/tmp/animdsl.md` → `sources/raw/code/animdsl.md`
   with the commit SHA.
3. **Ingest the design doc into the wiki.** The file
   `/p/v42/tagless/animdsl_specification_and_design.md` is the
   spec source of truth. Worth ingesting at
   `projects/animdsl/designs/specification-and-design.md` so the
   wiki can cite §-numbered sections.
4. **Next: presenter.** Slide deck DSL. Will consume
   `tagless-core` + `tagless-events` + `shapesdsl-*`. Largest
   sibling repo (~20 source files + slide-content presentations).

Refs: [[sources/tmp/animdsl]] · [[sources/summaries/animdsl]] ·
[[tech/guides/breakout]]

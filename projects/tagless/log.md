# tagless — project log

Append-only record of project-scoped events.

**Ownership: llm.**

---

## [2026-05-29] ingest | Initial breakout from /p/v42/tagless

Executed `breakout` from the monolithic source at `/p/v42/tagless`
to the new destination `/p/hg/tagless`. The human's brief was:

> *"option D + option C — separate repositories, fine-grained
> ten-way split of the tags module — not everything will be open
> sourced; I will use mill and publishLocally snapshots
> extensively"*

(Option D = ten-module split of the monolithic `tags`; option C =
multiple sibling breakouts. This run executed the tagless one;
shapesdsl / animdsl / presenter are explicit follow-ups.)

### Module decomposition

Fourteen modules total, all under `no.virtual-architect:tagless-<kebab>`:

| Group | Modules |
|-------|---------|
| Pure-types leaves | `htmlid`, `i18n` |
| Cursor algebra | `core` (depends on htmlid + i18n) |
| Specialized DSLs | `md`, `meta`, `page`, `form`, `table`, `crud`, `route`, `viz`, `htmx`, `svg` |
| JS-only runtime | `events` (depends on htmlid + Airstream) |

The split executes the *existing* internal package boundaries from
the source's `tags` module — no new module was invented.

### Wiki artefacts created

- [[sources/raw/code/tagless]] — bridge (promoted after initial commit `7e2ebe8`; was
  for human promotion to `sources/raw/code/tagless.md` once the
  initial commit lands)
- [[sources/summaries/tagless]] — distilled summary
- `projects/tagless/index.md` — this folder's index
- `projects/tagless/log.md` — this file
- `projects/tagless/adr/0001-adopt-functional-domain-design.md`
- `projects/tagless/adr/0002-deviate-deps-single-file.md`

### Normative pages touched

- `tech/patterns/functional-domain-design` — added `projects/tagless`
  to `used_by`
- `tech/decisions/deps-single-file` — added `projects/tagless` to
  `used_by` (deviation)
- `tech/guides/mill-cross-platform` — added `projects/tagless` to
  `used_by`

### Three structural code changes during the breakout

The breakout guide forbids speculative source edits but allows
moves driven by the layout. Three moves were forced by the split:

1. **`tags.viz.{visualize, toD3Json, toAsciiTree, toMermaid,
   asComponent}` extensions moved from `core/src/tags/dsl.scala`
   to `viz/src/tags/viz/dsl.scala`.** The source imported
   `tags.viz.{TreeVisualization, TreeVisualizer, ComponentMeta}`
   from inside `tags.dsl`, but `viz` already depends on `core` —
   a cycle. The viz-aware extensions belong with viz.
2. **`tags.route.asRoute` analogously moved to
   `route/src/tags/route/dsl.scala`.** Same reasoning: it adds a
   `data-route` attribute consumed by the `route` module, so it
   belongs there.
3. **`core` acquired a hard dep on `i18n`.** `Fragment.options`,
   `simpleOptions`, `navItems`, `listItems` take `i18n.I18n[?]`
   parameters. The pragmatic call was to bring i18n into core
   rather than split Fragment into pure-HTML and i18n-aware halves
   (which would have meant a new module).

Each of these is a single-direction move that *adds* an import for
consumers (`import tags.viz.dsl.*` / `import tags.route.dsl.*`) but
removes the cycle. No behavior change.

### Build verification

- `mill resolve __` ✓
- `mill __.compile` ✓ across 14 modules × 2 platforms (1 platform
  for `events`)
- `mill __.fastLinkJS` ✓
- Per-module JVM `testForked` ✓ except two pre-existing upstream
  failures in `core.jvm.test` (`Fragment.hiddenSection` — source
  emits `class="hidden"`, tests expect `class="is-hidden"`). Not
  introduced by the breakout. Flagged as the first follow-up.

### Skipped (intentional)

- shapesdsl + shapesdslsvg → planned `/p/hg/shapesdsl` breakout
- animdsl + animdslsvg + animdslooxml → planned `/p/hg/animdsl`
- presenter → planned `/p/hg/presenter`
- todoExample, todoExample2, FpinScala, NNandLLM, TheGenie — demo
  apps; not libraries; out of scope
- Working files: `PROMPT_*.md`, `tickets_*.md`, `tasks.md`,
  `progress.md`, `TODO.md`, `Makefile`, `.claude/`, `.bsp/`,
  `.metals/`, `out/`, `test-results/`
- Root-level demo HTML (`index-en.html`, `index-nb.html`)
- Design docs (`animdsl_specification_and_design.md`,
  `view_router_design_sketch.md`, `specs/emmet-dsl.md`) — left in
  source for now; the route design doc may be ingested under
  `projects/tagless/designs/` later

### Observations worth flagging for synthesis

- **Third project in a row to deviate from `deps-single-file`.**
  sourceline-manager (deviated), toolbox (initially deviated, then
  adopted via the `dm` migration), now tagless. If a fourth deviates,
  consider whether the canonical "fine-grained breakout" shape
  warrants a carve-out in the decision rather than a per-project ADR.
- **Three modules with package-vs-directory mismatch.** `md/src/md/`
  declares `package md`; `form/src/html/lib/form/` declares
  `package html.lib.form`; `table/src/html/lib/table/` declares
  `package html.lib.table`. Preserved verbatim per breakout rule.
  A future rename pass is worth scheduling.
- **TestI18n duplication.** Eight test modules use a
  `String.i18n` extension via `tags.TestI18n`. Currently
  duplicated per test module (small file). A shared test-kit
  artifact would be cleaner — defer until other projects start
  duplicating similar fixtures.

### Open questions surfaced to human

1. **Initial commit decision.** Tree at `/p/hg/tagless` is
   uncommitted. Author/email/sign config is already set per the
   personal-repo policy; the human makes the first commit.
2. **Fix pre-existing Fragment.hiddenSection upstream test bug.**
   The source emits `class="hidden"`; tests expect `class="is-hidden"`.
   Either patch the source, update the tests, or pin the failure.
3. **Sequence the follow-up breakouts.** shapesdsl, animdsl,
   presenter — each is a separate run. Order matters because
   `presenter` consumes both `shapesdsl` and `tagless`; do
   `tagless` (this run) → `shapesdsl` → `animdsl` → `presenter`.
4. **Package harmonization pass.** Decide whether to rename
   `package md`, `package html.lib.form`, `package html.lib.table`
   to `package tags.md`, `package tags.form`, `package tags.table`
   — and whether to keep stub re-exports for source-compat.

Refs: [[sources/raw/code/tagless]] · [[sources/summaries/tagless]] ·
[[tech/guides/breakout]]

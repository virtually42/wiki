---
id: source-tagless
type: code
repo: /p/hg/tagless
last_observed: 2026-05-29
commit: 7e2ebe8e96709d70706be8d29b5452fbf7a06911
branch: main
git_init_state: committed — initial commit `7e2ebe8` ("init") on 2026-05-29
entry_points:
  - README.md
  - build.mill
  - flake.nix
  - htmlid/src/htmlid/HtmlId.scala
  - core/src/tags/dsl.scala
  - core/src/tags/Cursor.scala
  - core/src/tags/Fragment.scala
  - i18n/src/tags/i18n/I18n.scala
  - md/src/md/Markdown.scala
  - meta/src/tags/meta/Meta.scala
  - page/src/tags/page/Page.scala
  - form/src/html/lib/form/Form.scala
  - table/src/html/lib/table/Table.scala
  - crud/src/tags/crud/CrudView.scala
  - route/src/tags/route/dsl.scala
  - viz/src/tags/viz/dsl.scala
  - htmx/src/htmx/htmx.scala
  - svg/src/svgelements/svg.scala
  - events/src/eventhandler/EventHandler.scala
source_repo: /p/v42/tagless
design_source_of_truth: (none — module boundaries derived from existing
                       build.mill in `/p/v42/tagless` plus explicit
                       fine-grained split requested by human)
---

## Structure Overview

`tagless` is the destination of a granular breakout from the
monolithic source at `/p/v42/tagless`. The source contains a much
larger ecosystem (shapesdsl, animdsl, presenter, demo apps) — only
the **HTML-DSL family** is extracted here. shapesdsl, animdsl, and
presenter are intended for separate sibling breakouts at
`/p/hg/shapesdsl`, `/p/hg/animdsl`, and `/p/hg/presenter`.

The human's call was for **option D + option C**: ten-way split of
the monolithic `tags` module into focused artifacts so each can be
individually published-local and individually open-/closed-sourced.
The breakout produces 14 modules total (htmlid, core, i18n, md,
meta, page, form, table, crud, route, viz, htmx, svg, events).

A `git init` was performed (branch `main`, unsigned-commit config,
author `tigidar`) but no initial commit has been recorded — that is
a separate human decision.

## Key Modules

| Module | Platforms | Deps | Artifact |
|--------|-----------|------|----------|
| `htmlid` | JVM, JS | — | `tagless-htmlid` |
| `core` | JVM, JS | `htmlid`, `i18n`, domtypes (+ ew on JS) | `tagless-core` |
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
| `events` | JS only | `htmlid`, airstream | `tagless-events` |

### Notable splits made during the breakout

The monolithic `tags` module in the source mixed concerns. Three
package-vs-directory adjustments stood out:

- The visualization extension methods (`visualize`, `toD3Json`,
  `toAsciiTree`, `toMermaid`, `asComponent`) were inside
  `tags/src/tags/dsl.scala` but referenced `tags.viz.*` — a back-edge
  that would have forced `core` to depend on `viz` (cycle). They moved
  to `viz/src/tags/viz/dsl.scala` as a separate import scope
  (`tags.viz.dsl.*`).
- `asRoute` (route-marking extension) moved analogously to
  `route/src/tags/route/dsl.scala`.
- `Fragment.options` / `simpleOptions` / `navItems` / `listItems` use
  `tags.i18n.{I18n, Lang}` directly — `core` therefore acquired a
  hard dep on `i18n`.

### Package vs directory mismatch

Three modules keep packages that do not match the module name (this
is preserved verbatim from the source — no source edits during a
breakout, per `tech/guides/breakout`):

- `md/src/md/*` → `package md`
- `form/src/html/lib/form/*` → `package html.lib.form`
- `table/src/html/lib/table/*` → `package html.lib.table`

Flagged for a future rename pass.

## Build

- Mill **1.1.2**, JVM **21**, Scala **3.8.3**, Scala.js **1.20.1**
- `object V` block inline in `build.mill` (deviates from
  `tech/decisions/deps-single-file` while standalone)
- Versions: domtypes 19.0.0 · airstream 17.2.1 · raquo/ew 0.2.0 ·
  munit 1.2.1 · os-lib 0.11.5 · pprint 0.9.4 · sourcecode 0.4.4
- `no.virtual-architect` group · `0.1.0-SNAPSHOT` version
- All 14 modules `mill __.compile` clean

## Tests

Distributed per concern. JVM-only (matches source).

| Module | Specs |
|--------|-------|
| `core` | AttrSpec, ClassesSpec, DslSpec, HtmlIdSpec, I18nSpec, IndexHtmlSpec, PrettyHtmlSpec, TestI18n |
| `meta` | MetaSpec |
| `page` | PageSpec |
| `form` | FormSpec |
| `table` | TableSpec |
| `md` | InlineMarkdownParserSpec, TreeTest |
| `viz` | VizSpec |
| `htmx` | HtmxSpec |
| `svg` | SvgSpec |

`TestI18n.scala` is duplicated into each test module that needs the
`String.i18n` extension (small file, no shared-test-fixture infra).

`mill <m>.jvm[3.8.3].test.testForked` passes for every module
**except** `core.jvm` where two pre-existing upstream test failures
remain (`Fragment.hiddenSection` — source emits `class="hidden"`,
tests expect `class="is-hidden"`). Not introduced by the breakout;
flagged for upstream-or-here fix.

## Cross-platform layout

Per `tech/guides/mill-cross-platform`:

```
<module>/src/             — shared sources
<module>/src-jvm/         — JVM-only (only when divergence exists)
<module>/src-js/          — JS-only
<module>/test/src/        — shared test sources
<module>/jvm/             — empty Cross-variant moduleDir
<module>/js/              — empty Cross-variant moduleDir
```

`core` has both `src-jvm/` and `src-js/` (`DerivedStyleBuilder`).
`form` has `src-js/` (`FormPopulator` — uses `scalajs.dom`). No
other module has platform divergences.

## Skipped during breakout

From the source repo, the following were **not** moved:

- shapesdsl, animdsl, animdslsvg, animdslooxml, shapesdslsvg → planned
  separate breakouts at `/p/hg/shapesdsl`, `/p/hg/animdsl`
- presenter → planned separate breakout at `/p/hg/presenter`
- todoExample, todoExample2, FpinScala, NNandLLM, TheGenie — consumer
  apps, not libraries
- `PROMPT_*.md`, `tickets_*.md`, `tasks.md`, `progress.md`, `TODO.md`,
  `Makefile`, `ralph.sh`, `loop.sh`, `start_claude.sh`,
  `upgrade_scala.sh`, `rename-presenter.sh`
- `index-en.html`, `index-nb.html` (root-level demo HTML)
- `specs/emmet-dsl.md`, `animdsl_specification_and_design.md`,
  `view_router_design_sketch.md` — design docs left in source
- `.claude/`, `.bsp/`, `.metals/`, `out/`, `test-results/`

## Compliance scan

| Norm | Stance |
|------|--------|
| `tech/patterns/functional-domain-design` | **adopts** — immutable Cursor zipper, ADT-encoded Node/Tag/Attr, operators (`>>`, `\|`, `^`) as the algebra. Form/Table use type-state phantom types for compile-time grammar. |
| `tech/decisions/deps-single-file` | **deviates** — versions inline in `object V` per breakout convention while standalone |
| `tech/guides/mill-cross-platform` | **adopts** — `sharedSrc` / `sharedTestSrc` task pattern, kebab-only module names, JVM+JS Cross variants |

No evidence yet of `tdd-rhythm` (no test-first commit history),
`symmetric-refactoring` (no paired-operator catalogue), or
`tidy-first-commits` (uncommitted tree at breakout time).

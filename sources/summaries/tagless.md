---
id: summary-tagless
title: tagless (type-safe HTML DSL family) — code summary
kind: descriptive
status: accepted
scope: global
created: 2026-05-29
updated: 2026-05-29
confidence: high
sources:
  - sources/raw/code/tagless.md
tags: [scala, scala-js, mill, html, dsl, zipper, type-state, i18n, htmx, svg, library, breakout]
---

## What it is

`tagless` (artifacts under `no.virtual-architect:tagless-<module>`,
version `0.1.0-SNAPSHOT`, Apache-2.0) is a fourteen-module Mill
build that decomposes a type-safe HTML DSL into **single-concern
artifacts**. The core abstraction is a phantom-typed `Cursor[D, K]`
(functional zipper) for navigating and building HTML trees; depth
`D` and element kind `K` (Normal vs Void) are tracked at the type
level so structural errors fail compilation.

A consumer that only wants the cursor algebra pulls `tagless-core`
and gets none of the Form DSL, Table DSL, Markdown DSL, HTMX
attributes, SVG elements, ScalaJS event handling, or tree
visualization. A consumer that needs forms pulls
`tagless-form`; for a CRUD scaffold add `tagless-crud`; for typed
internationalization wire up `tagless-i18n` (already a `core`
transitive dep).

The repository at `/p/hg/tagless` is the destination of a
"fine-grained split" breakout requested by the human on
2026-05-29. The source monolith at `/p/v42/tagless` has additional
DSL families (animations, shapes, presenter, multiple demo apps)
that will become separate sibling breakouts at `/p/hg/shapesdsl`,
`/p/hg/animdsl`, and `/p/hg/presenter`.

Initial commit `7e2ebe8` ("init") landed on 2026-05-29.

## The fourteen modules and what they do

| Module | Platforms | Deps | What it owns |
|--------|-----------|------|--------------|
| `htmlid` | JVM + JS | none | Singleton-typed `HtmlId[S <: String]`, `IdScope[P <: String]` hierarchy, `RouteScope` with paired route/element-ID paths |
| `core` | JVM + JS | `htmlid`, `i18n`, domtypes | `Cursor` zipper, `Tag[K]`, `Node` ADT (Element/VoidElement/Text), `Depth` phantoms, `Attr` ADT, attribute extensions (`.id`, `.cls`, `.href`, …), CSS-class composition (`ClassList`, `clsWhen`, `clsUnless`), `Fragment` builders, `dsl` operators (`~`, `>>`, `>>^`, `>`, `>^`, `^`, `^^`, `*`, `+`), `tags.{html, attrs}` predefined surfaces, `render.{Html, PrettyHtml}` |
| `i18n` | JVM + JS | none | `Lang`, `I18n[K]`, `TextScope[K]` with `Sub[S]` nesting; type-level keys ensure unique translation paths |
| `md` | JVM + JS | `core`, `i18n` | Wiki-style `Markdown` DSL (`<#`, `<##`, `<*`, `<--`, `<+`, `<\|`, `<<`), `InlineMarkdown` (bold/italic/code/link), `InlineMarkdownParser`, `MarkdownConverter` to HTML nodes |
| `meta` | JVM + JS | `core` | `Meta.{charset, viewport, description, og, twitter, httpEquiv, defaults}` |
| `page` | JVM + JS | `core`, `i18n`, `meta` | `Page` builder composing `<head>` (meta, stylesheets, scripts) and `<body>` content into a full document |
| `form` | JVM + JS | `core`, `i18n` | Type-state `Form` DSL (`\|>`, `\|\|`, `\|*`, `\|@`, `\|>>`, `\|<<`, `\|!`), field type extensions (`.txt`/`.area`/`.num`/`.email`/`.pwd`/…), validation chains, `SelectBuilder`/`RadioBuilder`/`CheckboxBuilder`, `FormDerivation` typeclass, `FormInterpreter`. JS variant adds `FormPopulator` (scalajs-dom) |
| `table` | JVM + JS | `core`, `i18n` | Type-state `Table` DSL (`--`, `\|*`, `\|-`, `\|`, `\|+`, `\|\|`, `\|^`), cell `.spanning(n)` / `.rowSpanning(n)`, `TableInterpreter`, `TypelevelRules` |
| `crud` | JVM + JS | `core`, `i18n`, `form` | `CrudView` — toggle between read-only display and form-edit modes for a derived case class |
| `route` | JVM + JS | `core` | `asRoute(path)` cursor extension (adds `data-route` attr), `RouteExtractor` to derive a client-side route table from a rendered tree |
| `viz` | JVM + JS | `core` | `TreeVisualization`, `TreeVisualizer.build`, ASCII / D3 JSON / Mermaid renderers, `asComponent` cursor extension (adds `data-component` attrs that the visualizer detects) |
| `htmx` | JVM + JS | `core` | `.hxGet`, `.hxPost`, `.hxTarget`, `.hxSwap`, `.hxTrigger`, `.hxConfirm`, `.hxInclude`, `.hxVals`, `.hxOn(event)`, `HxBool` (boost/preserve/history-elt) — type-safe HTMX attributes |
| `svg` | JVM + JS | `core` | SVG container tags (`svg`, `g`, `defs`, `symbol`, `marker`, …), shape void tags (`circle`, `rect`, `path`, `line`, …), namespaced attributes (`.fill`, `.stroke`, `.viewBox`, `.svgTransform`, …), `SvgNs` |
| `events` | **JS only** | `htmlid`, airstream | Document-level event capture (`DomEventSource.{clicks, changes, submits, inputs, …}`), `EventFilter` extensions (`.forId`, `.forPrefix`, `.filterById`, `.withId`, `.notId`), `DomEvent` ADT (`Click`/`Change`/`Submit`/`KeyDown`/…), routers (`Router`, `RouteActivator`, `LinkInterceptor`), handler factories (`ClickHandler`, `FormHandler`, `SelectHandler`, `CrudHandler`) |

The dependency graph is rooted at two leaves — `htmlid` (pure types,
no deps) and `i18n` (pure types, no deps). Everything HTML-shaped
flows through `core`, which folds `htmlid` + `i18n` together with the
cursor algebra. Specialized DSLs (`md`, `form`, `table`, `crud`,
`page`, `route`, `viz`, `htmx`, `svg`) are leaves; `events` is the
single JS-only branch.

## Why this layout

The granular split implements the human's stated goal:

> *"small, clean and focused libraries — not everything will be open
> sourced, I will keep some or more of these as internal libraries
> only … I will use mill and publishLocally snapshots extensively to
> make this work on my side"*

Concretely:

1. **Independent publication.** Each artifact can flip
   open/closed-source individually. `tagless-htmx` ships freely
   even if `tagless-crud` stays internal.
2. **Minimal consumption surface.** A static-site generator that
   only needs the cursor DSL pulls `core` + `htmlid` + `i18n` (and
   their transitive deps: domtypes) — none of the form/table/viz
   weight.
3. **No speculative breadth.** The decomposition follows the
   *existing* internal package boundaries in the source's `tags`
   module (`tags/{form, table, meta, page, crud, route, viz, i18n}`
   plus `md`) and the *existing* sibling modules (`htmlid`, `htmx`,
   `svgelements` → `svg`, `eventhandler` → `events`). No new module
   is invented; the breakout makes the implicit topology explicit
   as artifacts.

## Build wiring

- Mill 1.1.2, JDK 21, Scala 3.8.3, Scala.js 1.20.1
- `object V` declares all versions inline in `build.mill`
- Shared trait `TaglessCommon extends CrossScalaModule with TaglessPublish`
  defines compiler flags, `sharedSrc = Task.Sources(moduleDir / os.up / "src")`
- `TaglessJs extends TaglessCommon with ScalaJSModule` adds Scala.js
  config (`scalaJSVersion`, ES2021 features)
- `HasSrcJvm` / `HasSrcJs` traits add `src-jvm/` / `src-js/` only where
  divergences exist (`core`, `form`)
- Per-module shape:
  ```scala
  object <module> extends Module:
    trait JvmModule extends TaglessCommon:
      override def artifactName = "tagless-<module>"
      override def moduleDeps   = Seq(...)
      override def mvnDeps      = super.mvnDeps() ++ Seq(...)
      object test extends ScalaTests, TaglessTest
    object jvm extends Cross[JvmModule](V.scalaVersions)
    trait JsModule extends TaglessCommon, ScalaJSModule: ...
    object js extends Cross[JsModule](V.scalaVersions)
  ```
- `mill __.compile` produces clean output across all 14 modules ×
  2 platforms (1 platform for `events`).

## Cross-cutting type choices

- **Zipper-based DSL.** `Cursor[D <: Depth, K <: ElementKind]` carries
  a focus node and an explicit `List[Context]` stack of unzipped
  left siblings + parent. Pure construction; rebuilding the tree
  happens via `seal` which folds the stack back through the focus.
- **Phantom depth tracking.** `D0` (root), `Succ[D]` (one level
  deeper). Operators that change depth carry the change through
  the type: `>>` returns `Cursor[Succ[D], Normal]`; `^` requires
  `D <: Succ[_]` and returns `Cursor[D - 1, _]`. Compile-time
  guarantees: cannot ascend past root, cannot add siblings at root,
  cannot add children to `Void` elements.
- **Type-state Form/Table grammars.** `Form[S <: FormState]` with
  `Init`, `Fields`, `InFieldset`, `Done` phantom states. Each
  operator's signature constrains the legal predecessors. Same
  pattern for `Table` with `Init → Caption? → ColGroup? → Head → Body → Footer?`.
- **Singleton-typed HTML IDs.** `HtmlId[S <: String]` is a phantom-
  typed opaque-string wrapper; `IdScope[P <: String]` composes
  prefix paths via `compiletime.ops.string.+`. Two IDs with
  different paths have *incompatible types*. `RouteScope` extends
  this with paired URL paths so route↔element-ID maps derive once.
- **Singleton-typed I18n keys.** `I18n[K <: String]` analogously
  fixes the translation key in the type; `TextScope[K] { Sub[S] }`
  nests scopes the same way `IdScope` does.

## Compliance scan against current normative pages

| Norm | Stance | Why |
|------|--------|-----|
| `tech/patterns/functional-domain-design` | **adopts** | Immutable ADT model (`Node`, `Tag`, `Attr`, `Cursor`), pure constructors (`Tag.normal`/`Tag.void`), operator algebra (`>>`, `>>^`, `>`, `>^`, `^`, `^^`, `\|`, `+`, `*`), explicit grammar encoding via phantom states (forms/tables) and phantom depth (cursor). No mutable builders. Form/Table even ship the `Init → … → Done` typestate verbatim. |
| `tech/decisions/deps-single-file` | **deviates while standalone** | Versions inline in `object V`. Standard breakout deviation; revisit if/when `tagless` lands inside a monorepo. |
| `tech/guides/mill-cross-platform` | **adopts** | `sharedSrc` task pattern via `os.up` path math, Cross variants `jvm`/`js`, src-jvm/src-js only where divergences exist, kebab-only single-word module names. |
| `tech/decisions/tidy-first-commits` | **no evidence yet** | Uncommitted tree at breakout time. |
| `tech/patterns/tdd-rhythm` | **no evidence yet** | No test-first commit history to evaluate; pre-existing upstream `Fragment.hiddenSection` test/source mismatch suggests the codebase has drifted from a strict TDD rhythm. |
| `tech/patterns/symmetric-refactoring` | **partial** | Cursor extensions ship in pairs (`>>` / `>>^`, `>` / `>^`, `^` / `^^`) — the *named pair* is part of the surface. The pairing convention is repeated in Form/Table operators but the symmetry-as-discipline isn't recorded as a separate ADR yet. |

## Observations worth flagging

1. **Pre-existing test bug** in `Fragment.hiddenSection`: source emits
   `class="hidden"`, two tests (DslSpec and IndexHtmlSpec) expect
   `class="is-hidden"`. Not introduced by the breakout — already
   broken upstream. Either patch the source or update the tests in
   the new repo's first follow-up commit.
2. **Package vs module-name mismatch** in three modules: `md`,
   `form`, `table`. `md` files declare `package md` (not `tags.md`),
   `form` declares `package html.lib.form`, `table` declares
   `package html.lib.table`. Preserved verbatim per breakout rule
   ("no source changes"). Worth a harmonization pass post-breakout.
3. **Core ↔ viz back-edge** in the source: `tags/dsl.scala` imported
   `tags.viz.{TreeVisualization, TreeVisualizer, ComponentMeta}` for
   the `visualize`/`toD3Json`/`toAsciiTree`/`toMermaid` cursor
   extensions, but `viz` already depended on `core`. The breakout
   moved those extensions into `viz/src/tags/viz/dsl.scala` (a
   `tags.viz.dsl.*` import scope) to break the cycle. Same treatment
   for `asRoute` → `route/src/tags/route/dsl.scala`. This is the
   only structural code change made during the breakout, and it is
   *purely additive* from the consumer's view (existing call sites
   need an extra `import tags.viz.dsl.*` / `import tags.route.dsl.*`).
4. **Core ↔ i18n implicit coupling.** `Fragment.options`,
   `simpleOptions`, `navItems`, `listItems` take `i18n.I18n[?]`
   parameters. `core` therefore acquired a hard dep on `i18n`, which
   slightly fattens it for consumers that don't want
   internationalization. A future split could move those four
   builders to a separate `tagless-fragment-i18n` module — not done
   now.
5. **TestI18n.scala is duplicated** across test modules that use the
   `String.i18n` extension. Cleaner alternative is a shared test-kit
   artifact; the duplication is the pragmatic choice for a breakout.
6. **`events` is JS-only by design.** Airstream has no JVM target,
   and the event-capture surface only makes sense at the document.
   No JVM `events` variant exists.

## Reachability

This page is reachable from:

- [[index]] §Projects (added in this ingest)
- [[projects/tagless]] §Code Location
- [[sources/raw/code/tagless]] (bridge)
- [[meta/log]] (ingest entry on 2026-05-29)

## Related Pages

- [[tech/guides/breakout]] — the procedure this breakout follows
- [[tech/guides/mill-cross-platform]] — the build pattern used
- [[tech/decisions/deps-single-file]] — the decision this breakout deviates from
- [[tech/patterns/functional-domain-design]] — the pattern this codebase adopts
- [[projects/toolbox]] — sibling fine-grained breakout
- [[projects/sourceline-manager]] — minimum-shape breakout

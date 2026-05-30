---
id: source-animdsl
type: code
repo: /p/hg/animdsl
last_observed: 2026-05-30
commit: uninitialized-tree
branch: main
git_init_state: fresh — `git init` on 2026-05-30, no commits yet
entry_points:
  - README.md
  - build.mill
  - flake.nix
  - core/src/animdsl/Timeline.scala
  - core/src/animdsl/Prop.scala
  - core/src/animdsl/Easing.scala
  - core/src/animdsl/Trigger.scala
  - core/src/animdsl/Fill.scala
  - core/src/animdsl/KF.scala
  - core/src/animdsl/RepeatCount.scala
  - core/src/animdsl/AnimBuilder.scala
  - core/src/animdsl/AnimBackend.scala
  - core/src/animdsl/Types.scala
  - core/src/animdsl/Nel.scala
  - core/src/animdsl/dsl.scala
  - svg/src/animdsl/svg/SvgBackend.scala
  - svg/src/animdsl/svg/SmilTiming.scala
  - svg/src/animdsl/svg/SvgAnimAttrs.scala
  - ooxml/src/animdsl/ooxml/OoxmlBackend.scala
  - ooxml/src/animdsl/ooxml/PTimingBuilder.scala
  - ooxml/src/animdsl/ooxml/IdCounter.scala
  - ooxml/src/animdsl/ooxml/OoxmlRender.scala
source_repo: /p/v42/tagless
design_source_of_truth: /p/v42/tagless/animdsl_specification_and_design.md
---

## Structure Overview

`animdsl` is the destination of the third of four sibling breakouts
from `/p/v42/tagless`. The source design document
`animdsl_specification_and_design.md` is the authoritative layout
spec (§6 "Module Layout") and is preserved alongside the source.
The breakout executes the module boundaries that document records:

| Source repo | Target module | Artifact |
|-------------|---------------|----------|
| `/p/v42/tagless/animdsl/` | `core` | `animdsl-core` |
| `/p/v42/tagless/animdslsvg/` | `svg` | `animdsl-svg` |
| `/p/v42/tagless/animdslooxml/` | `ooxml` | `animdsl-ooxml` |

A `git init` was performed (branch `main`, unsigned-commit config,
author `tigidar`); no initial commit has been recorded yet.

## Modules

| Module | Platforms | Deps | Artifact |
|--------|-----------|------|----------|
| `core` | JVM, JS | — | `animdsl-core` |
| `svg` | JVM, JS | `core` + `no.virtual-architect:tagless-core` (Maven) | `animdsl-svg` |
| `ooxml` | **JVM only** | `core` + `no.virtual-architect:tagless-core` (Maven) | `animdsl-ooxml` |

### No structural code changes during the breakout

Unlike tagless (three moves) and shapesdsl (one move), animdsl had
**zero** intra-module cycles in the source — `core` has no
references to `svg` or `ooxml`. The breakout is a pure relocation
with no source edits.

### Design-doc-vs-implementation divergences worth flagging

The design doc (`animdsl_specification_and_design.md`) §7 lists
`scala-xml` as a recommended dependency for the svg and ooxml
backends. The actual source repos use `tags.{Node, Attr}` from
tagless instead. The breakout preserves the actual implementation
(not the design doc's recommendation) — `animdsl-svg` and
`animdsl-ooxml` therefore depend on `tagless-core`, not `scala-xml`.

Flagged for a future design-doc refresh once the implementation has
stabilized.

## Build

- Mill 1.1.2, JDK 21, Scala 3.8.3, Scala.js 1.20.1
- `object V` inline; `V.tagless = "0.1.0-SNAPSHOT"` (publishLocal coord)
- `no.virtual-architect` group · `0.1.0-SNAPSHOT` version
- `mill __.compile` ✓ across 3 modules (core+svg on 2 platforms,
  ooxml JVM only — 5 compile targets total)
- `mill __.fastLinkJS` ✓
- `mill svg.jvm[3.8.3].test.testForked` ✓ (SvgAnimAttrsSpec only;
  ooxml has no tests in the source repo)
- `mill __.publishLocal` ✓ (5 artifacts published to `~/.ivy2/local`)

## Tests

Only `svg/test/src/animdsl/svg/SvgAnimAttrsSpec.scala` exists in
the source. No tests for `core` or `ooxml` were authored upstream.
Flagged as a follow-up — both modules deserve property-based
round-trip tests.

## Compliance scan

| Norm | Stance |
|------|--------|
| `tech/patterns/functional-domain-design` | **adopts** — `enum Timeline` (Atom/Seq/Par/Delayed/Repeated), `enum Prop`, `enum Easing`, `enum Trigger`, `enum Fill`, `enum RepeatCount`, `case class KF`, `AnimBackend[A]` typeclass for interpreters. Cleanest expression of the pattern in the breakout family so far. |
| `tech/decisions/deps-single-file` | **deviates** — versions inline in `object V` (standalone breakout, fifth consecutive deviation; see [[meta/log]]) |
| `tech/guides/mill-cross-platform` | **adopts** — `sharedSrc` + `os.up` pattern, kebab-only module names |

## Related

- [[sources/raw/code/tagless]] — consumed via `tagless-core`
- [[sources/tmp/shapesdsl]] — sibling breakout (not yet promoted)
- [[tech/guides/breakout]] — procedure followed

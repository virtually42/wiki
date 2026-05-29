---
id: summary-sourceline-manager
title: sourceline-manager (foundation library) — code summary
kind: descriptive
status: accepted
scope: global
created: 2026-05-29
updated: 2026-05-29
confidence: high
sources:
  - sources/raw/code/sourceline-manager.md
tags: [scala, scala-js, scala-native, mill, code-generation, functional-domain-design, dsl, monoid, library]
---

## What it is

`sourceline-manager` (artifact `no.virtual-architect:sourceline-manager`,
version `0.2.0-SNAPSHOT`, base package `slm`) is a foundation library
for generating source code as data. It exposes a small algebra over
three types:

| Type | Role |
|------|------|
| `Token` | `Value(String) \| Indent \| Ref(String)` — the atom |
| `SourceLine` | A sequence of tokens forming one line |
| `SourceFile` | A sequence of lines forming a file |
| `SourceFileBuilder` | Fluent builder over the immutable model |

Rendering is one explicit pure function per layer with parameterized
indent / token / line separators. The model carries no
language-specific knowledge — Scala, Bash, SQL, and any other target
language sit on the same algebra, with at most a thin per-language
renderer wrapper above it.

## Why it matters to this wiki

Two reasons:

1. **Reference implementation of [[tech/patterns/functional-domain-design]].**
   The project's in-tree ADRs 0001 and 0002 together produce the same
   shape the global pattern prescribes: immutable model, private
   primary constructors with public smart constructors, operators
   encoding algebra (`++` / `|+|` / `combine` / `joinLines`), explicit
   rendering, and monoid laws tested as part of the public contract.
   The encoding is **declarative**: a small ADT, transformations as
   total functions over the ADT, no opaque function carriers.

2. **The empty-jar incident.** Version 0.1.0 shipped empty jars on all
   three platforms because the `Cross[]` + manual `sharedSources`
   hybrid used `os.up / os.up` (which escapes to the repo root)
   instead of `os.up`. Mill reports compile-green and zero test
   failures when zero sources resolve. This incident is the
   load-bearing example in [[tech/guides/mill-cross-platform]]
   §Pitfalls and motivated the `mill show <module>.sources` +
   `jar tf` verification recipe documented there. Fixed in
   0.2.0-SNAPSHOT.

## The four ADRs

### ADR-0001 — Source code is data, not strings (accepted)

Models source code as an ADT (`Token` / `SourceLine` / `SourceFile`)
instead of `String` interpolation. Rationale: every concern
(indentation, variable references, escaping, composition,
substitution) survives as a first-class node and as a total function
over the ADT, instead of collapsing into character manipulation.
Alternatives considered: pretty-printer combinators (Wadler-style;
deferred until line-wrapping or budget-aware layout is actually
needed) and a tree of `SourceFile`s (rejected — `SourceFile` already
composes monoidally; nesting belongs in the caller's domain model).

### ADR-0002 — Functional domain design (accepted)

Codifies the seven principles that govern the core: immutable model,
private primary constructors with public smart constructors, operators
that encode algebra (with operator aliases — `++` / `|+|` / `combine`),
derived `CanEqual`, explicit encoding (no `Product`-introspection or
`toString` pretty-printing), total functions where possible (`Option`
returns instead of throws), and testable monoid laws. This ADR is the
project-local instantiation of the global pattern
[[tech/patterns/functional-domain-design]] in its **declarative**
encoding.

### ADR-0003 — Cross-platform via single-source-of-truth (accepted)

One source tree (`slm/src/`), three Mill modules (`slm.jvm`, `slm.js`,
`slm.native`) sharing the same sources via override of `sources`. The
library code uses only `scala.collection.immutable`, `Option`,
`String`, `Int`, and `derives CanEqual` — no reflection, no
`java.io`, no `java.util.concurrent`, no `js.Dynamic`. The
cross-platform constraint is met by *not having a platform surface*,
not by the build juggling sources. Rejected alternatives:
`PlatformScalaModule` with empty `src-{jvm,js,native}/` directories
(would mislead a reader into looking for differences that aren't
there); publish JVM only and ship the rest later (rejected — the
library exists to be shared across the toolbox).

### ADR-0004 — Scala version policy (accepted)

Wire `Cross[]` for cross-Scala-version publishing from day one but
pin the matrix to a single version (`3.8.3`) until the next LTS lands.
Appending `"3.9.0"` (or whatever 3.9 LTS ships as) to
`V.scalaVersions` should be the only change required to start
cross-publishing. The `Cross[]` machinery is established and tested
with a single value so failure modes are debugged before they matter.

## Core types — operator inventory

`SourceLine`:

- Combine: `++`, `|+|`, `combine`
- Prepend: `prefix`, `+:`, `prependAll`
- Append: `postfix`, `:+`, `appendAll`
- Transform: `indent(n)`, `map`, `flatMap`, `filter`, `reverse`
- Fold: `foldLeft`, `foldRight`
- Render: `render(indentStr, separator)`, `renderTokens(indentStr)`

`SourceFile`:

- Combine: `++`, `|+|`, `combine`
- Inline-merge (last line of left joined with first line of right): `joinLines`, `|++|`
- Append / prepend (tokens at the last line, or whole lines): `:+`, `+:`, `appendLine`, `prependLine`, `appendLines`, `prependLines`
- Transform: `indentAll`, `map`, `flatMap`, `filter`, `filterNot`, `dropEmpty`, `reverse`, `take`, `drop`, `slice`, `mapTokens`, `updateLine`, `updateLastLine`, `updateFirstLine`, `intersperse`, `zipWith`, `zipWithIndex`
- Fold / search: `foldLeft`, `foldRight`, `foldLines`, `find`, `exists`, `forall`, `count`, `indexWhere`
- Render: `render(indentStr, tokenSeparator, lineSeparator)`, `renderLines(indentStr, tokenSeparator)`

`SourceFileBuilder` is a fluent convenience layer that maintains a
running `SourceFile` + current `SourceLine`; the canonical API is the
value algebra, not the builder.

## Build wiring (Mill 1.1.2)

Single `build.mill` with `object V` declaring versions inline (no
`deps/Dependencies.mill` file — the project has one external library
dep, `munit`). Three `Cross[]` modules — `slm.jvm`, `slm.js`,
`slm.native` — each carrying a nested `test` object sharing the same
`slm/test/src/` tree. `flake.nix` provides JDK 21 + Mill + Scala
Native toolchain.

The cross-platform pattern is the `Cross[]` + manual `sharedSources`
hybrid catalogued in [[tech/guides/mill-cross-platform]] (closest to
Pattern B). Path math:

```
slm.jvm[3.8.3]       moduleDir == slm/jvm/         → moduleDir / os.up / "src"      lands on slm/src/
slm.jvm[3.8.3].test  moduleDir == slm/jvm/test/    → moduleDir / os.up / os.up / "test" / "src"
                                                                                    lands on slm/test/src/
```

## Compliance scan against current normative pages

| Page | In scope? | Stance | Evidence |
|------|-----------|--------|----------|
| [[tech/patterns/functional-domain-design]] | Yes (Scala, any domain) | **Adopts**, declarative encoding | ADR-0001 (ADT model), ADR-0002 (seven principles, monoid laws) |
| [[tech/decisions/deps-single-file]] | Yes (Scala, any domain) | **Deviates** | `build.mill` has `object V` inline, no `deps/Dependencies.mill`. One external library dep (`munit`), so the file-extraction overhead doesn't pay for itself. See [[projects/sourceline-manager/adr/0002-deviate-deps-single-file]]. |

No other accepted normative pages currently apply.

## Project status

Active. Stable algebra (monoid laws tested). One Scala version
(3.8.3) targeted today; cross-publish wiring already in place.
Embeddable into the monorepo by renaming `build.mill` to
`package.mill` and editing the header — no source or test changes
required.

## Links

- [[sources/raw/code/sourceline-manager]] — source pointer (bridge file)
- [[projects/sourceline-manager/index]]
- [[projects/sourceline-manager/adr/0001-adopt-functional-domain-design]]
- [[projects/sourceline-manager/adr/0002-deviate-deps-single-file]]
- [[tech/patterns/functional-domain-design]]
- [[tech/decisions/deps-single-file]]
- [[tech/guides/mill-cross-platform]]
- [[tech/stack/mill]]

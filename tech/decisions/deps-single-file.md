---
id: deps-single-file
title: Single Dependencies.mill file with inline coordinates
kind: normative
status: accepted
scope: global
created: 2026-05-24
updated: 2026-05-24
applies_to:
  languages: [scala, scala-native, scala-js]
  domains: [any]
  excludes: []
used_by: []
sources:
  - tech/guides/mill-dependency-management.md
supersedes: []
superseded_by: null
---

## Context

Projects currently use a two-file pattern: `deps/Versions.mill` (version
strings) and `deps/Dependencies.mill` (mvn coordinates referencing Versions).
This creates indirection, version drift across projects, and is hostile to
automated update tools (nested objects like `V.Lihaoyi.osLib` defeat regex parsers).

## Decision

Use a single `deps/Dependencies.mill` file with full Maven coordinates.
Drop `Versions.mill`.

```scala
// deps/Dependencies.mill
package build.deps
import mill.*, scalalib.*

// Grouped versions for multi-artifact libraries
private val kyoV   = "1.0-RC1"
private val tapirV = "1.11.11"

object Deps:
  val kyoCore    = mvn"io.getkyo::kyo-core::$kyoV"
  val kyoPrelude = mvn"io.getkyo::kyo-prelude::$kyoV"
  val tapirCore  = mvn"com.softwaremill.sttp.tapir::tapir-core::$tapirV"
  val osLib      = mvn"com.lihaoyi::os-lib::0.11.7"
  val munit      = mvn"org.scalameta::munit::1.2.1"

object Platform:
  val scala       = "3.8.2"
  val scalaNative = "0.5.10"
  val scalaJS     = "1.20.2"
```

### Rules

- One file, one place per dependency
- Multi-artifact libraries (Kyo, Tapir) use a `private val` for the shared version
- Single-artifact libraries inline the version in the `mvn"..."` string
- Platform versions live in the same file as `object Platform`
- No nested version objects, no `lazy val`, no separate Versions file

## Consequences

- Scala Steward or Renovate can parse `mvn"group::artifact::version"` strings directly
- Version drift between projects eliminated (monorepo has one `Dependencies.mill`)
- One place to look when checking or bumping a version
- Trade-off: bumping Tapir touches one `private val` line, not N mvn strings — acceptable

## Alternatives Considered

- **Keep Versions.mill + Dependencies.mill split** — rejected: indirection without value, hostile to automation
- **TOML sidecar for versions** — rejected: adds a parser dependency and two-file maintenance
- **Mill BOM support** — deferred: Scala ecosystem doesn't publish BOMs; useful only for Java interop deps

## Links

- [[tech/guides/mill-dependency-management]]
- [[tech/stack/mill]]

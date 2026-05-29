---
id: shapesdsl-adr-0002
title: Deviate from deps-single-file while standalone
kind: normative
status: accepted
project: shapesdsl
created: 2026-05-29
compliance:
  adopts: []
  exceptions: []
  deviations:
    - tech/decisions/deps-single-file.md
  ignores: []
supersedes: []
---

## Context

[[tech/decisions/deps-single-file]] mandates a single source-of-truth
file for external library coordinates and platform versions. The
decision assumes a monorepo or shared-build context.

`shapesdsl` at breakout time is a **standalone repository** at
`/p/hg/shapesdsl`. There is no enclosing monorepo and no central
`deps/` to reference. Per `tech/guides/breakout` §Phase 4, versions
are inlined in an `object V` block at the top of `build.mill`,
including the cross-repo SNAPSHOT coordinate for `tagless-core`:

```scala
object V {
  val scala          = "3.8.3"
  val scalaVersions  = Seq(scala)
  val scalaJS        = "1.20.1"
  val organization   = "no.virtual-architect"
  val projectVersion = "0.1.0-SNAPSHOT"
  val tagless        = "0.1.0-SNAPSHOT"   // cross-repo publishLocal
  val munit          = "1.2.1"
  // ...
}
```

This is the fourth consecutive breakout to deviate from the
decision: [[projects/sourceline-manager/adr/0002-deviate-deps-single-file]],
[[projects/toolbox/adr/0002-deviate-deps-single-file]] (since
superseded by adoption), [[projects/tagless/adr/0002-deviate-deps-single-file]],
and now this one.

## Decision

Deviate from [[tech/decisions/deps-single-file]] for the duration
of `shapesdsl`'s standalone life. Revisit when:

- shapesdsl is embedded into a monorepo with a central `deps/`
- `dm` (dependency-manager) becomes the canonical source of Maven
  coordinates and shapesdsl opts in
- A carve-out in [[tech/decisions/deps-single-file]] itself
  formalizes the "fine-grained standalone breakout" exception

## Consequences

- Adding a new external dep requires two edits: a constant in
  `object V` and an `mvn"..."` reference in the consuming module.
  Acceptable for a 3-module repo.
- Cross-repo SNAPSHOT coordinates (currently `V.tagless`) are
  managed the same way as external libs — no special handling.
  Bumping the upstream version is a single `V.tagless = "..."` edit.
- When the migration to a monorepo or `dm` happens, this ADR is
  superseded by an `adopt-deps-single-file` ADR — the same
  trajectory toolbox followed.

## Related

- [[tech/decisions/deps-single-file]] — global decision
- [[projects/sourceline-manager/adr/0002-deviate-deps-single-file]]
- [[projects/toolbox/adr/0002-deviate-deps-single-file]] — superseded
- [[projects/toolbox/adr/0003-adopt-deps-single-file]] — trajectory
- [[projects/tagless/adr/0002-deviate-deps-single-file]] — sibling

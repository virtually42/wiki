---
id: tagless-adr-0002
title: Deviate from deps-single-file while standalone
kind: normative
status: accepted
project: tagless
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

[[tech/decisions/deps-single-file]] mandates that external library
coordinates and platform versions live in a single source-of-truth
file consumed by every module's `build.mill`. The decision is
written assuming a monorepo or shared-build context where a central
`deps/Dependencies.mill` (or `dm`-generated equivalent) can be
maintained.

`tagless` at breakout time is a **standalone repository** at
`/p/hg/tagless`. There is no enclosing monorepo and no central
`deps/` to reference. Following `tech/guides/breakout` §Phase 4, the
versions are inlined as an `object V` block at the top of
`build.mill`:

```scala
object V {
  val scala          = "3.8.3"
  val scalaVersions  = Seq(scala)
  val scalaJS        = "1.20.1"

  val organization   = "no.virtual-architect"
  val projectVersion = "0.1.0-SNAPSHOT"

  val domtypes  = "19.0.0"
  val airstream = "17.2.1"
  val raquoEw   = "0.2.0"

  val munit            = "1.2.1"
  val munitScalaCheck  = "1.1.0"
  val osLib            = "0.11.5"
  val pprint           = "0.9.4"
  val sourcecode       = "0.4.4"
}
```

Every module reads from `V.*`. The single-source-of-truth invariant
is preserved *within* this repository; the deviation is from the
*shared-across-projects* form of the decision.

This is the same deviation [[projects/sourceline-manager/adr/0002-deviate-deps-single-file]]
records, and the same deviation [[projects/toolbox]] recorded prior
to its dm-migration (see
[[projects/toolbox/adr/0002-deviate-deps-single-file]] — superseded
on 2026-05-29 by ADR-0003 once toolbox adopted dm). `tagless` is
expected to follow the same trajectory if/when it joins a monorepo
or migrates to `dm`.

## Decision

Deviate from [[tech/decisions/deps-single-file]] for the duration of
`tagless`'s standalone life. Version constants live in `object V`
in `build.mill`. Revisit if:

- `tagless` is embedded into a monorepo with a central `deps/`
- `dm` (dependency-manager) becomes the canonical source of Maven
  coordinates and `tagless` opts in
- A third project starts deviating with the same shape — at that
  point [[tech/decisions/deps-single-file]] itself may warrant a
  carve-out for fine-grained breakouts rather than per-project
  ADRs.

## Consequences

- Adding a new external dependency requires two edits: a constant
  in `object V` and an `mvn"..."` reference in the consuming
  module's `mvnDeps`. Acceptable for a 14-module repo.
- Bumping a shared version (e.g. `munit`) is a single edit in
  `object V`; the wiring is already centralised within the repo.
- When the migration to a monorepo or `dm` happens, this ADR is
  superseded by an `adopt-deps-single-file` ADR — the same
  trajectory toolbox followed.

## Related

- [[tech/decisions/deps-single-file]] — global decision this ADR
  deviates from
- [[projects/sourceline-manager/adr/0002-deviate-deps-single-file]]
  — minimum-shape precedent
- [[projects/toolbox/adr/0002-deviate-deps-single-file]] — initial
  toolbox deviation (since superseded)
- [[projects/toolbox/adr/0003-adopt-deps-single-file]] — the
  trajectory `tagless` is expected to follow once it joins a
  monorepo or migrates to dm

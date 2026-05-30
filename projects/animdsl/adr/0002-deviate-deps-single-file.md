---
id: animdsl-adr-0002
title: Deviate from deps-single-file while standalone
kind: normative
status: accepted
project: animdsl
created: 2026-05-30
compliance:
  adopts: []
  exceptions: []
  deviations:
    - page: tech/decisions/deps-single-file.md
      rationale: |
        `animdsl` at breakout time is a standalone repository at
        `/p/hg/animdsl`. There is no enclosing monorepo and no
        central `deps/` to reference. Per `tech/guides/breakout`
        §Phase 4, version constants are inlined in an `object V`
        block at the top of `build.mill`, including the cross-repo
        SNAPSHOT coordinate for `tagless-core` (`V.tagless`).
        The single-source-of-truth invariant is preserved within
        the repository — the deviation is from the
        shared-across-projects form of the decision.

        Fifth consecutive breakout to deviate (after slm/0002,
        toolbox/0002 superseded, tagless/0002, shapesdsl/0002).
        The carve-out hypothesis is now over-determined; a
        "fine-grained standalone breakout" exception in
        [[tech/decisions/deps-single-file]] itself is the
        recommended next step, marking the existing per-project
        deviation ADRs as `superseded` once that lands.
      severity: low
      mitigated_by: |
        - `object V` is the single source of truth within the repo;
          all 3 modules consume the same constants. Cross-repo
          SNAPSHOT coordinates (currently `V.tagless`) flow through
          the same mechanism.
        - Renovate can still parse the inline `mvn"…::${V.x}"`
          coordinates if pointed at `build.mill`.
        - Two explicit expiry conditions: (a) embedding in a
          monorepo with a central `deps/`, (b) opting into the dm
          catalog. Either condition supersedes this ADR with an
          `adopt-deps-single-file` ADR (the toolbox/0003
          trajectory).
  ignores: []
supersedes: []
---

## Context

[[tech/decisions/deps-single-file]] mandates a single source-of-
truth file for external library coordinates and platform versions.
The decision assumes a monorepo or shared-build context.

`animdsl` at breakout time is a **standalone repository** at
`/p/hg/animdsl`. Per `tech/guides/breakout` §Phase 4, versions are
inlined in an `object V` block:

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

This is the **fifth consecutive** breakout to deviate from the
decision:
[[projects/sourceline-manager/adr/0002-deviate-deps-single-file]],
[[projects/toolbox/adr/0002-deviate-deps-single-file]] (since
superseded by adoption),
[[projects/tagless/adr/0002-deviate-deps-single-file]],
[[projects/shapesdsl/adr/0002-deviate-deps-single-file]], and now
this one.

## Decision

Deviate from [[tech/decisions/deps-single-file]] for the duration
of `animdsl`'s standalone life. Revisit when:

- animdsl is embedded into a monorepo with a central `deps/`
- `dm` (dependency-manager) becomes the canonical source of Maven
  coordinates and animdsl opts in
- A carve-out in [[tech/decisions/deps-single-file]] itself
  formalizes the "fine-grained standalone breakout" exception

## Consequences

- Cross-repo SNAPSHOT coordinates (currently `V.tagless`) are
  managed the same way as external libs. Adding a future
  `V.shapesdsl` (if presenter ends up consuming shapesdsl via
  animdsl) is a single-line addition.
- When the migration to a monorepo or `dm` happens, this ADR is
  superseded by an `adopt-deps-single-file` ADR — the same
  trajectory toolbox followed.

## Related

- [[tech/decisions/deps-single-file]] — global decision
- [[projects/sourceline-manager/adr/0002-deviate-deps-single-file]]
- [[projects/toolbox/adr/0002-deviate-deps-single-file]] — superseded
- [[projects/toolbox/adr/0003-adopt-deps-single-file]] — trajectory
- [[projects/tagless/adr/0002-deviate-deps-single-file]] — sibling
- [[projects/shapesdsl/adr/0002-deviate-deps-single-file]] — sibling

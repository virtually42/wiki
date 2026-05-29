---
id: toolbox-adr-0002
title: Deviate from single-file Dependencies.mill (while standalone)
kind: normative
status: superseded
project: toolbox
created: 2026-05-29
superseded_by:
  - projects/toolbox/adr/0003-adopt-deps-single-file.md
compliance:
  adopts: []
  exceptions: []
  deviations:
    - page: tech/decisions/deps-single-file.md
      rationale: |
        `toolbox` declares its dependencies inline in `build.mill` via
        `object V` — platform versions (`scalaJS`, `scalaNative`),
        eight library coordinates (`osLib`, `kyoCore`, `catsEffect`,
        `fs2`, `slm`, `munit`, `munitCatsEffect`, `pprint`,
        `sourcecode`), organization, version. There is no
        `deps/Dependencies.mill` file.

        Unlike sourceline-manager (which has a single library
        dependency and a weak file-extraction case), `toolbox` has
        eight library coordinates and the file-extraction case is
        *stronger* here, not weaker. The reason for deviating is
        therefore not "the rule does not pay for itself" but
        "the rule will be satisfied by construction at monorepo
        embedding, and pre-creating `deps/Dependencies.mill` in a
        standalone repository is throwaway work."

        The new-design migration plan and README both treat
        `/p/hg/toolbox` as the destination of a source-of-truth
        re-layout that is *itself* a precursor to monorepo embedding.
        Inserting a deps-file conformance step between Phase A
        (module layout) and the monorepo migration would extend the
        path without changing the destination.
      severity: medium
      mitigated_by: |
        - `build.mill` keeps a single `object V` block as the only
          place version literals appear; per-module `mvnDeps`
          reference `V.kyoCore` / `V.osLib` / etc. via `mvn"…::${V.x}"`,
          so Scala Steward / Renovate can still parse every
          coordinate inline.
        - At monorepo embedding (per `new-design.md` and README),
          `object V` is replaced by references to the monorepo's
          `deps/Dependencies.mill`, and this deviation evaporates by
          construction.
        - The deviation is *medium* severity, not low like
          sourceline-manager's, because the dep count makes the
          monorepo-conformance ask substantive rather than cosmetic.
          Honest labelling.
  ignores: []
supersedes: []
---

> **Superseded 2026-05-29** by
> [[projects/toolbox/adr/0003-adopt-deps-single-file]]. The
> migration to the dm-managed `deps/Dependencies.mill` resolved
> the library-coordinates half; the platform-versions half is
> the remaining narrow exception codified in the superseding
> ADR. This document is retained as the reasoning history for
> the deviation's original premise.

## Context

[[tech/decisions/deps-single-file]] (accepted 2026-05-24, global
scope, `applies_to.languages: [scala, scala-native, scala-js]`)
requires Scala projects to declare dependencies in a single
`deps/Dependencies.mill` file with inline Maven coordinates.

`toolbox` is in scope (Scala / Scala.js / Scala Native, any domain)
but currently declares dependencies a different way:

```scala
// build.mill (excerpt)
object V {
  val scalaVersions = Seq("3.8.3")

  val scalaJS     = "1.20.1"
  val scalaNative = "0.5.12"
  val munit       = "1.0.3"

  val osLib      = "0.11.7"
  val kyoCore    = "1.0-RC1"
  val catsEffect = "3.6.1"
  val fs2        = "3.12.0"
  val slm        = "0.2.0-SNAPSHOT"
  val pprint     = "0.9.4"
  val sourcecode = "0.4.4"
  val munitCatsEffect = "2.1.0"

  val organization   = "no.virtual-architect"
  val projectVersion = "0.1.0-SNAPSHOT"
}
```

There is no `deps/` directory and no `Dependencies.mill` file. The
eight library coordinates are referenced per-module via
`mvn"<org>::<artifact>::${V.x}"` in each module's `mvnDeps`.

## Decision

Deviate from [[tech/decisions/deps-single-file]]. Continue to
declare dependencies inline in `build.mill` via `object V` while
`toolbox` is a standalone repository.

Conditions under which this deviation expires:

1. **Monorepo embedding** (per `new-design.md` and README) replaces
   `object V` with references to `build.deps.Dependencies` /
   `build.deps.Platform`. Conformance with the global decision then
   happens by construction. This is the expected resolution path.
2. **Independent dep-set growth** to a degree where the
   `build.mill` `object V` block becomes visually unwieldy
   (subjective threshold; revisit at ~15 library coordinates) — at
   that point the file-extraction trade-off flips even while
   standalone.

Either condition is a trigger to revise this ADR.

## Consequences

- `meta/drift.md` should not flag `toolbox` under
  *missing-declaration* for `deps-single-file` — the declaration
  exists, it is a deviation, and the expiry conditions are recorded.
- Scala Steward / Renovate continue to work against the inline
  `mvn"…::${V.x}"` coordinates; no automation is sacrificed.
- A future automated check that diffs every project's
  `deps/Dependencies.mill` for version drift will not include
  `toolbox` until it joins the monorepo, which is the desired
  behaviour (the standalone version-set is not the canonical one
  yet).
- This is the **second deviation** recorded against
  `deps-single-file` — the first is
  [[projects/sourceline-manager/adr/0002-deviate-deps-single-file]].
  Both deviations share the "embed into monorepo to conform"
  resolution path. If a third project lands with the same shape,
  consider whether the global decision needs to grow a "standalone
  pre-embedding" carve-out, rather than each project deviating.

## Alternatives Considered

- **Adopt unconditionally and create `deps/Dependencies.mill` now.**
  Rejected: would be deleted at monorepo embedding (the embedding
  path explicitly replaces it with monorepo references). The
  deviation is honest about a cost / benefit that flips at
  embedding time.
- **`ignores`.** Rejected: the decision applies (in-scope Scala
  project, eight library deps). Honest deviation with expiry
  conditions is better than silent ignore.
- **Wait until embedding and don't write this ADR.** Rejected:
  would leave `toolbox` flagged as missing-declaration in
  [[meta/drift]] and obscure the fact that the question has been
  considered.

## Links

- [[tech/decisions/deps-single-file]]
- [[tech/guides/mill-dependency-management]]
- [[tech/stack/mill]]
- [[sources/summaries/toolbox]]
- [[sources/tmp/toolbox]]
- [[projects/sourceline-manager/adr/0002-deviate-deps-single-file]] — sibling deviation
- [[projects/compositor/adr/0002-adopt-deps-single-file]] — sibling adoption (forward-looking, code not yet stood up)
- `/p/hg/toolbox/build.mill` — `object V` declaration site
- `/p/v42/toolbox/new-design.md` — design source of truth, references monorepo embedding

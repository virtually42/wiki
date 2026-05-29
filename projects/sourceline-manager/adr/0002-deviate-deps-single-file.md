---
id: sourceline-manager-adr-0002
title: Deviate from single-file Dependencies.mill
kind: normative
status: superseded
project: sourceline-manager
created: 2026-05-29
superseded_by:
  - projects/sourceline-manager/adr/0006-adopt-deps-single-file.md
compliance:
  adopts: []
  exceptions: []
  deviations:
    - page: tech/decisions/deps-single-file.md
      rationale: |
        sourceline-manager declares its dependencies inline in `build.mill`
        via `object V` (one external library — `munit` — plus platform
        versions, organization, artifact name, version). There is no
        `deps/Dependencies.mill` file.

        The single-file decision targets two concerns: (1) automated
        update tools (Scala Steward, Renovate) parsing `mvn"…"` strings,
        and (2) eliminating version drift across projects in a monorepo.

        Neither applies here in the same way:
        - Only one library coordinate exists (`munit`). The `mvn"…"`
          string is already inline; Steward / Renovate can parse it where
          it sits. There is no `deps/Versions.mill` indirection to
          rejecto in the first place.
        - The library is a *standalone repository*, not a monorepo member
          today. Version drift across sibling projects is not a concern
          until embedding into the monorepo, at which point the `object V`
          values are replaced by references to the monorepo's
          `deps/Dependencies.mill` (per the README's embedding section)
          and this deviation evaporates.
      severity: low
      mitigated_by: |
        Embedding into the monorepo (per `README.md` §"Embedding in a
        monorepo") naturally converts the inline `object V` into
        references to `deps/Dependencies.mill` / `deps/Platform`, at
        which point this project automatically conforms.

        Until then, the single inline coordinate (`mvn"org.scalameta::munit::${V.munit}"`)
        is parseable by Steward / Renovate without indirection.
  ignores: []
supersedes: []
---

> **Superseded 2026-05-29** by
> [[projects/sourceline-manager/adr/0006-adopt-deps-single-file]].
> The migration to the dm-managed
> `deps/Dependencies.mill` resolved the library-coordinates half;
> the platform-versions half is the remaining narrow exception
> codified in the superseding ADR. This document is retained as
> the reasoning history for the deviation's original premise.

## Context

[[tech/decisions/deps-single-file]] (accepted 2026-05-24, global
scope, `applies_to.languages: [scala, scala-native, scala-js]`)
requires Scala projects to declare dependencies in a single
`deps/Dependencies.mill` file with inline Maven coordinates.

`sourceline-manager` is in scope (Scala / Scala.js / Scala Native,
any domain) but currently declares dependencies a different way:

```scala
// build.mill (excerpt)
object V {
  val scalaVersions = Seq("3.8.3")
  val scalaJS     = "1.20.1"
  val scalaNative = "0.5.12"
  val munit       = "1.0.3"

  val organization   = "no.virtual-architect"
  val artifact       = "sourceline-manager"
  val projectVersion = "0.2.0-SNAPSHOT"
}
```

There is no `deps/` directory and no `Dependencies.mill` file. The
project has exactly one library dependency (`munit`, used by the
test modules) and three platform versions (`scalaVersions`,
`scalaJS`, `scalaNative`).

## Decision

Deviate from `tech/decisions/deps-single-file.md`. Continue to
declare dependencies inline in `build.mill` via `object V` while
`sourceline-manager` is a standalone repository.

Conditions under which this deviation expires:

1. The library gains a second external library dependency. At that
   point the inline-vs-file trade-off flips and a `deps/Dependencies.mill`
   pulled out of `build.mill` becomes the cleaner shape.
2. The library is embedded into the monorepo (per README §"Embedding
   in a monorepo"). The embedding path explicitly replaces `object V`
   with references to `build.deps.{Platform, Deps}`, so conformance
   with the global decision happens by construction.

Either condition is a trigger to revise this ADR.

## Consequences

- `meta/drift.md` should not flag this project under
  *missing-declaration* for `deps-single-file` — the declaration
  exists, it is a deviation, and the conditions under which it
  expires are recorded above.
- Scala Steward / Renovate continue to work against the inline
  `mvn"org.scalameta::munit::${V.munit}"` coordinate; no automation
  is sacrificed by the deviation.
- A future automated check that diffs every project's
  `deps/Dependencies.mill` for version drift will simply not include
  this project until it joins the monorepo, which is the desired
  behaviour.

## Alternatives Considered

- **Adopt unconditionally and create a near-empty `deps/Dependencies.mill`.**
  Rejected: a one-coordinate file is ceremony without payoff while
  the library is standalone, and the embedding path would then have
  to delete it again. The deviation is honest about the cost / benefit.
- **`ignores`.** Rejected: the decision does apply (Scala project, in
  scope); we just disagree with the prescription in this specific
  configuration. Honest deviation is better than silent ignore.
- **Wait until embedding and don't write this ADR.** Rejected: would
  leave the project flagged as missing-declaration in `meta/drift.md`
  and obscure the fact that the question has been considered.

## Links

- [[tech/decisions/deps-single-file]]
- [[tech/guides/mill-dependency-management]]
- [[tech/stack/mill]]
- [[sources/summaries/sourceline-manager]]
- `/p/hg/sourceline-manager/build.mill`
- `/p/hg/sourceline-manager/README.md` (§"Embedding in a monorepo")

---
id: safetensors-scala-adr-0001
title: Adopt single-file Dependencies.mill (library coords via dm; platforms inline)
kind: normative
status: accepted
project: safetensors-scala
created: 2026-05-29
compliance:
  adopts:
    - tech/decisions/deps-single-file.md
  exceptions:
    - page: tech/decisions/deps-single-file.md
      rationale: |
        `object Platform` (Scala / ScalaJS / ScalaNative versions) is
        not produced. Platform versions remain inline in `build.mill`'s
        `object V` (`scalaVersions`, `scalaJS`, `scalaNative`),
        alongside project-internal metadata (`organization`,
        `artifact`, `projectVersion`).

        Rationale: dm (see
        [[projects/dependency-manager/designs/dm-architecture]])
        intentionally does not manage platform versions — Renovate's
        Maven manager model does not cover them, and conflating
        Maven coords with platform strings in `libs.versions.toml`
        would be a wrong shape. The library coordinates half of
        the decision is satisfied via the dm-generated
        `deps/Dependencies.mill`; the `object Platform` half is the
        narrow remaining exception.
      severity: low
      mitigated_by: |
        - `build.mill` `object V` retains only platform versions and
          project-internal metadata. All 3 external Maven library
          coordinates (`munit`, `munit-scalacheck`, `scodec-core`)
          are sourced from `build.deps.Deps.*`.
        - The **scodec-core pin** (2.3.3, palladium-resolution) that
          motivated the original in-tree ADR-0001 is now held by the
          central catalog
          (`/p/hg/dependency-manager/deps/libs.versions.toml`).
          Future palladium-side drift is caught by `dm verify` /
          `dm promote` instead of relying on memory of the inline
          pin's reason.
        - If a future Renovate manager (or replacement bot) grows
          platform-version awareness, the open question in
          [[projects/dependency-manager/designs/dm-architecture-2026q2-refresh]]
          §"Open questions" is the place to revisit.
  deviations: []
  ignores: []
supersedes: []
---

## Context

[[tech/decisions/deps-single-file]] (accepted 2026-05-24, global
scope) requires Scala projects to declare dependencies in a
single `deps/Dependencies.mill` file with inline `mvn"…"`
coordinates.

`safetensors-scala` is the only consumer that did *not* carry a
prior wiki-side ADR on this decision — the equivalent record
lived in-tree at
`/p/hg/safetensors-scala/docs/adr/0001-inline-versions.md`
("inline versions; scodec pinned to palladium's resolution").
That in-tree ADR pre-dated the wiki/dm pipeline; this wiki ADR
is the first to record safetensors-scala's stance on
`deps-single-file`.

Up to 2026-05-29, the project declared its 3 external Maven
deps inline (`munit`, `munit-scalacheck`, `scodec-core`) in
`build.mill`'s `object V`. The scodec pin (2.3.3) was held
inline with an explanatory comment.

On 2026-05-29, safetensors-scala migrated to consume
`build.deps.Deps.{munit, munitScalacheck, scodecCore}` from
the dm-generated `deps/Dependencies.mill`. The scodec-pin
moved from inline `V.scodec = "2.3.3"` to the central catalog
(version unchanged, owner of the pin moved). See
[[projects/dependency-manager/log]] §"safetensors-scala
migrated to dm catalog (DM-002)" and
[[projects/safetensors-scala/log]] §"build.mill migrated to dm
catalog (DM-002)" for the migration record.

This ADR records the resulting conformance with
[[tech/decisions/deps-single-file]], with a narrow exception
for platform versions.

## Decision

Adopt [[tech/decisions/deps-single-file]] for **external Maven
library coordinates**. These now live in
`/p/hg/safetensors-scala/deps/Dependencies.mill`, auto-generated
by `dm regen` from the catalog at
`/p/hg/dependency-manager/deps/`.

Continue to inline:

- **Platform versions** (`scalaVersions`, `scalaJS`,
  `scalaNative`) — dm boundary.
- **Project-internal metadata** (`organization`, `artifact`,
  `projectVersion`) — not Maven coordinates.

The Mill 1.x discovery anchor `deps/package.mill` (one line:
`package build.deps`) is required for Mill to discover the
generated `Dependencies.mill`. Safetensors-scala's anchor was
added on 2026-05-29 as part of the DM-002 migration.

## Consequences

- `deps-single-file`'s automation goal is met for all 3 external
  Maven deps. Renovate parses the central catalog; `dm regen`
  rewrites `safetensors-scala/deps/Dependencies.mill`; Mill
  picks up the change at the next compile.
- **scodec pin transferred** from inline ownership to the
  central catalog. The pin itself is unchanged (2.3.3); future
  drift is caught by `dm verify` / `dm promote` rather than
  relying on a comment in `object V` to remind a future editor.
- Cross-project version drift on external deps is eliminated by
  construction (the catalog is shared with slm and toolbox; the
  common dep `munit` cannot drift apart).
- Narrow exception remains for platform versions; documented in
  the `compliance.exceptions` block above. Severity `low`.
- The in-tree
  `/p/hg/safetensors-scala/docs/adr/0001-inline-versions.md`
  now describes a state that no longer holds for the
  library-coords half. The in-tree ADR may be updated in a
  follow-up (human-owned, in-tree edit) — not blocking for this
  wiki ADR.
- `meta/drift.md` should now flag this project as **adopting**
  `deps-single-file` (with the platform-versions exception),
  not "missing-declaration" as it would have appeared otherwise.

## Alternatives Considered

- **Adopt unconditionally including `object Platform`.**
  Rejected: same reason as the slm and toolbox sibling ADRs —
  dm intentionally does not manage platform versions, and
  conflating shapes in `libs.versions.toml` would be a wrong
  move. Wait for either a Renovate manager that covers
  platforms or a different bot.
- **Mirror the in-tree ADR-0001 into the wiki as a deviation
  instead.** Rejected: the migration already happened; mirroring
  a deviation that no longer holds would be a fresh form of
  ADR rot. Adopting with a narrow exception is the honest
  current state.
- **Wait for the human to rewrite the in-tree ADR first.**
  Rejected: the wiki ADR is the normative surface dm cares
  about (linting, drift detection, used_by graph). The in-tree
  ADR can lag without breaking the wiki invariants.

## Links

- [[tech/decisions/deps-single-file]]
- [[projects/dependency-manager/index]]
- [[projects/dependency-manager/designs/dm-architecture]]
- [[projects/dependency-manager/log]] (DM-002 entry)
- [[projects/safetensors-scala/log]] (2026-05-29 migration entry)
- `/p/hg/safetensors-scala/build.mill`
- `/p/hg/safetensors-scala/deps/Dependencies.mill` (generated)
- `/p/hg/safetensors-scala/deps/package.mill` (Mill 1.x anchor)
- `/p/hg/safetensors-scala/docs/adr/0001-inline-versions.md` (in-tree predecessor)

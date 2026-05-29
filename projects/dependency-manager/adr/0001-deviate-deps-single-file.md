---
id: dependency-manager-adr-0001
title: Deviate from single-file Dependencies.mill (dm is the tool)
kind: normative
status: accepted
project: dependency-manager
created: 2026-05-29
compliance:
  adopts: []
  exceptions: []
  deviations:
    - page: tech/decisions/deps-single-file.md
      rationale: |
        `dm`'s own `build.mill` declares dependencies inline via
        `object V` — six library coordinates (`toolbox` × 3 modules,
        `tomlScala`, `scalaYaml`, `ujson`, `munit`) plus platform
        versions and organisation / artifact metadata. There is no
        `deps/Dependencies.mill` file in this project.

        The deviation is structural, not pragmatic: `dm` is the *tool*
        that produces compliant `deps/Dependencies.mill` files in
        *other* repos. The `deps/` directory in
        `/p/hg/dependency-manager/` is reserved for the central catalog
        (`libs.versions.toml` + `projects.yml`), not for a generated
        per-project deps file. The chicken-and-egg of
        "tool that manages dep catalogs needs its own dep catalog
        before it can run" is resolved by hand-authoring `object V`
        once at bootstrap.

        Unlike the analogous deviations in
        [[projects/sourceline-manager/adr/0002-deviate-deps-single-file]]
        (one library; rule does not pay) and
        [[projects/toolbox/adr/0002-deviate-deps-single-file]]
        (eight libraries; resolved at monorepo embedding), the dm
        deviation has a *third* shape — the project is the
        implementation of a generalised version of the decision and
        cannot bootstrap to its own output without first having an
        `object V` to read from.
      severity: medium
      mitigated_by: |
        - `build.mill` keeps a single `object V` block as the only
          place version literals appear. Per-module `mvnDeps`
          reference `V.toolbox` / `V.tomlScala` / etc. via
          `mvn"…::${V.x}"`, so Renovate's regex coordinate parser
          can still pick up every coordinate inline if pointed at
          this file.
        - The deviation is **structurally resolvable** in two ways:
          (a) at `/p/factory/` monorepo embedding (if that absorbs
          dm; per `DESIGN.md` open question), `object V` becomes
          monorepo deps references; (b) when `dm extract` runs
          against itself once `dm` is a published artifact, dm's own
          deps can flow through the catalog like any other repo —
          the bootstrap `object V` becomes the regenerated
          `deps/Dependencies.mill` and the deviation evaporates.
          Until either condition holds, the inline `object V` is the
          intentional bootstrap shape.
        - Severity is **medium**, matching toolbox rather than
          sourceline-manager: six library coordinates is non-trivial
          and the file-extraction case has weight. The honest label
          is "the rule applies and we're choosing not to satisfy it
          *in dm itself* because the path is wrong, not because the
          cost is wrong."
  ignores: []
supersedes: []
---

## Context

[[tech/decisions/deps-single-file]] (accepted 2026-05-24, global
scope, `applies_to.languages: [scala, scala-native, scala-js]`)
requires Scala projects to declare dependencies in a single
`deps/Dependencies.mill` file with inline Maven coordinates.

`dependency-manager` is in scope (Scala / JVM, any domain) but
currently declares its dependencies a different way:

```scala
// build.mill (excerpt)
object V {
  val scala = "3.8.3"

  val toolbox   = "0.1.0-SNAPSHOT"
  val tomlScala = "0.3.0"
  val scalaYaml = "0.3.1"
  val ujson     = "3.3.1"
  val munit     = "1.0.3"

  val organization   = "no.virtual-architect"
  val projectVersion = "0.1.0-SNAPSHOT"
}

object dm extends ScalaModule {
  def mvnDeps = Seq(
    mvn"no.virtual-architect::toolbox-script::${V.toolbox}",
    mvn"no.virtual-architect::toolbox-proc-oslib::${V.toolbox}",
    mvn"no.virtual-architect::toolbox-fluent::${V.toolbox}",
    mvn"com.indoorvivants::toml::${V.tomlScala}",
    mvn"org.virtuslab::scala-yaml::${V.scalaYaml}",
    mvn"com.lihaoyi::ujson::${V.ujson}"
  )
  // ...
}
```

There is no `deps/Dependencies.mill` and no plan to add one — `deps/`
in this repo is reserved for the central catalog (`libs.versions.toml` +
`projects.yml`) that dm itself manages.

The unique angle of this deviation, captured in `DESIGN.md`'s
"Bootstrap fallback" and "Renovate config" sections: dm is the
*implementation* of a generalised version of the decision the
project is deviating from. The downstream output of `dm regen` is
exactly the single-file `Dependencies.mill` shape the decision
mandates. The decision is satisfied *by construction* in every other
`/p/hg/` repo through codegen — dm itself is the only repo that
cannot bootstrap to that output without first having an `object V`
to read from.

## Decision

Deviate from [[tech/decisions/deps-single-file]] *in dm's own
`build.mill`*. Continue to declare dependencies inline via
`object V` while dm is the bootstrap implementation of the catalog.

Conditions under which this deviation expires:

1. **dm extract self-applied.** Once `dm extract` is implemented and
   `dm` itself has been published as an artifact, dm's own deps can
   flow through `libs.versions.toml` like any other consumer. The
   bootstrap `object V` is replaced by a regenerated
   `deps/Dependencies.mill` (with the DO-NOT-EDIT banner), and the
   deviation evaporates *by construction*. This is the expected
   resolution path.
2. **Monorepo embedding** (per `DESIGN.md` §"Open Questions"). If
   `/p/factory/` absorbs dm, `object V` is replaced by references to
   the monorepo's central `Dependencies.mill` / `Platform` (the same
   path toolbox and sourceline-manager will take). Resolves the
   deviation by the same mechanism as the other `/p/hg/` deviations.

Either condition is a trigger to revise this ADR.

## Consequences

- `meta/drift.md` should not flag `dependency-manager` under
  *missing-declaration* for `deps-single-file` — the declaration
  exists, it is a deviation, and the expiry conditions are recorded.
- Renovate, when pointed at `dependency-manager/build.mill`, can
  still parse every `mvn"…::${V.x}"` coordinate. The deviation does
  not sacrifice automation.
- **This is the third deviation** recorded against
  `deps-single-file`. The first two
  ([[projects/sourceline-manager/adr/0002-deviate-deps-single-file]],
  [[projects/toolbox/adr/0002-deviate-deps-single-file]]) share a
  "resolve at monorepo embedding" path. The dm deviation adds a
  *second* resolution path — "resolve at dm-extract self-application".
  If a fourth project lands with the same shape as one of these
  three, the case for growing `deps-single-file` to carry a
  "standalone pre-embedding" carve-out (or a "self-applying tool"
  carve-out) gets stronger. Worth a synthesis if it recurs.
- The downstream `deps/Dependencies.mill` files dm generates in
  *other* repos are first-class instances of the decision. The
  decision's success is measurable through `dm verify` — a CI-time
  diff between catalog state and committed Mill files in the
  consumer repos.
- The eventual dm internal type (`DependencyCatalog` /
  `ProjectGraph` / canonicalisation passes) will itself need to
  decide a stance on [[tech/patterns/functional-domain-design]];
  that ADR is deferred to when the algebra exists on disk.

## Alternatives Considered

- **Adopt unconditionally and pre-create `deps/Dependencies.mill`
  in dm now.** Rejected: the `deps/` directory in dm is reserved
  for the central catalog (`libs.versions.toml` + `projects.yml`),
  not for a per-project Mill deps file. Adding a
  `Dependencies.mill` alongside the catalog files would obscure
  which is the source of truth and creates a directory layout that
  contradicts dm's own design (`deps/` = catalog, not deps file).
- **Move the catalog elsewhere (e.g. `catalog/` or `.dm/`) and put
  `deps/Dependencies.mill` in `deps/`.** Considered. Rejected for
  the same reason `DESIGN.md` chose `deps/` for the catalog — the
  catalog *is* the dependency information for the `/p/hg/` cohort,
  and a separate name would make the wiring less self-evident.
- **`ignores`.** Rejected: the decision applies (Scala project,
  six library deps). Honest deviation with two expiry paths is
  better than silent ignore.
- **Wait until extract self-applies and don't write this ADR.**
  Rejected: would leave `dm` flagged as missing-declaration in
  [[meta/drift]] for a project whose entire purpose is to automate
  the decision. The wiki should reflect that the question has been
  considered and resolved.

## Links

- [[tech/decisions/deps-single-file]]
- [[tech/guides/mill-dependency-management]]
- [[tech/stack/mill]]
- [[sources/summaries/dependency-manager]]
- [[sources/raw/code/dependency-manager]]
- [[projects/dependency-manager/designs/dm-architecture]] — design source of truth (in-tree DESIGN.md)
- [[projects/sourceline-manager/adr/0002-deviate-deps-single-file]] — sibling deviation (rule does not pay)
- [[projects/toolbox/adr/0002-deviate-deps-single-file]] — sibling deviation (resolved at embedding)
- [[projects/compositor/adr/0002-adopt-deps-single-file]] — sibling adoption (forward-looking, code not yet stood up)
- `/p/hg/dependency-manager/build.mill` — `object V` declaration site
- `/p/hg/dependency-manager/DESIGN.md` — chronological decisions and chicken-and-egg discussion

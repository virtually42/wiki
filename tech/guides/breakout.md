---
id: guide-breakout
title: "Breakout — extract a micro-library from a monolithic source repo"
kind: descriptive
status: accepted
scope: global
created: 2026-05-29
updated: 2026-05-29
tags: [breakout, extraction, micro-library, monorepo, mill, scala, ingest]
ownership: shared
ownership_reason: procedure definition — human reviews, agent executes
sources:
  - sources/summaries/toolbox.md
  - sources/summaries/sourceline-manager.md
---

## Purpose

Extract a portion of a monolithic source repository into its own
standalone Mill repo at `/p/hg/<name>`, and register the result as a
wiki project. The new repo is laid out to be **monorepo-embeddable**
later — `build.mill` becomes `package.mill`, `object V` becomes
references to the monorepo's `deps/Dependencies.mill`, no source or
test changes required.

This guide captures the experience from two cases:
- **`sourceline-manager`** — single-module foundation library, no
  platform surface, one external library dep.
- **`toolbox`** — ten-module multi-platform library extracted from a
  larger monolithic source (`/p/v42/toolbox`) per a layout doc
  (`/p/v42/toolbox/new-design.md`).

## When to Use

- The source repo holds code that should be **shared** across other
  projects (a library), but currently lives inside something larger.
- The portion you want to extract has **a stable public surface** or
  is about to acquire one.
- You expect the extracted unit to **outlive the monolithic source**
  in some form — independently published, independently versioned,
  or eventually embedded into a different monorepo.

Do **not** breakout speculatively. A breakout is justified by a
*consumer* outside the current repo, not by "it could be reused
one day".

## Inputs

The human provides:

1. **Source path** — the monolithic repo (`/p/v42/toolbox`,
   `/p/old-thing`, etc.).
2. **Target name** — the new micro-library name (kebab-case;
   becomes both the on-disk directory at `/p/hg/<name>` and the
   default Maven artifact base).
3. **(Optional) Layout doc** — if the source contains a
   `new-design.md` / `extraction-plan.md` / similar, it is the
   *design source of truth* for the breakout. The breakout does
   not invent the module boundaries; it executes the boundaries
   the layout doc records.
4. **(Optional) Portion** — for source repos that should be
   broken into *multiple* micro-libraries, which subset goes into
   this breakout (one operation per target repo).

## Procedure: `breakout <source-path> <target-name>`

### Phase 1 — Understand the source

1. Read the source repo's README and any layout / design doc.
2. List the directories that constitute the portion to extract.
3. Identify the **module boundaries** in the destination (one
   library may become a single-module repo or a multi-module
   build).
4. Identify the **dependency boundary** — which external
   libraries the extracted code uses, and which (if any) of the
   monolithic source's other modules it depends on. The breakout
   target must not depend on code that does not also get
   extracted; record any such coupling as a follow-up.

### Phase 2 — Create the destination repo

1. `mkdir /p/hg/<target-name>`
2. `cd /p/hg/<target-name> && git init`
3. Configure for the personal-repo commit policy:
   ```bash
   git branch -m main
   git config --local commit.gpgsign false
   git config --local tag.gpgsign false
   git config --local user.name tigidar
   git config --local user.email scalavision@gmail.com
   ```
4. **Do not make an initial commit.** That is a human decision —
   the breakout produces the layout, the human commits it.
5. Add `.gitignore` covering Mill (`out/`, `.bsp/`, `.metals/`,
   `.bloop/`, `.scala-build/`, `mill.*`, `*.semanticdb`), Nix
   (`result`, `result-*`, `.direnv/`), IDEs, and OS files.

### Phase 3 — Move sources

1. Move source files **preserving package structure**. If the
   layout doc renames packages or modules, apply the renames here
   in one pass.
2. Use the cross-platform layout from
   [[tech/guides/mill-cross-platform]] §Patterns:
   - `<module>/src/` — shared sources, all platforms.
   - `<module>/<platform>/` — empty Cross-variant directory (the
     `moduleDir` Mill resolves the camelCase identifier to).
   - `<module>/src-jvm/`, `<module>/src-native/`, `<module>/src-js/` —
     platform divergences, only when actual divergences exist.
   - `<module>/test/src/` — shared test sources.
3. **Verify with `mill show <module>.sources`** that the resolved
   source set is non-empty for every Cross variant of every
   module. This is the empty-jar check from
   [[tech/guides/mill-cross-platform]] §Pitfalls — silent empty
   jars are the dominant failure mode at this step.
4. For modules with kebab-case names that contain `-` (e.g.
   `proc-oslib`, `safetensors-core`):
   - On-disk: kebab (`proc-oslib/`).
   - In `build.mill`: camelCase Mill object (`object procOslib`)
     with `override def moduleDir = super.moduleDir / os.up / "<kebab>"`.
   - Published `artifactName`: kebab (`toolbox-proc-oslib`).

### Phase 4 — Generate the build

1. `build.mill` with header `//| mill-version: <pinned>` and
   `//| mill-jvm-version: system`.
2. `object V` block declaring **all** versions inline:
   - `scalaVersions` (Cross over Scala 3 LTS line; see
     [[tech/stack/mill]] SNAPSHOT and version policy).
   - Platform versions: `scalaJS`, `scalaNative`.
   - Test framework versions: `munit`, `munitCatsEffect` (if `fs2`
     or `cats-effect` are present).
   - Library versions per actual `mvnDep`.
   - `organization`, `projectVersion`.
3. A shared trait (e.g. `ToolboxCommon`) that:
   - Extends `CrossScalaModule with PublishModule`.
   - Sets `artifactName = "<target-name>"` as the default; per-module
     overrides set `<target-name>-<kebab>`.
   - Defines `pomSettings` (organization, license, URL, developer).
   - Defines `scalacOptions` (`-deprecation`, `-feature`, `-explain`,
     `-Wunused:all`, `-language:implicitConversions` are the defaults
     seen in both case studies).
   - Defines `sharedSrc = Task.Sources(moduleDir / os.up / "src")` and
     `override def sources = Task { super.sources() ++ sharedSrc() }`.
4. A shared test trait (e.g. `ToolboxTestSources`) for `<module>/test/src/`
   shared test sources with `os.up / os.up` path math (Cross variant
   test moduleDir is `<module>/<platform>/test/`).
5. One Mill object per logical module. For each:
   - Inner trait `JvmModule extends ToolboxCommon` (and likewise for
     `JsModule extends ToolboxCommon with ScalaJSModule`,
     `NativeModule extends ToolboxCommon with ScalaNativeModule`).
   - `override def artifactName` to the kebab form.
   - `override def moduleDeps` to the right sibling modules.
   - `override def mvnDeps` for external libraries.
   - Nested `test` object per platform with the shared test trait.
   - **ES Module output** on JS modules that import Node built-ins
     via `@JSImport("node:…", JSImport.Namespace)`:
     `override def moduleKind = ModuleKind.ESModule`.

### Phase 5 — Generate `flake.nix` and README

1. `flake.nix` providing a dev shell with JDK, Mill, and the Scala
   Native toolchain (if Native is in the platform matrix).
2. `README.md` with:
   - One-line description.
   - `groupId`, status, design source of truth (if any).
   - Module table (responsibility per module).
   - Build invocations: `nix develop`, `mill resolve __`,
     `mill __.compile`, `mill __.test`, and per-module / per-platform
     forms.
   - Module-name encoding section, **only if** any module uses
     kebab + camelCase (`proc-oslib` style).
   - License (Apache-2.0 is the default — verify with the human).

**Do not** claim "no sources" or "pre-migration scaffold" in the
README when sources have already been moved. The toolbox case
study shows this kind of stale framing surviving the actual
breakout and confusing later ingests; write the README to match
*actual* state.

### Phase 6 — Register in the wiki

Mirror what [[projects/sourceline-manager]] and
[[projects/toolbox]] look like.

1. **Bridge file** at `sources/tmp/<target-name>.md` (per memory
   rule: `sources/raw/**` is human-owned; bridges stage in
   `sources/tmp/` for human promotion). Use the `code-source`
   schema from [[meta/schema]]. The `commit:` field is
   `uninitialized-tree` until the human makes the initial commit.

2. **Summary** at `sources/summaries/<target-name>.md`. Cover:
   - What it is (artifact coordinate, purpose).
   - The modules and their dependency graph.
   - Build wiring (Mill version, `object V`, platform matrix).
   - Cross-platform layout pattern in use.
   - Cross-cutting type choices that the code already commits to.
   - Compliance scan against current normative pages.

3. **Project page** at `projects/<target-name>/index.md`. Cover:
   - One-paragraph description + status.
   - Stack (language, platforms, effects, build, tests, deps).
   - Code location.
   - Embedding path (how this graduates to the monorepo).
   - ADR / Designs / Plans / Tickets / Syntheses sections, mostly
     empty at breakout time.
   - Module summary table.

4. **Project log** at `projects/<target-name>/log.md` with one
   ingest entry covering: breakout date, source repo, target
   location, `git init` state (no initial commit yet), wiki
   artefacts created, normative-page `used_by` updates, and any
   observations worth flagging for future synthesis.

5. **ADRs** at `projects/<target-name>/adr/` — one per **accepted**
   normative page the project is in-scope for, recording the
   project's stance (`adopts` / `deviates` / `excepts` / `ignores`).
   Both case studies converged on this set as the **minimum**:

   | # | ADR | Default stance | When to flip |
   |---|-----|----------------|--------------|
   | 0001 | [[tech/patterns/functional-domain-design]] | adopt (declarative) | Always for Scala code that models a domain |
   | 0002 | [[tech/decisions/deps-single-file]] | deviate while standalone | Adopt only if the new repo is already inside a monorepo at breakout time |

   Add ADRs 0003+ only when **evidence in the code** supports them
   (e.g. `tdd-rhythm` requires actual test-first commits or named
   law tests; `symmetric-refactoring` requires a paired operator
   catalogue). Do not pre-populate empty adoption ADRs.

6. **Update [[index]] §Projects** with a row for the new project
   (kept alphabetised among `active` rows).

7. **Populate `used_by`** on every normative page the new ADRs
   reference. Lint will eventually re-derive this, but doing it
   inline keeps the wiki coherent between lint runs.

8. **Append to [[meta/log]]** a top-level `ingest |` or `promote |`
   entry summarising the breakout and flagging cross-cutting
   observations (e.g. "second project to deviate from
   `deps-single-file`; if a third lands, consider a carve-out
   instead").

### Phase 7 — Hand off

Surface to the human:

1. **The uncommitted tree** at `/p/hg/<target-name>`. The human
   makes the initial commit (unsigned, no Co-Authored-By, author
   tigidar — per memory rule on personal-repo commit policy).
2. **The bridge in `sources/tmp/`**, ready to be promoted to
   `sources/raw/code/<target-name>.md` with the initial commit SHA
   filled into the `commit:` field.
3. **Any open questions** — typically a small list: README claims
   that should be updated, design-doc that may or may not need
   wiki ingest, layout decisions you didn't have authority to make
   (e.g. "should `proc-fs2` be JS-capable on day one?").

## Anti-Patterns

- **Pre-populating empty ADRs / plans / tickets.** A breakout
  produces the project skeleton, the two stance ADRs, and
  whatever the code already commits to. Speculation goes in
  *log entries*, not in pre-created ADRs.
- **Inventing module boundaries.** If the source repo has a
  layout / design doc, the breakout executes it. If it doesn't,
  the breakout *blocks* until the human writes one (or makes the
  layout decisions explicit in conversation).
- **Committing in the new repo.** The breakout produces an
  uncommitted tree. Initial commits are explicit human steps.
- **Writing to `sources/raw/code/`** at breakout time. Always
  stage to `sources/tmp/`; the human promotes after reviewing the
  bridge.
- **Tracking the new repo with `git add` in the wiki repo.**
  The new repo at `/p/hg/<target-name>` is a separate git
  repository, not part of the wiki tree.
- **Claiming the README is correct** without checking it against
  the moved sources. README drift survived the toolbox breakout
  and required a follow-up correction.

## Existing Breakouts

| Project | Source | Target | Notes |
|---------|--------|--------|-------|
| [[projects/sourceline-manager]] | (origin pre-dates wiki) | `/p/hg/sourceline-manager` | Single-module, no platform surface, one dep. Reference case for the *minimum* shape. |
| [[projects/toolbox]] | `/p/v42/toolbox` (per `new-design.md`) | `/p/hg/toolbox` | Ten modules, three platforms, eight library deps. Reference case for the *multi-module / multi-platform* shape and for kebab/camel module-name encoding. |
| [[projects/tagless]] | `/p/v42/tagless` (no design doc; existing build.mill module boundaries served as layout) | `/p/hg/tagless` | Fourteen modules, two platforms, deliberate fine-grained ten-way split of a monolithic `tags` module. Reference case for the *granular per-concern publish-local* shape and for breaking module-internal cycles (`core ↔ viz`, `core ↔ route`) during a split. |
| [[projects/shapesdsl]] | `/p/v42/tagless` (sibling extraction; shapesdsl + shapesdslsvg modules) | `/p/hg/shapesdsl` | Three modules, two platforms, one cross-repo dep (`tagless-core` via publishLocal SNAPSHOT). Reference case for *cross-repo wiring* between sibling breakouts. |

## Related Pages

- [[meta/schema]] — page formats, including `code-source` for the bridge file
- [[meta/ownership]] — confirms `sources/raw/**` is human-owned (use `sources/tmp/` for staging)
- [[tech/guides/mill-cross-platform]] — the build pattern every breakout adopts
- [[tech/decisions/deps-single-file]] — the decision most breakouts deviate from while standalone
- [[tech/patterns/functional-domain-design]] — the pattern most breakouts adopt
- [[tech/stack/mill]] — version policy and SNAPSHOT workflow

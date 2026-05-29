# toolbox — project log

Append-only record of project-scoped events.

**Ownership: llm.**

---

## [2026-05-29] commit | Initial toolbox v1 commit landed

Human approved agent-on-behalf commit (part of the /p/hg/*
commit sweep — see [[meta/log]]).

- **SHA**: `2b2a828`
- **Branch**: `main`
- **Author**: `tigidar`, unsigned, no `Co-Authored-By` trailer
- **Subject**: `Initial toolbox v1 — 10 modules (core, fluent, script, proc{,-oslib,-node,-fs2,-kyo}, vfs, example) + dm catalog adoption`
- **Files**: 102 changed, 16640 insertions

Bundled the entire v1 surface (all 10 modules + tests + flake +
.mill-version + .gitignore + README + the post-DM-001 build.mill
+ deps/) into a single initial commit. Splitting the DM-001
migration into a separate commit would have left the initial
commit weirdly partial — the migrated build.mill belongs with
the modules it builds, not as a follow-up.

The wiki bridge for toolbox currently lives at
`sources/tmp/toolbox.md` and remains untouched — a future
ingest pass can promote it to `sources/raw/code/toolbox.md`
with this SHA once a human signals it's worth doing
(toolbox doesn't have an explicit promote-bridge ticket yet
the way dm did).

Refs:
[[projects/toolbox/index]],
[[meta/log]]

---

## [2026-05-29] adr | Adopt deps-single-file post-migration (DM-008)

After DM-001 migrated toolbox to consume `build.deps.Deps.*`
from dm, the wiki-side ADR-0002 (deviate) no longer described
reality. Realigned the normative surface:

- Wrote
  [[projects/toolbox/adr/0003-adopt-deps-single-file]] adopting
  [[tech/decisions/deps-single-file]] for external Maven
  library coordinates, with a narrow exception for platform
  versions (Scala / ScalaJS / ScalaNative remain inline in
  `build.mill`'s `object V`) and project-internal metadata.
- Marked ADR-0002 `status: superseded`, populated
  `superseded_by: [adr/0003-adopt-deps-single-file.md]`, and
  added a superseded-by banner at the top of the §Context
  section. The body is retained as the reasoning history for
  the deviation's original premise.
- Updated `projects/toolbox/index.md`:
  - §"Embedding Path" rewritten — the deviation-by-construction
    framing is replaced with the dm-migration-by-construction
    framing.
  - §"ADRs" lists ADR-0002 as superseded and ADR-0003 as the
    current accepted state.
- Added `projects/toolbox/adr/0003-adopt-deps-single-file.md`
  to [[tech/decisions/deps-single-file]] `used_by`.

The exception severity is `low` because the platforms-only
boundary is principled (dm intentionally does not manage
platform versions; conflating shapes is wrong) rather than
incidental.

Refs:
[[projects/dependency-manager/tickets/0008-resolve-adr-debts]],
[[projects/toolbox/adr/0003-adopt-deps-single-file]],
[[projects/toolbox/adr/0002-deviate-deps-single-file]],
[[tech/decisions/deps-single-file]]

---

## [2026-05-29] implement | build.mill migrated to dm catalog (DM-001)

`/p/hg/toolbox/build.mill` switched from inline `object V` library
versions to `build.deps.Deps.*` references from the auto-generated
`deps/Dependencies.mill`. Catalog: `/p/hg/dependency-manager/deps/`.

### Surface migrated

10 external Maven libraries — `osLib`, `kyoCore`, `catsEffect`,
`fs2Core`, `fs2Io`, `sourcelineManager`, `pprint`, `sourcecode`,
`munit`, `munitCatsEffect` — across `ToolboxTestSources`, `script`
(3 platforms), `procOslib` (2), `procFs2` (1), `vfs` (3),
`procKyo` (2), `example` (1).

`V.fs2` (the single inline version) fanned out into
`Deps.fs2Core` + `Deps.fs2Io` at the proc-fs2 call site, matching
the catalog's separate `fs2-core` and `fs2-io` entries.

`V.slm` → `Deps.sourcelineManager` (kebab → camel; the catalog
handle is `sourceline-manager`).

`object V` retains only `scalaVersions`, `scalaJS`, `scalaNative`,
`organization`, `projectVersion`. The platform-versions
deferral is intentional and codified separately (see DM-008 in
the dm project for the cross-consumer rationale).

### `deps/package.mill` anchor

One-line file: `package build.deps`. Required by Mill 1.x to
discover sibling `Dependencies.mill` as a helper file. Same
pattern slm adopted on its earlier migration.

### Internal self-references untouched

`toolbox-script`, `toolbox-proc-oslib`, `toolbox-fluent`,
`toolbox-vfs`, etc. publish metadata (`def artifactName`,
`PublishModule`) unchanged. These are publishLocal'd artefacts,
not external Maven coords — explicitly *not* catalog candidates.

### Verification

```
$ mill resolve __                   →  SUCCESS
$ mill __.compile                   →  2659/2659 tasks SUCCESS
$ mill __.test                      →  green on JVM / JS / Native
$ cd /p/hg/dependency-manager
$ bin/dm verify --project=toolbox
# toolbox                  OK
$ bin/dm extract --force --out=/tmp/dm-test … && diff -r /tmp/dm-test deps/  → 0
```

Re-extracting against the refactored build.mill produces an
identical catalog to the pre-migration one — semantic equivalence
established.

### ADR partial-expiry

`projects/toolbox/adr/0002-deviate-deps-single-file.md` now
deviates only for *platform versions* (Scala/ScalaJS/ScalaNative);
library coordinates conform via dm-managed
`deps/Dependencies.mill`. The ADR rewrite/supersede is tracked
in DM-008 of the dependency-manager project.

Refs:
[[projects/dependency-manager/tickets/0001-migrate-toolbox-to-deps]],
[[projects/dependency-manager/log]],
[[projects/toolbox/adr/0002-deviate-deps-single-file]],
[[tech/decisions/deps-single-file]]

---

## [2026-05-29] ingest | Project registered in wiki

Ingested `/p/hg/toolbox` (no commit yet — `git init` performed during
this ingest, branch `main`, signing disabled, author `tigidar`).
Created wiki-side artefacts:

- `projects/toolbox/index.md` — project landing page with module
  summary and stack.
- `projects/toolbox/adr/0001-adopt-functional-domain-design.md` —
  adopts the global pattern (declarative encoding), citing the
  `Cmd` / `StreamTarget` / `ProcessSpec` / `VirtualFileSystem` /
  `KyoCommandResult` ADT shapes as evidence.
- `projects/toolbox/adr/0002-deviate-deps-single-file.md` — deviates
  from the global single-file deps decision; rationale: standalone
  repository today, inline `object V` in `build.mill`. Deviation
  expires on monorepo embedding (by construction).
- `sources/summaries/toolbox.md` — distilled summary covering the
  ten modules, dependency graph, platform matrix, build wiring, the
  module-name encoding convention, and a compliance scan.
- `sources/tmp/toolbox.md` — bridge file staged for human promotion
  to `sources/raw/code/toolbox.md` (per `sources/raw/**` being
  human-owned).

Populated `used_by` on [[tech/patterns/functional-domain-design]]
and [[tech/decisions/deps-single-file]] with the new toolbox ADRs.

Added a row to [[index]] §Projects between sourceline-manager and
the planned webapp.

Notable observations from the ingest:

- Toolbox is the **third project** to land in the wiki and the
  **second with on-disk code** (after sourceline-manager). Unlike
  sourceline-manager it has no in-tree ADRs — the design source of
  truth lives outside the repo at `/p/v42/toolbox/new-design.md`.
- The ingest **created the git repo** (`git init`, no commit yet).
  Before the bridge can graduate from `sources/tmp/` to
  `sources/raw/code/toolbox.md`, an initial commit needs to be made
  and the bridge's `commit:` field updated from `uninitialized-tree`
  to the SHA.
- README still claims "Phase A — module layout only, no sources"
  while ~75 Scala files exist across the ten target modules.
  Documentation drift on the source repo; flagged in
  [[sources/tmp/toolbox]] §Open Questions.
- **Second worked example for [[tech/guides/mill-cross-platform]].**
  This one exercises `src-jvm/` / `src-native/` / `src-js/`
  divergences (sourceline-manager had no platform surface) and the
  JS-side `ModuleKind.ESModule` requirement for
  `@JSImport("node:child_process", JSImport.Namespace)`. Worth
  adding a §Examples cross-reference in that guide on a future
  edit pass.
- **Candidate pattern for promotion:** the
  *algebra + N interpreters with `<algebra>-*` naming convention*
  (here: `proc` + `proc-oslib` / `proc-node` / `proc-fs2` /
  `proc-kyo`). Defer promotion until it recurs in another project.

Refs: [[projects/toolbox/index]],
[[sources/summaries/toolbox]],
[[sources/tmp/toolbox]],
[[tech/patterns/functional-domain-design]],
[[tech/decisions/deps-single-file]],
[[sources/summaries/sourceline-manager]]

---
id: DM-001
title: Migrate toolbox/build.mill to consume Deps from dm catalog
status: done
project: dependency-manager
created: 2026-05-29
closed: 2026-05-29
related_adr:
  - projects/dependency-manager/adr/0001-deviate-deps-single-file.md
  - projects/toolbox/adr/0002-deviate-deps-single-file.md
priority: high
---

## Goal

`/p/hg/toolbox/build.mill` references `build.deps.Deps.*` instead of
inline `mvn"…::${V.x}"` for the 10 external Maven libraries in dm's
catalog. The two `object V` halves split cleanly:

- **Out of V** (managed by dm catalog): `osLib`, `kyoCore`, `catsEffect`,
  `fs2`, `slm`, `pprint`, `sourcecode`, `munit`, `munitCatsEffect`,
  plus any other lib that maps to an entry in `libs.versions.toml`.
- **Stays in V**: `scalaVersions`, `scalaJS`, `scalaNative`,
  `organization`, `projectVersion`, and any `mvn"no.virtual-architect::…"`
  intra-monorepo self-references (those are publishLocal artefacts,
  not external Maven deps — explicitly *not* catalog candidates).

`fs2` is special: the catalog has separate `fs2-core` and `fs2-io`
entries (kebab handles → `Deps.fs2Core` and `Deps.fs2Io`); the
toolbox `V.fs2` single string fans out to two `Deps.*` references at
each call site that previously used both.

`slm` is similarly special: the catalog handle is `sourceline-manager`
→ `Deps.sourcelineManager`. Every `mvn"no.virtual-architect::sourceline-manager::${V.slm}"`
becomes `Deps.sourcelineManager`.

## Acceptance Criteria

- [ ] `/p/hg/toolbox/deps/package.mill` exists, one line:
  `package build.deps` (the Mill 1.x helper-discovery anchor).
- [ ] `/p/hg/toolbox/build.mill` `object V` has had the 10 library
  versions removed; only `scalaVersions`, `scalaJS`, `scalaNative`,
  `organization`, `projectVersion` remain (plus any non-Maven values
  not in the catalog).
- [ ] Every `mvn"…::${V.<lib>}"` call site for an external library
  has been rewritten to `build.deps.Deps.<lib>` (or the appropriate
  kebab → camel name).
- [ ] `mill resolve __` succeeds.
- [ ] `mill __.compile` succeeds (all platforms / all cross variants).
- [ ] `mill __.test` is green across all modules and platforms — JVM,
  Scala.js, Scala Native where applicable.
- [ ] `cd /p/hg/dependency-manager && bin/dm verify --project=toolbox`
  reports OK.
- [ ] `bin/dm extract --force --out=/tmp/x /p/hg/toolbox /p/hg/sourceline-manager /p/hg/safetensors-scala`
  produces a catalog byte-identical to
  `/p/hg/dependency-manager/deps/` (the consumer-side round-trip
  evidence).
- [ ] Log entry appended to `projects/dependency-manager/log.md`
  ([2026-MM-DD] implement | toolbox migrated to dm catalog) covering
  the migration, the per-call-site mapping, and the verify result.
- [ ] Log entry appended to `projects/toolbox/log.md` mirroring the
  slm pattern (migration + ADR partial-expiry flag).

## Notes

**Per-call-site rewrites** (sweep the file, ~15 sites — see
`grep -n "V\.\\|mvn\"" /p/hg/toolbox/build.mill`):

| Old | New | Where |
|-----|-----|-------|
| `mvn"com.lihaoyi::os-lib::${V.osLib}"` | `Deps.osLib` | proc-oslib module + tests |
| `mvn"io.getkyo::kyo-core::${V.kyoCore}"` | `Deps.kyoCore` | proc-kyo module |
| `mvn"org.typelevel::cats-effect::${V.catsEffect}"` | `Deps.catsEffect` | proc-fs2 module |
| `mvn"co.fs2::fs2-core::${V.fs2}"` | `Deps.fs2Core` | proc-fs2 module |
| `mvn"co.fs2::fs2-io::${V.fs2}"` | `Deps.fs2Io` | proc-fs2 module |
| `mvn"no.virtual-architect::sourceline-manager::${V.slm}"` | `Deps.sourcelineManager` | multiple module test deps |
| `mvn"com.lihaoyi::pprint::${V.pprint}"` | `Deps.pprint` | wherever it's used |
| `mvn"com.lihaoyi::sourcecode::${V.sourcecode}"` | `Deps.sourcecode` | wherever it's used |
| `mvn"org.scalameta::munit::${V.munit}"` | `Deps.munit` | every test module |
| `mvn"org.typelevel::munit-cats-effect::${V.munitCatsEffect}"` | `Deps.munitCatsEffect` | proc-fs2 test |

**Do NOT remove `V.slm`** if it appears in a non-`mvn"…"` context
(e.g., as a string in publish metadata). It's safe to remove only
when every reader becomes `Deps.sourcelineManager`. Sweep
`grep -n "V\.slm" build.mill` post-edit to verify zero remaining
references.

**Verification flow** (after edit):

```bash
cd /p/hg/sourceline-manager && mill __.publishLocal  # ensure slm artifact fresh
cd /p/hg/toolbox && mill resolve __
cd /p/hg/toolbox && mill __.compile
cd /p/hg/toolbox && mill __.test
cd /p/hg/dependency-manager && bin/dm verify --project=toolbox
cd /p/hg/dependency-manager && bin/dm extract --force --out=/tmp/dm-test
diff -r /tmp/dm-test /p/hg/dependency-manager/deps/ ; echo $?  # expect 0
rm -rf /tmp/dm-test
```

**toolbox internal self-refs.** `toolbox-script`, `toolbox-proc-oslib`,
`toolbox-fluent` (consumed by dm itself) are *not* in the catalog. The
toolbox build.mill should retain `def artifactName` and PublishModule
machinery untouched. Catalog adoption is on the consumer side, not the
publisher side.

**Order of `Deps.*` references.** The generated `Dependencies.mill`
sorts vals lexicographically. The build.mill rewrites do not need to
preserve any order; Mill's `Seq[mvn]` is order-insensitive for the
dependency graph.

## Implementation Log

### [2026-05-29] closed — toolbox migrated to catalog

- Added `/p/hg/toolbox/deps/package.mill` anchor (one line:
  `package build.deps`).
- Stripped `V.osLib`, `V.kyoCore`, `V.catsEffect`, `V.fs2`, `V.slm`,
  `V.pprint`, `V.sourcecode`, `V.munit`, `V.munitCatsEffect` from
  `build.mill`'s `object V`. Platform versions (`scalaVersions`,
  `scalaJS`, `scalaNative`), `organization`, `projectVersion`
  retained.
- Rewrote 9 call-site groups: `ToolboxTestSources.mvnDeps` (munit),
  script (slm × 3 platforms), proc-oslib (osLib × 2 platforms),
  vfs (slm × 3 platforms), proc-fs2 (fs2Core, fs2Io, catsEffect +
  munitCatsEffect test), proc-kyo (kyoCore × 2 platforms),
  example (pprint, sourcecode).
- Verification: `mill resolve __` OK, `mill __.compile` OK
  (2659 tasks), `mill __.test` green across JVM/JS/Native (no test
  failures). `bin/dm verify --project=toolbox` → `OK`.
- Round-trip: `bin/dm extract --force --out=/tmp/dm-test …` over
  all three consumers produced byte-identical catalog to
  `/p/hg/dependency-manager/deps/` (diff exit 0). 12 libraries, 3
  projects.
- `grep mvn"` on the migrated `build.mill` returns 0 matches.

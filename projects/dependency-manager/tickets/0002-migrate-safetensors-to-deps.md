---
id: DM-002
title: Migrate safetensors-scala/build.mill to consume Deps from dm catalog
status: done
project: dependency-manager
created: 2026-05-29
closed: 2026-05-29
related_adr:
  - projects/dependency-manager/adr/0001-deviate-deps-single-file.md
priority: high
---

## Goal

`/p/hg/safetensors-scala/build.mill` references `build.deps.Deps.*`
for the 3 external libraries dm currently catalogs for this project:
`munit`, `munit-scalacheck`, and `scodec-core`. Other `V.*` entries
(platforms, organisation, version) stay inline.

**scodec pinning preserved.** The in-tree ADR
`/p/hg/safetensors-scala/docs/adr/0001-inline-versions.md` records
that scodec is pinned to paladium's currently-resolved version (2.3.3)
to avoid eviction conflicts when paladium consumes this library. After
this ticket, the pin is held by the central catalog
(`libs.versions.toml` `scodec-core = "2.3.3"`) instead of the inline
`V.scodec`. dm's `promote` verb will catch any future drift if
paladium hand-edits scodec downstream.

## Acceptance Criteria

- [ ] `/p/hg/safetensors-scala/deps/package.mill` exists, one line:
  `package build.deps`.
- [ ] `/p/hg/safetensors-scala/build.mill` `object V` has had
  `munit`, `munitScalaCheck`, and `scodec` removed; platform versions
  and publishing metadata remain.
- [ ] `mvnDeps` rewrites:
  - `mvn"org.scalameta::munit::${V.munit}"` → `Deps.munit`
  - `mvn"org.scalameta::munit-scalacheck::${V.munitScalaCheck}"` →
    `Deps.munitScalacheck` (note case change: `Check` → `check`).
  - `mvn"org.scodec::scodec-core::${V.scodec}"` → `Deps.scodecCore`.
- [ ] `mill safetensors.{jvm,js,native}[3.8.3].compile` succeeds for
  all three platforms.
- [ ] `mill safetensors.{jvm,js,native}[3.8.3].test` is green on all
  three.
- [ ] `bin/dm verify --project=safetensors-scala` reports OK.
- [ ] `bin/dm extract --force --out=/tmp/x …` produces a
  byte-identical catalog (round-trip evidence).
- [ ] Log entry appended to `projects/dependency-manager/log.md`.
- [ ] Log entry appended to `projects/safetensors-scala/log.md`
  describing the migration and the scodec-pin transfer.
- [ ] Empty-jar footgun check (per
  [[tech/guides/mill-cross-platform]] §Pitfalls): post-migration,
  `jar tf` of the published JVM/JS/Native artefacts still shows
  non-empty class lists. This is a regression guard, not a new
  requirement — safetensors already passed at extraction time, but
  any `build.mill` edit re-opens the risk.

## Notes

**Smaller surface than toolbox** — only 3 vals to remove, 3 mvnDeps
sites to rewrite. Estimated 15 minutes of edits + verification once
DM-001 establishes the pattern.

**Verification flow:**

```bash
cd /p/hg/safetensors-scala && mill resolve __
cd /p/hg/safetensors-scala && mill __.compile
cd /p/hg/safetensors-scala && mill safetensors.jvm[3.8.3].test
cd /p/hg/safetensors-scala && mill safetensors.js[3.8.3].test
cd /p/hg/safetensors-scala && mill safetensors.native[3.8.3].test
cd /p/hg/dependency-manager && bin/dm verify --project=safetensors-scala
cd /p/hg/dependency-manager && bin/dm extract --force --out=/tmp/dm-test
diff -r /tmp/dm-test /p/hg/dependency-manager/deps/ ; echo $?
rm -rf /tmp/dm-test
# Empty-jar sentinel:
cd /p/hg/safetensors-scala && mill safetensors.jvm[3.8.3].publishLocal
jar tf ~/.ivy2/local/no.virtual-architect/safetensors-scala_3/*/jars/safetensors-scala_3.jar \
  | grep -v META-INF | head
```

**In-tree ADR cleanup is in DM-008**, not this ticket. This ticket
only handles the code migration; the normative debt resolution
(updating in-tree `docs/adr/0001-inline-versions.md` to reflect the
new state) lives in the ADR-debt ticket.

## Implementation Log

### [2026-05-29] closed — safetensors-scala migrated to catalog

- Added `/p/hg/safetensors-scala/deps/package.mill` anchor.
- Stripped `V.munit`, `V.munitScalaCheck`, `V.scodec` from
  `build.mill`'s `object V`. Comment in `object V` now notes the
  scodec-pin (2.3.3) is held centrally by the catalog.
- Rewrote 3 mvnDeps sites:
  - `mvn"org.scodec::scodec-core::${V.scodec}"` →
    `build.deps.Deps.scodecCore` (SafeTensorsCommon)
  - `mvn"org.scalameta::munit::${V.munit}"` → `build.deps.Deps.munit`
    (SafeTensorsTestSources)
  - `mvn"org.scalameta::munit-scalacheck::${V.munitScalaCheck}"` →
    `build.deps.Deps.munitScalacheck` (note case fold:
    `Check` → `check`)
- Verification:
  - `mill __.compile` → 342/342 SUCCESS
  - `mill safetensors.jvm[3.8.3].test` → 141/141 green
  - `mill safetensors.js[3.8.3].test` → 164/164 green
  - `mill safetensors.native[3.8.3].test` → 186/186 green
- `bin/dm verify --project=safetensors-scala` → OK
- Round-trip: `bin/dm extract --force …` produces byte-identical
  catalog (`diff` exit 0). scodec-core retained at `2.3.3`.
- Empty-jar sentinel: `mill safetensors.jvm[3.8.3].publishLocal`
  then `jar tf` on the ivy-local jar — 10+ classes under
  `no/virtual_architect/safetensors/`, no regression.

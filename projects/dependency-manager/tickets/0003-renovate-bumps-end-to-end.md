---
id: DM-003
title: Run Renovate-proposed bumps end-to-end through the catalog loop
status: done
project: dependency-manager
created: 2026-05-29
closed: 2026-05-29
related_adr:
  - projects/dependency-manager/adr/0001-deviate-deps-single-file.md
priority: medium
---

## Goal

Exercise the **upstream → downstream** half of the catalog loop in
anger by landing at least one Renovate-proposed Maven bump
end-to-end, with all three consumer projects compiling and testing
against the bumped version. Validates that:

1. The catalog edit (TOML) → `dm regen` → consumer `Dependencies.mill`
   path produces output that downstream `build.mill` actually
   consumes (vs. just looking right on disk).
2. The verify gate (`bin/dm verify`) reports drift before regen and
   sync after.
3. The whole flow takes less than 5 minutes from edit to green
   tests, validating "Renovate opens PR → human merges → consumers
   pick up at next CI" is a real workflow, not theoretical.

## Acceptance Criteria

- [ ] At least **two** Renovate-proposed bumps landed cleanly. Pick
  low-risk patches first:
  - `os-lib` `0.11.7` → `0.11.8` (lihaoyi patch — safe).
  - `pprint` `0.9.4` → `0.9.6` (lihaoyi patch — safe).
  - `munit` `1.0.3` → at most `1.0.4` (avoid `1.3.x` which has the
    `munit-scalacheck` major bump implicit).
  - `sourcecode` `0.4.4` → latest patch.
- [ ] At least **one** "larger" bump *attempted*, with a documented
  outcome (either landed clean or rolled back with reason recorded).
  Candidates:
  - `kyo-core` `1.0-RC1` → `1.0.0-RC2` (RC churn — could break).
  - `fs2` `3.12.0` → `3.13.0` (minor — moderate risk).
  - `cats-effect` `3.6.1` → `3.7-…` (note: Renovate proposed a SHA
    version; verify it's a real release before attempting).
- [ ] For each landed bump:
  - `libs.versions.toml` updated with new version.
  - `bin/dm verify` reports drift in the affected consumer(s)
    *before* regen (proof gate works).
  - `bin/dm regen` rewrites the affected `Dependencies.mill`.
  - `bin/dm verify` reports OK after regen.
  - Affected consumer's `mill __.test` is green.
- [ ] Log entry on `projects/dependency-manager/log.md` covering
  what was landed, what was rolled back (if anything), and any
  surprises.
- [ ] If a bump broke a consumer: rollback path recorded
  (`git checkout deps/libs.versions.toml` is the obvious one once
  DM-005 lands; pre-DM-005, manual revert).

## Notes

**Order of operations** for a single bump:

```bash
cd /p/hg/dependency-manager
# 1. Capture baseline
bin/dm verify  # → "all 3 in sync"

# 2. Edit catalog
$EDITOR deps/libs.versions.toml  # bump the version field

# 3. Verify catches drift
bin/dm verify --project=<affected-consumer>
# → expect DRIFT, exit 1

# 4. Regenerate downstream
bin/dm regen --project=<affected-consumer>
bin/dm verify --project=<affected-consumer>
# → expect OK

# 5. Test consumer
cd /p/hg/<affected-consumer>
mill __.compile
mill __.test  # → expect green

# 6. If green, leave catalog; if broken, rollback:
cd /p/hg/dependency-manager
git checkout deps/libs.versions.toml  # post-DM-005 only
bin/dm regen --project=<affected-consumer>
```

**Pre-DM-005 rollback** (no git yet): keep a backup
`cp deps/libs.versions.toml deps/libs.versions.toml.bak` before
editing; restore on failure.

**kyo-core RC bumps are notorious** for shifting effect APIs. If the
RC2 bump breaks toolbox's `proc-kyo` module, the right call is to
land the safe patches first and document RC2 as deferred until a
stable release.

**Renovate dry-run cache.** `nix run .#renovate-dryrun` is the
authoritative source of "what's available." Re-run before this
ticket starts to refresh the list — versions may have moved since
the previous dry-run on 2026-05-29.

## Implementation Log

### [2026-05-29] closed — three bumps landed, one rolled back

**Renovate dry-run skipped this round.** `nix run .#renovate-dryrun`
requires a git-tracked tree; dm is still pre-DM-005. Used the
previously-validated bump table from the 2026-05-29 verify session
log entry as the working list. (Once DM-005 lands, regular
dry-runs become trivial.)

**Landed bumps** (all toolbox-only — toolbox is the only consumer
of os-lib / pprint / munit-cats-effect):

| Library | Before | After | Outcome |
|---|---|---|---|
| `os-lib` | 0.11.7 | 0.11.8 | landed |
| `pprint` | 0.9.4  | 0.9.6  | landed |
| `munit-cats-effect` | 2.1.0 | 2.2.0 | landed |

For each: edited `libs.versions.toml` → `dm verify --project=toolbox`
reported DRIFT at the exact line (proof the gate works) → `dm regen`
rewrote `deps/Dependencies.mill` → `dm verify` reported OK →
relevant module's `mill … .test` green:

- os-lib: `procOslib.jvm[3.8.3].test` 249/249, `procOslib.native[3.8.3].test` 311/311 green.
- pprint: `example.jvm[3.8.3].test` 576/576 green.
- munit-cats-effect: `procFs2.jvm[3.8.3].test` 302/302 green.

Final regression sweep: `mill __.test` across the entire toolbox
build (JVM/JS/Native, all modules) — 3638 tasks, SUCCESS.

**Larger bump attempted: `kyo-core 1.0-RC1 → 1.0.0-RC2`.**

Catalog edit → `dm regen` clean → `mill procKyo.jvm[3.8.3].compile`
**failed**:

```
[error] proc-kyo/src-jvm/proc/kyo/KyoProcess.scala:123:58
  private def applyConfig(cmd: Process.Command): Process.Command =
                                                         ^^^^^^^
type Command is not a member of object kyo.Process
… 10 errors found
```

Kyo's `Process.Command` type moved/renamed in RC2. Predicted risk
in the ticket notes ("RC churn — could break"). Rollback:

1. Restored catalog: `1.0.0-RC2` → `1.0-RC1`.
2. `dm regen --project=toolbox` → `mill procKyo.jvm[3.8.3].compile`
   green.
3. `bin/dm verify` → all 3 in sync.

**Outcome:** kyo-core RC2 deferred until either a stable
`kyo-core 1.0.0` ships, or the toolbox `proc-kyo` module is
ported to the new `Process.Command` API. Likely a separate
follow-up ticket against the toolbox project rather than dm.

**Pre-DM-005 rollback note:** no git yet, so rollback was done
by direct file edit. The `libs.versions.toml.bak` backup
referenced in the ticket notes was created at the start of the
session and removed at end (catalog left clean, verified
in-sync).

**Catalog now at:**

```
cats-effect          3.6.1
fs2-core             3.12.0
fs2-io               3.12.0
kyo-core             1.0-RC1      (RC2 deferred — see above)
munit                1.0.3
munit-cats-effect    2.2.0        (bumped this round)
munit-scalacheck     1.0.0
os-lib               0.11.8       (bumped this round)
pprint               0.9.6        (bumped this round)
scodec-core          2.3.3        (palladium-pinned)
sourcecode           0.4.4
sourceline-manager   0.2.0-SNAPSHOT  (disabled by packageRule)
```

`bin/dm verify` reports `all 3 project(s) in sync`.

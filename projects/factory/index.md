---
id: factory
title: Factory monorepo
kind: descriptive
status: active
scope: project:factory
created: 2026-05-30
updated: 2026-05-30
---

# factory

Single-git monorepo at `/factory/` that hosts our code, the wiki, and
the workspace tooling. Replaces the current `/p/hg/*` polyrepo layout
and the `/p/wiki/` standalone repo. External upstream forks, public
mirror repositories, secrets, and Mill's build output sit *inside*
the directory tree but are gitignored from the monorepo and follow
their own policies.

**Status:** active (design accepted 2026-05-30 — pre-migration; `/factory/`
not yet materialised on disk)

## Stack

- Git: single repo at `/factory/.git/` for the workspace; per-subdir
  `.git/` for `upstream/`, `pub/`, and (during migration) the wiki via
  `git subtree`
- Build: Mill — root `build.mill` for cross-cutting jobs, per-library
  `hg/<lib>/build.mill` standalone
- Nix: root `flake.nix` for the workspace dev shell; standalone
  `flake.nix` generated into each `pub/<lib>` for external consumers
- Filesystem: btrfs subvolume for `/factory/`, snapshots managed by
  snapper, restic for off-site backup
- Secrets: sops with age + YubiKey — encrypted at rest, decryption
  keys never live inside `/factory/`
- Sync: `rsync` (hg → pub forward) + `git am`-style cherry-pick
  (pub → hg reverse, semi-manual)

## Code Location

`/factory/` does not exist yet. Once migrated:

```
/factory/.git/                          ← single monorepo
├── build.mill                          ← tracked
├── flake.nix                           ← tracked
├── .gitignore                          ← tracked (includes **/out/)
├── tools/                              ← tracked
├── hg/<lib>/                           ← tracked (no per-lib .git)
│   └── out/                            ← gitignored
├── wiki/                               ← tracked (subtree-merged)
├── upstream/<lib>/                     ← gitignored, own .git (forks)
├── pub/<lib>/                          ← gitignored, own .git (rsync target)
├── secrets/                            ← gitignored (sops-encrypted at rest)
└── out/                                ← gitignored (root Mill cache)
```

Personal-repo commit policy (unsigned, no Co-Authored-By, author
`tigidar`) applies to `/factory/.git/` and to every `pub/<lib>/.git/`
and `upstream/<lib>/.git/`. The wiki's prior commit policy
(Co-Authored-By) is **superseded** at the migration cutover — the
unified monorepo follows one policy.

## Role in the Wiki

The factory project specifies the **physical substrate** that the
wiki's `implement` / `test` / `run` operations act upon. Before
factory, those operations addressed `repo: /p/hg/<name>` as abstract
paths. After factory:

- Every per-project `sources/raw/code/<name>.md` bridge points into
  `/factory/hg/<name>/` (for our code) or
  `/factory/upstream/<name>/` (for external libs).
- Cross-project refactors become a single git commit in the factory
  monorepo, rollback-able as a unit.
- The `tools/update-all.sh` script (and its successors) iterate the
  factory subdirs, not `/p/hg/*`.

The factory is **not** a long-running owned codebase like
`deploymentbox` or `compositor`. It is an infrastructure decision
made permanent through ADRs. Active migration tickets and plans are
deletable once `/factory/` is live; ADRs persist as the record of why
the topology is the way it is.

## Pages

### Designs

- [designs/factory-monorepo-topology.md](designs/factory-monorepo-topology.md)
  — End-to-end design distilled from the
  `scratch/interview_about_factory.md` interview. Problem, constraints,
  options considered, proposed approach, trade-offs, open migration
  questions.

### ADRs

- [adr/0001-single-git-monorepo.md](adr/0001-single-git-monorepo.md)
  — Topology: one git repo at `/factory/.git/`; `upstream/`, `pub/`,
  `secrets/`, `out/`, and `**/out/` gitignored. Wiki absorbed via
  subtree merge.
- [adr/0002-decoupled-mill-builds.md](adr/0002-decoupled-mill-builds.md)
  — Each `hg/<lib>/build.mill` is standalone. Root `build.mill` runs
  cross-cutting jobs only — no Mill federation, no `package.mill`
  discovery from root.
- [adr/0003-pub-mirror-policy.md](adr/0003-pub-mirror-policy.md)
  — `pub/<lib>` populated by filtered one-way rsync from `hg/<lib>`.
  Filter list defined. deploymentbox v3 publishes *from* `pub/`.
  Reverse sync is semi-manual cherry-pick.
- [adr/0004-upstream-fork-rule.md](adr/0004-upstream-fork-rule.md)
  — Every upstream we consume is forked into our org first, then
  cloned to `upstream/<name>/`. Nightly sync job in root `build.mill`.
- [adr/0005-secrets-adopt-deploymentbox-custody.md](adr/0005-secrets-adopt-deploymentbox-custody.md)
  — `/factory/secrets/` holds sops-encrypted ciphertext; decryption
  keys live on YubiKey or `~/.config/sops/age/keys.txt`. Inherits the
  deploymentbox key-custody contract.

### Tickets, plans, syntheses

*None yet.* Migration plan and tickets land when the operator is
ready to execute the cutover.

### Other

- [log.md](log.md)

## Out of scope (and where the boundary is)

- **Per-library build.mill contents.** Each `hg/<lib>` decides for
  itself how it declares modules, deps, and tasks. The factory only
  specifies *that* each build is standalone (ADR-0002), not its
  internal shape.
- **Per-library publishing config.** Out of scope here — owned by
  `deploymentbox`. Factory only ensures `pub/<lib>` is the location
  from which deploymentbox v3 runs (ADR-0003).
- **CI strategy.** Deferred. Per-repo GitHub Actions in `pub/<lib>`
  (defined by deploymentbox). No factory-global CI yet.
- **Snapshot/backup policy details.** Operational. Documented in the
  design doc but not load-bearing enough for its own ADR.
- **The `dm` tool.** `dm` continues as a meta-tool. Root `build.mill`
  may invoke it as a job; it is not absorbed. Closes the deferred
  open question from `projects/dependency-manager/designs/dm-architecture.md`.
- **`/p/v42/`.** Dormant. Migrated piece-by-piece into `hg/` via the
  `breakout` operation, not absorbed wholesale.

## Open Questions

1. **Migration sequence.** Order of operations for the cutover: which
   repo lands first, how the wiki subtree merge integrates with
   in-flight wiki work, how to keep `/p/hg/*` working until the cut.
   To be resolved in a migration plan.
2. **Path migration script.** Single Python script under `wiki/fix/`
   that rewrites every `/p/hg/`, `/p/gh/`, `/p/wiki/`, `/p/v42/`
   reference. Idempotent. Reports unmatched paths. Author + test
   before the cutover.
3. **Upstream nightly sync mechanism.** Where the job runs (root
   `build.mill` task vs. systemd timer vs. a `tools/` cron script).
   Defer until first upstream needs a refresh.
4. **Reverse sync (pub → hg) workflow.** When the first external PR
   lands on a pub repo, formalise the cherry-pick helper. Defer until
   it actually happens.
5. **Snapper / restic policy details.** Exact retention, exclusion
   list (`out/` excluded, `secrets/` snapshotted as ciphertext),
   off-site target, restore drill cadence. Operational; resolve when
   provisioning the volume.

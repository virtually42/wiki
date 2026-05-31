---
id: factory-design-monorepo-topology
title: Factory monorepo — single-git workspace umbrella
kind: descriptive
status: accepted
project: factory
created: 2026-05-30
updated: 2026-05-30
related_adrs:
  - projects/factory/adr/0001-single-git-monorepo.md
  - projects/factory/adr/0002-decoupled-mill-builds.md
  - projects/factory/adr/0003-pub-mirror-policy.md
  - projects/factory/adr/0004-upstream-fork-rule.md
  - projects/factory/adr/0005-secrets-adopt-deploymentbox-custody.md
related_plans: []
sources:
  - scratch/interview_about_factory.md
  - scratch/interview_about_factory_followup.md
  - scratch/monorepo-design-wip.md
  - scratch/wiki_current_state_with_monorepo.md
---

# Design: Factory Monorepo Topology

This is the accepted topology for `/factory/`. It supersedes the
earlier `scratch/monorepo-design-wip.md` design which envisioned a
single git monorepo of code-only (`modules/` + `apps/` + `native/`).
The accepted design is a **workspace umbrella organised by origin**
that absorbs the wiki and brackets origin-specific subdirs (forks,
public mirrors) inside the same directory tree without dragging them
into the monorepo's git history.

## Problem

Today, the substrate the wiki acts on is fragmented across:

- `/p/wiki/` — wiki repo (own git, own commit policy)
- `/p/hg/*` — our libraries, one repo each (~10 repos)
- `/p/gh/*` — external library clones for `ingest-external` (Mill, Kyo,
  Airstream, toml-scala, microvm.nix), mixing our forks and
  read-only clones
- `/p/v42/*` — virt42 plugin code, on its way to deprecation

Five symptoms:

1. **Cross-project refactors are multi-repo PR ceremonies.** Changing
   a shared pattern across `tagless` + `shapesdsl` + `animdsl`
   touches three repos with three histories.
2. **The wiki's `sources/raw/code/*` bridges encode `/p/hg/`,
   `/p/gh/` as if they were stable physical addresses.** They drift
   whenever a repo moves.
3. **No common dev shell.** Each repo has its own (or none) `flake.nix`;
   toolchain pins drift.
4. **No place for cross-cutting jobs.** `dm refresh` across all libs,
   nightly upstream syncs, rsync to public mirrors — there is no
   structural home.
5. **The wiki/code seam is loose.** Wiki references to `/p/hg/<name>`
   are just strings, not part of the wiki's own filesystem tree.

## Constraints

| Constraint | Source | Implication |
|------------|--------|-------------|
| One git history for our work | User decision (Q1 follow-up) | `/factory/` is a single git repo |
| External forks remain pullable from upstream | Q3 fork rule | `upstream/<lib>` must keep its own `.git/`; can't be subtree |
| Public mirror repos are independent git histories | deploymentbox v3 publishes from them | `pub/<lib>` must keep its own `.git/` |
| `hg/<lib>` must be buildable standalone with Mill | Original portability goal, retained | Per-lib `build.mill` cannot depend on root `build.mill` |
| Wiki history preserved | User decision (Q1 follow-up) | Wiki merged into monorepo via `git subtree`, not copied |
| Unified commit policy across the monorepo | User decision (Q1 follow-up) | Personal-repo policy (unsigned, no Co-Authored-By, author `tigidar`) applies everywhere inside `/factory/.git/` |
| Secrets must survive on-disk backup leaks | Q11 concern | Encrypted at rest; decryption keys outside `/factory/` |
| Migration must be scripted, not manual | Q10 follow-up | Single idempotent Python script in `wiki/fix/` |

## Options Explored

### Option A: True code monorepo (`modules/` + `apps/` + `native/`)

The original `scratch/monorepo-design-wip.md`. One git repo. All code
folded into shared module roots. Strongest unification, but:

- Loses the breakout/portability story — moving a library *out* of
  the monorepo requires `git filter-repo` surgery.
- Couples Mill builds: the only `build.mill` is at the root.
- No place for the wiki, no place for external upstream clones.

Rejected as too aggressive a unification for our actual workflow.

### Option B: Pure workspace (no git at root)

`/factory/` is just a directory. Each subdir keeps its own `.git/`.
Simplest, no monorepo semantics, but:

- No place for `build.mill`, `tools/`, `flake.nix` to live coherently.
- Cross-project refactors stay multi-repo.
- The wiki/code seam stays loose.

Rejected — gains over the current `/p/hg/*` shape are marginal.

### Option C: Submodule monorepo

Root tracks each subdir as a git submodule. Standard pattern but:

- Submodule UX is notoriously fragile (detached heads, missed pushes,
  stale pointer commits).
- Cross-project refactor-as-one-commit becomes a submodule-pointer
  dance.
- High blast radius for normal operations.

Rejected.

### Option D (accepted): Single-git monorepo with selective gitignore

`/factory/.git/` tracks everything except origin-specific subdirs
that need their own `.git/`. The directory structure is the
workspace; the git topology is the policy.

```
/factory/.git/                          ← single monorepo, one history
├── build.mill                          ← tracked
├── flake.nix                           ← tracked
├── .gitignore                          ← tracked (**/out/, upstream/, pub/, secrets/, out/)
├── tools/                              ← tracked, full git
├── hg/<lib>/                           ← tracked (was /p/hg/<lib>)
│   └── out/                            ← gitignored (Mill cache)
├── wiki/                               ← tracked via git subtree merge
├── upstream/<lib>/                     ← gitignored, own .git (was /p/gh/<lib>)
├── pub/<lib>/                          ← gitignored, own .git (rsync target)
├── secrets/                            ← gitignored, sops-encrypted at rest
└── out/                                ← gitignored (root Mill cache)
```

Cross-project refactor inside `hg/` and `wiki/` is a single commit.
Forks and public mirrors stay independently pullable/pushable.
Secrets sit inside the tree but never enter the monorepo's history.

## Proposed Approach (accepted)

### Git topology

ADR-0001 establishes the single-git layout. Wiki is absorbed via
`git subtree add --prefix=wiki/ <wiki-repo> main --squash=false` so
that wiki history rebases into the monorepo. Forward-going commits
land directly in the monorepo; the wiki's old standalone repo
becomes a dormant historical record.

The personal-repo commit policy (unsigned, no Co-Authored-By, author
`tigidar`) applies to the entire monorepo, **superseding the wiki's
prior Co-Authored-By policy**. The override:

- Applies to: `/factory/.git/` (everything tracked)
- Does **not** apply to: `pub/<lib>/.git/` (each follows its own
  publish-flow policy), `upstream/<lib>/.git/` (forks; we don't
  commit there directly).

### Mill build coupling

ADR-0002 establishes decoupled sibling builds. Each `hg/<lib>/build.mill`
is fully standalone — `cd hg/<lib> && mill foo` works without
reference to the root. The root `build.mill` runs cross-cutting jobs
(rsync hg → pub, `dm refresh` across all libs, nightly upstream
sync) by shelling out to per-lib builds when needed. No
`package.mill` discovery, no Mill federation.

This preserves the move-a-library-out-of-monorepo story: if `hg/foo`
ever needs to live elsewhere, its `build.mill` already works
standalone.

Future option (explicitly deferred per Q2 follow-up): a plugin or
generator can emit a federated root `build.mill` that includes
selected children. Not on the critical path.

### `pub/` mirror

ADR-0003 defines the forward sync. Per-library granularity. Filter
keeps:

- Build files (`build.mill`, `package.mill`, `mill-version`, `deps/`)
- Source folders (per-module `src/`, `src-jvm/`, `src-js/`, `src-native/`)
- Test folders
- `README.md`, `LICENSE`, `CHANGELOG.md`
- `doc/` (if present)
- `.gitignore`
- `flake.nix`, `flake.lock` (standalone dev env for external contributors)
- `.scalafmt.conf`, `.scalafix.conf`
- `.mill-version` / `mill-version`

Filter strips:

- `.github/workflows/` — **explicitly excluded** per user follow-up; private and pub workflows may diverge
- `CLAUDE.md`, `AGENTS.md` (internal agent control)
- `wip.md`, `log.md` (internal)
- Any wiki cross-links in source comments

deploymentbox v3 publishes *from* `pub/<lib>`. Tags happen in both
`hg/` and `pub/` (the sync script propagates).

Reverse sync (pub → hg) is **semi-manual cherry-pick**: a helper
script in `tools/` extracts external PR commits, replays them on
the corresponding `hg/<lib>/` directory inside the monorepo, and
leaves the operator to commit with the standard policy.

### `upstream/` forks

ADR-0004 establishes the fork-first rule. Every external library we
read is forked into our org first, then cloned to `upstream/<lib>/`.
The `sources/raw/code/<name>.md` bridge records both the upstream
URL and the fork URL. A nightly sync job (location deferred —
likely a root `build.mill` task) rebases each fork against upstream.

### Nix

Single root `flake.nix` provides `devShells.default` — JDK, Mill,
node, clang, cargo, age, sops, rsync, plus per-toolchain helpers.
`/factory/.envrc` (direnv) activates it workspace-wide. Each
`hg/<lib>/` may add its own `.envrc` + `flake.nix` when its needs
diverge from the workspace shell (compositor, browser); nested
direnv handles the activation.

Each `pub/<lib>/` carries a **standalone** `flake.nix` generated by
the sync script. It pins the same toolchain versions as the
workspace root's `flake.lock` at sync time, ensuring public builds
match what we built internally.

### Secrets

ADR-0005 inherits the deploymentbox v3 custody contract. `/factory/secrets/`
holds sops-encrypted ciphertext (mode 0644 fine; ciphertext is
harmless without the key). Decryption keys live:

- **Local dev:** `~/.config/sops/age/keys.txt`, mode 0600, outside
  `/factory/`.
- **Production:** YubiKey only; sops-nix decrypts at host activation.

The encrypted-at-rest model means backups carry only ciphertext.
Restoring a leaked backup yields nothing without the YubiKey or the
local key file (which is outside `/factory/` and not in the backup
scope).

### Volume + backups

`/factory/` is its own btrfs subvolume on a dedicated dataset.
Snapper takes periodic snapshots. Restic backs up off-site,
excluding `**/out/`. `/factory/secrets/` is included in the backup
(it's ciphertext). The restore drill verifies the workspace boots
into a working state without access to the key file.

This is operational and not load-bearing enough for its own ADR. It
is documented here so the operator has one place to look when
provisioning.

## Trade-offs

| Concern | Cost |
|---------|------|
| `upstream/` and `pub/` outside the monorepo history | Hassle — two-step workflow for any reverse contribution. Mitigated by tooling. |
| Single git history across all `hg/` | One bad commit can break N libraries. Mitigated by per-lib build standalone-ness — selective Mill `compile` across affected subdirs in a pre-commit hook. |
| Wiki commit policy superseded | Loses Co-Authored-By attribution on wiki commits going forward. Accepted — uniformity wins. |
| Root and children Mill builds decoupled | Cross-tree selective execution and shared task caching unavailable. Mitigated by `dm` for dep tracking and per-lib `out/` caches. |
| `pub/` requires a sync mechanism | Forward auto, reverse semi-manual. Acceptable for our scale (few external PRs expected initially). |

## Open Questions

1. **Migration sequence.** What's the cutover order? Wiki first
   (subtree merge), then `hg/<lib>` directory-by-directory, then
   path-rewrite the wiki to point at new paths? Or all-at-once
   with a freeze window?
2. **Path migration script.** `wiki/fix/migrate-paths-to-factory.py`
   — Python stdlib only, longest-first replacement order, idempotent,
   reports unmatched paths. Test against a sample tree before the
   cutover.
3. **Upstream sync job home.** Root `build.mill` task vs. systemd
   timer vs. plain cron in `tools/`. Defer until first upstream
   needs refreshing.
4. **`build.mill` cross-cutting jobs.** What concrete jobs land at
   root on day one? Minimum: `syncPubAll`, `dmRefreshAll`,
   `nightlyUpstreamSync`. Define the bare set when authoring root
   build.
5. **Existing in-flight work on `/p/wiki/`.** This conversation's
   own changes need to either (a) land on `/p/wiki/` pre-migration
   and be carried by the subtree merge, or (b) wait for the cutover
   and land directly in `/factory/wiki/`. Recommend (a).

## Decision Record

Five ADRs decompose this design:

- [ADR-0001 — Single-git monorepo topology](../adr/0001-single-git-monorepo.md)
- [ADR-0002 — Decoupled per-library Mill builds](../adr/0002-decoupled-mill-builds.md)
- [ADR-0003 — `pub/` mirror policy](../adr/0003-pub-mirror-policy.md)
- [ADR-0004 — `upstream/` fork-first rule](../adr/0004-upstream-fork-rule.md)
- [ADR-0005 — Secrets adopt deploymentbox custody contract](../adr/0005-secrets-adopt-deploymentbox-custody.md)

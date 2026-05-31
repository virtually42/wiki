---
id: factory-adr-0001
title: Single-git monorepo topology at /factory/
kind: normative
status: accepted
project: factory
created: 2026-05-30
compliance:
  adopts: []
  exceptions: []
  deviations: []
  ignores: []
supersedes: []
---

## Context

The current substrate is split across `/p/wiki/`, `/p/hg/*` (one
repo per library), `/p/gh/*` (external library clones), and
`/p/v42/*` (dormant). Cross-project refactors require multi-repo
PRs; the wiki and the code it documents live in separate histories;
toolchain pins drift across repos; cross-cutting jobs (sync,
refresh, lint-all) have no structural home.

An earlier design (`scratch/monorepo-design-wip.md`) proposed a true
code-only monorepo at `/p/factory/`. That design was rejected as too
aggressive: it loses the breakout/portability story and has no place
for the wiki or for external upstream clones.

## Decision

Adopt a single-git monorepo at `/factory/` with selective gitignore
for origin-specific subdirectories.

```
/factory/.git/                          ← single monorepo, one history
├── build.mill                          ← tracked
├── flake.nix                           ← tracked
├── .gitignore                          ← tracked
├── tools/                              ← tracked
├── hg/<lib>/                           ← tracked (was /p/hg/<lib>)
├── wiki/                               ← tracked via git subtree merge
├── upstream/<lib>/                     ← gitignored, own .git
├── pub/<lib>/                          ← gitignored, own .git
├── secrets/                            ← gitignored
└── out/                                ← gitignored
```

Rules:

1. `/factory/.git/` is the only git repo for our own work. All
   `hg/<lib>/` directories are tracked here — no per-library
   `.git/`.
2. The wiki is absorbed via `git subtree add --prefix=wiki/`
   preserving history. After absorption, `/p/wiki/` becomes a
   dormant historical record.
3. `upstream/<lib>/` keeps its own `.git/` so `git pull upstream
   main` continues to work for forks.
4. `pub/<lib>/` keeps its own `.git/` so deploymentbox v3 can
   publish each library independently and so external contributors
   see a clean per-library history.
5. `secrets/` and `out/` (root + per-subdir Mill caches at
   `**/out/`) are gitignored.
6. The personal-repo commit policy (unsigned, no Co-Authored-By,
   author `tigidar`) applies to `/factory/.git/` and to every
   `pub/<lib>/.git/`. This **supersedes** the wiki's prior
   Co-Authored-By policy for forward-going commits.

## Consequences

**Gains:**

- Cross-project refactors across `hg/` and `wiki/` become a single
  commit, rollback-able as a unit.
- The wiki's `sources/raw/code/<name>.md` bridges point into
  `/factory/hg/<name>/` and `/factory/upstream/<name>/` — stable
  workspace-relative paths.
- One commit policy across the workspace; ownership stays per-page
  via `meta/ownership.md` but git mechanics are uniform.
- Cross-cutting tooling (`build.mill`, `tools/`, `flake.nix`) has a
  coherent home.

**Costs:**

- A single bad commit can break multiple libraries simultaneously.
  Mitigated by per-library `build.mill` standalone-ness (ADR-0002)
  and a pre-commit hook that runs `mill __.compile` across affected
  `hg/` subdirs.
- `upstream/` and `pub/` workflows require two-step coordination
  (work in the monorepo, then sync). Mitigated by `tools/` scripts.
- Wiki contributors lose Co-Authored-By attribution on
  forward-going wiki commits. Accepted for uniformity.
- Migration requires a one-time path-rewrite of every `/p/hg/`,
  `/p/gh/`, `/p/wiki/`, `/p/v42/` reference (open question in the
  design doc).

## Alternatives Considered

- **True code monorepo (`modules/` + `apps/` + `native/`).**
  Rejected — loses breakout/portability, no place for wiki or
  upstream clones.
- **Pure workspace (no git at root).** Rejected — marginal gains
  over the current `/p/hg/*` shape.
- **Submodule monorepo.** Rejected — submodule UX is fragile, blast
  radius too high for normal operations.

Full comparison in [[projects/factory/designs/factory-monorepo-topology]].

## Links

- [[projects/factory/designs/factory-monorepo-topology]]
- [[projects/factory/adr/0002-decoupled-mill-builds]]
- [[projects/factory/adr/0005-secrets-adopt-deploymentbox-custody]]
- [[scratch/interview_about_factory]]
- [[scratch/interview_about_factory_followup]]

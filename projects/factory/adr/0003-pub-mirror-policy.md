---
id: factory-adr-0003
title: pub/ mirror policy — filtered one-way sync with semi-manual reverse
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

deploymentbox v3 publishes `no.virtual-architect` artifacts via
GitHub Actions on per-library public repositories. Those public
repos need a source of truth that's separate from the private
monorepo's full contents — both for filtering (internal docs, agent
control files don't ship) and for git history hygiene (external
contributors see a clean per-library log, not the monorepo's
omnibus history).

The interview (Q4) confirmed:

- Per-library `pub/<lib>` repo granularity (not a single umbrella).
- Filter list: build files, source folders, test folders,
  `README.md`, `LICENSE`, `CHANGELOG.md`, `doc/`.
- `.github/workflows/` is **explicitly excluded** from sync
  (private and public workflows may diverge in wording).
- Tagged releases happen in **both** `hg/` and `pub/`.
- Primary direction is one-way (hg → pub); reverse (pub → hg)
  exists for external contributions and is semi-manual.

## Decision

### Forward sync (hg → pub)

Per-library, scripted, idempotent. A `tools/sync-pub <lib>` job (also
exposed as a root `build.mill` task `syncPub`) does the following:

1. Read filter manifest from `tools/sync-pub.toml` (per-library
   overrides allowed).
2. `rsync --delete --filter=<manifest>` from `hg/<lib>/` to
   `pub/<lib>/`.
3. Generate a standalone `flake.nix` in `pub/<lib>/` derived from
   the workspace `flake.lock` (so public builds use the same
   toolchain pin).
4. Stage and commit in `pub/<lib>/.git/` with author `tigidar`,
   unsigned (personal-repo commit policy).
5. Optionally `git push origin main`.

**Default filter — included:**

- All `build.mill`, `package.mill`, `mill-version`, `.mill-version`
- All `deps/` directories
- `src/`, `src-jvm/`, `src-js/`, `src-native/` (per-module)
- `test/`, `src-test/` (per-module)
- `README.md`, `LICENSE`, `CHANGELOG.md`
- `doc/` (if present)
- `.gitignore`
- `flake.nix`, `flake.lock` (regenerated, not copied)
- `.scalafmt.conf`, `.scalafix.conf`
- `.editorconfig` (if present)

**Default filter — excluded:**

- `.github/workflows/` — **explicitly excluded** per Q4 follow-up
- `CLAUDE.md`, `AGENTS.md`
- `wip.md`, `log.md`
- `out/`
- Any path inside `secrets/` or starting with `.env`
- Any in-source comment referring to wiki paths (handled by a
  post-rsync sed pass)

### Versioning

Tagged releases happen in both `hg/` and `pub/`. The sync script
propagates tags from `hg/` to `pub/` after a successful commit.
Tag names are identical (e.g. `v1.2.0`); the `pub/` tag points at
the synced commit, not at the `hg/` commit (they have different
SHAs).

### deploymentbox v3 integration

deploymentbox v3 publishes **from** `pub/<lib>/`. The `release.yml`
workflow in each `pub/<lib>` is authored manually (per
deploymentbox ADR-0007) and is **not** synced from `hg/`. This
preserves the separation between the agent-control side
(`hg/<lib>`) and the publish-flow side (`pub/<lib>` +
deploymentbox).

Internal-only artifacts (e.g. `dependency-manager`) are **not
mirrored to `pub/`**. They publish from `hg/` directly via the
historical v2 path (if revived) or via `mill publishLocal` for
internal consumption.

### Reverse sync (pub → hg)

Semi-manual. When an external contributor opens and merges a PR on
`pub/<lib>`, the operator runs:

```
tools/sync-from-pub <lib> <commit-range>
```

The script extracts the pub commits in `<commit-range>`, applies
them as patches into the corresponding `hg/<lib>/` subtree (handling
the rsync path delta), and leaves the working tree staged for the
operator to review and commit per personal-repo policy.

No automated reverse sync. The semi-manual flow is acceptable
because external PRs are expected to be rare at our scale; when
they become routine, this ADR is revisited.

## Consequences

**Gains:**

- Public repos contain only what's needed for an external user to
  build, test, and contribute.
- deploymentbox v3 flow is unchanged — it already publishes from
  per-library GitHub repos; `pub/<lib>` is just the new local
  rendezvous before the push.
- Tags in both places give us local visibility (`hg/<lib>`) and
  public-source-of-truth alignment (`pub/<lib>`).

**Costs:**

- Two git histories per public library (private `hg/.git/` + public
  `pub/<lib>/.git/`). Acceptable — the public history starts at the
  sync point and is intentionally clean.
- Forward sync must run before every public tag. Easy to forget;
  mitigated by a pre-tag hook or by always invoking
  `syncPub <lib> && tag` together.
- Reverse sync is friction. Mitigated by the semi-manual helper;
  revisited when external PR volume justifies automation.

## Alternatives Considered

- **Sync `.github/workflows/`.** Rejected per Q4 follow-up — public
  and private workflows may legitimately differ.
- **Single `pub/` umbrella repo (all libs in one).** Rejected —
  external users expect per-library repos for individual artifact
  consumption.
- **No `pub/` directory at all; push directly from `hg/` to
  GitHub.** Rejected — loses the filtering boundary; forces the
  filter logic into the push step.
- **Full bidirectional sync.** Rejected — high implementation cost
  for a low-frequency event.

## Links

- [[projects/factory/adr/0001-single-git-monorepo]]
- [[projects/deploymentbox/adr/0007-build-on-github-with-attestations]]
- [[projects/deploymentbox/index]]
- [[projects/factory/designs/factory-monorepo-topology]]

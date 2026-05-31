---
id: factory-adr-0004
title: upstream/ fork-first rule for external library clones
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

The current `/p/gh/*` directory mixes our forks of external
libraries (Mill, Kyo) with bare read-only clones (Airstream,
toml-scala, microvm.nix). The `ingest-external` operation depends
on these clones; if an upstream repo is taken down, renamed, or
force-pushed, our wiki's external-lib pages can no longer be
refreshed and may become unverifiable.

The interview (Q3) settled the naming: `upstream/` rather than
`gh/`. The follow-up (Q3) added the rule: **fork every upstream we
consume, always.**

## Decision

1. Every external library consumed via `ingest-external` lives at
   `/factory/upstream/<lib>/` with its own `.git/` (gitignored from
   the monorepo per ADR-0001).
2. **Fork-first rule:** before adding a new external library, fork
   the upstream into our org (e.g. `git@github.com:tigidar/<lib>`).
   The local clone's `origin` remote points at our fork; an
   `upstream` remote points at the original.
3. The `sources/raw/code/<lib>.md` bridge records both:

   ```yaml
   origin: git@github.com:tigidar/<lib>.git
   upstream: git@github.com:<original-org>/<lib>.git
   ```

4. A periodic sync job rebases each fork against its upstream:

   ```
   cd /factory/upstream/<lib> && \
     git fetch upstream && \
     git rebase upstream/<main-branch> && \
     git push origin <main-branch>
   ```

   The job is defined as a root `build.mill` task
   (`nightlyUpstreamSync`) and is also invocable per-library
   (`mill syncUpstream <lib>`). Schedule (cron/systemd timer)
   deferred — operator triggers manually until the sync becomes
   routine.
5. `ingest-external refresh <lib>` must run **after** an upstream
   sync — it observes the new commit SHA and refreshes wiki pages
   only against forks under our org.

## Consequences

**Gains:**

- Upstream availability becomes our responsibility, not the
  external project's. Even if the original repo disappears, the
  fork remains.
- The wiki's `commit:` field in external-lib bridges is stable
  (we control the remote that field references).
- The fork-first rule gives us a place to apply local patches if
  ever needed (e.g. carrying a backport while waiting for upstream
  merge).
- Manual sync gives us a deliberate moment to inspect upstream
  changes before our wiki refreshes against them.

**Costs:**

- Adding a new external library is a two-step process: fork on
  GitHub, then clone. Small friction, paid once.
- Forks must be kept rebased to remain useful as snapshots. The
  sync job handles this but requires periodic invocation.
- Our org's GitHub footprint grows. Acceptable — these are
  read-mostly forks, not active forks with divergent work.

## Alternatives Considered

- **Read-only clones (no forks).** Current state. Rejected — leaves
  upstream availability outside our control.
- **Fork only when upstream looks unstable.** Rejected — the rule
  needs to be unconditional or we end up making case-by-case
  judgements that drift.
- **Mirror via GitHub's built-in mirror feature.** Rejected — the
  mirror is on GitHub's terms; if our access pattern changes (e.g.
  GitLab move), the mirror story breaks. A regular fork is
  portable.

## Links

- [[projects/factory/adr/0001-single-git-monorepo]]
- [[projects/factory/designs/factory-monorepo-topology]]
- [[tech/guides/ingest-external]]

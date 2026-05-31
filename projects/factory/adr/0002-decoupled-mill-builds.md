---
id: factory-adr-0002
title: Decoupled per-library Mill builds
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

In a monorepo, Mill offers two coupling modes:

1. **Federated.** Root `build.mill` discovers each subdir's
   `package.mill`. One Mill process sees the whole tree; selective
   execution scopes tasks. But `cd hg/<lib> && mill foo` doesn't
   work standalone — Mill expects the root.
2. **Decoupled.** Each `hg/<lib>/build.mill` is a complete,
   standalone Mill build. The root has its own independent
   `build.mill` for cross-cutting jobs. Subdir builds are runnable
   in isolation.

The original portability goal (a library must be movable into or
out of the monorepo without silent breakage) and the explicit
constraint from the design interview ("each project totally
independent from root build.mill") favour decoupling.

## Decision

Adopt **decoupled Mill builds**:

1. Every `/factory/hg/<lib>/build.mill` is a complete, standalone
   Mill build. It must be runnable as `cd hg/<lib> && mill <task>`
   with no reference to any file outside `hg/<lib>/`.
2. The root `/factory/build.mill` is **independent** of per-library
   builds. It runs only cross-cutting jobs:
   - `syncPubAll` — rsync hg/<lib> → pub/<lib> for all libraries
     marked public
   - `dmRefreshAll` — invoke `dm refresh` against the catalog
   - `nightlyUpstreamSync` — rebase every `upstream/<lib>/` fork
     against its upstream
   - other infrastructure tasks as they emerge
3. The root build invokes per-library builds **by shelling out**
   (`( cd hg/<lib> && mill <task> )`), never by importing or
   federating their `build.mill`.
4. No `package.mill` discovery from root. Future option to generate
   a federated root build (via plugin or script) is explicitly
   deferred and **not on the critical path**.

## Consequences

**Gains:**

- Each library can be extracted out of the monorepo at any time
  (`pub/` sync is the structured form of this).
- A standalone `cd hg/<lib>` developer experience matches what
  external contributors see in `pub/<lib>` — no surprises.
- Build failures stay localised — one library's broken
  `build.mill` doesn't break the whole tree's tasks.
- The root `build.mill` stays small and focused on infrastructure;
  it doesn't grow with the number of libraries.

**Costs:**

- No cross-tree Mill selective execution. A pre-commit hook that
  runs `mill __.compile` against affected subdirs is the
  replacement.
- No shared Mill task cache across subdirs. Each `hg/<lib>/out/`
  is independent. Acceptable — disk is cheap, cross-lib cache
  reuse was speculative anyway.
- Cross-library deps still need to be tracked. `dm` handles this
  (see deferred open question in
  `projects/dependency-manager/designs/dm-architecture.md` — closed:
  `dm` stays as a meta-tool, factory does not absorb it).

## Alternatives Considered

- **Mill federation via `package.mill` discovery.** Rejected:
  breaks standalone-buildable subdir invariant.
- **Hybrid (root federates some, others standalone).** Rejected:
  inconsistent UX, hard to explain when a given subdir is or isn't
  federated.
- **Root `build.mill` empty, no cross-cutting jobs.** Rejected:
  cross-cutting jobs need a home, and `tools/` shell scripts are
  less discoverable than Mill tasks.

## Links

- [[projects/factory/adr/0001-single-git-monorepo]]
- [[projects/factory/adr/0003-pub-mirror-policy]]
- [[projects/factory/designs/factory-monorepo-topology]]
- [[projects/dependency-manager/designs/dm-architecture]]
- [[tech/guides/mill-monorepo]]

---
id: factory-design-interview
title: Interview — Factory monorepo topology decisions
kind: working-notes
status: open
created: 2026-05-30
related_scratch:
  - scratch/monorepo-design-wip.md
  - scratch/wiki_current_state_with_monorepo.md
---

# Interview: Factory Topology

Working doc. Each section: question, context/options, my lean, your
answer. When all answers are in, this gets distilled into a proper
design doc under `projects/factory/designs/`.

## Proposed sketch (the thing we're interviewing)

```
/factory/
├── build.mill       # meta build — lists projects, cross-project workflows
├── wiki/            # the wiki as-is
├── hg/              # homegrown private repos
├── gh/              # github repos
├── gl/              # gitlab repos
├── cb/              # codeberg repos
└── pub/             # public mirrors of hg, .gitignored, self-contained git repos
```

Key divergence from the original `/p/factory/` design (see
`scratch/monorepo-design-wip.md`): the original was **one git repo**
with `modules/` + `apps/` + `native/` at root (true monorepo). This
sketch is a **workspace umbrella organised by origin**, each subdir
keeping its own git autonomy. Pragmatic — preserves the breakout /
portability story we already invested in.

---

## Q1 — Is `/factory/` itself a git repo?

The single most consequential question. Three options:

- **(a) Pure workspace** — no git at root, just a directory hosting
  independent repos. Simplest; no monorepo semantics to fight.
- **(b) Thin meta-repo** — tracks only `build.mill`, `tools/`,
  `flake.nix`, `meta/`; all subdirs `.gitignored`. Gives one place to
  version cross-cutting orchestration.
- **(c) Submodule monorepo** — root tracks each subdir as a submodule.
  Most painful, hardest to keep in sync, biggest blast radius.

**Lean:** (b). Without it, "factory root" is just a folder, and
`build.mill` has nowhere to live coherently.

**Answer:**

Yes /factory is a monorepo tracked by git, except for the factory/pub which is .gitignored at root, this is where our open sourced libraries lives, they are just rsynced from our /factory/hg/ directory in principle. Hence:

/factory/hg/sourceline-manager
/factory/pub/sourceline-manager a filtered rsync, i.e. we grab only the files we need, it has its own ci / .github workflow according to our strategy for building and publishing open source libraries.

---

## Q2 — What does the root `build.mill` actually do?

Each subdir already has its own Mill build. The root can be:

- **Orchestration only** — shell out to subdir builds, aggregate
  observations, run cross-project workflows (rebuild-all, ingest-all,
  lint-all).
- **Mill federation** — reference each subdir's `build.mill` via
  Mill's external-module mechanism. Powerful but couples versions.
- **Meta-tasks only** — `dm refresh`, `wiki lint`, `breakout`,
  deploymentbox publish pipelines.

**Lean:** meta-tasks + orchestration. Federation is probably too tight
and re-introduces the monorepo coupling we deliberately avoided.

**Answer:**

> I think we start just defining our downstream projects in /factory/hg folder at a high level so that we can use mill to investigate from root. However each project has its own self contained build.mill, it should be totally independent from the root build.mill. Then it would contain the tasks we need, for example running rsync etc. to update our public repositories for example. Everything that is infrastructure related should exists as jobs in that meta build.

---

## Q3 — `gh/` is semantically different from `hg/`

- `hg/` = our own private homegrown work.
- `gh/`, `gl/`, `cb/` = **external upstream clones we read for
  `ingest-external`** (Mill, Kyo, Airstream, toml-scala, microvm.nix).

Different lifecycle — we don't write there, we pull. Options:

- **Name the distinction** — `upstream/gh/`, `upstream/gl/`,
  `upstream/cb/`.
- **Accept origin-by-folder is the rule** — `gh/` includes both our
  forks and read-only clones (current `/p/gh/` already mixes both).
- **Split read vs write** — `gh-read/` vs `gh-fork/` etc.

**Lean:** name the distinction. `upstream/` is honest, `hg/` (and
`pub/`) is ours. Browsing `/factory/upstream/kyo/` makes the
read-only intent obvious.

**Answer:**

> Nice, yes upstream is better, keep it. Also, I think we want forks on all of our upstream repositories, that way we will always have them available. This should be a rule.

---

## Q4 — `pub/` mirror sync mechanism

You said "mirrored from hg, self-contained git repos." Decisions
needed:

- **Granularity:** per-library pub repo, or one pub umbrella?
- **Filter:** what strips on the way out (history? `CLAUDE.md`?
  internal ADRs? wiki links?).
- **Relationship to deploymentbox:** tied to v3 publishing, or
  independent (mirror first, then publish from the public mirror)?
- **Versioning:** do tagged releases happen in hg, in pub, or both?
- **Direction:** one-way push (hg → pub), or bidirectional (accept
  outside contributions in pub, merge back to hg)?

**Lean:** per-library pub repo, one-way push, strips internal wiki
links + ADRs but keeps history if possible, tags happen in pub (it's
the public source of truth for the artifact), deploymentbox v3
publishes *from* pub.

**Answer:**

> 

- **Granularity:** per-library pub repo, we want independent repositories
- **Filter:** We keep build files, source folders, test folders, README.md, LICENSE, CHANGELOG.md, doc folder, nothing else. Tell me if I missed something important here.
- **Relationship to deploymentbox:** tied to v3 publishing yes, publish from the public repository when working on the open source stuff, the internal stuff will always use hg directly.
- **Versioning:** We do tagged releases in both I think
- **Direction:** mainly one-way push (hg → pub), but also support for bidirectional (accept
  outside contributions in pub, merge back to hg)? i.e. we need a sync script that goes from pub to hg as well.

---

## Q5 — Where does Nix live?

Original design had **one outer flake at `/factory/`** pinning the
toolchain for everything. Options:

- **Single root flake** — one source of truth, but every subdir
  checked out standalone loses it.
- **Per-repo flakes** — current state, works but drifts.
- **Both** — root flake for workspace dev shell + per-repo flakes for
  standalone use, root composes/imports children where it makes
  sense.

**Lean:** both. Root flake is the lowest-common-denominator dev shell
(JDK + Mill + node + clang + cargo + nix tools). Per-repo flakes
override only when a repo has genuinely different needs (compositor
needs wlroots, browser needs whatever the browser needs, etc.).

**Answer:**

> I think we try both here, but let me know if you think this will be convoluted in practice. We need to have separate / standalone flakes in the open source repositories I think. It should be easy for an LLM to generate those, since they are standalone and quite distinct and we can steal whatever we need from the private ones.

---

## Q6 — Agent surface

Where do these live?

- `tools/{build,test,run,observe}.sh` — JSON observation contract
  from the original design.
- `out/observations/` — handoff buffer between agent and wiki.
- `fix/` — idempotent scripts for human-owned edits (currently a
  top-level wiki concept).

**Lean:**

- `/factory/tools/` (tracked in the thin meta-repo).
- `/factory/out/` at root, `.gitignored`.
- `fix/` stays inside `/factory/wiki/fix/` — it's a wiki concept, not
  a factory concept.

**Answer:**

> yes keep the lean approach, but we want full git for the tools directory as well, not thin

---

## Q7 — `/p/v42/` plugins location

Current working dirs include `/p/v42/tagless/tags/test/src-jvm/tags`
— virt42 plugin code lives there today. Options:

- `/factory/v42/` as its own category.
- Folded into `/factory/hg/` (it's ours).
- `/factory/pub/v42/` (if v42 plugins are intended to be public).

**Lean:** depends on whether v42 plugins are private tooling or
public. If private, fold into `hg/`. If public-eventually, keep
`/factory/v42/` distinct so the boundary is visible.

**Answer:**

The v42 stuff will disappear, everything in there should be ignored pr now, this is a rule. We will move these things into the monorepo at /factory/hg step by step through breakout session and handle things piece by piece.

---

## Q8 — `scratch/` for human notes

Currently `/p/wiki/scratch/`. Options:

- **Stay in wiki** — `/factory/wiki/scratch/`. Keeps the
  human-owned-notes concept inside the place that defines ownership.
- **Hoist to root** — `/factory/scratch/`. Decouples from wiki
  schema; useful if scratch crosses projects beyond wiki concerns.

**Lean:** stay in wiki for now. The ownership and lint-exclusion
rules are wiki concepts. Hoisting can happen later if scratch
genuinely outgrows the wiki.

**Answer:**

> Keep under the wiki

---

## Q9 — Secrets / sops / age keys

Where do they live? Probably `/factory/secrets/` at root,
`.gitignored`. Decisions:

- Single age key for the whole factory, or per-repo keys?
- Does deploymentbox v3 (YubiKey-signed releases) need anything
  beyond what's already in the deploymentbox project?
- How do secrets cross the wiki ↔ code boundary (or do they)?

**Lean:** `/factory/secrets/` as the location, single age key for
local dev, sops-nix per-host on deployed machines, deploymentbox
stays as-is.

**Answer:**

> yes, keep a secrets directory under /factory, I guess this would be owned by root right ? and only root can read, write, execute in that directory ? 

---

## Q10 — Path migration

Mechanical but large. Affected:

- Every `sources/raw/code/*` bridge file (currently points to
  `/p/gh/<name>`, `/p/hg/<name>`).
- Every wiki reference to `/p/hg/`, `/p/gh/`, `/p/wiki/`, `/p/v42/`.
- `tools/update-all.sh` (currently iterates `/p/hg/*`).
- `CLAUDE.md` working-directory references.
- External library wikis (Mill, Kyo, Airstream, toml-scala,
  microvm.nix) — their bridges point at `/p/gh/<name>`.
- Any direnv / `.envrc` files in subdirs.

**Lean:** single idempotent sweep script in `fix/` rather than
ad-hoc edits. Plan the migration as one cutover with the script
re-runnable, so partial completion isn't catastrophic.

**Answer:**

> Yes, this must be done using a script, i.e. sed would be enough for this right ? it is pretty easy to match and we can search afterwards for things that didn't get replaced.

---

## Q11 — Volume / mount strategy

You mentioned "could be a separate volume or similar." Questions:

- Is `/factory/` a dedicated volume / btrfs subvol / zfs dataset?
- Does it sync across machines (syncthing, rsync, none)?
- Is there a snapshot policy (btrfs/zfs snapshots, restic backups)?
- Where do `out/` and `secrets/` live relative to the snapshot
  policy (you usually don't want `out/` snapshotted, but `secrets/`
  yes)?

**Lean:** btrfs subvol for `/factory/`, separate subvol for
`/factory/out/` (not snapshotted), `secrets/` snapshotted, restic
to off-site for the whole thing minus `out/`. But this is ops; can
be deferred.

**Answer:**

> I think a separate volume is preferable, also btrfs subvolumes are good, but I am concerned having secrets on such a filesystem, does this make sense ? Could we risk leaking things through backup mechanisms etc. ? What about having secrets on a separate volume as well ? We need to discuss this and look for best practices as it is a very important topic.

---

## Q12 — Project registration

This design currently lives in `scratch/`. Once decisions are made,
should `factory` become a real wiki project at
`projects/factory/`?

- ADRs for the topology decisions (Q1, Q3, Q4, Q5).
- A design doc distilled from this interview.
- `sources/raw/code/factory.md` bridge file pointing at the root.

**Lean:** yes. The original design doc and gap analysis already
treat factory as a project — it just never got promoted out of
scratch. Now is the time.

**Answer:**

> I am not sure, the factory is more of a concept that we will implement, maybe projects/factory is a good idea to track our work and then it can be deleted when we are done. The history here is not of importance at all I think, it is more accidental that we didn't create it like this in the first place.

---

## Things I might be missing

Flag any of these you want added as Q13+:

- CI strategy — does the factory have its own CI, or do per-repo
  CIs remain authoritative?
- Backup/restore drills — when does the human verify restore works?
- IDE setup — does Metals see one workspace, or one per repo?
- `direnv` / shell-init story across the workspace.
- Cross-repo refactors — when a change touches `tagless/` and
  `shapesdsl/` together, what's the workflow?
- The `dependency-manager` open question — does `dm` continue as
  meta-tool, or does the root `build.mill` absorb it?

My answers pr point:

- CI strategy can be defferred, we do not know exactly how that should be implemented yet.
- Since we have a separate volume, the backup / restore should be fairly straightforward
- IDE setup, we start metals pr repository, it should not deal with the whole picture at all.
- yes, apply `direnv` per repository if that can work, i.e. I guess one could move out of one direnv and into yet another right?
- I think we do cross repo refactoring and keep it as one commit, then if something was wrong we can roll back the whole thing, any downsides to this approach, let me know.
- dm is a meta-tool and not absorbed by root build.mill. I guess root `build.mill` can use it as it sees fit, and we might have jobs utilizing that tool as any other tool.





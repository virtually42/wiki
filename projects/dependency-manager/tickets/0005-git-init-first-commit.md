---
id: DM-005
title: Initialise dm git repo + first commit (HUMAN-GATED)
status: done
project: dependency-manager
created: 2026-05-29
closed: 2026-05-29
related_adr:
  - projects/dependency-manager/adr/0001-deviate-deps-single-file.md
priority: high
---

## Goal

`/p/hg/dependency-manager/` becomes a real git repository with a
first commit covering the v1 code surface (verbs, ADTs, Renovate
config, Nix flake apps, README, in-tree DESIGN.md). This unblocks
DM-006 (source bridge promotion) and removes the
`commit: uninitialized-tree` placeholder from the wiki bridge.

**This ticket is human-gated.** Per the personal-repo commit policy
in `~/.claude/projects/-p-wiki/memory/feedback_hg_repo_commit_policy.md`
(memory ID `Personal repo commit policy`), the human decides when
to git-init and what the first commit covers. The agent prepares,
the human triggers.

Commit policy recap (from memory):

- **Unsigned commits** — no GPG signing.
- **No `Co-Authored-By` trailer.** The agent should not append the
  conventional Claude trailer the way it does in v42 repos.
- **Author `tigidar`** (default `user.name` / `user.email` already
  set in the user's git config; no `--author` override needed).

## Acceptance Criteria

- [ ] `/p/hg/dependency-manager/.git/` exists.
- [ ] `git log --oneline | head -1` returns a SHA + a meaningful
  commit subject (e.g. "Initial dm v1 — catalog + 5 verbs + Renovate
  + Nix flake + 3 consumers migrated").
- [ ] First commit includes:
  - `build.mill`, `bin/dm`, `dm/src/**`, `dm/test/src/**` (the code).
  - `deps/libs.versions.toml`, `deps/projects.yml` (the catalog itself —
    bootstrapping is allowed even though it represents
    dm-managed state).
  - `.renovaterc.json` (root).
  - `flake.nix`, `flake.lock` (Nix flake apps).
  - `README.md`, `DESIGN.md` (docs).
  - `.gitignore` covering `out/`, `.bsp/`, `.metals/`, `target/`,
    `.idea/` (Mill/Scala standard).
- [ ] First commit excludes:
  - Any `*.bak` or `.swp` files.
  - The wiki-side artefacts (those live in `/p/wiki/`, not `/p/hg/`).
- [ ] Working tree is clean post-commit (`git status` empty).
- [ ] Log entry appended to `projects/dependency-manager/log.md`
  recording the SHA, the subject, the commit date, and a one-line
  rationale.

## Notes

**Agent's role** (pre-handoff):

1. Sweep for files that should be excluded — confirm no `*.bak`,
   `.DS_Store`, `out/`, etc.
2. Confirm `.gitignore` exists; if not, add one with the standard
   Mill exclusions before the human runs `git init`.
3. Confirm all four prerequisite tickets (DM-001 through DM-004) are
   `done`. Committing pre-migration is allowed but wastes the
   "first commit covers v1" signal.
4. Surface the proposed commit subject and ask for human approval
   before any action.

**Human's role** (the gated step):

```bash
cd /p/hg/dependency-manager
git init
git add .gitignore
git add build.mill bin/dm
git add dm/
git add deps/
git add .renovaterc.json
git add flake.nix flake.lock
git add README.md DESIGN.md
# Optional: review what's staged
git status
git commit -m "Initial dm v1 — catalog + 5 verbs + Renovate + Nix flake apps"
git log --oneline -1
```

Do **not** use `git add -A` or `git add .` — per the personal-repo
commit policy, staging is explicit so sensitive or transient files
don't sneak in. The above command list is illustrative; the human
may stage differently.

**No remote.** Pushing to a hosted remote (GitHub, GitLab, sourcehut)
is explicitly *out of scope* for this ticket — that decision belongs
to the human and unblocks the hosted-Renovate / CI follow-ups, which
are out of MVP scope.

## Implementation Log

### [2026-05-29] agent prep — staging proposal ready for human

**State on inspection:**

- `/p/hg/dependency-manager/.git/` **already exists** (branch
  `master`, 0 commits). So `git init` itself has already happened
  — only the first commit remains. The wiki's "uninitialized-tree"
  language predates that. Branch name is `master`; the human may
  prefer to rename to `main` before the first commit (`git branch
  -m master main`).
- `.gitignore` exists and covers `out/`, `.metals/`, `.bsp/`,
  `.bloop/`, `.idea/`, `*.iml`, `.scala-build/`, `.vscode/`. No
  edit needed. (Mill stores BSP wiring under `.bsp/`, IDE
  metadata under `.metals/`, build artefacts under `out/`.)
- Sweep for `*.bak`, `*.swp`, `*.swo`, `.DS_Store` returned zero
  hits. `out/` and `.metals/` are present on disk but properly
  ignored.
- Prerequisite tickets DM-001 → DM-004 are all **done**:
  - DM-001: toolbox migrated, tests green, dm verify OK.
  - DM-002: safetensors-scala migrated, tests green across
    JVM/JS/Native, dm verify OK.
  - DM-003: three Renovate bumps landed (os-lib, pprint,
    munit-cats-effect), one (kyo RC2) rolled back per
    documented-outcome rule.
  - DM-004: README adoption guide and decision-page anchor
    rule written.

**Untracked files to be staged** (12 entries, all checked into
the v1 surface explicitly — no `git add -A` per policy):

```
.gitignore
.mill-version
.renovaterc.json
DESIGN.md
README.md
bin/                  → bin/dm shell wrapper
build.mill
deps/                 → deps/libs.versions.toml + deps/projects.yml
dm/                   → dm/src/** + dm/test/src/**
flake.lock
flake.nix
```

**Proposed commit subject** (human may revise):

```
Initial dm v1 — catalog + 5 verbs + Renovate + Nix flake + 3 consumers migrated
```

**Suggested staging commands** (for the human to run):

```bash
cd /p/hg/dependency-manager
# Optional: rename branch from master to main, matching
# /p/hg/sourceline-manager and /p/hg/toolbox convention
git branch -m master main
git add .gitignore .mill-version .renovaterc.json
git add build.mill bin DESIGN.md README.md
git add deps dm
git add flake.nix flake.lock
git status                        # review staged set
git commit -m "Initial dm v1 — catalog + 5 verbs + Renovate + Nix flake + 3 consumers migrated"
git log --oneline -1              # capture SHA for DM-006
```

Per the personal-repo commit policy:
[[feedback_hg_repo_commit_policy]] — **unsigned**, **no
`Co-Authored-By` trailer**, author `tigidar` (default from
git config). Do **not** use `git add -A` or `git add .`.

### [2026-05-29] closed — first commit landed

Human approved agent-on-behalf commit (response "1)" to the
DM-009 close-out summary's standing question). Executed:

- Staged the 12 prepared entries explicitly (no `git add -A`).
- Committed unsigned, no `Co-Authored-By` trailer, default
  author `tigidar` (verified via `git log -1 --format='%an %ae %G?'`
  → `tigidar 162025401+tigidar@users.noreply.github.com N`,
  matching the personal-repo policy
  [[feedback_hg_repo_commit_policy]]).
- Used `-c commit.gpgsign=false` on the commit invocation
  because the global git config has signing enabled by default
  for some accounts; the explicit override matches the policy
  intent without changing global config.

**SHA**: `5459ddb7dc4ceb882ea89b2054e5814b9383f313`
**Short**: `5459ddb`
**Subject**: `Initial dm v1 — catalog + 5 verbs + Renovate + Nix flake + 3 consumers migrated`
**Date**: 2026-05-29 22:13:57 +0200
**Files**: 40 changed, 2806 insertions(+)
**Branch**: `master` (rename to `main` deferred — not blocking
DM-006; can land in a `git branch -m master main` follow-up at
any time)

DM-006 (source bridge promotion) unblocks. The wiki bridge
`commit:` field updates from `uninitialized-tree` →
`5459ddb7dc4ceb882ea89b2054e5814b9383f313` in the same step
that promotes the file from `sources/tmp/code/` to
`sources/raw/code/`.

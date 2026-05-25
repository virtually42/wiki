---
id: source-mill
type: external-lib
repo: /p/gh/mill
origin: https://github.com/com-lihaoyi/mill.git
upstream: https://github.com/com-lihaoyi/mill.git
wiki_branch: llm-wiki
last_observed: 2026-05-24
commit: 41ce6c977c4
wiki_sections:
  - concepts
  - modules
  - configuration
  - patterns
  - recipes
  - cli
---

## Purpose

Mill is our build tool for all Scala 3 projects (JVM, JS, Native). Used to
define multi-module builds, manage dependencies, cross-compile, test, and
publish artifacts. Central to the monorepo build system.

## Wiki Branch

```bash
cd /p/gh/mill && git checkout llm-wiki
# Query entry point:
cat llm-wiki/index.md
```

The `llm-wiki/` folder contains 40 pages across 6 sections with YAML
frontmatter for grep-based discovery. See `llm-wiki/CLAUDE.md` for
query strategy.

## Refresh Procedure

```bash
cd /p/gh/mill
git checkout llm-wiki
git fetch origin   # this is the upstream repo (no fork yet)
git rebase origin/main
# llm-wiki/ folder never conflicts — upstream doesn't have it
# Then run ingest-external refresh mill to update stale pages
```

## Note

This repo is cloned directly from upstream (com-lihaoyi/mill), not
from a personal fork. The `llm-wiki` branch is local only. If a fork
is created later, update `origin` to point to the fork and add the
upstream remote.

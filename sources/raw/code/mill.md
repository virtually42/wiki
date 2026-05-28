---
id: source-mill
type: external-lib
repo: /p/gh/mill
origin: https://github.com/com-lihaoyi/mill.git
upstream: https://github.com/com-lihaoyi/mill.git
wiki_path: mill/llm-wiki/
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

## Wiki Location

The wiki lives in this repo at `mill/llm-wiki/`. Source code lives at `/p/gh/mill`.

Pages reference source files with absolute paths (e.g. `/p/gh/mill/libs/scalalib/src/mill/scalalib/ScalaModule.scala`).

## Refresh Procedure

```bash
# 1. Update source repo
cd /p/gh/mill
git fetch origin   # cloned directly from upstream, no fork
git rebase origin/main

# 2. Back in wiki, update stale pages against new source
# Compare source_commit in page frontmatter against current HEAD
```

## Note

This repo is cloned directly from upstream (com-lihaoyi/mill), not
from a personal fork. If a fork is created later, update `origin` to
point to the fork and add the upstream remote.

---
id: source-kyo
type: external-lib
repo: /p/gh/kyo
origin: git@tigidar:tigidar/kyo.git
upstream: git@tigidar:getkyo/kyo.git
wiki_path: kyo/llm-wiki/
last_observed: 2026-05-24
commit: 9bab8d00
wiki_sections:
  - concepts
  - effects
  - data
  - modules
  - patterns
  - conventions
  - recipes
---

## Purpose

Kyo is our primary effect system for Scala 3 development. Used across all
Scala projects for algebraic effects, concurrency, streaming, HTTP, and more.

## Wiki Location

The wiki lives in this repo at `kyo/llm-wiki/`. Source code lives at `/p/gh/kyo`.

Pages reference source files with absolute paths (e.g. `/p/gh/kyo/kyo-core/shared/src/main/scala/kyo/Scope.scala`).

## Refresh Procedure

```bash
# 1. Update source repo
cd /p/gh/kyo
git fetch upstream
git rebase upstream/main

# 2. Back in wiki, update stale pages against new source
# Compare source_commit in page frontmatter against current HEAD
```

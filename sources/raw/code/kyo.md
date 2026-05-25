---
id: source-kyo
type: external-lib
repo: /p/gh/kyo
origin: git@tigidar:tigidar/kyo.git
upstream: git@tigidar:getkyo/kyo.git
wiki_branch: llm-wiki
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

## Wiki Branch

```bash
cd /p/gh/kyo && git checkout llm-wiki
# Query entry point:
cat llm-wiki/index.md
```

The `llm-wiki/` folder contains 65 pages across 8 sections with YAML
frontmatter for grep-based discovery. See `llm-wiki/CLAUDE.md` for
query strategy.

## Refresh Procedure

```bash
cd /p/gh/kyo
git checkout llm-wiki
git fetch upstream
git rebase upstream/main
# llm-wiki/ folder never conflicts — upstream doesn't have it
# Then run ingest-external refresh kyo to update stale pages
```

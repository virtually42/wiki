---
id: source-toml-scala
type: external-lib
repo: /p/gh/toml-scala
origin: git@github.com:virtually42/toml-scala.git
upstream: https://github.com/indoorvivants/toml-scala.git
wiki_path: toml-scala/llm-wiki/
last_observed: 2026-05-29
commit: 03d4e5f
wiki_sections:
  - concepts
  - api
  - data
  - codecs
  - derivation
  - recipes
---

## Purpose

`toml-scala` is a standards-compliant TOML parser, codec, and generator
for Scala 2.12, 2.13, and 3 on JVM / Scala.js / Scala Native. We use it
for project configuration parsing where TOML's structured-text shape
beats raw JSON or YAML on readability.

## Wiki Location

The wiki lives in this repo at `toml-scala/llm-wiki/`. Source code
lives at `/p/gh/toml-scala`.

Pages reference source files with absolute paths, e.g.
`/p/gh/toml-scala/core/src/main/scala/toml/Codec.scala`.

## Refresh Procedure

```bash
# 1. Update source repo
cd /p/gh/toml-scala
git fetch upstream
git rebase upstream/master   # confirm branch name on the remote first

# 2. Back in wiki, update stale pages against new source
# Compare source_commit in page frontmatter against current HEAD
```

## Note

`origin` points to the personal `virtually42` fork. Upstream is
`indoorvivants/toml-scala` (itself a maintained fork of the original
`sparsetech/toml-scala`).

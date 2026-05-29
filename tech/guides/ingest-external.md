---
id: guide-ingest-external
title: "Ingest External Library"
kind: descriptive
status: accepted
scope: global
created: 2026-05-24
updated: 2026-05-28
tags: [ingest, external-library, llm-wiki, query]
ownership: shared
ownership_reason: procedure definition — human reviews, agent executes
---

## Purpose

Create a query-optimized llm-wiki for a third-party library we use
frequently. The wiki lives in this repo under `<name>/llm-wiki/`,
with `source_files:` frontmatter pointing to absolute paths in the
source repo at `/p/gh/<name>`.

## When to Use

- Library is a core dependency (used across multiple projects)
- We'll query it repeatedly during coding sessions
- The library has enough API surface that reading raw docs is slow

## Procedure: `ingest-external <name>`

### Prerequisites

1. Library source exists at `/p/gh/<name>`
2. Upstream remote is configured if using a fork

### Steps

```
1. Create wiki structure in this repo:
   mkdir -p <name>/llm-wiki/{meta,concepts,modules,patterns,conventions,recipes}
   (adjust sections to match the library's domain)

2. Read the library's key docs at /p/gh/<name>:
   - README.md (overview, API docs)
   - CONTRIBUTING.md (conventions, patterns)
   - AGENTS.md or similar (if exists)
   - Source files for API surface

3. Create control files:
   - <name>/llm-wiki/CLAUDE.md     (~25 lines, query dispatch, source repo path)
   - <name>/llm-wiki/meta/schema.md (page formats for this wiki)
   - <name>/llm-wiki/index.md       (root catalog with quick lookup table)

4. Create section indexes:
   - Each section gets an index.md with a table of all pages

5. Create content pages:
   - One page per concept, API, module, pattern
   - Every page has YAML frontmatter with:
     id, title, category, layer, tags, source_files,
     source_commit, api_surface, related, see_also
   - source_files use ABSOLUTE paths: /p/gh/<name>/path/to/file.scala
   - Focus on what a developer NEEDS to use the API correctly

6. Register in main wiki:
   - Create sources/raw/code/<name>.md with type: external-lib
   - Set repo, origin, upstream, wiki_path, sections

7. Commit in this wiki repo
```

### Section Selection

Not every library needs all sections. Choose based on the library:

| Section | Include when |
|---------|-------------|
| concepts | Library has non-obvious mental model (effect system, type-level) |
| effects/apis | Library exposes many distinct APIs or types |
| data | Library has custom data types to learn |
| modules | Library is modular (sub-packages, plugins) |
| patterns | Common usage patterns aren't obvious from API |
| conventions | Library has code style rules (contributing guide) |
| recipes | Task-oriented "how to build X" is useful |

### Page Schema

See `<name>/llm-wiki/meta/schema.md` for the full spec.
Key frontmatter fields:

```yaml
---
id: <lib>-<category>-<name>     # unique within this wiki
title: "Human Title"
category: concept | effect | data | module | pattern | convention | recipe
layer: foundation | core | integration | application
tags: [searchable, keywords]
source_files: [/p/gh/<lib>/path/to/source.scala]  # absolute paths
source_commit: <short-hash>      # for staleness tracking
api_surface: [Type.method, ...]  # for grep-based discovery
related: [other-page-ids]
see_also: [pattern-ids]
---
```

## Procedure: `ingest-external refresh <name>`

Update an existing llm-wiki after the source repo rebases on upstream.

```
1. Read sources/raw/code/<name>.md to find repo path
2. cd /p/gh/<name> — check current HEAD commit
3. Compare HEAD to source_commit in wiki pages
4. For pages where source_files have changed since source_commit:
   - Re-read the source files
   - Update the page content
   - Update source_commit to current HEAD
5. Check for new APIs/modules not yet covered:
   - Scan source directories for files not referenced by any page
   - Create pages for significant additions
6. Rebuild index pages from current frontmatter
7. Update sources/raw/code/<name>.md with new commit and last_observed
```

## Procedure: `ingest-external query <name> <question>`

Query an external library's wiki.

```
1. Read sources/raw/code/<name>.md to find wiki_path
2. Read <name>/llm-wiki/CLAUDE.md for query strategy
3. Follow the discovery chain in <name>/llm-wiki/index.md
4. If page references source_files, verify against /p/gh/<name> if stale
```

## Existing External Libraries

| Library | Source Repo | Wiki Path | Sections |
|---------|-----------|-----------|----------|
| Kyo | /p/gh/kyo | kyo/llm-wiki/ | concepts, effects, data, modules, patterns, conventions, recipes |
| Mill | /p/gh/mill | mill/llm-wiki/ | concepts, modules, configuration, patterns, recipes, cli |
| Airstream | /p/gh/Airstream | Airstream/llm-wiki/ | concepts, signals, streams, state, ownership, transactions, operators, patterns, conventions |
| toml-scala | /p/gh/toml-scala | toml-scala/llm-wiki/ | concepts, api, data, codecs, derivation, recipes |
| microvm.nix | /p/gh/microvm.nix | microvm.nix/llm-wiki/ | concepts, hypervisors, options, host, recipes, conventions |

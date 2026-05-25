---
id: guide-ingest-external
title: "Ingest External Library"
kind: descriptive
status: accepted
scope: global
created: 2026-05-24
updated: 2026-05-24
tags: [ingest, external-library, llm-wiki, query]
ownership: shared
ownership_reason: procedure definition — human reviews, agent executes
---

## Purpose

Create a query-optimized llm-wiki for a third-party library we use
frequently. The wiki lives on an `llm-wiki` branch in our fork,
never merges to main, and provides fast context loading when coding
against that library.

## When to Use

- Library is a core dependency (used across multiple projects)
- We'll query it repeatedly during coding sessions
- The library has enough API surface that reading raw docs is slow

## Procedure: `ingest-external <repo-path>`

### Prerequisites

1. Library is forked into our origin (e.g., `tigidar/<name>`)
2. Upstream remote is configured: `git remote add upstream <upstream-url>`
3. Local clone exists at `<repo-path>`

### Steps

```
1. cd <repo-path>
2. git checkout -b llm-wiki
3. mkdir -p llm-wiki/{meta,concepts,effects,data,modules,patterns,conventions,recipes}
   (adjust sections to match the library's domain — not all sections apply)

4. Read the library's key docs:
   - README.md (overview, API docs)
   - CONTRIBUTING.md (conventions, patterns)
   - AGENTS.md or similar (if exists)
   - Source files for API surface

5. Create control files:
   - llm-wiki/CLAUDE.md     (~25 lines, query dispatch)
   - llm-wiki/meta/schema.md (page formats for this wiki)
   - llm-wiki/index.md       (root catalog with quick lookup table)

6. Create section indexes:
   - Each section gets an index.md with a table of all pages

7. Create content pages:
   - One page per concept, API, module, pattern
   - Every page has YAML frontmatter with:
     id, title, category, layer, tags, source_files,
     source_commit, api_surface, related, see_also
   - Focus on what a developer NEEDS to use the API correctly

8. Register in main wiki:
   - Create sources/raw/code/<name>.md with type: external-lib
   - Point to repo, origin, upstream, wiki_branch, sections

9. Commit on the llm-wiki branch:
   - git add llm-wiki/
   - git commit -m "[llm-wiki] add query-optimized knowledge base for <name>"

10. Push to origin:
    - git push -u origin llm-wiki
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

See `llm-wiki/meta/schema.md` in the target repo for the full spec.
Key frontmatter fields:

```yaml
---
id: <lib>-<category>-<name>     # unique within this wiki
title: "Human Title"
category: concept | effect | data | module | pattern | convention | recipe
layer: foundation | core | integration | application
tags: [searchable, keywords]
source_files: [relative/path/to/source.scala]
source_commit: <short-hash>      # for staleness tracking
api_surface: [Type.method, ...]  # for grep-based discovery
related: [other-page-ids]
see_also: [pattern-ids]
---
```

## Procedure: `ingest-external refresh <name>`

Update an existing llm-wiki after rebasing on upstream.

```
1. Read sources/raw/code/<name>.md to find repo path and wiki_branch
2. cd <repo-path> && git checkout <wiki_branch>
3. Compare current HEAD commit to source_commit in pages
4. For pages where source_files have changed since source_commit:
   - Re-read the source files
   - Update the page content
   - Update source_commit to current HEAD
5. Check for new APIs/modules not yet covered:
   - Scan source directories for files not referenced by any page
   - Create pages for significant additions
6. Rebuild index pages from current frontmatter
7. Update sources/raw/code/<name>.md with new commit and last_observed
8. Commit: "[llm-wiki] refresh from upstream <short-hash>"
```

## Procedure: `ingest-external query <name> <question>`

Query an external library's wiki from the main wiki context.

```
1. Read sources/raw/code/<name>.md to find repo path and wiki_branch
2. cd <repo-path> && git checkout <wiki_branch>
3. Read llm-wiki/CLAUDE.md for query strategy
4. Follow the discovery chain in llm-wiki/index.md
5. Return to main wiki context with the answer
```

## Existing External Libraries

| Library | Repo | Branch | Sections |
|---------|------|--------|----------|
| Kyo | /p/gh/kyo | llm-wiki | concepts, effects, data, modules, patterns, conventions, recipes |

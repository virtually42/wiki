# Mill Build Tool Wiki

Query-optimized knowledge base for the Mill build tool.
Start by reading `llm-wiki/index.md` to find relevant pages.

## Operations

- **query** — Find information for a coding task using this wiki
- **ingest** — Update wiki from upstream source changes (after rebase)
- **refresh** — Re-read source and update a specific page

## Query Strategy

1. Read index.md -> identify relevant section (concepts, modules, configuration, patterns, recipes, cli)
2. Read section index.md -> find specific pages matching your need
3. Read matched pages -> use frontmatter `related` and `see_also` for adjacent knowledge
4. If page references source: verify against actual source file (pages can be stale)

## Staleness

Pages track `source_commit`. If HEAD has moved significantly past a page's
source_commit, treat claims as *likely true but verify before relying on*.

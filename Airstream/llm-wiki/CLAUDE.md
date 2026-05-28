# Airstream Library Wiki

Query-optimized knowledge base for the Airstream reactive streaming library.
Start by reading `index.md` to find relevant pages. Source repo: `/p/gh/Airstream`

## Operations

- **query** — Find information for a coding task using this wiki
- **ingest** — Update wiki from upstream source changes (after rebase)
- **refresh** — Re-read source and update a specific page

## Query Strategy

1. Read index.md → identify relevant page from quick lookup or section list
2. Read matched pages → use frontmatter `related` and `see_also` for adjacent knowledge
3. If page references source: verify against actual source file at `/p/gh/Airstream` (pages can be stale)

## Staleness

Pages track `source_commit`. If HEAD has moved significantly past a page's
source_commit, treat claims as *likely true but verify before relying on*.

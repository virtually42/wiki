# toml-scala Wiki

Query-optimized knowledge base for `toml-scala` (TOML parser/codec for
Scala 2.12, 2.13, 3 on JVM/JS/Native). Source repo: `/p/gh/toml-scala`.

Start by reading `index.md` to find relevant pages.

## Operations

- **query** — Find information for a coding task using this wiki
- **ingest** — Update wiki from upstream source changes (after rebase)
- **refresh** — Re-read source and update a specific page

## Query Strategy

1. Read `index.md` -> identify section (concepts, api, data, codecs,
   derivation, recipes)
2. Read the section `index.md` -> find specific pages matching your need
3. Read matched pages -> follow `related` and `see_also` for adjacent
   knowledge
4. If page references source: verify against actual source file at
   `/p/gh/toml-scala` (pages may be stale)

## Staleness

Pages track `source_commit`. If HEAD has moved significantly past a
page's `source_commit`, treat claims as *likely true but verify before
relying on*.

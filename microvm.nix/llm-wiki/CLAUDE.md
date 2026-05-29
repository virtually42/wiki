# microvm.nix Wiki

Query-optimized knowledge base for `microvm.nix` (Nix flake to build and
run NixOS as a MicroVM on eight hypervisors). Source repo: `/p/gh/microvm.nix`.

Start by reading `index.md` to find relevant pages.

## Operations

- **query** — Find information for a NixOS / MicroVM configuration task
- **ingest** — Update wiki from upstream source changes (after rebase)
- **refresh** — Re-read source and update a specific page

## Query Strategy

1. Read `index.md` -> identify section (concepts, hypervisors, options,
   host, recipes, conventions)
2. Read the section `index.md` -> find specific pages matching your need
3. Read matched pages -> follow `related` and `see_also` for adjacent
   knowledge
4. If page references source: verify against actual source file at
   `/p/gh/microvm.nix` (pages may be stale)

## Staleness

Pages track `source_commit`. If `/p/gh/microvm.nix` HEAD has moved
significantly past a page's `source_commit`, treat claims as *likely true
but verify before relying on*. The handbook at
`/p/gh/microvm.nix/doc/src/` is the authoritative human-facing source.

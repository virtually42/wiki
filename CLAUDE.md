# Wiki

All knowledge lives in the wiki. Start every operation by reading `index.md`
to find relevant pages. Use frontmatter glob to narrow scope.

## Processes

### Knowledge Operations
- **ingest** — Import a source (document or code) into the wiki
- **ingest-external** — Create an llm-wiki for an external library in this wiki
- **breakout** — Extract a micro-library from a monolithic source repo into its own `/p/hg/<name>` location and register it as a wiki project. Human provides the source path. See `tech/guides/breakout.md`.
- **query** — Answer a question using wiki knowledge, if answer not found, research using other sources, update wiki with new key insights according to @media/schema.md
- **lint** — Check wiki consistency, compliance, and drift
- **synthesize** — Generate cross-cutting analysis across projects or tech

### Code Operations
- **implement** — Execute a task using wiki context, update wiki with new key insights
- **test** — Run tests, capture results, update wiki with observations
- **run** — Execute the system, observe behavior, update wiki

### Wiki Maintenance
- **promote** — Elevate a local pattern to global based on evidence
- **edit** — Modify a wiki page (check ownership first)

## Ownership

Before writing any wiki page, check ownership in `meta/ownership.md`.
- **human**: read only, surface proposals in conversation
- **llm**: agent owns, may create/edit/delete
- **shared**: either party edits, agent flags changes for review

## Schema

Page formats, frontmatter specs, and naming conventions live in
`meta/schema.md`. Read it when creating or editing wiki pages.

## Commands

### update-all
Fetch and rebase all git repos in the monorepo at `/p/hg`.

```bash
bash tools/update-all.sh
```

## Policy

Compliance and coherence rules live in `POLICY.md`. Read it when
performing lint, synthesize, or promote operations.

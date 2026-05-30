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
- **conform** — Evidence-check projects against normative patterns using declared fingerprints; produce stance recommendations and draft ADRs in `projects/*/adr/drafts/`. Output: `meta/conformance.md`. See `tech/guides/conformance.md`.
- **synthesize** — Generate cross-cutting analysis across projects or tech

### Code Operations
- **implement** — Execute a task using wiki context, update wiki with new key insights
- **test** — Run tests, capture results, update wiki with observations
- **run** — Execute the system, observe behavior, update wiki

### Session
- **wip** — Save current work state for handoff to a clean session. Writes `projects/<name>/wip.md` for project-scoped work, or top-level `wip.md` for cross-cutting work. Overwrites prior contents — history belongs in `log.md`. Required sections: Goal, Status, Files Touched, Decisions, Blockers, Next Step, Resume Instructions. Frontmatter: `updated: YYYY-MM-DD`, `project: <name|null>`, `branch: <git-branch>`, `related: []` (tickets/plans/designs).

### Wiki Maintenance
- **promote** — Elevate a local pattern to global based on evidence
- **edit** — Modify a wiki page (check ownership first)

## Ownership

Before writing any wiki page, check ownership in `meta/ownership.md`.
- **human**: read only, surface proposals in conversation
- **llm**: agent owns, may create/edit/delete
- **shared**: either party edits, agent flags changes for review

### Human-owned edits — fix scripts

When proposed changes target human-owned files, decide which path applies:

- **Obvious** (multiple edits, structured insertions, repeated changes across files): write an idempotent script to `fix/` without asking, then surface the proposal text alongside it.
- **Uncertain** (single non-trivial edit, or unclear whether automation helps): offer to write a script and let the human decide.
- **Trivial** (one short edit): surface the proposal as text, no script.

Scripts in `fix/` must be idempotent — re-runs print `skip` for already-applied chunks. Prefer Python with stdlib only.

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

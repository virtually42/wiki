# Project Schema: <project-name>

Inherits from root `CLAUDE.md` and `tech/POLICY.md`. Defines project-specific structure and tags. May extend the root schema but **must not** weaken the compliance-frontmatter contract.

## Purpose

One paragraph: what this project is, what stage it is in, what the wiki is for.

## Layout (project-local)

```
projects/<name>/
├── CLAUDE.md           # this file
├── adr/                # architectural decision records
├── tickets/            # in-flight work units
│   ├── open/
│   └── closed/
├── interfaces.md       # external seams
├── risk.md             # supply-chain and technical risks
├── log.md              # append-only project log
├── syntheses/          # project-scoped cross-cutting analyses
└── index.md            # generated
```

## Tagging

Project-specific tag taxonomy. Cross-project search uses `relevant_to` and `compliance`, not tags, so tags can be domain-shaped here.

Example for the compositor project:
- `subsystem:` `input` | `rendering` | `ipc` | `wm` | `widget-runtime`
- `surface:` `wlroots` | `kyo` | `wasm` | `airstream`
- `phase:` `design` | `prototype` | `stable`

## ADR conventions

- Filename: `adr/NNNN-kebab-title.md` where NNNN is monotonic.
- Every ADR has the `compliance` block from `tech/POLICY.md`.
- Superseding an ADR: new ADR cites the old one in `supersedes:`. Lint marks the old one read-only.

## Ticket conventions

- Filename: `tickets/open/NNNN-kebab-title.md`. Move to `closed/` on completion; keep the number.
- Frontmatter: `status`, `created`, `closed`, `related_adr`, `related_synthesis`.
- Tickets may reference tech pages but do not require compliance declarations — only ADRs do.

## Log conventions

Append-only. Each entry:

```
## [YYYY-MM-DD] <verb> | <subject>

<one-paragraph context>

Refs: [[adr/NNNN-...]], [[sources/summaries/...]]
```

Verbs: `ingest`, `adr`, `ticket-open`, `ticket-close`, `synthesis`, `gap`, `drift`, `lint`.

## Syntheses

Project-scoped only. Cross-project syntheses live in `/syntheses/` at root. If a synthesis starts here and grows cross-cutting, the agent proposes promoting it; the human approves the move.

## Local overrides

Document any deviation from the root schema here, with rationale. Example:

> This project uses Scala Native, so JVM-specific tech pages are marked `ignores` in ADR-001 wholesale. Subsequent ADRs do not need to re-ignore them.

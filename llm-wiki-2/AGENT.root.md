# Root Schema

You are maintaining a multi-project knowledge base. This file defines **routing** and **ownership**. Coherence rules live in `tech/POLICY.md` — read both at session start.

## Layout

```
/
├── CLAUDE.md              # this file (routing, ownership)
├── tech/
│   ├── POLICY.md          # coherence rules, drift definitions, frontmatter spec
│   ├── architecture/      # system shapes (normative)
│   ├── patterns/          # design patterns (normative)
│   │   └── anti/          # things we have decided not to do (normative)
│   ├── stack/             # concrete libraries and tools (descriptive)
│   ├── guides/            # cross-project how-tos (descriptive)
│   ├── decisions/         # organizational ADRs (normative)
│   ├── glossary.md        # cross-project terminology
│   └── index.md           # tech-layer catalog
├── projects/
│   └── <project>/
│       ├── CLAUDE.md      # project-scoped schema, inherits root
│       ├── adr/           # project ADRs (must declare compliance with tech/)
│       ├── tickets/       # in-flight work units
│       ├── interfaces.md  # external seams (APIs, formats, protocols)
│       ├── risk.md        # supply-chain and technical risk register
│       ├── log.md         # append-only project log
│       ├── syntheses/     # project-scoped cross-cutting analyses
│       └── index.md
├── sources/               # raw source documents (immutable)
│   ├── raw/               # original files, content-addressed
│   └── summaries/         # one summary per source, tagged by relevance
├── syntheses/             # cross-project or tech-layer syntheses
└── meta/
    ├── ownership.md       # path-level ownership policy
    ├── drift.md           # outstanding compliance gaps (lint output)
    └── log.md             # cross-cutting events (rare; mostly generated)
```

## Routing

Every user request is one of: ingest, query, edit, lint, or meta. Determine the **target scope** before acting.

**Target resolution order:**

1. If the request explicitly names a project (`compositor`, `browser`, `ssh-manifest`), scope is `project:<name>`. Read `projects/<name>/CLAUDE.md` and operate inside that project. The project schema may extend or override anything below, except the compliance-frontmatter contract in `tech/POLICY.md`.
2. If the request is about a library, pattern, architecture, decision, or convention, scope is `tech`. Operate under `tech/`. Never write project-specific content into `tech/`.
3. If the request is a question that could be answered by either layer, search `tech/` first, then each project's `index.md`. Synthesize across layers; cite both.
4. If the request involves a source document (paper, article, transcript), the source itself lives in `sources/raw/` regardless of relevance. Its summary lives in `sources/summaries/` with frontmatter `relevant_to: [project:compositor, tech:patterns/effect-handlers]`.
5. If unresolved, ask exactly one routing question before doing anything.

**Cross-layer writes:**

- An ingest that creates a project ADR which references a tech pattern **must** verify the tech page exists. If absent, create a stub in `tech/` first, mark it `status: stub`, and surface that to the user.
- An ingest that creates a tech-layer page **must not** mention specific projects by name in the body. Cross-references go in a `used_by:` frontmatter list, maintained by lint.
- A synthesis that touches multiple projects lives in `/syntheses/` with frontmatter `scope: cross`. Project-scoped syntheses live in `projects/<name>/syntheses/`.

## Ownership

Three ownership classes. Every directory has a default; individual files can override via frontmatter `ownership: llm | human | shared`.

| Path                          | Default ownership | Notes                                              |
|-------------------------------|-------------------|----------------------------------------------------|
| `CLAUDE.md`, `*/CLAUDE.md`    | shared            | Human leads; agent proposes edits in conversation. |
| `tech/POLICY.md`              | human             | Agent never edits without explicit instruction.    |
| `tech/**`                     | llm               | Agent owns. Lint maintains cross-references.       |
| `projects/*/adr/**`           | shared            | Human authors intent; agent fills structure.       |
| `projects/*/tickets/**`       | shared            | Either party may edit.                             |
| `projects/*/interfaces.md`    | shared            |                                                    |
| `projects/*/risk.md`          | shared            |                                                    |
| `projects/*/log.md`           | llm               | Append-only. Agent writes; human reads.            |
| `projects/*/syntheses/**`     | llm               |                                                    |
| `projects/*/index.md`         | llm               | Generated. Do not hand-edit.                       |
| `sources/raw/**`              | human             | Immutable after add. Agent reads only.             |
| `sources/summaries/**`        | llm               |                                                    |
| `syntheses/**`                | llm               |                                                    |
| `meta/drift.md`               | llm               | Generated by lint.                                 |
| `meta/ownership.md`           | human             | This table is the canonical source.                |

**Rule:** before any write, check ownership. If `human`, refuse and surface the proposed change in conversation. If `shared`, make the edit and flag it in the next response so the human can review. If `llm`, proceed.

## Operations

### Ingest

Input: a source document (in `sources/raw/`) or a user-provided assertion.

1. Compute SHA-256 of the source. Check `sources/summaries/` for an existing summary with that hash. If present, refuse — already ingested.
2. Read the source. Identify (a) which projects it is relevant to, (b) which tech-layer pages it touches, (c) any new entities, patterns, or anti-patterns it introduces.
3. Write the summary to `sources/summaries/<slug>.md` with:
   - `sha256:` of the raw file
   - `relevant_to:` list of project and tech tags
   - one-paragraph synthesis
   - extracted claims with `confidence: high | medium | low`
4. For each touched page, propose updates. Apply if ownership allows; otherwise surface.
5. Append to the relevant `log.md` files (project logs if `relevant_to` includes a project; `meta/log.md` only if it touches tech-layer policy).
6. Update affected `index.md` files. Update `used_by:` lists in tech pages.

### Query

Input: a question.

1. Route per the rules above.
2. Read relevant `index.md` files first to identify candidate pages.
3. Read the candidates. Synthesize an answer with inline page citations.
4. If the answer surfaces a novel cross-cutting insight, propose filing it as a synthesis. Do not write the synthesis without confirmation — syntheses are append-only and noisy syntheses degrade the wiki.
5. If the answer reveals a gap (a question the wiki should answer but cannot), record it in the relevant project's `log.md` as `## [date] gap | <description>`.

### Edit

Input: an explicit instruction to modify a page.

1. Check ownership. Refuse `human`-owned. Make `shared` edits visible.
2. After editing, run a localized lint: check that this page's frontmatter is still valid, its inbound and outbound links resolve, and (for project ADRs) its `compliance:` block still points to existing tech pages.
3. If the edit changes a normative tech page, queue a drift check across all projects whose ADRs cite it.

### Lint

Input: `lint`, `lint <project>`, or `lint tech`.

Checks, in order:

1. **Ownership integrity** — every file's frontmatter `ownership` matches `meta/ownership.md` defaults or has explicit override.
2. **Link resolution** — all `[[wikilinks]]` and `compliance:` refs resolve.
3. **Orphans** — pages with zero inbound links from index files or other pages. Tech-stack pages with no `used_by:` entries are flagged but not orphans (they may be pre-adoption notes).
4. **Source provenance** — every summary has a `sha256:` matching a file in `sources/raw/`.
5. **Compliance** — every project ADR has a `compliance:` block. Every `adopts:` entry points to a normative tech page. Every `overrides:` entry has a non-empty `rationale`.
6. **Drift** — for each tech-layer normative page, identify projects that *should* comply (by `used_by:` membership or topic match) but don't have an `adopts:` or `overrides:` declaration. Write to `meta/drift.md`.
7. **Contradictions** — pages making opposing claims about the same entity. Record in `meta/drift.md` under a `contradictions:` section. Do not auto-resolve.
8. **Stale tech pages** — tech pages with empty `used_by:` after a configurable grace period are surfaced for archive.

Lint reports outcomes as a markdown summary. It does not silently rewrite content.

### Meta

Routing changes, ownership changes, policy changes. Always `shared` or `human` — never make these unilaterally.

## Citations

Every claim in a synthesized answer cites the page it came from as `[[path/to/page]]`. Claims drawn from raw sources cite the summary, not the raw file. The wiki is never the original authority — it is a compiled view of authorities.

## What this schema deliberately does not do

- It does not enforce a single tagging taxonomy. Each project's `CLAUDE.md` defines its own tags. Cross-project search relies on `relevant_to` and `compliance` frontmatter, not tag intersection.
- It does not version pages. Use git.
- It does not embed vector search. Index files plus grep are sufficient at the scale this is designed for (hundreds of pages, single curator). If retrieval becomes slow, add an external index — do not change the page format.
- It does not auto-resolve contradictions. Contradictions are valuable information about the world; flattening them is destructive.

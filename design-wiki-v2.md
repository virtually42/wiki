# Design: Wiki V2 — Dynamic Discovery & Self-Learning

```yaml
status: draft
created: 2026-05-17
authors: [human, claude]
scope: wiki architecture
```

---

## Problem Statement

The current wiki schema (llm-wiki-schema.md) places the entire routing, ownership, page type, and operation specification inside CLAUDE.md (~780 lines). This creates several problems:

1. **CLAUDE.md is too large.** It consumes significant agent context before the agent has even started working. The agent must internalize 780 lines of schema before reading a single wiki page.

2. **Context is loaded eagerly, not lazily.** The agent gets all schema knowledge upfront regardless of what the user actually asked. A "run the tests" request loads the same context as "synthesize error handling patterns across all projects."

3. **Source code is disconnected.** The wiki treats raw documents (articles, papers) as inputs but has no mechanism for treating source code as an equally valid input. Code observations, architecture descriptions, and pattern usage are wiki claims without mechanical links to the code they describe.

4. **The wiki is read-only during coding.** Operations like implement, test, and run are not defined. The wiki captures knowledge but doesn't participate in the build-observe-learn cycle that makes it self-improving.

5. **Per-project CLAUDE.md files duplicate and dilute.** Each project has its own CLAUDE.md that "inherits from root." In practice this creates multiple schema files the agent must reconcile, with unclear override semantics.

---

## Design Goals

1. **CLAUDE.md is a command list, nothing more.** ~50 lines. Repeatable processes the agent can execute. All knowledge lives in the wiki itself.

2. **Discovery is dynamic.** The agent navigates from prompt → root index.md → relevant indexes → frontmatter glob → assembled context. Context is loaded lazily based on what the task actually needs.

3. **Source code is a first-class input.** Code has the same epistemic status as articles and papers: it's an authoritative external source the wiki observes and describes. The wiki is not the code; it's a compiled view of code.

4. **The wiki self-improves through use.** Implement, test, and run operations produce observations that flow back into the wiki. Every coding session is an opportunity for the wiki to learn.

5. **Single CLAUDE.md at wiki root.** No per-project CLAUDE.md. Projects are discovered through the wiki's index structure.

---

## Architecture

### Layer Model

```
Layer 1: External Sources (immutable, human-curated or code)
    |
    |  sources/raw/docs/    — articles, papers, specs
    |  sources/raw/code/    — pointers/snapshots of project repos
    |
Layer 2: Wiki (LLM-maintained knowledge graph)
    |   root index.md → tech/, projects/, syntheses/
    |   normative: decisions, patterns, anti-patterns, standards
    |   descriptive: technology, guides, syntheses, design docs
    |   project: ADRs, tickets, plans, design docs, logs
    |
Layer 3: CLAUDE.md (command dispatch table)
    |   defines repeatable processes only
    |   ~50 lines
    |
Layer 4: Agent (Claude Code session)
    |   reads CLAUDE.md → discovers context → executes operation
    |   writes observations back to wiki
    |
Layer 5: Code (actual implementation in repos)
    |   the agent acts on code using wiki knowledge
    |   code changes feed back as wiki observations
```

### CLAUDE.md — The Command Interface

CLAUDE.md contains only the list of repeatable processes and a pointer to root index.md for discovery. It does not contain the schema, page types, ownership rules, or any knowledge content.

```markdown
# Wiki

All knowledge lives in the wiki. Start every operation by reading `index.md`
to find relevant pages. Use frontmatter glob to narrow scope.

## Processes

### Knowledge Operations
- **ingest** — Import a source (document or code) into the wiki
- **query** — Answer a question using wiki knowledge
- **lint** — Check wiki consistency, compliance, and drift
- **synthesize** — Generate cross-cutting analysis across projects or tech

### Code Operations
- **implement** — Execute a task using wiki context, update wiki with findings
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

## Policy

Compliance and coherence rules live in `POLICY.md`. Read it when
performing lint, synthesize, or promote operations.
```

That's it. ~30 lines. Everything else is discovered dynamically.

### Discovery Chain

When the agent receives a user prompt:

```
1. Read CLAUDE.md → understand available commands
2. Determine which process applies (or ask one routing question)
3. Read index.md → find relevant sections
4. If project-scoped → read projects/<name>/index.md
5. Glob frontmatter for kind/scope/applies_to matching the task
6. Read matched pages → assemble working context
7. Execute the operation
8. Write observations back to wiki (log entries, updated pages)
```

**Key property:** The agent reads only what the current task demands. A "lint project X" reads X's index and ADRs plus relevant normative tech pages. An "implement ticket COMP-042" reads the ticket, related ADRs, relevant patterns, and the project's architecture page — nothing else.

**Frontmatter as filter:** The agent uses `kind`, `scope`, `applies_to`, `status`, and `tags` to narrow results. Example: "find all normative pages that apply to Scala Native" translates to a glob for `kind: normative` + `applies_to.languages` containing `scala-native`.

### Source Code as Input

Source code lives in separate repositories. The wiki references code, not copies it.

```
sources/
  raw/
    docs/           — articles, papers, specs (immutable)
    code/           — lightweight pointers to repos
      compositor.md — repo URL, last-observed commit, entry points
      webapp.md     — repo URL, last-observed commit, entry points
  summaries/        — one summary per source (doc or code observation)
```

A code source pointer:
```yaml
---
id: source-compositor
type: code
repo: /p/compositor          # local path or git URL
last_observed: 2026-05-17
commit: abc123
entry_points:
  - src/main/scala/Main.scala
  - build.sc
---

## Structure Overview
## Key Modules
## Build System
```

When the agent ingests code, it reads the actual repository, produces summary pages describing architecture, patterns, and technology usage, and links those summaries back to file paths. The wiki page says "project X uses the Repository pattern in src/main/scala/persistence/UserRepo.scala" — a verifiable claim.

**Code observations vs. code specifications:**
- A wiki page *describing* code ("X uses pattern Y") is descriptive, derived from reading code
- A wiki page *prescribing* code ("X should use pattern Y") is normative, authored by humans/agents as decisions
- The gap between description and prescription is drift — lint can flag it

### Self-Learning Loop

The implement/test/run operations close the feedback loop:

```
         wiki knowledge
              |
              v
    +-------------------+
    |    implement       |  agent reads wiki, writes code
    +-------------------+
              |
              v
    +-------------------+
    |      test          |  agent runs tests, observes results
    +-------------------+
              |
              v
    +-------------------+
    |      run           |  agent runs system, observes behavior
    +-------------------+
              |
              v
    update wiki with observations
    (log entries, pattern discoveries,
     anti-pattern identification,
     ticket status, synthesis candidates)
              |
              v
         wiki knowledge (improved)
```

Each cycle:
- **implement** reads relevant wiki pages (patterns, decisions, architecture), writes code, then logs what was done and what was discovered
- **test** runs tests, captures which passed/failed, notes any patterns in failures, updates test-strategy pages if insights emerge
- **run** executes the system, observes behavior, flags discrepancies between wiki claims and actual behavior

Over time, the wiki accumulates observations grounded in real code and real test results, not just initial design intent.

---

## Page Types

### Existing (retained)

| Type | Kind | Location | Purpose |
|------|------|----------|---------|
| decision | normative | tech/decisions/ | Architectural/organizational choice with obligations |
| pattern | normative | tech/patterns/ | Reusable design/implementation pattern |
| anti-pattern | normative | tech/patterns/anti/ | Explicitly rejected pattern |
| technology | descriptive | tech/stack/ | Library, tool, or platform description |
| capability | descriptive | tech/capabilities/ | Architectural need independent of technology |
| guide | descriptive | tech/guides/ | Cross-project how-to |
| synthesis | descriptive | syntheses/ or projects/*/syntheses/ | Cross-cutting analysis |
| glossary-entry | descriptive | tech/glossary.md | Shared term definition |
| adr | normative | projects/*/adr/ | Project-scoped decision with compliance |
| ticket | project | projects/*/tickets/ | Work unit |
| log-entry | project | projects/*/log.md | Append-only session record |

### New

| Type | Kind | Location | Purpose |
|------|------|----------|---------|
| **design-doc** | descriptive | projects/*/designs/ | Forward-looking architectural exploration. Explores problem space, options, trade-offs. Precedes ADRs — multiple ADRs may emerge from one design doc. Status: draft → accepted → superseded. |
| **plan** | project | projects/*/plans/ | Work decomposition and sequencing. Decomposes into tickets. References design docs and normative pages. Status: draft → active → completed → abandoned. |

### Document Hierarchy

```
design doc  →  ADRs           →  tickets      →  log entries
(explores)    (decides)         (decomposes)    (records)

plan        →  tickets         →  log entries
(sequences)    (assigns work)    (records)
```

A **design doc** asks "how should we solve X?" It explores options, considers constraints, and proposes an approach. It is forward-looking and may be revised as understanding deepens.

An **ADR** records "we decided Y." It captures the decision, its rationale, alternatives considered, and compliance declarations. It is backward-looking — it records what was decided and why.

A **plan** says "to achieve Y, do these steps in this order." It references the design doc and ADRs, then decomposes into concrete tickets.

A **ticket** says "do this one thing." It is an atomic work unit the agent can implement in a single session.

### Design Doc Format

```yaml
---
id: compositor-design-input-pipeline
title: Input event processing pipeline design
kind: descriptive
status: draft | accepted | superseded
project: compositor
created: 2026-05-17
updated: 2026-05-17
related_adrs: []           # ADRs that emerged from this design
related_plans: []           # plans that implement this design
sources: []
---

## Problem
What problem does this design address?

## Constraints
What constraints bound the solution space?

## Options Explored
### Option A: ...
### Option B: ...

## Proposed Approach
Which option and why.

## Trade-offs
What we gain, what we give up.

## Open Questions
What we don't know yet.

## Decision Record
Link to ADRs once decisions are made.
```

### Plan Format

```yaml
---
id: compositor-plan-input-pipeline
title: Implement input event processing pipeline
kind: project
status: draft | active | completed | abandoned
project: compositor
created: 2026-05-17
updated: 2026-05-17
design_doc: projects/compositor/designs/input-pipeline.md
related_adrs:
  - projects/compositor/adr/0003-input-handling.md
tickets: []                 # generated ticket IDs
estimated_sessions: 3       # rough scope indicator
---

## Goal
One sentence: what this plan achieves.

## Prerequisites
What must be true before starting.

## Steps
1. Step one — ticket ref, dependency
2. Step two — ticket ref, dependency
3. ...

## Acceptance Criteria
How we know the plan is complete.

## Risks
What could go wrong.
```

---

## Changes from Current Schema

### Removed

| What | Why |
|------|-----|
| Per-project CLAUDE.md | Single root CLAUDE.md only. Projects discovered via index. |
| SHA-256 provenance hashes | File paths + timestamps + git history are sufficient. Agent cannot reliably compute hashes. |
| Full schema in CLAUDE.md | Schema knowledge lives in wiki pages. CLAUDE.md is commands only. |
| Project CLAUDE.md template | Replaced by project index.md structure. |

### Changed

| What | From | To |
|------|------|-----|
| CLAUDE.md size | ~780 lines (full schema) | ~30-50 lines (commands only) |
| Context loading | Eager (read entire schema at start) | Lazy (discover via index → glob → read) |
| Source types | Documents only | Documents and code |
| Operations | ingest, query, edit, lint, synthesize, promote, meta | + implement, test, run |
| Project entry point | projects/*/CLAUDE.md | projects/*/index.md |

### Added

| What | Purpose |
|------|---------|
| design-doc page type | Forward-looking architectural exploration |
| plan page type | Work decomposition and sequencing |
| sources/raw/code/ | Code repository pointers |
| implement operation | Apply wiki knowledge to produce code |
| test operation | Run tests, capture observations |
| run operation | Execute system, observe behavior |

### Retained (unchanged)

- Routing-first architecture (resolve scope before acting)
- Ownership model (human/llm/shared with per-path defaults)
- Compliance-by-declaration (adopts/exceptions/deviations/ignores)
- "Silence is not compliance" rule
- POLICY.md as human-owned coherence rules
- Normative/descriptive/stub page kinds
- Promotion flow (project → synthesis → tech pattern → tech decision)
- Anti-patterns as first-class normative artifacts
- Contradiction preservation
- Drift detection categories
- All existing page types and their formats

---

## Updated Directory Layout

```
wiki/
├── CLAUDE.md                    # command dispatch (~30 lines)
├── POLICY.md                    # coherence rules (human-owned)
├── index.md                     # root catalog — agent's entry point
├── tech/
│   ├── index.md                 # tech-layer catalog
│   ├── architecture/
│   ├── patterns/
│   │   └── anti/
│   ├── decisions/
│   ├── stack/
│   ├── capabilities/
│   ├── guides/
│   └── glossary.md
├── projects/
│   └── <project>/
│       ├── index.md             # project catalog — agent reads this
│       ├── adr/
│       ├── designs/             # NEW: design documents
│       ├── plans/               # NEW: plan documents
│       ├── tickets/
│       │   ├── open/
│       │   └── closed/
│       ├── architecture.md
│       ├── interfaces.md
│       ├── risk.md
│       ├── log.md
│       └── syntheses/
├── sources/
│   ├── raw/
│   │   ├── docs/                # articles, papers, specs
│   │   └── code/                # NEW: repo pointers
│   └── summaries/
├── syntheses/
├── meta/
│   ├── ownership.md
│   ├── drift.md
│   ├── registry.md
│   └── log.md
└── tools/
    ├── lint.sh
    ├── index-gen.sh
    └── link-check.sh
```

---

## Operation Specifications

### Implement

Input: a ticket ID, task description, or user instruction.

```
1. Identify the target project from the ticket or prompt
2. Read project index.md → find related ADRs, design docs, architecture
3. Glob tech/ for normative pages matching the project's stack
4. Read matched pages → assemble implementation context
5. Execute the implementation (write code, modify configs, etc.)
6. Log what was done:
   - Append to projects/<name>/log.md: what changed, what was discovered
   - Update ticket status if applicable
   - If a pattern was discovered, note it as a synthesis candidate
7. If implementation revealed a gap in wiki knowledge, log it
```

### Test

Input: `test <project>` or `test <specific-test>`.

```
1. Read project index.md → find test-related pages, architecture
2. Run the test suite (or specific tests)
3. Capture results:
   - Append to projects/<name>/log.md: pass/fail summary
   - If failures reveal a pattern, note synthesis candidate
   - If tests contradict wiki claims, flag as drift
4. Update ticket if test was for a specific ticket
```

### Run

Input: `run <project>` or `run <specific-component>`.

```
1. Read project index.md → find operational pages, architecture
2. Execute the system (or component)
3. Observe behavior:
   - Append to projects/<name>/log.md: observations
   - Flag discrepancies between wiki claims and actual behavior
   - Note performance characteristics, error patterns, etc.
4. If behavior reveals undocumented patterns, note synthesis candidate
```

---

## Where the Schema Lives

Currently the schema is in CLAUDE.md. In V2, the schema is distributed across wiki pages that the agent discovers as needed:

| Schema concern | Lives in |
|----------------|----------|
| Available commands | CLAUDE.md |
| Ownership rules | meta/ownership.md |
| Compliance/coherence | POLICY.md |
| Page type formats | Learned from existing pages + this design doc |
| Frontmatter spec | POLICY.md (required fields section) |
| Naming conventions | POLICY.md |
| Linking conventions | POLICY.md |

The agent doesn't need to read all of these for every operation. It reads what it needs:
- For **lint**: CLAUDE.md + POLICY.md + meta/ownership.md + target pages
- For **implement**: CLAUDE.md + project index + relevant tech pages + ticket
- For **query**: CLAUDE.md + index.md + discovered pages

---

## Open Questions

1. **Index.md generation.** Should index files be auto-generated from frontmatter, or human-curated? Auto-generation ensures they're current but may produce noisy indexes. Human curation keeps them focused but requires maintenance.

2. **Code pointer freshness.** How often should sources/raw/code/ pointers be updated? Every session? On explicit ingest? When the agent notices a commit has changed?

3. **Schema bootstrapping.** The agent needs to know page formats to create pages, but page formats are learned from existing pages. On a fresh wiki, where does the initial knowledge come from? Options: (a) seed pages in helpers/examples/, (b) a schema reference page in the wiki itself, (c) POLICY.md includes format specs.

4. **Log verbosity.** How much should implement/test/run log? Too little loses the self-learning benefit. Too much makes logs unreadable. Suggested rule: log decisions, discoveries, and surprises — not routine operations.

5. **Cross-repo mechanics.** When the wiki lives in /p/wiki and code lives in /p/compositor, /p/webapp, etc., how does the agent navigate between them? Does it need to be told the repo paths, or does it discover them from sources/raw/code/ pointers?

---

## Implementation Plan

Phase 1: Restructure CLAUDE.md and create root index.md
Phase 2: Add design-doc and plan page types with examples
Phase 3: Add sources/raw/code/ pointers for existing projects
Phase 4: Define implement/test/run operations in POLICY.md
Phase 5: Migrate existing content to new structure
Phase 6: Test the discovery chain end-to-end

---

## References

- [llm-wiki-for-software-factories.md](llm-wiki-for-software-factories.md) — comparative analysis
- [llm-wiki-schema.md](llm-wiki-schema.md) — current schema (V1)
- [helpers/POLICY.md](helpers/POLICY.md) — current coherence policy

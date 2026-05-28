# Wiki Page Schema

Authoritative reference for page formats, frontmatter specifications,
and naming/linking conventions.

**Ownership: human.** The agent never edits this file without explicit instruction.

---

## Page Type Catalog

| Type | Kind | Location | Purpose |
|------|------|----------|---------|
| decision | normative | tech/decisions/ | Architectural/organizational choice with obligations |
| pattern | normative | tech/patterns/ | Reusable design/implementation pattern |
| anti-pattern | normative | tech/patterns/anti/ | Explicitly rejected pattern |
| technology | descriptive | tech/stack/ | Library, tool, or platform description |
| capability | descriptive | tech/capabilities/ | Architectural need independent of technology |
| guide | descriptive | tech/guides/ | Cross-project how-to |
| synthesis | descriptive | syntheses/ or projects/\*/syntheses/ | Cross-cutting analysis |
| glossary-entry | descriptive | tech/glossary.md | Shared term definition (sections, not files) |
| adr | normative | projects/\*/adr/ | Project-scoped decision with compliance |
| design-doc | descriptive | projects/\*/designs/ | Forward-looking architectural exploration |
| plan | project | projects/\*/plans/ | Work decomposition and sequencing |
| ticket | project | projects/\*/tickets/ | Atomic work unit |
| log-entry | project | projects/\*/log.md | Append-only session record (not a standalone file) |
| code-source | source | sources/raw/code/ | Pointer to a code repository |
| external-lib | source | sources/raw/code/ | Pointer to an external library with llm-wiki in this repo |

---

## Page Type Formats

### decision

An organizational or architectural decision that projects must address.

```yaml
---
id: effects-kyo
title: Use Kyo for effect management
kind: normative
status: accepted
scope: global
created: 2026-03-01
updated: 2026-05-15
applies_to:
  languages: [scala]
  domains: [any]
  excludes: [shell-scripts, nix-modules]
used_by: []                        # maintained by lint
sources: []
supersedes: []
superseded_by: null
---

## Context
## Decision
## Consequences
## Alternatives Considered
## Code Examples
## Links
```

### pattern

A reusable design or implementation pattern.

```yaml
---
id: typed-error-boundaries
title: Typed error boundaries at module edges
kind: normative
status: accepted
scope: global
created: 2026-04-01
updated: 2026-05-15
applies_to:
  languages: [scala]
  domains: [any]
promoted_from: []                  # project syntheses that led here
sources: []
---

## Problem
## Solution
## Structure
## Code Example
## When To Use
## When Not To Use
## Related Patterns
```

### anti-pattern

A pattern explicitly rejected.

```yaml
---
id: homebrew-for-crypto
title: Do not use Homebrew for cryptographic tooling
kind: normative
status: rejected
created: 2026-01-15
applies_to:
  domains: [security, build-systems]
reasons: []
alternatives: []
---

## What This Is
## Why It Is Rejected
## What To Do Instead
## References
```

### technology

A concrete library, tool, or platform.

```yaml
---
id: kyo
title: Kyo Effect System
kind: descriptive
status: active
scope: global
created: 2026-03-01
updated: 2026-05-15
capabilities: [effects, concurrency, io, streaming]
used_by: []                        # maintained by lint
version_notes: ""
---

## Overview
## Capabilities Served
## When To Use
## When Not To Use
## Project Usage
## Operational Notes
## Upgrade Notes
## Links
```

### capability

An architectural capability independent of technology.

```yaml
---
id: persistence
title: Data Persistence
kind: descriptive
status: active
scope: global
created: 2026-05-15
implementations:
  - tech: postgresql
    projects: [webapp, api-server]
  - tech: sqlite
    projects: [cli-tool, local-app]
---

## What This Capability Is
## Requirements
## Implementations Across Projects
## Comparison
## Recommendations
```

### guide

A cross-project how-to.

```yaml
---
id: nix-dev-shell
title: Setting up a Nix dev shell for Scala projects
kind: descriptive
status: active
scope: global
created: 2026-05-15
applies_to:
  languages: [scala, scala-native]
---

## Prerequisites
## Steps
## Variations
## Troubleshooting
## Links
```

### synthesis

Cross-cutting analysis or derived insight.

```yaml
---
id: error-handling-patterns-2026q2
title: Error handling patterns across projects (2026-Q2)
kind: descriptive
status: active
scope: cross-project | project:<name>
confidence: medium
created: 2026-05-15
sources: []                        # pages and raw sources consulted
---

## Observation
## Evidence
## Analysis
## Recommendations
## Confidence Assessment
```

### adr

Architecture Decision Record for a specific project.

```yaml
---
id: compositor-adr-007
title: Effect system choice
kind: normative
status: accepted
project: compositor
created: 2026-05-15
compliance:
  adopts: [tech/decisions/effects-kyo.md]
  exceptions: []
  deviations: []
  ignores: []
supersedes: []
---

## Context
## Decision
## Consequences
## Alternatives Considered
## Links
```

### design-doc

Forward-looking architectural exploration. Precedes ADRs — multiple ADRs
may emerge from one design doc.

```yaml
---
id: compositor-design-input-pipeline
title: Input event processing pipeline design
kind: descriptive
status: draft | accepted | superseded
project: compositor
created: 2026-05-17
updated: 2026-05-17
related_adrs: []                   # ADRs that emerged from this design
related_plans: []                  # plans that implement this design
sources: []
---

## Problem
## Constraints
## Options Explored
### Option A: ...
### Option B: ...
## Proposed Approach
## Trade-offs
## Open Questions
## Decision Record
```

### plan

Work decomposition and sequencing. Decomposes into tickets. References
design docs and normative pages.

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
tickets: []                        # generated ticket IDs
estimated_sessions: 3              # rough scope indicator
---

## Goal
## Prerequisites
## Steps
## Acceptance Criteria
## Risks
```

### ticket

An atomic work unit.

```yaml
---
id: COMP-042
title: Implement input event debouncing
status: open | in-progress | blocked | done | cancelled
project: compositor
created: 2026-05-15
closed: null
related_adr: []
related_synthesis: []
priority: high | medium | low
---

## Goal
## Acceptance Criteria
## Notes
## Implementation Log
```

### log-entry

Appended to `projects/<name>/log.md`. Not a standalone file.

```
## [2026-05-15] ingest | New source on Wayland protocol extensions

Ingested raw/compositor/wayland-ext-notes.md. Created summary. Updated
architecture.md with new protocol extension handling section.

Refs: [[sources/summaries/wayland-ext-notes]], [[projects/compositor/architecture]]
```

Log verbs: `ingest`, `adr`, `ticket-open`, `ticket-close`, `synthesis`,
`gap`, `drift`, `lint`, `session`, `promote`, `implement`, `test`, `run`.

### code-source

A lightweight pointer to a code repository in `sources/raw/code/`.

```yaml
---
id: source-compositor
type: code
repo: /p/compositor                # local path or git URL
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

### external-lib

An external library with a query-optimized llm-wiki in this repo.
The wiki lives at `<name>/llm-wiki/` in the wiki repo. Source code
lives at `/p/gh/<name>`. Pages reference source files with absolute paths.

```yaml
---
id: source-kyo
type: external-lib
repo: /p/gh/kyo                    # source code location
origin: git@tigidar:tigidar/kyo.git
upstream: git@tigidar:getkyo/kyo.git
wiki_path: kyo/llm-wiki/           # wiki location in this repo
last_observed: 2026-05-24
commit: 9bab8d00
wiki_sections:                     # what the llm-wiki covers
  - concepts
  - effects
  - data
  - modules
  - patterns
  - conventions
  - recipes
---

## Purpose
What we use this library for.

## Wiki Location
The wiki lives in this repo at `<name>/llm-wiki/`.
Source code lives at `/p/gh/<name>`.

## Refresh Procedure
1. Update source: `cd /p/gh/<name> && git fetch upstream && git rebase upstream/main`
2. Run `ingest-external refresh <name>` to update stale wiki pages
```

---

## Frontmatter Reference

### Required for all pages

```yaml
id: string              # stable identifier (kebab-case)
title: string           # human-readable title
kind: normative | descriptive | stub
status: draft | accepted | superseded | deprecated
```

### Required for scoped pages

```yaml
scope: global | project:<name> | cross-project
created: YYYY-MM-DD
updated: YYYY-MM-DD
```

### Optional common fields

```yaml
confidence: low | medium | high | reviewed
sources: []             # file paths to raw sources or other pages
ownership: human | llm | shared      # override only
ownership_reason: string             # mandatory with override
supersedes: []
superseded_by: null
tags: []
```

### Normative page fields

```yaml
applies_to:
  languages: []
  domains: []
  excludes: []
used_by: []             # maintained by lint
promoted_from: []
promotion_reason: string
promoted_at: YYYY-MM-DD
```

### Technology page fields

```yaml
capabilities: []        # which capabilities this tech serves
version: string
```

### Project ADR fields

```yaml
project: string
compliance:
  adopts: []
  exceptions: []
  deviations: []
  ignores: []
```

### Design doc fields

```yaml
project: string
related_adrs: []
related_plans: []
```

### Plan fields

```yaml
project: string
design_doc: string      # path to design doc
related_adrs: []
tickets: []             # generated ticket IDs
estimated_sessions: number
```

### Ticket fields

```yaml
project: string
priority: high | medium | low
closed: YYYY-MM-DD | null
related_adr: []
related_synthesis: []
```

### Code source fields

```yaml
type: code
repo: string            # local path or git URL
last_observed: YYYY-MM-DD
commit: string
entry_points: []
```

---

## Naming Conventions

- All lowercase, kebab-case: `typed-error-boundaries.md`
- ADRs: `NNNN-kebab-title.md` (project-local monotonic numbering)
- Tickets: `NNNN-kebab-title.md`
- Design docs: descriptive kebab-case names
- Plans: descriptive kebab-case names
- Syntheses: descriptive names, optionally date-prefixed for periodic analyses
- Log entries: date-prefixed within the log file
- Code sources: project name as filename

---

## Linking Conventions

- Use wiki links for internal references: `[[tech/decisions/effects-kyo]]`
- Use relative paths from wiki root
- Use normal markdown links for external URLs
- Every page should link to at least one other page
- When mentioning a concept or technology that has a page, link it

---

## Citations

Every claim cites its source as `[[path/to/page]]`. Claims from raw sources
cite the summary, not the raw file. The wiki is a compiled view of
authorities, never the original authority.

---

## Document Hierarchy

```
design doc  ->  ADRs           ->  tickets      ->  log entries
(explores)     (decides)          (decomposes)     (records)

plan        ->  tickets         ->  log entries
(sequences)    (assigns work)     (records)
```

---

## Normative Scope Declaration

Normative pages under `tech/` declare their scope:

```yaml
applies_to:
  languages: [scala, scala-native]   # which language ecosystems
  domains: [any]                      # which problem domains
  excludes: [shell-scripts]           # explicit exclusions
```

A project is in-scope when its tech stack overlaps with any declared
language or domain. In-scope projects must adopt, except, deviate from,
or ignore the page in an ADR.

---

## Promotion Metadata

When a project pattern is promoted to a tech-layer page:

```yaml
promoted_from:
  - projects/compositor/syntheses/error-boundaries.md
  - projects/webapp/adr/003-typed-errors.md
promotion_reason: Consistent successful use across projects
promoted_at: 2026-05-15
```

Demotion: set `status: deprecated` and `superseded_by:`.

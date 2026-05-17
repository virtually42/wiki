# LLM Wiki Schemas and README

This document contains a complete starter schema for a federated LLM wiki: a root workspace wiki coordinating multiple project wikis, shared governance, technology coherence, standards, provenance, and cross-project synthesis.

It is written as if these files live in a repository.

---

# `README.md`

```md
# Federated LLM Wiki

This repository defines a federated LLM wiki system for coordinating multiple software projects, technologies, architecture decisions, standards, and operational knowledge.

The main idea is:

```text
raw sources + schemas + prompts + model runs -> maintained markdown knowledge graph
```

The wiki is split into two levels:

```text
root wiki
  Shared governance, technology catalog, standards, patterns, portfolio views, provenance, and cross-project synthesis.

project wikis
  Local project knowledge: ADRs, tickets, logs, summaries, architecture, interfaces, operations, tests, and implementation notes.
```

The root wiki should not duplicate every project detail. It should coordinate projects, promote reusable patterns, enforce governance, and track coherence across the workspace.

## Goals

- Maintain durable project knowledge in Markdown.
- Keep raw sources immutable.
- Track provenance for generated pages and important claims.
- Coordinate multiple projects through shared standards and governance.
- Keep technology, architecture, and design decisions coherent across projects.
- Allow different projects to use different technologies when appropriate.
- Make deviations from standards explicit and reviewable.
- Promote useful local project patterns into global standards.

## Non-goals

- The root wiki is not a replacement for source code.
- The project wiki is not a replacement for issue trackers, Git history, or CI logs.
- The LLM should not silently mutate raw sources.
- The LLM should not invent facts without source grounding.
- The wiki should not force every project into the same technology stack.

## Repository layout

```text
workspace/
  raw/
    global/
    projects/
      project-a/
      project-b/

  schema/
    README.md
    root-schema.md
    project-schema.md
    page-types.md
    frontmatter.md
    governance-schema.md
    provenance-schema.md
    lint-rules.md
    promotion-flow.md

  prompts/
    ingest.md
    query.md
    lint.md
    synthesize.md
    refactor.md
    review.md

  wiki/
    root/
      portfolio/
      governance/
        standards/
        choices/
        exceptions/
        deviations/
        reviews/
      architecture/
      patterns/
      technology/
      capabilities/
      decisions/
      contracts/
      operations/
      security/
      provenance/
      synthesis/
      glossary/

    projects/
      project-a/
        adr/
        tickets/
        log/
        summaries/
        synthesis/
        architecture/
        implementation/
        interfaces/
        operations/
        security/
        tests/
        dependencies/
        governance/
          choices/
          exceptions/
          deviations/

      project-b/
        ...

  runs/
    ingest/
    query/
    lint/
    synthesis/
    review/
```

## Core principles

### 1. Raw sources are immutable

The LLM may read files under `raw/`, but must not edit them.

Raw sources include:

- project notes
- meeting notes
- source excerpts
- tickets
- transcripts
- architectural sketches
- issue exports
- decision documents
- command logs
- external documents copied into the repository

### 2. The wiki is derived knowledge

Files under `wiki/` are maintained knowledge artifacts generated or updated by the LLM, reviewed by humans, and versioned in Git.

### 3. Provenance is mandatory

Every generated page must say what it was generated from.

At minimum:

```yaml
generated_from:
  - path: raw/projects/project-a/notes/foo.md
    sha256: "..."
generated_by:
  model: "..."
  prompt: prompts/ingest.md
  schema: schema/project-schema.md
generated_at: 2026-05-15T12:00:00Z
confidence: medium
```

### 4. Standards define compliance

A project is only non-compliant when it violates an explicit standard, rule, invariant, or policy.

Using SQLite instead of PostgreSQL is not automatically a deviation. It is usually a normal technology choice.

### 5. Choices, exceptions, and deviations are separate

```text
choice
  A normal fit-for-purpose selection.

exception
  An accepted departure from a preferred pattern.

deviation
  A violation of an explicit standard, policy, or compliance rule.
```

### 6. Local learning can become global standards

Project-specific patterns may be promoted upward:

```text
project experience
  -> project synthesis
  -> root synthesis
  -> root pattern
  -> root standard
```

## Typical workflows

### Ingest

Read raw material and update wiki pages.

```text
raw/projects/project-a/notes/new-design.md
  -> wiki/projects/project-a/summaries/new-design.md
  -> wiki/projects/project-a/architecture/module-map.md
  -> wiki/projects/project-a/adr/ADR-0004-foo.md
```

### Query

Answer a question using the wiki first, then raw sources if needed. Cite provenance.

### Lint

Check for:

- missing provenance
- broken wiki links
- stale pages
- orphaned concepts
- claims without sources
- standards without compliance criteria
- deviations without mitigation
- choices incorrectly marked as deviations

### Synthesize

Create higher-level knowledge across pages or projects.

Examples:

- repeated patterns across projects
- technology drift
- recurring bugs
- common architecture boundaries
- inconsistent terminology
- candidates for promotion to standards

### Review

Periodically inspect governance, standards, deviations, and exceptions.

## Root wiki responsibilities

The root wiki manages cross-project coherence:

- project portfolio
- global standards
- technology catalog
- architecture principles
- design patterns
- capabilities
- contracts
- operations
- security
- provenance
- cross-project synthesis
- glossary

## Project wiki responsibilities

Each project wiki manages local knowledge:

- ADRs
- tickets
- implementation logs
- summaries
- synthesis
- local architecture
- implementation notes
- interfaces
- operations
- security
- tests
- dependencies
- local choices, exceptions, and deviations

## Governance model

Governance lives under:

```text
wiki/root/governance/
  standards/
  choices/
  exceptions/
  deviations/
  reviews/
```

Project-local governance lives under:

```text
wiki/projects/<project>/governance/
  choices/
  exceptions/
  deviations/
```

The root governance folder defines what compliance means. Project-local governance explains how a project applies, bends, or violates those standards.

## Technology coherence model

Projects may use different technologies. Coherence does not mean sameness.

A technology is coherent when:

- it is documented
- it satisfies the relevant capability
- it complies with applicable standards
- its tradeoffs are explicit
- it has a maintenance story
- it does not violate security or operational constraints

## Recommended page lifecycle

```text
draft
  Page created but not reviewed.

active
  Current accepted knowledge.

superseded
  Replaced by newer page or decision.

deprecated
  Still true historically but should not guide new work.

archived
  Kept only for historical reference.
```

## Naming conventions

Use lowercase kebab-case filenames.

Examples:

```text
error-handling.md
project-a-persistence-sqlite.md
ADR-0001-use-nix-dev-shell.md
2026-05-architecture-review.md
```

Use stable identifiers for decisions:

```text
ADR-0001
STD-0001
PAT-0001
DEV-0001
EXC-0001
CHO-0001
```

## Link conventions

Use Obsidian-style wiki links for internal references:

```md
[[governance/standards/error-handling]]
[[technology/catalog/sqlite]]
[[projects/project-a/adr/ADR-0004-use-sqlite]]
```

Use normal Markdown links for external URLs.

## Human review

LLM-generated pages can be useful without being authoritative.

A page becomes authoritative when:

- provenance is present
- sources are sufficient
- confidence is high enough
- a human has reviewed it, or the project explicitly accepts LLM-maintained knowledge as sufficient for that page type

## Minimal first implementation

Start with:

```text
schema/
  root-schema.md
  project-schema.md
  page-types.md
  governance-schema.md
  provenance-schema.md

wiki/root/
  portfolio/projects.md
  governance/standards/provenance.md
  governance/standards/project-structure.md
  technology/catalog.md
  synthesis/current-state.md

wiki/projects/<project>/
  summaries/
  adr/
  log/
  architecture/overview.md
```

Then add stricter linting and richer governance later.
```

---

# `schema/root-schema.md`

```md
# Root Wiki Schema

The root wiki coordinates all projects in the workspace.

It contains shared standards, patterns, technology knowledge, governance, provenance, and cross-project synthesis.

## Location

```text
wiki/root/
```

## Root folders

```text
wiki/root/
  portfolio/
  governance/
  architecture/
  patterns/
  technology/
  capabilities/
  decisions/
  contracts/
  operations/
  security/
  provenance/
  synthesis/
  glossary/
```

## Folder responsibilities

### `portfolio/`

Tracks the projects in the workspace.

Typical pages:

```text
projects.md
project-map.md
project-status.md
project-dependencies.md
project-roadmap.md
```

Answers:

- What projects exist?
- What state are they in?
- Which projects depend on each other?
- Which projects use which technologies?
- Which projects share capabilities?

### `governance/`

Defines standards, choices, exceptions, deviations, and reviews.

```text
governance/
  standards/
  choices/
  exceptions/
  deviations/
  reviews/
```

See `schema/governance-schema.md`.

### `architecture/`

Describes shared architecture principles and cross-project architecture views.

Typical pages:

```text
principles.md
module-boundaries.md
data-flow.md
service-boundaries.md
functional-core-imperative-shell.md
```

### `patterns/`

Reusable design and implementation patterns.

Typical pages:

```text
typed-error-boundaries.md
capability-oriented-modules.md
configuration-as-data.md
explicit-effects-at-boundaries.md
```

Patterns may start as local project discoveries and later be promoted to root-level patterns.

### `technology/`

Catalogs technologies and their approved use.

Recommended structure:

```text
technology/
  catalog.md
  catalog/
    scala.md
    nix.md
    sqlite.md
    postgresql.md
    tapir.md
    kyo.md
    vite.md
```

A technology page should describe:

- status
- use cases
- capabilities served
- projects using it
- risks
- operational notes
- upgrade notes
- alternatives

### `capabilities/`

Describes architectural capabilities independently of specific technologies.

Examples:

```text
authentication.md
persistence.md
html-rendering.md
background-jobs.md
observability.md
deployment.md
configuration.md
```

A capability page should compare how different projects satisfy the same need.

### `decisions/`

Global ADRs and workspace-level decisions.

Examples:

```text
ADR-0001-use-markdown-wiki.md
ADR-0002-use-nix-for-dev-environments.md
ADR-0003-require-provenance.md
```

Project ADRs should link to global ADRs where relevant.

### `contracts/`

Shared interface, protocol, API, schema, and file format conventions.

Examples:

```text
http-api-conventions.md
cli-conventions.md
json-formats.md
database-boundaries.md
event-formats.md
```

### `operations/`

Shared operational knowledge.

Examples:

```text
deployment.md
backups.md
secrets.md
monitoring.md
incident-response.md
local-development.md
```

### `security/`

Shared security knowledge, trust boundaries, threat models, and supply-chain rules.

Examples:

```text
threat-modeling.md
secrets.md
key-management.md
supply-chain.md
reproducible-builds.md
trust-boundaries.md
```

### `provenance/`

Tracks source registry, generated pages, model runs, and stale pages.

Examples:

```text
source-registry.md
model-runs.md
generated-pages.md
stale-pages.md
claim-audit.md
```

See `schema/provenance-schema.md`.

### `synthesis/`

Cross-project analysis and derived insights.

Examples:

```text
current-architecture.md
technology-drift.md
repeated-problems.md
common-patterns.md
migration-candidates.md
risk-overview.md
```

### `glossary/`

Shared vocabulary.

Examples:

```text
project.md
capability.md
service.md
module.md
adapter.md
domain-model.md
standard.md
choice.md
exception.md
deviation.md
```

## Root page requirements

Every root page must include frontmatter.

Minimum:

```yaml
---
type: concept
scope: global
status: draft
owner: null
created_at: 2026-05-15
updated_at: 2026-05-15
confidence: medium
generated_from: []
---
```

## Root-level authority

Root pages may be authoritative when they define:

- standards
- governance rules
- accepted patterns
- global architecture principles
- technology status
- security requirements
- provenance requirements

Root pages should not invent local project details. They should link to project pages instead.

## Cross-project linking

Root pages may link into project wikis:

```md
Used by:
- [[projects/project-a/dependencies/technology-stack]]
- [[projects/project-b/architecture/overview]]
```

Project pages may link back to root standards:

```md
Complies with:
- [[root/governance/standards/provenance]]
- [[root/governance/standards/testing]]
```

## Promotion from project to root

A local project pattern may be promoted when:

- it appears in more than one project
- it solves a recurring problem
- it aligns with root architecture principles
- it has enough provenance
- it has been reviewed

Promotion path:

```text
project log
  -> project synthesis
  -> root synthesis
  -> root pattern
  -> root standard, if normative
```
```

---

# `schema/project-schema.md`

```md
# Project Wiki Schema

Each project has a local wiki under:

```text
wiki/projects/<project>/
```

The project wiki captures local project knowledge while following root-level governance and standards.

## Project folder structure

```text
wiki/projects/<project>/
  README.md
  adr/
  tickets/
  log/
  summaries/
  synthesis/
  architecture/
  implementation/
  interfaces/
  operations/
  security/
  tests/
  dependencies/
  governance/
    choices/
    exceptions/
    deviations/
```

## Folder responsibilities

### `README.md`

Project overview.

Must answer:

- What is this project?
- What problem does it solve?
- What is its current status?
- What are the main technologies?
- Where are the most important pages?

### `adr/`

Architecture Decision Records.

Use for significant decisions that should survive beyond a ticket or implementation log.

Examples:

```text
ADR-0001-use-sqlite-for-local-persistence.md
ADR-0002-use-scala-js-for-ui.md
ADR-0003-use-nix-flake-for-dev-env.md
```

### `tickets/`

Ticket summaries and issue-tracker mirrors.

Tickets should not replace the real issue tracker unless this wiki is the issue tracker.

Useful for:

- ticket summaries
- status synthesis
- linking implementation logs to decisions
- cross-ticket patterns

### `log/`

Chronological project log.

Useful for:

- implementation notes
- debugging sessions
- command outputs
- investigation notes
- short-lived context that may later be summarized

Recommended naming:

```text
2026-05-15-debug-database-migration.md
2026-05-16-add-auth-boundary.md
```

### `summaries/`

Generated summaries of raw material, logs, transcripts, or tickets.

Summaries should be source-grounded and should include provenance.

### `synthesis/`

Higher-level project insight.

Examples:

```text
current-state.md
open-risks.md
architecture-summary.md
recurring-problems.md
candidate-root-patterns.md
```

### `architecture/`

Local project architecture.

Examples:

```text
overview.md
module-map.md
boundaries.md
data-flow.md
invariants.md
```

### `implementation/`

Important implementation details.

Examples:

```text
important-files.md
core-types.md
algorithms.md
invariants.md
state-management.md
```

### `interfaces/`

Project-local interfaces and contracts.

Examples:

```text
cli.md
http-api.md
database.md
events.md
file-formats.md
```

### `operations/`

How to run, build, deploy, recover, and operate this project.

Examples:

```text
dev-env.md
build.md
deploy.md
backup.md
recovery.md
runbook.md
```

### `security/`

Project-local security knowledge.

Examples:

```text
threat-model.md
secrets.md
supply-chain.md
trust-boundaries.md
```

### `tests/`

Testing strategy and important test cases.

Examples:

```text
strategy.md
important-test-cases.md
known-gaps.md
property-tests.md
manual-tests.md
```

### `dependencies/`

Technology stack and external dependencies.

Examples:

```text
technology-stack.md
external-services.md
upgrade-notes.md
licenses.md
```

### `governance/choices/`

Normal local choices.

Example:

```text
persistence-sqlite.md
frontend-scalajs-airstream.md
```

### `governance/exceptions/`

Accepted exceptions to preferred root patterns.

Example:

```text
local-mutable-cache.md
non-standard-directory-layout.md
```

### `governance/deviations/`

Violations of explicit standards or compliance rules.

Example:

```text
missing-provenance-on-generated-pages.md
no-versioned-database-migrations.md
```

## Project page requirements

Every project page must include frontmatter.

Minimum:

```yaml
---
type: project-summary
project: project-a
scope: project
status: draft
created_at: 2026-05-15
updated_at: 2026-05-15
confidence: medium
generated_from: []
---
```

## Project README template

```md
---
type: project
project: project-a
scope: project
status: active
created_at: 2026-05-15
updated_at: 2026-05-15
confidence: high
generated_from: []
---

# Project A

## Purpose

## Status

## Main capabilities

## Technology stack

## Important links

- [[architecture/overview]]
- [[dependencies/technology-stack]]
- [[synthesis/current-state]]
- [[governance/choices/persistence-sqlite]]

## Root standards followed

- [[root/governance/standards/provenance]]
- [[root/governance/standards/project-structure]]

## Open risks

## Recent changes
```

## Local knowledge must link to root governance

Technology choices should link to relevant root standards and technology catalog entries.

Example:

```md
Selected technology:
- [[root/technology/catalog/sqlite]]

Complies with:
- [[root/governance/standards/persistence]]
- [[root/governance/standards/backups]]
```

## Project-local standards

A project may define local standards, but they must not contradict root standards unless documented as an exception or deviation.

Recommended location:

```text
wiki/projects/<project>/governance/standards/
```

Only add this folder when needed. Prefer root standards when possible.
```

---

# `schema/page-types.md`

```md
# Page Types

Every wiki page must declare a `type` in frontmatter.

This file defines accepted page types.

## Core page types

```text
project
source-summary
concept
technology
pattern
standard
adr
ticket
log-entry
synthesis
choice
exception
deviation
review
runbook
contract
threat-model
glossary-entry
capability
architecture-view
implementation-note
test-strategy
dependency-summary
provenance-record
model-run
```

## `project`

Represents one project in the workspace.

Required fields:

```yaml
type: project
project: project-a
scope: project
status: active
```

## `source-summary`

Summary of one or more raw sources.

Required fields:

```yaml
type: source-summary
generated_from:
  - path: raw/...
    sha256: "..."
```

Rules:

- Must not add unsupported claims.
- Must link to the raw source.
- Must include confidence.

## `concept`

Explains a concept used across the wiki.

Examples:

- functional core, imperative shell
- capability
- bounded context
- provenance

Required fields:

```yaml
type: concept
scope: global | project
```

## `technology`

Describes a technology.

Required fields:

```yaml
type: technology
technology: sqlite
status: preferred | allowed | experimental | legacy | forbidden
capabilities:
  - persistence
used_by: []
```

Technology status meanings:

```text
preferred
  Default choice for a use case.

allowed
  Acceptable when it fits.

experimental
  May be used for learning, prototypes, or approved experiments.

legacy
  Existing use is tolerated, but avoid for new work.

forbidden
  Must not be used unless a deviation is explicitly approved.
```

## `pattern`

A reusable architectural or design pattern.

Required fields:

```yaml
type: pattern
status: draft | active | superseded | deprecated
scope: global | project
applies_to: []
```

Patterns may be promoted into standards.

## `standard`

A normative rule or convention.

Required fields:

```yaml
type: standard
id: STD-0001
status: active
scope: global | project
compliance_level: required | recommended | optional
applies_to: []
```

Rules:

- Must define compliance criteria.
- Must define what counts as a deviation.
- Should link to reviews.

## `adr`

Architecture Decision Record.

Required fields:

```yaml
type: adr
id: ADR-0001
project: project-a | null
status: proposed | accepted | superseded | rejected
```

Recommended sections:

```md
## Context
## Decision
## Consequences
## Alternatives considered
## Links
```

## `ticket`

Ticket or issue summary.

Required fields:

```yaml
type: ticket
project: project-a
external_id: null
status: open | in-progress | blocked | done | cancelled
```

## `log-entry`

Chronological implementation or investigation log.

Required fields:

```yaml
type: log-entry
project: project-a
date: 2026-05-15
```

Rules:

- Logs may be messy.
- Important stable knowledge should later be summarized or synthesized.

## `synthesis`

Higher-level derived insight.

Required fields:

```yaml
type: synthesis
scope: global | project
confidence: low | medium | high
```

Rules:

- Must cite source pages or raw sources.
- Must distinguish facts from interpretation.
- Should identify uncertainty.

## `choice`

Normal fit-for-purpose choice.

Example: SQLite for local persistence.

Required fields:

```yaml
type: choice
id: CHO-0001
project: project-a
capability: persistence
selected: sqlite
status: proposed | accepted | superseded
```

Rules:

- A choice is not a violation.
- It should explain tradeoffs.
- It should link to relevant standards.

## `exception`

Accepted departure from a preferred pattern.

Required fields:

```yaml
type: exception
id: EXC-0001
project: project-a
related_standard: null
related_pattern: root/patterns/...
status: active | expired | superseded
review_by: 2026-09-01
```

Rules:

- An exception bends a preference.
- It does not necessarily violate a required standard.
- It should have a review date.

## `deviation`

Violation of an explicit standard, policy, or compliance requirement.

Required fields:

```yaml
type: deviation
id: DEV-0001
project: project-a
violated_standard: root/governance/standards/...
severity: low | medium | high | critical
status: temporary | accepted-risk | resolved
mitigation: "..."
review_by: 2026-06-01
```

Rules:

- Must link to violated standard.
- Must explain reason.
- Must include mitigation.
- Must include owner or review responsibility when possible.

## `review`

Governance, architecture, security, or project review.

Required fields:

```yaml
type: review
scope: global | project
review_type: architecture | security | governance | operations | provenance
review_date: 2026-05-15
```

## `runbook`

Operational procedure.

Required fields:

```yaml
type: runbook
scope: global | project
status: active
```

Recommended sections:

```md
## Purpose
## Preconditions
## Steps
## Verification
## Rollback
## Risks
```

## `contract`

API, CLI, schema, protocol, or file format contract.

Required fields:

```yaml
type: contract
scope: global | project
contract_type: http-api | cli | json | event | database | file-format | protocol
status: active
```

## `threat-model`

Security threat model.

Required fields:

```yaml
type: threat-model
scope: global | project
status: draft | active
assets: []
trust_boundaries: []
```

## `glossary-entry`

Defines a shared term.

Required fields:

```yaml
type: glossary-entry
term: capability
status: active
```

Rules:

- Keep definitions stable.
- Link related concepts.
- Prefer one canonical term.

## `capability`

Describes an architectural capability independent of specific technology.

Required fields:

```yaml
type: capability
capability: persistence
status: active
implemented_by: []
```

## `architecture-view`

Architecture page for a project or the root wiki.

Required fields:

```yaml
type: architecture-view
scope: global | project
view: overview | module-map | boundaries | data-flow | invariants
```

## `implementation-note`

Important implementation details.

Required fields:

```yaml
type: implementation-note
project: project-a
status: active
```

## `test-strategy`

Testing approach or known gaps.

Required fields:

```yaml
type: test-strategy
project: project-a
status: active
```

## `dependency-summary`

Technology stack or dependency page.

Required fields:

```yaml
type: dependency-summary
project: project-a
status: active
```

## `provenance-record`

Tracks sources, generated pages, or claim origins.

Required fields:

```yaml
type: provenance-record
record_type: source | page | claim | run
```

## `model-run`

Records an LLM operation.

Required fields:

```yaml
type: model-run
run_id: 2026-05-15T120000Z-ingest-project-a
operation: ingest | query | lint | synthesize | refactor | review
model: "..."
prompt: prompts/ingest.md
schema: schema/project-schema.md
inputs: []
outputs: []
```
```

---

# `schema/frontmatter.md`

```md
# Frontmatter Schema

All wiki pages must begin with YAML frontmatter.

## Base frontmatter

```yaml
---
type: concept
scope: global
status: draft
created_at: 2026-05-15
updated_at: 2026-05-15
confidence: medium
generated_from: []
reviewed_by: null
reviewed_at: null
---
```

## Required fields for all pages

```yaml
type: string
scope: global | project
status: draft | active | superseded | deprecated | archived
created_at: YYYY-MM-DD
updated_at: YYYY-MM-DD
confidence: low | medium | high | human-reviewed
generated_from: list
```

## Optional common fields

```yaml
id: string
project: string | null
owner: string | null
review_by: YYYY-MM-DD | null
reviewed_by: string | null
reviewed_at: YYYY-MM-DD | null
tags: []
related: []
complies_with: []
supersedes: []
superseded_by: null
```

## Provenance fields

```yaml
generated_from:
  - path: raw/projects/project-a/notes/foo.md
    sha256: "..."
    role: primary-source

generated_by:
  model: "..."
  prompt: prompts/ingest.md
  schema: schema/project-schema.md
  run_id: 2026-05-15T120000Z-ingest-project-a

generated_at: 2026-05-15T12:00:00Z
```

## Status values

```text
draft
  Created but not yet trusted.

active
  Current accepted page.

superseded
  Replaced by newer page.

deprecated
  Historically useful but should not guide new work.

archived
  Kept only for historical reference.
```

## Confidence values

```text
low
  Weak or incomplete sources. Treat carefully.

medium
  Reasonable source support but may need review.

high
  Strong source support.

human-reviewed
  Reviewed and accepted by a human.
```

## Example: technology page

```yaml
---
type: technology
technology: sqlite
scope: global
status: active
technology_status: allowed
capabilities:
  - persistence
used_by:
  - project-a
alternatives:
  - postgresql
  - duckdb
created_at: 2026-05-15
updated_at: 2026-05-15
confidence: high
generated_from:
  - path: raw/global/technology/sqlite-notes.md
    sha256: "..."
generated_by:
  model: claude-3-7-sonnet
  prompt: prompts/ingest.md
  schema: schema/root-schema.md
  run_id: 2026-05-15T120000Z-ingest-root
---
```

## Example: choice page

```yaml
---
type: choice
id: CHO-0001
project: project-a
scope: project
capability: persistence
selected: sqlite
status: accepted
complies_with:
  - root/governance/standards/persistence
  - root/governance/standards/backups
alternatives_considered:
  - postgresql
  - embedded-json-files
created_at: 2026-05-15
updated_at: 2026-05-15
confidence: human-reviewed
generated_from:
  - path: raw/projects/project-a/notes/persistence-decision.md
    sha256: "..."
---
```

## Example: deviation page

```yaml
---
type: deviation
id: DEV-0001
project: project-a
scope: project
violated_standard: root/governance/standards/provenance
severity: medium
status: temporary
mitigation: add source hashes to generated pages
review_by: 2026-06-01
created_at: 2026-05-15
updated_at: 2026-05-15
confidence: high
generated_from:
  - path: runs/lint/2026-05-15-project-a.md
    sha256: "..."
---
```
```

---

# `schema/governance-schema.md`

```md
# Governance Schema

Governance defines how projects stay coherent without forcing every project to be identical.

Governance lives primarily under:

```text
wiki/root/governance/
```

Project-local governance lives under:

```text
wiki/projects/<project>/governance/
```

## Governance folders

```text
governance/
  standards/
  choices/
  exceptions/
  deviations/
  reviews/
```

## Conceptual model

```text
standards define rules
choices document valid local decisions
exceptions document accepted bending of preferences
deviations document broken requirements
reviews keep the whole thing honest
```

## Standards

Location:

```text
wiki/root/governance/standards/
```

A standard defines a rule, convention, invariant, or policy.

A standard should include:

```md
## Purpose
## Scope
## Rule
## Compliance criteria
## Examples
## Non-compliance
## Related choices
## Related exceptions
## Related deviations
## Review policy
```

### Standard frontmatter

```yaml
---
type: standard
id: STD-0001
scope: global
status: active
compliance_level: required
applies_to:
  - all-projects
created_at: 2026-05-15
updated_at: 2026-05-15
confidence: human-reviewed
generated_from: []
---
```

### Compliance levels

```text
required
  Must be followed. Violation creates a deviation.

recommended
  Should be followed. Departure may create an exception.

optional
  Guidance only. Departure does not require exception or deviation.
```

## Choices

Location:

```text
wiki/root/governance/choices/
wiki/projects/<project>/governance/choices/
```

A choice documents a normal fit-for-purpose selection.

Examples:

```text
Project A uses SQLite for local persistence.
Project B uses PostgreSQL for multi-user server persistence.
Project C uses Scala.js for browser UI.
```

A choice is not a deviation.

### Choice frontmatter

```yaml
---
type: choice
id: CHO-0001
project: project-a
scope: project
capability: persistence
selected: sqlite
status: accepted
complies_with:
  - root/governance/standards/persistence
alternatives_considered:
  - postgresql
created_at: 2026-05-15
updated_at: 2026-05-15
confidence: high
generated_from: []
---
```

### Choice template

```md
# Choice: Use SQLite for local persistence

## Context

## Selected option

## Capability served

## Why this fits

## Alternatives considered

## Tradeoffs

## Relevant standards

## Risks

## Review triggers
```

## Exceptions

Location:

```text
wiki/root/governance/exceptions/
wiki/projects/<project>/governance/exceptions/
```

An exception is an accepted departure from a preferred pattern or recommended standard.

It does not necessarily violate a required rule.

Examples:

```text
Project A uses a local mutable cache even though immutable state is preferred.
Project B uses a non-standard directory layout for compatibility with an external tool.
```

### Exception frontmatter

```yaml
---
type: exception
id: EXC-0001
project: project-a
scope: project
related_pattern: root/patterns/immutable-domain-state
related_standard: null
status: active
reason: external tool requires mutable cache
risk: low
review_by: 2026-09-01
created_at: 2026-05-15
updated_at: 2026-05-15
confidence: high
generated_from: []
---
```

### Exception template

```md
# Exception: Local mutable cache

## Context

## Preferred pattern

## Exception

## Reason

## Risk

## Mitigation

## Review date

## Related decisions
```

## Deviations

Location:

```text
wiki/root/governance/deviations/
wiki/projects/<project>/governance/deviations/
```

A deviation is a violation of an explicit standard, policy, invariant, or compliance rule.

Examples:

```text
Generated pages are missing provenance.
Production schema changes were made without migrations.
Secrets were committed to a repository.
```

### Deviation frontmatter

```yaml
---
type: deviation
id: DEV-0001
project: project-a
scope: project
violated_standard: root/governance/standards/provenance
severity: medium
status: temporary
reason: older generated pages predate provenance standard
mitigation: backfill generated_from and source hashes
review_by: 2026-06-01
created_at: 2026-05-15
updated_at: 2026-05-15
confidence: high
generated_from: []
---
```

### Deviation template

```md
# Deviation: Missing provenance on generated pages

## Violated standard

## What is broken

## Why it happened

## Severity

## Risk

## Mitigation

## Owner / responsible party

## Review date

## Resolution
```

## Reviews

Location:

```text
wiki/root/governance/reviews/
```

Reviews inspect standards, choices, exceptions, and deviations.

Examples:

```text
2026-05-governance-review.md
2026-05-security-review.md
2026-05-architecture-review.md
```

### Review frontmatter

```yaml
---
type: review
scope: global
review_type: governance
review_date: 2026-05-15
status: active
created_at: 2026-05-15
updated_at: 2026-05-15
confidence: human-reviewed
generated_from: []
---
```

### Review template

```md
# Governance Review: 2026-05

## Scope

## Standards reviewed

## Choices reviewed

## Exceptions reviewed

## Deviations reviewed

## New risks

## Resolved risks

## Required follow-up
```

## Classification rules

Use this decision tree:

```text
Does it violate an explicit required standard?
  yes -> deviation
  no  -> continue

Does it depart from a preferred or recommended pattern?
  yes -> exception
  no  -> continue

Is it a fit-for-purpose selected option?
  yes -> choice
  no  -> ordinary documentation
```

## Examples

### SQLite instead of PostgreSQL

Classification:

```text
choice
```

Reason:

```text
No standard says PostgreSQL is required. SQLite satisfies the persistence capability for this project.
```

### No provenance on generated wiki pages

Classification:

```text
deviation
```

Reason:

```text
Violates required provenance standard.
```

### Mutable cache in otherwise pure domain model

Classification:

```text
exception
```

Reason:

```text
Bends preferred architecture pattern, but may not violate a required standard.
```
```

---

# `schema/provenance-schema.md`

```md
# Provenance Schema

Provenance means traceability from wiki output back to its inputs.

Inputs are everything the LLM was allowed to use.

Examples:

```text
raw files
schema files
prompt files
model version
previous wiki pages
human instructions
run logs
```

Provenance lets us answer:

- Where did this claim come from?
- Which source supports this page?
- Which prompt generated it?
- Which model generated it?
- Has the source changed since generation?
- Is the page stale?

## Required provenance for generated pages

Every generated page must include:

```yaml
generated_from:
  - path: raw/projects/project-a/notes/foo.md
    sha256: "..."
    role: primary-source

generated_by:
  model: "..."
  prompt: prompts/ingest.md
  schema: schema/project-schema.md
  run_id: 2026-05-15T120000Z-ingest-project-a

generated_at: 2026-05-15T12:00:00Z
confidence: medium
```

## Source roles

```text
primary-source
  Direct source for the page.

supporting-source
  Background or supplementary source.

prior-wiki-page
  Existing wiki page used as input.

schema
  Schema that constrained the generation.

prompt
  Prompt used by the LLM.

human-instruction
  Direct human instruction.
```

## Source registry

Location:

```text
wiki/root/provenance/source-registry.md
```

The source registry indexes raw sources.

Template:

```md
# Source Registry

| Path | SHA-256 | Type | Project | Added | Description |
|---|---:|---|---|---|---|
| raw/projects/project-a/notes/foo.md | ... | note | project-a | 2026-05-15 | Persistence decision notes |
```

## Generated pages registry

Location:

```text
wiki/root/provenance/generated-pages.md
```

Template:

```md
# Generated Pages

| Page | Type | Generated at | Model | Run ID | Confidence | Sources |
|---|---|---|---|---|---|---|
| wiki/projects/project-a/summaries/foo.md | source-summary | 2026-05-15 | ... | ... | medium | raw/... |
```

## Model run records

Every LLM operation should produce a run record under:

```text
runs/<operation>/<run-id>.md
```

Example:

```text
runs/ingest/2026-05-15T120000Z-ingest-project-a.md
```

### Model run template

```md
---
type: model-run
run_id: 2026-05-15T120000Z-ingest-project-a
operation: ingest
model: claude-3-7-sonnet
prompt: prompts/ingest.md
schema: schema/project-schema.md
created_at: 2026-05-15T12:00:00Z
inputs:
  - raw/projects/project-a/notes/foo.md
outputs:
  - wiki/projects/project-a/summaries/foo.md
---

# Model Run: ingest project-a

## Operation

## Inputs

## Outputs

## Prompt

## Schema

## Notes

## Warnings
```

## Claim-level provenance

Important claims should be source-linked inline.

Example:

```md
SQLite was selected because the project is a single-user local application with no requirement for concurrent writers.

Claim provenance:
- raw/projects/project-a/notes/persistence-decision.md
- wiki/projects/project-a/governance/choices/persistence-sqlite.md
```

For highly important claims, use explicit claim blocks:

```md
> Claim: SQLite satisfies the persistence capability for Project A.
> Sources:
> - raw/projects/project-a/notes/persistence-decision.md
> Confidence: high
```

## Staleness detection

A page is stale when:

- one or more `generated_from` source hashes no longer match
- the page links to a superseded decision
- a standard it depends on changed
- a technology status changed
- a project status changed
- a review date has passed

Stale pages should be listed in:

```text
wiki/root/provenance/stale-pages.md
```

## Provenance lint rules

A page fails provenance lint if:

- `generated_from` is missing
- source path does not exist
- source hash is missing
- source hash does not match
- generated_by is missing for generated pages
- confidence is missing
- high-confidence claim lacks support
- generated page has no run record
```

---

# `schema/lint-rules.md`

```md
# Lint Rules

Linting keeps the wiki coherent, auditable, and useful.

Linting should run over:

```text
schema/
wiki/
runs/
```

Raw sources under `raw/` should not be modified by linting.

## Link lint

Fail when:

- internal wiki link points to missing page
- root page links to project page that does not exist
- project page links to root standard that does not exist
- page is orphaned without reason

Warn when:

- page has no inbound links
- page has too many unrelated links
- project pages duplicate root content

## Frontmatter lint

Fail when:

- page has no frontmatter
- `type` is missing
- `type` is not in `schema/page-types.md`
- `scope` is missing
- `status` is missing
- `created_at` or `updated_at` is missing
- `confidence` is missing

Warn when:

- `updated_at` is old
- `owner` is missing for standards, deviations, or runbooks
- `review_by` is missing for exceptions or deviations

## Provenance lint

Fail when:

- generated page has no `generated_from`
- listed source path does not exist
- listed source hash is missing
- listed source hash does not match
- `generated_by` is missing
- generated page has no corresponding model run

Warn when:

- confidence is high but source count is weak
- synthesis has no source links
- claim looks normative but does not link to a standard

## Governance lint

Fail when:

- deviation does not link to violated standard
- deviation has no severity
- deviation has no mitigation
- deviation has no review date
- standard has no compliance criteria
- required standard does not define non-compliance

Warn when:

- choice appears to be misclassified as deviation
- exception has no related pattern or standard
- standard has no examples
- project has many unresolved deviations

## Technology lint

Fail when:

- project technology stack references unknown technology
- technology page has no status
- forbidden technology is used without deviation

Warn when:

- experimental technology is used in active project without choice page
- technology has no owner or maintenance notes
- technology has no capability mapping

## Architecture lint

Warn when:

- project has no architecture overview
- project has no module map
- project has no boundary description
- project has no current-state synthesis

Fail only if root standard requires these pages.

## Security lint

Fail when:

- secrets are documented directly in wiki
- threat model is required but missing
- security deviation has no mitigation

Warn when:

- project uses external service without dependency summary
- project has no secrets documentation
- project has no supply-chain notes

## Operations lint

Warn when:

- active project has no build instructions
- active project has no runbook
- active project has no recovery notes
- deployment procedure has no rollback section

## Synthesis lint

Fail when:

- synthesis has no sources
- synthesis presents interpretation as fact without qualification

Warn when:

- synthesis is stale relative to updated source pages
- synthesis page is not linked from project README or root synthesis index

## Classification lint

The linter should flag possible misclassification.

Examples:

```text
SQLite instead of PostgreSQL
  likely choice, not deviation

Missing provenance
  likely deviation if provenance standard is required

Mutable cache despite immutable-state preference
  likely exception unless a required standard forbids it
```

## Review lint

Warn when:

- review date has passed
- active deviation has not been reviewed
- exception has no expiry or review trigger
- standards have not been reviewed within review interval
```

---

# `schema/promotion-flow.md`

```md
# Promotion Flow

Promotion is how local project knowledge becomes global knowledge.

The root wiki should learn from projects.

## Promotion path

```text
project log
  -> project summary
  -> project synthesis
  -> root synthesis
  -> root pattern
  -> root standard
```

Not every insight should become a standard.

## Promotion stages

### 1. Local observation

A project log records something useful.

```text
wiki/projects/project-a/log/2026-05-15-error-handling.md
```

### 2. Local synthesis

The project wiki extracts a stable pattern.

```text
wiki/projects/project-a/synthesis/error-handling-pattern.md
```

### 3. Cross-project synthesis

The root wiki notices the same pattern in multiple projects.

```text
wiki/root/synthesis/repeated-error-handling-patterns.md
```

### 4. Root pattern

The pattern becomes reusable guidance.

```text
wiki/root/patterns/typed-error-boundaries.md
```

### 5. Root standard

If the pattern should become normative, promote it to a standard.

```text
wiki/root/governance/standards/error-handling.md
```

## Promotion criteria

Promote to root pattern when:

- the pattern appears in multiple projects, or
- one project demonstrates a clearly reusable solution, and
- the pattern has enough provenance, and
- tradeoffs are understood.

Promote to root standard when:

- the organization wants consistency, and
- compliance can be checked, and
- deviations can be clearly defined, and
- the cost of inconsistency is high.

## Do not promote when

- the idea is project-specific
- there is not enough evidence
- the tradeoffs are unclear
- the pattern is still experimental
- enforcing it would reduce useful local flexibility

## Promotion frontmatter

Root patterns and standards should record promotion origin.

```yaml
promoted_from:
  - wiki/projects/project-a/synthesis/error-handling-pattern.md
  - wiki/projects/project-b/adr/ADR-0003-error-model.md
promotion_reason: repeated successful use across projects
promoted_at: 2026-05-15
```

## Demotion

A standard can be demoted to a pattern when it is too strict.

A pattern can be deprecated when it is no longer useful.

Record this with:

```yaml
status: deprecated
superseded_by: root/patterns/new-pattern
```
```

---

# `schema/operations.md`

```md
# LLM Wiki Operations

This file describes common LLM wiki operations.

## `ingest`

Read raw sources and update wiki pages.

Inputs:

```text
raw files
existing wiki pages
schema files
prompt file
```

Outputs:

```text
summaries
concept pages
technology pages
choices
ADRs
synthesis pages
model run record
```

Rules:

- Never edit `raw/`.
- Preserve provenance.
- Prefer updating existing pages over creating duplicates.
- Link related pages.
- Mark uncertainty.

## `query`

Answer a question using the wiki.

Rules:

- Prefer wiki pages over raw sources when current and trusted.
- Use raw sources when provenance is missing or the wiki is stale.
- Cite source pages and raw inputs.
- Distinguish fact from interpretation.

## `lint`

Audit the wiki.

Rules:

- Do not silently fix governance-sensitive issues.
- Create or update lint reports.
- Mark stale pages.
- Suggest fixes.

## `synthesize`

Create higher-level insight.

Examples:

- project current state
- cross-project technology drift
- repeated implementation problems
- promotion candidates
- risk overview

Rules:

- Must include sources.
- Must mark confidence.
- Must avoid unsupported conclusions.

## `refactor`

Improve wiki structure without changing meaning.

Examples:

- split long page
- merge duplicates
- rename unclear page
- add links
- normalize frontmatter

Rules:

- Preserve provenance.
- Preserve old links or add redirect notes.
- Do not change standards without explicit review.

## `review`

Evaluate standards, deviations, exceptions, choices, or project state.

Outputs:

```text
wiki/root/governance/reviews/<date>-<kind>-review.md
```

Rules:

- Be explicit about reviewed scope.
- List required follow-up.
- Link deviations and exceptions.
```

---

# Starter root standard examples

## `wiki/root/governance/standards/provenance.md`

```md
---
type: standard
id: STD-0001
scope: global
status: active
compliance_level: required
applies_to:
  - generated-pages
  - synthesis-pages
  - standards
created_at: 2026-05-15
updated_at: 2026-05-15
confidence: human-reviewed
generated_from: []
---

# Standard: Provenance

## Purpose

All generated wiki knowledge must be traceable back to its inputs.

## Rule

Every generated page must include provenance metadata showing source files, source hashes, prompt, schema, model, and generation run.

## Compliance criteria

A page is compliant when it includes:

- `generated_from`
- source paths
- source hashes
- `generated_by.model`
- `generated_by.prompt`
- `generated_by.schema`
- `generated_by.run_id`
- `generated_at`
- `confidence`

## Non-compliance

A generated page without provenance is a deviation.

## Examples

Compliant:

```yaml
generated_from:
  - path: raw/projects/project-a/notes/foo.md
    sha256: "..."
generated_by:
  model: claude-3-7-sonnet
  prompt: prompts/ingest.md
  schema: schema/project-schema.md
  run_id: 2026-05-15T120000Z-ingest-project-a
generated_at: 2026-05-15T12:00:00Z
confidence: medium
```

## Review policy

Review quarterly or whenever provenance tooling changes.
```

## `wiki/root/governance/standards/project-structure.md`

```md
---
type: standard
id: STD-0002
scope: global
status: active
compliance_level: recommended
applies_to:
  - active-projects
created_at: 2026-05-15
updated_at: 2026-05-15
confidence: human-reviewed
generated_from: []
---

# Standard: Project Wiki Structure

## Purpose

Project wikis should have a predictable structure so humans and LLMs can navigate them reliably.

## Rule

Active project wikis should follow the structure defined in `schema/project-schema.md`.

## Compliance criteria

A project is compliant when it has:

- `README.md`
- `adr/`
- `log/`
- `summaries/`
- `synthesis/`
- `architecture/overview.md`
- `dependencies/technology-stack.md`

## Non-compliance

Because this standard is recommended, missing folders are usually exceptions or warnings, not deviations.

## Review policy

Review when adding a new project or restructuring an existing project.
```

## `wiki/root/governance/standards/technology-choices.md`

```md
---
type: standard
id: STD-0003
scope: global
status: active
compliance_level: required
applies_to:
  - active-projects
created_at: 2026-05-15
updated_at: 2026-05-15
confidence: human-reviewed
generated_from: []
---

# Standard: Technology Choices

## Purpose

Projects may use different technologies, but important technology choices must be explicit and justified.

## Rule

Important technology choices must be documented as choices, not deviations, unless they violate a required standard.

## Compliance criteria

A technology choice is compliant when it documents:

- capability served
- selected technology
- alternatives considered
- reason for selection
- relevant standards
- risks
- review triggers

## Non-compliance

A project is non-compliant when it uses a significant technology without documenting the choice and the technology affects architecture, operations, security, or maintenance.

## Examples

SQLite instead of PostgreSQL is usually a choice, not a deviation.

A forbidden technology used in production without approval is a deviation.
```


# LLM Wikis for Software Factories

A comparative analysis of two wiki approaches for agentic software engineering, with recommendations for an optimal design targeting NixOS, Scala 3, Kyo, PostgreSQL, and multi-project development.

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [What Is a Software Factory?](#what-is-a-software-factory)
3. [Wiki-1: The Karpathy Pattern + Federated Extension](#wiki-1-the-karpathy-pattern--federated-extension)
4. [Wiki-2: The Routing/Ownership/Compliance Model](#wiki-2-the-routingownershipcompliance-model)
5. [Head-to-Head Comparison](#head-to-head-comparison)
6. [Strengths and Weaknesses](#strengths-and-weaknesses)
7. [What Both Miss](#what-both-miss)
8. [Verdict](#verdict)
9. [Recommendations: The Optimal Wiki](#recommendations-the-optimal-wiki)
10. [Appendix: Design Principles for Agentic Wikis](#appendix-design-principles-for-agentic-wikis)

---

## Executive Summary

Two wiki designs were analyzed for their fitness as knowledge substrates for AI-assisted multi-project software development:

- **Wiki-1** ships two variants: a simple Karpathy-style single-domain knowledge base (4 page types, Obsidian tooling) and an ambitious federated schema (25+ page types, SHA-256 provenance, formal governance hierarchy, promotion flows). The simple variant is pleasant but too shallow for software engineering. The federated variant has excellent ideas buried under enterprise ceremony.

- **Wiki-2** is a compact, operational design built around three core mechanisms: request routing (scope resolution before action), ownership classes (human/llm/shared with per-path defaults), and compliance-by-declaration (adopts/overrides/ignores with rationale). It is lean, mechanically verifiable, and respects the boundaries between human authority and agent autonomy.

**Verdict:** Wiki-2 is the stronger foundation. Its routing-first, ownership-aware architecture is better suited to how agentic coding actually works. Wiki-1's federated variant contributes valuable ideas (governance vocabulary, promotion flows, technology catalog, cross-project synthesis) that should be imported into Wiki-2's frame, not the other way around.

Neither wiki addresses the critical integration layer: how wiki knowledge flows into CLAUDE.md files, how agents discover relevant pages during coding sessions, or how code references validate against wiki claims. The optimal wiki must solve these.

---

## What Is a Software Factory?

In the context of AI-assisted development, a "software factory" is:

**A structured knowledge substrate that enables AI agents to operate autonomously on code projects while maintaining coherence, provenance, and human oversight.**

The factory analogy captures the key properties:

- **Repeatable processes** — ingest, query, lint, synthesize are defined operations, not ad-hoc conversations
- **Quality control** — drift detection, compliance verification, contradiction surfacing
- **Modularity** — specialized agents handle different concerns (API generation, database schemas, frontend components, infrastructure)
- **Shared tooling** — patterns, conventions, and standards are reusable across products
- **Human oversight** — the factory owner sets policy; the machines execute within constraints

The wiki sits at the center of this architecture:

```
Layer 1: Raw Sources (immutable, human-curated)
    |
Layer 2: Wiki (LLM-maintained knowledge graph)
    |   Root: governance, patterns, technology, architecture
    |   Projects: ADRs, tickets, logs, implementation
    |
Layer 3: Schema/Policy (CLAUDE.md, POLICY.md)
    |
Layer 4: Skills & Agents (domain-specific capabilities)
    |
Layer 5: Code (actual implementation in repos)
```

The wiki is the **compiled, verifiable, citable intermediate representation** between human intent and agent action. It prevents knowledge drift, hallucinated architecture, silent non-compliance, and loss of human control.

---

## Wiki-1: The Karpathy Pattern + Federated Extension

### Simple Variant (llm-wiki-master)

Based on Andrej Karpathy's LLM Wiki concept. A template repository where:

- `raw/` holds immutable source documents
- `wiki/` holds LLM-written and maintained pages
- `CLAUDE.md` serves as the schema (tells the LLM how to structure everything)
- Three operations: ingest, query, lint

**Page types:** concept, entity, summary, synthesis (4 total)

**Frontmatter:** title, type, tags, created, updated, sources, confidence

**Notable features:**
- Obsidian integration (Dataview dashboard, Charts View analytics, spaced repetition flashcards)
- Journal/research log with structured template
- Marp slide generation
- Clean, approachable, domain-agnostic

**Philosophy:** "You provide raw sources. The LLM reads them, writes structured wiki pages, cross-links everything, and maintains it over time. You never edit the wiki directly."

### Federated Variant (llm_wiki_schemas_and_readme.md)

A ~2900-line specification extending the simple pattern to multi-project coordination:

**Architecture:**
```
workspace/
  raw/global/ + raw/projects/
  schema/ (7 schema files)
  prompts/ (6 operation prompts)
  wiki/root/ (13 top-level folders)
  wiki/projects/<name>/ (14 folders per project)
  runs/ (model run records)
```

**Page types:** 25+ (project, source-summary, concept, technology, pattern, standard, adr, ticket, log-entry, synthesis, choice, exception, deviation, review, runbook, contract, threat-model, glossary-entry, capability, architecture-view, implementation-note, test-strategy, dependency-summary, provenance-record, model-run)

**Key mechanisms:**
- Mandatory SHA-256 provenance on all generated pages
- Model run records for every LLM operation
- Governance hierarchy: standards (rules) > choices (normal selections) > exceptions (accepted bending) > deviations (violations)
- Technology status taxonomy: preferred / allowed / experimental / legacy / forbidden
- Promotion flow: project log -> project synthesis -> root synthesis -> root pattern -> root standard
- Page lifecycle: draft -> active -> superseded -> deprecated -> archived
- Confidence levels: low / medium / high / human-reviewed
- Comprehensive lint rules (links, frontmatter, provenance, governance, technology, architecture, security, operations, synthesis, classification)

---

## Wiki-2: The Routing/Ownership/Compliance Model

A compact design (~400 lines across 4 files) built on three pillars:

### Pillar 1: Routing

Every request resolves to a scope before any action:

1. If it names a project -> scope is `project:<name>`, read that project's CLAUDE.md
2. If it's about a pattern/architecture/decision -> scope is `tech`, operate under `tech/`
3. If ambiguous -> search tech first, then project indices, synthesize across both
4. If it involves a source document -> source in `sources/raw/`, summary in `sources/summaries/`
5. If unresolved -> ask exactly one routing question, then act

**Why this matters:** Agents don't wander. Every operation begins with a deterministic target resolution, preventing the common failure of an agent writing project-specific content into shared spaces or vice versa.

### Pillar 2: Ownership

Three classes with path-level defaults:

| Ownership | Meaning |
|-----------|---------|
| **human** | Agent reads but never writes. Surfaces proposals in conversation. |
| **llm** | Agent owns. May create, edit, restructure, delete. |
| **shared** | Either party edits. Agent edits flagged for review. |

Critical design choices:
- `tech/POLICY.md` is **human-owned** — the agent cannot edit the rules it operates under
- `sources/raw/` is **human-owned** — immutable inputs
- `projects/*/log.md` is **llm-owned** — append-only mechanical records
- Individual files can override via frontmatter with mandatory `ownership_reason`

**Why this matters:** This is the only mechanism in either wiki that explicitly prevents the agent-editing-its-own-rules failure mode. It creates a clear separation of authority.

### Pillar 3: Compliance

Project ADRs declare compliance with tech-layer norms through structured frontmatter:

```yaml
compliance:
  adopts:
    - tech/decisions/effects-kyo.md
  overrides:
    - page: tech/patterns/blocking-io.md
      rationale: |
        Frame deadlines are hard; blocking-IO would cause jank.
  ignores:
    - page: tech/guides/jvm-tuning.md
      rationale: Scala Native, not JVM.
```

**Rules:**
- `adopts` entries must point to existing normative pages
- `overrides` requires a substantive rationale (empty/token rationales fail lint)
- `ignores` requires rationale (can be brief)
- **Silence is not compliance** — if a project never mentions a relevant normative page, lint flags it

**Page kinds:**
- `normative` — creates obligations (drift-checked)
- `descriptive` — creates awareness (freshness-checked, contradiction-checked)
- `stub` — placeholder (surfaced until filled, no enforcement)

### Pillar 4: Anti-patterns

Patterns explicitly rejected are first-class normative artifacts in `tech/patterns/anti/`. They declare what NOT to do, with reasons and alternatives. Lint scans for endorsement of anti-patterns.

---

## Head-to-Head Comparison

| Dimension | Wiki-1 (Federated) | Wiki-2 |
|-----------|-------------------|--------|
| **Lines of spec** | ~2900 | ~400 |
| **Page types** | 25+ | ~6 (by kind, not enumerated) |
| **Request handling** | Implicit (human reads schema) | Explicit routing algorithm |
| **Who writes what** | Implied (LLM writes wiki, human writes raw) | Explicit ownership table with override mechanism |
| **Compliance model** | Governance hierarchy (standards/choices/exceptions/deviations) | Compliance frontmatter (adopts/overrides/ignores) |
| **Drift detection** | Described conceptually in lint rules | Mechanically specified with 5 drift categories |
| **Provenance** | SHA-256 hashes, model run IDs, source chain | SHA-256 hashes, confidence levels (lighter touch) |
| **Technology management** | Full catalog with status taxonomy | `tech/stack/` pages with `used_by:` lists |
| **Cross-project synthesis** | Dedicated synthesis folders + promotion pipeline | `syntheses/` at root with scope frontmatter |
| **Anti-patterns** | Not addressed | First-class normative artifacts |
| **Agent self-modification** | Not addressed | Prevented by ownership classes |
| **Contradiction handling** | Flagged by lint | "Contradictions are valuable information; flattening them is destructive" |
| **Code integration** | None | None |
| **Obsidian tooling** | Dashboard, analytics, flashcards | None |
| **Schema enforcement** | Extensive frontmatter validation rules | Minimal required frontmatter, kind-based |

---

## Strengths and Weaknesses

### Wiki-1 Strengths

1. **Governance vocabulary is genuinely useful.** The choice/exception/deviation taxonomy captures real-world nuance. "I chose SQLite because it fits" is different from "I bent the preferred pattern" which is different from "I violated a required standard." This vocabulary should survive into any optimal design.

2. **Promotion flow captures organizational learning.** The path from project observation to root standard is well-designed: local log -> local synthesis -> root synthesis -> root pattern -> root standard. This prevents premature standardization while enabling bottom-up knowledge propagation.

3. **Technology catalog with capability mapping.** Linking technologies to capabilities (persistence, authentication, rendering) and tracking which projects use what is valuable for a 5-10 project portfolio. "What serves the persistence capability in each project?" is a real question.

4. **Cross-project synthesis as a first-class operation.** Dedicated synthesis pages that compare patterns across projects, identify drift, and surface promotion candidates. This is where multi-project wikis earn their keep.

5. **Comprehensive lint specification.** The lint rules are thorough: link resolution, frontmatter validation, provenance chain, governance consistency, technology coherence, architecture completeness, security basics, operations coverage. Even if over-specified, the coverage is instructive.

6. **Page lifecycle model.** Draft -> active -> superseded -> deprecated -> archived provides clear status semantics, especially `superseded` with its version chain.

7. **Obsidian integration (simple variant).** Dataview dashboard for surfacing low-confidence pages, orphan detection, and recent changes is practical for human review sessions.

### Wiki-1 Weaknesses

1. **Enterprise ceremony for a solo/small-team setting.** Formal deviation tracking with severity levels, mitigation plans, review dates, and quarterly reviews assumes an organization with compliance obligations. A developer with 5-10 personal projects needs "I chose X because Y, might revisit" — not `DEV-0001` with `severity: medium` and `review_by: 2026-06-01`.

2. **25+ page types with mandatory frontmatter creates schema compliance burden.** The LLM will frequently produce pages that fail lint because it forgot `review_by` on a deviation or omitted `compliance_level` on a standard. The simpler 4-type system (concept/entity/summary/synthesis) is more realistic. Each additional page type is a new way for generation to fail.

3. **SHA-256 provenance is aspirational without tooling.** The model cannot reliably compute SHA-256 hashes. Even if it could, file hashes change on every save. You need external tooling (a script, a pre-commit hook) to stamp hashes — which makes the "LLM maintains everything" promise hollow. Provenance is important; SHA-256 verification is the wrong mechanism for an LLM-maintained system.

4. **Model run records assume batch-process interaction.** In practice with Claude Code, you have dozens of micro-interactions per day. Recording each as a formal run with `run_id: 2026-05-15T120000Z-ingest-project-a` is bureaucratic overhead that no one will maintain. The append-only log captures session activity better.

5. **No routing logic.** The federated schema tells you what folders exist but not how to decide where a given request should be handled. The human (or LLM) must implicitly understand the two-layer architecture. Wiki-2's explicit routing algorithm is strictly superior here.

6. **No ownership model.** There's no mechanism to prevent the LLM from editing governance standards, raw sources, or its own schema. The immutability of `raw/` is stated as a rule but not enforced mechanically. Wiki-2's ownership classes solve this.

7. **No agent self-modification prevention.** The LLM could rewrite `schema/governance-schema.md` to relax its own compliance requirements. Nothing in the design prevents this.

8. **Obsidian-locked features.** Dashboard, analytics, and flashcards require Obsidian plugins. Terminal-first agentic development (Claude Code) cannot use these.

9. **Mandatory index updates on every change.** Every wiki edit requires touching `index.md` and `log.md`. This turns quick knowledge capture into a multi-file transaction where partial failure leaves the wiki inconsistent.

### Wiki-2 Strengths

1. **Routing-first design eliminates ambiguity.** Every request resolves to a scope before action. This is the single most important design choice for agentic operation — the agent knows where to look and where to write before doing anything.

2. **Ownership classes prevent catastrophic failures.** The human/llm/shared distinction with per-path defaults and override mechanism is the only design in either wiki that addresses the agent-editing-its-own-rules problem. `tech/POLICY.md` being human-owned is a critical safety property.

3. **Compliance-by-declaration is mechanically verifiable.** The adopts/overrides/ignores model with mandatory rationales creates a machine-checkable compliance surface. Lint can verify that `adopts:` entries point to existing pages, that `overrides:` have substantive rationales, and that silence is flagged.

4. **"Silence is not compliance" is the right default.** When a project never mentions a relevant normative page, it's a drift signal, not tacit acceptance. This prevents the common failure where standards exist but no one knows about them.

5. **Normative vs. descriptive distinction is clean and practical.** Instead of 25+ page types, Wiki-2 has two modes that matter: things you must comply with and things that are just information. This is the right abstraction level.

6. **Anti-patterns as first-class artifacts.** Explicitly documenting what NOT to do, with reasons and alternatives, is more useful than positive patterns alone. "Don't use Homebrew for crypto tooling because bottles lack reproducible provenance" is actionable.

7. **Compact specification.** ~400 lines vs ~2900 lines. The entire schema fits in a single context window. An agent can internalize it fully, reducing the chance of partial compliance.

8. **Contradiction preservation.** "Contradictions are valuable information about the world; flattening them is destructive." This is philosophically correct and practically important — auto-resolving contradictions destroys signal.

9. **Deliberate non-goals section.** "Does not enforce a single tagging taxonomy. Does not version pages (use git). Does not embed vector search. Does not auto-resolve contradictions." Knowing what the system deliberately doesn't do is as important as knowing what it does.

### Wiki-2 Weaknesses

1. **No governance vocabulary.** There's no equivalent of choice/exception/deviation. Everything is either adopted, overridden, or ignored. This loses nuance: "I chose SQLite" (normal) vs "I'm using mutable state despite the immutability preference" (exception) vs "I'm violating the provenance standard" (deviation) all collapse into `overrides:` with rationale.

2. **No promotion flow.** There's no mechanism for local project discoveries to become global patterns or standards. The synthesis system exists (`syntheses/` at root) but the lifecycle from local observation to shared convention is not specified.

3. **No technology catalog.** `tech/stack/` exists but there's no structured technology page format, no capability mapping, no status taxonomy. You can't ask "which projects use PostgreSQL?" without grep.

4. **No cross-project synthesis operation.** Wiki-2 defines ingest, query, edit, lint, and meta operations. There's no "synthesize across projects" operation. Cross-cutting insights depend on the human asking the right questions.

5. **Sparse page format specification.** There's no template system, no required sections by page type, no structured comparison format. Agents have freedom but also no guardrails for consistent page structure.

6. **No Obsidian or visualization integration.** The wiki is purely text-based. There's no dashboard, no analytics, no way to visualize the knowledge graph. For human review sessions, this is a gap.

7. **Drift detection is specified but not operationalized.** The five drift categories are defined, but there's no `meta/drift.md` template, no example output, no guidance on how often to run lint or what to do with results.

---

## What Both Miss

### 1. Code-Wiki Integration

Neither wiki provides a mechanism to link wiki pages to actual source code files, functions, modules, or types. For Scala 3 + Kyo development, you want references like:

```
Implements: src/main/scala/core/Effects.scala (KyoApp trait)
Tests: src/test/scala/core/EffectsSpec.scala
```

Without code references, the wiki exists in a parallel universe from the actual codebase. Claims about architecture cannot be validated against implementation. A wiki page saying "we use the Repository pattern for persistence" has no mechanical link to the actual repository trait.

### 2. CLAUDE.md Integration

Neither wiki explains how wiki knowledge feeds into the per-project `CLAUDE.md` files that Claude Code actually reads at session start. The wiki and the agentic coding context are disconnected. In practice, a developer needs:

- The project's CLAUDE.md to reference relevant wiki pages
- A mechanism for the wiki to generate or update CLAUDE.md content
- A way for agents to discover wiki pages during coding sessions without reading the entire wiki

### 3. Agent Session Workflow

Neither wiki addresses how an agent should use the wiki during a coding session:

- When should the agent consult the wiki? (Before starting? When hitting a decision point?)
- How does the agent know which pages are relevant to the current task?
- Should the agent update the wiki during a coding session or only during dedicated wiki operations?
- How does session context (what the agent learned during coding) flow back to the wiki?

### 4. Incremental Update

When a project's code changes, how does the wiki stay current? Neither system has a diff-based update mechanism. The entire ingest pipeline conceptually re-runs, which is wasteful and often impractical.

### 5. Multi-Repository Reality

Both wikis assume a single repository containing everything. In practice, a 5-10 project portfolio has separate git repos. The wiki needs to either:
- Live in its own repo with references to project repos
- Be distributed across repos with a federation mechanism
- Use a monorepo approach

### 6. Practical Tooling

Neither wiki ships with:
- A lint script that actually runs
- A hash computation utility
- A link checker
- An index generator
- A staleness detector

The lint rules are prose for LLMs to interpret, not executable checks. For a software factory, you want both: LLM-interpretable prose AND executable validation.

---

## Verdict

### Winner: Wiki-2, with significant imports from Wiki-1

Wiki-2's architecture is fundamentally sound for agentic software engineering:

1. **Routing solves the most common failure mode** — agents writing to the wrong scope
2. **Ownership solves the most dangerous failure mode** — agents modifying their own constraints
3. **Compliance-by-declaration creates mechanical verifiability** — lint can check it
4. **Compact specification fits in agent context** — the agent can fully internalize the rules
5. **Normative/descriptive distinction is the right abstraction** — compliance obligations vs. informational awareness

Wiki-1's federated variant contributes ideas that Wiki-2 should adopt:

1. **Governance vocabulary** (choice/exception/deviation) — adds nuance to `overrides:`
2. **Promotion flow** — enables bottom-up learning from projects to standards
3. **Technology catalog with capabilities** — answers "what serves persistence across projects?"
4. **Page templates with required sections** — ensures consistent structure for LLM generation
5. **Cross-project synthesis operation** — makes multi-project insight extraction a defined workflow

Wiki-1's simple variant contributes:

1. **Clean onboarding experience** — the template is immediately usable
2. **Obsidian dashboard concept** — human review needs a surface (adapt for terminal use)
3. **Journal/session log** — research sessions deserve capture (merge with log.md)

### What to discard

From Wiki-1:
- SHA-256 provenance hashes (replace with file paths + timestamps)
- Model run records (replace with append-only session logs)
- 25+ page types (reduce to ~8-10 with clear required sections)
- Formal deviation IDs and review dates (keep vocabulary, drop ceremony)
- Technology status taxonomy (preferred/allowed/experimental/legacy/forbidden — too bureaucratic for a solo developer)
- Obsidian-locked features (adapt concepts for terminal-first use)

From Wiki-2:
- Nothing to discard. Everything in Wiki-2 either survives as-is or gets extended.

---

## Recommendations: The Optimal Wiki

The optimal wiki for agentic software engineering across NixOS, Scala 3, Kyo, PostgreSQL, and multiple projects should:

### Architecture

1. **Use Wiki-2's routing/ownership/compliance as the foundation.** The three-pillar architecture (routing, ownership, compliance) is the structural backbone.

2. **Add Wiki-1's governance vocabulary as a compliance refinement.** `overrides:` in the compliance block should distinguish between exceptions (bending a preference) and deviations (violating a requirement). The `adopts/exceptions/deviations/ignores` model is richer than `adopts/overrides/ignores`.

3. **Add a promotion flow.** Define how local project patterns become global standards. Keep it lightweight: tag candidates in project syntheses, periodically run a cross-project synthesis operation.

4. **Add a technology catalog.** Structured pages for each technology (Scala 3, Kyo, PostgreSQL, SQLite, NixOS, Tapir, ScalaJS, etc.) with capability mapping and project usage tracking.

5. **Add code-wiki integration.** Wiki pages should reference source files. A separate index maps wiki concepts to code locations. This enables validation: "does the code still match what the wiki claims?"

6. **Add CLAUDE.md generation/linking.** The wiki should be able to produce project-specific CLAUDE.md content or at minimum provide stable references that CLAUDE.md files can import.

### Page Types (Reduced Set)

```
normative:  decision, pattern, anti-pattern, standard
descriptive: technology, guide, synthesis, glossary-entry
project:    adr, ticket, log-entry, interface, risk
meta:       stub (any kind, not yet filled)
```

~12 types total, each with clear required sections and simple frontmatter.

### Frontmatter (Simplified)

```yaml
---
id: effects-kyo                    # stable identifier
title: Use Kyo for effect management
kind: normative | descriptive | stub
status: draft | accepted | superseded | deprecated
scope: global | project:<name>
confidence: low | medium | high | reviewed
created: 2026-05-15
updated: 2026-05-15
applies_to:                        # normative pages only
  languages: [scala]
  domains: [any]
used_by: []                        # maintained by lint
supersedes: []
sources: []                        # file paths, not hashes
ownership: human | llm | shared    # override only, usually inherited
---
```

### Operations

Keep Wiki-2's five operations (ingest, query, edit, lint, meta) and add:

- **synthesize** — explicit cross-project synthesis operation
- **promote** — move a local pattern to root level
- **session-capture** — lightweight log of what happened during a coding session

### Key Principles

1. **Routing before action** — always resolve scope first
2. **Ownership before writing** — always check who owns the target
3. **Compliance by declaration** — projects declare their relationship to norms
4. **Silence is not compliance** — missing declarations are flagged
5. **Contradictions are preserved** — do not auto-resolve
6. **Normative pages create obligations; descriptive pages create awareness**
7. **The agent cannot edit its own rules** — POLICY.md and ownership.md are human-owned
8. **Promotion earns its way** — local patterns become global only with evidence
9. **Fit in context** — the full schema must fit in one agent context window
10. **Executable where possible** — lint rules should be both prose and scripts

See `llm-wiki-schema.md` for the full specification.

---

## Appendix: Design Principles for Agentic Wikis

### The Working Memory Problem

An LLM agent has no persistent memory across sessions. The wiki serves as external working memory — but only if the agent knows how to find relevant pages quickly. This means:

- **Index files are retrieval entry points.** Agents read the index first, not the entire wiki.
- **Frontmatter enables filtering.** `kind: normative` + `applies_to: scala` narrows the search space.
- **Routing algorithms are faster than search.** Deterministic scope resolution beats "search everything."
- **The wiki must fit the agent's attention.** If the agent needs to read 50 pages to understand a project, the wiki has failed. Five pages (README, architecture overview, technology stack, current synthesis, relevant standards) should be sufficient.

### The Authority Problem

When the AI is both consumer and producer of wiki content, circularity threatens:

- The agent reads a page it wrote last week
- It treats that page as authoritative
- It generates new content based on possibly incorrect prior output
- Errors compound

Solution: provenance chains that terminate at non-generated inputs:
```
wiki page -> cites -> summary -> has source path -> matches -> raw file (human-provided)
```

Confidence levels serve as trust signals:
- `low` / `medium` — LLM-generated, treat as hypotheses
- `high` — multiple corroborating sources
- `reviewed` — human has validated

### The Coherence Problem

Multiple projects sharing technology (Scala 3, Kyo, NixOS) should make compatible architectural choices. But coherence != uniformity:

- A pattern that works for a web server may not work for a Wayland compositor
- SQLite and PostgreSQL are both valid persistence choices for different contexts
- Scala JVM and Scala Native have different performance profiles and library availability

The wiki solves coherence through:
1. **Normative pages** — things everyone must address (adopt, override, or ignore)
2. **Descriptive pages** — things everyone should be aware of
3. **Drift detection** — mechanical identification of unaddressed obligations
4. **Compliance rationales** — understanding WHY a project deviates, not just THAT it deviates

### The Granularity Problem

Too coarse: "We use functional programming" (useless for an agent writing code)
Too fine: "Line 42 of Effects.scala uses `Kyo.run`" (too volatile, instantly stale)

The sweet spot for agent consumption:
- **Patterns** describe HOW to structure code (with examples)
- **Decisions** explain WHY a choice was made (with alternatives considered)
- **Interfaces** define WHAT the boundaries look like (with contracts)
- **Guides** show HOW to accomplish common tasks (with step-by-step instructions)

Each page should be independently useful — an agent reading just that page should be able to act on it without reading 10 prerequisite pages.

### The Staleness Problem

Wiki content becomes stale when:
- Code changes but the wiki doesn't
- A decision is superseded but the page isn't updated
- A technology version changes
- A pattern proves problematic in practice

Mitigation:
- **Append-only logs** capture the temporal dimension
- **Status field** marks superseded/deprecated pages
- **`updated:` timestamps** surface old pages
- **Lint** checks for common staleness signals
- **Synthesis operations** periodically reconcile wiki claims against current state

### The Scale Problem

At 5-10 projects with NixOS infrastructure, Scala 3 libraries, web services, and CLI tools, you might have:
- 50-100 wiki pages in the root
- 20-50 pages per project
- Total: 200-600 pages

This is manageable with index files and frontmatter filtering. No vector search needed. Grep + structured frontmatter is sufficient.

If you hit 1000+ pages, add an external index. But design for the current scale, not a hypothetical future.

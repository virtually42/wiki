# Coherence Policy

This file defines what coherence means across projects and how it is enforced.
CLAUDE.md handles command dispatch; meta/schema.md handles page structure;
this file handles normative coherence.

**Ownership: human.** The agent never edits this file without explicit instruction.

---

## Page Kinds

Every page under `tech/` and every project ADR declares a `kind` in frontmatter.

| Kind          | Where                                               | Meaning                                                    |
|---------------|-----------------------------------------------------|------------------------------------------------------------|
| `normative`   | `tech/architecture/`, `tech/patterns/`, `tech/decisions/`, project `adr/` | A rule, decision, or pattern that projects must address.   |
| `descriptive` | `tech/stack/`, `tech/capabilities/`, `tech/guides/`, `tech/glossary.md`, summaries, syntheses, design docs | An observation, fact, or analysis. No compliance obligation. |
| `project`     | `projects/*/plans/`, `projects/*/tickets/`, `projects/*/log.md` | Project-scoped work artifacts. No compliance obligation. |
| `session`     | `projects/*/wip.md`, top-level `wip.md`             | Session-bound handoff state. Overwritten each session. No compliance obligation. |
| `stub`        | anywhere                                            | Placeholder. Lint surfaces these until filled in.          |

Normative pages are the only ones drift checks operate on. Descriptive pages get freshness and contradiction checks but no compliance enforcement. Session pages get freshness checks only — stale `wip.md` files surface in drift.

---

## Compliance Contract

Every project ADR has a `compliance` block. This is the mechanical hook for drift detection.

```yaml
compliance:
  adopts:
    - tech/decisions/effects-kyo.md
  exceptions:
    - page: tech/patterns/immutable-state.md
      rationale: |
        Rendering pipeline uses mutable frame buffer for performance.
      risk: low
  deviations:
    - page: tech/decisions/require-property-tests.md
      rationale: |
        Property test generators not yet written for protocol types.
      severity: medium
      mitigated_by: Manual edge case testing in tests/manual.md
  ignores:
    - page: tech/guides/jvm-tuning.md
      rationale: Scala Native, not JVM.
```

### Categories

| Category     | What it means                                 | Required fields                    |
|--------------|-----------------------------------------------|------------------------------------|
| `adopts`     | Follows this norm                             | Target path (must exist, be normative) |
| `exceptions` | Bends a preference with justification         | `page`, `rationale`, `risk`        |
| `deviations` | Violates a requirement with mitigation        | `page`, `rationale`, `severity`, `mitigated_by` |
| `ignores`    | Norm does not apply to this project           | `page`, `rationale`               |

### Rules

- `adopts` targets must exist and have `kind: normative` with `status: accepted`.
- `exceptions` rationale must be at least one full sentence.
- `deviations` rationale must explain WHY the violation exists and HOW it is mitigated.
- `ignores` rationale can be brief but must state why the norm is irrelevant.
- **Silence is not compliance.** A project whose ADRs never mention a normative tech page that applies to its stack gets flagged in `meta/drift.md`.

---

## Normative Tech Pages

Normative pages declare their own scope:

```yaml
applies_to:
  languages: [scala, scala-native]
  domains: [any]
  excludes: [shell-scripts]
used_by: []              # maintained by lint
supersedes: []
superseded_by: null
```

- `applies_to` is interpreted permissively. Stack overlap = in scope.
- `used_by` is maintained by lint from project ADR compliance blocks.
- A superseded page is read-only. New ADRs must cite the current version.

---

## Drift

Drift is mechanically computed by lint and written to `meta/drift.md`.

### Drift categories

1. **Missing declaration.** Project is in-scope for a normative page but its ADRs make no statement.
2. **Dangling adoption.** Project adopts a page that no longer exists or has been superseded.
3. **Weak rationale.** An `exceptions` or `deviations` entry with placeholder or empty rationale.
4. **Conflicting adoptions.** Project adopts two normative pages that contradict each other.
5. **Unused normative pages.** A normative page that no project has addressed after a reasonable period.

Drift entries are **not auto-fixed**. They are surfaced to the human.

---

## Anti-Patterns

`tech/patterns/anti/` holds patterns explicitly rejected. They are normative — projects must not adopt them.

```yaml
---
id: homebrew-for-crypto
title: Do not use Homebrew for cryptographic tooling
kind: normative
status: rejected
applies_to:
  domains: [security, build-systems]
reasons:
  - Bottle binaries lack reproducible provenance
alternatives:
  - tech/guides/build-from-source-with-checksums.md
---
```

---

## Page Lifecycle

```
stub -> draft -> accepted -> (superseded | deprecated)
```

- A page in `stub` or `draft` is not enforced by drift checks even if normative. This lets the agent create placeholders without raising drift everywhere.
- Promotion to `accepted` is a human action. The agent may propose it.

---

## Promotion

Local project patterns may be promoted to tech-layer when:

- The pattern appears in 2+ projects, OR one project demonstrates a clearly reusable solution
- Tradeoffs are understood
- Evidence supports it (provenance from project syntheses)

Promotion path:
```
project log -> project synthesis -> cross-project synthesis -> tech pattern -> tech decision (if normative)
```

Promoted pages record their origin:
```yaml
promoted_from:
  - projects/compositor/syntheses/error-boundaries.md
  - projects/webapp/adr/003-typed-errors.md
promoted_at: 2026-05-15
```

Demotion: change `status: deprecated` and set `superseded_by:`.

---

## Citations and Provenance

Every normative claim in a tech page should cite at least one source or summary. The chain:

```
tech/decision.md -> cites -> sources/summaries/paper.md -> references -> sources/raw/paper.pdf
```

Lint walks this chain. A normative claim with no source citation is flagged as `unsourced` — the human decides whether it is self-evident, organizational consensus, or needs grounding.

---

## What This Policy Deliberately Does Not Do

- Does not require every project to know about every tech page. `applies_to` scopes the universe.
- Does not enforce semantic consistency across natural-language descriptions. That is what `glossary.md` and human review are for.
- Does not compute compliance scores or dashboards. Coherence is checked one ADR at a time.
- Does not auto-resolve contradictions. They are valuable signal.

# Ownership Policy

Canonical source for who edits what. The root `CLAUDE.md` mirrors this table; if they disagree, this file wins.

## Defaults

| Path glob                     | Default ownership | Override allowed? |
|-------------------------------|-------------------|-------------------|
| `CLAUDE.md`                   | shared            | no                |
| `tech/POLICY.md`              | human             | no                |
| `tech/architecture/**`        | llm               | yes               |
| `tech/patterns/**`            | llm               | yes               |
| `tech/patterns/anti/**`       | llm               | yes               |
| `tech/decisions/**`           | shared            | yes               |
| `tech/stack/**`               | llm               | yes               |
| `tech/guides/**`              | llm               | yes               |
| `tech/glossary.md`            | shared            | no                |
| `tech/index.md`               | llm               | no                |
| `projects/*/CLAUDE.md`        | shared            | no                |
| `projects/*/adr/**`           | shared            | yes               |
| `projects/*/tickets/**`       | shared            | yes               |
| `projects/*/interfaces.md`    | shared            | yes               |
| `projects/*/risk.md`          | shared            | yes               |
| `projects/*/log.md`           | llm               | no                |
| `projects/*/syntheses/**`     | llm               | yes               |
| `projects/*/index.md`         | llm               | no                |
| `sources/raw/**`              | human             | no                |
| `sources/summaries/**`        | llm               | yes               |
| `syntheses/**`                | llm               | yes               |
| `meta/ownership.md`           | human             | no                |
| `meta/drift.md`               | llm               | no                |
| `meta/log.md`                 | llm               | no                |

## Semantics

- **human**: the agent reads but never writes. Edits require explicit, in-conversation human action. If the agent has a proposal, it surfaces the diff and waits.
- **llm**: the agent owns the file. It may create, edit, restructure, or delete (with caution). The human reads but should not hand-edit; hand-edits can be overwritten by future operations.
- **shared**: either party edits. Agent edits are flagged in the response so the human can review. Human edits should not embed agent-managed structure (e.g., generated index sections).

## Override mechanism

When `Override allowed? = yes`, an individual file's frontmatter may override the default:

```yaml
---
ownership: human   # overrides default of llm
ownership_reason: This page records a decision the human is still drafting.
---
```

`ownership_reason` is mandatory when overriding. Lint enforces this.

## Why these defaults

- **`tech/POLICY.md` is `human`**: this file defines the rules the agent operates under. The agent editing its own rules is a class of failure to avoid.
- **`tech/decisions/` is `shared` but `tech/architecture/` and `tech/patterns/` are `llm`**: decisions encode human intent and should be human-led. Architecture and pattern pages are descriptions of structure the agent can capture from sources.
- **`projects/*/log.md` is `llm`**: logs are append-only mechanical records. Human edits to logs break the timeline.
- **`sources/raw/**` is `human`**: raw sources are immutable. The hash check in lint depends on this.
- **`projects/*/index.md` is `llm`**: generated from frontmatter. Hand-edits will be lost.

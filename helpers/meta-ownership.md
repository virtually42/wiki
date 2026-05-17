# Ownership Policy

Canonical source for who edits what. If CLAUDE.md's ownership table disagrees with this file, this file wins.

**Ownership: human.** The agent never edits this file.

---

## Defaults

| Path glob                     | Default   | Override? |
|-------------------------------|-----------|-----------|
| `CLAUDE.md`                   | shared    | no        |
| `POLICY.md`                   | human     | no        |
| `tech/architecture/**`        | llm       | yes       |
| `tech/patterns/**`            | llm       | yes       |
| `tech/decisions/**`           | shared    | yes       |
| `tech/stack/**`               | llm       | yes       |
| `tech/capabilities/**`        | llm       | yes       |
| `tech/guides/**`              | llm       | yes       |
| `tech/glossary.md`            | shared    | no        |
| `tech/index.md`               | llm       | no        |
| `projects/*/CLAUDE.md`        | shared    | no        |
| `projects/*/adr/**`           | shared    | yes       |
| `projects/*/tickets/**`       | shared    | yes       |
| `projects/*/architecture.md`  | shared    | yes       |
| `projects/*/interfaces.md`    | shared    | yes       |
| `projects/*/risk.md`          | shared    | yes       |
| `projects/*/log.md`           | llm       | no        |
| `projects/*/syntheses/**`     | llm       | yes       |
| `projects/*/index.md`         | llm       | no        |
| `sources/raw/**`              | human     | no        |
| `sources/summaries/**`        | llm       | yes       |
| `syntheses/**`                | llm       | yes       |
| `meta/ownership.md`           | human     | no        |
| `meta/drift.md`               | llm       | no        |
| `meta/registry.md`            | shared    | no        |
| `meta/log.md`                 | llm       | no        |
| `tools/**`                    | human     | no        |

---

## Semantics

- **human**: agent reads but never writes. Proposals surfaced in conversation.
- **llm**: agent owns. May create, edit, restructure. Human reads but should not hand-edit — hand-edits may be overwritten.
- **shared**: either party edits. Agent edits are flagged in conversation for review.

---

## Override Mechanism

When override is allowed, a file's frontmatter may override the default:

```yaml
---
ownership: human
ownership_reason: This decision is still in active human deliberation.
---
```

`ownership_reason` is mandatory when overriding. Lint enforces this.

---

## Why These Defaults

- **POLICY.md is human**: the agent editing its own rules is a failure mode to prevent.
- **tech/decisions/ is shared**: decisions encode human intent, agent structures them.
- **tech/architecture/ and tech/patterns/ are llm**: structural descriptions the agent captures from evidence.
- **projects/*/log.md is llm**: append-only mechanical records. Human edits break the timeline.
- **sources/raw/ is human**: immutable inputs. The provenance chain depends on this.
- **projects/*/index.md is llm**: generated from frontmatter. Hand-edits will be lost.
- **tools/ is human**: executable scripts should not be modified by the agent operating under those scripts.

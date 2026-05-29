# Ownership Policy

Canonical source for who edits what.

**Ownership: human.** The agent never edits this file.

---

## Defaults

| Path glob                     | Default   | Override? |
|-------------------------------|-----------|-----------|
| `CLAUDE.md`                   | shared    | no        |
| `POLICY.md`                   | human     | no        |
| `meta/schema.md`              | human     | no        |
| `meta/ownership.md`           | human     | no        |
| `meta/drift.md`               | llm       | no        |
| `meta/registry.md`            | shared    | no        |
| `meta/log.md`                 | llm       | no        |
| `index.md`                    | llm       | no        |
| `wip.md`                      | llm       | no        |
| `tech/index.md`               | llm       | no        |
| `tech/architecture/**`        | llm       | yes       |
| `tech/patterns/**`            | llm       | yes       |
| `tech/decisions/**`           | shared    | yes       |
| `tech/stack/**`               | llm       | yes       |
| `tech/capabilities/**`        | llm       | yes       |
| `tech/guides/**`              | llm       | yes       |
| `tech/glossary.md`            | shared    | no        |
| `projects/*/index.md`         | llm       | no        |
| `projects/*/adr/**`           | shared    | yes       |
| `projects/*/designs/**`       | shared    | yes       |
| `projects/*/plans/**`         | shared    | yes       |
| `projects/*/tickets/**`       | shared    | yes       |
| `projects/*/architecture.md`  | shared    | yes       |
| `projects/*/interfaces.md`    | shared    | yes       |
| `projects/*/risk.md`          | shared    | yes       |
| `projects/*/log.md`           | llm       | no        |
| `projects/*/wip.md`           | llm       | no        |
| `projects/*/syntheses/**`     | llm       | yes       |
| `sources/raw/**`              | human     | no        |
| `sources/summaries/**`        | llm       | yes       |
| `syntheses/**`                | llm       | yes       |
| `tools/**`                    | human     | no        |
| `scratch/**`                  | human     | no        |

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

- **POLICY.md and meta/schema.md are human**: the agent editing its own rules or format specs is a failure mode to prevent.
- **tech/decisions/ is shared**: decisions encode human intent, agent structures them.
- **tech/architecture/ and tech/patterns/ are llm**: structural descriptions the agent captures from evidence.
- **projects/*/designs/ and projects/*/plans/ are shared**: collaborative exploration and planning.
- **projects/*/log.md is llm**: append-only mechanical records. Human edits break the timeline.
- **sources/raw/ is human**: immutable inputs. The provenance chain depends on this.
- **projects/*/index.md is llm**: generated from frontmatter. Hand-edits will be lost.
- **tools/ is human**: executable scripts should not be modified by the agent operating under those scripts.
- **scratch/ is human**: personal working notes. Agent reads if asked, never writes, lint never enforces — outside the schema by design.
- **wip.md (top-level and projects/*/wip.md) is llm**: session handoff state, overwritten each session. Like `log.md`, hand-edits will be lost on next `wip` invocation.


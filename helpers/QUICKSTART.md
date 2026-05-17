# Quick Start: Software Factory Wiki

How to bootstrap the wiki for your multi-project workspace.

---

## 1. Create the directory structure

```
mkdir -p wiki/{tech/{architecture,patterns/anti,decisions,stack,capabilities,guides},projects,sources/{raw,summaries},syntheses,meta,tools}
```

## 2. Copy the core files

```
cp helpers/POLICY.md wiki/POLICY.md
cp helpers/meta-ownership.md wiki/meta/ownership.md
cp helpers/meta-registry.md wiki/meta/registry.md
cp llm-wiki-schema.md wiki/CLAUDE.md    # or adapt it
```

Create empty scaffolding:
```
touch wiki/tech/index.md
touch wiki/tech/glossary.md
touch wiki/meta/drift.md
touch wiki/meta/log.md
```

## 3. Register your first project

Edit `wiki/meta/registry.md` to add your project:

```markdown
| my-project | active | Scala 3, Kyo, PostgreSQL | Description here | 0 |
```

Create the project structure:
```
mkdir -p wiki/projects/my-project/{adr,tickets/open,tickets/closed,syntheses}
```

Create `wiki/projects/my-project/CLAUDE.md` from the project template in the schema.

Create `wiki/projects/my-project/log.md`:
```markdown
# my-project Log

## [2026-05-17] ingest | Project wiki initialized

Created project structure, CLAUDE.md, initial architecture overview.
```

## 4. Write your first tech pages

Start with the technologies you actually use. Each gets a page in `tech/stack/`:

```
wiki/tech/stack/scala.md
wiki/tech/stack/kyo.md
wiki/tech/stack/nix.md
wiki/tech/stack/postgresql.md
```

See `helpers/examples/tech-stack-postgresql.md` for the template.

## 5. Write your first decision

If you have a workspace-wide decision (e.g., "use Kyo for effects"), create it in `tech/decisions/`:

```
wiki/tech/decisions/effects-kyo.md
```

See `helpers/examples/tech-decision-effects-kyo.md` for the template.

## 6. Write your first project ADR

Create an ADR in your project that references the tech decision:

```
wiki/projects/my-project/adr/0001-effect-system.md
```

Include the compliance block:
```yaml
compliance:
  adopts:
    - tech/decisions/effects-kyo.md
  exceptions: []
  deviations: []
  ignores: []
```

See `helpers/examples/project-adr-with-compliance.md` for the template.

## 7. Run lint

Ask the agent: "lint my-project"

It should verify:
- CLAUDE.md exists
- ADR has compliance block
- `adopts` targets exist and are normative
- No drift (missing declarations)

## 8. Grow organically

Don't create pages speculatively. Add pages when:

- You make a decision that should be documented (ADR)
- You notice a pattern across projects (synthesis, then maybe pattern)
- You evaluate a technology (stack page)
- You need to explain how to do something (guide)
- You need to define a term (glossary entry)

The wiki should grow from actual needs, not from filling out a template.

---

## What to do in an agentic coding session

When starting a coding session with Claude Code:

1. **The agent reads the project's CLAUDE.md** — this gives it the project context
2. **For architectural questions**, the agent consults `tech/` pages
3. **For implementation decisions**, the agent checks existing ADRs
4. **After the session**, the agent can append to `log.md` noting what was done

The wiki serves as persistent working memory across sessions. What the agent learns in one session is captured for the next.

---

## File sizes to target

- **CLAUDE.md (root)**: 200-400 lines. Must fit in agent context.
- **POLICY.md**: 100-200 lines. Read at session start.
- **Tech pages**: 50-150 lines each. One topic per page.
- **Project ADRs**: 50-100 lines. Decision + compliance block.
- **Syntheses**: 100-200 lines. Analysis with citations.
- **Log entries**: 5-15 lines per entry. Brief but traceable.

If a page exceeds 200 lines, consider splitting it.

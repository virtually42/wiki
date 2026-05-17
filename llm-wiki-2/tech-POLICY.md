# Coherence Policy

This file defines what coherence means across projects and how it is enforced. The root `CLAUDE.md` handles routing and ownership; this file handles normative content.

## Page kinds

Every page under `tech/` and every project ADR declares a `kind` in frontmatter.

| Kind          | Where                                  | Meaning                                                                 |
|---------------|----------------------------------------|-------------------------------------------------------------------------|
| `normative`   | `tech/architecture/`, `tech/patterns/`, `tech/decisions/`, project `adr/` | A rule, decision, or pattern that projects must comply with or override. |
| `descriptive` | `tech/stack/`, `tech/guides/`, `tech/glossary.md`, summaries, syntheses | An observation, fact, or analysis. No compliance obligation.            |
| `stub`        | anywhere                               | Placeholder. Lint surfaces these until filled in.                       |

Normative pages are the only ones drift checks operate on. Descriptive pages get freshness and contradiction checks but no compliance enforcement.

## Compliance frontmatter

Every project ADR has a `compliance` block. This is the mechanical hook for drift detection.

```yaml
---
id: compositor-adr-007
title: Effect system choice
kind: normative
status: accepted    # proposed | accepted | superseded | deprecated
date: 2026-05-15
compliance:
  adopts:
    - tech/decisions/effects-kyo.md
    - tech/patterns/effect-handlers.md
  overrides:
    - page: tech/patterns/blocking-io.md
      rationale: |
        The compositor's input thread cannot use the blocking-IO pattern
        because frame deadlines are hard. See tickets/2026-Q2-input-latency.
  ignores:
    - page: tech/guides/jvm-tuning.md
      rationale: Scala Native, not JVM.
---
```

**Rules:**

- `adopts` entries must point to normative tech pages. Lint verifies the target exists and has `kind: normative`.
- `overrides` requires a non-empty `rationale` of at least one full sentence. Empty or token rationales fail lint.
- `ignores` is for normative pages that don't apply to this project at all (wrong platform, wrong language, wrong domain). Still requires a rationale, but a short one is fine.
- Silence is not compliance. If a project's ADR set never mentions a normative tech page, lint computes whether that page is *topically relevant* to the project (by `used_by:` membership and tag overlap) and flags missing declarations in `meta/drift.md`.

## Normative tech pages

Normative pages declare their own scope so projects know whether they apply.

```yaml
---
id: effect-handlers
title: Effect handlers as the default control structure
kind: normative
status: accepted
date: 2026-03-01
applies_to:
  languages: [scala, scala-native]
  domains: [any]
  excludes: [shell-scripts]
used_by:
  - projects/compositor
  - projects/browser
supersedes: []
superseded_by: null
---
```

**Rules:**

- `applies_to` is interpreted permissively. A project whose tech stack overlaps with any of the declared languages or domains is considered in-scope and must adopt, override, or ignore.
- `used_by` is maintained by lint, not by hand. The agent updates it when project ADRs adopt or override the page.
- `supersedes` and `superseded_by` form the version chain. A superseded page is read-only; new ADRs must cite the current version.

## Drift

Drift is any case where coherence is mechanically violated. The lint operation computes drift and writes `meta/drift.md`. Drift entries fall into categories:

1. **Missing declaration.** A project is in-scope for a normative tech page but its ADRs make no statement.
2. **Dangling adoption.** A project adopts a tech page that no longer exists, has been superseded, or has been deprecated.
3. **Unjustified override.** An `overrides:` entry with a placeholder rationale or with `rationale` missing key terms from the overridden page's title.
4. **Conflicting adoptions.** A project adopts two tech pages that contradict each other (per the contradictions index).
5. **Unused normative pages.** A `tech/decisions/` page that no project has either adopted, overridden, or ignored after a grace period. Indicates the decision was made in a vacuum.

Drift entries are not auto-fixed. They are presented to the human, who chooses one of: write a new ADR, update the tech page, mark the drift as accepted, or change the policy.

## Anti-patterns

`tech/patterns/anti/` holds patterns explicitly rejected. They are normative — projects must not adopt them. Lint scans project code references and synthesis pages for anti-pattern mentions and flags any that read as endorsement rather than warning.

Anti-pattern frontmatter:

```yaml
---
id: homebrew-for-crypto
title: Using Homebrew for cryptographic tooling
kind: normative
status: rejected
date: 2026-01-15
applies_to:
  domains: [security, build-systems]
reasons:
  - Bottle binaries lack reproducible provenance
  - Formula signing is best-effort, not enforced
  - Conflicts with audited-source policy
alternatives:
  - tech/guides/build-from-source-with-checksums.md
---
```

## Page lifecycle

- **stub** → **draft** → **accepted** → (**superseded** | **deprecated**)
- A page in `stub` or `draft` is not enforced by drift checks even if normative. This lets the agent create placeholders during ingest without immediately raising drift everywhere.
- Promotion to `accepted` is a human action. The agent may propose it.

## Citations and provenance

Every normative claim in a tech page should cite at least one source or summary. The chain is:

`tech/decision.md` → cites → `sources/summaries/paper.md` → has `sha256:` → matches `sources/raw/paper.pdf`

Lint walks this chain. A normative claim with no source citation is allowed but flagged as `unsourced` so the human can decide whether the claim is self-evident, organizational consensus, or actually needs grounding.

## What this policy deliberately does not do

- It does not require every project to be aware of every tech page. `applies_to` plus `used_by` scope the universe of relevant pages per project.
- It does not enforce semantic consistency across natural-language descriptions. Lint cannot tell whether two pages mean the same thing if they use different words. That is what `glossary.md` and human review are for.
- It does not compute compliance scores or dashboards. Coherence is not a metric; it is a property checked one ADR at a time.

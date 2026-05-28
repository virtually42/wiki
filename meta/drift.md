# Drift Report

Mechanically computed by `lint`. Each entry is a coherence gap surfaced
to the human — entries are **not auto-fixed**. The human decides whether
to remediate, override, or accept.

**Ownership: llm** (regenerated each lint).

---

## Run Metadata

- **Run at**: 2026-05-28 (third run of the day)
- **Previous run**: 2026-05-28 (post-remediation, all 8 findings closed)
- **Operation**: lint
- **Normative pages in scope**:
  - `tech/decisions/deps-single-file.md` (accepted, 2026-05-24)
  - `tech/patterns/functional-domain-design.md` (accepted, 2026-05-28)
- **Projects on disk**: `compositor` (only — webapp / cli-tool / infra remain `planned`, excluded)
- **External-lib bridges in scope**: `mill`, `kyo`, `airstream`
- **New Layer-2 pages since last lint**: `tech/stack/kyo.md`, `tech/stack/airstream.md`, `syntheses/wiki-layering-and-external-lib-wikis.md`, `sources/summaries/throw_away_the_irrelevant_john_de_goes_podcast.md`

---

## Summary

| ID | Category | Severity | Status |
|----|----------|----------|--------|
| DRIFT-009 | dangling-link | low | **resolved** — removed the `meta/registry.md` line from `index.md` |
| DRIFT-010 | dangling-link | low | **resolved** — created `tech/glossary.md` as a stub matching the schema's `glossary-entry` location |
| DRIFT-011 | content-frontmatter-contradiction | low | **open** — `tech/patterns/functional-domain-design.md` body claims no ADR adopters while frontmatter `used_by` lists one |
| DRIFT-012 | formatting-glitch | low | **resolved** — human deleted the orphan `scratch/` paragraph from `meta/ownership.md` |
| DRIFT-013 | descriptive-used_by-empty | informational | **open** — `tech/stack/mill.md`, `tech/stack/kyo.md`, `tech/stack/airstream.md` all have `used_by: []` while compositor lists Mill and Kyo in its stack |

**Net**: 5 new findings since the previous clean state. Compliance side
(missing-declaration / dangling-adoption / weak-rationale / conflicting-
adoptions / unused-normative) remains clean — both accepted normative
pages still have their compositor adopter.

---

## DRIFT-009 — dangling-link (index.md → meta/registry.md)

**Category**: dangling-link
**Severity**: low
**Subject**: `index.md` line 81

```markdown
- [meta/registry.md](meta/registry.md) — project registry
```

The file `meta/registry.md` does not exist. `/p/wiki/meta/` contains
only `drift.md`, `log.md`, `ownership.md`, and `schema.md`. No other
page in the wiki references `meta/registry.md` — neither `CLAUDE.md`
nor `POLICY.md` describes a registry. The link was likely carried over
from an earlier wiki shape.

### Remediation options

1. **Remove the line** from `index.md`. Lowest-effort; matches reality.
2. **Create `meta/registry.md`** as a generated registry of projects
   (similar to the `Projects` table already in `index.md`). Adds a
   page; redundant with the index unless it gains content the index
   doesn't carry.

Recommended: option 1.

---

## DRIFT-010 — dangling-link (glossary references)

**Category**: dangling-link
**Severity**: low
**Subjects**:
- `index.md:24` — Tech-Layer table row "Glossary | tech/glossary.md | Shared vocabulary"
- `tech/index.md:40` — "[tech/glossary.md](glossary.md)"

The file `tech/glossary.md` does not exist. The schema
(`meta/schema.md:21`) explicitly lists `glossary-entry` as a page
type whose location is `tech/glossary.md`, so removing the references
without acknowledging the schema would leave the schema describing a
non-existent location.

### Remediation options

1. **Create `tech/glossary.md` as a stub** with `kind: stub` per the
   schema's `Page Lifecycle` model. Most conservative — matches the
   schema's expectation.
2. **Remove both references** and amend `meta/schema.md` to drop
   `glossary-entry` from the catalog. Requires a human edit to
   `meta/schema.md` (human-owned).

Recommended: option 1.

---

## DRIFT-011 — content-frontmatter-contradiction (functional-domain-design.md)

**Category**: content-frontmatter-contradiction
**Severity**: low
**Subject**: `tech/patterns/functional-domain-design.md` §"Open Questions / Drift Signals" (lines 236–243)

The section claims:

> "We have no project ADR yet citing this page. Until a project adopts,
> excepts, or ignores it, lint will surface it under *unused normative
> pages* in `meta/drift.md`."

This contradicts the same file's frontmatter:

```yaml
used_by:
  - projects/compositor/adr/0001-adopt-functional-domain-design.md
```

…and `meta/drift.md` DRIFT-008 was marked resolved in the previous
lint run with this page recorded as having one adopter.

### Remediation

Rewrite the §"Open Questions / Drift Signals" section to reflect the
current state — compositor adopted on 2026-05-28 with one deviation
around allocation semantics. Or remove the section entirely as the
open question it tracked has closed.

Page is `llm`-owned (`tech/patterns/**` default per `meta/ownership.md`).

---

## DRIFT-012 — formatting-glitch (meta/ownership.md)

**Category**: formatting-glitch
**Severity**: low
**Subject**: `meta/ownership.md` lines 80–83

```text
- **scratch/ is human**: personal working notes. Agent reads if asked, never writes, lint never enforces — outside the schema by design.
**scratch/ is human**: personal working notes. Agent reads if
    asked, never writes, lint never enforces — outside the schema by
    design.
```

The first occurrence is a correctly-formed bullet under §"Why These
Defaults". The second occurrence (lines 81–83) is an orphan paragraph
restating the same content without a bullet marker — apparently the
remnant of a previous edit that was never fully cleaned up.

### Remediation

Delete lines 81–83. `meta/ownership.md` is **human-owned**; surfaced
here for the human to apply, the agent will not edit it.

---

## DRIFT-013 — descriptive-used_by-empty (technology stack pages)

**Category**: descriptive-used_by-empty
**Severity**: informational
**Subjects**:
- `tech/stack/mill.md` — `used_by: []`
- `tech/stack/kyo.md` — `used_by: []`
- `tech/stack/airstream.md` — `used_by: []`

The schema's `technology` page template (`meta/schema.md:127–147`)
includes `used_by: []` with the comment "maintained by lint", but the
field is only mechanically required on normative pages per `POLICY.md`.
Descriptive `tech/stack/` pages are not in any compliance contract.

However, `projects/compositor/index.md` §"Stack" lists Mill and Kyo as
in-use by the compositor project. The descriptive `used_by` field is
therefore informally populatable.

### Remediation options

1. **Leave as-is** and accept that descriptive `used_by` is best-effort.
   The compliance story is unaffected.
2. **Populate descriptive `used_by` from project index Stack sections**.
   Adds a soft cross-reference; requires defining a rule (project's
   index lists technology by id → tech/stack page's `used_by` lists
   the project).
3. **Drop `used_by` from descriptive technology pages** — amend the
   schema's template to mark the field normative-only.

Recommended: option 2 if the wiki grows past one project; option 1 for
now. No human action required to keep things clean.

---

## Compliance-Side Findings (none new)

- **Missing declaration**: none. compositor has ADRs adopting both
  accepted normative pages.
- **Dangling adoption**: none. Both adoption targets exist and remain
  `accepted`.
- **Weak rationale**: none. The compositor ADR 0001 deviation has a
  full multi-sentence rationale and a `mitigated_by` reference.
- **Conflicting adoptions**: none. `deps-single-file` and
  `functional-domain-design` are orthogonal.
- **Unused normative pages**: none. Both accepted normative pages have
  at least one adopter ADR.

---

## Out-of-Scope Reminders

- `scratch/**` continues to be excluded from all lint checks per
  `meta/ownership.md` and `meta/schema.md` §"Out-of-schema directories".
- `mill/llm-wiki/`, `kyo/llm-wiki/`, `Airstream/llm-wiki/` (Layer 3)
  are mechanically curated from upstream and not subject to Layer-2
  schema / compliance / citation rules. Their own `CLAUDE.md` files
  govern them.
- `planned` projects (webapp, cli-tool, infra) have no on-disk
  presence and are excluded from missing-declaration checks per the
  `index.md` note added in the prior remediation.

---

## Notes for Human

- **Open items**: 2 (DRIFT-011, DRIFT-013). DRIFT-009 and DRIFT-010
  were closed by the agent immediately after this lint; DRIFT-012
  was closed by the human deleting the orphan paragraph in
  `meta/ownership.md`.
- **No compliance regressions**. The remediation work from the
  previous run still holds.
- **Remaining triage**: DRIFT-011 is intentionally left open — the
  next project to land will produce an ADR addressing the page,
  closing the gap at the same time as rewriting the stale body
  section. DRIFT-013 is informational and may stay open.

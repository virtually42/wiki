# Drift Report

Mechanically computed by `lint`. Each entry is a coherence gap surfaced
to the human — entries are **not auto-fixed**. The human decides whether
to remediate, override, or accept.

**Ownership: llm** (regenerated each lint).

---

## Run Metadata

- **Run at**: 2026-05-29 (post-tagless-breakout + dm tdd-rhythm/symmetric-refactoring adoption + shapesdsl breakout + deploymentbox v2)
- **Previous run**: 2026-05-29 (post-DM-009 close-out)
- **Operation**: lint
- **Normative pages in scope** (6 accepted, 1 draft):
  - `tech/decisions/deps-single-file.md` (accepted, 2026-05-24, updated 2026-05-29)
  - `tech/decisions/tidy-first-commits.md` (**draft**, 2026-05-29) — not enforced
  - `tech/patterns/functional-domain-design.md` (accepted, 2026-05-28, updated 2026-05-29, confidence high)
  - `tech/patterns/tdd-rhythm.md` (accepted, 2026-05-29, confidence high)
  - `tech/patterns/symmetric-refactoring.md` (accepted, 2026-05-29, confidence high)
  - `tech/patterns/test-economics.md` (accepted, 2026-05-29, confidence high)
- **Projects on disk** (8): `compositor`, `sourceline-manager`, `toolbox`, `safetensors-scala`, `dependency-manager`, `tagless`, `shapesdsl`, `deploymentbox`
  (`webapp` / `cli-tool` / `infra` remain `planned`, excluded)
- **External-lib bridges in scope**: `mill`, `kyo`, `airstream`, `toml-scala`, `microvm-nix`
- **Changes since last lint**:
  - **New projects**: `tagless` (registered + 2 ADRs), `shapesdsl` (registered + 2 ADRs, **all 4 files untracked in git**), `deploymentbox` (registered + 6 ADRs + 2 designs, v1→v2 supersession)
  - **New ADRs**:
    - `projects/dependency-manager/adr/0003-adopt-tdd-rhythm.md`
    - `projects/dependency-manager/adr/0004-adopt-symmetric-refactoring.md`
    - `projects/tagless/adr/0001-adopt-functional-domain-design.md`
    - `projects/tagless/adr/0002-deviate-deps-single-file.md`
    - `projects/shapesdsl/adr/0001-adopt-functional-domain-design.md`
    - `projects/shapesdsl/adr/0002-deviate-deps-single-file.md`
    - `projects/deploymentbox/adr/000{1..6}-*.md` (six ADRs)
  - **Tech pages updated**:
    - `tech/decisions/deps-single-file.md` — `used_by` extended with `tagless/0002` (shapesdsl/0002 **not** added)
    - `tech/patterns/functional-domain-design.md` — `used_by` extended with `dm/0002` and `tagless/0001` (shapesdsl/0001 **not** added)

---

## Summary

| ID | Category | Severity | Status |
|----|----------|----------|--------|
| DRIFT-013 | descriptive-used_by-empty | informational | **open** (carryover, unchanged) |
| DRIFT-014 | source-fidelity | medium | **open — substantially mitigated** (carryover) |
| DRIFT-015 | tech-layer-tension | medium | **open — substantially mitigated** (carryover) |
| DRIFT-020 | missing-declaration | medium | **open — superseded by DRIFT-024** (scope grew with new projects + new patterns) |
| DRIFT-023 | pending-promotion | informational | ~~resolved 2026-05-29~~ — moved to historical |
| DRIFT-024 | missing-declaration | medium | **open** (new — post-promotion fan-out across 7 projects × 4 patterns) |
| DRIFT-025 | stale-index-annotation | low | ~~resolved 2026-05-29~~ — `(draft)` annotation removed from `tech/index.md` |
| DRIFT-026 | invalid-kind | low | ~~resolved 2026-05-29~~ — `kind: design-doc` → `kind: descriptive` on `dm-architecture-2026q2-refresh.md` |
| DRIFT-027 | malformed-compliance | low | ~~resolved 2026-05-29~~ — `deviations:` restructured to `{page, rationale, severity, mitigated_by}` on tagless/0002 + shapesdsl/0002 |
| DRIFT-028 | wrong-kind-adoption | medium | **open** (new — deploymentbox ADR-0006 `adopts` a `descriptive` source summary; POLICY requires `adopts` targets to be `kind: normative status: accepted`) |
| DRIFT-029 | non-schema-compliance-fields | low | **open** (new — deploymentbox ADR-0006 uses `layer:` keys instead of `page:` in `exceptions:` / `deviations:`; related to DRIFT-028) |
| DRIFT-030 | stale-page-content | low | ~~resolved 2026-05-29~~ — §Adopters / §Open Questions refreshed on FDD + tdd-rhythm + symmetric-refactoring |
| DRIFT-031 | missing-back-reference | low | ~~resolved 2026-05-29~~ — shapesdsl/0001 added to `functional-domain-design` `used_by`; shapesdsl/0002 added to `deps-single-file` `used_by` |
| DRIFT-032 | untracked-project | informational | **partially open** (index.md row already present; `git add` for three untracked paths remains) |

**Bidirectional integrity check** for the deps-single-file
sub-graph after this run:

| ADR | Status | `adopts:` / `deviations:` | listed in `used_by`? |
|---|---|---|---|
| compositor/0002 | accepted | adopts deps-single-file | ✓ |
| slm/0002 | superseded | (carried, history) | ✓ (retained) |
| slm/0006 | accepted | adopts + 1 exception | ✓ |
| toolbox/0002 | superseded | (carried, history) | ✓ (retained) |
| toolbox/0003 | accepted | adopts + 1 exception | ✓ |
| safetensors-scala/0001 | accepted | adopts + 1 exception | ✓ |
| dm/0001 | accepted | deviates | ✓ |
| tagless/0002 | accepted | deviates (malformed entry — DRIFT-027) | ✓ |
| shapesdsl/0002 | accepted | deviates (malformed entry — DRIFT-027) | ✓ (added 2026-05-29 — closed DRIFT-031) |

**functional-domain-design** sub-graph:

| ADR | Status | listed in `used_by`? |
|---|---|---|
| compositor/0001 | accepted | ✓ |
| slm/0001 | accepted | ✓ |
| toolbox/0001 | accepted | ✓ |
| dm/0002 | accepted | ✓ |
| tagless/0001 | accepted | ✓ |
| shapesdsl/0001 | accepted | ✓ (added 2026-05-29 — closed DRIFT-031) |

---

## DRIFT-013 — descriptive-used_by-empty (technology stack pages)

**Category**: descriptive-used_by-empty
**Severity**: informational (carryover, unchanged)
**Subjects**:
- `tech/stack/mill.md` — `used_by: []`
- `tech/stack/kyo.md` — `used_by: []`
- `tech/stack/airstream.md` — `used_by: []`

Descriptive `used_by` is not required by POLICY. No remediation
expected at this size; revisit when project count grows or when the
pages get refreshed.

---

## DRIFT-014 — source-fidelity (TDD Di Bello summary vs. strict Beck)

**Category**: source-fidelity
**Severity**: medium (carryover; substantially mitigated)
**Subject**: `sources/summaries/tdd_course_notes_kent_beck_pierodibello.md`

Unchanged since previous run — the `tdd-rhythm` body already carries
the post-source synthesis; the summary rewrite is optional clean-up.
See previous drift entry for full sub-finding table (14a–14f).

---

## DRIFT-015 — tech-layer-tension (TDD vs. FP posture)

**Category**: tech-layer-tension
**Severity**: medium (carryover; substantially mitigated; 15h closed)
**Subject**: `sources/summaries/tdd_course_notes_kent_beck_pierodibello.md`

Unchanged since previous run. 15h closed by `MonoidLawsSuite[A]`
landing in `sourceline-manager`. Two sub-flags (15b, 15f) remain
partly open by silence.

---

## DRIFT-020 — missing-declaration (post-promotion, compositor cells) — SUPERSEDED BY DRIFT-024

**Category**: missing-declaration
**Severity**: medium
**Status**: superseded — see DRIFT-024 for the expanded matrix.

The original DRIFT-020 framed the post-promotion fan-out across
compositor + sourceline-manager only. The current scope is 7
in-scope Scala projects × 4 newly-accepted patterns. DRIFT-024
replaces this entry with the full matrix.

The compositor cells listed in DRIFT-020 (compositor × tdd-rhythm /
symmetric-refactoring / test-economics) are still open and now
appear as rows in DRIFT-024.

---

## DRIFT-024 — missing-declaration (post-promotion fan-out) — NEW

**Category**: missing-declaration
**Severity**: medium
**Subjects**: 17 missing project-ADR / normative-page cells.

`functional-domain-design`, `tdd-rhythm`, `symmetric-refactoring`,
and `test-economics` are all `kind: normative status: accepted`
with `applies_to.languages: [scala, scala-native, scala-js]` and
`excludes: [shell-scripts, nix-modules]` (test-economics omits
`nix-modules`). Every Scala project on disk must `adopts` /
`exceptions` / `deviations` / `ignores` each pattern.

### Adoption matrix

| Project | FDD | tdd-rhythm | symmetric-ref | test-econ | deps-single-file |
|---------|-----|------------|----------------|------------|-------------------|
| compositor | ✓ 0001 | **missing** | **missing** | **missing** | ✓ 0002 |
| sourceline-manager | ✓ 0001 | ✓ 0003 | ✓ 0004 | ✓ 0005 | ✓ 0002+0006 |
| toolbox | ✓ 0001 | **missing** | **missing** | **missing** | ✓ 0002+0003 |
| safetensors-scala | **missing** | **missing** | **missing** | **missing** | ✓ 0001 |
| dependency-manager | ✓ 0002 | ✓ 0003 | ✓ 0004 | **missing** | ✓ 0001 |
| tagless | ✓ 0001 | **missing** | **missing** | **missing** | ✓ 0002 |
| shapesdsl | ✓ 0001† | **missing** | **missing** | **missing** | ✓ 0002† |

† Bidirectional integrity issue — see DRIFT-031.

**Cell count**: 17 open missing-declaration cells (3 compositor +
3 toolbox + 4 safetensors-scala + 1 dm + 3 tagless + 3 shapesdsl).

`deploymentbox` is **out of scope** for all five normative pages
above (no Scala source; falls under `excludes: [nix-modules]` for
FDD / tdd-rhythm and outside `applies_to.languages` for the
others). No missing-declaration cells for deploymentbox.

### Why this is one finding, not 17

The cells share a single root cause: four patterns went `accepted`
on 2026-05-29 and the project ADR fan-out is incomplete. Each cell
is a short adoption ADR — the work is bounded and per-project, but
the *coherence gap* is one event in the wiki.

### Remediation

Decompose by project, then by pattern. Within each project, a
single ADR can cover one pattern. Drafting guidance per cell:

- **functional-domain-design**: copy
  [[projects/toolbox/adr/0001-adopt-functional-domain-design]] as
  template; substitute the project's ADT inventory.
- **tdd-rhythm**: if the project has any test suite,
  [[projects/dependency-manager/adr/0003-adopt-tdd-rhythm]] is a
  good template (records honest exceptions for the parts not yet
  realised).
- **symmetric-refactoring**: if no operator catalogue / symmetric
  pair exists, prefer `ignores` with rationale
  ("no operator-catalogue domain; revisit when an algebra-shaped
  subsystem emerges") rather than forward-looking `adopts`.
- **test-economics**: forward-looking `adopts` is admissible
  pre-suite — `compositor` and `tagless` can adopt with a note
  that the amortisation case is aspirational pre-PBT.

ADR pages are `shared`-owned (`projects/*/adr/**`); agent may draft,
human reviews. This pass does **not** draft any of the 17 cells —
the volume and the cross-project ADR-shape calls warrant explicit
human sequencing.

### Sub-finding: stale "Open Questions" prose in pattern pages

`tdd-rhythm.md` §"Open Questions / Drift Signals" still claims
"compositor and sourceline-manager are in scope. Both lack
adoption ADRs today — expected post-promotion state, will surface
as missing-declaration on next lint." This was true at promotion
time; today sourceline-manager + dm both adopt and tagless +
shapesdsl + toolbox + safetensors-scala remain the open cells.
Same shape in `symmetric-refactoring.md`. Tracked under DRIFT-030.

---

## ~~DRIFT-025~~ — stale-index-annotation — RESOLVED 2026-05-29

**Category**: stale-index-annotation
**Severity**: low
**Status**: **resolved** 2026-05-29

`*(draft)*` annotation removed from the `test-economics` line in
`tech/index.md`. `tech/decisions/tidy-first-commits.md`
legitimately remains `draft` and keeps its `*(draft)*` annotation.

---

## ~~DRIFT-026~~ — invalid-kind — RESOLVED 2026-05-29

**Category**: invalid-kind
**Severity**: low
**Status**: **resolved** 2026-05-29

`kind: design-doc` → `kind: descriptive` on
`projects/dependency-manager/designs/dm-architecture-2026q2-refresh.md`.
All design docs on disk now use `kind: descriptive`.

---

## ~~DRIFT-027~~ — malformed-compliance — RESOLVED 2026-05-29

**Category**: malformed-compliance
**Severity**: low
**Status**: **resolved** 2026-05-29

Both `projects/tagless/adr/0002-deviate-deps-single-file.md` and
`projects/shapesdsl/adr/0002-deviate-deps-single-file.md`
`deviations:` blocks restructured to the schema shape
(`page` / `rationale` / `severity` / `mitigated_by`). Severity
`low` on both, matching the sibling `slm/0002` and `toolbox/0002`
deviations. Content lifted from existing §Context + §Decision
body sections — no new claims.

---

## DRIFT-028 — wrong-kind-adoption — NEW

**Category**: wrong-kind-adoption
**Severity**: medium
**Subject**: `projects/deploymentbox/adr/0006-adopt-paranoid-nixos-hardening.md`

```yaml
compliance:
  adopts:
    - sources/summaries/paranoid_nixos_xe_iaso.md
```

Per `POLICY.md` §"Rules": *`adopts` targets must exist and have
`kind: normative` with `status: accepted`*. The cited target is
`kind: descriptive status: accepted` — a source summary, not a
normative tech page.

The 2026-05-29 deploymentbox log entry flags this explicitly:
"First wiki ADR that explicitly adopts a sources/summaries/ page
as its `compliance:` source. Normal pattern for `compliance:` is
referencing `tech/decisions/*` or `tech/patterns/*`; we don't
have a hardening pattern yet, and the source-summary is the
closest written ground. If a `tech/patterns/defense-in-depth.md`
ever promotes from the paranoid-NixOS source, ADR-0006 should be
re-pointed."

The author is aware of the violation; the wiki currently has no
normative target to point at. Two admissible resolutions:

1. **Promote a `tech/patterns/defense-in-depth.md` or
   `tech/guides/hardened-nixos.md`** from the source summary, then
   re-point ADR-0006 at the new normative page. POLICY's promotion
   criteria (single project with clearly reusable solution **or**
   two projects) admit this with one project — deploymentbox is
   the consumer. The defense-in-depth framing is also the most
   transferable artefact identified in the summary itself.
2. **Re-shape ADR-0006 as a project-internal hardening decision**
   that *cites* the source summary in its body but does not place
   it in `compliance.adopts`. Set `compliance.adopts: []`; move
   the layer-by-layer adoption / deferral / exception material
   into the body (where most of it already lives).

Either resolution clears the policy violation. The first is
preferred if the human expects a second NixOS hardening consumer
in the foreseeable future; the second is preferred otherwise.

### Remediation

Human-gated — this is a wiki-shape question (do we want a
hardening pattern?), not a mechanical edit. Page is `shared`-owned.

---

## DRIFT-029 — non-schema-compliance-fields — NEW

**Category**: non-schema-compliance-fields
**Severity**: low
**Subject**: `projects/deploymentbox/adr/0006-adopt-paranoid-nixos-hardening.md`

The ADR's `exceptions:` and `deviations:` entries use a `layer:`
key (e.g. `layer: tailscale-only-ssh`, `layer: tmpfs-root +
impermanence`) where the schema requires `page:`. This is a
consequence of DRIFT-028: the page being "adopted" is not a
normative page, so its exceptions can't reasonably point at
sub-pages. Resolving DRIFT-028 along path #2 (above) collapses
this finding into the body rewrite; resolving along path #1
(promoting a defense-in-depth page with named sub-layers) lets
the `page:` field point at those sub-layers' anchors.

### Remediation

Closes when DRIFT-028 closes.

---

## ~~DRIFT-030~~ — stale-page-content — RESOLVED 2026-05-29

**Category**: stale-page-content
**Severity**: low
**Status**: **resolved** 2026-05-29

Three normative pattern pages refreshed:

- `tech/patterns/functional-domain-design.md` §"Adopters" — table
  expanded from 2 rows to 6 (compositor, slm, toolbox, dm, tagless,
  shapesdsl), each with a one-line shape characterisation.
  Safetensors-scala called out as the in-scope project still
  missing a stance (cross-link to DRIFT-024). Closing paragraph
  reframed around four orthogonal realisation shapes.
- `tech/patterns/tdd-rhythm.md` §"Open Questions / Drift Signals"
  first bullet — replaced "compositor and sourceline-manager are
  in scope; both lack adoption ADRs" with the current adoption
  matrix (2 adopt, 5 missing), cross-linked to DRIFT-024.
- `tech/patterns/symmetric-refactoring.md` §"Open Questions / Drift
  Signals" first bullet — same refresh, plus a new bullet noting
  the operator-layer vs parallel-module distinction surfaced by
  dm's adoption (potential future page split).

---

## ~~DRIFT-031~~ — missing-back-reference — RESOLVED 2026-05-29

**Category**: missing-back-reference
**Severity**: low
**Status**: **resolved** 2026-05-29

Both shapesdsl ADRs now back-referenced:
- `tech/patterns/functional-domain-design.md` `used_by` lists `projects/shapesdsl/adr/0001-adopt-functional-domain-design.md`.
- `tech/decisions/deps-single-file.md` `used_by` lists `projects/shapesdsl/adr/0002-deviate-deps-single-file.md`.

---

## DRIFT-032 — untracked-project — NEW

**Category**: untracked-project
**Severity**: informational
**Subjects**:
- `projects/shapesdsl/` (directory + 4 files, all untracked)
- `sources/tmp/shapesdsl.md` (untracked)
- `sources/summaries/shapesdsl.md` (untracked)

`git status` shows three untracked paths covering the shapesdsl
breakout. Also: the project does **not** appear in the top-level
`index.md` §Projects table. The breakout was performed (project
log §"Initial breakout from /p/v42/tagless" attests) but the
wiki-side integration is incomplete.

The wiki's lint compliance is on file presence, not git tracking,
so the project's ADRs are evaluated normally (and surface in
DRIFT-024 / DRIFT-031). The git-tracking and index-registration
gaps are surfaced here as informational.

### Remediation

- `git add projects/shapesdsl/ sources/summaries/shapesdsl.md sources/tmp/shapesdsl.md` (`tools/` and `sources/raw/` policy unaffected).
- Add a `shapesdsl` row to `index.md` §Projects between `tagless` and `toolbox` (alphabetical).
- Optional: stage the bridge promotion from `sources/tmp/shapesdsl.md` to `sources/raw/code/shapesdsl.md` once the `/p/hg/shapesdsl` repo lands a first commit (same shape as DM-006 promoted the dm bridge).

---

## Historical / Resolved

### DRIFT-021 — fabricated used_by (test-economics) — RESOLVED 2026-05-29
Closed by writing the real adopting ADR `slm/0005`. See previous
drift report for the closure log.

### DRIFT-022 — content-frontmatter-contradiction (test-economics) — RESOLVED 2026-05-29
Closed by rewriting `tech/patterns/test-economics.md` §Problem
paragraph. See previous drift report.

### DRIFT-023 — pending-promotion (dm bridge / DESIGN refresh / first commit) — RESOLVED 2026-05-29
Closed by the same-day commit sweep (5 commits across 4 repos)
and option-B DESIGN.md strip. See previous drift report for the
closure log. No carryover from this entry.

---

## Compliance-Side Findings

- **Missing declaration**: 17 cells — see DRIFT-024 above.
- **Dangling adoption**: 1 — see DRIFT-028 (deploymentbox/0006
  adopts a descriptive summary).
- **Weak rationale / malformed compliance**: 2 — see DRIFT-027
  (tagless/0002 + shapesdsl/0002 bare-path `deviations:`).
- **Conflicting adoptions**: none.
- **Unused normative pages**: none.
- **Fabricated `used_by`**: none — every listed ADR exists.
- **Missing back-references**: 2 — see DRIFT-031 (shapesdsl
  ADRs not back-referenced in `used_by`).
- **Schema violations**:
  - DRIFT-026 (`kind: design-doc` invalid).
  - DRIFT-029 (`layer:` keys non-schema; consequential to DRIFT-028).

---

## Intake-Side Observations (not findings)

- `sources/tmp/tdd_course_notes_kent_beck_pierodibello.md` (staged
  2026-05-29), `sources/tmp/functional_domain_modeling_zio2_debasish_ghosh.txt`
  (staged 2026-05-28), `sources/tmp/paranoid_nixos_xe_iaso.md` (staged
  2026-05-29), `sources/tmp/toolbox.md`, `sources/tmp/code/toml-scala.md`,
  `sources/tmp/code/deploymentbox.md`, `sources/tmp/shapesdsl.md`
  (untracked — see DRIFT-032), and
  `sources/tmp/github_actions_nix_cachix_dhall_gvolpe.md` all sit in
  the agreed staging area awaiting human triage per
  `feedback_ingest_staging`. No drift.
- `sources/raw/docs/TDD_HOW_TO.md` and
  `sources/raw/code/sourceline-manager.md` remain **untracked** in
  git (carryover from previous run). The wiki's compliance is on
  file presence, not git tracking; the human may want to
  `git add` both at the next commit cycle.

---

## Out-of-Scope Reminders

- `scratch/**` excluded from all lint checks per `meta/ownership.md`
  and `meta/schema.md` §"Out-of-schema directories".
- `mill/llm-wiki/`, `kyo/llm-wiki/`, `Airstream/llm-wiki/`,
  `toml-scala/llm-wiki/`, `microvm.nix/llm-wiki/` (Layer 3) are
  mechanically curated from upstream and not subject to Layer-2
  schema / compliance / citation rules.
- `planned` projects (webapp, cli-tool, infra) have no on-disk
  presence and are excluded from missing-declaration checks.
- In-tree ADRs at `/p/hg/<project>/docs/adr/` are authoritative for
  project-local decisions and excluded from wiki compliance checks;
  the wiki only mirrors *stance* on global normative pages.
- `tech/decisions/tidy-first-commits.md` remains `draft` and is not
  enforced. No project is currently obliged to address it.
- `deploymentbox` is out of scope for all five accepted normative
  pages (no Scala source; falls under `excludes: [nix-modules]` for
  FDD / tdd-rhythm and outside `applies_to.languages` for the
  others).

---

## Notes for Human

- **Open items: 6** after the second remediation pass (4 carryover
  — DRIFT-013 / 014 / 015 / 020; 2 new — DRIFT-024 / 028; plus
  consequential DRIFT-029 and informational DRIFT-032). DRIFT-020
  is superseded by DRIFT-024, so the active count is effectively
  4 + the 17-cell matrix.
- **Closed in remediation pass (2026-05-29)**: DRIFT-025 (annotation
  fix), DRIFT-026 (`kind: design-doc` fix), DRIFT-031 (shapesdsl
  back-references), DRIFT-027 (malformed `deviations:` restructure
  on tagless/0002 + shapesdsl/0002), DRIFT-030 (stale prose refresh
  on FDD + tdd-rhythm + symmetric-refactoring).
- **What this run did**:
  - Inventoried 8 on-disk projects + 6 accepted normative pages
    (deps-single-file + 4 patterns).
  - Verified bidirectional integrity on the deps-single-file +
    functional-domain-design `used_by` graphs (8 + 6 cells
    respectively).
  - Identified the post-promotion fan-out gap (DRIFT-024, 17
    cells) covering 5 projects × 3 patterns + safetensors-scala ×
    functional-domain-design + dm × test-economics.
  - Identified four new low-severity schema / content drifts
    (DRIFT-025 / 026 / 027 / 030).
  - Identified one medium new finding (DRIFT-028) for the
    paranoid-NixOS adoption pointing at a descriptive source.
  - Identified one informational integration drift (DRIFT-032)
    for the partially-integrated shapesdsl breakout.
- **What needs human input**:
  - **DRIFT-024 (17-cell ADR fan-out)**: bulk drafting decision —
    do we batch by project (one session per project drafting all
    pattern stances) or by pattern (one session per pattern
    drafting all project stances)? Recommendation: by project,
    since each project's stance is usually consistent across the
    three patterns (adopt / ignore / forward-look).
  - **DRIFT-028 path choice**: promote a `tech/patterns/defense-in-depth.md`
    from the paranoid-NixOS summary (path 1) or rewrite ADR-0006
    body-only (path 2)? The promotion-from-one-project criterion
    in POLICY admits path 1; the answer depends on whether a
    second NixOS hardening consumer is expected.
  - **DRIFT-032 git-tracking**: `git add` the three untracked
    shapesdsl paths and append a `shapesdsl` row to `index.md`.
- **Mechanical fixes still pending**: none. All remaining open
  items are human-gated (DRIFT-024 ADR drafting, DRIFT-028
  wiki-shape question, DRIFT-032 `git add`) or carryover by
  design (DRIFT-013 / 014 / 015).
- **Stays open by design**: DRIFT-013 (informational, descriptive).
- **No DRIFT-023-style sequenced human-gated work** introduced
  this run.

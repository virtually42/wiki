# Drift Report

Mechanically computed by `lint`. Each entry is a coherence gap surfaced
to the human — entries are **not auto-fixed**. The human decides whether
to remediate, override, or accept.

**Ownership: llm** (regenerated each lint).

---

## Run Metadata

- **Run at**: 2026-05-29 (post-dependency-manager MVP plan execution — DM-001..DM-004, DM-007 draft, DM-008, DM-009)
- **Previous run**: 2026-05-29 (post-sourceline-manager ADR drafting pass + DRIFT-021/022 closure)
- **Operation**: lint (DM-009)
- **Normative pages in scope** (5 accepted, 1 draft):
  - `tech/decisions/deps-single-file.md` (accepted, 2026-05-24, updated 2026-05-29)
  - `tech/decisions/tidy-first-commits.md` (**draft**, 2026-05-29) — not enforced
  - `tech/patterns/functional-domain-design.md` (accepted, 2026-05-28)
  - `tech/patterns/tdd-rhythm.md` (accepted, 2026-05-29, confidence high)
  - `tech/patterns/symmetric-refactoring.md` (accepted, 2026-05-29, confidence high)
  - `tech/patterns/test-economics.md` (accepted, 2026-05-29, confidence high)
- **Projects on disk**: `compositor`, `sourceline-manager`, `toolbox`, `safetensors-scala`, `dependency-manager`
  (`webapp` / `cli-tool` / `infra` remain `planned`, excluded)
- **External-lib bridges in scope**: `mill`, `kyo`, `airstream`
- **Changes since last lint**:
  - `projects/toolbox/adr/0003-adopt-deps-single-file.md` — new (DM-008)
  - `projects/toolbox/adr/0002-deviate-deps-single-file.md` — marked `superseded` (DM-008)
  - `projects/sourceline-manager/adr/0006-adopt-deps-single-file.md` — new (DM-008)
  - `projects/sourceline-manager/adr/0002-deviate-deps-single-file.md` — marked `superseded` (DM-008)
  - `projects/safetensors-scala/adr/0001-adopt-deps-single-file.md` — new (DM-008; first wiki ADR for this project)
  - `tech/decisions/deps-single-file.md`:
    - `used_by` extended with 3 new ADRs
    - §"Mill 1.x discovery pre-requisite" added (DM-004)
  - `projects/dependency-manager/designs/dm-architecture-2026q2-refresh.md` — new (DM-007 wiki-side draft)
  - `projects/toolbox/index.md` — §"Embedding Path" rewritten; §"ADRs" updated
  - `projects/sourceline-manager/index.md` — §"ADRs" updated
  - `projects/safetensors-scala/index.md` — §"ADRs" reworked from "none" to list the new ADR
  - `projects/dependency-manager/index.md` — §"Current Blockers" + §"Tickets" + §"Designs" refreshed

---

## Summary

| ID | Category | Severity | Status |
|----|----------|----------|--------|
| DRIFT-013 | descriptive-used_by-empty | informational | **open** (carryover, unchanged) |
| DRIFT-014 | source-fidelity | medium | **open — substantially mitigated** by `tdd-rhythm` body (carryover) |
| DRIFT-015 | tech-layer-tension | medium | **open — substantially mitigated** by `tdd-rhythm` body; 15h closed (carryover) |
| DRIFT-020 | missing-declaration | medium | **open — half-resolved**: 3 of 6 cells closed (sourceline-manager); 3 compositor cells remain open (unchanged this run) |
| DRIFT-021 | fabricated-used_by | low | **resolved** 2026-05-29 — superseded by real adopting ADR |
| DRIFT-022 | content-frontmatter-contradiction | low | **resolved** 2026-05-29 — paragraph rewrite |
| DRIFT-023 | pending-promotion | informational | **resolved** 2026-05-29 — DM-005 (`5459ddb`), DM-006 (bridge promoted), DM-007 (`3482be3`, option B applied) all closed |

**Compliance side**: clean on adoption rules. The
deps-single-file decision now has **6 wiki ADRs** in `used_by`
(compositor adopts, slm deviate→superseded + adopt, toolbox
deviate→superseded + adopt, safetensors-scala adopt,
dependency-manager deviate). All three new adopt-ADRs share
the same exception template (platforms-only, severity `low`,
cross-linking the dm open question).

**Bidirectional integrity check** for the deps-single-file
sub-graph after DM-008:

| ADR | Status | `adopts:` / `deviations:` | listed in `used_by`? |
|---|---|---|---|
| compositor/0002 | accepted | adopts deps-single-file | ✓ |
| slm/0002 | superseded | (carried, history) | ✓ (retained) |
| slm/0006 | accepted | adopts + 1 exception | ✓ |
| toolbox/0002 | superseded | (carried, history) | ✓ (retained) |
| toolbox/0003 | accepted | adopts + 1 exception | ✓ |
| safetensors-scala/0001 | accepted | adopts + 1 exception | ✓ |
| dm/0001 | accepted | deviates (bootstrap chicken-and-egg) | ✓ |

No dangling adopts; no fabricated `used_by`; supersession chain
is explicit (each superseded ADR carries `superseded_by:`).

**Resolved this run (DM-009)**: none of the carryover items
closed; one new informational entry (DRIFT-023) opened to track
the human-gated DM-005 / DM-006 sequence.

**Pre-MVP completion gates** (DRIFT-023):

| Gate | Owner | Blocks |
|---|---|---|
| DM-005 first commit | human | DM-006 (needs SHA) |
| DM-006 bridge promotion | agent (post-DM-005) | wiki link rewrite, frontmatter `commit:` field |
| DM-007 in-tree DESIGN.md apply | human | wiki mirror re-ingest |

None of these are coherence violations under POLICY — they are
sequenced gates with explicit ownership. The lint flags them
once for visibility and closes when the gating action completes.

---

## DRIFT-013 — descriptive-used_by-empty (technology stack pages)

**Category**: descriptive-used_by-empty
**Severity**: informational (carryover, unchanged)
**Subjects**:
- `tech/stack/mill.md` — `used_by: []`
- `tech/stack/kyo.md` — `used_by: []`
- `tech/stack/airstream.md` — `used_by: []`

`projects/compositor/index.md` §Stack lists Mill and Kyo;
`projects/sourceline-manager/index.md` §Stack lists Mill. Descriptive
`used_by` is not required by POLICY but remains informationally empty
on these pages.

No remediation expected at this size; revisit when project count grows.

---

## DRIFT-014 — source-fidelity (TDD Di Bello summary vs. strict Beck)

**Category**: source-fidelity
**Severity**: medium (carryover; substantially mitigated)
**Subject**: `sources/summaries/tdd_course_notes_kent_beck_pierodibello.md`

Status table (unchanged since previous run):

| Sub-finding | Status after `tdd-rhythm` body |
|-------------|--------------------------------|
| 14a — *TDD as if you meant it* misattributed | **Addressed in `tdd-rhythm` body**: Braithwaite's variant split out as a related-but-distinct pattern. |
| 14b — private-method scaffolding not Beck | Open in summary; `tdd-rhythm` silent on private-method tests (consistent with Beck-strict). |
| 14c — end-to-end-first overgeneralised | Open in summary; `tdd-rhythm` Stage 0 + Stage 1 prefer inside-out. |
| 14d — Triangulation + Obvious Implementation absent | **Addressed in `tdd-rhythm` body**: all three green-strategies enumerated. |
| 14e — Beck-vs-Mancuso peers framing | **Addressed in `tdd-rhythm` body**: Chicago vs London split called out; Mancuso/mocks framed as out of scope per `devtools:tdd`. |
| 14f — *Test Desiderata* underused | **Addressed in `tdd-rhythm` body**: Beck's *Test Desiderata* enumerated explicitly. |

### Remediation

Edit `sources/summaries/tdd_course_notes_kent_beck_pierodibello.md`
in place (page is `llm`-owned). The `tdd-rhythm` body already carries
the post-source synthesis; the summary rewrite is now optional
clean-up rather than load-bearing. Acceptable to defer.

---

## DRIFT-015 — tech-layer-tension (TDD vs. FP posture)

**Category**: tech-layer-tension
**Severity**: medium (carryover; substantially mitigated; 15h closed)
**Subject**: `sources/summaries/tdd_course_notes_kent_beck_pierodibello.md`

Status table (unchanged since previous run):

| Sub-finding | Status |
|-------------|--------|
| 15a — OO refactoring vocabulary | Partly mitigated: `tdd-rhythm` body adds FP-stack vocabulary as peer. |
| 15b — deterministic isolation a non-problem under purity | Open in summary; `tdd-rhythm` silent. |
| 15c — design-during-refactor without type-first | **Addressed**: `tdd-rhythm` Stage 0 prepends type/algebra-first. |
| 15d — Fake It vs type-driven derivation | Partly mitigated by green-strategies enumeration. |
| 15e — mocks vs fakes-over-mocks | **Addressed**: London/Chicago split called out. |
| 15f — private-method encapsulation | Partly mitigated by silence (Beck-strict alignment). |
| 15g — error handling at type level | **Addressed**: cross-linked to `functional-domain-design`. |
| 15h — property-based / law-based testing missing | **Closed 2026-05-29** by `MonoidLawsSuite[A]` landing in `sourceline-manager`. |

### Remediation

Same disposition as DRIFT-014: the summary rewrite is now optional
clean-up. Two sub-flags (15b, 15f) remain partly open by silence.

---

## DRIFT-020 — missing-declaration (post-promotion, three accepted patterns) — HALF-RESOLVED 2026-05-29

**Category**: missing-declaration
**Severity**: medium
**Status**: 3 of 6 cells closed; 3 compositor cells open.

| Project | Normative page | ADR status |
|---------|----------------|------------|
| compositor | `tech/patterns/tdd-rhythm.md` | **open** |
| compositor | `tech/patterns/symmetric-refactoring.md` | **open** |
| compositor | `tech/patterns/test-economics.md` | **open** |
| sourceline-manager | `tech/patterns/tdd-rhythm.md` | **resolved** — `adr/0003-adopt-tdd-rhythm.md` |
| sourceline-manager | `tech/patterns/symmetric-refactoring.md` | **resolved** — `adr/0004-adopt-symmetric-refactoring.md` |
| sourceline-manager | `tech/patterns/test-economics.md` | **resolved** — `adr/0005-adopt-test-economics.md` |

The sourceline-manager half was drafted in one pass on 2026-05-29
from the synthesis evidence. All three ADRs adopt unconditionally
(no exceptions / deviations), reflecting that the synthesis is
direct, in-repo, and confidence-high on each pattern.

### Remediation (remainder)

- **compositor × `tdd-rhythm`**: forward-looking `adopts`
  recommended. Compositor's [[projects/compositor/designs/input-pipeline]]
  is already a Stage 0 (pure
  `(Event, State) => (Event, State)` stages with property-tested
  core) + Stage 2 (laws planned) example. ADR shape: same as
  [[projects/compositor/adr/0002-adopt-deps-single-file]].
- **compositor × `symmetric-refactoring`**: less direct fit. The
  current design has no operator catalogue at the same density as
  sourceline-manager. Two admissible options:
  - `ignores` with rationale "no operator-catalogue domain in the
    current design; revisit when an algebra-shaped subsystem emerges".
  - Forward-looking `adopts` constraining future API design to follow
    the pattern when an algebra surfaces.
- **compositor × `test-economics`**: forward-looking, either
  `adopts` (with a note that the amortisation case is aspirational
  pre-code) or `ignores` (with rationale "no test corpus to
  amortise yet; revisit on first stable test suite").

Page is `shared`-owned (`projects/*/adr/**`). Agent may draft, human
reviews. The compositor side is *not* drafted in this pass — without
code on disk, the calls are more design-loaded than the
sourceline-manager side was and warrant explicit human input.

---

## ~~DRIFT-021~~ — fabricated used_by (test-economics) — RESOLVED 2026-05-29

**Category**: fabricated-used_by
**Severity**: low
**Status**: **resolved** 2026-05-29

Closed via option 2 (write the real adopting ADR rather than clear
the field):
[[projects/sourceline-manager/adr/0005-adopt-test-economics]] adopts
`tech/patterns/test-economics.md` unconditionally. The
`tech/patterns/test-economics.md` frontmatter `used_by` now lists
`projects/sourceline-manager/adr/0005-adopt-test-economics.md`, which
traces to a real `adopts:` entry. §Adopters table row updated
correspondingly — the parenthetical "(carrier)" is gone.

---

## ~~DRIFT-023~~ — pending-promotion (dm bridge / DESIGN refresh / first commit) — RESOLVED 2026-05-29

**Category**: pending-promotion
**Severity**: informational
**Status**: **resolved** 2026-05-29 — all three sub-findings closed in a single session.

**Closure log (2026-05-29):**
- Sub-finding #1 (DM-005): human approved agent-on-behalf commit. First commit `5459ddb7dc4ceb882ea89b2054e5814b9383f313` on branch `main` (renamed from `master` post-commit), unsigned, no Co-Authored-By, author `tigidar`.
- Sub-finding #2 (DM-006): bridge promoted to `sources/raw/code/dependency-manager.md` with the SHA in `commit:` field. 7 live wiki references rewritten. `sources/tmp/code/dependency-manager.md` removed. Body refreshed to reflect post-v1 reality.
- Sub-finding #3 (DM-007): human chose **option B** (strip DESIGN.md to decisions + open questions) rather than the original four-block in-place rewrite. Agent executed on behalf; commit `3482be3` ("docs: strip DESIGN.md to decisions archive (option B)"). Wiki mirror at `projects/dependency-manager/designs/dm-architecture.md` refreshed to match; the transitional draft `dm-architecture-2026q2-refresh.md` marked `status: superseded` with a banner.

**Adjacent commits the same session** (not strictly part of DRIFT-023 but bundled with the same approval): three other /p/hg repos with pending DM-001/DM-002 work were also committed on behalf:
- `/p/hg/safetensors-scala@a8a60e8`: DM-002 migration + ADR-0002 supersession of in-tree ADR-0001; branch renamed `master` → `main`.
- `/p/hg/sourceline-manager@e21a58d, b22cb55`: laws+primitives (e21a58d) and DM-001 catalog adoption (b22cb55) split into two commits per atomic-feature convention.
- `/p/hg/toolbox@2b2a828`: initial v1 commit (102 files, 16640 insertions) bundling the entire v1 surface plus the DM-001 migration since the repo had zero prior commits.

The dependency-manager MVP plan
([[projects/dependency-manager/plans/mvp]]) sequences three
gates that the agent cannot execute unilaterally:

1. **DM-005** — first git commit in `/p/hg/dependency-manager`.
   Personal-repo policy
   ([[feedback_hg_repo_commit_policy]]) puts this on the human.
   `.git/` already exists (branch `master`, 0 commits); staging
   list and proposed subject prepared (see
   [[projects/dependency-manager/tickets/0005-git-init-first-commit]]).
2. **DM-006** — promote
   `sources/tmp/code/dependency-manager.md` to
   `sources/raw/code/dependency-manager.md` with the real SHA
   from DM-005. Blocked on DM-005.
3. **DM-007** — apply the wiki-side draft at
   [[projects/dependency-manager/designs/dm-architecture-2026q2-refresh]]
   to `/p/hg/dependency-manager/DESIGN.md` (in-tree; human-owned).
   On confirmation, the agent re-ingests the wiki mirror.

### Why this is informational

- DM-005 is *not* a missing-declaration drift; it is a
  scheduled action with explicit ownership.
- DM-006 is *not* a broken-link drift; the 10 wiki references
  to `sources/tmp/code/dependency-manager` are correct
  (they point to a file that exists in the staging area).
  They become wrong only after DM-006 promotes the file and
  removes the tmp copy.
- DM-007 is *not* a content-drift; the wiki-side
  `designs/dm-architecture.md` mirror still reflects the
  in-tree DESIGN.md as ingested. It becomes stale only after
  the human applies the refresh in-tree (at which point the
  agent re-ingests on the next pass).

### Remediation

Sequential, by ownership:

- Human: trigger DM-005 commit.
- Agent: execute DM-006 (promote bridge, sweep `[[sources/tmp/...]]`
  → `[[sources/raw/...]]` across the 10 referring files,
  remove the tmp copy, update the bridge `commit:` field).
- Human: apply DM-007 in-tree.
- Agent: re-ingest
  `projects/dependency-manager/designs/dm-architecture.md` from
  the refreshed in-tree DESIGN.md.

Each step closes a sub-finding of DRIFT-023; the entry as a
whole closes when all three are complete. The MVP plan
([[projects/dependency-manager/plans/mvp]]) flips to
`status: completed` at the same time.

---

## ~~DRIFT-022~~ — content-frontmatter-contradiction (test-economics) — RESOLVED 2026-05-29

**Category**: content-frontmatter-contradiction
**Severity**: low
**Status**: **resolved** 2026-05-29

`tech/patterns/test-economics.md` §Problem paragraph rewritten. The
"draft / needs second source" framing was replaced with a sentence
stating the page was promoted to `accepted` (`confidence: high`) on
2026-05-29, citing
[[projects/sourceline-manager/syntheses/monoid-laws-as-pbt-evidence]]
§"Status Update — 2026-05-29 (post-primitives + StringUtils
composition)" as the second source / project synthesis that
satisfied the second-source requirement via realised evidence.

---

## Compliance-Side Findings

- **Missing declaration**: see DRIFT-020 above. **3** missing ADRs
  remain (all compositor-side).
- **Dangling adoption**: none. All ADR `adopts` / `deviations`
  targets exist with `kind: normative`, `status: accepted`.
- **Weak rationale**: none.
  - compositor ADR-0001 (functional-domain-design deviation):
    multi-sentence rationale, severity `low`, `mitigated_by` cites
    `projects/compositor/designs/input-pipeline.md`.
  - sourceline-manager ADR-0002 (deps-single-file deviation):
    multi-paragraph rationale naming the two trigger conditions for
    deviation expiry, severity `low`, `mitigated_by` cites the
    upstream README's embedding section.
  - sourceline-manager ADR-0003 / 0004 / 0005 (this pass): all
    unconditional adoptions with `Context` / `Decision` / `Consequences`
    / `Alternatives Considered` sections. No deviations to rationalise.
- **Conflicting adoptions**: none.
- **Unused normative pages**: none. All five accepted normative
  pages have at least one adopter; new this run:
  - `tech/patterns/tdd-rhythm.md` — 1 adopter (sourceline-manager)
  - `tech/patterns/symmetric-refactoring.md` — 1 adopter
  - `tech/patterns/test-economics.md` — 1 real adopter (was
    fabricated; DRIFT-021 closed)
- **Fabricated `used_by`**: none. DRIFT-021's entry was superseded
  by a real ADR.

---

## Intake-Side Observations (not findings)

- `sources/tmp/tdd_course_notes_kent_beck_pierodibello.md` (staged
  2026-05-29) and
  `sources/tmp/functional_domain_modeling_zio2_debasish_ghosh.txt`
  (staged 2026-05-28) sit in the agreed staging area awaiting human
  triage per `feedback_ingest_staging`. Both summaries derived from
  them are accepted in `sources/summaries/`. No drift.
- `sources/raw/docs/TDD_HOW_TO.md` and
  `sources/raw/code/sourceline-manager.md` remain **untracked** in
  git. The wiki's compliance is on file presence, not git tracking;
  the human may want to `git add` both at the next commit cycle.

---

## Out-of-Scope Reminders

- `scratch/**` excluded from all lint checks per `meta/ownership.md`
  and `meta/schema.md` §"Out-of-schema directories".
- `mill/llm-wiki/`, `kyo/llm-wiki/`, `Airstream/llm-wiki/` (Layer 3)
  are mechanically curated from upstream and not subject to Layer-2
  schema / compliance / citation rules.
- `planned` projects (webapp, cli-tool, infra) have no on-disk
  presence and are excluded from missing-declaration checks.
- In-tree ADRs at `/p/hg/sourceline-manager/docs/adr/` are
  authoritative for project-local decisions and excluded from wiki
  compliance checks; the wiki only mirrors *stance* on global
  normative pages.
- `tech/decisions/tidy-first-commits.md` remains `draft` and is not
  enforced. No project is currently obliged to address it.

---

## Notes for Human

- **Open items: 5** (DRIFT-013 informational; DRIFT-014 + DRIFT-015
  substantially mitigated; DRIFT-020 down to 3 compositor cells;
  DRIFT-023 informational / open-by-design). Zero new compliance
  violations introduced by the DM-001..DM-009 pass.
- **What this run (DM-009) did**:
  - Surfaced the new dependency-manager / toolbox /
    safetensors-scala ADRs in scope and verified `used_by`
    bidirectional integrity on `deps-single-file`.
  - Confirmed the deps-single-file decision-page §"Mill 1.x
    discovery pre-requisite" cross-link landed (DM-004).
  - Marked DRIFT-023 as new informational entry capturing the
    three human-gated gates (DM-005 commit, DM-006 bridge
    promotion, DM-007 in-tree apply) — none of which is a true
    coherence violation under POLICY.
  - Updated `projects/dependency-manager/index.md` §"Current
    Blockers" + §"Tickets" + §"Designs" to reflect the closed
    tickets and the new DESIGN refresh draft.
- **What still needs human input**:
  - **Compositor × 3 ADRs**: unchanged from previous run; see
    DRIFT-020 remediation.
  - **Promotion call on [[tech/decisions/tidy-first-commits]]**:
    unchanged from previous run.
  - **DM-005 first commit** in `/p/hg/dependency-manager` (per
    DRIFT-023). Agent prep complete; staging list and proposed
    subject in [[projects/dependency-manager/tickets/0005-git-init-first-commit]].
  - **DM-007 in-tree apply** — wiki-side draft at
    [[projects/dependency-manager/designs/dm-architecture-2026q2-refresh]]
    ready for human to apply against
    `/p/hg/dependency-manager/DESIGN.md`.
  - Optional: in-tree rewrite of
    `/p/hg/safetensors-scala/docs/adr/0001-inline-versions.md`
    to reflect post-DM-002 state (the wiki ADR is sufficient
    for the normative surface).
- **Stays open by design**: DRIFT-013 (informational,
  descriptive); DRIFT-023 (sequenced human-gated work).
- **No compliance regressions** introduced by the DM-001..DM-009
  pass. The deps-single-file `used_by` graph is bidirectionally
  consistent: every listed ADR exists, every ADR `adopts:` or
  `deviations:` entry points to a normative page that lists it.

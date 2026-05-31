---
id: wip-conform-foundation
title: "WIP — `conform` operation foundation"
kind: session
status: active
project: null
created: 2026-05-30
updated: 2026-05-30
branch: main
related:
  - tech/guides/conformance.md
  - meta/drift.md
---

## Goal

Lay the foundation for a new wiki operation `conform` that
evidence-checks projects against normative patterns (FDD,
tdd-rhythm, symmetric-refactoring, test-economics,
deps-single-file) using declared fingerprints. The operation is
the long-term answer to [[meta/drift]] §DRIFT-024 — the 17-cell
project × pattern fan-out backlog. Foundations first;
visualization deferred to a later stage.

## Status

Stage 0 (foundation) complete. Stage 1 (validation case: FDD ×
toolbox) not yet started; all prerequisites for it are in place.
Two human-gated steps before Stage 1 can run: (a) the schema /
ownership fix script needs to be executed (or rejected), (b) the
shared `CLAUDE.md` edit and the FDD `## Conformance` block need
a review pass.

## Files Touched

**Uncommitted, new:**
- `tech/guides/conformance.md` — full operation spec
  (8-phase procedure, conformance block schema, output format,
  sequencing strategy, anti-patterns). llm-owned page,
  `kind: descriptive status: draft`.
- `fix/apply-conformance-schema.py` — idempotent fix script
  proposing additions to `meta/schema.md` (§Conformance Block) and
  `meta/ownership.md` (`meta/conformance.md` row + `projects/*/adr/drafts/**`
  row + matching rationale paragraphs).

**Uncommitted, modified:**
- `CLAUDE.md` — `conform` registered in §Knowledge Operations
  between `lint` and `synthesize`. **Shared-owned edit, flag for
  review.**
- `tech/patterns/functional-domain-design.md` — `## Conformance`
  block added before §Open Questions. verifiability: medium; 4 hard
  signals (no-var-in-domain, adt-encoding-present,
  composable-operators-present, no-runtime-effects-in-algebra) +
  2 soft signals (describes-not-does, interpreter-separation) +
  classification rubric + adr_template.
- `meta/log.md` — top-level entry recording the foundation
  session, sequencing plan, and human-gated items.

**Pre-existing modifications (from prior sessions, not touched
this session):**
- `meta/drift.md`, `projects/shapesdsl/adr/0002-deviate-deps-single-file.md`,
  `projects/tagless/adr/0002-deviate-deps-single-file.md`,
  `tech/patterns/{tdd-rhythm,symmetric-refactoring}.md` —
  prior drift remediation work; unrelated to this session.
- `sources/tmp/animdsl.md` — untracked, prior ingest staging.

## Decisions

- **Evidence-based, not assertion-based.** Flip the wiki's
  compliance epistemology. ADRs become summaries of mechanical
  findings + soft-signal judgement, not human declarations.
- **Hybrid signals.** Each normative page declares `hard_signals`
  (grep / ast / metric / shell) and `soft_signals` (LLM-evaluated
  prompts). Hard signals run as scripts; soft signals run as agent
  evaluations against pre-loaded file context.
- **Inline-first fingerprint storage.** grep + metric checks live
  inline in the page (YAML). ast checks reference Scalafix rule
  names; shell checks reference scripts under
  `tools/conformance/<pattern-id>/` (human-owned per existing
  ownership policy).
- **Verifiability is honest.** A pattern that can't be mechanised
  (process-not-artifact like `tdd-rhythm`) rates `low`, not faked
  `high`. Output is "unclear" rather than confidently-wrong.
- **Drafts go to `projects/*/adr/drafts/`.** New llm-owned
  sub-tree. Humans review and move accepted drafts to
  `projects/*/adr/` where ownership becomes shared.
- **Foundations before visualization.** Operator explicitly
  chose this sequencing. Stage 5 is the TUI / web view; everything
  before is data shape and operation correctness.
- **FDD chosen as the first proof-of-concept.** Highest-applicability
  pattern; `verifiability: medium` exercises both signal kinds.
  Toolbox chosen as Stage 1 target because its existing
  `0001-adopt-functional-domain-design.md` is the canonical
  unconditional adoption (known-good baseline).

## Blockers

None blocking the work itself. Two human-gated steps before Stage 1:

1. **Run or reject `fix/apply-conformance-schema.py`.** The script
   is idempotent. Without it, `meta/schema.md` doesn't formally
   carry the `## Conformance` block spec, and `meta/ownership.md`
   doesn't carry the rows for `meta/conformance.md` /
   `projects/*/adr/drafts/**`. Stage 1 can technically run without
   these (the guide carries the spec inline), but lint will
   eventually flag the gap.
2. **Review pass** on `CLAUDE.md` and the FDD `## Conformance`
   block. Especially: are the hard-signal glob scopes
   (`src/main/scala/**/{domain,model,algebra}/**.scala`)
   appropriate across the project shapes (toolbox uses 10 modules,
   tagless uses 14, etc.)? May need per-project scope override.

## Next Step

Start Stage 1: run the FDD fingerprint by hand (in-context, no
automation yet) against `/p/hg/toolbox` and verify the output
matches the existing
`projects/toolbox/adr/0001-adopt-functional-domain-design.md`.

Concretely:
1. Read [[tech/patterns/functional-domain-design]] §Conformance.
2. For each hard signal: run the grep against `/p/hg/toolbox` and
   collect evidence (file:line pairs, counts).
3. For each soft signal: read the relevant files and produce the
   verdict + citations.
4. Apply the classification rubric to derive a stance.
5. Compare with `projects/toolbox/adr/0001-adopt-functional-domain-design.md`
   §compliance and §body.
6. Outcomes: **match** → log "Stage 1 validated, FDD fingerprint
   sound on toolbox"; **mismatch** → adjust either the fingerprint
   (signals too broad / too narrow) or surface a real ADR drift.

## Resume Instructions

1. Read [[tech/guides/conformance]] (the operation spec) end to
   end — it's the canonical reference for everything below.
2. Read [[tech/patterns/functional-domain-design]] §Conformance —
   the first fingerprint, the one Stage 1 validates.
3. Read [[meta/drift]] §DRIFT-024 — the backlog this operation
   retires.
4. Read [[projects/toolbox]] index + ADR-0001 to anchor the
   validation case.
5. Check whether the human has run
   `python3 fix/apply-conformance-schema.py` — if yes,
   `meta/schema.md` and `meta/ownership.md` will already carry
   the additions; if no, decide whether to proceed without them
   for Stage 1 (admissible — the spec is in the guide) or wait.
6. Begin Stage 1 per §Next Step.

If the human asks to **change direction** instead of resuming Stage
1 — e.g. start with `deps-single-file` (Stage 2) or skip straight
to the visualization (Stage 5) — both are admissible but should
re-read the §Sequencing Strategy in the guide first to understand
what gets skipped.

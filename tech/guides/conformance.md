---
id: guide-conformance
title: "Conformance — evidence-checking projects against normative patterns"
kind: descriptive
status: draft
scope: global
created: 2026-05-30
updated: 2026-05-30
tags: [conformance, compliance, fingerprint, evidence, automation, drift]
ownership: shared
ownership_reason: procedure definition — human reviews shape, agent executes
sources:
  - meta/drift.md
  - POLICY.md
  - meta/schema.md
---

## Purpose

Flip the wiki's normative compliance from **assertion-based** ("a human
writes an ADR claiming the project follows pattern X") to
**evidence-based** ("the code is inspected; an ADR draft is derived").

The `conform` operation runs declared *fingerprints* — small checks
attached to each normative `tech/patterns/*` or `tech/decisions/*` page
— against a project's source tree and produces:

1. A **stance recommendation** (`adopts` / `adopts + exceptions` /
   `deviates` / `ignores`) with cited evidence.
2. A **draft ADR** mirroring the existing `compliance:` schema.
3. A **regression report** when re-run: where the code has drifted
   from a previously declared stance.

This is the long-term answer to [[meta/drift]] §DRIFT-024
(the 17-cell project × pattern fan-out). Manual ADR fan-out scales
poorly and is the wrong abstraction once normative pages outnumber
projects.

## When to Use

- After a normative page is promoted from `draft` to `accepted`, to
  fan out adoption ADRs across in-scope projects mechanically.
- Periodically (e.g. each `lint` pass) to detect **code-level**
  regressions where a project's source has drifted from its declared
  ADR stance.
- When a new project is registered, to seed its first adoption ADRs
  without hand-drafting.
- When a pattern's body changes substantively, to re-evaluate every
  project's stance against the updated fingerprint.

## When Not to Use

- For patterns whose conformance block declares `verifiability: low`
  without a meaningful soft-signal section — the operation runs but
  the output is "unclear" everywhere and adds noise.
- During the *first* adoption of a pattern by a single project —
  hand-drafted ADRs are still the right shape when a human is
  actively shaping the project's stance. `conform` is for fan-out
  and regression, not initial articulation.
- Against `descriptive` pages (`tech/stack/`, `tech/guides/`, etc.).
  Only normative pages declare conformance blocks.

## Inputs

The human or upstream `lint` provides:

1. **Project** — `projects/<name>/` (must exist on disk; resolved
   via `projects/<name>/index.md` frontmatter, which carries the
   source path).
2. **Pattern** (optional) — `tech/patterns/<id>.md` or
   `tech/decisions/<id>.md`. If omitted, conform runs every
   in-scope normative page against the project.
3. **Mode** (optional) — `fresh` (treat existing ADRs as informational,
   draft full new stances) or `diff` (only surface deltas from existing
   ADRs). Default: `diff` on re-runs, `fresh` on first run.

## Procedure: `conform [<project>] [<pattern>]`

### Phase 1 — Discover

1. Resolve project root from `projects/<name>/index.md` (the project's
   on-disk source location, e.g. `/p/hg/<name>`).
2. Read the project's stack declaration from its index frontmatter —
   languages, build system, test framework — to determine *which*
   normative pages it is in-scope for (via `applies_to` and `excludes`
   per [[POLICY]]).
3. List the project's existing ADRs and parse their `compliance:`
   blocks. These are the "declared stance" baseline.

### Phase 2 — Load fingerprints

For each in-scope normative page:

1. Parse the `## Conformance` section per the schema below.
2. Group checks into hard signals (executable now) and soft signals
   (queued for LLM evaluation).
3. Skip the page entirely if it declares `verifiability: low` AND has
   no soft signals — produce one row in the report flagging "no
   fingerprint" and move on.

### Phase 3 — Execute hard signals

For each hard signal, in order:

1. Resolve the signal's `scope:` glob relative to the project root.
2. Execute the signal's `method:` (grep / ast / metric / shell).
3. Collect evidence: file paths, line numbers, counter-examples,
   numeric measures.
4. Cap evidence per signal at a sane noise floor (default: first 20
   matches; first 5 file paths; full numeric measures). Excess goes
   into a `truncated: true` flag with the total count.

### Phase 4 — Execute soft signals

For each soft signal:

1. Pre-load context: the project's domain-layer source files (or
   whatever the signal's `scope:` declares).
2. Issue the signal's `prompt:` to the LLM, instructing it to return
   one of the declared `verdict_kinds:` plus citations (file + line).
3. Record the verdict + citations as evidence.

Soft signals are honest about uncertainty: an `unclear` verdict is a
first-class outcome, not a failure.

### Phase 5 — Classify

Apply the pattern's `classification:` rubric to the collected evidence
to derive a stance:

- **adopts** — hard signals pass; soft signals lean positive.
- **adopts + exceptions** — pass with localized counter-examples;
  exceptions list the specific spots.
- **deviates** — the project consistently uses a different shape;
  evidence supports the alternative.
- **ignores** — pattern is out of scope for the project (e.g.
  shell-only project under `excludes: [shell-scripts]`).

Each cell carries a **confidence score** (`high` / `medium` / `low`)
derived from: hard-signal coverage, soft-signal certainty, and the
pattern's overall `verifiability:` rating.

### Phase 6 — Diff against existing ADR (if any)

- If no existing ADR: stance is **new**. Phase 7 drafts one.
- If existing ADR matches the derived stance: log **confirmed** in
  the report; no draft needed.
- If existing ADR disagrees: log **drift** in the report. Phase 7
  drafts a follow-up ADR (or supersession) and surfaces the
  discrepancy explicitly.

### Phase 7 — Draft

For every cell flagged **new** or **drift**:

1. Open the ADR template (per [[meta/schema]] §`adr`).
2. Fill the `compliance:` block with the derived stance. For
   `adopts + exceptions`, populate `exceptions:` with the
   evidence-cited spots; for `deviates`, populate `deviations:` with
   the evidence-cited alternative shape.
3. Fill §Context, §Decision, §Consequences from a per-pattern draft
   template (each normative page may declare one in its conformance
   block; otherwise use the generic shape).
4. Cite every load-bearing claim with file + line evidence collected
   in Phase 3 / 4.
5. Set `confidence:` in frontmatter to match the derived score.

Drafts land in **`projects/<name>/adr/drafts/`** until a human reviews,
edits, and accepts them. Drafts are llm-owned; once moved to
`projects/<name>/adr/`, ownership becomes shared per [[meta/ownership]].

### Phase 8 — Hand off

Surface to the human:

1. The conformance report at `meta/conformance.md` (overwritten each
   run; history goes in `meta/log.md`).
2. The list of new draft ADRs under `projects/*/adr/drafts/`.
3. Any **drift** cells where existing ADRs disagree with current
   evidence — these are the highest-priority human decisions.
4. Any **no-fingerprint** cells where a pattern was skipped — these
   are flags to either declare the pattern's verifiability honestly
   or write the conformance block.

## Conformance Block Schema

Every normative page may carry a `## Conformance` section. Pages
without one are skipped (and surfaced as no-fingerprint).

```yaml
## Conformance

verifiability: high | medium | low
verifiability_rationale: |
  One paragraph explaining what can and can't be mechanically
  verified for this pattern, and why.

hard_signals:
  - id: <kebab-id>                     # stable, unique within the page
    name: <one-line description>
    method: grep | ast | metric | shell
    # method-specific fields:
    pattern: <regex>                   # for method: grep
    rule: <ruleName>                   # for method: ast (Scalafix)
    config: { ... }                    # for method: ast
    measure: <name>                    # for method: metric
    threshold: { op: gte|lte|eq, value: <n> }   # for method: metric
    script: <path>                     # for method: shell — under tools/conformance/<pattern-id>/
    # common fields:
    scope: <glob>                      # default: project root
    verdict_on_match: violation | evidence
    rationale: <one-line why>

soft_signals:
  - id: <kebab-id>
    name: <one-line description>
    prompt: |
      Instructions for the evaluator. Should describe what evidence
      to look for and how to decide between verdict kinds.
    verdict_kinds: [present, partial, absent, unclear]
    scope: <glob>                      # default: project root
    rationale: <one-line why>

classification:
  adopts: |
    Conditions on signal outcomes that indicate full adoption.
  adopts_with_exceptions: |
    Conditions that indicate partial adoption with localized gaps.
  deviates: |
    Conditions that indicate a consistent alternative shape.
  ignores: |
    Conditions under which the pattern is out of scope for the
    project (typically already covered by applies_to.excludes,
    but pattern-specific rules go here).

adr_template: |
  Optional. A per-pattern §Context / §Decision skeleton that drafts
  reuse, with placeholders like {project} and {evidence_summary}.
```

### Fingerprint storage

- **grep / metric** signals are inline in the page (cheap, readable).
- **ast** signals reference Scalafix rule names; rule implementations
  live under `tools/conformance/<pattern-id>/scalafix/` (human-owned).
- **shell** signals reference scripts under
  `tools/conformance/<pattern-id>/` (human-owned). Scripts return
  JSON on stdout: `{"verdict": "...", "evidence": [...], "truncated": false}`.

The inline-first policy keeps most fingerprints reviewable in the
page itself. Scripts are an escape hatch for AST / multi-file
analysis the page can't express cleanly.

### Verifiability ratings

| Rating | Meaning | Typical patterns |
|--------|---------|------------------|
| `high` | Structural, mechanically decidable | `deps-single-file`, ADT-encoding shape |
| `medium` | Mechanical signals + soft judgement | `functional-domain-design`, `test-economics` |
| `low` | Process-not-artifact; weak code signals | `tdd-rhythm`, `symmetric-refactoring` |

Verifiability is honest, not aspirational. A `low` rating with no soft
signals means the pattern is **not mechanizable today** — the operation
records this without faking confidence.

## Output: `meta/conformance.md`

Mirrors `meta/drift.md` in shape (regenerated each run; llm-owned).

```markdown
# Conformance Report

Mechanically computed by `conform`.

## Run Metadata
- Run at: YYYY-MM-DD
- Mode: fresh | diff
- Patterns evaluated: ...
- Projects evaluated: ...
- Drafts produced: N (under projects/*/adr/drafts/)

## Matrix

| Project | FDD | tdd-rhythm | symmetric-ref | test-econ | deps-single-file |
|---------|-----|------------|----------------|-----------|-------------------|
| compositor | adopts (high) | unclear (low) | ... |
| toolbox | adopts (high) — confirms 0001 | ... |
...

## Per-cell drill-downs

### compositor × functional-domain-design — adopts (high, confirms ADR 0001)

Hard signals:
- no-var-in-domain: PASS — 0 / 142 files
- adt-encoding-present: PASS — 12 case classes, 4 enums under src/main/scala/domain/**

Soft signals:
- describes-not-does: PRESENT — "EventPipeline ADT separates description from execution" (src/main/scala/domain/EventPipeline.scala:14)

Existing ADR: projects/compositor/adr/0001-adopt-functional-domain-design.md
Outcome: confirmed — no draft produced.

### tagless × test-economics — adopts with exceptions (medium, NEW)

Hard signals:
- pbt-suite-present: PARTIAL — 3 / 14 modules have PBT
...

Outcome: draft at projects/tagless/adr/drafts/0005-adopt-test-economics.md
Drift: NEW (no existing ADR)
```

## Sequencing Strategy

The user has chosen **foundations first, visualization later**, and
within foundations, **highest-verifiability pattern first**:

1. **Stage 0 (this work)** — write this guide; declare schema; add
   one example `## Conformance` block to validate the schema shape.
2. **Stage 1 — FDD × toolbox baseline.** Write the FDD conformance
   block in full. Run it (by hand, in-context) against `toolbox`.
   Verify the output matches the existing
   `projects/toolbox/adr/0001-adopt-functional-domain-design.md`.
   This proves the loop end-to-end on known-good ground before any
   automation.
3. **Stage 2 — deps-single-file.** Highest-verifiability pattern;
   the easiest fingerprint to write. Run against all 7 in-scope
   projects; expect every cell to already match existing ADRs.
4. **Stage 3 — symmetric-refactoring + test-economics.** Medium
   verifiability; richer soft-signal sections.
5. **Stage 4 — tdd-rhythm.** Honest `low` verifiability; soft
   signals dominate; git-history checks as a hard-signal experiment.
6. **Stage 5 — visualization tooling.** Once the data shape is
   stable, a small TUI / web view over `meta/conformance.md` for
   the human to drill into cells and accept / edit drafts.

Each stage produces a working subset; nothing is gated on later
stages.

## Anti-Patterns

- **Faking high verifiability.** If a pattern is process-not-artifact,
  rate it `low` and lean on soft signals. A fake `high` rating
  produces confident-wrong drafts and erodes trust in the operation.
- **Over-broad scopes.** Hard signals with `scope: **/*.scala` and a
  liberal regex catch noise — build files, tests, generated code.
  Scope to where the pattern actually lives (e.g.
  `src/main/scala/**/domain/**`).
- **Drafting without evidence citations.** Every claim in a generated
  ADR cites a file + line. A draft without citations is unreviewable
  and gets rejected.
- **Auto-accepting drafts.** Drafts always land in `adr/drafts/` and
  require a human to move them. The operation never edits accepted
  ADRs.
- **Treating `unclear` as adoption.** A soft signal returning
  `unclear` means the LLM couldn't decide. That's a flag for human
  review, not a default to `adopts`.
- **Inline scripts.** Scripts that live in the page (rather than
  `tools/conformance/<pattern-id>/`) hide behind YAML and aren't
  reviewable as code. Push complex logic to script files.

## Open Questions / Future

- **Cross-pattern interactions.** A project may `adopts` FDD and
  `deviates` from `tdd-rhythm` — these are independent. But some
  patterns reinforce each other (FDD + property-based testing is the
  natural pair). Capture interaction hints in classification rubrics?
- **Per-project overrides.** A project might legitimately override a
  hard signal ("we use `var` in `Buffer` for arena reuse — see ADR
  0004"). The override mechanism today is the `exceptions:` block in
  the existing ADR. Should `conform` learn to *suppress* hard signals
  pointed at by existing exceptions, so they don't surface again as
  noise on re-runs?
- **Confidence calibration.** The `high` / `medium` / `low` mapping
  from signal outcomes to overall confidence is ad-hoc at Stage 0.
  After Stages 1-3 we'll have empirical data on which signals
  correlated with correct stances; tune the rubric then.
- **Compatibility with `lint`.** Should `conform` run as a phase of
  `lint`, or stay separate? Probably separate (slower, costlier),
  but `drift.md` should cross-reference `conformance.md` for any
  in-scope project with no fingerprint output.
- **Visualization shape.** TBD; the human will lead this once Stage
  4 produces stable matrix output.

## Related Pages

- [[meta/schema]] — adds the `conformance-report` page type and the
  `## Conformance` block (proposal pending — see fix/ script).
- [[meta/drift]] §DRIFT-024 — the fan-out backlog this operation
  retires.
- [[POLICY]] §Compliance Contract — the schema-level shape derived
  ADRs must match.
- [[meta/ownership]] — `tools/` is human-owned; conformance scripts
  follow that policy. `adr/drafts/` is a new llm-owned sub-tree.
- [[tech/guides/breakout]] — the procedure model this guide mirrors.

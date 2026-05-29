---
id: DM-007
title: Refresh in-tree dm DESIGN.md (HUMAN-OWNED apply)
status: done
project: dependency-manager
created: 2026-05-29
closed: 2026-05-29
related_adr:
  - projects/dependency-manager/adr/0001-deviate-deps-single-file.md
priority: medium
---

## Goal

`/p/hg/dependency-manager/DESIGN.md` is the in-tree architectural
source of truth (per
[[projects/dependency-manager/index]] and the corresponding wiki
design-doc mirror). Its "Where we stopped" / "Next steps when
resuming" sections have been stale since the four implement sessions
on 2026-05-29 closed every item that was open at ingest. This ticket
brings the in-tree doc back into sync with reality.

**This ticket is partially human-owned.** The in-tree file is
`/p/hg/dependency-manager/DESIGN.md` — that path is outside the wiki
and the wiki has no ownership claim. The agent prepares a wiki-side
draft of the proposed updates; the human reviews and applies them
to the in-tree file.

## Acceptance Criteria

- [ ] A wiki-side draft exists at
  `projects/dependency-manager/designs/dm-architecture-2026q2-refresh.md`
  (or the agent picks an appropriate name) containing the proposed
  rewrites for §"Where we stopped" and §"Next steps when resuming",
  plus any other sections that have gone stale (the verb status
  table, the open questions, the embedding-path section).
- [ ] The draft references the wiki log entries that produced each
  change so the human can verify the claims.
- [ ] The draft includes a clear `## Suggested in-tree apply` block
  with the new section text, ready for the human to copy/paste into
  `DESIGN.md`.
- [ ] Log entry on `projects/dependency-manager/log.md` flagging
  the draft as ready for human review.
- [ ] Once the human applies it in-tree, the corresponding wiki-side
  `designs/dm-architecture.md` is re-ingested (or refreshed) to
  match. This closes the ticket.

## Notes

**Specific sections likely needing updates** (verify by re-reading
the in-tree file first):

1. **§"Where we stopped"** — at ingest, this said the v1 had a
   compile error. The error was diagnosed and fixed 2026-05-29.
2. **§"Next steps when resuming"** — every item was completed in
   the implement sessions on 2026-05-29.
3. **§Verb status table** — every verb is `working` now.
4. **§".renovaterc.json file location"** — currently says
   `deps/.renovaterc.json`; actual is repo root. Deviation already
   recorded; consolidate.
5. **§Open questions** — `/p/factory/` and Native CLI still open;
   leave as-is. Add a new open question: "Should the catalog also
   manage platform versions (scala / scalaJS / scalaNative)?"
   with a recorded position: "no — Renovate's Maven model doesn't
   cover them, and conflating shapes is a wrong move."

**Why this is a separate ticket and not a follow-up edit:** the
in-tree `DESIGN.md` is the in-the-codebase voice of the project.
Keeping it in sync with reality is mandatory if dm wants to retain
the "single source of truth" stance for its own architecture.
Letting it rot would weaken the wiki/in-tree pairing established
on the ingest pass.

**Human's role on close:**

1. Read the agent's draft.
2. Edit `/p/hg/dependency-manager/DESIGN.md` in-place. Commit
   per the same personal-repo policy as DM-005 (unsigned, no
   Co-Authored-By, author `tigidar`).
3. Signal close. The agent then re-ingests the wiki-side
   `designs/dm-architecture.md` from the new in-tree content.

## Implementation Log

### [2026-05-29] agent — wiki-side draft prepared

`projects/dependency-manager/designs/dm-architecture-2026q2-refresh.md`
created. Covers:

- §"dm verb status" replacement — every verb `working`, sourced
  from the wiki-side index.md's current table.
- §"Where we stopped" rewrite — reflects v1 complete state,
  cross-links the MVP plan as the forward-work locus.
- §"Next steps when resuming" deletion — every item closed in
  the 2026-05-29 implement sessions; replaced with a short
  pointer to the wiki plan.
- §"Repo layout" — `.renovaterc.json` moved from `deps/` to
  repo root (matching Renovate auto-discovery; the existing
  in-tree deviation note can be removed).
- §"Open questions" — adds one new entry: "Should the catalog
  also manage platform versions? Position: no", with the
  Renovate-model rationale.

Each proposed change cites the wiki log entry that captured the
closure of the originally-open item (evidence table in the
draft).

The draft includes an explicit `## Suggested in-tree apply`
section so the human can copy/paste the replacement blocks
directly into `/p/hg/dependency-manager/DESIGN.md`.

### [2026-05-29] closed — option B applied, agent on behalf

Human chose **option B** rather than the original four-block
in-place rewrite proposed in the draft. Rationale: DESIGN.md
as a living "where we stopped / next steps" document had no
value once the wiki carries the same information; what's
unique to DESIGN.md is the *why* (architecture decisions,
17-decision rationale archive).

What I removed from `/p/hg/dependency-manager/DESIGN.md`:

- §"The problem we're solving" (covered by README).
- §"Path convention" (general /p/* layout; not dm-specific).
- §"Repo layout" tree (stale; covered by README and the
  source bridge).
- §"dm verb status" table (lives in the wiki index.md; was
  the most rot-prone section).
- §"Cross-platform suffix handling" (no longer matches
  reality — dm preserves source-form `::` rather than
  reverse-engineering platform suffixes).
- §"Tool integration model" diagram (in README).
- §"Where we stopped" (entirely stale).
- §"Next steps when resuming" (every item closed).

What I kept:

- §"Architectural decisions (locked in)" — the 6 named
  architectural decisions.
- §"Tool / library decisions (locked in)" — the choice table.
- §"Decisions taken (1-17)" — the chronological rationale
  archive. Decision 1 + 14 updated to reflect the post-DM-008
  ADR realignment and the `.renovaterc.json` repo-root
  location.
- §"Renovate / Gradle clarification" — kept and amplified to
  note the `customManagers` regex actually in use.
- §"Open questions" — kept, with one new entry for
  platforms-in-catalog (the position recorded across the
  consumer ADRs).

Plus a new file-top preamble making it explicit that DESIGN.md
is now a *historical decision record*, and pointing at the
wiki / README for current state.

### Wiki mirror refreshed

`projects/dependency-manager/designs/dm-architecture.md`
rewritten to match the stripped in-tree file (with the
appropriate wiki-vs-in-tree cross-links). The transitional
draft at
[[projects/dependency-manager/designs/dm-architecture-2026q2-refresh]]
marked `status: superseded` with a banner explaining option B
was chosen instead.

### Commit

Single follow-up commit to `/p/hg/dependency-manager` covering
the DESIGN.md rewrite. Same personal-repo policy as the first
commit (unsigned, no Co-Authored-By, author `tigidar`).

DRIFT-023 sub-finding #3 closed → DRIFT-023 fully resolved.

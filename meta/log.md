# Cross-cutting Log

Append-only record of cross-project / wiki-wide events. Project-scoped
events live in `projects/<name>/log.md`.

**Ownership: llm.**

---

## [2026-05-28] ingest | An Introduction to Functional Design (De Goes, 2020)

Ingested `sources/raw/docs/introduction_to_functional_design_john_de_goes.txt`.
Created summary at `sources/summaries/introduction_to_functional_design_john_de_goes.md`
covering: functional-domain framing, executable vs declarative
(final vs initial) encodings, worked email-filter example in both
encodings, encoding tradeoffs (extensibility, optimization, persistence,
legacy interop), and related concepts (expression problem, object
algebras, tagless-final).

Flagged as candidate for promotion to `tech/patterns/functional-domain-design.md`
once a second source or project synthesis corroborates the pattern.

Refs: [[sources/summaries/introduction_to_functional_design_john_de_goes]],
[[sources/raw/docs/introduction_to_functional_design_john_de_goes.txt]]

## [2026-05-28] ingest | Functional Domain Modeling — The ZIO 2 Way (Ghosh, 2022)

Ingested SlideShare deck
`https://www.slideshare.net/slideshow/functional-domain-modeling-the-zio-2-way/253277754`
(Debasish Ghosh, 39 slides, 2022-09-22). Created summary at
`sources/summaries/functional_domain_modeling_zio2_debasish_ghosh.md`
covering: DDD-flavored pattern language (entities/VOs, repositories,
domain services), concrete-ZIO vs tagless-final tradeoff, ZLayer-based
dependency injection, and a worked Trading domain example.

Staged text extraction (WebFetch output) written to
`sources/tmp/functional_domain_modeling_zio2_debasish_ghosh.txt` for
human review. `sources/raw/**` is human-owned per `meta/ownership.md`;
`sources/tmp/` is the agreed staging area — the human decides whether
to promote the snapshot to `sources/raw/docs/` or discard it.

Notable: this is the second functional-design source in the wiki and
covers a complementary axis (architectural layering vs encoding choice).
Together they motivate a future `tech/patterns/functional-domain-design.md`
and potentially a `tech/patterns/functional-domain-layering.md` —
promotion still requires per `POLICY.md` either a second corroborating
source or an internal project synthesis.

Refs: [[sources/summaries/functional_domain_modeling_zio2_debasish_ghosh]],
[[sources/summaries/introduction_to_functional_design_john_de_goes]]

## [2026-05-28] promote | Draft tech/patterns/functional-domain-design.md

Drafted `tech/patterns/functional-domain-design.md` (status: draft)
from the two functional-design summaries. Pattern focuses on the
encoding axis (executable / final vs declarative / initial) with the
"immutable model + constructors + composable operators" framing as
its core. Ghosh's architectural layering is cited under Related
Patterns as a candidate for a separate future page
(`functional-domain-layering`).

Page is `draft` per `POLICY.md` lifecycle — not yet enforced by drift
checks. Human promotes to `accepted` when ready. Updated
`tech/index.md` to list it under Patterns (normative).

Refs: [[tech/patterns/functional-domain-design]],
[[sources/summaries/introduction_to_functional_design_john_de_goes]],
[[sources/summaries/functional_domain_modeling_zio2_debasish_ghosh]]

## [2026-05-28] promote | tech/patterns/functional-domain-design.md → accepted

Human promoted the draft to `status: accepted`. Rationale (from
session): this is the user's default pattern for almost all design
work — strong personal preference and prior track record outweigh the
absence of in-repo project syntheses.

Consequences:
- In-scope projects (Scala / Scala Native / Scala JS, any domain) must
  now address this pattern in their ADRs: adopt, except, deviate, or
  ignore. Silence becomes drift.
- Lint will start reporting *missing declaration* in `meta/drift.md`
  for any project whose ADRs don't mention this page.

Updated `tech/index.md` (removed draft tag). Confidence raised to high.

Refs: [[tech/patterns/functional-domain-design]]

## [2026-05-28] lint | First post-promotion drift report

Ran lint against the wiki. Wrote `meta/drift.md` with 8 findings:

- **DRIFT-001, DRIFT-002** (medium, missing-declaration): the only
  on-disk project, `compositor`, has no ADRs and is in-scope for both
  accepted normative pages. Notable: compositor's `designs/input-pipeline.md`
  is already a textbook application of `functional-domain-design`
  (pure `(Event, State) => (Event, State)` stages, property-tested
  core) — an `adopts` ADR would be quick.
- **DRIFT-003** (medium): `index.md` advertises webapp, cli-tool,
  infra as active but none exist on disk.
- **DRIFT-004, DRIFT-006** (low): two dangling internal links.
- **DRIFT-005** (medium): `tech/stack/mill.md` §Dependency Management
  still documents the two-file deps pattern explicitly rejected by
  `tech/decisions/deps-single-file.md` — descriptive page now
  contradicts an accepted normative decision.
- **DRIFT-007** (low): five root-level markdown files outside the schema.
- **DRIFT-008** (informational): both normative pages have zero
  adopters; baseline recorded for future lint comparisons.

Refs: [[meta/drift]]

## [2026-05-28] adr | compositor adopts functional-domain-design (with deviation)

Created `projects/compositor/adr/0001-adopt-functional-domain-design.md`
(status: accepted). The compositor adopts
`tech/patterns/functional-domain-design.md` as its default design
pattern, with one explicit **deviation**: interpreters must allocate
only from arena / per-frame scratch, never from the GC heap. Cited
input-pipeline design as evidence the pattern is already in use.

Resolves DRIFT-002. Populated `used_by` on the pattern page.

Refs: [[projects/compositor/adr/0001-adopt-functional-domain-design]],
[[tech/patterns/functional-domain-design]]

## [2026-05-28] adr | compositor adopts deps-single-file (forward-looking)

Created `projects/compositor/adr/0002-adopt-deps-single-file.md`
(status: accepted). Forward-looking adoption — compositor has no code
repository at `/p/compositor` yet; the ADR records intent so that the
codebase, when stood up, will use a single `Dependencies.mill` from
day one.

Resolves DRIFT-001. Populated `used_by` on the decision page.

Refs: [[projects/compositor/adr/0002-adopt-deps-single-file]],
[[tech/decisions/deps-single-file]]

## [2026-05-28] edit | tech/stack/mill.md aligned to deps-single-file

Rewrote `tech/stack/mill.md` §Dependency Management to follow the
single-file pattern: removed `Versions.mill` example, replaced
`import build.deps.{Versions => V}` consumption with the
`object Deps` form, and added an opening pointer to the normative
decision. Fixed dangling link in Links section
(`tech/decisions/build-system-mill` → `tech/decisions/deps-single-file`).

Resolves DRIFT-004 and DRIFT-005. Bumped `updated` to 2026-05-28.

Refs: [[tech/stack/mill]], [[tech/decisions/deps-single-file]]

## [2026-05-28] edit | wiki index reflects on-disk project state

Updated `index.md` project table: compositor → `active (design-stage)`,
webapp / cli-tool / infra → `planned`. Added note that `planned`
projects are not evaluated by lint until they have on-disk presence.

Resolves DRIFT-003.

Refs: [[index]]

## [2026-05-28] edit | compositor index cleanup

`projects/compositor/index.md` now lists the two new ADRs, removed the
dangling link to `architecture.md`, added a note that the architecture
page is a schema-standard page to be created when the codebase is
stood up.

Resolves DRIFT-006.

Refs: [[projects/compositor/index]]

## [2026-05-28] lint | Post-remediation drift report

Rewrote `meta/drift.md`. 7 of 8 prior findings resolved. Only DRIFT-007
(five unstructured root-level markdown files) remains open, awaiting
human triage — agent will not move user-authored content.

Refs: [[meta/drift]]

## [2026-05-28] edit | scratch/ directory for personal working notes

With user authorization, moved five unstructured root-level markdown
files into `/p/wiki/scratch/`:

- `agentic_coding_through_the_lense_of_cellular_automata_ex1.md`
- `agentic_coding_through_the_lense_of_cellular_automata_ex2.md`
- `monorepo-design-wip.md`
- `scala-days.md`
- `wiki_current_state_with_monorepo.md`

Wiki root now contains only `CLAUDE.md`, `index.md`, `POLICY.md` and
the standard directories. `meta/drift.md` updated to mark DRIFT-007
resolved at the file-system level and exclude `scratch/**` from
future lint runs.

Two diffs pending for the human (agent cannot edit those files):
- `meta/ownership.md` — add `scratch/**` row (`human`, no override).
- `meta/schema.md` — add an "Out-of-schema directories" note.

Refs: [[meta/drift]]

## [2026-05-28] edit | scratch/ codified in ownership and schema

With explicit user authorization to edit human-owned files:

- `meta/ownership.md` — added `scratch/**` row to Defaults
  (`human`, no override), and a corresponding "Why These Defaults"
  bullet.
- `meta/schema.md` — `### Out-of-schema directories` section was
  already present (added by the user); no agent edit needed.

DRIFT-007 fully closed. `meta/drift.md` updated. The wiki is now
clean: 8 of 8 findings resolved.

Side note: `meta/ownership.md` also contains a `sources/scratch/**`
row that the agent did not add; flagged to the human in
conversation in case the path was intended to be `scratch/**`.

Refs: [[meta/ownership]], [[meta/schema]], [[meta/drift]]

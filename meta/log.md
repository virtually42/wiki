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

## [2026-05-28] ingest | Throw Away the Irrelevant (De Goes on CoRecursive)

Ingested `sources/raw/docs/throw_away_the_irrelevant_john_de_goes_podcast.txt`
(CoRecursive interview with John A De Goes, Adam Gordon Bell host,
circa 2018 — Scalaz 8 / Cats 1.0 era). Created summary at
`sources/summaries/throw_away_the_irrelevant_john_de_goes_podcast.md`
covering twelve positions: polymorphism vs descriptive monomorphic
names, principled type classes with algebraic laws, data structures
as premature specialization, performance characteristics belonging
in type-class contracts, type classes vs OO traits in Scala, the case
for `IO` everywhere with capability-type-class refinement, the three
generations of Scala effect monads, why monad-transformer stacks
collapse on the JVM (heap churn + megamorphism), the
`newtype`-over-`IO` workaround, why Scala FP must diverge from
Haskell, the Cats vs Scalaz 8 split, and meta-commentary on writing
style.

Flagged two follow-up candidates for the tech layer:

- `tech/patterns/principled-polymorphism` — single-source as of now;
  promotion needs a second corroborating source or project synthesis.
- `tech/patterns/anti/monad-transformer-stacks-on-jvm` — strong
  single-source evidence; second source desirable before promotion.

Also flagged an apparent tension between this source (polymorphic
`M[_]` with capabilities) and
[[sources/summaries/functional_domain_modeling_zio2_debasish_ghosh]]
(concrete `IO[E,A]` in service contracts) — likely different
boundaries (internal helpers vs public service contracts), worth
synthesizing later.

Refs: [[sources/summaries/throw_away_the_irrelevant_john_de_goes_podcast]],
[[sources/summaries/introduction_to_functional_design_john_de_goes]],
[[sources/summaries/functional_domain_modeling_zio2_debasish_ghosh]],
[[tech/patterns/functional-domain-design]]

## [2026-05-28] edit | Human closed DRIFT-012 (ownership.md formatting)

Human deleted the orphan `**scratch/ is human**...` paragraph
(lines 81–83) from `meta/ownership.md` — the leftover duplicate of
the correctly-formed bullet at line 80. `meta/ownership.md` is
human-owned; the agent flagged the issue in `meta/drift.md` but
did not edit. `meta/drift.md` summary table updated and
Notes-for-Human section narrowed to the two remaining items
(DRIFT-011 deferred to the next project, DRIFT-013 informational).

Refs: [[meta/ownership]], [[meta/drift]]

## [2026-05-28] edit | Closed DRIFT-009 and DRIFT-010

Per user instruction, applied the recommended remediations:

- **DRIFT-009** — removed the `meta/registry.md` line from
  `index.md`. No other page in the wiki referenced a registry
  concept; the line was carried over from an earlier wiki shape.
- **DRIFT-010** — created `tech/glossary.md` as a stub
  (`kind: stub`, `status: stub`) so the schema's `glossary-entry`
  location matches reality. No entries yet — populated on demand
  when terms accumulate cross-page ambiguity. Both inbound
  references (from `index.md` and `tech/index.md`) now resolve.

DRIFT-011 was explained to the user but not yet remediated; left
open in `meta/drift.md` until a remediation decision is made.
DRIFT-012 (human-owned file) and DRIFT-013 (informational) remain
open with no action expected.

Updated `meta/drift.md` summary table: DRIFT-009 and DRIFT-010
marked **resolved**; Notes-for-Human section narrowed to the three
remaining items.

Refs: [[meta/drift]], [[index]], [[tech/glossary]], [[tech/index]]

## [2026-05-28] lint | Five new findings, compliance side still clean

Ran lint against the wiki. Rewrote `meta/drift.md` with 5 findings —
all post-reachability-work. Compliance side (missing-declaration,
dangling-adoption, weak-rationale, conflicting-adoptions,
unused-normative) remains clean: both accepted normative pages still
have their compositor adopter and no new normative pages have landed.

New findings:

- **DRIFT-009** (low, dangling-link): `index.md` line 81 links to
  `meta/registry.md`, which does not exist on disk. Likely carried
  over from an earlier wiki shape; nothing else references a registry.
- **DRIFT-010** (low, dangling-link): both `index.md` and
  `tech/index.md` reference `tech/glossary.md`, which does not exist.
  Schema (`meta/schema.md:21`) still lists `glossary-entry` as a
  valid page type, so removing the references alone would leave the
  schema describing a non-existent location.
- **DRIFT-011** (low, content-frontmatter-contradiction):
  `tech/patterns/functional-domain-design.md` §"Open Questions /
  Drift Signals" claims no project ADR yet cites the page, while the
  same file's `used_by` already lists the compositor adopter and the
  previous drift report marked DRIFT-008 as resolved with this page
  having one adopter.
- **DRIFT-012** (low, formatting-glitch): `meta/ownership.md`
  lines 81–83 contain an orphan paragraph restating the `scratch/`
  bullet without a bullet marker — apparent edit remnant. File is
  human-owned; surfaced for the human to fix.
- **DRIFT-013** (informational, descriptive-used_by-empty):
  `tech/stack/mill.md`, `tech/stack/kyo.md`, `tech/stack/airstream.md`
  all have `used_by: []`, while `projects/compositor/index.md` §Stack
  lists Mill and Kyo. The schema template includes `used_by` on
  technology pages but POLICY only normatively requires it on
  normative pages.

Three of the five (DRIFT-009, DRIFT-010 via stub, DRIFT-011) are
trivially agent-fixable; DRIFT-012 needs human action on a
human-owned file; DRIFT-013 is informational.

Refs: [[meta/drift]]

## [2026-05-28] edit | Airstream llm-wiki reachability fixes (mirror of Mill / Kyo)

Applied the same one-way Layer 2 → Layer 3 reachability pattern to
Airstream that was previously applied to Mill and Kyo. Before this
edit, the only Layer-2 reference to the Airstream llm-wiki was the
*External Library Wikis* table row in [[index]] and the bridge file
at [[sources/raw/code/airstream]].

Changes:

- Created [[tech/stack/airstream]] (descriptive, scope: global)
  with the same shape as [[tech/stack/mill]] and [[tech/stack/kyo]]:
  *Deep Reference* block at the top pointing at
  [[Airstream/llm-wiki/index]], pointer to the bridge file, pointer
  to the layering synthesis, mention of the
  `frontend:airstream-ownership-patterns` agent skill, plus a lean
  orientation covering type hierarchy, a core reading list keyed to
  Layer-3 pages, the ownership pitfall, dependency coordinates
  (Scala.js only), and the relation to
  [[tech/patterns/functional-domain-design]].
- [[tech/index]] now lists `stack/airstream.md` under Stack
  alongside `stack/mill.md` and `stack/kyo.md`.
- [[syntheses/wiki-layering-and-external-lib-wikis]] updated:
  *Generalization* now records that **all three** registered
  external-lib wikis have a Layer-2 anchor; *Open questions*
  retroactively recognizes that "wait for ADR adoption" was the
  wrong trigger condition — reachability and policy adoption are
  separate concerns, and future external-lib additions should
  create the stack page at the same time as the bridge file. Links
  section and sources frontmatter extended.

Not done (out of scope):
- No Airstream guides under `tech/guides/` (no Airstream guide
  currently exists in Layer 2; nothing to retrofit).
- No back-links from `Airstream/llm-wiki/` into Layer 2 (one-way
  coupling preserved).
- No new ADR adopting Airstream — page created ahead of formal
  adoption, same as the Kyo case earlier in this session.

The three reachability fixes (Mill → Kyo → Airstream) together
close out the synthesis's original "Generalization to other
external libs" section — every registered bridge now has at least
one inbound Layer-2 link from a `tech/stack/<name>.md` page.

Refs: [[tech/stack/airstream]], [[tech/index]],
[[syntheses/wiki-layering-and-external-lib-wikis]],
[[Airstream/llm-wiki/index]], [[sources/raw/code/airstream]]

## [2026-05-28] edit | Kyo llm-wiki reachability fixes (mirror of Mill)

Applied the same one-way Layer 2 → Layer 3 reachability pattern to
Kyo that was previously applied to Mill. Before this edit, the only
Layer-2 reference to the Kyo llm-wiki was the *External Library
Wikis* table row in [[index]] and the bridge file at
[[sources/raw/code/kyo]] — a human or agent landing in `tech/` had
no obvious hint that `kyo/llm-wiki/` existed.

Changes:

- Created [[tech/stack/kyo]] (descriptive, scope: global) with the
  same shape as [[tech/stack/mill]]: *Deep Reference* block at the
  top pointing at [[kyo/llm-wiki/index]], pointer to the bridge file,
  pointer to the layering synthesis, list of `scala:kyo-*` agent
  skills, plus a lean orientation covering module layers, core
  concepts, an effects cheat-sheet, data types, dependency
  coordinates, conventions, and the relation to
  [[tech/patterns/functional-domain-design]].
- [[tech/index]] now lists `stack/kyo.md` under Stack.
- [[syntheses/wiki-layering-and-external-lib-wikis]] updated:
  *Generalization to other external libs* records the Kyo fix is
  applied; *Open questions* narrows the unresolved item to
  Airstream; sources list extended to include the new Kyo pages.

Not done (out of scope):
- No Kyo guides under `tech/guides/` (no Kyo guide currently exists
  in Layer 2; nothing to retrofit).
- No back-links from `kyo/llm-wiki/` into Layer 2 (the synthesis is
  explicit that the coupling must remain one-way).
- Airstream still has no Layer-2 footprint; deferred until an
  adopter materializes.

The Layer-2 footprint for Kyo is created ahead of formal ADR
adoption — compositor lists Kyo in its stack but has no ADR for it
yet. The user authorized creating the stack page anyway to fix
reachability now rather than wait for the ADR trigger condition.

Refs: [[tech/stack/kyo]], [[tech/index]],
[[syntheses/wiki-layering-and-external-lib-wikis]],
[[kyo/llm-wiki/index]], [[sources/raw/code/kyo]]

## [2026-05-28] synthesis | Wiki layering and Mill llm-wiki reachability

Created `syntheses/wiki-layering-and-external-lib-wikis.md`. Names the
three layers on disk — Meta (rules of engagement), Content (our tech
layer + projects + sources), and External-lib wikis
(`mill/llm-wiki/`, `kyo/llm-wiki/`, `Airstream/llm-wiki/`) — and
describes the bridge mechanism via `sources/raw/code/<lib>.md` files
with `type: external-lib` frontmatter. Includes a topic-level
cross-walk between our Layer-2 Mill pages and the Layer-3
`mill/llm-wiki/` pages.

Applied reachability fixes so the Mill llm-wiki is discoverable from
where readers actually land:

- `index.md` — added an *External Library Wikis* section listing
  Mill, Kyo, Airstream with bridge-file links; surfaced the new
  synthesis under Cross-Project Syntheses.
- `tech/stack/mill.md` — added a *Deep Reference* block near the top
  pointing at `mill/llm-wiki/index.md` and the synthesis; expanded
  the Links section to include the llm-wiki, bridge, and the three
  Mill guides.
- `tech/guides/mill-cross-platform.md`,
  `tech/guides/mill-monorepo.md`,
  `tech/guides/mill-dependency-management.md` — each gained an
  *Upstream Reference* block linking the most relevant
  `mill/llm-wiki/` pages and the synthesis.

Fixes are intentionally one-way (Layer 2 → Layer 3) to keep the
external-lib wikis self-contained and refreshable without coupling
to our opinions.

Two flagged candidates for future work (not done now):

- A `tech/stack/kyo.md` / `tech/stack/airstream.md` analogous to
  `tech/stack/mill.md` once those libraries pick up ADR adopters.
- A lint check that every `sources/raw/code/*.md` bridge has at least
  one inbound Layer-2 link, so a future llm-wiki cannot be silently
  orphaned.

Refs: [[syntheses/wiki-layering-and-external-lib-wikis]],
[[index]], [[tech/stack/mill]], [[mill/llm-wiki/index]],
[[sources/raw/code/mill]]

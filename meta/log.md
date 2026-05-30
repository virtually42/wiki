# Cross-cutting Log

Append-only record of cross-project / wiki-wide events. Project-scoped
events live in `projects/<name>/log.md`.

**Ownership: llm.**

---

## [2026-05-30] session | `conform` operation — foundation laid for evidence-based normative compliance

DRIFT-024 (the 17-cell project × pattern fan-out backlog from
2026-05-29's four-pattern promotion sweep) framed the question:
manual ADR fan-out is the wrong abstraction at this scale. Operator
agreed; design conversation produced an evidence-based alternative
that flips the wiki's compliance epistemology — from *assertion*
("a human writes an ADR claiming we adopt X") to *evidence*
("the code is inspected; an ADR draft is derived"). Operator
explicitly chose foundations-first sequencing with visualization
deferred to a later stage.

The operation:

- New top-level wiki op `conform [<project>] [<pattern>]` alongside
  `lint`. Reads each normative page's new `## Conformance` block
  (hard signals = grep/AST/metric/shell; soft signals = LLM-evaluated
  prompts), runs them against a project's source, classifies a
  stance (adopts / adopts+exceptions / deviates / ignores) with
  confidence, drafts an ADR matching the existing
  `compliance:` schema, and (on re-runs) detects regression where
  code has drifted from declared stance.
- Drafts land in `projects/*/adr/drafts/` (new llm-owned sub-tree);
  humans review and move accepted drafts into `projects/*/adr/`
  where ownership becomes shared per [[meta/ownership]].
- Report at `meta/conformance.md`, regenerated each run, same role
  as [[meta/drift]].

Foundation deliverables created this session:

- `tech/guides/conformance.md` — full operation spec (kind:
  descriptive, status: draft). Mirrors
  [[tech/guides/breakout]]'s phase-by-phase structure.
- `CLAUDE.md` — `conform` registered in §Knowledge Operations
  alongside `lint`. (Shared-owned edit; flagged for review.)
- `tech/patterns/functional-domain-design.md` — first `##
  Conformance` block, exercising the schema with 4 hard signals
  (no-var-in-domain, adt-encoding-present, composable-operators-present,
  no-runtime-effects-in-algebra) + 2 soft signals (describes-not-does,
  interpreter-separation) + classification rubric + adr_template.
  Chosen as the highest-verifiability `medium`-rated pattern to
  validate the schema with realistic shape.
- `fix/apply-conformance-schema.py` — idempotent fix script
  proposing additions to two human-owned files:
  - `meta/schema.md` § new `## Conformance Block` section
    describing the fingerprint schema and verifiability ratings.
  - `meta/ownership.md` — adds rows for `meta/conformance.md`
    (llm) and `projects/*/adr/drafts/**` (llm), plus matching
    rationale paragraphs.

Sequencing plan (recorded in the guide §Sequencing Strategy):

1. Stage 0 (done) — guide + schema + first conformance block.
2. Stage 1 — FDD × toolbox baseline. Run the FDD fingerprint
   (by hand, in-context first) against `/p/hg/toolbox`; verify
   the output matches the existing
   `projects/toolbox/adr/0001-adopt-functional-domain-design.md`.
   This is the **validation case** before any automation.
3. Stage 2 — `deps-single-file` (highest verifiability).
4. Stage 3 — `symmetric-refactoring` + `test-economics`.
5. Stage 4 — `tdd-rhythm` (honest `low` verifiability).
6. Stage 5 — visualization tooling.

Human-gated:

- Run `python3 fix/apply-conformance-schema.py` to land the
  schema + ownership additions (or reject and ask for revisions).
- Review the new `conform` entry in CLAUDE.md.
- Review the FDD conformance block; tune hard-signal globs /
  regexes if they over-fire against any existing project.

Cross-references for [[meta/drift]] next run:
- DRIFT-024 should annotate that a structural alternative is in
  Stage 0; cells remain open until conform runs and produces
  drafts, but the *expected resolution path* is no longer 17
  hand-drafted ADRs.
- A new finding may surface: a normative page with no `##
  Conformance` block is a soft drift (visible after conform runs;
  not flagged today).

Refs:
[[tech/guides/conformance]], [[meta/drift]] §DRIFT-024,
[[tech/patterns/functional-domain-design]] §Conformance,
[[POLICY]] §Compliance Contract, [[meta/schema]] §(proposed) Conformance Block,
`fix/apply-conformance-schema.py`.

---

## [2026-05-30] adr | deploymentbox v3 — GitHub Actions + sigstore attestation supersedes v2 microVM substrate for public OSS

Day after v2 landed, the operator re-framed the question: could a
much simpler "let GitHub build, download to laptop, sign, upload,
re-verify on clean machine" path match v2's security? Answer in
conversation: yes for **public OSS specifically**, *if* the bare
SHA-from-GitHub is replaced with sigstore-signed build provenance
attestation (`actions/attest-build-provenance`, GA 2024). The
attestation binds artifact → source commit SHA → workflow run in
a public transparency log via GitHub's OIDC identity. That's SLSA
Build L3 — stronger provenance than v2's bare SHA-256 manifest.

With attestations in scope, the trade-off net-favors v3 for public
OSS: €0/mo (saves €7-8/mo Hetzner line), zero host maintenance,
public reproducibility, no SSH-forwarding ceremony, signing key
responses never leave the laptop USB bus. The single new trust
delta — GitHub Actions infrastructure — is small relative to
"GitHub already hosts the source." Clean-machine re-verify
(`gpg --verify` + `sha256sum` re-check +
`gh attestation verify` against Central-served bytes) is the
trust-but-verify capstone.

**Scope is explicitly public-OSS-only.** Any future private
`no.virtual-architect` artifact must reach for a v2-shaped
self-managed pipeline; v3 does not extend. The v2 design + ADRs
0001/0005/0006 are preserved with `status: superseded` specifically
so they remain a starting point.

Created:

- `projects/deploymentbox/designs/release-pipeline-v3-github-attested.md`
- `projects/deploymentbox/adr/0007-build-on-github-with-attestations.md`
  (load-bearing v3 decision; supersedes 0001 / 0002 / 0003 / 0005 / 0006)

Marked superseded:

- v2 design + ADRs 0001 / 0002 / 0003 / 0005 / 0006 (frontmatter
  `status: superseded`, `superseded_by:` pointing to 0007 / v3 design)

Unchanged:

- ADR-0004 (tag-driven, one key, no snapshots, groupId
  `no.virtual-architect`, Central Portal endpoint) — carries over
  to v3 intact.

Updated:

- `projects/deploymentbox/index.md` — rewritten for v3.
- `projects/deploymentbox/wip.md` — overwritten with v3 blockers
  (namespace TXT still pending; first library `release.yml`,
  operator-side release script, `/p/hg/deploymentbox/` disposition).
- `index.md` (top-level) — deploymentbox row updated for v3 stack.

Two design pivots in 24 hours (v1→v2 yesterday, v2→v3 today). The
wiki's preserve-superseded pattern keeps the reasoning trail intact
across both — six superseded ADRs vs two accepted ones, but
fully reconstructible. ADR-0007 §Context explicitly narrates *why*
ADR-0001's GitHub-runner rejection aged out (Volpe pattern fixes
toolchain pinning; sigstore separates build from sign so
Secrets-only-key-custody is no longer the only path).

First wiki use of sigstore / SLSA / build-attestation primitives.
Nothing in `tech/decisions/` or `tech/patterns/` covers them yet.
Promotion candidate (premature today) would be something like
`tech/patterns/ci-attested-local-signed-release.md` if a second
distribution path (npm, container registries) ever adopts the
same shape.

Refs:
[[projects/deploymentbox/designs/release-pipeline-v3-github-attested]],
[[projects/deploymentbox/adr/0007-build-on-github-with-attestations]],
[[projects/deploymentbox/log]] (full session entry),
[[sources/summaries/github_actions_nix_cachix_dhall_gvolpe]]
(load-bearing for the runner-hermeticity argument).

## [2026-05-30] ingest | animdsl — third of four sibling breakouts from /p/v42/tagless

Executed `breakout` on the animation timeline DSL. Third of the
four sibling breakouts forecast in the tagless ingest entry. The
design document at `/p/v42/tagless/animdsl_specification_and_design.md`
served as the authoritative layout spec — its §6 "Module Layout"
matches the on-disk structure 1:1.

Destination: `/p/hg/animdsl`. Three modules under
`no.virtual-architect:animdsl-<kebab>`:

- `core` — Timeline ADT + Prop/Easing/Trigger/Fill/RepeatCount enums + AnimBackend typeclass (no deps)
- `svg` — SvgBackend (Timeline → tagless Node = SMIL elements); JVM + JS
- `ooxml` — OoxmlBackend (Timeline → PresentationML `<p:timing>` tree); **JVM only**

Both backends depend on `no.virtual-architect:tagless-core:0.1.0-SNAPSHOT`
(cross-repo publishLocal — second use of the pattern after shapesdsl).

Created:

- `sources/tmp/animdsl.md` — bridge (uncommitted-tree state)
- `sources/summaries/animdsl.md` — distilled summary
- `projects/animdsl/{index, log}.md`
- `projects/animdsl/adr/0001-adopt-functional-domain-design.md`
- `projects/animdsl/adr/0002-deviate-deps-single-file.md` (uses the
  richer deviation schema with rationale / severity / mitigated_by
  that the user introduced on the tagless/shapesdsl ADRs)

Touched:

- `index.md` §Projects — added animdsl row
- `tech/patterns/functional-domain-design` — added
  `projects/animdsl/adr/0001` to `used_by`
- `tech/decisions/deps-single-file` — added
  `projects/animdsl/adr/0002` to `used_by` (deviation)
- `tech/guides/breakout` §Existing Breakouts — added animdsl row

Four observations worth flagging:

1. **Fifth consecutive deviation from
   [[tech/decisions/deps-single-file]].** sourceline-manager,
   toolbox-pre-DM, tagless, shapesdsl, animdsl. The carve-out
   hypothesis is over-determined. Strong recommendation: extend
   [[tech/decisions/deps-single-file]] with a "fine-grained
   standalone breakout" exception, marking the five existing
   per-project deviation ADRs as `superseded` once that lands.
2. **Cleanest expression of `functional-domain-design` in the
   family.** `core` is 12 source files of pure ADTs + a typeclass
   — no phantom types, no type-state, no extension-heavy DSL. Just
   `enum Timeline`, four orthogonal enums, one `case class KF`, one
   `opaque type ShapeRef`, one `AnimBackend[A]` typeclass.
   `projects/animdsl/adr/0001` makes the case that animdsl
   exercises the *expression-problem inverse* (free to add new
   interpreters) that the prior worked examples did not exercise as
   crisply.
3. **Zero structural code changes during the breakout.** Unlike
   tagless (3 moves) and shapesdsl (1 move), animdsl had no
   intra-module cycles in the source. `core` has zero references
   to `svg` or `ooxml`. The breakout is a pure relocation. This
   matches the cleanliness expected from a codebase whose layout
   was designed up-front in the spec document.
4. **Design doc vs implementation divergences.** The design doc §7
   recommends `cats-core` (for `NonEmptyList`) and `scala-xml` (for
   backend output). The actual implementation rolls a tiny in-tree
   `Nel` and returns `tags.Node` from both backends to share
   rendering infra with the family. Flagged for a future design-doc
   refresh.

Build verified: `mill resolve __` ✓, `mill __.compile` ✓ (5 compile
targets: core+svg × 2 platforms, ooxml × 1), `mill __.fastLinkJS`
✓, `mill svg.jvm[3.8.3].test.testForked` ✓ (SvgAnimAttrsSpec — the
only test upstream), `mill __.publishLocal` ✓ (5 artifacts in
`~/.ivy2/local`).

Remaining sibling breakout: presenter (next).

Refs: [[sources/tmp/animdsl]] · [[sources/summaries/animdsl]] ·
[[projects/animdsl]] · [[tech/guides/breakout]]

---

## [2026-05-29] lint | second remediation pass — DRIFT-027 / 030 closed + DRIFT-032 partial

Human asked which of the remaining open items the agent could
close without further input. Three more closed:

- **DRIFT-027**: restructured malformed `deviations:` blocks on
  `projects/tagless/adr/0002-deviate-deps-single-file.md` and
  `projects/shapesdsl/adr/0002-deviate-deps-single-file.md` from
  bare-path lists to the schema-mandated
  `{page, rationale, severity, mitigated_by}` shape. Content
  lifted from each ADR's existing §Context + §Decision body
  sections — no new claims, no severity escalation (`low` to
  match siblings). The breakout template that produced the
  malformation should be patched in `tech/guides/breakout.md` so
  future breakouts don't reintroduce the bug; not done this pass.
- **DRIFT-030**: refreshed §Adopters / §Open Questions prose on
  three pattern pages. FDD's §Adopters table grew from 2 rows to
  6 with shape characterisations per project; safetensors-scala
  is now named as the in-scope missing-stance project.
  `tdd-rhythm.md` and `symmetric-refactoring.md` §"Open Questions"
  first bullets replaced "X and Y are in scope; both lack adoption
  ADRs" framings with the actual adoption matrix and DRIFT-024
  cross-links. `symmetric-refactoring.md` also picked up a new
  bullet noting the operator-layer vs parallel-module form
  distinction (dm being the single data point for the latter).
- **DRIFT-032 partial**: top-level `index.md` already carries a
  `shapesdsl` row (added between lint sweeps); only the `git add`
  for the three untracked paths remains.

Open count drops from 8 to 6. Active mechanical work: **none**.
Remaining open items are all human-gated (DRIFT-024 ADR
sequencing, DRIFT-028 wiki-shape promotion-vs-rewrite call,
DRIFT-032 git-add) or carryover-by-design (DRIFT-013 / 014 / 015).

Refs: [[meta/drift]]

---

## [2026-05-29] lint | mechanical remediation — DRIFT-025 / 026 / 031 closed

Human-requested follow-up to the lint sweep below. Three
mechanical drifts closed in the same session:

- **DRIFT-025**: dropped `*(draft)*` annotation on the
  `test-economics` line in `tech/index.md`. Page has been
  `accepted` since 2026-05-29 promotion.
- **DRIFT-026**: `kind: design-doc` → `kind: descriptive` on
  `projects/dependency-manager/designs/dm-architecture-2026q2-refresh.md`.
  Only invalid `kind` value on disk; brings the page into schema
  conformance (status remains `superseded`).
- **DRIFT-031**: added `projects/shapesdsl/adr/0001-adopt-functional-domain-design.md`
  to `tech/patterns/functional-domain-design.md` `used_by`; added
  `projects/shapesdsl/adr/0002-deviate-deps-single-file.md` to
  `tech/decisions/deps-single-file.md` `used_by`. Bidirectional
  integrity restored — `used_by` now matches every `adopts:` /
  `deviations:` claim on the project side.

Drift report Summary table updated; resolved entries condensed to
two-line closure stubs. Open count drops from 11 to 8 (effectively
6 + the 17-cell DRIFT-024 matrix).

Mechanical drifts remaining: DRIFT-027 (bare-path `deviations:`
on tagless/0002 + shapesdsl/0002 — restructure pending) and
DRIFT-030 (stale §Adopters / §Open Questions prose on three
pattern pages — deferred until DRIFT-024 closes for a stable
rewrite state).

Refs: [[meta/drift]]

---

## [2026-05-29] lint | post-tagless / post-shapesdsl / post-deploymentbox-v2 sweep

Full lint after a high-volume day: tagless breakout (14 modules, 2
ADRs), shapesdsl breakout (3 modules, 2 ADRs, **all untracked in
git**), deploymentbox v1 → v2 supersession (6 ADRs, 2 designs), and
dm's tdd-rhythm + symmetric-refactoring adoption ADRs landing on
the same day the patterns went `accepted`.

### Snapshot

- 8 on-disk projects (was 5 last lint): `compositor`,
  `sourceline-manager`, `toolbox`, `safetensors-scala`,
  `dependency-manager`, **`tagless`**, **`shapesdsl`**,
  **`deploymentbox`**.
- 6 accepted normative pages + 1 draft (`tidy-first-commits`,
  unchanged).
- 5 external-lib bridges (`mill`, `kyo`, `airstream`,
  `toml-scala`, `microvm-nix`).

### Drift delta vs previous run

**Closed (carried to historical)**: DRIFT-023 (all three
sub-findings closed by the 2026-05-29 commit sweep — already
recorded in previous drift report).

**Opened (8 new entries)**:

| ID | Severity | Subject |
|----|----------|---------|
| DRIFT-024 | medium | Post-promotion fan-out — 17 missing-declaration cells across 5 projects × 3–4 patterns. Supersedes DRIFT-020. |
| DRIFT-025 | low | `tech/index.md` flags `test-economics` as `(draft)`; page is `accepted`. |
| DRIFT-026 | low | `dm-architecture-2026q2-refresh.md` uses invalid `kind: design-doc`. |
| DRIFT-027 | low | tagless ADR-0002 + shapesdsl ADR-0002 have bare-path `deviations:` instead of `{page, rationale, severity, mitigated_by}`. |
| DRIFT-028 | medium | deploymentbox ADR-0006 `adopts` a `descriptive` source summary; POLICY requires `normative status: accepted`. |
| DRIFT-029 | low | deploymentbox ADR-0006 `exceptions:` / `deviations:` use `layer:` instead of `page:`. Consequential to DRIFT-028. |
| DRIFT-030 | low | Stale §Adopters / §Open Questions prose in `functional-domain-design.md`, `tdd-rhythm.md`, `symmetric-refactoring.md`. |
| DRIFT-031 | low | shapesdsl ADRs not back-referenced in `functional-domain-design.md` and `deps-single-file.md` `used_by`. |
| DRIFT-032 | info | `projects/shapesdsl/` + 2 sources/tmp + summaries paths untracked in git; project missing from `index.md`. |

**Carryover (unchanged)**: DRIFT-013, DRIFT-014, DRIFT-015.
DRIFT-020 superseded by DRIFT-024 (same root issue, wider scope).

### Bidirectional integrity verified

- `deps-single-file.md` `used_by` cross-checked against 8 cited
  ADRs: 7 of 8 listed back-references match an `adopts` /
  `deviations` claim on the ADR side; **shapesdsl/0002 is the
  one missing back-reference** (DRIFT-031).
- `functional-domain-design.md` `used_by` cross-checked against
  5 cited ADRs: 5 of 6 actual adopting ADRs are listed;
  **shapesdsl/0001 is the one missing back-reference** (DRIFT-031).
- `tdd-rhythm.md` / `symmetric-refactoring.md` / `test-economics.md`
  `used_by`: every listed ADR exists and adopts; no fabrications.

### Notable observations

- **First time the wiki has a normative ADR pointing at a
  `descriptive` page** (DRIFT-028). The author flagged it in the
  deploymentbox log entry the same day — the violation is
  acknowledged, not unnoticed. The resolution path is a wiki-shape
  call: either promote a `tech/patterns/defense-in-depth.md` from
  the paranoid-NixOS summary (POLICY admits one-project promotion
  when the solution is clearly reusable) or rewrite ADR-0006 body-
  only and clear `compliance.adopts`. Neither is purely mechanical.
- **The 17-cell fan-out (DRIFT-024) is the dominant finding**.
  It's the expected post-promotion shape: four patterns went
  `accepted` on 2026-05-29 against a project cohort that grew
  from 5 to 8 the same day. The cells split roughly: compositor 3
  (carryover from DRIFT-020), safetensors-scala 4 (the only
  project missing FDD), toolbox 3, tagless 3, shapesdsl 3, dm 1
  (test-economics only).
- **Schema drifts are low-volume but real** (DRIFT-025 / 026 /
  027). The tagless and shapesdsl `deviations:` malformation
  shares a template — both breakouts produced the same bare-path
  shape. Worth fixing at the source if `tech/guides/breakout.md`
  ships an ADR template snippet.
- **shapesdsl integration is half-finished** (DRIFT-032). Four
  on-disk files untracked, missing from top-level `index.md`. The
  ADRs themselves are well-formed and well-located; the
  registration sweep just didn't complete. Cheap to close.

### What this run did NOT do

- Did **not** draft any of the 17 DRIFT-024 cells. Volume +
  per-project ADR-shape calls (adopt vs ignore vs forward-look
  for symmetric-refactoring on projects with no operator
  catalogue) warrant human sequencing.
- Did **not** auto-fix DRIFT-025 / 026 / 031 even though they are
  one-line mechanical edits. Deferred to a remediation pass so
  the next lint sees a clean delta.
- Did **not** rewrite the stale §Adopters / §Open Questions prose
  flagged by DRIFT-030. Defer until DRIFT-024 is largely closed
  so the rewrite is from a stable state.

Refs:
[[meta/drift]],
[[projects/tagless/log]],
[[projects/shapesdsl/log]],
[[projects/deploymentbox/log]],
[[projects/dependency-manager/log]]

---

## [2026-05-29] ingest | shapesdsl — second of four sibling breakouts from /p/v42/tagless

Executed `breakout` on the 2D shape + heatmap DSL family. Second of
the four sibling breakouts forecast in the tagless ingest entry
(tagless → shapesdsl → animdsl → presenter). Sequencing forced by
the cross-repo dep: `shapesdsl-svg` consumes `tagless-core` via
publishLocal SNAPSHOT, so `tagless` had to be `mill __.publishLocal`'d
before this run.

Destination: `/p/hg/shapesdsl`. Three modules under
`no.virtual-architect:shapesdsl-<kebab>`:

- `core` — Shape ADT, ShapeScene, ShapeStyle, ColorScale, Effect, dsl (no deps)
- `heatmap` — Heatmap ADT; JVM-only HeatmapImage (Java2D) + HeatmapDemo
- `svg` — SvgShapeInterpreter; depends on `tagless-core`

The source's two-module structure (`shapesdsl`, `shapesdslsvg`) split
further into three to keep `core` free of the Java2D + Heatmap weight
and free of the cross-repo `tagless-core` dep.

Created:

- `sources/tmp/shapesdsl.md` — bridge (staged; human promotes after
  initial commit)
- `sources/summaries/shapesdsl.md` — distilled summary
- `projects/shapesdsl/{index, log}.md`
- `projects/shapesdsl/adr/0001-adopt-functional-domain-design.md`
- `projects/shapesdsl/adr/0002-deviate-deps-single-file.md`

Touched:

- `index.md` §Projects — added shapesdsl row (alphabetised)
- `tech/patterns/functional-domain-design` — added
  `projects/shapesdsl/adr/0001` to `used_by`
- `tech/decisions/deps-single-file` — added
  `projects/shapesdsl/adr/0002` to `used_by` (deviation)
- `tech/guides/breakout` §Existing Breakouts — added shapesdsl row

Three observations worth flagging:

1. **Fourth consecutive breakout to deviate from
   [[tech/decisions/deps-single-file]].** sourceline-manager,
   toolbox-pre-DM, tagless, shapesdsl. The carve-out hypothesis is
   now well-supported — worth drafting a "fine-grained standalone
   breakout" exception in the decision itself rather than continuing
   per-project deviation ADRs.
2. **Cross-repo publishLocal pattern works cleanly.** First time we
   have a `/p/hg/<a>` depending on a `/p/hg/<b>` artifact. Pattern:
   carry the upstream version as `V.<name>: String = "0.1.0-SNAPSHOT"`
   in the consumer's `object V`; reference as
   `mvn"${V.organization}::<upstream-module>::${V.<name>}"`. Mill
   resolves `_3` vs `_sjs1_3` from the consuming Cross variant.
   Worth adding to [[tech/guides/breakout]] §Phase 4 as a recipe.
3. **`Scala.js sub-package conflict`** — first attempt placed the
   moved `heatmap[T]` factory in a sub-package `package shapesdsl.heatmap`.
   JS compilation rejected it with "Trying to define package with
   same name as class heatmap". JVM was fine. Root cause unclear
   (the only `Heatmap`-shaped name in scope is the uppercase case
   class; case sensitivity should not collide). Worked around with
   a top-level `object Heatmaps` in `package shapesdsl`. Flagged in
   [[sources/summaries/shapesdsl]] §Observations as worth a pitfall
   entry in [[tech/guides/mill-cross-platform]] if it recurs.

Build verified: `mill resolve __` ✓, `mill __.compile` ✓ (3 modules
× 2 platforms), `mill __.fastLinkJS` ✓, per-module `testForked` ✓
across all three modules, `mill __.publishLocal` ✓ (6 artifacts in
`~/.ivy2/local`).

Refs: [[sources/tmp/shapesdsl]] · [[sources/summaries/shapesdsl]] ·
[[projects/shapesdsl]] · [[tech/guides/breakout]]

---

## [2026-05-29] implement | deploymentbox v2 — Firecracker microVM + MinIO + SHA verify + paranoid-NixOS hardening

User pushed back on the v1 design (registered earlier the same day)
on the grounds that the *deploymentbox host itself* was still the
build environment — a malicious dep in any library's flake could
execute on the host during `mill compile` / `nix develop` and
reach the Sonatype token and gpg-agent. The v1 ADRs answered
"laptop is the build env" by moving it to Hetzner; v1 didn't answer
"Hetzner box is the build env." User explicitly chose Firecracker
("safest minimal VM I know") and asked for SHA verification of the
handoff.

Same session: user pointed at the
[[sources/summaries/paranoid_nixos_xe_iaso]] summary (also ingested
earlier 2026-05-29) and asked which layers transfer to the
deploymentbox.

v2 architecture:

- Build moves inside a **Firecracker microVM** declared via
  `microvm.vms.build-sandbox` on an internal `microvm0` bridge.
- **MinIO** (single-node, bound to bridge IP only) handles artifact
  handoff: microVM puts to `builds/<id>/`, host reads.
- **SHA-256 manifest** emitted by microVM, verified by host before
  signing. Integrity check, not provenance.
- **YubiKey + gpg forwarding unchanged** from v1 — signing happens
  on the host, key still lives only on the YubiKey.
- **Selected paranoid-NixOS layers** adopted at the host: auditd
  execve, `noexec` writable mounts, `defaultPackages = []`,
  restricted `nix.settings.allowed-users`, MinIO `Protect*` flags,
  kernel sysctls. tmpfs-root + impermanence *deferred* with
  recorded expiry condition. Tailscale-only *excepted* (already
  rejected by v1 ADR-0002).

Created:

- `projects/deploymentbox/designs/release-pipeline-v2-microvm.md` —
  v2 design (architecture, secrets map, timing table, file
  inventory, open questions).
- `projects/deploymentbox/adr/0005-build-in-firecracker-microvm.md`.
- `projects/deploymentbox/adr/0006-adopt-paranoid-nixos-hardening.md`.

Updated:

- `projects/deploymentbox/designs/release-pipeline.md` — marked
  `status: superseded`; `superseded_by:` set; preserved as
  historical record.
- `projects/deploymentbox/index.md` — stack, role diagram, ADR
  list, open questions all updated for v2.
- `projects/deploymentbox/log.md` — implement entry preserving
  the decision walk.
- `index.md` §Projects — row updated to reflect v2 stack and
  design.
- `sources/tmp/code/deploymentbox.md` — bridge updated with v2
  file inventory.

Repo scaffold at `/p/hg/deploymentbox/` extended with: `microvm.nix`
flake input, `modules/microvm-host.nix` (host module + bridge +
NAT), `modules/minio.nix`, `modules/hardening.nix`,
`microvms/build-sandbox/configuration.nix`,
`microvms/build-sandbox/build-job.sh`, rewritten
`scripts/release.sh`, extended `scripts/bootstrap.md`. Existing
modules updated where v2 requires (release user gains `mc`;
firewall opens DHCP and MinIO on the internal bridge only).

Notable observations:

- **First wiki use of the microvm.nix llm-wiki mid-design.**
  Hypervisor matrix + declarative recipe pages let the design
  walk converge in ~5 minutes. The external-lib wikis paying off
  for *in-progress* design work (not just post-hoc reference) is
  the use case
  [[syntheses/wiki-layering-and-external-lib-wikis]] argued for.
  Counts as evidence.
- **First wiki ADR that explicitly adopts a sources/summaries/
  page** as its `compliance:` source (ADR-0006 cites
  `sources/summaries/paranoid_nixos_xe_iaso.md` in `adopts:`).
  Normal pattern for `compliance:` is referencing
  `tech/decisions/*` or `tech/patterns/*`; we don't have a
  hardening pattern yet, and the source-summary is the closest
  written ground. If a `tech/patterns/defense-in-depth.md` ever
  promotes from the paranoid-NixOS source, ADR-0006 should be
  re-pointed.
- **Supersession semantics exercised.** v1 design ↔ v2 design via
  `superseded_by`/`supersedes` is the first time the wiki has
  exercised supersession on a same-day design pair. Frontmatter +
  a top-of-page banner on the superseded doc; v1's ADRs inherited
  unchanged into v2. Worth carrying as a pattern: not every
  superseded doc deletes — when the historical walk matters (and
  here it does for "alternatives we already rejected" context),
  preserve and link.

Refs:
[[projects/deploymentbox/designs/release-pipeline-v2-microvm]],
[[projects/deploymentbox/designs/release-pipeline]] (superseded),
[[projects/deploymentbox/adr/0005-build-in-firecracker-microvm]],
[[projects/deploymentbox/adr/0006-adopt-paranoid-nixos-hardening]],
[[sources/summaries/paranoid_nixos_xe_iaso]],
[[microvm.nix/llm-wiki/index]]

## [2026-05-29] ingest | tagless — fine-grained breakout from /p/v42/tagless

Executed `breakout` on the HTML-DSL family extracted from the
monolithic source at `/p/v42/tagless`. Human's call was **option D +
option C** — granular ten-way split of the source's `tags` module
into focused artifacts, executed as a single repository, with
shapesdsl / animdsl / presenter explicitly deferred to sibling
breakouts. Motivation: each artifact must be flippable between
open-source and internal-only individually; mill `publishLocal`
SNAPSHOTs wire downstream consumers.

Destination: `/p/hg/tagless`. Fourteen modules under
`no.virtual-architect:tagless-<kebab>`:

- Pure-types leaves — `htmlid`, `i18n`
- Cursor algebra — `core` (depends on htmlid + i18n + raquo/domtypes)
- Specialized DSLs — `md`, `meta`, `page`, `form`, `table`, `crud`,
  `route`, `viz`, `htmx`, `svg`
- JS-only runtime — `events` (depends on htmlid + Airstream)

Created:

- `sources/raw/code/tagless.md` — bridge (promoted from `sources/tmp/`
  after initial commit `7e2ebe8`)
- `sources/summaries/tagless.md` — distilled summary
- `projects/tagless/{index, log}.md`
- `projects/tagless/adr/0001-adopt-functional-domain-design.md`
- `projects/tagless/adr/0002-deviate-deps-single-file.md`

Touched:

- `index.md` §Projects — added tagless row (alphabetised among
  `active` rows)
- `tech/patterns/functional-domain-design` — added
  `projects/tagless/adr/0001` to `used_by`
- `tech/decisions/deps-single-file` — added
  `projects/tagless/adr/0002` to `used_by` (deviation)
- `tech/guides/mill-cross-platform` — added `projects/tagless` to
  `used_by`

Three structural notes worth flagging:

1. **Third consecutive breakout to deviate from
   [[tech/decisions/deps-single-file]]** (after sourceline-manager
   and toolbox-pre-DM). If a fourth deviates with the same shape,
   consider a carve-out in the decision rather than per-project
   ADRs.
2. **Three modules carry package-vs-directory mismatches** — `md`
   declares `package md`, `form` declares `package html.lib.form`,
   `table` declares `package html.lib.table`. Preserved verbatim
   per breakout rule. Surfaced as a follow-up rename pass in
   [[projects/tagless/log]].
3. **`core ↔ viz` and `core ↔ route` cycles broken** during the
   split by moving the visualization (`visualize`, `toD3Json`,
   `toAsciiTree`, `toMermaid`, `asComponent`) and route
   (`asRoute`) cursor extensions from the source's
   `tags/src/tags/dsl.scala` into `viz/src/tags/viz/dsl.scala`
   and `route/src/tags/route/dsl.scala`. The only structural code
   change made during the breakout; documented in the project log.

Build verified: `mill resolve __` ✓, `mill __.compile` ✓ (14 modules
× 2 platforms), `mill __.fastLinkJS` ✓. Per-module
`testForked` ✓ except two pre-existing upstream `Fragment.hiddenSection`
failures in `core.jvm.test` (source emits `class="hidden"`, tests
expect `class="is-hidden"`). Not introduced by the breakout.

Sibling breakouts (`shapesdsl`, `animdsl`, `presenter`) are explicit
follow-up operations; they are not yet executed.

Refs: [[sources/raw/code/tagless]] · [[sources/summaries/tagless]] ·
[[projects/tagless]] · [[tech/guides/breakout]]

---

## [2026-05-29] ingest | Xe Iaso — Paranoid NixOS Setup (2021-07-18)

Ingested xeiaso.net/blog/paranoid-nixos-2021-07-18/ — a long-form
hardening recipe for NixOS hosts. Third Nix-adjacent source after
[[sources/summaries/github_actions_nix_cachix_dhall_gvolpe]] and
[[sources/summaries/nix_dev_ci_github_actions]] (both build-side).
This one covers the runtime posture: tmpfs root + impermanence,
`noexec` everywhere but `/nix/store`, restricted `nix.allowedUsers`,
systemd `Protect*` unit options, Tailscale-only SSH, auditd with
off-host log shipping.

Created:

- `sources/tmp/paranoid_nixos_xe_iaso.md` — raw extraction (staged;
  human decides whether to promote to `sources/raw/docs/`).
- `sources/summaries/paranoid_nixos_xe_iaso.md` — summary with
  defense-in-depth layer table, modern-option translation table
  (pre-flake `nixos-21.05` → current), and explicit mapping onto
  the deploymentbox project that landed earlier in the same
  session.

Notable observations:

- **deploymentbox is now the concrete anchor.** The previous
  [[meta/log#paranoid-nixos…]] line of reasoning ("no consumer
  yet, defer") was overtaken in this session by the
  [[projects/deploymentbox/index]] registration. The summary
  records which layers deploymentbox already adopts (the SSH
  hardening of [[projects/deploymentbox/adr/0002-public-ssh-hardened]]),
  which it explicitly rejects (Tailscale-only SSH — one operator,
  one laptop), and which remain plausibly applicable but
  unaddressed (tmpfs root + impermanence + `noexec`,
  `nix.settings.allowed-users` restriction, systemd `Protect*`
  flags, auditd execve logging).
- **Author framing is the most transferable artefact.** The
  "annoy the attacker enough that they give up" + per-layer
  bounded-responsibility framing is pattern-shaped, but one source
  on one platform is thin evidence. A future
  `tech/patterns/defense-in-depth.md` would need a second
  corroborating source before promotion.
- **Impermanence as security, not tidiness.** The post reframes
  tmpfs root + impermanence as bounding attacker dwell-time, not
  config hygiene. Worth carrying into a future deploymentbox
  hardening pass.
- **Pre-flake option drift.** The post uses `nix.allowedUsers`,
  `services.openssh.passwordAuthentication`, etc. — names that
  have moved under `nix.settings.*` / `services.openssh.settings.*`
  in current NixOS. Summary records the mapping table; any
  guide-level promotion would need full re-validation.
- **No promotion candidates from this ingest.** The deploymentbox
  consumer is too early to justify a `tech/guides/paranoid-nixos.md`
  (writing one now would either pre-empt its decisions or document
  only its current narrow scope). Revisit when deploymentbox has
  a second hardening pass or a second NixOS host lands.
- **Open gaps explicit in the summary:** secrets on tmpfs
  (sops-nix / agenix), `/nix/persist` backup strategy, `/boot`
  integrity (secure boot / lanzaboote), and the detection-side
  runbook for the auditd execve stream.

Refs: [[sources/summaries/paranoid_nixos_xe_iaso]],
[[sources/tmp/paranoid_nixos_xe_iaso]],
[[projects/deploymentbox/index]],
[[projects/deploymentbox/adr/0002-public-ssh-hardened]],
[[sources/summaries/nix_dev_ci_github_actions]],
[[sources/summaries/github_actions_nix_cachix_dhall_gvolpe]]

## [2026-05-29] ingest | deploymentbox registered as wiki project

Registered `deploymentbox` — a single-purpose hardened NixOS host on
Hetzner Cloud whose role is to build and publish signed Maven Central
artifacts for the `no.virtual-architect` libraries living under
`/p/hg/`. The host is the architectural answer to the supply-chain
concern raised earlier in the same 2026-05-29 conversation (laptop
compromise as injection vector) without surrendering signing-key
isolation (the YubiKey stays on the operator's laptop and is reached
over an SSH-forwarded gpg-agent socket at release time).

Created:

- `projects/deploymentbox/index.md`, `log.md`
- `projects/deploymentbox/designs/release-pipeline.md` — the
  architectural source of truth (end-to-end flow, secrets map,
  alternatives considered, open questions including the YubiKey key
  ceremony deferred to its own session).
- Four ADRs: `0001-host-hetzner-nixos`, `0002-public-ssh-hardened`,
  `0003-signing-yubikey-forwarded`, `0004-tag-driven-central-releases`.
  Together they capture the conversation's decision history without
  scattering it across implicit code state.
- `sources/tmp/code/deploymentbox.md` — bridge staged for promotion
  to `sources/raw/code/` once the human makes the initial commit at
  `/p/hg/deploymentbox/`.

Updated:

- `index.md` §Projects — new row between `dependency-manager` and
  the planned `webapp`.

Notable observations:

- **First wiki-managed infrastructure project.** Prior `/p/hg/`
  projects are Scala libraries (toolbox, sourceline-manager,
  safetensors-scala) or build tooling (dependency-manager). This is
  the first one whose unit of delivery is a *running host*. The
  schema fits as-is — ADRs name decisions, design docs name
  architecture — but the project deviates from every existing tech-
  layer normative page on the same grounds (NixOS config is not
  Scala source).
- **Decision history preservation.** The four ADRs preserve the
  conversational walk (laptop-only → GitHub-hosted → self-hosted
  VPS → Hetzner NixOS box) in their "Alternatives Considered"
  sections, so a future "should we just run releases from the
  laptop?" suggestion can be answered with written ground rather
  than relitigated from scratch.
- **YubiKey-not-on-the-box is the load-bearing property.** The whole
  architecture is *only* defensible because the signing key lives
  in hardware on the operator's desk and never traverses the
  network in usable form. ADR-0003 records this as a contract:
  any future change that would put a software signing key on the
  box (or in a GitHub Secret) is explicitly out of scope and must
  reopen this ADR. The Sonatype token, by contrast, is on the box —
  rotatable, no signature forgery risk if leaked.
- **No promotions from this ingest.** All four ADRs are project-
  internal (no `tech/decisions/` counterparts exist). If a second
  infra project lands later (e.g. a per-customer release host),
  patterns common across NixOS infra configs become promotion
  candidates; a single data point is not enough.
- **Volpe-ingest connection.** The "GitHub Actions for tests only,
  build elsewhere with Nix-pinned toolchain" posture sketched in
  [[sources/summaries/github_actions_nix_cachix_dhall_gvolpe]] (and
  staged earlier in the same 2026-05-29 session) is *partially*
  realised here: the deploymentbox is the "build elsewhere" target;
  test-only GitHub Actions in each library repo remain a per-library
  concern out of scope for this project. The Volpe ingest is the
  closest existing wiki reference for the per-library `nix develop
  --command mill …` pattern this design relies on.

Refs: [[projects/deploymentbox/index]],
[[projects/deploymentbox/designs/release-pipeline]],
[[projects/deploymentbox/adr/0001-host-hetzner-nixos]],
[[projects/deploymentbox/adr/0002-public-ssh-hardened]],
[[projects/deploymentbox/adr/0003-signing-yubikey-forwarded]],
[[projects/deploymentbox/adr/0004-tag-driven-central-releases]],
[[sources/tmp/code/deploymentbox]],
[[sources/summaries/github_actions_nix_cachix_dhall_gvolpe]]

## [2026-05-29] commit | /p/hg/* commit sweep (4 repos, 5 commits)

Single-session sweep covering pending DM work in three sibling
repos plus the dm DESIGN.md option-B strip. All commits per the
personal-repo policy ([[feedback_hg_repo_commit_policy]]):
unsigned (`-c commit.gpgsign=false`), no `Co-Authored-By`
trailer, author `tigidar`.

| Repo | SHA | Subject |
|---|---|---|
| dependency-manager | `3482be3` | docs: strip DESIGN.md to decisions archive (option B) |
| safetensors-scala | `a8a60e8` | adopt dm catalog (DM-002): build.mill consumes Deps.*; deps/ generated; ADR-0002 supersedes ADR-0001 |
| sourceline-manager | `e21a58d` | monoid laws + SourceLine primitives + StringUtils composition specs |
| sourceline-manager | `b22cb55` | adopt dm catalog (DM-001): build.mill consumes Deps.*; deps/ generated |
| toolbox | `2b2a828` | Initial toolbox v1 — 10 modules + dm catalog adoption (102 files, 16640 insertions) |

Branch renames `master` → `main` applied to dm and
safetensors-scala (the other two were already on `main`). All
four repos now consistent.

### slm split rationale

slm's working tree had two distinct stories tangled — split as
two atomic commits rather than bundled:
- **e21a58d**: monoid-laws + primitives (SourceLine.scala
  extensions + 6 new test files + refactor of existing specs
  to delegate to the property-based suites).
- **b22cb55**: DM-001 catalog adoption (build.mill + deps/ +
  flake.lock).

### toolbox bundling rationale

toolbox had zero prior commits — the entire v1 surface (102
files) plus the DM-001 migration landed as one "Initial
toolbox v1" commit. Splitting the migration out would have
made the initial commit weirdly partial (no migrated
build.mill alongside the 10 modules). Conventional for an
initial commit.

### DRIFT-023 resolution

This sweep closed the last open sub-finding of DRIFT-023 (#3,
DM-007 in-tree apply via option B). DRIFT-023 is now fully
resolved.

Refs:
[[projects/dependency-manager/tickets/0007-refresh-in-tree-design]],
[[projects/dependency-manager/log]],
[[projects/toolbox/log]],
[[projects/sourceline-manager/log]],
[[projects/safetensors-scala/log]],
[[meta/drift]]

---

## [2026-05-29] promote | dm source bridge tmp → raw (DM-006)

Promoted `sources/tmp/code/dependency-manager.md` to
`sources/raw/code/dependency-manager.md` after DM-005 landed the
first commit. Bridge frontmatter now carries
`commit: 5459ddb7dc4ceb882ea89b2054e5814b9383f313` and
`branch: master`; entry_points list expanded to cover the full
v1 surface (catalog/*, mill/, test/*); the obsolete
`git_init_state` field removed.

The body was refreshed from the tmp version to reflect post-v1
reality — every "Current state" row flipped from
`stub`/`error`/`not initialised` to `working`/populated/SHA.
"Open Questions" trimmed to 3 deferred items (factory, Native,
platforms-in-catalog).

### Wiki references rewritten

7 live referrers updated:
- `projects/dependency-manager/index.md` §Code Location
- `sources/summaries/dependency-manager.md` (frontmatter sources + Links)
- `projects/dependency-manager/adr/0001-deviate-deps-single-file.md` §Links
- `projects/dependency-manager/adr/0002-adopt-functional-domain-design.md` §Links
- `projects/dependency-manager/designs/dm-architecture.md` (frontmatter sources + Links)

Historical log entries and tickets that mention the tmp path
were left alone — they document the state at write time.

`meta/drift.md` DRIFT-023 marked **partially resolved**:
sub-findings #1 (DM-005) and #2 (DM-006) closed; sub-finding #3
(DM-007 in-tree apply) remains open by design.

Refs:
[[projects/dependency-manager/tickets/0006-promote-source-bridge]],
[[sources/raw/code/dependency-manager]],
[[meta/drift]]

---

## [2026-05-29] commit | dm first commit (DM-005, agent on behalf)

Per the personal-repo commit policy
([[feedback_hg_repo_commit_policy]]) the first commit is
human-gated. Human approved agent-on-behalf execution in the
DM-009 close-out reply.

- **SHA**: `5459ddb7dc4ceb882ea89b2054e5814b9383f313`
- **Branch**: `master`
- **Author**: `tigidar 162025401+tigidar@users.noreply.github.com`
- **Signature**: none (`%G?` → `N`); used `-c commit.gpgsign=false`
  to override any global signing default without touching config.
- **Trailer**: no `Co-Authored-By`.
- **Subject**: `Initial dm v1 — catalog + 5 verbs + Renovate + Nix flake + 3 consumers migrated`
- **Files**: 40 changed, 2806 insertions; staged explicitly (no
  `git add -A`).

Rename `master` → `main` is deferred — non-blocking; can land any
time with `git branch -m master main` as a follow-up.

Refs:
[[projects/dependency-manager/tickets/0005-git-init-first-commit]],
[[projects/dependency-manager/log]]

---

## [2026-05-29] lint | DM-009 — dependency-manager MVP plan execution close-out

Final lint pass for the dependency-manager MVP plan. The plan
([[projects/dependency-manager/plans/mvp]]) decomposed into 9
tickets DM-001..DM-009; this entry records the close-out state.

### Ticket disposition

| # | Ticket | Status | Notes |
|---|---|---|---|
| DM-001 | toolbox build.mill migration | **done** | 10 libs, all platforms green |
| DM-002 | safetensors-scala migration | **done** | 3 libs, JVM/JS/Native green |
| DM-003 | Renovate bumps end-to-end | **done** | 3 landed (os-lib, pprint, munit-cats-effect); kyo RC2 rolled back |
| DM-004 | consumer adoption README | **done** | dm README + deps-single-file decision page updated |
| DM-005 | git-init first commit | **agent prep done; awaiting human commit** (human-gated) |
| DM-006 | source bridge promotion | **blocked on DM-005's SHA** |
| DM-007 | DESIGN.md refresh draft | **draft ready; awaiting human in-tree apply** |
| DM-008 | consumer ADR realignment | **done** | 3 new ADRs (slm/0006, toolbox/0003, safetensors-scala/0001); 2 superseded (slm/0002, toolbox/0002) |
| DM-009 | this lint pass | **in progress** (this entry's close completes it) |

Six of nine tickets fully closed; three (DM-005, DM-006, DM-007)
are sequenced human-gated work captured as DRIFT-023 (open by
design).

### Compliance impact

[[tech/decisions/deps-single-file]] `used_by` now lists 6 ADRs
(compositor adopts, slm deviate→superseded + adopt, toolbox
deviate→superseded + adopt, safetensors-scala adopt, dm
deviate). All three new adopt-ADRs share the same
adopt-with-platforms-exception template, severity `low`.

Bidirectional integrity verified: every `used_by` entry has a
matching `adopts:` / `deviations:` claim in the listed ADR's
frontmatter. No fabricated entries.

### New blockers / drift

DRIFT-023 (informational, open-by-design) tracks the three
sequenced gates.

### What still works

`bin/dm verify` reports `all 3 project(s) in sync`. Toolbox
full `mill __.test` (3638 tasks across JVM/JS/Native) green
post-bumps. Safetensors-scala test across all platforms green
post-migration.

The MVP plan is updated to `status: completed` simultaneously
with this entry (acceptance criteria 7/8 met; criterion 6 —
no outstanding drift — substantially met modulo DRIFT-023
which is sequenced human-gated work, not a coherence violation).

Refs:
[[projects/dependency-manager/plans/mvp]],
[[projects/dependency-manager/tickets/0009-lint-and-drift-cleanup]],
[[projects/dependency-manager/log]],
[[meta/drift]]

---

## [2026-05-29] ingest | microvm.nix external-lib wiki

`ingest-external @/p/gh/microvm.nix/` — created `microvm.nix/llm-wiki/`
(6 sections: concepts, hypervisors, options, host, recipes, conventions;
~40 pages total) and the bridge file
`sources/raw/code/microvm-nix.md` at commit `0d49083`. Source: Nix
flake to run NixOS as a MicroVM on eight hypervisors (qemu,
cloud-hypervisor, firecracker, crosvm, kvmtool, stratovirt, alioth,
vfkit). Wiki covers the guest module options, host module + systemd
template services, declarative-vs-imperative MicroVM definitions, the
runner package contract, three networking topologies, store-on-disk vs
host share, and the macOS / vfkit / Rosetta path.

Followed `tech/guides/ingest-external.md` procedure; index.md and
guide updated with the new entry.

Refs: [[sources/raw/code/microvm-nix]],
[[microvm.nix/llm-wiki/index]]

---

## [2026-05-29] ingest | Volpe blog post on Nix-shell + Cachix + Dhall on GitHub Actions

Ingested gvolpe.com/blog/github-actions-nix-cachix-dhall/ (2020-06-02)
during an open conversation on the supply-chain hygiene of a Maven
Central release pipeline for `no.virtual-architect` libraries
(YubiKey signing, Mill builds, GitHub Actions vs self-hosted runner).

Created:

- `sources/tmp/github_actions_nix_cachix_dhall_gvolpe.md` — raw
  extraction (staged; human decides whether to promote to
  `sources/raw/docs/`).
- `sources/summaries/github_actions_nix_cachix_dhall_gvolpe.md` —
  summary with explicit mapping onto the in-flight Maven Central /
  supply-chain conversation.

Article advocates three things, of which only the first transfers
cleanly to our context:

- **`shell.nix` (or flake) pinned per repo, used identically by
  local dev and CI** — *adopt*. Directly answers "I don't trust the
  GitHub runner's preinstalled toolchain." Closest existing wiki
  reference to the Phase-1 CI design under discussion. No existing
  `tech/guides/` page documents the Nix-wrapped-Mill-in-CI pattern.
- **Dhall as a typed alternative to YAML workflows** — *skip*.
  Costs more than it saves at our scale and the user has explicitly
  asked for minimum management. Captured as a negative
  recommendation in the summary, not an anti-pattern (it doesn't
  rise to that).
- **Cachix on every job** — *skip on release jobs*; consider on
  test/PR jobs only if cold-build cost becomes painful. Volpe's own
  data ("I could probably get away without") argues for YAGNI.
  Pulling cached release artifacts through a third-party CDN
  weakens the supply-chain story we're optimising for.

Notable observations:

- **Article silent on artifact signing.** The Scala worked example
  is a microsite `publishSite` using `GITHUB_TOKEN`, not a signed
  Maven Central release. The YubiKey-vs-CI-secret question is not
  addressed and must be answered from elsewhere.
- **Article silent on reproducibility verification as a
  supply-chain control.** Volpe uses Nix to *produce* reproducible
  environments but never proposes "rebuild locally, compare hashes,
  then sign" — the verifier model that came up in this thread on
  2026-05-29.
- **Article predates flakes mainstream.** Uses `fetchTarball` with a
  pinned URL+SHA; we'd use `flake.lock`. Conceptually identical.
- **No promotion candidates from this ingest.** The `shell.nix`
  discipline could become `tech/guides/nix-wrapped-mill-ci.md` *if*
  one of the open-source libraries adopts it in code. Per breakout
  discipline ("a breakout is justified by a *consumer*, not by 'it
  could be reused one day'"), we wait for the code.

Refs: [[sources/summaries/github_actions_nix_cachix_dhall_gvolpe]],
[[sources/tmp/github_actions_nix_cachix_dhall_gvolpe]],
[[tech/guides/mill-cross-platform]], [[tech/stack/mill]]

## [2026-05-29] ingest | dependency-manager registered as wiki project

Ingested `/p/hg/dependency-manager` — the private CLI (`dm`) that
centralises Maven versions across `/p/hg/` repos via a two-file
TOML+YAML catalog and regenerates per-project `deps/Dependencies.mill`.

Created:

- `projects/dependency-manager/index.md`, `log.md`
- `projects/dependency-manager/adr/0001-deviate-deps-single-file.md` —
  third deviation against [[tech/decisions/deps-single-file]] but the
  first whose project IS the *implementation* of a generalised version
  of the same decision. Two expiry paths (dm-extract self-application,
  monorepo embedding) rather than the single embedding-only path the
  other two deviations have.
- `projects/dependency-manager/designs/dm-architecture.md` — wiki-side
  reflection of in-tree `DESIGN.md` (source of truth).
- `sources/summaries/dependency-manager.md` and
  `sources/tmp/code/dependency-manager.md` (bridge staged for
  promotion).

Populated `used_by` on [[tech/decisions/deps-single-file]] with the
new ADR. Added a row to [[index]] §Projects between toolbox and the
planned webapp.

Notable observations:

- **First wiki-managed project whose entire purpose is to automate a
  wiki-resident decision.** dm is the implementation of a generalised
  cross-project version of [[tech/decisions/deps-single-file]]. If
  the wiki later grows a cross-project version-policy page, dm is
  its in-house implementation. Worth a synthesis once at least one
  downstream `Dependencies.mill` has been regenerated end-to-end.
- **Third `/p/hg/` deviation against `deps-single-file`** — with a
  third resolution path. If a fourth project lands with one of these
  three shapes, the case for growing `deps-single-file` to carry a
  "standalone pre-embedding" or "self-applying tool" carve-out gets
  stronger.
- **First private / unlicensed project in the wiki.** Prior projects
  are Apache-2.0; dm is explicitly unlicensed and not for distribution.
  The wiki enforces no licensing policy today — flagged in the
  summary as an open question.
- **Four ADRs deliberately not written** —
  [[tech/patterns/functional-domain-design]],
  [[tech/patterns/tdd-rhythm]],
  [[tech/patterns/symmetric-refactoring]], and
  [[tech/patterns/test-economics]]. The v1 code surface is CLI
  plumbing (Main / Resolve / MillQuery) with two trivial smoke tests;
  no domain ADT, no algebra, no economics signal yet. The ADRs land
  when the code does. [[meta/drift]] will surface the gap in the
  next lint pass — the intended mechanism.
- **Compile error not yet diagnosed.** `DESIGN.md` records it under
  §"Where we stopped". The ingest does not attempt a fix — the
  bridge documents the suspected causes; the next code session
  should reproduce and address.
- **Not git-initialised.** Unlike the toolbox ingest (which did
  `git init`), this ingest leaves the repo without `.git` — per the
  personal-repo commit policy
  (`feedback_hg_repo_commit_policy`), git init and the first commit
  are the human's call. Bridge stays at `commit: uninitialized-tree`.

Refs: [[projects/dependency-manager/index]],
[[projects/dependency-manager/adr/0001-deviate-deps-single-file]],
[[projects/dependency-manager/designs/dm-architecture]],
[[sources/summaries/dependency-manager]],
[[sources/tmp/code/dependency-manager]],
[[tech/decisions/deps-single-file]]

## [2026-05-29] edit | breakout operation added under Knowledge Operations

Added a new knowledge operation `breakout` to [[CLAUDE]] §Processes
and wrote the full procedure at [[tech/guides/breakout]]. The guide
distils the experience from the two recent breakouts
([[projects/sourceline-manager]], [[projects/toolbox]]) into:

- a 7-phase procedure (understand source → create destination repo →
  move sources → generate build → generate flake+README → register in
  wiki → hand off to human),
- a minimum-ADR table (0001 functional-domain-design, 0002
  deps-single-file) and the rule "do not pre-populate empty
  adoption ADRs beyond those two",
- an anti-patterns section (pre-populating ADRs, inventing module
  boundaries, committing in the new repo, writing to
  `sources/raw/code/`, claiming the README is correct without
  checking it), and
- a table of existing breakouts as worked examples.

Linked the new guide from [[tech/index]] §Guides alongside
[[tech/guides/ingest-external]].

Refs: [[CLAUDE]], [[tech/guides/breakout]], [[projects/toolbox]],
[[projects/sourceline-manager]]

## [2026-05-29] promote | toolbox registered as wiki project

Promoted `toolbox` from a code-source-only ingest (earlier today) to
a full wiki project, matching sourceline-manager's shape. Added a
row to [[index]] §Projects between safetensors-scala and the planned
webapp; created `projects/toolbox/` with `index.md`, `log.md`, and
`adr/{0001-adopt-functional-domain-design.md, 0002-deviate-deps-single-file.md}`.
Populated `used_by` on [[tech/patterns/functional-domain-design]]
and [[tech/decisions/deps-single-file]] with the new toolbox ADRs.

`toolbox` is the **second project to deviate** from
[[tech/decisions/deps-single-file]] (first is sourceline-manager).
Both share the "embed into monorepo to conform" resolution. If a
third project lands with the same shape, that decision likely wants
a "standalone pre-embedding" carve-out rather than three deviations.
Flagging for future synthesis.

Refs: [[projects/toolbox/index]],
[[projects/toolbox/adr/0001-adopt-functional-domain-design]],
[[projects/toolbox/adr/0002-deviate-deps-single-file]],
[[tech/patterns/functional-domain-design]],
[[tech/decisions/deps-single-file]],
[[projects/sourceline-manager/adr/0002-deviate-deps-single-file]]

## [2026-05-29] implement | safetensors-scala extracted from palladium

New project promoted from `planned` to `active`:
[[projects/safetensors-scala/index]]. Extraction designed and executed
in one session against
[[projects/safetensors-scala/designs/extract-from-paladium]] and
[[projects/safetensors-scala/plans/extract-from-paladium]] — both move
to `accepted` / `completed` respectively.

- `/p/hg/safetensors-scala@f3df739` — Mill 1.1.2 cross-build (JVM/JS/Native,
  Scala 3.8.3), `no.virtual_architect.safetensors` package, single
  runtime dep (`scodec-core 2.3.3`, pinned to palladium's value).
  17 MUnit tests green per platform; publishLocal jars non-empty
  (verified). Personal-repo commit policy applied.
- `/p/v42/paladium@0c9a7ac` — in-tree files deleted, single thin
  `WeightsLoader.scala` adapter added, mvnDep added to the `Shared`
  trait. JS (41) and Native (43) test suites green incl. adapter +
  `loadWeights` integration. JVM main compile clean; JVM test path
  blocked by pre-existing missing `com.virtually42:shapesdsl_3:0.0.1`
  test dep (unrelated).

**Candidate pattern surfaced**:
[[projects/safetensors-scala/syntheses/library-extraction-via-type-alias-adapter]] —
top-level `type X = ns.X; val X = ns.X` re-exports plus `export` plus
wrap-and-rebind let a monorepo consume an extracted library with **zero
caller import changes** even when the upstream API shape differs.
Confidence medium (one worked example); defer promotion to
[[tech/patterns]] until a second extraction provides evidence — same
shape of restraint we applied to toolbox's *interpreter family naming*.

**Evidence added to existing guides**:
[[tech/guides/mill-cross-platform]] §Pitfalls path math confirmed for
the second project (sourceline-manager was the first). `mill show
<module>.sources` and the `jar tf` empty-jar check together remain the
two-step verification for Pattern B + manual `sharedSrc` hybrids.

**Drift implication**: `safetensors-scala` now in scope for the lint
compliance matrix. ADR-0001 in-repo records the inline-versions
deviation (same shape as
[[projects/sourceline-manager/adr/0002-deviate-deps-single-file]]); no
new wiki-side ADRs needed because all other normative pages either do
not apply (this is a foundation library with no domain logic) or are
not yet enforced (`tdd-rhythm`, `symmetric-refactoring`,
`test-economics`, `functional-domain-design` — opt-in for new code on
each next iteration).

Refs: [[projects/safetensors-scala/index]],
[[projects/safetensors-scala/syntheses/library-extraction-via-type-alias-adapter]],
[[tech/guides/mill-cross-platform]],
[[tech/decisions/deps-single-file]],
`/p/hg/safetensors-scala@f3df739`, `/p/v42/paladium@0c9a7ac`.

## [2026-05-29] ingest | toolbox (composable shell pipelines + process execution)

Ingested `/p/hg/toolbox` — ten-module Mill 1.1.2 build implementing
the re-layout described in `/p/v42/toolbox/new-design.md`. Bridge
file staged at `sources/tmp/toolbox.md` per the
`sources/raw/**`-is-human rule; summary written to
`sources/summaries/toolbox.md`.

Performed `git init` on `/p/hg/toolbox` (branch `main`, signing
disabled, author `tigidar`, per the personal-repo commit policy);
no initial commit recorded. Bridge's `commit:` field is
`uninitialized-tree` and should be updated once the first commit
lands, at which point the bridge can graduate from `sources/tmp/`
to `sources/raw/code/toolbox.md`.

Findings worth flagging:

- README still labels the tree "Phase A — no sources" while ~75
  Scala files exist across the ten target modules. Documentation
  drift, not state drift.
- `toolbox` is **not in [[index]] §Projects**. Four open
  triage questions logged in the bridge: project status, design-doc
  ingest, README correction, initial-commit timing.
- Compliance scan adopts [[tech/patterns/functional-domain-design]],
  [[tech/guides/mill-cross-platform]], [[tech/stack/mill]], partial
  [[tech/stack/kyo]] (only `proc-kyo`); deviates from
  [[tech/decisions/deps-single-file]] on the same grounds as
  sourceline-manager (single inline `object V`).
- Second worked example for [[tech/guides/mill-cross-platform]] —
  this one exercises `src-jvm/` / `src-native/` / `src-js/`
  divergences (sourceline-manager had no platform surface) and
  the JS-side `ModuleKind.ESModule` requirement for `@JSImport`
  of `node:child_process`.
- Candidate pattern for future promotion: **interpreter family
  naming** (`proc` algebra + `proc-oslib` / `proc-node` / `proc-fs2`
  / `proc-kyo` interpreters). Defer until it recurs in another
  project.

Refs: [[sources/summaries/toolbox]], [[sources/tmp/toolbox]],
[[sources/summaries/sourceline-manager]],
[[tech/guides/mill-cross-platform]],
[[tech/patterns/functional-domain-design]]

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

## [2026-05-28] edit | Mill cross-platform pitfalls + SNAPSHOT workflow

Captured three insights from a `sourceline-manager` ↔ `toolbox`
publishLocal migration session:

- `tech/guides/mill-cross-platform.md` gained a *Pitfalls* section
  documenting the `moduleDir` path-math footgun for the Cross[] +
  manual `sharedSources` hybrid (`os.up / os.up / "src"` lands on
  the repo root, not the shared `src/`), plus the silent
  empty-jar / zero-tests failure mode and the
  `mill show <module>.sources` + `jar tf` verification recipe.
- `tech/stack/mill.md` gained a *SNAPSHOT Workflow* section
  explaining that `-SNAPSHOT` versions are Coursier-level (not
  Maven-specific), how `publishLocal` overwrites them silently, and
  the cross-repo iteration loop.
- `tech/stack/mill.md` *Known Issues* gained the empty-jar silent
  failure entry, cross-linking the cross-platform guide.

These came from a real incident: `sourceline-manager` 0.1.0
shipped empty jars on all three platforms because of the path
mistake; consumers compiled green but resolved `Not found: slm`.
Fixed in 0.2.0-SNAPSHOT.

Flagged (not done): toolbox's `deps/` directory uses both
`Versions.mill` and `Dependencies.mill`, which
[[tech/decisions/deps-single-file]] rejects. Migration queued
for a follow-up session.

Refs: [[tech/guides/mill-cross-platform]], [[tech/stack/mill]],
[[tech/decisions/deps-single-file]]

## [2026-05-29] ingest | sourceline-manager (foundation library)

Ingested `/p/hg/sourceline-manager` at commit `e4c15c2b` (date
2026-05-28, "fix: shared-sources path + native 0.5.12 +
0.2.0-SNAPSHOT"). The library models source code as a typed value
algebra (`Token` / `SourceLine` / `SourceFile`) cross-published to
JVM, Scala.js, and Scala Native from one shared source tree.

Created wiki-side artefacts:

- `projects/sourceline-manager/index.md` — new project landing page.
- `projects/sourceline-manager/log.md` — project log.
- `projects/sourceline-manager/adr/0001-adopt-functional-domain-design.md`
  — adopts [[tech/patterns/functional-domain-design]] in its
  declarative encoding, citing the library's in-tree ADR-0001 (ADT
  model) and ADR-0002 (seven principles, monoid laws) as evidence.
- `projects/sourceline-manager/adr/0002-deviate-deps-single-file.md`
  — deviates from [[tech/decisions/deps-single-file]] (inline
  `object V` in `build.mill`; one library dep — `munit`). Deviation
  expires automatically on monorepo embedding (per upstream README)
  or on a second library dependency landing in the project.
- `sources/summaries/sourceline-manager.md` — distilled summary
  covering ADRs, core types + operator inventory, build wiring, and
  the empty-jar history.
- `sources/tmp/sourceline-manager-bridge.md` — staged bridge file
  (`type: code`) for human promotion to
  `sources/raw/code/sourceline-manager.md`. `sources/raw/**` is
  human-owned per `meta/ownership.md`; staging via `sources/tmp/` is
  the agreed pattern.

Populated `used_by` on both global normative pages:
- [[tech/patterns/functional-domain-design]] now lists the new
  adoption ADR alongside the compositor's.
- [[tech/decisions/deps-single-file]] now lists the new deviation
  ADR alongside the compositor's adoption ADR.

Updated [[index]] project table: added `sourceline-manager` as
**active** between compositor and webapp.

Notable: this is the first project to land in the wiki with an
existing on-disk codebase plus in-tree ADRs. The wiki preserves the
in-tree ADRs as authoritative for project-local decisions
(`docs/adr/0001..0004`) and only mirrors *stance* on global
normative pages. The choice is recorded in the project index page.

Also notable: this is also the first **deviation** recorded on the
deps-single-file decision, and it surfaces a useful boundary
condition — the decision targets monorepo members; a standalone
single-library-dep project has no payoff from a separate
`deps/Dependencies.mill`. The ADR records the two trigger conditions
under which the deviation expires.

Refs: [[projects/sourceline-manager/index]],
[[projects/sourceline-manager/adr/0001-adopt-functional-domain-design]],
[[projects/sourceline-manager/adr/0002-deviate-deps-single-file]],
[[sources/summaries/sourceline-manager]],
[[tech/patterns/functional-domain-design]],
[[tech/decisions/deps-single-file]], [[index]]

## [2026-05-29] ingest | My notes on Kent Beck's TDD course (Di Bello, 2021)

Ingested Medium article
`https://pierodibello.medium.com/my-notes-on-kent-becks-tdd-course-8a1a7c8b7a95`
(Pietro Di Bello, 2021-04-02) — structured notes on Kent Beck's
2010 Pragmatic Screencasts TDD course (~2-hour Java/Tyrant DB
walkthrough). Created summary at
`sources/summaries/tdd_course_notes_kent_beck_pierodibello.md`
covering 15 themes: test list as planning artefact, end-to-end
first, small/deterministic steps, two-phase implementation
("TDD as if you meant it"), design-during-refactor, fake-it-till-
you-make-it, symmetry as refactoring guide, predictive testing
("call the shot"), micro/macro rhythms, test economics
(cost / benefit per test *and* per skipped test), Beck-vs-Mancuso
on when design happens, problem slicing and task-order effect on
architecture, private-method tests as scaffolding, error handling
as a choice not a default, and TDD maturity as managing
management-axis × design-axis simultaneously.

Staged raw extraction (WebFetch outline form, no verbatim passages)
at `sources/tmp/tdd_course_notes_kent_beck_pierodibello.md` for
human triage. `sources/raw/**` is human-owned per
`meta/ownership.md`; `sources/tmp/` is the agreed staging area.

This is the wiki's first source on TDD. Flagged three candidate
normative pages for future promotion (per `POLICY.md` requires a
second corroborating source or a project synthesis):

- `tech/patterns/tdd-rhythm` — test-list → expand → extract →
  refactor loop with red/green/refactor at its core.
- `tech/patterns/test-economics` — costs / benefits framing for
  both individual tests and skipped tests.
- `tech/patterns/symmetric-refactoring` — symmetry as a refactoring
  signal; preserve duplication when asymmetric extraction would
  destroy the pattern.

Plausible second sources to ingest later: Beck's *Test-Driven
Development: By Example*, Beck's *Test Desiderata* article, Freeman
& Pryce's *Growing Object-Oriented Software, Guided by Tests*.

Tension noted with the existing `devtools:tdd` agent skill — that
skill already encodes a TDD posture for this codebase. A short
synthesis is queued for when a second source corroborates whether
Beck's refactor-time-design framing or Mancuso's outside-in framing
fits better with our FP-heavy stack.

Cross-reference: Theme 14 (error handling as choice) aligns with
[[tech/patterns/functional-domain-design]] — a closed algebra makes
many error cases disappear at the type level, removing the need for
defensive tests.

Refs: [[sources/summaries/tdd_course_notes_kent_beck_pierodibello]],
[[sources/tmp/tdd_course_notes_kent_beck_pierodibello]],
[[tech/patterns/functional-domain-design]]

## [2026-05-29] ingest | TDD How-To (Beck + Tidy First, agent-prompt-form)

Ingested `sources/raw/docs/TDD_HOW_TO.md` — a prescriptive,
second-person codification of Kent Beck's TDD methodology fused with
Beck's later *Tidy First* approach, structured as an agent prompt
(references a `plan.md` test list and a `"go"` trigger word). Created
summary at `sources/summaries/tdd_how_to.md`.

**Wiki state change**: this is the **second** TDD source. Per
`POLICY.md` the promotion threshold (second corroborating source or
project synthesis) is now **met** for the cycle core
(red/green/refactor + simplest-first + refactor-only-on-green +
small commits). A draft `tech/patterns/tdd-rhythm.md` is now
unblocked. Tidy First (structural-vs-behavioural commit separation)
remains single-sourced and is the lead candidate for a separate
`tech/decisions/tidy-first-commits` page once a second source lands.

**Reconciliation with DRIFT-014 / DRIFT-015** (manual-review flags
against the Di Bello summary, raised earlier today):

- *Reinforced* (this source confirms the gap): 014a (TDD-as-if-you-meant-it misattributed), 014b (private-method scaffolding not Beck), 014c (end-to-end-first overgeneralised).
- *Partly answered*: 014d ("simplest solution that could possibly work" is **Obvious Implementation** under another name; Triangulation still absent).
- *Partly mitigated*: 015a (FP coda asserts the FP posture but doesn't replace OO vocabulary), 015b (minimise-side-effects rule moves toward purity), 015d (simplest-solution compatible with type-driven derivation), 015f (silence on private-method tests aligns with Beck-strict).
- *Unchanged / still open*: 014e (silent on Mancuso), 014f (no *Test Desiderata* citation), 015c (no type-first design stage), 015e (silent on mocks), 015g (no type-level error handling), 015h (no property-based testing).

Updated [[meta/drift]] reconciliation notes inside DRIFT-014 and
DRIFT-015 — flags are not closed, but each is now annotated with the
post-second-source status.

**Provenance question for the human**: the source document is in
agent-prompt form and has no author / origin recorded. If it was
copied from an external prompt template (e.g. a circulated
Claude/Cursor TDD prompt) rather than user-authored, an attribution
line in the file's preamble would tighten provenance. Flagged in the
summary's "What this source does not answer" section.

**Promotion plan candidates (with two sources now)**:

| Layer-2 page | Sources | Status |
|--------------|---------|--------|
| `tech/patterns/tdd-rhythm` (cycle core) | Di Bello + TDD_HOW_TO | drafting unblocked |
| `tech/decisions/tidy-first-commits` | TDD_HOW_TO only | needs second source |
| `tech/patterns/test-economics` | Di Bello only | needs second source |
| `tech/patterns/symmetric-refactoring` | Di Bello only | needs second source |

Any future `tech/patterns/tdd-rhythm` draft must address DRIFT-015c
(prepend type-first stage), DRIFT-015h (PBT as a peer to
example-based), and DRIFT-014a (split Braithwaite's *TDD as if you
meant it* into a separate related-pattern entry) before reaching
`accepted`.

Refs: [[sources/summaries/tdd_how_to]],
[[sources/summaries/tdd_course_notes_kent_beck_pierodibello]],
[[meta/drift]], [[tech/patterns/functional-domain-design]]

## [2026-05-29] lint | Post-sourceline-manager + TDD_HOW_TO drift report

Rewrote `meta/drift.md`. Compliance side remains clean: both accepted
normative pages (`tech/decisions/deps-single-file`,
`tech/patterns/functional-domain-design`) now carry 2 adopters with
distinct shapes — compositor (allocation deviation on the pattern,
unconditional adoption on deps) and sourceline-manager (unconditional
declarative-encoding adoption on the pattern, single-dep deviation on
deps).

7 findings open:

- **Carryovers**: DRIFT-011 (functional-domain-design body still says
  "no project ADR yet" while frontmatter lists 2 adopters — now
  further out of sync), DRIFT-013 (descriptive `tech/stack/*` used_by
  empty, informational), DRIFT-014 + DRIFT-015 (Di Bello TDD summary
  fidelity / FP-tension gaps — each now **partially mitigated** by
  the `tdd_how_to.md` landing; reinforcement / part-answer status
  tabulated per sub-finding).
- **New**: DRIFT-017 (`sources/raw/code/sourceline-manager.md`
  dangling from 4 inbound references — bridge file staged at
  `sources/tmp/sourceline-manager-bridge.md` awaiting human
  promotion), DRIFT-018 (TDD_HOW_TO.md sits in `sources/raw/docs/`
  with provenance unrecorded — likely human-authored agent prompt,
  flagged by both the summary and the ingest log entry for human
  confirmation), DRIFT-019 (frontmatter-axis duplicate of DRIFT-017
  on the sourceline-manager summary's `sources:` field).

Compliance findings (missing-declaration / dangling-adoption /
weak-rationale / conflicting-adoptions / unused-normative): all
clean.

Carryover DRIFT-009, DRIFT-010, DRIFT-012 were resolved earlier and
not relisted.

Refs: [[meta/drift]], [[projects/sourceline-manager]],
[[sources/summaries/sourceline-manager]],
[[sources/summaries/tdd_how_to]],
[[tech/patterns/functional-domain-design]],
[[tech/decisions/deps-single-file]]

## [2026-05-29] edit | DRIFT-011 closed, DRIFT-017 mitigated

Two agent-side remediations from the post-sourceline-manager +
TDD_HOW_TO drift report:

- **DRIFT-011 resolved.** Rewrote
  [[tech/patterns/functional-domain-design]] §"Open Questions / Drift
  Signals". The stale "no project ADR yet" claim is removed; a new
  §Adopters table enumerates compositor (allocation deviation,
  declarative-for-pipelines/executable-for-callbacks mixed encoding)
  and sourceline-manager (unconditional adoption, declarative
  encoding throughout, reference implementation) with their distinct
  shapes — recorded explicitly as the baseline for future drift
  detection. The trimmed §Open Questions section now lists the two
  *actual* open candidates: a separate
  `tech/patterns/functional-domain-layering` page (Ghosh axis) and
  the PBT-as-peer-to-example-based question
  ([[meta/drift]] §DRIFT-015h). Frontmatter `updated` bumped to
  2026-05-29.

- **DRIFT-017 mitigated** (full closure still requires human bridge
  promotion). The unannotated third inbound link in
  [[projects/sourceline-manager/adr/0001-adopt-functional-domain-design]]
  now carries the same `"(pending promotion from
  sources/tmp/sourceline-manager-bridge.md)"` caveat the other two
  body links (index, summary) already carried. The dangling state is
  now signposted consistently; full closure (and DRIFT-019 closure)
  still requires the human to move
  `sources/tmp/sourceline-manager-bridge.md` →
  `sources/raw/code/sourceline-manager.md`.

Updated [[meta/drift]]: DRIFT-011 marked resolved, DRIFT-017 marked
"open (mitigated)", Notes for Human revised — net open count goes
from 7 to 6 (4 if counting DRIFT-013 informational + DRIFT-017
mitigated as effectively closed pending human bridge move).

Not done in this pass (waiting on human input):

- **DRIFT-014 / DRIFT-015 remediation** — both remain agent-editable
  in the Di Bello summary, but their fix benefits from a prior human
  decision on which of the four promotion candidates listed in
  [[sources/summaries/tdd_how_to]] §"Promotion candidates" to draft
  first. Defaulting unilaterally on this would lock in framing
  before the human gets to weigh in.
- **DRIFT-017 / DRIFT-019 full closure** — human bridge promotion.
- **DRIFT-018** — human confirmation of `TDD_HOW_TO.md` provenance.

Refs: [[tech/patterns/functional-domain-design]],
[[projects/sourceline-manager/adr/0001-adopt-functional-domain-design]],
[[meta/drift]]

## [2026-05-29] promote | Drafted all 4 TDD candidates + bridge promotion + provenance

Three coordinated actions per user direction ("1) promote all, 2)
promote these too, 3) sorry, taken from the gist: <url>").

**(1) Drafted four new tech-layer pages** (all `status: draft`,
pending user acceptance pass):

- [[tech/patterns/tdd-rhythm]] — corroborated by both TDD sources
  (Di Bello + TDD_HOW_TO). Five-stage cycle: **Stage 0 type/algebra
  first** (FP-stack-specific prepend addressing DRIFT-015c) → test
  list → red (example-based **and** law-based as peers, addressing
  DRIFT-015h) → green (all three Beck strategies named: Obvious
  Implementation, Fake It, Triangulation — addressing DRIFT-014d)
  → refactor (Fowler-named, symmetry-aware, links
  [[tech/patterns/symmetric-refactoring]]) → call-the-shot. Beck's
  *Test Desiderata* enumerated explicitly (DRIFT-014f). Chicago vs
  London school split called out; Mancuso/mocks framed as out of
  scope per `devtools:tdd` (DRIFT-014e + DRIFT-015e). Type-level
  error encoding cross-linked to
  [[tech/patterns/functional-domain-design]] (DRIFT-015g).
  Braithwaite's *TDD as if you meant it* split out as a related but
  **distinct** pattern (DRIFT-014a).

- [[tech/decisions/tidy-first-commits]] — single-sourced from
  TDD_HOW_TO. Codifies structural-vs-behavioural commit separation,
  commit message tagging, structural-first rule, and the "tests
  pass before and after structural" precondition. Cross-links the
  existing [[feedback_hg_repo_commit_policy]] (form rules) — this
  decision adds type rules on top of form rules. Notes the
  conventional-commit vocabulary (`feat`/`fix` → behavioural,
  `refactor`/`tidy` → structural) as the carrier mechanism.

- [[tech/patterns/test-economics]] — single-sourced from Di Bello
  Theme 10. Frames test-write *and* test-skip as symmetric
  transactions with cost/benefit/risk-premium terms over a time
  horizon. FP-stack amortisation argument: one law, N
  implementations, per-instance cost approaches zero as N grows.
  [[projects/sourceline-manager]] monoid-law tests cited as the
  live example. Deletion-as-economics-decision section addresses
  the Di Bello "private-method scaffolding" framing without
  endorsing it.

- [[tech/patterns/symmetric-refactoring]] — single-sourced from
  Di Bello Theme 7 (citing Beck's *Implementation Patterns*).
  Three-move decision tree: preserve symmetric duplication, name
  the algebra, reject asymmetric extraction. `sourceline-manager`'s
  deliberately symmetric operator catalogue (`++` / `|+|` /
  `combine`, `:+` / `+:`, `appendLine` / `prependLine`) cited as
  the in-repo example. Cross-link with
  [[tech/patterns/functional-domain-design]] as the algebra-naming
  endgame.

User explicitly waived POLICY's "second corroborating source"
requirement for the three single-sourced candidates. Drafts are
`status: draft` per established workflow (precedent:
`functional-domain-design` drafted by agent → accepted by human).

**(2) Promoted bridge file**: moved
`sources/tmp/sourceline-manager-bridge.md` →
`sources/raw/code/sourceline-manager.md`. User explicitly authorised
the move into human-owned `sources/raw/**`. Removed all three
"pending promotion" annotations from inbound links
([[projects/sourceline-manager/index]] §Code Location,
[[projects/sourceline-manager/adr/0001-adopt-functional-domain-design]]
Links section, [[sources/summaries/sourceline-manager]] Links
section). Closes DRIFT-017 and DRIFT-019.

**(3) Recorded TDD_HOW_TO provenance**: confirmed copied from
public gist `https://gist.github.com/spilist/8bbf75568c0214083e4d0fbbc1f8a09c`
by GitHub user `spilist`. Updated
[[sources/summaries/tdd_how_to]]:
- Frontmatter `sources:` extended with the gist URL.
- New `provenance:` frontmatter block with `upstream_author`,
  `upstream_url`, `upstream_kind: public-gist`,
  `introduced_to_wiki_by: user`, `confirmed_at: 2026-05-29`.
- §Source rewritten with the provenance block; document now
  framed as a *community codification* of Beck + Tidy First, not
  Beck's own writing.
- §"What this source does not answer" updated: provenance question
  resolved, `plan.md` question still open, Tidy First × commit
  policy interaction now addressed via [[tech/decisions/tidy-first-commits]].
Closes DRIFT-018.

**Index updates**:
- [[tech/index]] lists the four new pages under Decisions and
  Patterns, each marked *(draft)*.

**[[meta/drift]] updates**: DRIFT-017, DRIFT-018, DRIFT-019 marked
**resolved** 2026-05-29. Notes-for-Human revised — open count down
from 6 to 3 (DRIFT-013 informational, DRIFT-014 + DRIFT-015 partly
mitigated, agent-editable). DRIFT-014/015 sub-points that the
[[tech/patterns/tdd-rhythm]] draft already addresses (014a, 014d,
014e, 014f, 015c, 015e, 015g, 015h) are noted; the Di Bello summary
itself still hasn't been rewritten — that's a separate maintenance
pass.

**New compliance implication for next lint run**: once the user
accepts any of the four drafts, the on-disk projects (compositor,
sourceline-manager) come under a new declaration obligation per
accepted page. Currently 0/4 adopter ADRs across both projects —
expected state for drafts; will surface as missing-declaration on
lint after acceptance. Pre-emptive ADRs are *not* recommended while
the pages are `draft` per `POLICY.md`.

Refs: [[tech/patterns/tdd-rhythm]],
[[tech/decisions/tidy-first-commits]],
[[tech/patterns/test-economics]],
[[tech/patterns/symmetric-refactoring]],
[[tech/index]], [[sources/raw/code/sourceline-manager]],
[[sources/summaries/tdd_how_to]],
[[sources/summaries/tdd_course_notes_kent_beck_pierodibello]],
[[meta/drift]]

## [2026-05-29] promote | tdd-rhythm + symmetric-refactoring → accepted

Per user direction. Both pages promoted from `draft` to `accepted`
on the strength of
[[projects/sourceline-manager/syntheses/monoid-laws-as-pbt-evidence]]
(written earlier today).

**[[tech/patterns/symmetric-refactoring]]** — confidence raised to
`high`. The synthesis's evidence is direct: `sourceline-manager`'s
operator catalogue (`++` / `|+|` / `combine`, `:+` / `+:`,
`appendLine` / `prependLine`, `appendLines` / `prependLines`,
`appendToken` / `prependTokenToLast`, `appendAll` / `prependAll`)
realises decision-tree moves 1 and 2 — preserve symmetric
duplication, name the algebra. §Open Questions rewritten to record
the new declaration obligation.

**[[tech/patterns/tdd-rhythm]]** — confidence stays at `medium`.
The synthesis corroborates Stages 0 (type/algebra first), 4
(refactor on green), and the *naming* half of Stage 2 (test names
narrate behaviour and label algebraic invariants). The
*quantification* half of Stage 2 (law-based as peer to
example-based via `forAll`) is **not yet realised** in any in-repo
project — `sourceline-manager` names laws but asserts them as
single examples. The promotion notes this explicitly via
`promotion_reason` frontmatter; DRIFT-015h stays open until a
`MonoidLawsSuite[A]` lands.

Both pages' frontmatter now carry:
- `status: accepted`
- `promoted_from: [projects/sourceline-manager/syntheses/monoid-laws-as-pbt-evidence.md]`
- `promotion_reason: |  ...` (multi-line; see each page)
- `promoted_at: 2026-05-29`

Index updates:
- [[tech/index]] — *(draft)* tag removed from both; reordered so
  the two accepted patterns sit above the still-draft
  `test-economics`.

[[meta/drift]] updates:
- **Run Metadata**: scope expanded — 4 accepted normative pages now
  in compliance scope (was 2).
- **DRIFT-014, DRIFT-015**: status changed from "partially
  mitigated" to "substantially mitigated" — the tdd-rhythm body
  addresses 14a/14d/14e/14f and 15a/15c/15d/15e/15g directly. 15h
  is the surviving open thread.
- **DRIFT-020 opened** (medium, missing-declaration): 2 pages × 2
  on-disk projects = 4 missing adoption ADRs. Expected
  post-promotion state. Remediation paths recorded per project.
- **Notes for Human**: open count 3 → 4; DRIFT-020 added.

Status of the four single-sourced drafts after this promotion:

| Draft | Status | Reason |
|-------|--------|--------|
| [[tech/patterns/symmetric-refactoring]] | **accepted** | Synthesis evidence: high |
| [[tech/patterns/tdd-rhythm]] | **accepted** | Synthesis evidence: partial; promoted with open question (DRIFT-015h) |
| [[tech/patterns/test-economics]] | still `draft` | User did not include in this promotion |
| [[tech/decisions/tidy-first-commits]] | still `draft` | Synthesis is silent on commit-history evidence |

Not done in this pass (waiting on user direction):
- ADRs from compositor and sourceline-manager addressing the two
  newly-accepted pages (DRIFT-020). The `sourceline-manager`
  adoption ADRs are essentially write-themselves from the synthesis
  evidence; the compositor ADRs would be forward-looking.
- A `MonoidLawsSuite[A]` extraction in `sourceline-manager` to
  close DRIFT-015h.
- Promotion decision on the remaining two drafts
  (`test-economics`, `tidy-first-commits`).

Refs: [[tech/patterns/symmetric-refactoring]],
[[tech/patterns/tdd-rhythm]],
[[projects/sourceline-manager/syntheses/monoid-laws-as-pbt-evidence]],
[[tech/index]], [[meta/drift]]

## [2026-05-29] implement | MonoidLawsSuite[A] lands in sourceline-manager — DRIFT-015h closed, tdd-rhythm confidence raised to high

Realised the open follow-up from this morning's `tdd-rhythm`
promotion. `/p/hg/sourceline-manager` now ships a reusable
`MonoidLawsSuite[A]` (MUnit-ScalaCheck `ScalaCheckSuite` + `forAll`)
plus a `Generators.scala` and two one-line consuming specs
(`SourceLineMonoidLawsSpec`, `SourceFileMonoidLawsSpec`). The six
prior hand-written law tests were deleted; the three quantified
properties run on each platform. `mill` test results: JVM 140/140,
Scala.js 163/163, Scala Native 184/184 — all green.

Cross-cutting wiki effects:

- [[meta/drift]] §DRIFT-015 row + §DRIFT-015h sub-finding marked
  **resolved 2026-05-29**.
- [[tech/patterns/tdd-rhythm]] `confidence` raised `medium` →
  `high`; `promotion_reason` updated; §Open Questions §DRIFT-015h
  entry rewritten as closed. The Stage 2 law-based-as-peer claim
  is now a demonstrated in-repo realisation, not just a draft-time
  argument from the type system.
- [[projects/sourceline-manager/syntheses/monoid-laws-as-pbt-evidence]]
  gains a §Status Update recording the realisation of
  recommendations 6 and 7 (and partial realisation of 8).
- [[projects/sourceline-manager/log]] records the implement event
  with full file inventory and test results.

The follow-up from this morning's `tdd-rhythm` promotion that is
**not** addressed by this work: DRIFT-020 (missing adoption ADRs
on `compositor` and `sourceline-manager` for `tdd-rhythm` and
`symmetric-refactoring`). That is a separate authoring task and is
left for a later pass. `test-economics` confidence raise on the
amortisation case is also a candidate now that the case is
realised, but is out of scope here.

Build change: `org.scalameta::munit-scalacheck::1.0.0` added to
`SlmTestSources.mvnDeps` in `build.mill`. One library dep added;
the `deps-single-file` deviation already covers this shape.

Refs: [[tech/patterns/tdd-rhythm]], [[meta/drift]] §DRIFT-015h,
[[projects/sourceline-manager/syntheses/monoid-laws-as-pbt-evidence]],
[[projects/sourceline-manager/log]],
`/p/hg/sourceline-manager/slm/test/src/slm/MonoidLawsSuite.scala`,
`/p/hg/sourceline-manager/slm/test/src/slm/Generators.scala`,
`/p/hg/sourceline-manager/slm/test/src/slm/SourceLineMonoidLawsSpec.scala`,
`/p/hg/sourceline-manager/slm/test/src/slm/SourceFileMonoidLawsSpec.scala`

## [2026-05-29] implement | SourceLine primitives + StringUtils composition + primitive laws — test-economics promoted, confidence raised to high

Second wave of algebraic-contract evidence landed in
`sourceline-manager`, extending the monoid-laws claim from
`(empty, ++)` to the full operator catalogue.

What landed (see [[projects/sourceline-manager/log]] for full
detail):

- **Primitive operator set** on `SourceLine` — 16 orthogonal
  methods in five families (slicing / search / predicates /
  pattern / joining), each a one-line wrap over `Vector[Token]`.
- **`StringUtilsCompositionSpec`** — 23 Apache Commons
  `StringUtils`-equivalent functions derived as local `def`s
  composing only existing operators. No new methods added to
  `SourceLine`. Proves the primitive set is *sufficient* to
  cover the StringUtils surface.
- **`SourceLinePrimitivesLawsSpec`** — 46 `forAll`-quantified
  ScalaCheck properties grouped by primitive family. Asserts
  the algebraic contract that any future refactor must preserve.

JVM 227/227 green. Build unchanged
(`munit-scalacheck` already on classpath from the prior
`MonoidLawsSuite` landing).

Cross-cutting wiki effects:

- [[projects/sourceline-manager/syntheses/monoid-laws-as-pbt-evidence]]
  gains a §"Status Update — 2026-05-29 (post-primitives +
  StringUtils composition)" recording the new evidence and its
  per-pattern effects.
- [[tech/patterns/test-economics]] **promoted**: `status:
  draft` → `accepted`, `confidence: medium` → `high`. The FP-
  stack amortisation case is now realised at two layers
  (monoid + 16-primitive sets certifying 23 derived functions).
  `promoted_from` cites the synthesis; `used_by` populated with
  the carrier FDD-adoption ADR; §"FP-stack amortisation"
  paragraph removes the "would, if extracted" subjunctive;
  §Open Questions §"No project currently exposes one" closed;
  §Adopters table added.
- [[tech/patterns/functional-domain-design]] — no frontmatter
  change. §"Design Principles for the Primitive Set"
  (orthogonality / expressivity / composability) is now
  realised across the full operator catalogue, not just the
  monoid layer. The §Adopters note for `sourceline-manager`
  gains an implicit strengthening via the synthesis citation.
- [[tech/patterns/tdd-rhythm]] — no status change (already at
  `confidence: high` post-MonoidLawsSuite). Stage 2 evidence is
  now an order of magnitude stronger.
- [[tech/patterns/symmetric-refactoring]] — no status change
  (already `accepted`, `high`). New symmetric pairs landed:
  `take` / `drop`, `takeWhile` / `dropWhile`, `indexWhere` /
  `lastIndexWhere`, `startsWith` / `endsWith`.

The user-side framing question that motivated this work — "did
we prove FP is more maintainable than imperative `StringUtils`?"
— is now answered by the conjunction of the two new specs.
`StringUtilsCompositionSpec` proves expressivity sufficiency
(static snapshot); `SourceLinePrimitivesLawsSpec` proves
refactor-resistance (lifecycle claim). Either alone is
incomplete; together they are the maintenance contract.

Out of scope: compositor-side adoption of the same discipline,
and a sharpening of [[tech/patterns/functional-domain-design]]
§Adopters notes column.

Refs: [[tech/patterns/test-economics]],
[[projects/sourceline-manager/syntheses/monoid-laws-as-pbt-evidence]],
[[projects/sourceline-manager/log]],
`/p/hg/sourceline-manager/slm/src/slm/SourceLine.scala`,
`/p/hg/sourceline-manager/slm/test/src/slm/StringUtilsCompositionSpec.scala`,
`/p/hg/sourceline-manager/slm/test/src/slm/SourceLinePrimitivesLawsSpec.scala`

## [2026-05-29] lint | Post-test-economics-promotion drift report

Rewrote `meta/drift.md`. Compliance scope widened from 4 → 5 accepted
normative pages (test-economics promoted earlier today).

Open items: 6.

- **Carryovers**: DRIFT-013 (informational, descriptive `used_by`
  empty on `tech/stack/*`), DRIFT-014 + DRIFT-015 (Di Bello summary
  fidelity / FP-tension — both substantially mitigated by the
  `tdd-rhythm` body content; summary rewrite is now optional
  clean-up rather than load-bearing).
- **Expanded**: DRIFT-020 (missing-declaration) — from 4 cells
  (tdd-rhythm × 2 projects + symmetric-refactoring × 2 projects) to
  6 cells (test-economics × 2 projects added). No project has yet
  written an adoption ADR for any of the three patterns; the
  monoid-laws synthesis is `kind: descriptive` and doesn't satisfy
  POLICY's adoption-declaration requirement.
- **New**: DRIFT-021 — `tech/patterns/test-economics.md`
  frontmatter `used_by` lists
  `projects/sourceline-manager/adr/0001-adopt-functional-domain-design.md`,
  but that ADR's `compliance` block only `adopts:
  tech/patterns/functional-domain-design.md` — it does not adopt
  test-economics. POLICY says `used_by` is mechanically maintained
  from ADR compliance blocks; "carrier" semantics is not in the
  schema.
- **New**: DRIFT-022 — `tech/patterns/test-economics.md` §Problem
  body still claims `draft` / "needs second source for accepted"
  while frontmatter is `accepted` / `confidence: high`. Same shape
  as the now-closed DRIFT-011 on `functional-domain-design`.

Compliance findings (dangling-adoption / weak-rationale /
conflicting-adoptions): all clean. Unused-normative: none
mechanically — three pages have empty / fabricated `used_by` but
all three are evidenced by the same in-repo synthesis.

Two **agent-fixable now** items (DRIFT-021 option 1, DRIFT-022)
left for the next session rather than chained into this lint run —
fixing them would be a small content edit each; the user may want
to bundle them with the DRIFT-020 sourceline-manager ADR drafting
pass, since the recommended `adr/0005-adopt-test-economics.md`
closes DRIFT-021 by the higher-quality path (a real adopting ADR
rather than clearing `used_by`).

Intake-side observations recorded (not findings): the two staged
items in `sources/tmp/` and the two untracked `sources/raw/**`
files (`TDD_HOW_TO.md`, `sourceline-manager.md` bridge) — both
expected per `feedback_ingest_staging`.

Refs: [[meta/drift]], [[tech/patterns/test-economics]],
[[tech/patterns/tdd-rhythm]], [[tech/patterns/symmetric-refactoring]],
[[projects/sourceline-manager/syntheses/monoid-laws-as-pbt-evidence]]

## [2026-05-29] adr | sourceline-manager × tdd-rhythm + symmetric-refactoring + test-economics

Drafted three new adoption ADRs for `sourceline-manager`, each
adopting one of the patterns promoted earlier today on the strength
of [[projects/sourceline-manager/syntheses/monoid-laws-as-pbt-evidence]].
All three are unconditional adoptions (no exceptions, no deviations).

- [[projects/sourceline-manager/adr/0003-adopt-tdd-rhythm]] —
  Adopts [[tech/patterns/tdd-rhythm]]. Stage 0 (type-first) cites
  in-tree ADR-0001/0002; Stage 2 (law-based as peer) cites
  `MonoidLawsSuite[A]` + `SourceLineMonoidLawsSpec` +
  `SourceFileMonoidLawsSpec` + `SourceLinePrimitivesLawsSpec`;
  Stage 4 (refactor on green) cites the operator catalogue's
  symmetry as the post-refactor result.
- [[projects/sourceline-manager/adr/0004-adopt-symmetric-refactoring]] —
  Adopts [[tech/patterns/symmetric-refactoring]]. Enumerates the
  symmetric pairs at both the monoid layer (`++` / `|+|` /
  `combine`, `:+` / `+:`, `appendLine` / `prependLine`, etc.) and
  the primitive layer (`take` / `drop`, `takeWhile` / `dropWhile`,
  `indexWhere` / `lastIndexWhere`, `startsWith` / `endsWith`).
  Move 3 (reject asymmetric extraction) is realised by absence —
  no `appendOrPrepend(side, …)` helper exists.
- [[projects/sourceline-manager/adr/0005-adopt-test-economics]] —
  Adopts [[tech/patterns/test-economics]]. Per-test framing cites
  the three-line monoid-law tests; FP-stack amortisation cites
  the two-layer realisation
  (`MonoidLawsSuite[A]` × N instances + `SourceLinePrimitivesLawsSpec`
  × 46 properties × 16 primitives certifying 23 derived StringUtils-
  equivalent functions). Cross-platform parity (JVM / Scala.js /
  Scala Native) multiplies the amortisation payoff.

Cross-cutting effects:

- `tech/patterns/tdd-rhythm.md` `used_by` populated with ADR-0003.
- `tech/patterns/symmetric-refactoring.md` `used_by` populated with
  ADR-0004.
- `tech/patterns/test-economics.md` `used_by` corrected: the
  fabricated entry pointing at `adr/0001-adopt-functional-domain-design`
  (DRIFT-021) is replaced with the real adopting entry pointing at
  ADR-0005. §Adopters table row updated correspondingly; the
  parenthetical "(carrier)" framing is removed.
- `tech/patterns/test-economics.md` §Problem paragraph rewritten:
  the "draft / needs second source" sentence (DRIFT-022) is
  replaced with a sentence stating the page is accepted at
  `confidence: high` and citing the synthesis as the second
  source. Same shape as the now-closed DRIFT-011 on
  `functional-domain-design`.
- [[projects/sourceline-manager/index]] §Pages → ADRs lists all
  five ADRs.

[[meta/drift]] updates:
- **DRIFT-020 half-resolved**: 3 of 6 cells closed
  (sourceline-manager side). 3 compositor cells remain open,
  awaiting human design call between forward-looking `adopts` and
  `ignores`.
- **DRIFT-021 resolved** via option 2 (write the real ADR rather
  than clear `used_by`).
- **DRIFT-022 resolved**.
- Open count: 6 → 4 (DRIFT-013 informational; DRIFT-014 +
  DRIFT-015 substantially mitigated; DRIFT-020 down to 3 cells).

All three new ADRs are `shared`-owned per `projects/*/adr/**`;
agent draft, human review pending.

Refs: [[projects/sourceline-manager/adr/0003-adopt-tdd-rhythm]],
[[projects/sourceline-manager/adr/0004-adopt-symmetric-refactoring]],
[[projects/sourceline-manager/adr/0005-adopt-test-economics]],
[[projects/sourceline-manager/index]],
[[tech/patterns/tdd-rhythm]],
[[tech/patterns/symmetric-refactoring]],
[[tech/patterns/test-economics]],
[[projects/sourceline-manager/syntheses/monoid-laws-as-pbt-evidence]],
[[meta/drift]]

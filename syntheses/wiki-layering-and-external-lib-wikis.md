---
id: synthesis-wiki-layering-and-external-lib-wikis
title: Wiki layering and the role of external-lib llm-wikis
kind: descriptive
status: accepted
scope: cross-project
confidence: high
created: 2026-05-28
updated: 2026-05-28
revisions:
  - 2026-05-28 — added Kyo reachability fixes (tech/stack/kyo.md created)
  - 2026-05-28 — added Airstream reachability fixes (tech/stack/airstream.md created)
sources:
  - CLAUDE.md
  - POLICY.md
  - meta/schema.md
  - meta/ownership.md
  - tech/guides/ingest-external.md
  - sources/raw/code/mill.md
  - sources/raw/code/kyo.md
  - sources/raw/code/airstream.md
  - mill/llm-wiki/index.md
  - mill/llm-wiki/CLAUDE.md
  - tech/stack/mill.md
  - tech/stack/kyo.md
  - tech/stack/airstream.md
  - kyo/llm-wiki/index.md
  - kyo/llm-wiki/CLAUDE.md
  - Airstream/llm-wiki/index.md
  - Airstream/llm-wiki/CLAUDE.md
  - tech/guides/mill-cross-platform.md
  - tech/guides/mill-monorepo.md
  - tech/guides/mill-dependency-management.md
tags: [wiki-architecture, external-lib, llm-wiki, layering, reachability, mill, kyo, airstream]
---

## Observation

The wiki under `/p/wiki/` is not a single corpus — it is **three
distinct layers** with three different sources of authority, three
different update cadences, and three different audiences. Until now
the relationships between them have been implicit, and the only path
from the curated layer down into the upstream-derived layer was via
`sources/raw/code/<lib>.md`, which is itself easy to miss.

This synthesis names the layers, defines their responsibilities, and
records the reachability fixes applied to make the Mill llm-wiki
discoverable from where a human or agent will actually look for it.

## The three layers

### Layer 1 — Meta (rules of engagement)

Files: `CLAUDE.md`, `POLICY.md`, `meta/schema.md`,
`meta/ownership.md`, `meta/log.md`, `meta/drift.md`,
`meta/registry.md`.

- **Authority**: human-owned. The agent reads, never edits without
  explicit authorization.
- **Stability**: very slow change. These define what a page *is*,
  who owns what, and what coherence means.
- **Audience**: every operation. Read by both human and agent before
  any non-trivial wiki write.

### Layer 2 — Content (our wiki proper)

Directories: `tech/` (decisions, patterns, stack, capabilities,
guides, glossary), `projects/`, `sources/raw/docs/`,
`sources/summaries/`, `syntheses/`.

- **Authority**: shared. Normative pages (`tech/decisions`,
  `tech/patterns`, `projects/*/adr`) carry compliance weight per
  `POLICY.md`; descriptive pages (stack, capabilities, guides,
  summaries, syntheses) carry awareness only.
- **Stability**: moderate. Driven by our project work and ingest of
  external sources.
- **Audience**: anyone designing, deciding, or reviewing in our
  codebase. This is where *our position* lives.

### Layer 3 — External-lib wikis (upstream knowledge, mechanically curated)

Directories: `mill/llm-wiki/`, `kyo/llm-wiki/`,
`Airstream/llm-wiki/`. Each is a *self-contained* knowledge base
about one third-party library, with its own `CLAUDE.md`,
`meta/schema.md`, and section taxonomy chosen to fit that library.

- **Authority**: agent-owned, but derived from the upstream source
  at `/p/gh/<lib>` rather than from our opinions. Each page tracks
  the upstream commit it was read from (`source_commit`) so staleness
  is detectable.
- **Stability**: bound to the upstream's release cadence. Refresh
  is a separate procedure (`ingest-external refresh <name>`).
- **Audience**: the agent doing a focused lookup ("how does Mill's
  cross-build work?", "what does Kyo's `Abort` do?"). Reading raw
  upstream docs would take an order of magnitude longer.

### Why three layers, not one

These layers have **incompatible update cadences and authorities**.
Mixing them collapses important guarantees:

- If our opinions lived inside `mill/llm-wiki/`, an upstream refresh
  would risk overwriting them.
- If upstream mechanical knowledge lived inside `tech/stack/mill.md`,
  the page would be either constantly stale or constantly churning,
  and would dwarf the parts that are actually ours.
- Without `meta/` as a separate human-owned layer, the agent could
  rewrite the rules it operates under.

The split is load-bearing.

## How the layers connect — the bridge files

Each external-lib wiki is registered in Layer 2 by a single pointer
file under `sources/raw/code/<lib>.md` with `type: external-lib`
frontmatter. That file is the canonical bridge:

```yaml
---
id: source-mill
type: external-lib
repo: /p/gh/mill               # upstream source code
wiki_path: mill/llm-wiki/      # the Layer-3 wiki for this library
last_observed: 2026-05-24
commit: 41ce6c977c4
wiki_sections: [concepts, modules, configuration, patterns, recipes, cli]
---
```

The schema for `external-lib` is defined in
[[meta/schema]] §"External-lib". The shared procedure for
creating, refreshing, and querying these wikis is in
[[tech/guides/ingest-external]].

### Current registry

| Library   | Bridge file                                                       | Wiki path             | Source repo         |
|-----------|-------------------------------------------------------------------|-----------------------|---------------------|
| Mill      | [[sources/raw/code/mill]]                                         | `mill/llm-wiki/`      | `/p/gh/mill`        |
| Kyo       | [[sources/raw/code/kyo]]                                          | `kyo/llm-wiki/`       | `/p/gh/kyo`         |
| Airstream | [[sources/raw/code/airstream]]                                    | `Airstream/llm-wiki/` | `/p/gh/Airstream`   |

## Mill — the concrete worked example

Mill is the most fragmented case because it shows up at every layer.
Knowing where to land matters:

| You want… | Read this | Why |
|-----------|-----------|-----|
| Upstream API surface — what does `mvnDeps` actually do? what types does `Task.Sources` return? | [[mill/llm-wiki/index]] | Mechanical, derived from `/p/gh/mill` |
| Our project conventions — what does the monorepo's build look like? what traits do modules extend? | [[tech/guides/mill-monorepo]] | Our chosen layout |
| Our cross-platform conventions | [[tech/guides/mill-cross-platform]] | Our chosen module shape |
| Our dependency convention (and *why*) | [[tech/guides/mill-dependency-management]] (descriptive) and [[tech/decisions/deps-single-file]] (normative) | Decision + rationale |
| A summary of Mill suitable for someone evaluating the stack | [[tech/stack/mill]] | One-page orientation |
| The status of the bridge — last observed commit, sections present | [[sources/raw/code/mill]] | The registry entry |

### Topic-level cross-walk

| Topic | Our page (Layer 2) | Mill llm-wiki page (Layer 3) |
|-------|--------------------|------------------------------|
| Dependencies | [[tech/decisions/deps-single-file]], [[tech/guides/mill-dependency-management]] | [[mill/llm-wiki/configuration/dependencies]] |
| Cross-platform | [[tech/guides/mill-cross-platform]] | [[mill/llm-wiki/configuration/cross-building]], [[mill/llm-wiki/recipes/multi-platform]] |
| Multi-module monorepo | [[tech/guides/mill-monorepo]] | [[mill/llm-wiki/patterns/multi-module]], [[mill/llm-wiki/patterns/build-file-structure]] |
| Scala.js modules | [[tech/stack/mill]] §"Scala.js Configuration" | [[mill/llm-wiki/modules/scalajs-module]] |
| Scala Native modules | [[tech/stack/mill]] §"Native Linking" | [[mill/llm-wiki/modules/scala-native-module]] |
| Test modules | (not yet captured at Layer 2) | [[mill/llm-wiki/modules/test-module]] |
| Publishing | (not yet captured at Layer 2) | [[mill/llm-wiki/configuration/publishing]], [[mill/llm-wiki/recipes/publish-maven]] |
| CLI usage | [[tech/stack/mill]] §"Agent Interface" | [[mill/llm-wiki/cli/commands]], [[mill/llm-wiki/cli/task-resolution]] |
| Build graph / caching / evaluation | (not yet captured at Layer 2) | [[mill/llm-wiki/concepts/build-graph]], [[mill/llm-wiki/concepts/caching]], [[mill/llm-wiki/concepts/evaluation]] |

The asymmetry is informative: Layer 2 covers **what we have opinions
about**; Layer 3 covers **what Mill does**. The rows where Layer 2
is empty are not gaps — they are the upstream-only topics where we
have no project-specific position.

## Reachability — fixes applied

Before this synthesis, the Mill llm-wiki was reachable only via
`sources/raw/code/mill.md`. A human or agent landing on
`tech/stack/mill.md`, [[index]], or any Mill guide had no obvious
hint that the deep upstream wiki existed at all.

The following reachability fixes are applied alongside this
synthesis (see corresponding log entry):

1. **`index.md`** — add an *External Library Wikis* section listing
   each `<lib>/llm-wiki/` and pointing at the bridge file.
2. **`tech/stack/mill.md`** — add a *Deep Reference* link pointing
   at [[mill/llm-wiki/index]] near the top of the page, plus
   pointers to the bridge file and the synthesis.
3. **`tech/guides/mill-cross-platform.md`,
   `tech/guides/mill-monorepo.md`,
   `tech/guides/mill-dependency-management.md`** — each gets an
   *Upstream Reference* link to the most relevant
   [[mill/llm-wiki/]] page in its Links section.

The fix is intentionally *one-way and minimal*: from Layer 2 into
Layer 3. Layer 3 stays self-contained — adding back-links from
`mill/llm-wiki/` into our wiki would couple upstream-mechanical
content to our opinions and complicate the `ingest-external
refresh` story.

## Division of responsibility — rules of thumb

When writing a new Mill-related page, decide which layer it belongs in:

- Is it **true regardless of our project**? → Layer 3
  (`mill/llm-wiki/...`).
- Is it **our chosen policy or pattern**? → Layer 2
  (`tech/decisions/`, `tech/patterns/`, `tech/guides/`).
- Does it **change the rules of how we write pages**? → Layer 1
  (`meta/...`, requires human authorization).

Symmetrically when reading:

- Need a fact about Mill? → Layer 3 first.
- Need our policy on Mill? → Layer 2.
- Need to know who owns what? → Layer 1.

## Generalization to other external libs

The same model applies to Kyo and Airstream. Each has:

- A Layer-2 summary / stack page where our position lives.
- A Layer-3 llm-wiki where upstream knowledge lives.
- A `sources/raw/code/<name>.md` bridge.

The reachability fixes applied here for Mill have now also been
applied to Kyo and Airstream via the same pattern:

- [[tech/stack/kyo]] was created on 2026-05-28 with the same
  *Deep Reference* block shape as [[tech/stack/mill]]: pointer to
  [[kyo/llm-wiki/index]], pointer to [[sources/raw/code/kyo]], and
  pointer back to this synthesis. The page also lists the
  `scala:kyo-*` agent skills as additional Layer-3 entry points.
- [[tech/stack/airstream]] was created on 2026-05-28 with the same
  *Deep Reference* block shape: pointer to
  [[Airstream/llm-wiki/index]], pointer to
  [[sources/raw/code/airstream]], and pointer back to this synthesis.
  The page also lists the `frontend:airstream-ownership-patterns`
  agent skill as an additional Layer-3 entry point.
- [[tech/index]] now lists `stack/kyo.md` and `stack/airstream.md`
  under Stack alongside `stack/mill.md`.

All three currently registered external-lib wikis (Mill, Kyo,
Airstream) now have a Layer-2 anchor with a *Deep Reference* block.
A future llm-wiki added without a matching `tech/stack/<name>.md`
would be the next reachability gap.

## Open questions

- Both `tech/stack/kyo.md` and `tech/stack/airstream.md` were
  created on 2026-05-28 ahead of formal ADR adoption — purely to
  fix reachability. The original "trigger condition" (more than one
  project formally adopting via ADR) is now retroactively
  recognized as too strict: reachability of upstream knowledge is
  a separate concern from policy adoption, and waiting for the
  latter starves the former. Future external-lib additions should
  create the Layer-2 stack page *at the same time as* the bridge
  file.
- Should an automated lint check verify that every
  `sources/raw/code/*.md` bridge has at least one inbound link from
  Layer 2 (other than from itself)? Currently a missing link would
  silently leave the llm-wiki unreachable. This is a candidate
  addition to `lint`. With the Kyo and Airstream fixes in place,
  all currently registered bridges would pass; the check would
  catch future regressions.

## Confidence Assessment

**High.** The layering described is exactly the structure on disk;
the fixes are mechanical and verifiable. The only soft claim is the
division-of-responsibility heuristic, which is opinionated guidance
rather than mechanical rule — it should be revisited if a real
borderline case forces a re-think.

## Links

- [[CLAUDE]] (root)
- [[POLICY]]
- [[meta/schema]]
- [[meta/ownership]]
- [[tech/guides/ingest-external]]
- [[sources/raw/code/mill]]
- [[sources/raw/code/kyo]]
- [[sources/raw/code/airstream]]
- [[mill/llm-wiki/index]]
- [[kyo/llm-wiki/index]]
- [[Airstream/llm-wiki/index]]
- [[tech/stack/mill]]
- [[tech/stack/kyo]]
- [[tech/stack/airstream]]

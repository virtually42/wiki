# Wiki Index

Root catalog. Start here to discover wiki content.

---

## Tech Layer

Cross-project knowledge: decisions, patterns, architecture, stack, capabilities, guides.

- [tech/index.md](tech/index.md) — tech-layer catalog

### Key Areas

| Area | Path | Content |
|------|------|---------|
| Architecture | tech/architecture/ | System shapes, module boundaries |
| Patterns | tech/patterns/ | Reusable design patterns (normative) |
| Anti-patterns | tech/patterns/anti/ | Rejected patterns (normative) |
| Decisions | tech/decisions/ | Organizational ADRs (normative) |
| Stack | tech/stack/ | Libraries, tools, platforms (descriptive) |
| Capabilities | tech/capabilities/ | Architectural needs independent of tech |
| Guides | tech/guides/ | Cross-project how-tos |
| Glossary | tech/glossary.md | Shared vocabulary |

---

## Projects

| Project | Status | Stack | Description |
|---------|--------|-------|-------------|
| animdsl | active | Scala 3 (JVM/JS), Mill | Declarative animation DSL with SVG/SMIL + OOXML backends (3 modules: `core` / `svg` / `ooxml`); both backends consume `tagless-core` |
| compositor | active (design-stage) | Scala Native, Kyo, Wayland, wlroots | Wayland compositor |
| sourceline-manager | active | Scala 3 (JVM/JS/Native), Mill | Foundation library: source code as a typed value algebra |
| safetensors-scala | active | Scala 3 (JVM/JS/Native), Mill, scodec | Foundation library: HuggingFace SafeTensors format reader |
| shapesdsl | active | Scala 3 (JVM/JS), Mill, Java2D (JVM) | Declarative 2D shape + heatmap DSL (3 modules: `core` / `heatmap` / `svg`); `svg` consumes `tagless-core` |
| tagless | active | Scala 3 (JVM/JS), Mill, raquo/domtypes, Airstream | Type-safe HTML DSL family (14 modules: `htmlid` / `core` / `i18n` / `md` / `meta` / `page` / `form` / `table` / `crud` / `route` / `viz` / `htmx` / `svg` / `events`) |
| toolbox | active | Scala 3 (JVM/JS/Native), Mill, Kyo, fs2, os-lib | Composable shell pipelines + platform-agnostic process execution (10 modules: `core` / `fluent` / `script` / `proc` + four `proc-*` interpreters / `vfs` / `example`) |
| dependency-manager | active (v1 shipped) | Scala 3 (JVM), Mill, toolbox, toml-scala, scala-yaml | Private build-tooling CLI (`dm`) — centralised TOML+YAML dependency catalog for `/p/hg/` repos; regenerates per-project `deps/Dependencies.mill`. All 3 v1 consumers migrated (toolbox/slm/safetensors-scala); first commits landed on `main` |
| deploymentbox | active (v3 accepted; pre-first-release) | GitHub Actions, sigstore attestation, Nix (per-lib flake), gpg + YubiKey, Sonatype Central Portal | Publishing pipeline for signed `no.virtual-architect` Maven Central artifacts. v3 (public-OSS path): GitHub Actions builds with `actions/attest-build-provenance`; operator downloads to laptop, verifies attestation + SHA, signs locally with YubiKey, uploads to Central, re-verifies on a clean machine. v1 (host-builds-directly) and v2 (Firecracker microVM + MinIO on Hetzner) preserved as historical record — v2 remains the starting point for any future private-artifact pipeline |
| factory | active (design accepted; pre-migration) | git, Mill, Nix, btrfs, sops + YubiKey, rsync | Single-git workspace umbrella at `/factory/` absorbing the wiki and all `/p/hg/*` libraries into one history. `upstream/<lib>` (forks) and `pub/<lib>` (per-library public mirrors) sit inside the tree but keep their own `.git/` and are gitignored from the monorepo. Five accepted ADRs lock the topology; migration plan + path-rewrite script forthcoming. Closes the deferred `dm` absorption question (`dm` stays as meta-tool) |
| webapp | planned | Scala 3, Kyo, Tapir, PostgreSQL | Web application |
| cli-tool | planned | Scala 3, Kyo, SQLite | CLI utility |
| infra | planned | NixOS, PostgreSQL, Envoy | Infrastructure configs |

Each project has: `projects/<name>/index.md` with ADRs, designs, plans,
tickets, architecture, interfaces, risk, log, and syntheses. `planned`
projects have no on-disk presence yet and are not evaluated by `lint`.

---

## Sources

- [sources/raw/docs/](sources/raw/docs/) — articles, papers, specs (immutable)
- [sources/raw/code/](sources/raw/code/) — code repository pointers + external-lib bridges
- [sources/summaries/](sources/summaries/) — one summary per source

---

## External Library Wikis

Query-optimized, upstream-derived wikis for libraries we use heavily.
Each is a self-contained Layer-3 knowledge base; a bridge file under
`sources/raw/code/` records the upstream commit and section taxonomy.
See [[syntheses/wiki-layering-and-external-lib-wikis]] for the
relationship between these wikis and our tech layer.

| Library | Wiki | Bridge | Source repo |
|---------|------|--------|-------------|
| Mill | [mill/llm-wiki/](mill/llm-wiki/index.md) | [[sources/raw/code/mill]] | `/p/gh/mill` |
| Kyo | [kyo/llm-wiki/](kyo/llm-wiki/index.md) | [[sources/raw/code/kyo]] | `/p/gh/kyo` |
| Airstream | [Airstream/llm-wiki/](Airstream/llm-wiki/index.md) | [[sources/raw/code/airstream]] | `/p/gh/Airstream` |
| toml-scala | [toml-scala/llm-wiki/](toml-scala/llm-wiki/index.md) | [[sources/raw/code/toml-scala]] | `/p/gh/toml-scala` |
| microvm.nix | [microvm.nix/llm-wiki/](microvm.nix/llm-wiki/index.md) | [[sources/raw/code/microvm-nix]] | `/p/gh/microvm.nix` |

Procedure for creating, refreshing, or querying these wikis:
[[tech/guides/ingest-external]].

---

## Cross-Project Syntheses

- [syntheses/](syntheses/) — cross-cutting analyses spanning multiple projects
- [[syntheses/wiki-layering-and-external-lib-wikis]] — three-layer model (meta / our tech / external-lib wikis) and Mill ↔ tech-layer cross-walk

---

## Meta

- [meta/schema.md](meta/schema.md) — page formats, frontmatter spec
- [meta/ownership.md](meta/ownership.md) — who edits what
- [meta/drift.md](meta/drift.md) — compliance gaps (generated by lint)
- [meta/log.md](meta/log.md) — cross-cutting events

---
id: factory-design-monorepo-gap-analysis
title: Monorepo design vs current wiki and repository state
kind: descriptive
status: draft
project: factory
created: 2026-05-28
updated: 2026-05-28
related_adrs: []
related_plans: []
sources:
  - monorepo-design-wip.md
---

# Monorepo Design vs. Current Reality

Gap analysis comparing `monorepo-design-wip.md` against the actual state of
the wiki and code repositories as of 2026-05-28.

---

## What the design doc envisions

A single `/p/factory/` monorepo with:

- Unified `build.mill` + shared `FactoryModule` traits
- `modules/` (cross-platform libs: core, render) + `apps/` (compositor, browser) + `native/` (Rust FFI)
- Nix flake as the outer boundary pinning everything
- `tools/` agent command surface with structured JSON observations
- Sister relationship with the wiki via `sources/raw/code/factory.md`

---

## What actually exists today

### 7 separate repos across two locations, no monorepo

| Repo | Location | What it is | Build |
|------|----------|-----------|-------|
| **swc** (compositor) | `/p/hg/swc/` | Wayland compositor -- Scala Native | Mill 1.1.2, own flake.nix, `core.jvm`/`core.native` + `compositor` |
| **bro** (browser) | `/p/v42/bro/` | Security browser -- Scala Native | Mill 1.1.2, own flake.nix, 17 modules under `modules/`, `rust-shims/` |
| **fashion-designer** | `/p/v42/fashion-designer/` | WebGPU tool -- ScalaJS + Native | Mill 1.1.2, `webgpu` cross-platform module |
| **paladium** | `/p/v42/paladium/` | Cross-platform lib -- JVM/JS/Native | Mill 1.1.2, full `Cross[]` + `PlatformScalaModule` |
| **tagless** | `/p/v42/tagless/` | HTML DSL lib -- JVM/JS/Native | Mill 1.1.2 |
| **toolbox** | `/p/v42/toolbox/` | CLI utilities -- mixed | Mill 1.0.6 (!), own flake |
| **infra** | `/p/v42/infra/` | NixOS VMs | Nix flake, no Mill |

---

## Key gaps between design and reality

### 1. No shared rendering backend exists yet

The design's core thesis -- compositor and browser share `modules/render` -- is
not realized. `bro` has its own `modules/render` with 17 internal modules. `swc`
has a separate `core` module. They share zero code. The "shared-backend
invariant" from the design doc is entirely aspirational.

### 2. The trait/convention split is already happening -- but divergently

Each repo independently invented its own base trait pattern:

- `swc`: `CoreModule` (ad-hoc, inline deps)
- `bro`: `BroModule extends ScalaNativeModule` (Native-only, no cross)
- `fashion-designer`: `Shared extends ScalaModule` (namespace container cross pattern)
- `paladium`: `Shared extends CrossScalaModule with PlatformScalaModule` (full Cross[] matrix)
- `tagless`/`toolbox`: `Config` object with `ScalacOptions` (tpolecat-based)

The design's `FactoryModule`/`FactoryNative`/`FactoryJS` would unify these, but
it's unwritten code.

### 3. The wiki already captured the patterns -- that's the good news

The wiki guides (`tech/guides/mill-cross-platform.md`, `mill-monorepo.md`)
document all four patterns (A-D) observed across these repos and recommend a
hybrid for the factory. The `tech/stack/mill.md` page describes the target build
structure. This is exactly the wiki's job -- descriptive pages derived from
observation. The wiki is ahead of the code.

### 4. Nix layer exists but is fragmented

`swc`, `bro`, and `toolbox` each have their own `flake.nix`. The design envisions
one flake pinning one toolchain. Today: three flakes, likely divergent nixpkgs
pins, no shared `nix/mill.nix` (the from-source OkHttp-free Mill derivation --
the "long pole" from Phase 0 -- doesn't exist yet).

### 5. Agent command surface (`tools/`) is empty

The design specifies `tools/{build,test,run,observe}.sh` with structured JSON
output. `swc/tools/` has only `bdf2c.py`. `bro/tools/` is empty. No JSON
observation contract exists anywhere.

### 6. Wiki seam is partially wired

`sources/raw/code/` has pointers for `kyo`, `mill`, and `airstream` (external
libs) -- but no pointer for the compositor, browser, or any of the actual project
repos. The `sources/raw/code/factory.md` from the design doesn't exist, and
neither do per-repo pointers for the existing separate repos.

### 7. Only one project registered in the wiki

`projects/compositor/` exists with a design doc and plan. But there's no
`projects/browser/`, no `projects/webapp/`, no `projects/factory/`. The index.md
lists compositor, webapp, cli-tool, and infra -- but only compositor has actual
wiki pages.

### 8. Rust FFI exists -- but only in bro

`bro/rust-shims/` with a `Cargo.toml` is the real-world version of the design's
`native/render-ffi`. It's bro-specific, not shared. `swc` has no Rust FFI at all.

---

## Summary scorecard

| Design doc aspect | Status |
|-------------------|--------|
| Monorepo exists at `/p/factory/` | **Not started** -- 7 separate repos |
| Shared `FactoryModule` traits | **Not started** -- each repo has own traits |
| Cross-platform module model | **Proven in isolation** -- 4 patterns observed, hybrid recommended |
| Shared render backend | **Not started** -- bro and swc have independent renderers |
| Nix flake outer boundary | **Fragmented** -- 3+ separate flakes |
| From-source OkHttp-free Mill | **Not started** (Phase 0 long pole) |
| `tools/` agent command surface | **Not started** |
| Wiki seam (`sources/raw/code/`) | **Not wired** for own projects |
| Wiki guides documenting the target | **Done** -- guides capture patterns and recommend the hybrid |
| Bootstrapping phases 0-7 | **All pending** |

---

## Bottom line

The design doc is a well-reasoned consolidation plan, and the wiki's tech guides
already capture the empirical evidence supporting it. But the gap between design
and reality is the entire implementation -- nothing from the 7-phase
bootstrapping sequence has started. The most valuable thing the design does right
now is document the *why* behind consolidation (shared render backend,
reproducible TCB, agent command surface) -- which gives clear criteria for whether
and when to actually do it.

The immediate practical question: is consolidation worth doing now, or should the
wiki keep tracking divergent repos as-is until a concrete need (like actually
sharing the render backend between compositor and browser) forces the merge?

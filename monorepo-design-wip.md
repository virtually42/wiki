---
id: factory-design-monorepo-build-substrate
title: Monorepo build substrate — Scala 3 cross-platform + Nix infrastructure
kind: descriptive
status: draft
project: factory
created: 2026-05-24
updated: 2026-05-24
related_adrs: []
related_plans: []
sources:
  - design-wiki-v2.md
  - mill-nixpkgs-design.md
---

# Design: Monorepo Build Substrate

```yaml
status: draft
created: 2026-05-24
authors: [human, claude]
scope: build system, repository topology, infrastructure-as-code, wiki integration
```

---

## Problem Statement

The software factory has two kinds of artifact that currently have no shared physical home:

1. **The code.** Multiple Scala 3 projects — the Wayland compositor (Scala Native + wlroots), the security-first browser (Scala Native), shared libraries (rendering backend, effect-system glue, domain models) — each potentially targeting more than one platform. The compositor and browser are *meant* to share a rendering backend (Taffy/tiny-skia bindings); today nothing structurally enforces or even expresses that sharing.

2. **The knowledge.** The Wiki V2 system is designed as the backbone of agentic coding. Its `sources/raw/code/` pointers reference repositories; its `implement` / `test` / `run` operations invoke a build; its self-learning loop depends on observing real build and test results. But the wiki design treats those repos as external givens — `repo: /p/compositor`, `repo: /p/webapp` — abstract paths with no defined structure, no defined build interface, and no defined relationship to each other.

The gap: **there is no specification for the physical substrate the wiki observes and acts upon.** The wiki is "a compiled view of code" (its own words), but the code it compiles a view of is unspecified. This document specifies that substrate.

The substrate must satisfy four hard requirements that pull in different directions:

- **Cross-platform from one codebase.** A single library module must compile to JVM, JS, and Native without per-platform source duplication, because the rendering backend is shared between a Native compositor and (potentially) a JS-targeting tool surface.
- **Reproducible and auditable to the trusted-computing-base standard** already established for this factory: declarative, content-addressed, pinned, no imperative package managers in the cryptographic-tooling path.
- **A stable, machine-discoverable interface for the agent.** The wiki's `implement`/`test`/`run` operations need deterministic commands with deterministic output locations, not a build whose structure the agent must re-learn each session.
- **Refactor-survivable module boundaries.** A module must be movable (into or out of the monorepo, e.g. open-sourcing the rendering backend) without silent breakage — the portability concern from the earlier Mill discussion.

---

## Constraints

| Constraint | Source | Implication |
|------------|--------|-------------|
| Scala 3 across all code | Established stack | Mill (first-class Scala 3 + cross-platform), not sbt |
| JVM + Scala.js + Scala Native targets | Compositor/browser are Native; tooling may be JVM/JS | Cross-platform module factoring is mandatory, not optional |
| NixOS / Nix flakes for all infra | Established preference | The flake is the outer build boundary; Mill runs *inside* a Nix-pinned toolchain |
| Auditable minimal TCB | Established preference | Mill itself should be the from-source, OkHttp-free derivation from `mill-nixpkgs-design.md` |
| Single root `CLAUDE.md`, no per-project control files | Wiki V2 design goal #5 | The monorepo must NOT carry per-project agent-control files; agent control lives in the wiki repo |
| Deterministic on-disk output paths | Wiki `test`/`run` need to find artifacts | Mill's per-module deterministic `out/` paths are load-bearing |
| Code lives in repos *separate* from the wiki | Wiki V2 layer model (Layer 1 vs Layer 2) | The monorepo and the wiki are distinct repositories; the wiki points into the monorepo |

A non-constraint worth stating explicitly: the wiki and the monorepo do **not** need to be the same repository, and should not be. The wiki is LLM-maintained knowledge with its own ownership/coherence policy; the monorepo is human-and-agent-authored code with a compiler as its arbiter of correctness. Conflating them would put 780-line schema files next to build files and confuse both ownership models. They are sister repositories.

---

## Repository Topology

Three repositories, one logical factory:

```
/p/factory/                      ← the code monorepo (this document)
/p/wiki/                         ← the knowledge wiki (design-wiki-v2.md)
/p/nixpkgs-overlay/  (optional)  ← shared Nix derivations incl. from-source Mill
```

The wiki's `sources/raw/code/` points *into* `/p/factory`:

```yaml
# /p/wiki/sources/raw/code/factory.md
---
id: source-factory
type: code
repo: /p/factory
last_observed: 2026-05-24
commit: <sha>
entry_points:
  - build.mill
  - modules/render/src/Render.scala
  - apps/compositor/src/Main.scala
  - flake.nix
---
```

This is the single seam between knowledge and code. Everything below specifies what lives behind that seam.

---

## Architecture Overview

Four nested layers, outermost first. Each layer pins the one inside it.

```
┌─────────────────────────────────────────────────────────────┐
│ Layer 0: Nix Flake  (flake.nix)                               │
│   - Pins nixpkgs, the Scala toolchain, LLVM/Clang for Native, │
│     Rust toolchain for the C-ABI static libs, JDK, Node.      │
│   - Provides `nix develop` shell + `nix build` outputs.       │
│   - Vendors from-source, OkHttp-free Mill (mill-nixpkgs).     │
│   ┌─────────────────────────────────────────────────────────┐│
│   │ Layer 1: Mill root  (build.mill)                         ││
│   │   - Shared traits: FactoryModule, version constants,     ││
│   │     repository list, common deps.                        ││
│   │   - Discovers subtrees via package.mill files.           ││
│   │   ┌───────────────────────────────────────────────────┐ ││
│   │   │ Layer 2: Module tree                                │ ││
│   │   │   modules/   — cross-platform libraries             │ ││
│   │   │   apps/      — deployable binaries (Native)         │ ││
│   │   │   native/    — Rust C-ABI static libs               │ ││
│   │   │   ┌─────────────────────────────────────────────┐   │ ││
│   │   │   │ Layer 3: Platform cross-axis                 │   │ ││
│   │   │   │   each lib module = {jvm, js, native}        │   │ ││
│   │   │   │   shared src/ + per-platform src-{jvm,…}/    │   │ ││
│   │   │   └─────────────────────────────────────────────┘   │ ││
│   │   └───────────────────────────────────────────────────┘ ││
│   └─────────────────────────────────────────────────────────┘│
└───────────────────────────────────────────────────────────────┘
```

The discipline of the nesting: **a tool at layer N may only invoke tools at layer N+1, never reach around.** `nix build` invokes Mill; Mill invokes scalac/scala-native-cli; the agent invokes `nix develop -c ./mill …`. Nothing invokes scalac directly outside the Nix shell, because that would escape the pinned toolchain and break reproducibility. This is the same "tool at layer N invokes layer N+1" discipline that made the from-source Mill derivation tractable.

---

## Directory Layout

```
/p/factory/
├── flake.nix                      # Layer 0: pins everything, defines outputs
├── flake.lock                     # pinned input hashes (committed)
├── .envrc                         # direnv → `use flake` for auto-shell
│
├── build.mill                     # Layer 1: root build, shared traits
├── .mill-version                  # pins Mill version (matches flake's Mill)
│
├── modules/                       # cross-platform LIBRARIES (no main)
│   ├── package.mill               # subtree marker, shared lib traits
│   ├── core/                      # domain models, pure FP, effect glue (Kyo)
│   │   ├── package.mill
│   │   ├── src/                   # shared sources (all platforms)
│   │   ├── src-jvm/               # JVM-only sources
│   │   ├── src-js/                # JS-only sources
│   │   ├── src-native/            # Native-only sources
│   │   └── test/
│   │       ├── src/               # shared tests
│   │       └── src-native/        # platform-specific tests
│   └── render/                    # THE shared rendering backend
│       ├── package.mill
│       ├── src/                   # shared layout/paint API
│       ├── src-native/            # Taffy/tiny-skia FFI bindings (Native only)
│       └── test/src/
│
├── apps/                          # deployable BINARIES (Scala Native)
│   ├── package.mill               # subtree marker, app traits
│   ├── compositor/                # Wayland compositor (Native + wlroots)
│   │   ├── package.mill
│   │   ├── src/
│   │   └── test/src/
│   └── browser/                   # security-first browser (Native)
│       ├── package.mill
│       ├── src/
│       └── test/src/
│
├── native/                        # Rust C-ABI static libraries
│   ├── render-ffi/                # Taffy + tiny-skia + resvg wrapper
│   │   ├── Cargo.toml
│   │   ├── src/lib.rs
│   │   └── render-ffi.h           # generated C header, consumed by render
│   └── font-ffi/                  # fontdue glyph rasterizer (per CVE-2025-27363)
│       ├── Cargo.toml
│       └── src/lib.rs
│
├── nix/                           # Nix infrastructure-as-code
│   ├── mill.nix                   # from-source OkHttp-free Mill derivation
│   ├── toolchain.nix              # Scala/LLVM/Rust/JDK/Node pinning
│   ├── deps.nix                   # mill2nix-generated dependency repo
│   ├── mill2nix.lock              # dependency lock (committed)
│   ├── native-libs.nix            # builds native/ Rust libs as derivations
│   ├── apps.nix                   # packages apps/ binaries
│   └── checks.nix                 # `nix flake check` definitions
│
├── tools/                         # agent-facing command surface
│   ├── build.sh                   # `nix develop -c ./mill __.compile`
│   ├── test.sh                    # deterministic test invocation
│   ├── run.sh                     # run an app, structured output
│   └── observe.sh                 # emit JSON build/test facts for the wiki
│
└── docs/                          # repo-local docs (NOT the wiki)
    └── README.md                  # how to clone, enter shell, build
```

Note what is **absent**: there is no `CLAUDE.md`, no `POLICY.md`, no `meta/schema.md` anywhere in `/p/factory`. Per Wiki V2 design goal #5, all agent control lives in `/p/wiki`. The monorepo carries only `docs/README.md` for humans. The agent learns how to act on this repo from the wiki's `tech/` pages and the `tools/` command surface — not from in-repo control files.

---

## The Cross-Platform Module Model

This is the load-bearing design decision and the one with the most options to weigh.

### The problem

`modules/render` must produce a JVM artifact (for tooling/tests on a fast platform), a Native artifact (for the compositor and browser, which are Native), and possibly a JS artifact (for any browser-rendered tool surface). The *layout algorithm* (Taffy-shaped logic) is identical across platforms; only the *FFI to the Rust libs* differs (Native links the static lib directly; JVM might use a JNI shim or a pure-Scala fallback; JS has no FFI at all and may stub or use WASM).

### Options explored

**Option A — Separate modules per platform, manual source sharing.**
`render-jvm`, `render-native`, `render-js`, each its own module, sharing code via a `render-shared` module they all `moduleDeps`. Explicit, dumb, works everywhere. But it triples the module count, and the shared module can only contain code that compiles on *all* platforms — the lowest common denominator. Platform-conditional shared logic becomes awkward.

**Option B — Mill's `CrossPlatform` + cross-axis.**
One module declaration parametrized over a platform axis. Mill generates `render.jvm`, `render.js`, `render.native` as cross-instances of one definition. Shared sources live in `src/`; platform sources in `src-jvm/`, `src-js/`, `src-native/` are added to the compile only for that platform. This is the idiomatic Mill answer and the one the earlier discussion landed on ("the `CrossPlatform` pattern in ~15 lines of `build.mill` is cleaner than three near-duplicate YAML files").

**Option C — sbt-crossproject-style with a build matrix in YAML.**
Mill's YAML build config can express cross-builds, but as the earlier discussion found, traits aren't a YAML concept — `extends:` takes module class names, not user-defined traits, so anything involving shared platform-specific behavior pushes you back into Scala anyway. YAML stops paying for itself exactly at the cross-platform boundary.

### Proposed approach: Option B

Use Mill's cross-platform module support with a shared `FactoryCross` trait. Source-directory convention:

```
modules/render/
  src/          → compiled for ALL platforms (the layout algorithm)
  src-jvm/      → compiled for JVM only (JNI shim or pure fallback)
  src-native/   → compiled for Native only (direct C-ABI to render-ffi)
  src-js/       → compiled for JS only (WASM stub or no-op)
  test/src/     → shared tests
  test/src-native/ → Native-only tests (FFI integration)
```

The `package.mill` declares the module once over the platform axis. A consumer that only needs Native (the compositor) depends on `render.native`; a consumer that wants to unit-test layout logic fast depends on `render.jvm`. The algorithm source is written *once*.

### Trade-offs

What we gain: single source of truth for shared logic; the compositor and browser provably share the *same* `render` algorithm code (they depend on the same cross-module, just the Native instance); fast JVM-side testing of platform-agnostic logic without spinning up Native compilation.

What we give up: the cross-axis adds a learning-curve tax on the build file, and Scala Native + Scala.js have real semantic differences (no reflection on Native, different `Future`/threading models) that the `src/` shared code must respect — the compiler enforces this per-platform, but it constrains how "shared" code can be written. There is also a non-trivial build-time cost: a full `__.compile` builds every platform of every module unless scoped.

### The shared-backend invariant, made mechanical

The whole point of the monorepo is that the compositor and browser share rendering. The invariant:

> `apps/compositor` and `apps/browser` both `moduleDeps` exactly `modules.render.native` — never a copy, never a fork.

This is mechanically checkable. `./mill show apps.compositor.transitiveModuleDeps` and the same for `browser` must both contain `render.native`. A wiki `lint` operation can run this query and flag drift if either app grows its own rendering code instead of depending on the shared module. This turns "they should share a backend" from a design aspiration into an auditable build fact — exactly the description-vs-prescription drift the wiki is built to catch.

---

## Root Build and Shared Traits

The root `build.mill` defines the traits every module inherits. This is where version constants, the repository list, common dependencies, and warning/hardening flags live — the things that, in Maven, would be in a parent POM's `<dependencyManagement>` and `<properties>`.

```scala
// build.mill  (illustrative — not a drop-in)
package build

import mill._, scalalib._, scalanativelib._, scalajslib._

// One place for versions. Moving a module out of the repo means
// inlining whichever of these it actually uses (the portability cost).
object V {
  val scala       = "3.7.0"
  val scalaNative = "0.5.x"
  val scalaJS     = "1.x"
  val kyo         = "<pinned>"
}

// Base trait: every Scala module in the factory extends this.
trait FactoryModule extends ScalaModule {
  def scalaVersion = V.scala
  // Hardened compiler posture: fail on warnings, no unsafe features.
  def scalacOptions = Seq(
    "-Wunused:all", "-Werror", "-deprecation",
    "-feature", "-explain", "-Yexplicit-nulls"
  )
  // Repositories come from the Nix-provided offline mirror, NOT the network.
  // NIX_MAVEN_REPO is set by the flake; coursier resolves file:// only.
  def repositoriesTask = Task.Anon {
    super.repositoriesTask() // augmented by NixMavenRepo, see nix/deps.nix
  }
}

// Cross-platform library trait: adds the platform axis.
trait FactoryCross extends FactoryModule with PlatformScalaModule
```

Two design points worth calling out:

**`-Werror` is deliberate and interacts with the wiki.** A warning-free build is a precondition for the wiki's `implement` operation to log a clean observation. When `implement` produces code that warns, the build *fails*, and that failure is itself a wiki observation — the self-learning loop catches sloppy generated code at the compiler, not in review.

**Repositories resolve offline.** Per the established TCB posture and the `mill-nixpkgs-design.md` work, the build never reaches the network for dependencies during a Nix build. `nix/deps.nix` provides a content-addressed Maven mirror; `NIX_MAVEN_REPO` points coursier at `file:///nix/store/…`. No OkHttp, no network, fully reproducible. The from-source Mill in `nix/mill.nix` structurally excludes OkHttp as designed.

### Subtree markers and portability

Each subtree (`modules/`, `apps/`) carries a `package.mill`. For large subtrees that should be movable as a unit, mark them with Mill 1.0's nested-build allowance:

```scala
//| mill-allow-nested-build-mill: true
package build.modules
```

This is the concrete mitigation for the portability concern raised earlier: a subtree marked this way is closer to standalone-ready, so extracting `modules/render` into its own open-source repository is `cp -r` plus inlining the `V.*` constants it uses and converting any `moduleDeps` on internal-only modules into `mvnDeps` on published artifacts. The build-file surgery is mechanical because the task graph is introspectable (`./mill show render.transitiveModuleDeps` gives the exact boundary).

### BOM: supported but redundant here

Mill supports BOMs (`bomMvnDeps`), but as established, they're largely redundant when the version constants already live in one root file and the dependency set is Nix-pinned anyway. A BOM earns its place only if `modules/render` is published for *external* consumers who need a coordinated version set without the Nix mirror. Defer it until there's an external consumer.

---

## Native Library Integration (Rust C-ABI)

The `native/` directory holds Rust static libraries with a C ABI, consumed by Scala Native modules via FFI. This matches the established pattern: `render-ffi` wraps Taffy/tiny-skia/resvg; `font-ffi` wraps fontdue (chosen as pure Rust specifically to avoid FreeType's CVE-2025-27363).

### Build ordering

The dependency chain is: Rust libs → C headers → Scala Native FFI bindings → linked binary. Nix orchestrates the ordering because it is the outer build:

```
native-libs.nix builds each Rust crate as a fixed-output-ish derivation
        ↓ produces librender_ffi.a + render-ffi.h in the Nix store
toolchain.nix exposes those paths via env (RENDER_FFI_LIB, RENDER_FFI_INCLUDE)
        ↓
Mill's render.native module references the .a at link time
        ↓ scala-native links against the static lib
apps.compositor.native produces the final binary
```

The Rust crates are built by Nix, not by Mill, deliberately: it keeps the Rust toolchain pinned at Layer 0 and means the static libs are content-addressed store paths. Mill never invokes `cargo`; it consumes the already-built `.a`. This preserves the layer discipline (Nix → Mill, never Mill → cargo as a side-channel) and keeps the Rust supply chain auditable through the same flake-lock mechanism as everything else.

### Linker flags in the Native module

```scala
// apps/compositor/package.mill (illustrative)
trait CompositorNative extends FactoryModule with ScalaNativeModule {
  def scalaNativeVersion = V.scalaNative
  def moduleDeps = Seq(build.modules.render.native, build.modules.core.native)
  // Static libs come from Nix-provided env, not vendored binaries.
  def nativeLinkingOptions = Task {
    Seq(
      s"-L${sys.env("RENDER_FFI_LIB")}",
      "-lrender_ffi",
      s"-L${sys.env("FONT_FFI_LIB")}",
      "-lfont_ffi",
      "-lwlroots"  // system lib, provided by the Nix shell
    )
  }
}
```

The key property: every linked path traces back to a pinned Nix store path or a Nix-provided system library. There are no binaries vendored into the repo and no `homebrew`/imperative-package-manager paths in the cryptographic or build-critical path — consistent with the established preference.

---

## Nix Flake: The Outer Boundary

`flake.nix` is the single entry point. It pins every tool, provides the dev shell, and defines build outputs and checks.

### What the flake pins

| Input | Why pinned |
|-------|-----------|
| nixpkgs | base for everything |
| Scala 3 toolchain | exact compiler version = reproducible bytecode |
| LLVM / Clang | Scala Native codegen + linking |
| Rust toolchain | `native/` C-ABI libs |
| JDK 21 | JVM target + Mill runtime |
| Node | Scala.js linker (if JS target used) |
| from-source Mill | the OkHttp-free derivation; the build tool itself is in the TCB |

### Outputs

```nix
# flake.nix (illustrative structure)
{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/<pinned>";
    # ... flake-utils, etc.
  };
  outputs = { self, nixpkgs, ... }: {
    # `nix develop` — the shell the agent and humans work in
    devShells.<sys>.default = pkgs.mkShell {
      packages = [ millFromSource scala3 clang rustToolchain jdk21 nodejs wlroots ];
      shellHook = ''
        export NIX_MAVEN_REPO=${import ./nix/deps.nix { ... }}
        export RENDER_FFI_LIB=${nativeLibs.render-ffi}/lib
        export FONT_FFI_LIB=${nativeLibs.font-ffi}/lib
      '';
    };
    # `nix build .#compositor` — reproducible app builds
    packages.<sys> = import ./nix/apps.nix { ... };
    # `nix flake check` — CI entry point
    checks.<sys> = import ./nix/checks.nix { ... };
  };
}
```

### Two build paths, one source of truth

There is a deliberate duality:

- **Inner loop (development):** `nix develop` drops you into the pinned shell, then `./mill __.compile` / `./mill apps.compositor.run`. Fast, incremental, Mill's caching active. This is what the agent uses for `implement`/`test`/`run`.
- **Outer loop (release/CI):** `nix build .#compositor` produces a fully reproducible, content-addressed artifact with no network and no mutable state. This is what CI and deployment use.

Both drive the same Mill build and the same source tree. The inner loop optimizes for iteration speed; the outer loop optimizes for reproducibility and auditability. The agent lives in the inner loop; the wiki's release observations come from the outer loop.

This mirrors the gwproxy/OPNsense infrastructure approach already in use — declarative flakes deployed to remote VMs with signed Nix store paths — extended here to the application build itself.

---

## Wiki Integration: The Agent Command Surface

This is where the monorepo and the sister wiki project meet. The wiki defines three code operations — `implement`, `test`, `run` — each of which ends by writing observations back into the wiki. For that loop to work, the monorepo must expose a **stable, deterministic, machine-parseable command surface**. That is the job of `tools/`.

### Design principle: the agent never reverse-engineers the build

The wiki's discovery chain is lazy and minimal — the agent reads only what a task needs. If acting on the code required the agent to first read and understand `build.mill`, that would violate the lazy-loading goal and reintroduce the eager-context problem Wiki V2 was built to solve. Instead, the monorepo offers a fixed verb surface that never changes shape, so the wiki's `tech/` pages can describe it once and the agent invokes it without re-learning.

### The verb surface

| Wiki op | Monorepo command | Deterministic output |
|---------|------------------|----------------------|
| `implement` | `nix develop -c ./mill <module>.compile` | exit code; `out/<module>/compile.dest/` |
| `test` | `tools/test.sh <module>` | JUnit XML at fixed path + JSON summary on stdout |
| `run` | `tools/run.sh <app>` | structured stdout/stderr, PID file, exit code |

`tools/test.sh` and `tools/run.sh` wrap Mill so the agent gets **structured output**, not raw build-tool chatter:

```bash
# tools/test.sh — wraps Mill, emits a JSON fact the wiki can ingest directly
#!/usr/bin/env bash
set -euo pipefail
module="${1:-__}"   # default: every module
nix develop -c ./mill "${module}.test" --report-format json \
  > "out/observations/test-$(date -u +%Y%m%dT%H%M%SZ).json"
# stdout: a one-line summary the agent reads; file: the full fact
jq -c '{passed, failed, skipped, duration}' "out/observations/"test-*.json | tail -1
```

### The observation contract

The self-learning loop depends on a stable schema for what the build *reports*. Define it once, in `tools/observe.sh`, as the contract between monorepo and wiki:

```json
{
  "operation": "test",
  "module": "modules.render.jvm",
  "commit": "<git sha>",
  "timestamp": "2026-05-24T10:00:00Z",
  "result": { "passed": 42, "failed": 0, "skipped": 1 },
  "duration_ms": 3170,
  "warnings": [],
  "drift_candidates": []
}
```

The wiki's `test` operation reads this and appends to `projects/factory/log.md`; if `failed > 0` or `warnings` is non-empty, it notes a synthesis or drift candidate exactly as the Wiki V2 `test` spec describes. The monorepo's contribution is guaranteeing the JSON is always there, always the same shape, at an always-known path (`out/observations/`). The agent never parses Mill's human-readable output.

### Selective execution for PR-scoped agent work

Mill's snapshot-diff selective execution is the mechanism that lets the agent (or CI) run only the tasks downstream of a change — the `bazel query` equivalent. When the agent's `implement` touches `modules/render/src/Layout.scala`, the wiki can scope `test` to exactly the affected downstream modules:

```bash
nix develop -c ./mill selective.resolve __.test  # what changed downstream?
nix develop -c ./mill selective.run    __.test  # run only those
```

This keeps each agent session's `test` observation tightly scoped to what it actually changed, which makes the resulting wiki log entry precise rather than a full-suite blur. It also bounds session cost, which matters when the agent runs many implement→test cycles.

### What the monorepo does NOT do for the agent

To respect the wiki's ownership and control model, the monorepo deliberately omits:

- **No `CLAUDE.md` / control files** — agent behavior is the wiki's concern (design goal #5).
- **No knowledge content** — architecture descriptions live as *descriptive* wiki pages derived by `ingest`, not as prose in the repo. A wiki page may say "factory uses the cross-platform pattern in `modules/render/package.mill`" — a verifiable claim pointing at a real file.
- **No prescriptions** — "render should be shared" is a *normative* ADR in `/p/wiki/projects/factory/adr/`, and the monorepo's job is merely to make that prescription mechanically checkable (the shared-backend invariant above). The gap between the ADR's prescription and the build's actual `transitiveModuleDeps` is drift the wiki can lint.

---

## End-to-End Flow: One Agentic Coding Cycle

Tracing a single `implement` request through both repos shows how the substrate and the wiki interlock:

```
1. Human: "implement ticket FACTORY-042: share glyph cache between
   compositor and browser"
        │
2. Agent reads /p/wiki/CLAUDE.md → recognizes `implement` op
        │
3. Agent reads /p/wiki/projects/factory/index.md
   → finds the ticket, related ADRs (shared-backend ADR),
     architecture.md, and the render pattern page
        │
4. Agent reads /p/wiki/sources/raw/code/factory.md
   → learns repo path /p/factory and entry points
        │
5. Agent enters the substrate:
   cd /p/factory && nix develop          ← Layer 0 pins toolchain
        │
6. Agent edits modules/render/src/GlyphCache.scala
   (shared source → both apps inherit it)
        │
7. Agent: nix develop -c ./mill selective.run __.compile
   → -Werror clean? If warnings, build FAILS = observation
        │
8. Agent: tools/test.sh modules.render
   → out/observations/test-*.json written
        │
9. Agent verifies the invariant still holds:
   ./mill show apps.compositor.transitiveModuleDeps | grep render.native
   ./mill show apps.browser.transitiveModuleDeps    | grep render.native
   → both still depend on the shared module ✓
        │
10. Agent writes observations back to /p/wiki:
    - append to projects/factory/log.md (what changed, test result)
    - update ticket FACTORY-042 status → closed
    - if a reusable pattern emerged → synthesis candidate
        │
11. Wiki is now an improved compiled view of the code.
```

Steps 5–9 happen in the monorepo; steps 1–4 and 10–11 in the wiki. The seam is exactly `sources/raw/code/factory.md` (step 4) and the structured observations (step 8/10). Neither repo needs to know the other's internals beyond that seam.

---

## Bootstrapping Sequence

Build order matters because each layer pins the next. Initial setup:

```
Phase 0: Nix foundation
  - Write flake.nix pinning nixpkgs + toolchains.
  - Port the from-source OkHttp-free Mill derivation (mill-nixpkgs-design.md)
    into nix/mill.nix. This is the long pole; everything depends on it.
  - `nix develop` must drop into a shell with `mill`, `scalac`, `clang`,
    `cargo`, `jdk`.

Phase 1: Mill skeleton
  - Root build.mill with FactoryModule / FactoryCross traits.
  - Empty modules/core as the first cross-platform module to prove the axis.
  - Verify: ./mill core.jvm.compile, core.native.compile both succeed.

Phase 2: Native libs
  - native/render-ffi and native/font-ffi Rust crates.
  - nix/native-libs.nix builds them; toolchain exposes paths.
  - Verify: the .a and .h appear in the Nix store, env vars resolve.

Phase 3: Shared render module
  - modules/render with the cross axis; native instance links render-ffi.
  - Verify: render.native.compile links; render.jvm.test runs layout tests.

Phase 4: Apps
  - apps/compositor and apps/browser, both moduleDeps render.native.
  - Verify the shared-backend invariant via transitiveModuleDeps.

Phase 5: Dependency mirror
  - Run mill2nix to generate nix/deps.nix + mill2nix.lock.
  - Verify: NIX_MAVEN_REPO set, build succeeds with network OFF.

Phase 6: Agent command surface
  - tools/{build,test,run,observe}.sh with the JSON observation contract.
  - Verify: tools/test.sh emits valid JSON at out/observations/.

Phase 7: Wiki seam
  - In /p/wiki, create sources/raw/code/factory.md pointing at /p/factory.
  - Run an `ingest` to produce the first descriptive pages.
  - Run one full implement→test→observe cycle end to end.
```

Phase 0 is the critical path and the riskiest — it reuses the existing from-source Mill design, so the risk is integration, not invention.

---

## Open Questions

1. **JS target: real or deferred?** The layout above provisions `src-js/` and a `.js` cross-instance, but no current app targets JS. Carrying the axis costs build complexity for a platform nothing ships yet. Option: declare `render` as `{jvm, native}` only for now, add `js` when a JS tool surface actually exists. Leaning toward deferring JS until there's a consumer.

2. **Rust libs in-repo vs. sibling repo.** `native/` lives in the monorepo here. Alternative: a separate `native` repo consumed as a flake input. In-repo gives atomic cross-language changes (edit Rust + Scala FFI in one commit); separate gives a cleaner open-source boundary for the Rust libs. The monorepo's atomic-change benefit probably wins until one of the Rust libs needs independent release.

3. **Observation storage location.** `out/observations/` is inside Mill's `out/`, which is git-ignored and wiped by `./mill clean`. Should observations be more durable (e.g. `tools/observations/` committed) or is the wiki log the durable record and `out/` just the handoff buffer? Leaning toward the latter: the wiki *is* the durable store; `out/` is ephemeral handoff.

4. **Selective execution baseline.** Mill's snapshot-diff needs a baseline snapshot to diff against. In an agent session, what is the baseline — the last commit, or the session start? This affects how `test` scopes itself. Needs a decision before Phase 6.

5. **Cross-repo navigation, restated.** This is open question #5 from Wiki V2, now half-answered: the agent discovers `/p/factory` from `sources/raw/code/factory.md`, and `nix develop` makes the toolchain location-independent. What remains: does the agent need write access to both repos in one session (yes, for the implement→observe loop), and how is that permissioned?

6. **Multi-instance parallelism.** The established tmux-based multi-instance Claude Code pattern could run several agent sessions against the monorepo at once. Mill's per-module locking and deterministic output paths should make this safe for *reads*, but concurrent `implement` on overlapping modules needs a coordination story — possibly the wiki ticket system as the lock.

---

## References

- `design-wiki-v2.md` — the sister LLM-wiki project this substrate serves
- `mill-nixpkgs-design.md` — the from-source, OkHttp-free Mill derivation reused in Phase 0
- Prior discussion: Mill monorepo/hierarchical builds, cross-platform module model, BOM support, subtree extraction portability


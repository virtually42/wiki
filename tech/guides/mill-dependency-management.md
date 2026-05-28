---
id: mill-dependency-management
title: Mill dependency management and auto-update strategy
kind: descriptive
status: draft
scope: global
created: 2026-05-24
updated: 2026-05-24
applies_to:
  languages: [scala, scala-native, scala-js]
---

## Problem

Each project currently maintains its own `deps/` folder with `Versions.mill`
and `Dependencies.mill`. This creates version drift across projects (e.g.,
toolbox has os-lib 0.11.7, paladium has 0.11.5) and requires manual updates.

We need:
1. A single source of truth for dependency versions (monorepo-wide)
2. Automated dependency updates (Renovate or similar)
3. The deps pattern to work with Mill's resolution and Nix's offline mirror

## Current Pattern: deps/ Folder

```
deps/
├── package.mill        # package build.deps; object `package` extends Module
├── Versions.mill       # version string constants
└── Dependencies.mill   # mvn"..." declarations using Versions
```

**Strengths:**
- Versions are centralized within each project
- Dependencies are typed (autocomplete in IDE)
- Platform availability is documentable per dep

**Weaknesses:**
- Duplicated across projects — each has its own copy with diverging versions
- No machine-readable format for Renovate to parse (Scala source, not TOML/JSON)
- `lazy val` vs `val` vs `def` inconsistency across projects
- Nested version objects (e.g., `V.Lihaoyi.osLib`) make regex-based update tools harder

## Options for the Monorepo

### Option A: Root deps/ folder (current pattern, unified)

Keep the existing pattern but with one `deps/` at the monorepo root.
All modules import from the same `build.deps.Versions`.

```scala
// /p/factory/deps/Versions.mill
package build.deps
object Versions:
  val scala       = "3.8.2"
  val scalaNative = "0.5.10"
  val scalaJS     = "1.20.2"
  val kyo         = "1.0-RC1"
  val munit       = "1.2.1"
  val scodec      = "2.3.2"
  // ...
```

**Renovate compatibility:** Renovate has a custom manager that can parse
regex patterns from any file format. A flat `val name = "version"` structure
is regex-friendly:

```json
{
  "customManagers": [{
    "customType": "regex",
    "fileMatch": ["deps/Versions\\.mill$"],
    "matchStrings": ["val (?<depName>[\\w]+)\\s*=\\s*\"(?<currentValue>[^\"]+)\""],
    "datasourceTemplate": "maven"
  }]
}
```

**Problem:** The regex can extract versions, but it can't map `val kyo = "1.0-RC1"`
to the Maven coordinate `io.getkyo:kyo-core_3`. Renovate needs to know
the artifact coordinate to look up new versions.

### Option B: Versions in a TOML/JSON sidecar

Keep `Dependencies.mill` for the typed API but extract versions into a
machine-readable file that Renovate natively understands:

```toml
# deps/versions.toml
[versions]
scala = "3.8.2"
scala-native = "0.5.10"
scala-js = "1.20.2"

[libraries]
kyo-core = { group = "io.getkyo", artifact = "kyo-core", version = "1.0-RC1" }
munit = { group = "org.scalameta", artifact = "munit", version = "1.2.1" }
scodec-core = { group = "org.scodec", artifact = "scodec-core", version = "2.3.2" }
```

Then `Versions.mill` reads the TOML at build time (Mill has no built-in
TOML parser, so this requires a build plugin or code generation step).

**Strengths:** Renovate can parse TOML natively via the `gradle` or custom manager.
**Weaknesses:** Indirection — two files to maintain, plus a parser dependency.

### Option C: Mill's built-in dependency resolution + Renovate regex on Dependencies.mill

Skip the Versions indirection entirely. Declare deps inline with full
coordinates in `Dependencies.mill`:

```scala
// deps/Dependencies.mill
package build.deps
import mill.*, scalalib.*

object Deps:
  val kyoCore    = mvn"io.getkyo::kyo-core::1.0-RC1"
  val munit      = mvn"org.scalameta::munit::1.2.1"
  val scodec     = mvn"org.scodec::scodec-core::2.3.2"
  val osLib      = mvn"com.lihaoyi::os-lib::0.11.7"
```

Renovate regex targets the full `mvn"group::artifact::version"` strings:

```json
{
  "customManagers": [{
    "customType": "regex",
    "fileMatch": ["deps/Dependencies\\.mill$"],
    "matchStrings": ["mvn\"(?<depName>[^:]+)::(?<packageName>[^:]+)::(?<currentValue>[^\"]+)\""],
    "datasourceTemplate": "maven",
    "registryUrlTemplate": "https://repo1.maven.org/maven2"
  }]
}
```

**Strengths:**
- Single source of truth (one file, one place per dep)
- Full Maven coordinates visible → Renovate can look up new versions
- No Versions.mill indirection to maintain
- Simpler mental model: "find the dep, see the version, change the version"

**Weaknesses:**
- Loses the grouped-version pattern (when multiple artifacts share a version, e.g., all Tapir modules at the same version)
- A version bump of Tapir requires changing N lines instead of one

**Mitigation for grouped versions:**

```scala
object Deps:
  private val tapirV = "1.11.11"
  val tapirCore      = mvn"com.softwaremill.sttp.tapir::tapir-core::$tapirV"
  val tapirNetty     = mvn"com.softwaremill.sttp.tapir::tapir-netty-server-sync:$tapirV"
  val tapirCirce     = mvn"com.softwaremill.sttp.tapir::tapir-json-circe:$tapirV"
```

Renovate's `groupName` feature can group these PRs together.

### Option D: Mill BOM (Bill of Materials)

Mill supports `bomMvnDeps` for coordinated version sets from upstream BOMs.
This is relevant when a library ecosystem publishes a BOM (e.g., Spring,
Vert.x). The Scala ecosystem generally does not publish BOMs, so this is
only useful for Java interop dependencies.

## Recommended Approach

**Option C** (inline full coordinates in Dependencies.mill) with grouped
version variables for multi-artifact libraries.

Rationale:
- The monorepo is the single consumer — there's no need for a reusable
  version catalog across repos (that's what BOMs are for)
- Renovate regex on `mvn"..."` strings is straightforward and well-tested
  in the ecosystem
- Grouped version variables keep the N-artifact-one-version case manageable
- No external tooling (TOML parsers, code generators) needed

### Proposed structure for the monorepo

```scala
// deps/Dependencies.mill
package build.deps
import mill.*, scalalib.*

// Grouped versions for multi-artifact libraries
private val kyoV    = "1.0-RC1"
private val tapirV  = "1.11.11"
private val scodecV = "2.3.2"

object Deps:
  // Core
  val kyoCore      = mvn"io.getkyo::kyo-core::$kyoV"
  val kyoPrelude   = mvn"io.getkyo::kyo-prelude::$kyoV"
  val scodecCore   = mvn"org.scodec::scodec-core::$scodecV"

  // Web (JVM only)
  val tapirCore    = mvn"com.softwaremill.sttp.tapir::tapir-core::$tapirV"
  val tapirNetty   = mvn"com.softwaremill.sttp.tapir::tapir-netty-server-sync:$tapirV"
  val tapirCirce   = mvn"com.softwaremill.sttp.tapir::tapir-json-circe:$tapirV"

  // Li Haoyi ecosystem
  val osLib        = mvn"com.lihaoyi::os-lib::0.11.7"
  val sourcecode   = mvn"com.lihaoyi::sourcecode::0.4.4"
  val pprint       = mvn"com.lihaoyi::pprint::0.9.4"

  // Test
  val munit        = mvn"org.scalameta::munit::1.2.1"
  val munitCheck   = mvn"org.scalameta::munit-scalacheck::1.1.0"

// Platform versions live alongside deps (single file to update)
object Platform:
  val scala       = "3.8.2"
  val scalaNative = "0.5.10"
  val scalaJS     = "1.20.2"
```

### What about Versions.mill?

**Drop it.** In the monorepo, the separate `Versions.mill` file adds
indirection without value. The version is right next to the coordinate
in `Dependencies.mill` — either inline or as a local `private val` for
grouped libraries. One file, one place to look, one place for Renovate
to target.

## Renovate Configuration

```json
{
  "extends": ["config:recommended"],
  "customManagers": [{
    "customType": "regex",
    "fileMatch": ["deps/Dependencies\\.mill$"],
    "matchStrings": [
      "mvn\"(?<depName>[^:]+)::(?<packageName>[^:]+)::(?<currentValue>[^\"]+)\"",
      "mvn\"(?<depName>[^:]+)::(?<packageName>[^:]+):(?<currentValue>[^\"]+)\""
    ],
    "datasourceTemplate": "maven",
    "registryUrlTemplate": "https://repo1.maven.org/maven2"
  }],
  "packageRules": [
    {
      "groupName": "kyo",
      "matchPackagePatterns": ["io.getkyo.*"]
    },
    {
      "groupName": "tapir",
      "matchPackagePatterns": ["com.softwaremill.sttp.tapir.*"]
    }
  ]
}
```

### Renovate vs Scala Steward

| | Renovate | Scala Steward |
|---|---|---|
| Mill support | Regex custom manager (works) | Native Mill support (since 0.20+) |
| Self-hosted | GitHub App or self-hosted | Self-hosted (JVM app) |
| Grouping | Flexible rules | Basic grouping |
| Nix integration | No special support | No special support |
| PR workflow | Mature, auto-merge rules | Mature |

**Scala Steward** understands Mill natively (parses `ivy"..."` and `mvn"..."`)
and can update versions in any `.mill` file without regex configuration.
It may be simpler than Renovate's regex approach for the Scala ecosystem.

**Recommendation:** Try Scala Steward first (less configuration for Mill),
fall back to Renovate if we need broader ecosystem coverage (Rust crates
in `Cargo.toml`, Nix flake inputs, Node deps).

## Interaction with Nix Offline Mirror

When dependencies are updated (by Renovate or Scala Steward), the Nix
offline mirror (`nix/deps.nix` or `mill2nix.lock`) must also be regenerated.
This is a post-update step:

1. PR updates `deps/Dependencies.mill`
2. CI runs `mill2nix` (or equivalent) to regenerate the lock
3. If the lock changes, commit it to the same PR
4. `nix build` verifies the build still works with offline resolution

This can be automated as a Renovate post-upgrade command or a CI step
triggered on deps/ changes.

## Open Questions

1. Should Scala Steward or Renovate manage platform versions (scala, scalaNative, scalaJS) as well, or are those pinned manually?
2. How does the offline mirror regeneration interact with the Nix flake lock? Both need updating atomically.
3. Should the monorepo use `mill-contrib-versionfile` for project-internal versioning?

## Upstream Reference

For the mechanical Mill API behind dependency declarations:

- [[mill/llm-wiki/configuration/dependencies]] — `mvnDeps`, the
  `mvn"..."` interpolator, cross-version syntax (`:`, `::`, `:::`)
- [[tech/decisions/deps-single-file]] — the normative decision this
  guide informed
- [[syntheses/wiki-layering-and-external-lib-wikis]] — how this guide
  relates to the Mill llm-wiki

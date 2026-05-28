---
id: mill-monorepo
title: Mill monorepo patterns — shared traits, subtrees, and module organization
kind: descriptive
status: draft
scope: global
created: 2026-05-24
updated: 2026-05-24
applies_to:
  languages: [scala, scala-native, scala-js]
---

## Problem

Multiple Scala projects (compositor, browser, web tools, shared libraries)
need to live in one repository with shared build configuration, consistent
compiler flags, and a discoverable module structure.

## Mill 1.x Monorepo Layout

```
/p/factory/
├── build.mill              # root: shared traits, version constants
├── .mill-version           # "1.1.2"
├── deps/
│   ├── package.mill        # package build.deps
│   └── Dependencies.mill   # all dep coordinates + platform versions
├── modules/
│   ├── package.mill        # package build.modules
│   ├── core/
│   │   └── package.mill    # the actual module definition
│   └── render/
│       └── package.mill
├── apps/
│   ├── package.mill        # package build.apps
│   ├── compositor/
│   │   └── package.mill
│   └── browser/
│       └── package.mill
└── native/                 # Rust C-ABI libs (built by Nix, not Mill)
```

## Root build.mill: Shared Traits

The root `build.mill` defines traits every module inherits:

```scala
//| mill-version: 1.1.2
//| mill-jvm-version: system

package build

import mill.*, scalalib.*, scalanativelib.*, scalajslib.*
import build.deps.{Platform, Deps}

// Base trait: all Scala modules
trait FactoryModule extends ScalaModule:
  def scalaVersion = Platform.scala
  override def scalacOptions = Seq(
    "-deprecation", "-feature", "-unchecked",
    "-Wunused:all", "-Werror", "-Yexplicit-nulls"
  )

// Native module trait
trait FactoryNative extends FactoryModule with ScalaNativeModule:
  def scalaNativeVersion = Platform.scalaNative
  override def scalacOptions = Task {
    super.scalacOptions().filterNot(_.startsWith("-release"))
  }

// JS module trait
trait FactoryJS extends FactoryModule with ScalaJSModule:
  def scalaJSVersion = Platform.scalaJS

// Native linking via pkg-config
trait PkgConfigLinked extends FactoryNative:
  def pkgConfigLibs: Seq[String] = Seq.empty
  override def nativeLinkingOptions = Task {
    val libs = pkgConfigLibs.flatMap { lib =>
      os.proc("pkg-config", "--libs", lib)
        .call(check = false).out.trim().split("\\s+").toSeq.filter(_.nonEmpty)
    }
    super.nativeLinkingOptions() ++ libs
  }
  override def nativeCompileOptions = Task {
    val flags = pkgConfigLibs.flatMap { lib =>
      os.proc("pkg-config", "--cflags", lib)
        .call(check = false).out.trim().split("\\s+").toSeq.filter(_.nonEmpty)
    }
    super.nativeCompileOptions() ++ flags
  }
```

## package.mill Files

Each subdirectory with a `package.mill` becomes a nested Mill package.
These are lightweight markers:

```scala
// modules/package.mill
package build.modules
import mill.*
```

Module definitions in subdirectories use the full package path:

```scala
// modules/core/package.mill
package build.modules
import mill.*, scalalib.*, scalanativelib.*
import build.{FactoryModule, FactoryNative}
import build.deps.{Platform, Deps}

object core extends Module:
  object jvm extends FactoryModule:
    override def sources = Task.Sources(moduleDir / os.up / "src")
    override def mvnDeps = super.mvnDeps() ++ Seq(Deps.kyoCore)
    object test extends ScalaTests with TestModule.Munit:
      override def mvnDeps = super.mvnDeps() ++ Seq(Deps.munit)

  object native extends FactoryNative:
    override def sources = Task.Sources(moduleDir / os.up / "src")
    override def mvnDeps = super.mvnDeps() ++ Seq(Deps.kyoCore)
```

## Module Organization Principles

### Libraries vs Applications

| Directory | Contains | Platform | Trait |
|-----------|----------|----------|-------|
| `modules/` | Cross-platform libraries (no main) | JVM + Native (+ JS when needed) | `FactoryModule` / `FactoryNative` |
| `apps/` | Deployable binaries | Native only | `FactoryNative` |

### Naming

- Module directories are kebab-case: `modules/render-engine/`
- Mill objects use kebab-case with backticks or camelCase: `` object `render-engine` `` or `object renderEngine`
- The package.mill uses the directory's package path

### Dependencies flow downward

```
apps/compositor  →  modules/render.native  →  modules/core.native
apps/browser     →  modules/render.native  →  modules/core.native
                    (shared!)
```

No upward dependencies. No cycles. Apps depend on modules; modules depend
on other modules. Never the reverse.

## Introspection Commands

Mill's task graph is introspectable — useful for CI, the wiki agent, and
verifying module relationships:

```bash
# List all modules
./mill resolve __

# Show a module's direct dependencies
./mill show modules.render.native.moduleDeps

# Show transitive dependencies (the full tree)
./mill show modules.render.native.transitiveModuleDeps

# Show all compilation tasks
./mill resolve __.compile

# Compile everything
./mill __.compile

# Test everything
./mill __.test

# Selective execution (only what changed)
./mill selective.resolve __.test
./mill selective.run __.test
```

## Subtree Portability

A module that may be extracted (open-sourced, moved to its own repo) should
minimize root-build coupling:

1. Use the shared traits but don't embed root-specific logic
2. Keep `moduleDeps` to published artifacts where possible
3. The extraction cost is: inline the trait definitions + convert internal
   `moduleDeps` to `mvnDeps` on published coordinates

Mill makes this mechanical: `./mill show <module>.transitiveModuleDeps`
gives the exact dependency boundary. Everything in that list either comes
with the extracted module or becomes an external dep.

## Build Performance

### Incremental compilation

Mill tracks source changes per-module. Editing `modules/core/src/Model.scala`
recompiles only `core` and its downstream dependents.

### Parallel compilation

Mill parallelizes independent tasks by default. `modules/render` and
`modules/net` compile in parallel if neither depends on the other.

### Selective execution

For CI on large monorepos, Mill's `selective.*` commands use snapshot diffs
to run only tasks affected by changes since a baseline:

```bash
# Create baseline snapshot
./mill selective.prepare __.compile __.test

# ... make changes ...

# Run only affected tasks
./mill selective.run __.test
```

### Avoiding full recompilation

- `-Werror` means any new warning in an unchanged file won't suddenly fail —
  warnings are stable across incremental compiles
- Scala Native linking is slow; structure tests to run on JVM via `.jvm.test`
  and only link Native for integration tests

## Common Mistakes

1. **Depending on the container instead of the platform instance.**
   Wrong: `moduleDeps = Seq(modules.render)` — that's the `Module` container.
   Right: `moduleDeps = Seq(modules.render.native)`

2. **Forgetting `super.nativeLinkingOptions()` in override.**
   Without `super.`, you lose upstream linking flags from trait composition.

3. **Using `-release` flag with Scala Native.**
   It's JVM-only. Filter it in `scalacOptions`.

4. **Hardcoding paths instead of using `moduleDir`.**
   `moduleDir` gives the module's source directory. Use it for relative
   references to sibling files.

5. **Cross-module `generatedSources` creating implicit build ordering.**
   If module A's `generatedSources` reads module B's output, Mill resolves
   this correctly but it's an implicit dependency. Make it a `moduleDep`
   or document it clearly.

## Upstream Reference

For the mechanical Mill API behind these patterns:

- [[mill/llm-wiki/patterns/multi-module]] — upstream multi-module
  pattern and module discovery
- [[mill/llm-wiki/patterns/build-file-structure]] — `build.mill` /
  `package.mill` conventions
- [[mill/llm-wiki/concepts/module-system]] — `Module`, nesting,
  hierarchy resolution
- [[mill/llm-wiki/concepts/build-graph]] — DAG, dependency resolution,
  topological sort (relevant when reasoning about
  `transitiveModuleDeps`)
- [[mill/llm-wiki/cli/task-resolution]] — how `__` wildcards and
  `./mill resolve` work (the introspection commands in this guide)
- [[syntheses/wiki-layering-and-external-lib-wikis]] — how this guide
  relates to the Mill llm-wiki

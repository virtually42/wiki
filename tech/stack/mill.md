---
id: mill
title: Mill Build Tool
kind: descriptive
status: active
scope: global
created: 2026-05-24
updated: 2026-05-24
capabilities: [build, dev-environment, testing]
used_by: []
version_notes: "1.1.2 — Mill 1.x series with .mill file support"
---

## Overview

Mill is the build tool for all Scala 3 projects. It provides first-class
support for Scala JVM, Scala.js, and Scala Native from a single build
definition written in Scala.

Mill was chosen over sbt for:
- Scala 3 as the build language (not a custom DSL)
- Native cross-platform module support (JVM/JS/Native from one definition)
- Deterministic per-module output paths (`out/<module>/`)
- Fast incremental compilation with snapshot-based selective execution
- Introspectable task graph (`./mill show`, `./mill resolve`)

## Build File Structure (Mill 1.x)

Mill 1.x uses `.mill` files with a `package build` declaration:

```
project/
├── build.mill              # root build, package build
├── .mill-version           # pins Mill version (e.g. "1.1.2")
├── modules/
│   ├── package.mill        # subtree marker, package build.modules
│   ├── core/
│   │   └── package.mill    # module definition
│   └── render/
│       └── package.mill
└── deps/
    ├── package.mill        # marker: package build.deps
    ├── Versions.mill       # version constants
    └── Dependencies.mill   # mvn coordinate objects
```

### Key conventions

- `//| mill-version: 1.1.2` at top of `build.mill` pins the Mill version
- `//| mill-jvm-version: system` uses the system JVM (relevant for Nix shells)
- `//| mvnDeps: [...]` declares build-time plugin dependencies
- Each directory with a `package.mill` becomes a nested package under `build`

## Cross-Platform Modules

Mill supports two patterns for cross-platform code:

### Pattern 1: Manual cross-axis (current usage)

Separate objects per platform sharing sources via `Task.Sources`:

```scala
object webgpu extends Module:
  trait Shared extends ScalaModule:
    def sharedSources = Task.Sources(moduleDir / os.up / "src")

  object js extends Shared with ScalaJSModule:
    def jsSources = Task.Sources(moduleDir / os.up / "src-js")
    override def sources = Task {
      super.sources() ++ sharedSources() ++ jsSources()
    }

  object native extends Shared with ScalaNativeModule:
    def nativeSources = Task.Sources(moduleDir / os.up / "src-native")
    override def sources = Task {
      super.sources() ++ sharedSources() ++ nativeSources()
    }
```

### Pattern 2: Cross[] with PlatformScalaModule

Full cross-build matrix using Mill's `Cross` mechanism:

```scala
trait Shared extends CrossScalaModule with PlatformScalaModule:
  override def mvnDeps = super.mvnDeps() ++ Seq(deps.core)

object paladium extends Module:
  object jvm    extends Cross[JvmModule](scalaVersions)
  object js     extends Cross[JsModule](scalaVersions)
  object native extends Cross[NativeModule](scalaVersions)
```

### Source directory convention

```
module/
├── src/            # shared across ALL platforms
├── src-jvm/        # JVM-only
├── src-js/         # Scala.js-only
├── src-native/     # Scala Native-only
├── test/
│   ├── src/        # shared tests
│   └── src-native/ # platform-specific tests
```

## Dependency Management

### The deps/ pattern

A `deps/` directory at project root containing:

- `package.mill` — marker extending `Module`
- `Versions.mill` — version string constants
- `Dependencies.mill` — `mvn"group::artifact::version"` declarations

```scala
// deps/Versions.mill
package build.deps
object Versions:
  val scala       = "3.8.2"
  val scalaNative = "0.5.10"
  val kyo         = "1.0-RC1"

// deps/Dependencies.mill
package build.deps
import build.deps.{Versions => V}
object Kyo:
  def kyoCore = mvn"io.getkyo::kyo-core::${V.Kyo.kyo}"
```

Consumed in modules via `import deps.{Versions, Dependencies}` or
`import build.deps.{Versions => V, ...}`.

### Platform availability markers

Dependencies use `::` (double-colon) for cross-platform artifacts and
`:` (single-colon) for platform-specific ones. The deps file documents
platform constraints with comments:

```scala
/** N => Only available on Native
  * J => Only available on JVM
  * S => Only available on Scala.js
  */
object Tapir:
  /** J - JVM only */
  def nettyServerSync = mvn"com.softwaremill.sttp.tapir::tapir-netty-server-sync:${V.Tapir.tapir}"
```

### mvn vs ivy string syntax

Mill 1.x uses `mvn"group::artifact::version"` for cross-platform Scala deps.
The older `ivy"group::artifact::version"` syntax still works but `mvn` is
preferred for new code.

## Native Linking

### pkg-config integration

A common trait for modules that link against system libraries:

```scala
trait NativeLinked extends BroModule:
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

### Rust C-ABI static libraries

Link against pre-built Rust `.a` files:

```scala
trait RustShimLinked extends BroModule:
  override def nativeLinkingOptions = Task {
    val shimLib = (moduleDir / os.up / "rust-shims" / "target" / "release" / "libbrowser_shims.a").toString
    super.nativeLinkingOptions() ++ Seq(shimLib, "-ldl", "-lpthread", "-lm")
  }
```

## Scala.js Configuration

```scala
object frontend extends ScalaJSModule:
  def scalaJSVersion = V.scalaJS
  override def moduleKind = ModuleKind.ESModule        // for Vite/bundler
  override def moduleSplitStyle = ModuleSplitStyle.FewestModules
  override def scalaJSExperimentalUseWebAssembly = true // WASM target
```

## Compiler Hardening

```scala
trait FactoryModule extends ScalaModule:
  override def scalacOptions = Seq(
    "-deprecation", "-feature", "-unchecked",
    "-Wunused:all", "-Werror"
  )
```

Note: Scala Native requires filtering `-release` flags:
```scala
override def scalacOptions = Task {
  super.scalacOptions().filterNot(opt =>
    opt.startsWith("-release") || opt.startsWith("--release")
  )
}
```

## Agent Interface

Key Mill commands for the wiki's implement/test/run operations:

| Operation | Command | Output |
|-----------|---------|--------|
| Compile all | `./mill __.compile` | `out/<module>/compile.dest/` |
| Compile one | `./mill modules.core.compile` | deterministic path |
| Test all | `./mill __.test` | test reports |
| Test one | `./mill modules.core.test` | per-module report |
| Run app | `./mill apps.compositor.run` | stdout/stderr |
| Show deps | `./mill show <module>.transitiveModuleDeps` | JSON array |
| Resolve tasks | `./mill resolve __.compile` | task list |
| Selective test | `./mill selective.run __.test` | only changed |

## Operational Notes

- Mill's `out/` directory is gitignored; it contains all build artifacts
- `.mill-version` pins the Mill launcher version (must match Nix-provided Mill)
- Build plugins are declared in `//| mvnDeps: [...]` at the top of build.mill
- `mill-contrib-buildinfo` is commonly used for compile-time constants

## Known Issues

- Scala Native modules must filter `-release` compiler flags (JVM-only option)
- Cross-build with `Cross[Module](versions)` requires careful `moduleDeps` wiring — reference the cross instance, not the container (e.g., `paladium.jvm(scalaVersions)`)
- `generatedSources` tasks that depend on other modules' outputs (e.g., ScalaJS → embed in Native) create cross-module build dependencies that Mill resolves correctly but add complexity

## Links

- [Mill documentation](https://mill-build.org/docs)
- [[tech/decisions/build-system-mill]] (pending)

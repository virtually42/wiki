---
id: mill-cross-platform
title: Cross-platform Scala modules in Mill
kind: descriptive
status: draft
scope: global
created: 2026-05-24
updated: 2026-05-24
applies_to:
  languages: [scala, scala-native, scala-js]
---

## Problem

A library module must compile to multiple platforms (JVM, JS, Native) from
shared source code, while allowing platform-specific implementations for
FFI, threading, or browser APIs.

## Patterns in Current Projects

### Pattern A: Namespace container with manual source sharing (fashion-designer, swc)

```scala
object webgpu extends Module:
  trait Shared extends ScalaModule:
    def scalaVersion = V.scala
    def sharedSources = Task.Sources(moduleDir / os.up / "src")

  object js extends Shared with ScalaJSModule:
    def scalaJSVersion = V.scalaJS
    def jsSources = Task.Sources(moduleDir / os.up / "src-js")
    override def sources = Task {
      super.sources() ++ sharedSources() ++ jsSources()
    }

  object native extends Shared with ScalaNativeModule:
    def scalaNativeVersion = V.scalaNative
    def nativeSources = Task.Sources(moduleDir / os.up / "src-native")
    override def sources = Task {
      super.sources() ++ sharedSources() ++ nativeSources()
    }
```

**Directory layout:**
```
webgpu/
├── src/          # shared (compiled for all platforms)
├── src-js/       # JS-only
├── src-native/   # Native-only
├── js/           # Mill object dir (module metadata)
└── native/       # Mill object dir
```

**Characteristics:**
- Each platform is a separate Mill module object
- Shared sources added via explicit `Task.Sources(moduleDir / os.up / "src")`
- Consumer depends on the specific platform: `moduleDeps = Seq(webgpu.js)`
- No `Cross[]` machinery — simpler to understand
- Works well when you only target 2 platforms

### Pattern B: Cross[] with PlatformScalaModule (paladium)

```scala
trait Shared extends CrossScalaModule with PlatformScalaModule:
  override def mvnDeps = super.mvnDeps() ++ Seq(Lihaoyi.sourcecode, Scodec.core)

trait Js extends Shared with ScalaJSModule:
  override def scalaJSVersion = V.scalaJS

trait Native extends Shared with ScalaNativeModule:
  override def scalaNativeVersion = V.scalaNative

object paladium extends Module:
  trait JvmModule extends Shared { ... }
  object jvm    extends Cross[JvmModule](scalaVersions)
  trait JsModule extends Js { ... }
  object js     extends Cross[JsModule](scalaVersions)
  trait NativeModule extends Native { ... }
  object native extends Cross[NativeModule](scalaVersions)
```

**Characteristics:**
- Full cross-build matrix: platforms × Scala versions
- Uses `PlatformScalaModule` for automatic platform source detection
- Consumer uses: `moduleDeps = Seq(paladium.jvm(scalaVersions))`
- More ceremony but supports multi-version publishing

### Pattern C: Flat per-platform modules with shared core (swc/compositor)

```scala
object core extends Module:
  object jvm extends CoreModule:
    // shared sources via: override def sources = Task.Sources(moduleDir / os.up / "src")
  object native extends CoreModule with ScalaNativeModule:
    def scalaNativeVersion = "0.5.10"

object compositor extends ScalaNativeModule:
  override def moduleDeps = Seq(core.native)
```

**Characteristics:**
- Simplest pattern when there's one "real" platform (Native) and JVM is just for testing
- No cross machinery at all
- JVM module exists purely for fast test feedback on shared logic

### Pattern D: Native-only with no cross (bro)

```scala
trait BroModule extends ScalaNativeModule:
  def scalaVersion       = V.scala
  def scalaNativeVersion = V.scalaNative

object modules extends Module:
  object core extends BroModule
  object render extends BroModule:
    override def moduleDeps = Seq(core)
  object dom extends BroModule:
    override def moduleDeps = Seq(core)
  // ...
```

**Characteristics:**
- Everything is Native — no cross-platform axis
- Simple, fast builds — no platform multiplication
- Appropriate when the app is fundamentally single-platform

## Choosing a Pattern

| Situation | Pattern | Why |
|-----------|---------|-----|
| App is single-platform (compositor, browser) | D (Native-only) | No cross overhead |
| Shared lib with JVM for testing only | C (flat core.jvm/core.native) | Minimal ceremony |
| Shared lib targeting 2-3 platforms | A (namespace + manual sources) | Explicit, readable |
| Publishing to multiple Scala versions + platforms | B (Cross[] matrix) | Required for publishing |

## Monorepo Recommendation

For the factory monorepo, a hybrid:

- **modules/** use Pattern A (namespace container) — they target JVM + Native,
  with JS added only when needed. The manual source wiring is explicit and
  Pattern A doesn't require `Cross[]` version parameterization since the
  monorepo pins one Scala version.

- **apps/** use Pattern D (single-platform Native-only) — they're leaf
  binaries that `moduleDeps` the cross-platform modules' `.native` instance.

```scala
// modules/render/package.mill
package build.modules
import mill.*, scalalib.*, scalanativelib.*
import build.deps.{Platform, Deps}

object render extends Module:
  trait Shared extends ScalaModule:
    def scalaVersion = Platform.scala
    def sharedSources = Task.Sources(moduleDir / os.up / "src")
    override def mvnDeps = super.mvnDeps() ++ Seq(Deps.kyoCore)

  object jvm extends Shared:
    override def sources = Task { super.sources() ++ sharedSources() }
    object test extends ScalaTests with TestModule.Munit:
      override def mvnDeps = super.mvnDeps() ++ Seq(Deps.munit)

  object native extends Shared with ScalaNativeModule:
    def scalaNativeVersion = Platform.scalaNative
    def nativeSources = Task.Sources(moduleDir / os.up / "src-native")
    override def sources = Task { super.sources() ++ sharedSources() ++ nativeSources() }
    override def nativeLinkingOptions = Task {
      super.nativeLinkingOptions() ++ Seq(
        s"-L${sys.env("RENDER_FFI_LIB")}", "-lrender_ffi"
      )
    }

// apps/compositor/package.mill
package build.apps
import mill.*, scalanativelib.*
import build.deps.Platform
import build.modules

object compositor extends ScalaNativeModule:
  def scalaVersion = Platform.scala
  def scalaNativeVersion = Platform.scalaNative
  override def moduleDeps = Seq(modules.render.native, modules.core.native)
```

## Key Invariants

1. **Shared source is written once.** `modules/render/src/` contains the
   platform-agnostic rendering algorithm. Both `render.jvm` and `render.native`
   compile it.

2. **Tests run on JVM for speed.** `render.jvm.test` tests the shared logic
   without Scala Native compile time. Native-specific tests live in
   `test/src-native/`.

3. **Apps depend on `.native`, never on the container.** Correct:
   `moduleDeps = Seq(modules.render.native)`. Wrong:
   `moduleDeps = Seq(modules.render)` (that's the Module container, not a compilable module).

4. **The shared-backend invariant is checkable:**
   ```bash
   ./mill show apps.compositor.transitiveModuleDeps | grep render.native
   ./mill show apps.browser.transitiveModuleDeps    | grep render.native
   ```

## Platform Gotchas

### Scala Native
- Must filter `-release` compiler flag (JVM-only)
- `ScalaNativeModule` requires `def scalaNativeVersion`
- Linking options are cumulative — use `super.nativeLinkingOptions() ++ ...`
- `nativeMultithreading = Some(false)` disables multi-threading (needed for some FFI)

### Scala.js
- `ModuleKind.ESModule` required for Vite/bundler integration and WASM
- `ModuleSplitStyle.FewestModules` for WASM targets
- `scalaJSExperimentalUseWebAssembly = true` enables WASM compilation
- Tests may need different `moduleKind` than the main module (CommonJS for Node test runner)

### Shared code constraints
- No reflection (Native doesn't support it)
- No `java.io.File` in shared code (use os-lib or platform-specific sources)
- Threading models differ: JVM has real threads, Native has optional, JS is single-threaded
- String interpolation with `\n` works everywhere but file paths must use os-lib's `os.sep`

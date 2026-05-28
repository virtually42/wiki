---
id: scalajs-module
title: ScalaJSModule
section: modules
source_files:
  - /p/gh/mill/libs/scalajslib/src/mill/scalajslib/ScalaJSModule.scala
source_commit: 41ce6c977c4
related:
  - modules/scala-module.md
  - recipes/scalajs-project.md
  - recipes/multi-platform.md
---

# ScalaJSModule

Extends `ScalaModule` for Scala.js cross-compilation to JavaScript.

## Import

```scala
import mill._, scalalib._, scalajslib._
```

## Minimal Example

```scala
object frontend extends ScalaJSModule {
  def scalaVersion = "3.6.4"
  def scalaJSVersion = "1.18.2"
}
```

## Key Tasks

| Task | Type | Description |
|------|------|-------------|
| `scalaJSVersion` | `T[String]` | Scala.js version (required) |
| `moduleKind` | `T[ModuleKind]` | `NoModule`, `CommonJSModule`, `ESModule` |
| `moduleSplitStyle` | `T[ModuleSplitStyle]` | Code splitting strategy |
| `esFeatures` | `T[ESFeatures]` | ES version features |
| `jsEnvConfig` | `T[JsEnvConfig]` | JS runtime (Node, JSDom, etc.) |
| `scalaJSOptimizer` | `T[Boolean]` | Enable Closure optimizer |
| `fastLinkJS` | `T[Report]` | Fast-optimized JS output |
| `fullLinkJS` | `T[Report]` | Fully-optimized JS output |

## Module Kind

```scala
import mill.scalajslib.api.ModuleKind

def moduleKind = ModuleKind.ESModule      // ES modules (import/export)
def moduleKind = ModuleKind.CommonJSModule // CommonJS (require/module.exports)
def moduleKind = ModuleKind.NoModule       // No module system (default)
```

## ES Module Output

```scala
object frontend extends ScalaJSModule {
  def scalaVersion = "3.6.4"
  def scalaJSVersion = "1.18.2"
  def moduleKind = ModuleKind.ESModule
  def moduleSplitStyle = ModuleSplitStyle.SmallModulesFor(
    List("myapp")
  )
}
```

## JS Environment

```scala
import mill.scalajslib.api.JsEnvConfig

// Node.js (default)
def jsEnvConfig = JsEnvConfig.NodeJs()

// Node.js with args
def jsEnvConfig = JsEnvConfig.NodeJs(
  args = List("--experimental-modules")
)

// JSDom (browser-like)
def jsEnvConfig = JsEnvConfig.JsDom()
```

## Testing

```scala
object tests extends ScalaJSTests with TestModule.Munit {
  def mvnDeps = Seq(mvn"org.scalameta::munit::1.0.0")
}
```

Note the `::` suffix for Scala.js test dependencies — Mill handles
the platform suffix automatically via `mvn"org::name::version"` syntax.

## CLI Commands

```bash
mill frontend.fastLinkJS    # fast dev build
mill frontend.fullLinkJS    # optimized production build
mill frontend.run           # run with Node.js
mill frontend.tests.test    # run tests
```

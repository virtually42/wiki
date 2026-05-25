---
id: scala-native-module
title: ScalaNativeModule
section: modules
source_files:
  - libs/scalanativelib/src/mill/scalanativelib/ScalaNativeModule.scala
source_commit: 41ce6c977c4
related:
  - modules/scala-module.md
  - recipes/scala-native-project.md
  - recipes/multi-platform.md
---

# ScalaNativeModule

Extends `ScalaModule` for Scala Native compilation to native binaries.

## Import

```scala
import mill._, scalalib._, scalanativelib._
```

## Minimal Example

```scala
object myapp extends ScalaNativeModule {
  def scalaVersion = "3.6.4"
  def scalaNativeVersion = "0.5.7"
}
```

## Key Tasks

| Task | Type | Description |
|------|------|-------------|
| `scalaNativeVersion` | `T[String]` | Scala Native version (required) |
| `releaseMode` | `T[ReleaseMode]` | `Debug`, `ReleaseFast`, `ReleaseFull`, `ReleaseSize` |
| `logLevel` | `T[NativeLogLevel]` | Compiler output verbosity |
| `nativeLinkingOptions` | `T[Seq[String]]` | Linker flags (e.g., `-L/path/to/lib`) |
| `nativeCompileOptions` | `T[Seq[String]]` | C compiler flags |
| `nativeLink` | `T[PathRef]` | Linked native binary |

## Release Modes

```scala
import mill.scalanativelib.api.ReleaseMode

def releaseMode = ReleaseMode.Debug        // fast compile, slow run (default)
def releaseMode = ReleaseMode.ReleaseFast  // balanced
def releaseMode = ReleaseMode.ReleaseFull  // slow compile, fast run
def releaseMode = ReleaseMode.ReleaseSize  // optimize for binary size
```

## Native Linking

```scala
def nativeLinkingOptions = Seq(
  "-L/usr/local/lib",
  "-lsqlite3"
)

def nativeCompileOptions = Seq(
  "-I/usr/local/include"
)
```

## Testing

```scala
object tests extends ScalaNativeTests with TestModule.Munit {
  def mvnDeps = Seq(mvn"org.scalameta::munit::1.0.0")
}
```

## CLI Commands

```bash
mill myapp.nativeLink       # compile and link native binary
mill myapp.run              # link and run
mill myapp.tests.test       # run tests
```

---
id: module-system
title: Module System
section: concepts
source_files:
  - /p/gh/mill/core/api/src/mill/api/Module.scala
  - /p/gh/mill/core/api/src/mill/api/ModuleCtx.scala
source_commit: 41ce6c977c4
related:
  - concepts/task-system.md
  - concepts/build-graph.md
  - patterns/multi-module.md
---

# Module System

Modules are the organizational units in Mill. A build is a tree of modules,
each containing tasks and nested sub-modules.

## Key Types

### Module

```scala
// core/api/src/mill/api/Module.scala
trait Module {
  def moduleDirectChildren: Seq[Module]
  def moduleDir: os.Path           // module's source directory
  def moduleSegments: Segments     // full path from root (e.g. foo.bar.baz)
}
```

Every `object` or `trait` extending `Module` (or a subtype like `JavaModule`)
becomes a node in the build tree. Nested objects create child modules.

### ModuleCtx

```scala
// core/api/src/mill/api/ModuleCtx.scala
trait ModuleCtx {
  def enclosing: String            // lexical context name
  def fileName: String             // source file
  def lineNum: Int                 // source line
  def millSourcePath: os.Path      // module's source directory
  def segments: Segments           // full path from root
  def enclosingModule: Module      // parent module
  def crossValues: Seq[Any]        // cross-build dimension values
  def discover: Discover           // metadata discovery
}
```

Implicitly available inside module definitions. Provides location and
hierarchy information.

## Module Discovery

Mill uses reflection to discover:
- Nested `object` definitions -> child modules
- `def` methods returning `Task[T]` -> tasks
- `def` methods with `Task.Command` -> CLI commands

No manual registration needed. Define an `object` extending a module trait
and it's automatically part of the build tree.

## Module Types

| Type | Trait | Purpose |
|------|-------|---------|
| Root module | `RootModule` | Top-level build definition |
| Java module | `JavaModule` | JVM compilation + packaging |
| Scala module | `ScalaModule` | Scala compilation |
| Test module | `TestModule` | Test execution |
| Publish module | `PublishModule` | Maven/Ivy publishing |
| Cross module | `Cross[T]` | Cross-version builds |
| External module | `ExternalModule` | Build helpers outside project |

## Nesting Pattern

```scala
// build.mill
import mill._, scalalib._

object myapp extends ScalaModule {
  def scalaVersion = "3.6.4"

  object tests extends ScalaTests with TestModule.Munit {
    def mvnDeps = Seq(mvn"org.scalameta::munit:1.0.0")
  }

  object sub extends ScalaModule {
    def scalaVersion = myapp.scalaVersion
    def moduleDeps = Seq(myapp)
  }
}
```

CLI paths mirror nesting: `mill myapp.tests.test`, `mill myapp.sub.compile`.

## Source Directory Convention

Each module's sources default to `<moduleDir>/src/`. For a module at
`build.mill > object foo > object bar`, the source directory is `foo/bar/src/`.

Override with:
```scala
def sources = Task.Sources("custom-src")
```

---
id: multi-module
title: Multi-Module Projects
section: patterns
source_commit: 41ce6c977c4
related:
  - concepts/module-system.md
  - configuration/dependencies.md
  - patterns/build-file-structure.md
---

# Multi-Module Projects

How to organize builds with multiple modules.

## Basic Multi-Module

```scala
// build.mill
import mill._, scalalib._

trait MyModule extends ScalaModule {
  def scalaVersion = "3.6.4"
}

object core extends MyModule {
  def mvnDeps = Seq(mvn"com.lihaoyi::os-lib:0.11.4")
}

object domain extends MyModule {
  def moduleDeps = Seq(core)
}

object app extends MyModule {
  def moduleDeps = Seq(domain)

  object tests extends ScalaTests with TestModule.Munit {
    def mvnDeps = Seq(mvn"org.scalameta::munit:1.0.0")
  }
}
```

## Shared Configuration Trait

Extract common settings into a trait:

```scala
trait MyModule extends ScalaModule with ScalafmtModule {
  def scalaVersion = "3.6.4"
  def scalacOptions = Seq("-deprecation", "-Wunused:all")

  trait MyTests extends ScalaTests with TestModule.Munit {
    def mvnDeps = Seq(mvn"org.scalameta::munit:1.0.0")
  }
}

object core extends MyModule {
  object tests extends MyTests
}

object app extends MyModule {
  def moduleDeps = Seq(core)
  object tests extends MyTests
}
```

## Dependency Types Between Modules

```scala
object app extends MyModule {
  // Compile + runtime dependency — app can use core's classes,
  // and core's classes are on app's runtime classpath
  def moduleDeps = Seq(core)

  // Compile-only — available at compile time but not runtime
  // Use for annotation processors, macro libraries
  def compileModuleDeps = Seq(macros)

  // Runtime-only — on runtime classpath but not compile classpath
  // Use for runtime implementations (SLF4J backends, etc.)
  def runModuleDeps = Seq(logbackImpl)
}
```

## CLI Operations on Multi-Module

```bash
mill __.compile          # compile all modules
mill __.test             # test all modules
mill app.compile         # compile app (and its deps)
mill _.compile           # compile all top-level modules
```

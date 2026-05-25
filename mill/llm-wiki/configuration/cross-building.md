---
id: cross-building
title: Cross-Building
section: configuration
source_files:
  - core/api/src/mill/api/Cross.scala
source_commit: 41ce6c977c4
related:
  - modules/scala-module.md
  - recipes/multi-platform.md
---

# Cross-Building

Build the same code across multiple versions or platforms.

## Cross-Scala Versions

```scala
object mylib extends Cross[MylibModule]("2.13.16", "3.6.4")
trait MylibModule extends CrossScalaModule {
  // scalaVersion is automatically set from the cross value
  def mvnDeps = Seq(mvn"com.lihaoyi::upickle:4.1.0")

  object tests extends CrossScalaTests with TestModule.Munit {
    def mvnDeps = Seq(mvn"org.scalameta::munit:1.0.0")
  }
}
```

CLI:
```bash
mill mylib[3.6.4].compile
mill mylib[2.13.16].compile
mill mylib[_].compile          # all versions
```

## Cross Module Traits

| Trait | Cross Dimensions |
|-------|-----------------|
| `Cross.Module[T1]` | 1 dimension |
| `Cross.Module2[T1, T2]` | 2 dimensions |
| `Cross.Module3[T1, T2, T3]` | 3 dimensions |

## Multi-Dimension Cross

```scala
val scalaVersions = Seq("2.13.16", "3.6.4")
val platforms = Seq("jvm", "js", "native")

object mylib extends Cross[MylibModule](scalaVersions.flatMap(sv => platforms.map(p => (sv, p))))
trait MylibModule extends ScalaModule with Cross.Module2[String, String] {
  val (sv, platform) = (crossValue, crossValue2)
  def scalaVersion = sv
  // platform-specific configuration...
}
```

## CrossScalaModule

Convenience trait that sets `scalaVersion` from `crossValue`:

```scala
trait MylibModule extends CrossScalaModule {
  // No need to manually set scalaVersion
  // crossValue is automatically used
}
```

## Accessing Cross Values

```scala
trait MylibModule extends ScalaModule with Cross.Module[String] {
  def crossValue: String     // the cross dimension value
  // For Module2:
  // def crossValue: T1
  // def crossValue2: T2
}
```

## Cross-Module Dependencies

```scala
object core extends Cross[CoreModule]("2.13.16", "3.6.4")
trait CoreModule extends CrossScalaModule { ... }

object app extends Cross[AppModule]("2.13.16", "3.6.4")
trait AppModule extends CrossScalaModule {
  def moduleDeps = Seq(core(crossValue))  // match cross values
}
```

## CLI Cross Syntax

```bash
mill mylib[3.6.4].compile          # specific cross value
mill mylib[_].compile              # all cross values (wildcard)
mill mylib[2.13.16].tests.test     # nested module in cross
```

---
id: scala-module
title: ScalaModule
section: modules
source_files:
  - /p/gh/mill/libs/scalalib/src/mill/scalalib/ScalaModule.scala
source_commit: 41ce6c977c4
related:
  - modules/java-module.md
  - modules/scalajs-module.md
  - modules/scala-native-module.md
  - configuration/cross-building.md
---

# ScalaModule

Extends `JavaModule` with Scala compilation support.

## Import

```scala
import mill._, scalalib._
```

## Minimal Example

```scala
object myapp extends ScalaModule {
  def scalaVersion = "3.6.4"
  def mvnDeps = Seq(
    mvn"com.lihaoyi::os-lib:0.11.4"
  )
}
```

## Key Tasks (beyond JavaModule)

### Scala Version (required)

```scala
def scalaVersion: T[String] = "3.6.4"    // Scala 3
def scalaVersion: T[String] = "2.13.16"  // Scala 2
```

### Compiler Options

```scala
def scalacOptions = Seq(
  "-deprecation",
  "-unchecked",
  "-Wunused:all",         // Scala 3
  "-Xfatal-warnings"
)
```

### Compiler Plugins

```scala
def scalacPluginMvnDeps = Seq(
  mvn"org.typelevel:::kind-projector:0.13.3"   // ::: for full cross-version
)
```

### Scala-Specific Tasks

| Task | Type | Description |
|------|------|-------------|
| `scalaVersion` | `T[String]` | Scala compiler version (required) |
| `scalacOptions` | `T[Seq[String]]` | Scalac compiler flags |
| `scalacPluginMvnDeps` | `T[Seq[Dep]]` | Compiler plugin dependencies |
| `scalaCompilerBridge` | `T[Option[PathRef]]` | Zinc bridge JAR |
| `scalaDocOptions` | `T[Seq[String]]` | Scaladoc flags |
| `platformSuffix` | `T[String]` | Cross-version suffix (_2.13, _3) |

## Cross-Version Builds

```scala
object mylib extends Cross[MylibModule]("2.13.16", "3.6.4")
trait MylibModule extends CrossScalaModule {
  // scalaVersion automatically set from crossValue
  def mvnDeps = Seq(mvn"com.lihaoyi::upickle:4.1.0")
}
```

CLI: `mill mylib[3.6.4].compile`, `mill mylib[2.13.16].test`

## Dependency Cross-Version Syntax

```scala
def mvnDeps = Seq(
  mvn"org.apache.commons:commons-lang3:3.14.0",  // Java dep (no ::)
  mvn"com.lihaoyi::os-lib:0.11.4",               // Scala dep (:: = binary version)
  mvn"org.typelevel:::kind-projector:0.13.3"      // Full cross-version (:::)
)
```

## Test Module

```scala
object tests extends ScalaTests with TestModule.Munit {
  def mvnDeps = Seq(mvn"org.scalameta::munit:1.0.0")
}
```

## SBT Compatibility

For projects using SBT directory layout (`src/main/scala`, `src/test/scala`):

```scala
object myapp extends SbtModule {
  def scalaVersion = "3.6.4"
}
```

## Code Formatting

```scala
object myapp extends ScalaModule with ScalafmtModule {
  def scalaVersion = "3.6.4"
}
// CLI: mill myapp.reformat
```

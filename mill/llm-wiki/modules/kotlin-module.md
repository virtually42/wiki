---
id: kotlin-module
title: KotlinModule
section: modules
source_files:
  - /p/gh/mill/libs/kotlinlib/src/mill/kotlinlib/KotlinModule.scala
source_commit: 41ce6c977c4
related:
  - modules/java-module.md
---

# KotlinModule

Extends `JavaModule` for Kotlin compilation.

## Import

```scala
import mill._, kotlinlib._
```

## Minimal Example

```scala
object myapp extends KotlinModule {
  def kotlinVersion = "2.1.0"
  def mvnDeps = Seq(
    mvn"org.jetbrains.kotlinx:kotlinx-coroutines-core:1.9.0"
  )
}
```

## Key Tasks

| Task | Type | Description |
|------|------|-------------|
| `kotlinVersion` | `T[String]` | Kotlin compiler version (required) |
| `kotlinLanguageVersion` | `T[String]` | Language level |
| `kotlinApiVersion` | `T[String]` | API level |
| `kotlincOptions` | `T[Seq[String]]` | Kotlin compiler flags |
| `allKotlinSourceFiles` | `T[Seq[PathRef]]` | `.kt` source files |

## Testing

```scala
object tests extends KotlinTests with TestModule.Junit5 {
  def mvnDeps = Seq(
    mvn"org.junit.jupiter:junit-jupiter:5.10.0"
  )
}
```

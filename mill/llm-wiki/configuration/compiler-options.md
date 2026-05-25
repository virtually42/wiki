---
id: compiler-options
title: Compiler Options
section: configuration
source_commit: 41ce6c977c4
related:
  - modules/java-module.md
  - modules/scala-module.md
  - modules/kotlin-module.md
---

# Compiler Options

How to configure compiler flags for each language.

## Java (javacOptions)

```scala
object myapp extends JavaModule {
  def javacOptions = Seq(
    "-source", "21",
    "-target", "21",
    "-Xlint:all",
    "-Werror"
  )
}
```

## Scala (scalacOptions)

### Scala 3

```scala
object myapp extends ScalaModule {
  def scalaVersion = "3.6.4"
  def scalacOptions = Seq(
    "-deprecation",
    "-unchecked",
    "-feature",
    "-Wunused:all",
    "-Xfatal-warnings",
    "-explain",                  // detailed error explanations
    "-new-syntax",               // enforce new Scala 3 syntax
    "-indent",                   // enforce indentation syntax
    "-source:future"             // future migration warnings
  )
}
```

### Scala 2

```scala
def scalacOptions = Seq(
  "-deprecation",
  "-unchecked",
  "-feature",
  "-Xlint",
  "-Ywarn-dead-code",
  "-Ywarn-unused",
  "-Xfatal-warnings"
)
```

## Scala Compiler Plugins

```scala
def scalacPluginMvnDeps = Seq(
  mvn"org.typelevel:::kind-projector:0.13.3",   // ::: for full version
  mvn"com.olegpy::better-monadic-for:0.3.1"     // :: for binary version
)
```

## Kotlin (kotlincOptions)

```scala
object myapp extends KotlinModule {
  def kotlinVersion = "2.1.0"
  def kotlincOptions = Seq(
    "-Werror",
    "-progressive"
  )
}
```

## Conditional Options

```scala
def scalacOptions = Task {
  val base = Seq("-deprecation", "-unchecked")
  if (scalaVersion().startsWith("3.")) base ++ Seq("-Wunused:all")
  else base ++ Seq("-Xlint")
}
```

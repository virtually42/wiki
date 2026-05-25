---
id: sources
title: Sources and Resources
section: configuration
source_commit: 41ce6c977c4
related:
  - modules/java-module.md
  - concepts/task-system.md
---

# Sources and Resources

How Mill discovers and manages source files and resources.

## Default Source Layout

```
myapp/
  src/              <- sources (Java/Scala/Kotlin files)
  resources/        <- resources (config files, etc.)
  tests/
    src/            <- test sources
    resources/      <- test resources
```

## Customizing Sources

```scala
object myapp extends ScalaModule {
  def scalaVersion = "3.6.4"

  // Override source directories
  def sources = Task.Sources("src", "src-extra")

  // Override resource directories
  def resources = Task.Sources("resources", "config")
}
```

## Generated Sources

```scala
def generatedSources = Task {
  val dest = Task.dest / "generated"
  os.makeDir.all(dest)
  os.write(dest / "Version.scala", s"""object Version { val v = "${publishVersion()}" }""")
  Seq(PathRef(dest))
}
```

Generated sources are compiled alongside regular sources.

## SBT Layout

For projects using Maven/SBT directory conventions:

```scala
object myapp extends SbtModule {
  def scalaVersion = "3.6.4"
  // Sources: src/main/scala, src/main/java
  // Resources: src/main/resources
  // Tests: src/test/scala, src/test/java
}
```

## Platform-Specific Sources

For cross-platform projects, platform-specific sources go in separate directories:

```
shared/src/           <- shared sources
jvm/src/              <- JVM-only sources
js/src/               <- JS-only sources
native/src/           <- Native-only sources
```

Configure via `sources` override in each platform module.

## PathRef and File Tracking

`Task.Sources` returns `Seq[PathRef]`. `PathRef` wraps a path with a
content hash for change detection. When file contents change, downstream
tasks are invalidated.

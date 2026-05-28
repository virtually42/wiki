---
id: dependencies
title: Dependencies
section: configuration
source_files:
  - /p/gh/mill/libs/javalib/src/mill/javalib/Dep.scala
  - /p/gh/mill/libs/javalib/src/mill/javalib/JavaModule.scala
source_commit: 41ce6c977c4
related:
  - modules/java-module.md
  - modules/scala-module.md
---

# Dependencies

How to declare and manage dependencies in Mill.

## Maven Dependencies

Use `mvnDeps` with the `mvn"..."` string interpolator:

```scala
def mvnDeps = Seq(
  mvn"org.apache.commons:commons-lang3:3.14.0"  // Java library
)
```

## Cross-Version Syntax

```scala
// Java dependency (no cross-versioning)
mvn"group:artifact:version"

// Scala binary version (:: — most common for Scala libs)
mvn"group::artifact:version"
// Resolves to: group:artifact_2.13:version or group:artifact_3:version

// Scala full version (::: — for compiler plugins)
mvn"group:::artifact:version"
// Resolves to: group:artifact_3.6.4:version

// Platform cross-version (for ScalaJS/Native)
mvn"group::artifact::version"
// Resolves to: group:artifact_sjs1_3:version
```

## Module Dependencies

```scala
object core extends ScalaModule { ... }

object app extends ScalaModule {
  // Compile + runtime dependency on core
  def moduleDeps = Seq(core)

  // Compile-only dependency (not on runtime classpath)
  def compileModuleDeps = Seq(macroLib)

  // Runtime-only dependency (not on compile classpath)
  def runModuleDeps = Seq(logging)
}
```

## Unmanaged Dependencies

For local JAR files not in a Maven repository:

```scala
def unmanagedClasspath = Task {
  Seq(PathRef(millSourcePath / "lib" / "custom.jar"))
}
```

## Exclusions

```scala
def mvnDeps = Seq(
  mvn"org.apache.spark::spark-core:3.5.0"
    .exclude("org.slf4j" -> "slf4j-log4j12")
    .exclude("log4j" -> "log4j")
)

// Exclude all transitive from an org
mvn"com.example::lib:1.0.0"
  .excludeOrg("org.unwanted")
```

## Force Version

```scala
mvn"com.fasterxml.jackson.core:jackson-databind:2.15.0"
  .forceVersion()
```

## Optional Dependencies

```scala
mvn"com.example::optional-lib:1.0.0"
  .optional(true)
```

## Dependency Resolution

Mill uses Coursier for dependency resolution. Configure repositories:

```scala
def repositoriesTask = Task.Anon {
  super.repositoriesTask() ++ Seq(
    coursier.MavenRepository("https://my.repo/maven")
  )
}
```

## Bill of Materials (BOM)

```scala
def bomDeps = Seq(
  mvn"com.google.cloud:libraries-bom:26.27.0"
)
// Then use deps without version:
def mvnDeps = Seq(
  mvn"com.google.cloud:google-cloud-storage"
)
```

## Viewing Dependencies

```bash
mill myapp.mvnDeps             # list declared deps
mill myapp.resolvedMvnDeps     # list resolved deps with versions
mill myapp.compileClasspath    # full classpath
```

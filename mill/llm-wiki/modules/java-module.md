---
id: java-module
title: JavaModule
section: modules
source_files:
  - libs/javalib/src/mill/javalib/JavaModule.scala
source_commit: 41ce6c977c4
related:
  - modules/scala-module.md
  - modules/test-module.md
  - configuration/dependencies.md
---

# JavaModule

Base module for JVM projects. All language-specific modules (Scala, Kotlin)
extend this.

## Import

```scala
import mill._, javalib._
```

## Minimal Example

```scala
object myapp extends JavaModule {
  def mvnDeps = Seq(
    mvn"org.apache.commons:commons-lang3:3.14.0"
  )
}
```

## Key Tasks

### Sources & Resources

| Task | Type | Default | Description |
|------|------|---------|-------------|
| `sources` | `T[Seq[PathRef]]` | `src/` | Java source directories |
| `resources` | `T[Seq[PathRef]]` | `resources/` | Resource directories |
| `generatedSources` | `T[Seq[PathRef]]` | `[]` | Generated source directories |
| `allSources` | `T[Seq[PathRef]]` | sources + generated | All source directories |

### Compilation

| Task | Type | Description |
|------|------|-------------|
| `compile` | `T[CompilationResult]` | Compile sources via Zinc |
| `javacOptions` | `T[Seq[String]]` | Javac compiler flags |
| `compileClasspath` | `T[Seq[PathRef]]` | Classpath for compilation |

### Dependencies

| Task | Type | Description |
|------|------|-------------|
| `mvnDeps` | `T[Seq[Dep]]` | Maven/Ivy dependencies |
| `moduleDeps` | `Seq[JavaModule]` | Module dependencies (compile + runtime) |
| `compileModuleDeps` | `Seq[JavaModule]` | Compile-only module deps |
| `runModuleDeps` | `Seq[JavaModule]` | Runtime-only module deps |
| `unmanagedClasspath` | `T[Seq[PathRef]]` | Manual JAR file paths |

### Execution

| Task | Type | Description |
|------|------|-------------|
| `run(args: String*)` | `Command` | Run main class |
| `runMain(mainClass: String, args: String*)` | `Command` | Run specific main class |
| `mainClass` | `T[Option[String]]` | Main class override |
| `forkArgs` | `T[Seq[String]]` | JVM arguments for forked execution |
| `forkEnv` | `T[Map[String, String]]` | Environment for forked execution |
| `runClasspath` | `T[Seq[PathRef]]` | Runtime classpath |

### Packaging

| Task | Type | Description |
|------|------|-------------|
| `jar` | `T[PathRef]` | Create JAR |
| `assembly` | `T[PathRef]` | Create fat/uber JAR |
| `manifest` | `T[JarManifest]` | JAR manifest |
| `assemblyRules` | `Seq[Assembly.Rule]` | Merge/exclude rules for assembly |

### JDK

| Task | Type | Description |
|------|------|-------------|
| `javaHome` | `T[Option[PathRef]]` | Custom JDK path |
| `jvmWorker` | `ModuleRef[JvmWorkerModule]` | JVM worker reference |

## Inner Test Module

```scala
object myapp extends JavaModule {
  object tests extends JavaTests with TestModule.Junit5 {
    def mvnDeps = Seq(
      mvn"org.junit.jupiter:junit-jupiter:5.10.0"
    )
  }
}
```

See [test-module](test-module.md) for test framework options.

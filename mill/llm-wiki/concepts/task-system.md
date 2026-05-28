---
id: task-system
title: Task System
section: concepts
source_files:
  - /p/gh/mill/core/api/src/mill/api/Task.scala
  - /p/gh/mill/core/api/java11/src/mill/api/TaskCtx.scala
source_commit: 41ce6c977c4
related:
  - concepts/evaluation.md
  - concepts/caching.md
---

# Task System

Tasks are the computation units in Mill. Each task is a node in a DAG
with typed inputs and a single typed output.

## Task Types

### Task (cached target)

The most common type. Result is cached on disk as JSON. Re-evaluated only
when inputs change.

```scala
def lineCount: T[Int] = Task {
  os.walk(sources().path).filter(_.ext == "scala").length
}
```

- Cached in `out/<module>/<taskName>.json`
- Scratch directory at `out/<module>/<taskName>.dest/`
- Inputs are other tasks referenced via `()` call syntax

### Task.Source / Task.Sources

Tracks file system paths. Invalidates when file content hash changes.

```scala
def sources = Task.Sources("src")           // Seq[PathRef]
def config = Task.Source("config.json")     // PathRef
```

### Task.Input

Re-evaluated every run. No caching. Use for external state.

```scala
def currentTime = Task.Input { java.time.Instant.now() }
def gitHash = Task.Input { os.proc("git", "rev-parse", "HEAD").call().out.trim() }
```

### Task.Command

CLI-callable. Not cached between runs. Can accept arguments.

```scala
def deploy(env: String) = Task.Command {
  println(s"Deploying to $env")
  os.proc("deploy.sh", env).call()
}
// CLI: mill myapp.deploy --env production
```

**Exclusive commands** run serially after all parallel tasks:
```scala
def migrate() = Task.Command(exclusive = true) { ... }
```

### Task.Worker

Long-lived in-memory state. Persists for daemon lifetime. Must be
`AutoCloseable`.

```scala
def compiler = Task.Worker {
  new ExpensiveCompiler(scalacOptions())
}
// Invalidated when inputs change, but not between runs
```

### Task.Anon

Anonymous helper. No CLI name, no caching. Internal use only.

```scala
def helper = Task.Anon {
  someComputation()
}
```

## Task Context (TaskCtx)

Available inside `Task { ... }` blocks via implicit:

```scala
def myTask = Task {
  val dest = Task.dest          // os.Path — scratch directory
  val log = Task.log            // Logger
  val env = Task.env            // Map[String, String]
  val workspace = Task.workspace // os.Path — project root
  val jobs = Task.jobs          // Int — parallel job count
  // ...
}
```

Key context members:

| Member | Type | Description |
|--------|------|-------------|
| `Task.dest` | `os.Path` | Unique scratch directory (cleared each run unless persistent) |
| `Task.log` | `Logger` | Task-specific logger |
| `Task.env` | `Map[String, String]` | Environment variables |
| `Task.workspace` | `os.Path` | Project root directory |
| `Task.jobs` | `Int` | Number of parallel jobs |
| `Task.fork` | `Fork` | Async futures API |

## Task Dependencies

Tasks depend on each other by calling `.apply()` (parentheses):

```scala
def compiled = Task { compile() }        // depends on compile
def jarFile = Task {
  val c = compiled()                      // depends on compiled
  val s = sources()                       // depends on sources
  createJar(c, s)
}
```

Mill builds the DAG from these references automatically. Circular
dependencies cause a compile-time or runtime error.

## Persistent Tasks

By default, `Task.dest` is cleared before each run. For tasks that need
to keep state across runs:

```scala
def incrementalCompile = Task(persistent = true) {
  // Task.dest preserved between runs
  zinc.compile(Task.dest, sources())
}
```

---
id: workers
title: Workers
section: patterns
source_commit: 41ce6c977c4
related:
  - concepts/task-system.md
---

# Workers

Long-lived in-memory objects that persist across task runs.

## When to Use

- Expensive initialization (classloaders, compilers, connection pools)
- State that benefits from caching across runs
- External process management

## Basic Worker

```scala
def myCompiler = Task.Worker {
  // This runs once, result is cached in memory for daemon lifetime
  new ExpensiveCompiler(scalacOptions())
}

def compile = Task {
  myCompiler().compile(sources())
}
```

## Invalidation

Workers are re-created when their inputs change:

```scala
def myWorker = Task.Worker {
  // If scalacOptions() changes, worker is discarded and re-created
  new Compiler(scalacOptions())
}
```

## AutoCloseable

Workers should implement `AutoCloseable` for cleanup:

```scala
def myWorker = Task.Worker {
  new AutoCloseable {
    val pool = new ConnectionPool()
    def close(): Unit = pool.shutdown()
  }
}
```

## Worker Lifetime

- Created on first access
- Persists for the daemon's lifetime (or until invalidated)
- Automatically closed when the daemon shuts down
- Not serialized to disk — lost on daemon restart

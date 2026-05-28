---
id: kyo-effect-scope
title: "Scope — Resource Lifecycle"
category: effect
layer: core
tags: [resources, lifecycle, acquire-release, finalization, closeable]
source_files:
  - /p/gh/kyo/kyo-core/shared/src/main/scala/kyo/Scope.scala
source_commit: 9bab8d00
api_surface: [Scope.acquire, Scope.acquireRelease, Scope.ensure, Scope.run]
related: [kyo-effect-async, kyo-concept-resource-management]
see_also: [kyo-pattern-fiber-coordination]
platforms: [jvm, js, native]
effect_type: ContextEffect
suspend_methods: [acquire, acquireRelease, ensure]
handle_methods: [run]
pending_type: "Scope"
---

## What It Does

Manages resource lifecycles with guaranteed cleanup. Resources acquired within a scope are released when the scope closes — even on error or fiber interruption. Similar to ZIO's `Scope`.

## Key APIs

### Suspending

| Method | Signature | Purpose |
|--------|-----------|---------|
| `Scope.acquire(closeable)` | `R < (Scope & Async)` | Acquire a `Closeable`, auto-close on scope end |
| `Scope.acquireRelease(acquire)(release)` | `R < (Scope & Async)` | Custom acquire/release |
| `Scope.ensure(finalizer)` | `Unit < Scope` | Register a finalizer |

### Handling

| Method | Signature | Purpose |
|--------|-----------|---------|
| `Scope.run(comp)` | `A < Async` | Run computation, close all resources after |

## Common Patterns

### Java Closeable

```scala
import java.io.Closeable

class Database extends Closeable:
    def query: String < Sync = Sync.defer("result")
    def close() = println("closed")

val result: String < Async =
    Scope.run {
        Scope.acquire(new Database).map(_.query)
    }
// Database.close() called automatically
```

### Custom acquire/release

```scala
val managed: Connection < (Scope & Async) =
    Scope.acquireRelease(openConnection())(conn => conn.close())
```

### Finalizer without acquire

```scala
def withTempFile[A](f: File => A < Async): A < (Scope & Async) =
    val file = createTempFile()
    Scope.ensure(file.delete()).andThen(f(file))
```

## Gotchas

- `Scope.acquire` requires `Async` (resources are tied to fiber lifecycle)
- Resources released in reverse acquisition order (LIFO)
- Don't let acquired resources escape the scope (use-after-free)
- `Async.run` (fork) requires `Scope` — child fibers are scoped resources
- Convention: `init` methods create scoped resources, `initUnscoped` creates unmanaged ones

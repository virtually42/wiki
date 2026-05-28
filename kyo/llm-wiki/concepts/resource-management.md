---
id: kyo-concept-resource-management
title: "Resource Management"
category: concept
layer: core
tags: [scope, resources, acquire-release, lifecycle, finalization]
source_files:
  - /p/gh/kyo/kyo-core/shared/src/main/scala/kyo/Scope.scala
source_commit: 9bab8d00
api_surface: [Scope, Scope.init, Scope.run, Scope.ensure]
related: [kyo-effect-scope, kyo-effect-async]
see_also: [kyo-pattern-fiber-coordination]
platforms: [jvm, js, native]
---

## Core Idea

`Scope` manages resource lifecycles with guaranteed cleanup. Resources acquired within a scope are released when the scope closes, even on failure or fiber interruption.

## The Pattern

```scala
import kyo.*

// Acquire a resource that needs cleanup
val managed: Connection < (Scope & Sync) =
    Scope.acquireRelease(openConnection())(_.close())

// Use it within a scope — cleanup is automatic
val result: String < Sync =
    Scope.run {
        managed.map(_.query("SELECT 1"))
    }
```

## init vs initUnscoped

Convention in Kyo modules:

| Method | Behavior |
|--------|----------|
| `init` / `initWith` | Creates resource managed by enclosing `Scope` (default) |
| `initUnscoped` | Creates unmanaged resource (caller responsible for cleanup) |

**Prefer `init`** unless you have a specific reason to manage lifecycle manually.

## Scope + Async

Scope integrates with fiber lifecycle. When a fiber is interrupted, its scope closes and all acquired resources are released:

```scala
val server: Unit < (Async & Scope) =
    direct {
        val conn = Scope.acquireRelease(connect())(_.close()).now
        val fiber = Async.run(handleRequests(conn)).now
        // If this fiber is interrupted, conn.close() runs automatically
        fiber.get.now
    }
```

## ensure (Finalizers)

For simple cleanup without acquire/release:

```scala
val withCleanup: Unit < Scope =
    Scope.ensure(cleanup())
    // cleanup() runs when scope closes
```

## Gotchas

- `Scope.run` handles the Scope effect — resources are released when the block completes
- Resources are released in reverse acquisition order (LIFO)
- Don't let resources escape their scope (e.g., returning an acquired connection from `Scope.run`)
- `Scope` is required by `Async.run` (fibers need a scope for resource tracking)

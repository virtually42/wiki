---
id: kyo-effect-async
title: "Async — Green Threads & Fibers"
category: effect
layer: core
tags: [concurrency, fibers, fork, join, parallelism, async]
source_files:
  - /p/gh/kyo/kyo-core/shared/src/main/scala/kyo/Async.scala
  - /p/gh/kyo/kyo-core/shared/src/main/scala/kyo/Fiber.scala
source_commit: 9bab8d00
api_surface: [Async.run, Async.parallel, Async.race, Async.sleep, Async.timeout, Async.never, Fiber.get, Fiber.map]
related: [kyo-effect-sync, kyo-effect-scope]
see_also: [kyo-pattern-fiber-coordination, kyo-pattern-concurrency]
platforms: [jvm, js, native]
effect_type: ArrowEffect
suspend_methods: [run, parallel, race, sleep, timeout]
handle_methods: [KyoApp.run]
pending_type: "Async"
---

## What It Does

Provides green thread (fiber) concurrency. `Async` implies `Sync` — any async computation can also perform side effects. Fibers are lightweight, scheduled on Kyo's adaptive work-stealing scheduler.

## Key APIs

### Creating Fibers

| Method | Signature | Purpose |
|--------|-----------|---------|
| `Async.run(comp)` | `Fiber[A] < (Async & Scope)` | Fork a fiber (requires Scope) |
| `Async.parallel(comps)` | `Seq[A] < Async` | Run all in parallel, collect results |
| `Async.race(comps)` | `A < Async` | First to complete wins, others interrupted |

### Fiber Operations

| Method | Purpose |
|--------|---------|
| `fiber.get` | Await fiber result (suspends Async) |
| `fiber.map(f)` | Transform result when ready |
| `fiber.interrupt` | Cancel the fiber |

### Timing

| Method | Purpose |
|--------|---------|
| `Async.sleep(duration)` | Suspend for duration |
| `Async.timeout(duration)(comp)` | Fail if comp exceeds duration |
| `Async.never` | Suspend forever (useful for servers) |

## Composition

```scala
import kyo.*

val result: (Int, String) < Async =
    direct {
        // Fork two fibers
        val f1 = Async.run(computeInt()).now
        val f2 = Async.run(computeString()).now
        // Join both
        (f1.get.now, f2.get.now)
    }
```

## Common Patterns

### Parallel collection processing

```scala
val results: Seq[Result] < Async =
    Async.parallel(items.map(process))
```

### Timeout with fallback

```scala
val withTimeout: Int < Async =
    Async.timeout(5.seconds)(slowComputation)
        .handle(Abort.recover[Timeout](_ => defaultValue))
```

### Background worker

```scala
val server: Unit < (Async & Scope) =
    direct {
        val fiber = Async.run(processRequests()).now
        Async.never.now  // keep alive
    }
```

## Gotchas

- `Async.run` requires `Scope` — fibers are resource-managed (interrupted when scope closes)
- `Async` implies `Sync` — you don't need both in a type signature
- Fibers inherit `Local` values from their parent
- Never block a thread — use `Async.sleep` not `Thread.sleep`
- Use `KyoApp` to run the top-level Async computation

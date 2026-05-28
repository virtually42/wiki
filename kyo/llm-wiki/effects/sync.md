---
id: kyo-effect-sync
title: "Sync — Side Effect Suspension"
category: effect
layer: core
tags: [side-effects, suspension, io, unsafe]
source_files:
  - /p/gh/kyo/kyo-core/shared/src/main/scala/kyo/Sync.scala
source_commit: 9bab8d00
api_surface: [Sync.defer, Sync.Unsafe.run, KyoApp]
related: [kyo-effect-async, kyo-concept-pending-type]
see_also: []
platforms: [jvm, js, native]
effect_type: ArrowEffect
suspend_methods: [defer]
handle_methods: [Unsafe.run]
pending_type: "Sync"
---

## What It Does

Suspends a side-effecting computation. Unlike traditional effect systems, Kyo's base type `<` does NOT assume side effects — `Sync` must be explicitly introduced.

## Key APIs

### Suspending

| Method | Signature | Purpose |
|--------|-----------|---------|
| `Sync.defer(expr)` | `A < Sync` | Suspend a side-effecting expression |

### Handling

Users should NOT handle Sync directly. Use `KyoApp` instead:

```scala
object MyApp extends KyoApp:
    run {
        Sync.defer(println("hello"))
    }
```

For interop (rare), requires explicit unsafe acknowledgment:

```scala
import AllowUnsafe.embrace.danger
val result: Int < Abort[Nothing] = Sync.Unsafe.run(Sync.defer(42))
```

## Common Patterns

```scala
// Wrap any side-effecting code
val readFile: String < Sync =
    Sync.defer(scala.io.Source.fromFile("data.txt").mkString)

// Combine with other effects
val result: String < (Sync & Abort[Exception]) =
    for
        content <- Sync.defer(readFile)
        parsed  <- Abort.catching(parseJson(content))
    yield parsed
```

## Gotchas

- **Never handle Sync directly** — it breaks referential transparency. Use `KyoApp`.
- `Sync` does NOT include async/fiber capabilities — use `Async` for that.
- `Async` implies `Sync` (every async computation can also perform side effects).
- A pure computation (`Int < Any`) has no `Sync` — it's truly pure.

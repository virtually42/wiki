---
id: kyo-pattern-unsafe-boundary
title: "Unsafe Boundary Pattern"
category: pattern
layer: core
tags: [unsafe, two-tier, allow-unsafe, boundary, interop]
source_files: []
source_commit: 9bab8d00
api_surface: [AllowUnsafe.embrace.danger, Sync.Unsafe.run, Channel.Unsafe]
related: [kyo-effect-sync, kyo-effect-async]
see_also: []
platforms: [jvm, js, native]
when_to_use: "Interop with non-Kyo code, performance-critical inner loops, Java library integration"
when_not_to_use: "Normal application code (use KyoApp instead)"
---

## Problem

How to bridge between Kyo's effect system and unsafe/imperative code.

## Solution

### Two-Tier API Pattern

Every Kyo type has a safe API (effects tracked) and an Unsafe API (direct access):

```scala
// Safe API — effects tracked
val value: Int < Sync = channel.take

// Unsafe API — no effect tracking, requires AllowUnsafe
import AllowUnsafe.embrace.danger
val value: Int = channel.Unsafe.poll().getOrThrow
```

### AllowUnsafe Gate

```scala
import AllowUnsafe.embrace.danger // explicit import required

// Now unsafe operations are available
val result: Int = Sync.Unsafe.run(computation)
```

### Common Boundaries

**Java interop (callbacks):**
```scala
javaLib.onComplete { result =>
    import AllowUnsafe.embrace.danger
    channel.Unsafe.offer(result)
}
```

**Performance-critical:**
```scala
def hotPath(data: Array[Byte])(using AllowUnsafe): Unit =
    // Direct access without effect overhead
    queue.Unsafe.offer(data)
```

## Trade-offs

- Unsafe operations break referential transparency
- `AllowUnsafe` is explicit — makes unsafe boundaries visible in signatures
- Prefer `KyoApp` for top-level running, Unsafe only for interop
- Convention: `Unsafe` companion objects mirror the safe API

## Related

- Use `Sync.Unsafe.defer` to bridge back from unsafe → safe

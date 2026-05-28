---
id: kyo-effect-retry
title: "Retry — Automatic Retry with Backoff"
category: effect
layer: core
tags: [retry, backoff, resilience, fault-tolerance]
source_files:
  - /p/gh/kyo/kyo-core/shared/src/main/scala/kyo/Retry.scala
source_commit: 9bab8d00
api_surface: [Retry, Retry.Policy, Schedule]
related: [kyo-effect-async, kyo-effect-abort]
see_also: [kyo-recipe-concurrent-service]
platforms: [jvm, js, native]
effect_type: ArrowEffect
suspend_methods: []
handle_methods: [Retry]
pending_type: "Async"
---

## What It Does

Retries a failing computation with configurable backoff and limits. Works with `Abort` — retries on failure, gives up after policy exhausted.

## Key APIs

| Method | Purpose |
|--------|---------|
| `Retry[E](policy)(comp)` | Retry computation on `Abort[E]` failures |
| `Retry[E](comp)` | Retry with default policy |

### Policy Configuration

```scala
Retry.Policy(
    limit = 3,                    // max attempts
    backoff = Schedule.exponential(100.millis, 2.0)  // delay between retries
)
```

## Common Patterns

### Simple retry

```scala
val result: String < (Async & Abort[IOError]) =
    Retry[IOError](Retry.Policy(limit = 3)) {
        httpGet("https://api.example.com/data")
    }
```

### With exponential backoff

```scala
val policy = Retry.Policy(
    limit = 5,
    backoff = Schedule.exponential(100.millis, 2.0)
    // 100ms, 200ms, 400ms, 800ms, 1600ms
)

val result: Response < (Async & Abort[NetworkError]) =
    Retry[NetworkError](policy)(callExternalService())
```

## Gotchas

- Retry requires `Async` (for sleep between attempts)
- Only retries `Abort[E]` failures — `Panic` exceptions are NOT retried
- After exhausting retries, the last failure propagates
- Default policy exists but prefer explicit policies for production code

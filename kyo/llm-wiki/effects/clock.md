---
id: kyo-effect-clock
title: "Clock — Time Operations"
category: effect
layer: core
tags: [time, clock, instant, testing, time-control]
source_files:
  - /p/gh/kyo/kyo-core/shared/src/main/scala/kyo/Clock.scala
source_commit: 9bab8d00
api_surface: [Clock.now, Clock.nowMonotonic, Clock.sleep, Clock.repeatAtInterval, Clock.withTimeControl, Clock.withTimeShift]
related: [kyo-data-duration, kyo-effect-async]
see_also: [kyo-pattern-testing]
platforms: [jvm, js, native]
effect_type: ContextEffect
suspend_methods: [now, nowMonotonic, sleep, repeatAtInterval]
handle_methods: [withTimeControl, withTimeShift]
pending_type: "Sync"
---

## What It Does

Time operations with testability built in. Provides current time, sleep, scheduling, and time manipulation for testing.

## Key APIs

### Time Queries

| Method | Purpose |
|--------|---------|
| `Clock.now` | Current wall-clock time (Instant) |
| `Clock.nowMonotonic` | Monotonic time (for measuring elapsed) |

### Scheduling

| Method | Purpose |
|--------|---------|
| `Clock.sleep(duration)` | Suspend for duration |
| `Clock.repeatAtInterval(interval)(comp)` | Run repeatedly at fixed interval |
| `Clock.repeatWithDelay(delay)(comp)` | Run repeatedly with delay between runs |

### Testing

| Method | Purpose |
|--------|---------|
| `Clock.withTimeControl(comp)` | Full time control for tests |
| `Clock.withTimeShift(shift)(comp)` | Offset clock by duration |

## Common Patterns

### Periodic task

```scala
val heartbeat: Unit < Async =
    Clock.repeatAtInterval(30.seconds) {
        sendHeartbeat()
    }
```

### Measuring elapsed time

```scala
val timed: (Duration, A) < Sync =
    direct {
        val start = Clock.nowMonotonic.now
        val result = computation.now
        val elapsed = Clock.nowMonotonic.now - start
        (elapsed, result)
    }
```

### Testing with controlled time

```scala
val test: Unit < Async =
    Clock.withTimeControl { control =>
        direct {
            val fiber = Async.run(Clock.sleep(1.hour).andThen(action())).now
            control.advance(1.hour).now  // instantly advance
            fiber.get.now                // action completes immediately
        }
    }
```

## Gotchas

- `Clock.sleep` requires `Async` (fiber suspension, not thread blocking)
- Use `nowMonotonic` for elapsed time measurement (not affected by clock adjustments)
- `withTimeControl` replaces the clock entirely — useful for deterministic tests
- `Clock` is handled by `KyoApp` automatically

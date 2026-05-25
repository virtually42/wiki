---
id: kyo-effect-channel
title: "Channel — Bounded Async Communication"
category: effect
layer: core
tags: [concurrency, channel, bounded, backpressure, mpmc]
source_files:
  - kyo-core/shared/src/main/scala/kyo/Channel.scala
source_commit: 9bab8d00
api_surface: [Channel.init, Channel.put, Channel.take, Channel.offer, Channel.poll, Channel.stream, Channel.close]
related: [kyo-effect-queue, kyo-effect-hub, kyo-effect-async]
see_also: [kyo-pattern-concurrency]
platforms: [jvm, js, native]
effect_type: ArrowEffect
suspend_methods: [put, take]
handle_methods: []
pending_type: "Async"
---

## What It Does

Bounded multi-producer multi-consumer (MPMC) channel with backpressure. `put` suspends when full, `take` suspends when empty.

## Key APIs

### Creation

| Method | Purpose |
|--------|---------|
| `Channel.init[A](capacity)` | Create bounded channel |
| `Channel.init[A](capacity, Access.Spsc)` | Single-producer single-consumer (faster) |

### Async Operations (suspend when blocked)

| Method | Purpose |
|--------|---------|
| `channel.put(value)` | Send value (suspends if full) |
| `channel.take` | Receive value (suspends if empty) |
| `channel.putBatch(chunk)` | Send multiple values |
| `channel.takeExactly(n)` | Receive exactly n values |

### Sync Operations (never suspend)

| Method | Purpose |
|--------|---------|
| `channel.offer(value)` | Try send, return Boolean |
| `channel.poll` | Try receive, return Maybe[A] |

### Lifecycle

| Method | Purpose |
|--------|---------|
| `channel.close` | Close channel (pending takes get Absent) |
| `channel.stream` | Convert to Stream for consumption |
| `channel.size` | Current element count |

## Common Patterns

### Producer-consumer

```scala
val pipeline: Unit < (Async & Scope) =
    direct {
        val chan = Channel.init[Int](capacity = 64).now
        // Producer
        val producer = Async.run {
            Stream.range(1, 1000).foreach(chan.put).andThen(chan.close)
        }.now
        // Consumer
        chan.stream.foreach(process).now
    }
```

### Work distribution

```scala
val chan = Channel.init[Task](capacity = 16)
// Multiple consumers
val workers = Async.parallel(
    (1 to 4).map(_ => chan.stream.foreach(handleTask))
)
```

## Gotchas

- `Channel.init` requires `Scope` (resource-managed)
- `put` suspends the fiber when channel is full — never blocks a thread
- `Access` variants: `Mpmc` (default), `Mpsc`, `Spmc`, `Spsc` — use narrower for perf
- `close` causes pending `take` operations to receive `Absent`
- Channel is NOT an effect — it's a concurrent data structure used within `Async`

---
id: kyo-effect-hub
title: "Hub — Broadcast with Backpressure"
category: effect
layer: core
tags: [concurrency, broadcast, pub-sub, fan-out]
source_files:
  - /p/gh/kyo/kyo-core/shared/src/main/scala/kyo/Hub.scala
source_commit: 9bab8d00
api_surface: [Hub.init, Hub.put, Hub.offer, Hub.subscribe, Hub.close]
related: [kyo-effect-channel, kyo-effect-queue]
see_also: [kyo-pattern-concurrency]
platforms: [jvm, js, native]
effect_type: ArrowEffect
suspend_methods: [put]
handle_methods: []
pending_type: "Async"
---

## What It Does

Multi-producer multi-consumer broadcast. Every subscriber receives every message. Publishers experience backpressure from the slowest subscriber.

## Key APIs

| Method | Purpose |
|--------|---------|
| `Hub.init[A](capacity)` | Create hub with buffer capacity |
| `hub.put(value)` | Publish (suspends if any subscriber is full) |
| `hub.offer(value)` | Try publish (non-blocking) |
| `hub.putBatch(chunk)` | Publish multiple values |
| `hub.subscribe` | Create a new subscriber (returns Channel-like) |
| `hub.close` | Close hub and all subscribers |

## Common Patterns

### Event broadcasting

```scala
val system: Unit < (Async & Scope) =
    direct {
        val events = Hub.init[Event](capacity = 32).now

        // Multiple subscribers
        val logger = events.subscribe.now
        val metrics = events.subscribe.now

        // Process each stream independently
        Async.run(logger.stream.foreach(logEvent)).now
        Async.run(metrics.stream.foreach(recordMetric)).now

        // Publish events
        events.put(Event("user.login")).now
    }
```

## When to Use

| Primitive | Pattern | Use when |
|-----------|---------|----------|
| Channel | Point-to-point | One consumer per message |
| Hub | Broadcast | All consumers get every message |
| Queue | Non-blocking buffer | Polling, no backpressure needed |

## Gotchas

- Backpressure comes from the SLOWEST subscriber — one slow consumer blocks the publisher
- `subscribe` creates a new Channel for that subscriber
- `Hub.init` requires `Scope`
- Closing the hub closes all subscriber channels

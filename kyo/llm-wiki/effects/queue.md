---
id: kyo-effect-queue
title: "Queue — Concurrent FIFO"
category: effect
layer: core
tags: [concurrency, queue, non-blocking, fifo]
source_files:
  - /p/gh/kyo/kyo-core/shared/src/main/scala/kyo/Queue.scala
source_commit: 9bab8d00
api_surface: [Queue.init, Queue.offer, Queue.poll, Queue.size, Queue.close]
related: [kyo-effect-channel, kyo-effect-hub]
see_also: [kyo-pattern-concurrency]
platforms: [jvm, js, native]
effect_type: ArrowEffect
suspend_methods: []
handle_methods: []
pending_type: "Sync"
---

## What It Does

Non-blocking bounded FIFO queue. Unlike Channel, Queue never suspends — `offer` returns false when full, `poll` returns `Maybe.empty` when empty.

## Key APIs

| Method | Purpose |
|--------|---------|
| `Queue.init[A](capacity)` | Create bounded queue |
| `queue.offer(value)` | Try enqueue, returns Boolean |
| `queue.poll` | Try dequeue, returns `Maybe[A]` |
| `queue.peek` | Look at front without removing |
| `queue.size` | Current element count |
| `queue.close` | Close the queue |

## When to Use Queue vs Channel

| | Queue | Channel |
|---|---|---|
| Blocking behavior | Never blocks | Suspends fiber |
| Backpressure | Manual (check `offer` result) | Automatic |
| Effect required | `Sync` | `Async` |
| Use case | Fire-and-forget, polling | Producer-consumer with flow control |

## Common Patterns

### Event buffer

```scala
val eventQueue: Queue[Event] < Scope =
    Queue.init[Event](capacity = 1024)

// Producer: drop if full
def emit(event: Event): Unit < Sync =
    eventQueue.map(_.offer(event)).unit

// Consumer: process available
def drain(): Chunk[Event] < Sync =
    eventQueue.map { q =>
        Loop(Chunk.empty[Event]) { acc =>
            q.poll.map {
                case Maybe.Present(e) => Loop.continue(acc.append(e))
                case Maybe.Absent     => Loop.done(acc)
            }
        }
    }
```

## Gotchas

- Queue is non-blocking — use Channel if you need backpressure
- `Queue.init` requires `Scope` (resource-managed)
- Access variants available (Mpmc, Spsc, etc.) for performance
- Only introduces `Sync`, not `Async`

---
id: kyo-pattern-concurrency
title: "Concurrency Primitive Selection"
category: pattern
layer: core
tags: [concurrency, channel, queue, hub, gate, latch, selection-guide]
source_files: []
source_commit: 9bab8d00
api_surface: [Channel, Queue, Hub, Gate, Latch, Exchange, Atomic]
related: [kyo-effect-channel, kyo-effect-queue, kyo-effect-hub, kyo-effect-async]
see_also: [kyo-pattern-fiber-coordination]
platforms: [jvm, js, native]
when_to_use: "Any concurrent data sharing or coordination between fibers"
when_not_to_use: "Single-fiber state (use Var); sequential code"
---

## Problem

Which concurrency primitive for which scenario?

## Solution

### Selection Guide

| I need... | Use | Why |
|-----------|-----|-----|
| Send data between fibers with backpressure | **Channel** | Suspends when full/empty |
| Buffer events, no blocking | **Queue** | offer/poll never suspend |
| Broadcast to all consumers | **Hub** | Every subscriber gets every message |
| Wait for N signals | **Latch** | Countdown coordination |
| Synchronize N fibers at a barrier | **Gate** | CyclicBarrier-like |
| Exchange data between two fibers | **Exchange** | Two-way rendezvous |
| Shared mutable counter/flag | **Atomic** | Lock-free CAS |
| Shared mutable accumulator | **Adder** | Lock-free addition |

### Channel Access Patterns

| Pattern | When |
|---------|------|
| `Access.Mpmc` (default) | Multiple producers, multiple consumers |
| `Access.Mpsc` | Multiple producers, single consumer |
| `Access.Spmc` | Single producer, multiple consumers |
| `Access.Spsc` | Single producer, single consumer (fastest) |

### Common Architectures

**Fan-out (work distribution):**
```scala
val tasks = Channel.init[Task](64)
val workers = (1 to 4).map(_ => Async.run(tasks.stream.foreach(process)))
```

**Fan-in (result collection):**
```scala
val results = Channel.init[Result](64)
// Multiple producers write to same channel
// Single consumer drains
```

**Broadcast (events):**
```scala
val events = Hub.init[Event](32)
val logger = events.subscribe  // gets all events
val metrics = events.subscribe // gets all events too
```

## Trade-offs

| Primitive | Backpressure | Blocking | Overhead |
|-----------|-------------|----------|----------|
| Channel | Yes | Fiber-suspend | Medium |
| Queue | No (drop/fail) | Never | Low |
| Hub | Yes (slowest sub) | Fiber-suspend | High |
| Atomic | N/A | Never (CAS) | Minimal |

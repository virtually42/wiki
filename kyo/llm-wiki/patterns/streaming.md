---
id: kyo-pattern-streaming
title: "Streaming Patterns"
category: pattern
layer: core
tags: [streaming, stream, emit, poll, chunked, backpressure]
source_files: []
source_commit: 9bab8d00
api_surface: [Stream, Emit, Poll, Channel.stream]
related: [kyo-effect-stream, kyo-effect-emit, kyo-effect-channel]
see_also: []
platforms: [jvm, js, native]
when_to_use: "Processing sequences of data lazily or with backpressure"
when_not_to_use: "Small fixed collections (use Chunk directly)"
---

## Problem

Which streaming abstraction for which scenario?

## Solution

### Selection Guide

| Abstraction | Model | Use when |
|-------------|-------|----------|
| **Stream** | High-level, composable | Most streaming use cases |
| **Emit** | Push-based, low-level | Producing values during computation |
| **Poll** | Pull-based, low-level | Consumer-driven backpressure |
| **Channel.stream** | Backpressured bridge | Connecting producers and consumers |

### Stream Pipeline (most common)

```scala
val result: Chunk[String] < Sync =
    Stream.range(1, 1000)
        .filter(_ % 2 == 0)
        .map(i => Sync.defer(transform(i)))
        .take(10)
        .run
```

### Stream from Channel (backpressured)

```scala
val pipeline: Unit < (Async & Scope) =
    direct {
        val input = Channel.init[Raw](64).now
        // Producer fills channel
        val producer = Async.run(produceData(input)).now
        // Consumer processes as stream
        input.stream.map(process).foreach(save).now
    }
```

### Emit for Side-Channel Output

```scala
val (logs, result): (Chunk[LogEntry], Output) < Sync =
    Emit.run {
        for
            _ <- Emit.value(LogEntry("starting"))
            r <- compute()
            _ <- Emit.value(LogEntry("done"))
        yield r
    }
```

### Chunked Processing for Performance

```scala
// mapChunk processes entire chunks — faster than element-by-element
Stream.from(data)
    .mapChunk(chunk => chunk.map(transform))
    .run
```

## Trade-offs

| | Stream | Emit | Channel |
|---|---|---|---|
| Composability | Excellent | Limited | Via .stream |
| Backpressure | Automatic (chunked) | None | Explicit (bounded) |
| Memory | Lazy (process in chunks) | Collect all (Emit.run) | Bounded buffer |
| Complexity | Low | Low | Medium (async setup) |

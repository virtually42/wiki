---
id: kyo-effect-stream
title: "Stream — Composable Data Processing"
category: effect
layer: prelude
tags: [streaming, data-processing, chunked, backpressure, lazy]
source_files:
  - /p/gh/kyo/kyo-prelude/shared/src/main/scala/kyo/Stream.scala
source_commit: 9bab8d00
api_surface: [Stream.init, Stream.range, Stream.from, Stream.run, Stream.runSeq, Stream.foreach, Stream.fold, Stream.map, Stream.filter, Stream.flatMap, Stream.take, Stream.drop, Stream.concat]
related: [kyo-effect-emit, kyo-effect-channel]
see_also: [kyo-pattern-streaming]
platforms: [jvm, js, native]
effect_type: ArrowEffect
suspend_methods: [init, range, from]
handle_methods: [run, runSeq, foreach, fold]
pending_type: "Stream[V, S]"
---

## What It Does

High-level composable streaming with chunked processing and automatic flow control. Preferred over raw `Emit` for most streaming use cases.

## Key APIs

### Creating Streams

| Method | Purpose |
|--------|---------|
| `Stream.init(chunk)` | From a Chunk |
| `Stream.range(start, end)` | Numeric range |
| `Stream.from(channel)` | From a Channel (backpressured) |

### Transforming

| Method | Purpose |
|--------|---------|
| `.map(f)` | Transform each element |
| `.mapPure(f)` | Pure transform (no effects, optimized) |
| `.mapChunk(f)` | Transform entire chunks |
| `.filter(f)` | Keep elements matching predicate |
| `.flatMap(f)` | One-to-many transform |
| `.take(n)` | First n elements |
| `.drop(n)` | Skip first n elements |
| `.concat(other)` | Append another stream |

### Consuming

| Method | Result | Purpose |
|--------|--------|---------|
| `.run` | `Chunk[V] < S` | Collect all into Chunk |
| `.runSeq` | `Seq[V] < S` | Collect all into Seq |
| `.foreach(f)` | `Unit < S` | Process each element |
| `.fold(init)(f)` | `B < S` | Reduce to single value |
| `.scan(init)(f)` | `Stream[B, S]` | Running accumulation |

## Common Patterns

### Processing pipeline

```scala
val result: Chunk[String] < Sync =
    Stream.range(1, 100)
        .filter(_ % 2 == 0)
        .map(i => Sync.defer(transform(i)))
        .take(10)
        .run
```

### From channel (backpressured)

```scala
val processed: Unit < Async =
    Scope.run {
        for
            chan <- Channel.init[Int](capacity = 16)
            _   <- Stream.from(chan)
                      .map(process)
                      .foreach(emit)
        yield ()
    }
```

## Gotchas

- Streams process in chunks for efficiency — `.mapChunk` is faster than `.map` for batch operations
- Use `.mapPure` when the transform has no effects (avoids unnecessary suspension)
- `Stream.run` collects ALL elements into memory — use `.foreach` or `.fold` for large streams
- Streams are lazy — nothing executes until consumed (`.run`, `.foreach`, `.fold`)

---
id: kyo-recipe-stream-processing
title: "Process Data Streams"
category: recipe
layer: application
tags: [streaming, pipeline, backpressure, channel]
source_files: []
source_commit: 9bab8d00
api_surface: [Stream, Channel, Stream.from, Stream.range, Stream.map, Stream.filter, Stream.fold, Stream.foreach]
related: [kyo-effect-stream, kyo-effect-channel]
see_also: [kyo-pattern-streaming]
platforms: [jvm, js, native]
modules_needed: [kyo-core]
complexity: moderate
---

## Goal

Process sequences of data lazily with optional backpressure.

## Steps

### Simple pipeline

```scala
import kyo.*

val result: Chunk[String] < Sync =
    Stream.range(1, 10000)
        .filter(_ % 2 == 0)
        .map(i => Sync.defer(expensive(i)))
        .take(100)
        .run
```

### Producer-consumer with backpressure

```scala
val pipeline: Unit < (Async & Scope) =
    direct {
        val chan = Channel.init[RawData](capacity = 64).now

        // Producer fiber
        val producer = Async.run {
            produceData().foreach(chan.put).andThen(chan.close)
        }.now

        // Consumer processes as stream
        chan.stream
            .map(parse)
            .filter(_.isValid)
            .map(transform)
            .foreach(save)
            .now

        producer.get.now
    }
```

### Fold to summary

```scala
val stats: Stats < Sync =
    Stream.from(dataSource)
        .fold(Stats.empty) { (acc, item) =>
            acc.update(item)
        }
```

### Parallel processing

```scala
val results: Chunk[Output] < Async =
    Stream.from(inputs)
        .mapChunk { chunk =>
            Async.parallel(chunk.toSeq.map(process)).map(Chunk.from)
        }
        .run
```

## Variations

- **Error handling in streams:** Use `.map(item => Abort.catching(process(item)))` then handle errors per-item
- **Chunked I/O:** Use `.mapChunk` for batch database writes
- **Multiple consumers:** Use `Hub` to broadcast to multiple stream processors

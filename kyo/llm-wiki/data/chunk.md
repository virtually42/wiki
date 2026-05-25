---
id: kyo-data-chunk
title: "Chunk — Efficient Immutable Sequence"
category: data
layer: foundation
tags: [collection, sequence, immutable, slice, efficient]
source_files:
  - kyo-data/shared/src/main/scala/kyo/Chunk.scala
source_commit: 9bab8d00
api_surface: [Chunk, Chunk.apply, Chunk.empty, Chunk.from, Chunk.fill]
related: [kyo-data-maybe, kyo-effect-stream]
see_also: [kyo-pattern-streaming]
platforms: [jvm, js, native]
opaque: false
replaces: "List/Vector"
---

## What It Is

Immutable sequence with O(1) take/drop/slice via structural sharing. Kyo's preferred collection.

## When to Use

**Use `Chunk` instead of `List`, `Vector`, `Seq` in Kyo code.**

## Key APIs

### Creation

| Method | Purpose |
|--------|---------|
| `Chunk(a, b, c)` | From varargs |
| `Chunk.empty[A]` | Empty chunk |
| `Chunk.from(seq)` | From Iterable |
| `Chunk.fill(n)(value)` | Repeated value |

### Slicing (O(1))

| Method | Purpose |
|--------|---------|
| `.take(n)` | First n elements |
| `.drop(n)` | Skip first n |
| `.slice(from, to)` | Sub-range |

### Transformation

| Method | Purpose |
|--------|---------|
| `.map(f)` | Transform elements |
| `.filter(f)` | Keep matching |
| `.flatMap(f)` | One-to-many |
| `.foldLeft(init)(f)` | Reduce |
| `.concat(other)` | Append |
| `.append(elem)` | Add one |

## Performance

- O(1) slice/take/drop via structural sharing
- Array-backed for cache-friendly access
- Better than List for random access, better than Vector for slicing
- `Emit.run` returns Chunk; Stream processes in Chunks internally

## Gotchas

- NOT lazy — use Stream for lazy evaluation
- Use `ChunkBuilder` for incremental construction

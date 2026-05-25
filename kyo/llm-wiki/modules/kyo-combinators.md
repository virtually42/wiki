---
id: kyo-module-kyo-combinators
title: "kyo-combinators — ZIO-Style Operators"
category: module
layer: core
tags: [combinators, zio-style, operators, extensions, parallel]
source_files:
  - kyo-combinators/shared/src/main/scala/kyo/
source_commit: 9bab8d00
api_surface: [Kyo.foreach, Kyo.collect, Kyo.foreachPar, Kyo.collectPar, "*>", "<*>", "<&>", fork, delay, repeat]
related: [kyo-concept-pending-type]
see_also: []
platforms: [jvm, js, native]
module_name: "kyo-combinators"
dependencies: [kyo-core]
---

## Purpose

ZIO-like combinators and extension methods for Kyo computations. Opt-in convenience layer.

## Setup

```scala
libraryDependencies += "io.getkyo" %% "kyo-combinators" % kyoVersion
```

## Key APIs

### Sequential Operators

| Operator | Purpose |
|----------|---------|
| `a *> b` | Sequence, keep right (zipRight) |
| `a <* b` | Sequence, keep left (zipLeft) |
| `a <*> b` | Sequence, keep both (zip) |

### Parallel Operators

| Operator | Purpose |
|----------|---------|
| `a &> b` | Parallel, keep right |
| `a <& b` | Parallel, keep left |
| `a <&> b` | Parallel, keep both |

### Extension Methods on `A < S`

| Method | Purpose |
|--------|---------|
| `.fork` | Fork with Scope-guaranteed interruption |
| `.delay(duration)` | Delay execution |
| `.repeat(n)` | Repeat n times |
| `.repeatAtInterval(interval)` | Periodic execution |
| `.debugValue` | Print value for debugging |
| `.debugTrace` | Print with stack trace |

### Collection Operations on `Kyo` Object

| Method | Purpose |
|--------|---------|
| `Kyo.foreach(seq)(f)` | Map sequentially |
| `Kyo.collect(seq)` | Sequence computations |
| `Kyo.foreachPar(seq)(f)` | Map in parallel |
| `Kyo.collectPar(seq)` | Sequence in parallel |

## Integration Notes

- Parallel operations default to `2 * CPU cores` concurrency
- Symbolic operators are NOT in kyo-core — must import kyo-combinators
- For-comprehension style works without this module

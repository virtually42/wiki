---
id: kyo-effect-emit
title: "Emit — Value Emission"
category: effect
layer: prelude
tags: [emission, writer, accumulation, push-based]
source_files:
  - /p/gh/kyo/kyo-prelude/shared/src/main/scala/kyo/Emit.scala
source_commit: 9bab8d00
api_surface: [Emit.value, Emit.valueWith, Emit.run, Emit.runFold, Emit.runForeach]
related: [kyo-effect-var, kyo-effect-stream]
see_also: [kyo-pattern-streaming]
platforms: [jvm, js, native]
effect_type: ArrowEffect
suspend_methods: [value, valueWith, valueWhen]
handle_methods: [run, runFold, runForeach]
pending_type: "Emit[V]"
---

## What It Does

Push-based value emission (writer effect). Emits values during computation without accumulating them in a data structure until handled. Lower-level than Stream.

## Key APIs

### Suspending

| Method | Signature | Purpose |
|--------|-----------|---------|
| `Emit.value(v)` | `Unit < Emit[V]` | Emit a single value |
| `Emit.valueWith(v)(f)` | `A < Emit[V]` | Emit and continue |
| `Emit.valueWhen(cond)(v)` | `Unit < Emit[V]` | Conditional emit |

### Handling

| Method | Signature | Purpose |
|--------|-----------|---------|
| `Emit.run(comp)` | `(Chunk[V], A) < S` | Collect all emitted values |
| `Emit.runFold(init)(f)(comp)` | `(B, A) < S` | Fold over emitted values |
| `Emit.runForeach(f)(comp)` | `A < S` | Process each emission (side effect) |

## Common Patterns

### Logging events during computation

```scala
val result: (Chunk[String], Int) < Any =
    Emit.run {
        for
            _ <- Emit.value("started")
            r <- compute()
            _ <- Emit.value("done")
        yield r
    }
```

### Fold into summary

```scala
val (count, result) =
    Emit.runFold(0)((acc, _: Event) => acc + 1) {
        processEvents()
    }
```

## Gotchas

- `Emit` is push-based (producer drives) — for pull-based, use `Poll` or `Stream`
- Prefer `Stream` for most streaming use cases — `Emit` is lower-level
- Emitted values are collected as `Chunk` by default (efficient)
- `Emit.run` accumulates ALL values in memory — use `runFold`/`runForeach` for large streams

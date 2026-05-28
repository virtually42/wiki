---
id: kyo-effect-var
title: "Var — Functional Mutable State"
category: effect
layer: prelude
tags: [state, mutable, functional-state, isolation]
source_files:
  - /p/gh/kyo/kyo-prelude/shared/src/main/scala/kyo/Var.scala
source_commit: 9bab8d00
api_surface: [Var.get, Var.set, Var.update, Var.use, Var.run, Var.runTuple]
related: [kyo-effect-emit, kyo-effect-local]
see_also: [kyo-pattern-streaming]
platforms: [jvm, js, native]
effect_type: ArrowEffect
suspend_methods: [get, set, update, use]
handle_methods: [run, runTuple]
pending_type: "Var[V]"
---

## What It Does

Provides functional mutable state within a computation. State changes are tracked through the effect system and isolated per handler invocation.

## Key APIs

### Suspending

| Method | Signature | Purpose |
|--------|-----------|---------|
| `Var.get[V]` | `V < Var[V]` | Read current state |
| `Var.set[V](value)` | `Unit < Var[V]` | Replace state |
| `Var.update[V](f: V => V)` | `Unit < Var[V]` | Transform state |
| `Var.use[V](f: V => A)` | `A < Var[V]` | Read and transform |

### Handling

| Method | Signature | Purpose |
|--------|-----------|---------|
| `Var.run[V](initial)(comp)` | `A < S` | Handle, discard final state |
| `Var.runTuple[V](initial)(comp)` | `(V, A) < S` | Handle, return (finalState, result) |

## Common Patterns

### Accumulator

```scala
val result: (Int, Seq[String]) < Any =
    Var.runTuple(0) {
        for
            _ <- Var.update[Int](_ + 1)
            _ <- Var.update[Int](_ + 1)
            v <- Var.get[Int]
        yield Seq(s"count: $v")
    }
// result: (2, Seq("count: 2"))
```

### State machine

```scala
enum State:
    case Idle, Running, Done

val computation: String < Var[State] =
    for
        _ <- Var.set(State.Running)
        r <- doWork()
        _ <- Var.set(State.Done)
    yield r
```

## Gotchas

- `Var` state is NOT shared between fibers — each fiber gets its own copy
- Use `Var.run` to provide initial state (similar to `Env.run` but mutable)
- For shared concurrent state, use `Atomic` or `Channel` instead
- `Var` isolates state per handler — useful for testing

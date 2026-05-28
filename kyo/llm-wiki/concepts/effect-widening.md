---
id: kyo-concept-effect-widening
title: "Effect Widening"
category: concept
layer: foundation
tags: [type-system, contravariance, widening, subtyping]
source_files:
  - /p/gh/kyo/kyo-kernel/shared/src/main/scala/kyo/kernel/Pending.scala
source_commit: 9bab8d00
api_surface: []
related: [kyo-concept-pending-type, kyo-concept-effect-composition]
see_also: []
platforms: [jvm, js, native]
---

## Core Idea

The `S` parameter in `A < S` is contravariant. This means a computation with fewer effects automatically widens to accept more effects:

```scala
val a: Int < Any = 1                          // pure
val b: Int < Sync = a                         // widen to Sync
val c: Int < (Sync & Abort[Exception]) = b    // widen further
val d: Int < (Sync & Abort[Exception]) = 42   // pure value widens directly
```

## Why This Matters

1. **No wrapping needed** — pure values pass directly where effects are expected
2. **map subsumes flatMap** — the returned computation widens automatically
3. **Flexible function parameters** — functions accepting `A < S` accept any subset of `S`

```scala
// This function accepts any computation with at most Sync & Abort
def process(v: Int < (Sync & Abort[Exception])): Int < (Sync & Abort[Exception]) =
    v.map(_ + 1)

// All of these work:
process(42)                           // pure value
process(Sync.defer(42))              // only Sync
process(Abort.get(Right(42)))        // only Abort
process(Sync.defer(Abort.get(Right(42)).eval)) // both
```

## How map Uses Widening

When you `map` over a computation and return another computation, the effect sets union:

```scala
val a: Int < Sync = Sync.defer(1)

// The lambda returns Int < Abort[String], but map's result
// automatically widens to include both Sync and Abort
val b: Int < (Sync & Abort[String]) =
    a.map(x => Abort.get(Right(x)))
```

This is why `map` and `flatMap` are equivalent in Kyo — there's no need for `flatMap` to "unwrap" an inner effect type because widening handles it.

## Gotchas

- Widening only goes one direction: you can add effects, never remove them
- To remove effects, you must handle them (e.g., `Abort.run`)
- Type inference sometimes needs help — annotate when the compiler struggles

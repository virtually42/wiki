---
id: kyo-concept-pending-type
title: "The Pending Type: A < S"
category: concept
layer: foundation
tags: [type-system, pending, effects, core-abstraction]
source_files:
  - /p/gh/kyo/kyo-kernel/shared/src/main/scala/kyo/kernel/Pending.scala
source_commit: 9bab8d00
api_surface: [<, eval, map, flatMap, andThen, handle]
related: [kyo-concept-effect-widening, kyo-concept-effect-composition]
see_also: [kyo-concept-direct-syntax]
platforms: [jvm, js, native]
---

## Core Idea

All Kyo computations are expressed via the infix type `<` ("Pending"):

```scala
opaque type <[+A, -S]
```

- `A` — the output type
- `S` — the pending effects (unordered type-level set via intersection)

```scala
Int < Abort[String]              // Int pending Abort
String < (Abort[Absent] & Sync)  // String pending Abort and Sync
```

## Pure Values Are Computations

Any `T` is automatically `T < Any` (empty effect set). This eliminates the need to distinguish pure values from effectful computations:

```scala
val a: Int < Any = 1
val b: Int = a.eval  // no effects to handle, safe to eval
```

## Map Instead of FlatMap

Because of effect widening, `map` subsumes `flatMap`. The effect set automatically unions:

```scala
def example(
    a: Int < Sync,
    b: Int < Abort[Exception]
): Int < (Sync & Abort[Exception]) =
    a.map(v => b.map(_ + v))
```

## Key Operations

| Method | Purpose |
|--------|---------|
| `.map(f)` | Transform output, effects automatically widen |
| `.flatMap(f)` | Same as map (exists for for-comprehension compat) |
| `.andThen(next)` | Sequence, discard first result |
| `.handle(handlers*)` | Chain effect handlers without nesting |
| `.eval` | Extract pure value (only when S = Any) |

## The handle Method

Chains effect handlers fluently:

```scala
val a: Int < (Abort[String] & Env[Int]) = ...

val result: Result[String, Int] =
    a.handle(Abort.run(_))
     .handle(Env.run(10))
     .eval

// Or multiple at once:
a.handle(Abort.run(_), Env.run(10)).eval
```

## Gotchas

- `eval` only works when no effects remain (S = Any). Compiler rejects otherwise.
- Prefer `map` over `flatMap` — they're equivalent in Kyo due to widening.
- Type inference usually works, but explicit annotations help readability.

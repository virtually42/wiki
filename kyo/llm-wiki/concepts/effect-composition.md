---
id: kyo-concept-effect-composition
title: "Effect Composition"
category: concept
layer: foundation
tags: [effects, composition, intersection-types, handling-order]
source_files:
  - kyo-kernel/shared/src/main/scala/kyo/kernel/Pending.scala
source_commit: 9bab8d00
api_surface: [map, flatMap, handle, Abort.run, Env.run]
related: [kyo-concept-pending-type, kyo-concept-effect-widening]
see_also: [kyo-pattern-error-handling]
platforms: [jvm, js, native]
---

## Core Idea

Effects compose via type intersection (`&`). When you combine computations with different effects, Kyo automatically unions their effect sets:

```scala
val a: Int < Sync = Sync.defer(42)
val b: Int < Abort[String] = Abort.get(Right(1))

// Combining: effects union automatically
val c: Int < (Sync & Abort[String]) =
    a.map(x => b.map(y => x + y))
```

## Handling Order Matters

Effects are unordered at the type level, but handling order affects the result type and runtime behavior:

```scala
val computation: Int < (Abort[String] & Abort[Exception]) = ...

// Handle String first → Exception wraps String result
val a: Result[Exception, Result[String, Int]] =
    Abort.run[String](computation)
        .handle(Abort.run[Exception](_))
        .eval

// Handle Exception first → String wraps Exception result  
val b: Result[String, Result[Exception, Int]] =
    Abort.run[Exception](computation)
        .handle(Abort.run[String](_))
        .eval
```

**Rule:** The outermost handler "catches" its effect first. Short-circuiting effects (like Abort) change behavior based on handling order.

## Union Types for Shared Effects

Multiple errors of the same effect can use union types:

```scala
// These are equivalent:
val a: Int < (Abort[String] & Abort[Exception]) = ...
val b: Int < Abort[String | Exception] = ...

// Handle the union at once:
val result: Result[String | Exception, Int] < Any =
    Abort.run[String | Exception](b)
```

## For-Comprehension Style

Effects compose naturally in for-comprehensions:

```scala
val result: Int < (Abort[String] & Env[Int]) =
    for
        v <- Abort.get(Right(42))
        e <- Env.get[Int]
    yield v + e
```

## Handling Multiple Effects

Use `handle` for fluent chaining:

```scala
val result: Result[String, Int] =
    computation
        .handle(Abort.run(_))
        .handle(Env.run(10))
        .eval
```

## Gotchas

- Handling order for `Abort` with multiple error types changes the nesting of `Result` types
- Effects are unordered in the type — `(Sync & Abort[E])` == `(Abort[E] & Sync)`
- You cannot `eval` until ALL effects are handled
- `Sync` should typically be the last effect handled (via KyoApp)

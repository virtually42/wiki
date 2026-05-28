---
id: kyo-effect-abort
title: "Abort — Typed Error Handling"
category: effect
layer: prelude
tags: [error-handling, short-circuit, typed-errors, union-types, result]
source_files:
  - /p/gh/kyo/kyo-prelude/shared/src/main/scala/kyo/Abort.scala
source_commit: 9bab8d00
api_surface: [Abort.fail, Abort.panic, Abort.get, Abort.when, Abort.unless, Abort.catching, Abort.run, Abort.runPartial, Abort.recover, Abort.fold]
related: [kyo-data-result, kyo-effect-env]
see_also: [kyo-pattern-error-handling]
platforms: [jvm, js, native]
effect_type: ArrowEffect
suspend_methods: [fail, panic, get, when, unless, catching]
handle_methods: [run, runPartial, recover, fold]
pending_type: "Abort[E]"
---

## What It Does

Short-circuits computation with a typed error `E`. Equivalent to ZIO's failure channel. Three outcomes:
- **Success[A]** — completed normally
- **Failure[E]** — domain error (typed, recoverable)
- **Panic(Throwable)** — unexpected exception (propagates through all handlers)

## Key APIs

### Suspending (introducing Abort[E])

| Method | Signature | Purpose |
|--------|-----------|---------|
| `fail` | `Abort.fail[E](e: E): Nothing < Abort[E]` | Short-circuit with typed error |
| `panic` | `Abort.panic(ex: Throwable): Nothing < Abort[E]` | Unrecoverable exception |
| `get` | `Abort.get(either: Either[E, A]): A < Abort[E]` | Extract Right or fail with Left |
| `get` | `Abort.get(maybe: Maybe[A]): A < Abort[Absent]` | Extract Present or fail |
| `when` | `Abort.when[E](cond: Boolean)(e: => E): Unit < Abort[E]` | Conditional fail |
| `unless` | `Abort.unless[E](cond: Boolean)(e: => E): Unit < Abort[E]` | Inverse conditional fail |
| `catching` | `Abort.catching[E <: Throwable](f: => A): A < Abort[E]` | Catch exceptions as typed |

### Handling (eliminating Abort[E])

| Method | Result | Purpose |
|--------|--------|---------|
| `Abort.run[E](v)` | `Result[E, A] < S` | Full handling (Success, Failure, Panic) |
| `Abort.runPartial[E](v)` | `Result.Partial[E, A] < S` | Handles Failure only (Panic throws) |
| `Abort.recover[E](f)(v)` | `A < S` | Recover from Failure with function |
| `Abort.fold[E](fail, panic)(v)` | `B < S` | Handle all cases |

## Composition

### Union types for multiple errors

```scala
// Two separate Abort effects
val a: Int < (Abort[String] & Abort[Exception]) = ...

// Or union type (equivalent)
val b: Int < Abort[String | Exception] = ...

// Handle one at a time
val c: Result[String, Int] < Abort[Exception] = Abort.run[String](a)

// Or handle union at once
val d: Result[String | Exception, Int] < Any = Abort.run[String | Exception](b)
```

### Handling order affects nesting

```scala
// Handle String first:
Abort.run[String](v)  // → Result[String, Int] < Abort[Exception]
// Then Exception:     // → Result[Exception, Result[String, Int]] < Any

// Handle Exception first:
Abort.run[Exception](v)  // → Result[Exception, Int] < Abort[String]
// Then String:           // → Result[String, Result[Exception, Int]] < Any
```

## Common Patterns

```scala
// Guard clause
def process(input: String): Output < Abort[InvalidInput] =
    Abort.when(input.isEmpty)(InvalidInput("empty"))
    // ... continue

// Catch and type exceptions
val parsed: Int < Abort[NumberFormatException] =
    Abort.catching[NumberFormatException]("123".toInt)

// Convert Either-based APIs
val result: User < Abort[DbError] =
    Abort.get(db.findUser(id))
```

## Gotchas

- `Abort.run` returns `Result[E, A]`, not bare `A` — must unwrap or chain
- `Panic` bypasses typed error handling — it's for genuine bugs
- Abort requires a type parameter: `Abort.run[String](...)` not `Abort.run(...)`
- Handling order matters for short-circuiting behavior

---
id: kyo-data-result
title: "Result — Typed Failure Handling"
category: data
layer: foundation
tags: [result, success, failure, panic, error-handling, opaque-type]
source_files:
  - /p/gh/kyo/kyo-data/shared/src/main/scala/kyo/Result.scala
source_commit: 9bab8d00
api_surface: [Result.succeed, Result.fail, Result.panic, Result.apply, Result.Success, Result.Failure, Result.Panic]
related: [kyo-data-maybe, kyo-effect-abort]
see_also: [kyo-pattern-error-handling]
platforms: [jvm, js, native]
opaque: true
replaces: "Either/Try"
---

## What It Is

Three-state computation result: Success[A], Failure[E], Panic(Throwable). Combines Try and Either.

## When to Use

**Always use `Result` instead of `Either`/`Try` in Kyo code.** Produced by `Abort.run`.

## Key APIs

### Creation

| Method | Purpose |
|--------|---------|
| `Result.succeed(value)` | Create Success |
| `Result.fail(error)` | Create Failure[E] |
| `Result.panic(throwable)` | Create Panic |
| `Result(expr)` | Catch exceptions → Panic |

### Querying

| Method | Purpose |
|--------|---------|
| `.isSuccess` / `.isFailure` / `.isPanic` | Check state |
| `.getOrThrow` | Unwrap or throw |
| `.getOrElse(default)` | Unwrap with fallback |

### Transforming

| Method | Purpose |
|--------|---------|
| `.map(f)` | Transform success value |
| `.flatMap(f)` | Chain Result operations |
| `.mapFailure(f)` | Transform error type |
| `.flatMapFailure(f)` | Recover from failure |
| `.foldError(success, failure)` | Handle both cases |
| `.filter(pred)` | Conditionally fail |

### Conversion

| Method | Purpose |
|--------|---------|
| `.toEither` | Convert to Either |
| `.toTry` | Convert to Try |
| `.toMaybe` | Success → Present, else Absent |

## Pattern Matching

```scala
result match
    case Result.Success(value) => s"ok: $value"
    case Result.Failure(err)   => s"failed: $err"
    case Result.Panic(ex)      => s"panic: ${ex.getMessage}"
```

## Relationship to Abort

`Abort.run` → `Result`, `Abort.runPartial` → `Result.Partial` (no Panic case).

## Gotchas

- THREE states, not two — always consider Panic
- `Result(expr)` catches as Panic, not Failure
- Opaque type — use `t`-strings for display
- Pattern match all three cases for exhaustive handling

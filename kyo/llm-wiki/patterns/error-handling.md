---
id: kyo-pattern-error-handling
title: "Error Handling Patterns"
category: pattern
layer: core
tags: [error-handling, abort, result, union-types, recovery]
source_files: []
source_commit: 9bab8d00
api_surface: [Abort.fail, Abort.run, Abort.recover, Abort.fold, Result]
related: [kyo-effect-abort, kyo-data-result]
see_also: []
platforms: [jvm, js, native]
when_to_use: "Any computation that can fail with typed domain errors"
when_not_to_use: "Simple absence (use Maybe) or truly unexpected exceptions (let them Panic)"
---

## Problem

How to handle typed errors, compose multiple error types, and recover gracefully.

## Solution

### Single error type

```scala
def validate(input: String): Valid < Abort[ValidationError] =
    Abort.when(input.isEmpty)(ValidationError("empty"))
    parse(input)

// Handle at boundary
val result: Result[ValidationError, Valid] < Any =
    Abort.run(validate(userInput))
```

### Multiple error types (union)

```scala
def process(id: Int): Data < Abort[DbError | NetworkError] =
    for
        raw  <- fetchFromDb(id)     // Abort[DbError]
        data <- enrichFromApi(raw)  // Abort[NetworkError]
    yield data

// Handle all at once
val result: Result[DbError | NetworkError, Data] = 
    Abort.run[DbError | NetworkError](process(1)).eval
```

### Selective recovery

```scala
// Recover from one error, let others propagate
val recovered: Data < Abort[NetworkError] =
    Abort.recover[DbError] { err =>
        fallbackData(err)
    }(process(id))
```

### Fold for complete handling

```scala
val response: Response < Sync =
    Abort.fold[DbError | NetworkError](
        fail = {
            case e: DbError      => Response.serverError(e.msg)
            case e: NetworkError => Response.gatewayError(e.msg)
        },
        panic = ex => Response.internalError(ex.getMessage)
    )(process(id))
```

## Trade-offs

- Union types keep error types precise but can get verbose
- `Abort.run` wraps in Result (need to unwrap); `Abort.recover` stays flat
- Handle errors as close to the source as possible, or bubble up to boundary

## Related Patterns

- [dependency-injection](dependency-injection.md) — inject error handlers
- [streaming](streaming.md) — error handling in streams

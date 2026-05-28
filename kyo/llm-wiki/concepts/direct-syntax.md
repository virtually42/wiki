---
id: kyo-concept-direct-syntax
title: "Direct Syntax"
category: concept
layer: core
tags: [direct, syntax, now, later, control-flow, macro]
source_files:
  - /p/gh/kyo/kyo-direct/shared/src/main/scala/kyo/
source_commit: 9bab8d00
api_surface: [direct, .now, .later]
related: [kyo-concept-pending-type, kyo-module-kyo-direct]
see_also: []
platforms: [jvm, js, native]
---

## Core Idea

`direct { }` provides imperative-looking syntax for effectful code. Instead of chaining `.map`, you use `.now` to sequence effects:

```scala
import kyo.*

// Direct style (recommended for complex sequences)
val a: String < (Abort[Exception] & Sync) =
    direct {
        val b: String = Sync.defer("hello").now
        val c: String = Abort.get(Right("world")).now
        b + " " + c
    }

// Equivalent desugared
val b: String < (Abort[Exception] & Sync) =
    Sync.defer("hello").map { b =>
        Abort.get(Right("world")).map { c =>
            b + " " + c
        }
    }
```

## .now vs .later

| Operator | Purpose | Result type |
|----------|---------|-------------|
| `.now` | Sequence effect immediately, get result | The output type `A` |
| `.later` | Preserve effect without sequencing | The pending type `A < S` |

```scala
direct {
    val x: Int = Sync.defer(1).now         // sequenced: Int
    val y: Int < Sync = Sync.defer(2).later // preserved: Int < Sync
    x + y.now                               // sequence later
}
```

## Supported Control Flow

The `direct` macro virtualizes:
- Value definitions (`val x = effect.now`)
- `if`/`else` with effectful conditions
- `while` loops with effectful conditions
- Pattern matching on effectful values
- `&&` and `||` with short-circuit semantics
- Collection operations (`.foreach`, `.map` on Seq/Option/Either)

```scala
direct {
    val cond: Boolean = Sync.defer(true).now
    if cond then "yes" else "no"

    val result: String = Sync.defer(1).now match
        case 1 => "One"
        case _ => "Other"
}
```

## Effectful Hygiene

Within `direct`, any `<` value MUST be used with `.now` or `.later`. Unused effects cause a compile error:

```scala
// COMPILE ERROR — effect would be silently dropped
direct {
    Sync.defer(println(42))  // error: must use .now or .later
    42
}
```

## Disallowed Constructs

Inside `direct` blocks, these are NOT allowed:
- Nested `direct` blocks
- `var` declarations
- `return` statements
- `lazy val`
- `lambda` or `def` containing `.now`
- `try`/`catch` blocks
- `throw` expressions
- `class`, `trait`, `object` definitions
- `for`-comprehensions

## Gotchas

- `direct` is a macro (built on dotty-cps-async) — compile errors can be cryptic
- `.now` can only be used at the top level of `direct`, not inside lambdas
- Use `.map` for transformations inside lambdas, even within direct blocks
- Module: `kyo-direct` (separate dependency from kyo-core)

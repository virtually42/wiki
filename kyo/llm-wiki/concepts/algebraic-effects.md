---
id: kyo-concept-algebraic-effects
title: "Algebraic Effects in Kyo"
category: concept
layer: foundation
tags: [effects, algebraic-effects, suspend, handle, architecture]
source_files:
  - kyo-kernel/shared/src/main/scala/kyo/kernel/
source_commit: 9bab8d00
api_surface: [ArrowEffect, ContextEffect]
related: [kyo-concept-pending-type, kyo-concept-effect-composition]
see_also: []
platforms: [jvm, js, native]
---

## Core Idea

Kyo implements algebraic effects with modular handlers. Unlike monad-based systems (Cats Effect, ZIO), effects are:

- **Open** — developers define custom effects, not just use built-in ones
- **Composable** — effects combine via type intersection, not monad stacking
- **No category theory** — no Functor, Monad, Applicative hierarchies

## Suspend / Handle Model

Every effect has two sides:

1. **Suspend** — introduce the effect (e.g., `Abort.fail("oops")`)
2. **Handle** — eliminate the effect (e.g., `Abort.run(computation)`)

Suspending adds an effect to the `S` type parameter. Handling removes it:

```scala
// Suspend: introduces Abort[String] into S
val a: Int < Abort[String] = Abort.fail("oops")

// Handle: removes Abort[String] from S, wraps in Result
val b: Result[String, Int] < Any = Abort.run(a)
```

## Two Effect Kinds

| Kind | Purpose | Example |
|------|---------|---------|
| **ArrowEffect** | Intercepts computation, may short-circuit or fork | Abort, Async, Choice |
| **ContextEffect** | Provides a value to the computation | Env, Local |

ArrowEffects are more powerful (can change control flow). ContextEffects are simpler (just provide data).

## Effect Naming Conventions

| Prefix | Purpose | Example |
|--------|---------|---------|
| `init*` | Create an instance of the effect's container | `Fiber.init` |
| `get*` | Extract a value, introducing the effect | `Abort.get(either)` |
| `run*` | Handle the effect, removing it from S | `Abort.run(computation)` |

## No Monads

Kyo does NOT use monads. The `<` type is not a monad — it's an opaque type representing a suspended computation. This means:

- No `pure`/`flatMap` laws to satisfy
- No monad transformers needed
- Effects compose directly via intersection types
- `map` works like `flatMap` due to widening (no distinction needed)

## How It Differs from ZIO/CE

| Aspect | ZIO/Cats Effect | Kyo |
|--------|----------------|-----|
| Error channel | Fixed (ZIO: E, CE: Throwable) | Open (any Abort[E]) |
| Dependencies | Fixed (ZIO: R) | Open (any Env[R]) |
| Custom effects | Not truly supported | First-class |
| Base type | Monad | Opaque pending type |
| Composition | Monad stacking | Type intersection |

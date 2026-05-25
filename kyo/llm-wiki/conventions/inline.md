---
id: kyo-convention-inline
title: "Inline Guidelines"
category: convention
layer: foundation
tags: [inline, performance, suspend, handle, optimization]
source_files:
  - CONTRIBUTING.md
source_commit: 9bab8d00
api_surface: []
related: [kyo-convention-method-signatures]
see_also: []
platforms: [jvm, js, native]
---

## Rule

Use `inline` on effect **suspension** paths (creating effects). Do NOT use `inline` on **handling** paths (running effects).

## Rationale

Inlining suspension paths avoids function dispatch overhead on the hot path (effect creation). Handler paths are called once at boundaries — inlining them bloats bytecode for no benefit.

## Examples

### Do — Inline suspension

```scala
// Effect creation — inline for zero-cost suspension
inline def fail[E](e: E)(using inline Tag[E], inline Frame): Nothing < Abort[E] = ...
inline def defer[A](expr: => A)(using inline Frame): A < Sync = ...
```

### Don't — Inline handling

```scala
// Effect handling — NOT inline (called at boundaries)
def run[E](comp: A < (Abort[E] & S))(using Tag[E], Frame): Result[E, A] < S = ...
def run(comp: A < (Sync & S))(using AllowUnsafe): A < S = ...
```

### Inline using clauses

```scala
// In inline methods, `using` params should also be `inline`
inline def myEffect[A](using inline Tag[A], inline Frame): A < MyEffect = ...
```

## Exceptions

- Use inline to avoid function dispatch in hot-path utilities
- Never inline large method bodies
- `inline` in test code is rarely needed

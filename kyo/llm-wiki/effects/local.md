---
id: kyo-effect-local
title: "Local — Scoped Values"
category: effect
layer: prelude
tags: [context, scoped-values, thread-local, propagation]
source_files:
  - /p/gh/kyo/kyo-prelude/shared/src/main/scala/kyo/Local.scala
source_commit: 9bab8d00
api_surface: [Local.init, Local.get, Local.let]
related: [kyo-effect-env, kyo-effect-var]
see_also: []
platforms: [jvm, js, native]
effect_type: ContextEffect
suspend_methods: [get]
handle_methods: [let]
pending_type: "Sync"
---

## What It Does

Scoped contextual values, similar to `ThreadLocal` but with explicit scoping. Used for request context, tracing IDs, etc. Automatically propagated to forked fibers.

## Key APIs

| Method | Signature | Purpose |
|--------|-----------|---------|
| `Local.init(default)` | `Local[V]` | Create with default value |
| `local.get` | `V < Sync` | Read current value |
| `local.let(value)(comp)` | `A < S` | Set value within scope |

## Common Patterns

### Request context

```scala
val requestId: Local[String] = Local.init("unknown")

def processRequest(id: String, body: Request): Response < Sync =
    requestId.let(id) {
        // All code within this scope sees the request ID
        handleBody(body)
    }

def log(msg: String): Unit < Sync =
    requestId.get.map(id => println(s"[$id] $msg"))
```

### Fiber propagation

```scala
val traceId: Local[String] = Local.init("")

val result: Unit < Async =
    traceId.let("abc-123") {
        // Forked fibers inherit the local value
        Async.run(log("child fiber")).map(_.get)
        // Output: [abc-123] child fiber
    }
```

## Gotchas

- `Local` operates on top of `Sync` — reading it introduces `Sync`
- Values propagate to forked fibers automatically
- `let` is lexically scoped — value reverts when the block completes
- Different from `Env`: Local is mutable within scope, Env is immutable dependency injection
- Different from `Var`: Local uses dynamic scoping (propagates), Var uses handler scoping

---
id: kyo-effect-env
title: "Env — Dependency Injection"
category: effect
layer: prelude
tags: [dependency-injection, environment, typemap, layer]
source_files:
  - kyo-prelude/shared/src/main/scala/kyo/Env.scala
source_commit: 9bab8d00
api_surface: [Env.get, Env.run, Env.runLayer, Layer, Layer.init, Layer.from]
related: [kyo-effect-local, kyo-effect-abort]
see_also: [kyo-pattern-dependency-injection]
platforms: [jvm, js, native]
effect_type: ContextEffect
suspend_methods: [get]
handle_methods: [run, runLayer]
pending_type: "Env[R]"
---

## What It Does

Provides typed dependency injection. Similar to ZIO's environment but more granular — inject individual services directly or compose them via Layers.

## Key APIs

### Suspending

| Method | Signature | Purpose |
|--------|-----------|---------|
| `Env.get[R]` | `R < Env[R]` | Summon an instance from the environment |

### Handling

| Method | Signature | Purpose |
|--------|-----------|---------|
| `Env.run(value)(comp)` | Provides a concrete value, removes `Env[R]` |
| `Env.runLayer(layer)(comp)` | Provides dependencies via Layer composition |

## Composition

Multiple dependencies compose via intersection:

```scala
trait Database:
    def query: String < Sync

trait Cache:
    def get: Int < Sync

// Computation requiring both
val comp: String < (Env[Database] & Env[Cache] & Sync) =
    for
        db    <- Env.get[Database]
        cache <- Env.get[Cache]
        r     <- db.query
    yield r
```

## Common Patterns

### Direct injection

```scala
val db = new Database { def query = Sync.defer("result") }
val result: String < Sync = Env.run(db)(comp)
```

### Layer composition

```scala
val dbLayer: Layer[Database, Any] = Layer { new Database { ... } }
val cacheLayer: Layer[Cache, Any] = Layer { new Cache { ... } }

// Compose layers
val appLayer: Layer[Database & Cache, Any] =
    Layer.init[Database & Cache](dbLayer, cacheLayer)

// Provide via layer
val result: String < (Sync & Memo) = Env.runLayer(appLayer)(comp)
// Note: Layer uses Memo to ensure single initialization
val final_result: String < Sync = Memo.run(result)
```

### Layer with dependencies

```scala
// Layer that depends on another service
val userServiceLayer: Layer[UserService, Env[Database] & Sync] =
    Layer.from { (db: Database) =>
        new UserService { def getUser(id: Int) = db.query }
    }

// Chain: dbLayer provides Database, userServiceLayer consumes it
val combined: Layer[UserService, Sync] = dbLayer.to(userServiceLayer)
```

### Layer operators

| Operator | Purpose |
|----------|---------|
| `a.to(b)` | Output of `a` feeds input of `b` |
| `a.and(b)` | Parallel — provides both outputs |
| `a.using(b)` | Like `to` but keeps both outputs |

## Gotchas

- `Env.runLayer` introduces `Memo` effect (for single-init guarantee) — handle with `Memo.run`
- Each `Env.get[R]` is independent — getting `Database` twice returns the same instance
- Layer resolution is type-based, not name-based

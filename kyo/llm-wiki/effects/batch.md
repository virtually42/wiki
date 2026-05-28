---
id: kyo-effect-batch
title: "Batch — Automatic N+1 Optimization"
category: effect
layer: prelude
tags: [batching, n-plus-one, optimization, data-loading]
source_files:
  - /p/gh/kyo/kyo-prelude/shared/src/main/scala/kyo/Batch.scala
source_commit: 9bab8d00
api_surface: [Batch.source, Batch.sourceSeq, Batch.sourceMap, Batch.eval, Batch.run]
related: [kyo-effect-stream, kyo-effect-async]
see_also: []
platforms: [jvm, js, native]
effect_type: ArrowEffect
suspend_methods: [eval, source, sourceSeq, sourceMap]
handle_methods: [run]
pending_type: "Batch"
---

## What It Does

Automatically groups individual data lookups into batch operations. Solves N+1 query problems without changing application logic.

## Key APIs

### Creating Sources

| Method | Purpose |
|--------|---------|
| `Batch.sourceSeq[K, V, S](f: Seq[K] => Seq[V])` | Batch function returning ordered Seq |
| `Batch.sourceMap[K, V, S](f: Seq[K] => Map[K, V])` | Batch function returning Map |
| `Batch.source[K, V, S](f: Seq[K] => K => V < S)` | Generic batch with per-key effects |

### Using

| Method | Purpose |
|--------|---------|
| `Batch.eval(seq)` | Introduce elements to batch over |
| `source(key)` | Look up a single key (will be batched) |
| `Batch.run(comp)` | Execute, performing actual batched calls |

## Common Patterns

### Database batch loading

```scala
// Define source ONCE (reuse it!)
val userSource = Batch.sourceMap[Int, User, Sync] { ids =>
    Sync.defer(db.loadUsers(ids))  // single query for all ids
}

// Use individually — Batch groups them
val result: Seq[(Int, User)] < Sync =
    Batch.run {
        for
            id   <- Batch.eval(Seq(1, 2, 3, 4, 5))
            user <- userSource(id)  // NOT 5 queries — 1 batch!
        yield (id, user)
    }
```

### Chained batches

```scala
val result: Seq[String] < Sync =
    Batch.run {
        for
            id    <- Batch.eval(1 to 100)
            user  <- userSource(id)      // batch 1
            posts <- postSource(user.id)  // batch 2
        yield posts.title
    }
```

## Gotchas

- **Reuse source functions** — batching is identity-based. Creating new sources inline defeats batching.
- Source must return same number of elements as input (for `sourceSeq`)
- `Batch.run` executes all batched operations — call it once at the boundary
- Sources can have effects (the `S` type parameter)

```scala
// WRONG — new source each iteration, no batching
for
    id <- Batch.eval(ids)
    u  <- Batch.sourceSeq[Int, User, Any](seq => loadUsers(seq))(id)
yield u

// RIGHT — source defined once, reused
val src = Batch.sourceSeq[Int, User, Any](seq => loadUsers(seq))
for
    id <- Batch.eval(ids)
    u  <- src(id)
yield u
```

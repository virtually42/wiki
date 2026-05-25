---
id: kyo-module-kyo-stm
title: "kyo-stm — Software Transactional Memory"
category: module
layer: application
tags: [stm, transactions, concurrent-state, tref]
source_files:
  - kyo-stm/shared/src/main/scala/kyo/
source_commit: 9bab8d00
api_surface: [STM, TRef, STM.run]
related: [kyo-effect-async]
see_also: [kyo-pattern-concurrency]
platforms: [jvm, js, native]
module_name: "kyo-stm"
dependencies: [kyo-core]
---

## Purpose

Composable atomic transactions over shared mutable state. Alternative to locks for concurrent state management.

## Setup

```scala
libraryDependencies += "io.getkyo" %% "kyo-stm" % kyoVersion
```

## Key APIs

| Type/Method | Purpose |
|-------------|---------|
| `TRef[A]` | Transactional reference (mutable cell) |
| `TRef.init(value)` | Create a transactional reference |
| `tref.get` | Read within transaction |
| `tref.set(value)` | Write within transaction |
| `STM.run(comp)` | Execute transaction atomically |

## Common Patterns

### Atomic transfer

```scala
def transfer(from: TRef[Int], to: TRef[Int], amount: Int): Unit < (STM & Async) =
    STM.run {
        for
            balance <- from.get
            _       <- Check.require(balance >= amount, "insufficient")
            _       <- from.set(balance - amount)
            toBalance <- to.get
            _       <- to.set(toBalance + amount)
        yield ()
    }
```

## Integration Notes

- Transactions automatically retry on conflict (optimistic concurrency)
- Compose multiple TRef operations atomically
- No deadlocks (unlike lock-based approaches)
- Requires `Async` effect

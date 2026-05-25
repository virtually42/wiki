---
id: kyo-pattern-fiber-coordination
title: "Fiber Coordination Patterns"
category: pattern
layer: core
tags: [fibers, fork-join, structured-concurrency, latch, gate, scope]
source_files: []
source_commit: 9bab8d00
api_surface: [Async.run, Async.parallel, Async.race, Fiber.get, Latch, Gate, Scope.run]
related: [kyo-effect-async, kyo-effect-scope]
see_also: [kyo-pattern-concurrency]
platforms: [jvm, js, native]
when_to_use: "Multiple fibers need to coordinate or share lifecycle"
when_not_to_use: "Independent computations (use Async.parallel directly)"
---

## Problem

How to coordinate multiple fibers safely with proper lifecycle management.

## Solution

### Fork and Join

```scala
val result: (A, B) < (Async & Scope) =
    direct {
        val fa = Async.run(computeA()).now
        val fb = Async.run(computeB()).now
        (fa.get.now, fb.get.now)
    }
```

### Structured Concurrency with Scope

```scala
// Fibers are interrupted when scope closes
val managed: Result < Async =
    Scope.run {
        direct {
            val worker1 = Async.run(process()).now
            val worker2 = Async.run(process()).now
            worker1.get.now + worker2.get.now
        }
    }
// Both workers interrupted if scope exits (even on error)
```

### Countdown with Latch

```scala
val coordinated: Unit < (Async & Scope) =
    direct {
        val latch = Latch.init(3).now
        // Three workers count down when done
        Async.run(work().andThen(latch.down)).now
        Async.run(work().andThen(latch.down)).now
        Async.run(work().andThen(latch.down)).now
        // Main waits for all three
        latch.pass.now
    }
```

### Barrier with Gate

```scala
val synced: Unit < (Async & Scope) =
    direct {
        val gate = Gate.init(3).now
        // All three must arrive before any proceed
        Async.run(prepare().andThen(gate.pass)).now
        Async.run(prepare().andThen(gate.pass)).now
        prepare().andThen(gate.pass).now
    }
```

### Race (First Wins)

```scala
val fastest: Result < Async =
    Async.race(
        fetchFromServer1(),
        fetchFromServer2(),
        fetchFromServer3()
    )
// Losers are interrupted
```

## Trade-offs

- `Async.run` always requires `Scope` — enforces structured concurrency
- `Async.parallel` is simpler than manual fork/join for independent tasks
- Latch is one-shot (count to zero); Gate is reusable (CyclicBarrier)
- Race cancels losers — be aware of side effects in cancelled fibers

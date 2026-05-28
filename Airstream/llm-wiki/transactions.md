---
id: airstream-transactions
title: "Transactions"
category: concept
tags: [transaction, glitch-free, topological-rank, sync-observable, propagation]
source_files:
  - /p/gh/Airstream/src/main/scala/com/raquo/airstream/core/Transaction.scala
  - /p/gh/Airstream/src/main/scala/com/raquo/airstream/core/SyncObservable.scala
source_commit: 781abe8
related: [airstream-concepts, airstream-ownership]
see_also: [airstream-operators]
---

# Transactions

Transactions provide glitch-free propagation. They ensure synchronously-
dependent observables fire in the correct topological order within a single
logical "tick."

## The Glitch Problem

Without transactions:
```
Var(1) ──map(*2)──> Signal(2)
   │                    │
   └──map(+10)──> Signal(11)
                       │
              combine ──> Signal(2, 11)  ← CORRECT

But if Var changes to 3:
  Signal(*2) fires 6 first  → combine sees (6, 11) ← GLITCH
  Signal(+10) fires 13      → combine sees (6, 13) ← CORRECT
```

Transactions solve this by ordering fires by topological rank.

## Transaction Mechanics

```scala
class Transaction(code: Transaction => Any):
  private var maybePendingObservables: JsPriorityQueue[SyncObservable[_]]

  def enqueuePendingObservable(observable: SyncObservable[_]): Unit
  def resolvePendingObservables(): Unit
```

### Topological Rank (topoRank)

Every observable has a `topoRank: Int`:
- Source observables (Var, EventBus): rank 1
- Derived observables: rank = max(parent ranks) + 1

When a transaction fires:
1. Source emits value → fires to internal observers
2. Derived observables receive event but DON'T fire immediately
3. Instead, they enqueue themselves as "pending" in the transaction
4. Transaction resolves pending observables in topoRank order (lowest first)
5. Each dequeued observable computes and fires its value
6. This may enqueue more observables (higher rank)
7. Repeat until queue is empty

### Result: No Glitches

```
Transaction starts:
  Var(3) fires → rank 1
    Signal(*2) receives, marks pending → rank 2
    Signal(+10) receives, marks pending → rank 2
  
  Resolve queue (both at rank 2, arbitrary order):
    Signal(*2) fires 6 → combine receives, marks pending → rank 3
    Signal(+10) fires 13 → combine receives, marks pending → rank 3
    (combine already pending, just updates its inputs)
  
  Resolve queue (rank 3):
    combine fires (6, 13) ← CORRECT, no glitch
```

## SyncObservable

```scala
trait SyncObservable[A]:
  private[airstream] def syncFire(transaction: Transaction): Unit
```

Observables that participate in transaction ordering implement this trait.
Used by: CombineObservable, MergeStream, and other synchronous derivations.

## Transaction Creation

Transactions are created by:

```scala
// Explicit (rare in user code)
Transaction { trx => ... }

// Implicit (common)
myVar.set(42)              // creates transaction internally
eventBus.emit(value)       // creates transaction internally
Var.set(x -> 1, y -> 2)   // one transaction for both
```

## Transaction Depth Limit

```scala
Transaction.maxDepth = 1000  // default

// If exceeded:
AirstreamError.sendUnhandledError(TransactionDepthExceeded(...))
// Transaction is NOT executed
```

Prevents infinite loops from circular dependencies (e.g., two Vars that
update each other in their observers).

## Transaction.onStart.shared

Batch multiple observer additions:

```scala
Transaction.onStart.shared {
  signal1.addObserver(obs1)(owner)
  signal2.addObserver(obs2)(owner)
}
```

Without `shared`, each addObserver triggers its own initial-value emission.
With `shared`, they're batched so all observers see a consistent state.

## Merge and Transactions

When multiple streams merge and fire in the same transaction:

```scala
val merged = EventStream.merge(stream1, stream2)
```

If both `stream1` and `stream2` fire in one transaction:
1. First value fires to merged stream's observers
2. Second value fires in a NEW transaction
3. Observers always see one event per transaction from merge

This prevents "event loss" — both events are delivered, just sequentially.

## Async Boundaries

Some operators break the synchronous transaction:

```scala
stream.delay(100)       // fires in new transaction after 100ms
stream.debounce(300)    // fires in new transaction after 300ms silence
stream.throttle(1000)   // may fire in new transaction
```

After an async boundary, the value fires in a fresh transaction.
Topological ordering restarts from that point.

# Ownership Model

Airstream uses ownership-based memory management. Observables are lazy and
only live while observed. Owners control when subscriptions die.

## Core Types

### Owner

```scala
trait Owner:
  protected val subscriptions: JsArray[Subscription]
  protected def killSubscriptions(): Unit   // kill all owned subscriptions
  protected def onOwned(subscription: Subscription): Unit = ()  // hook
```

An Owner tracks all subscriptions created under it. When the owner is
destroyed, all its subscriptions are killed, which removes observers
from observables.

### Subscription

```scala
class Subscription(owner: Owner, cleanup: () => Unit):
  def kill(): Unit          // remove observer, cleanup
  def isKilled: Boolean     // monotonic — once killed, stays killed
```

A Subscription is the link between an observer and an observable.
It belongs to exactly one Owner and cannot be transferred.

### DynamicOwner

```scala
class DynamicOwner:
  def activate(): Unit      // start all dynamic subscriptions
  def deactivate(): Unit    // stop all dynamic subscriptions
  def isActive: Boolean
```

Unlike regular Owner (destroy once), DynamicOwner can be activated and
deactivated multiple times. Used for UI components that mount/unmount.

### DynamicSubscription

```scala
class DynamicSubscription(
  dynamicOwner: DynamicOwner,
  activate: Owner => Subscription
):
  // Created when dynamicOwner.activate() is called
  // Killed when dynamicOwner.deactivate() is called
```

## Lifecycle Flow

```
1. observable.addObserver(observer)(owner)
   │
   ├── Creates Subscription(owner, cleanup = removeObserver)
   ├── Adds subscription to owner.subscriptions
   ├── Adds observer to observable.externalObservers
   ├── Starts observable chain (if first observer)
   └── Returns Subscription

2. Owner is destroyed (e.g., component unmounts)
   │
   ├── owner.killSubscriptions()
   │   └── For each subscription: subscription.kill()
   │       ├── Calls cleanup() → removes observer from observable
   │       └── Removes subscription from owner
   │
   └── Observable may stop (if no observers remain)
       └── Stops parent chain recursively
```

## Start/Stop Lifecycle of Observables

```
Observable STARTS when:
  - First external observer added (via addObserver + owner)
  - First internal observer added (child observable starts)

Observable STOPS when:
  - Last observer removed (both external and internal)
  - All children stopped AND all user observers killed

On START:
  1. onWillStart() — recursive up parent chain, syncs values
  2. onStart() — adds internal observer to parents

On STOP:
  1. onStop() — removes internal observer from parents
  2. Resets willStartDone flag
```

## Memory Management

### What keeps an observable alive

An observable is garbage-collectible when:
- No external observers (all subscriptions killed)
- No child observables observing it (all children stopped)
- No user-held references

### Common memory leak patterns

```scala
// LEAK: observer created but never killed
observable.addObserver(observer)(owner)
// If `owner` is never destroyed, subscription lives forever

// SAFE: use DynamicOwner tied to component lifecycle
val dynOwner = new DynamicOwner
// Activate on mount, deactivate on unmount
```

### Owner implementations

| Owner | Lifecycle | Use case |
|-------|-----------|----------|
| OneTimeOwner | Kill once, cannot reuse | Simple scope |
| ManualOwner | Kill manually when done | Tests, scripts |
| DynamicOwner | Activate/deactivate repeatedly | UI components |

## Usage Patterns

### Basic subscription

```scala
implicit val owner: Owner = new ManualOwner

val sub: Subscription = signal.foreach(value => println(value))

// Later:
sub.kill()           // or owner.killSubscriptions()
```

### With Laminar (typical usage)

In Laminar, each element has a DynamicOwner that activates when the
element is mounted to the DOM and deactivates when unmounted:

```scala
div(
  // This observer lives as long as the div is mounted:
  signal --> observer
  // Equivalent to: signal.addObserver(observer)(element's dynamic owner)
)
```

### TransferableSubscription

```scala
class TransferableSubscription(
  activate: () => Unit,
  deactivate: () => Unit
):
  def setOwner(owner: DynamicOwner): Unit
  def clearOwner(): Unit
```

Allows moving a subscription between owners without killing/recreating.
Used internally by Laminar for element re-parenting.

## Transaction.onStart.shared

When adding multiple observers that should "see" the same initial state:

```scala
Transaction.onStart.shared {
  signal1.addObserver(obs1)(owner)
  signal2.addObserver(obs2)(owner)
  // Both observers receive initial values in the same transaction batch
}
```

Without `shared`, each `addObserver` might trigger intermediate states
that the other observer hasn't yet observed.

# Core Concepts

## Type Hierarchy

```
BaseObservable[Self[+_], +A]
├── Observable[+A]  (type alias for BaseObservable[Observable, A])
│   ├── EventStream[+A]    — no current value, fires discrete events
│   └── Signal[+A]         — always has a current value, fires updates
│
├── WritableObservable[A]  — can fire values to observers
│   ├── WritableStream[A]  — concrete writable event stream
│   └── WritableSignal[A]  — concrete writable signal with cached value

Source[+A]   — something that produces values (Observable or EventBus)
Sink[-A]     — something that consumes values (Observer)
```

## Key Distinction: Signal vs EventStream

| | Signal | EventStream |
|---|---|---|
| Current value | Always has one (Try[A]) | Never |
| Initial value | Required (from parent or explicit) | N/A |
| Starts with | Emits current value to new observers | Does not emit on subscribe |
| Semantics | Continuous state | Discrete events |
| Laziness | Lazy — evaluates only when observed | Lazy |

## Laziness Model

Observables are **lazy**: they only compute values when someone is observing.

```
Signal A ──map──> Signal B ──map──> Signal C
                                       │
                                   Observer (via owner)
```

- Signal C starts because it has an observer
- Signal C starting causes Signal B to start (adds internal observer)
- Signal B starting causes Signal A to start
- When the observer is killed (owner destroyed), the chain reverses:
  - C stops → removes internal observer from B → B stops → A stops

## Self Type Pattern

`BaseObservable[Self[+_], +A]` uses the Self type to preserve the concrete
type through operator chains:

```scala
val stream: EventStream[Int] = ???
val mapped: EventStream[String] = stream.map(_.toString)  // NOT Observable[String]

val signal: Signal[Int] = ???
val mapped: Signal[String] = signal.map(_.toString)  // NOT Observable[String]
```

This works because operators are defined on `BaseObservable` with Self-typed
return types, and `EventStream` / `Signal` provide the concrete Self.

## Observer

```scala
trait Observer[-A]:
  def onNext(nextValue: A): Unit
  def onError(nextError: Throwable): Unit
  def onTry(nextValue: Try[A]): Unit
```

Observers are contravariant — an `Observer[Animal]` can observe a `Signal[Cat]`.

**Contract:** Observer callbacks must not throw. Exceptions in observers are
caught and sent to `AirstreamError.sendUnhandledError`.

### Observer Operators

```scala
observer.contramap[B](project: B => A): Observer[B]
observer.contracollect[B](pf: PartialFunction[B, A]): Observer[B]
observer.filter(passes: A => Boolean): Observer[A]
observer.delay(ms: Int): Observer[A]
Observer.combine[A](observers: Observer[A]*): Observer[A]
```

## Internal vs External Observers

- **External observers:** User-created via `observable.addObserver(obs)(owner)`.
  Managed by Owner/Subscription lifecycle.
- **Internal observers:** Created by child observables to listen to parents.
  Managed by start/stop lifecycle. Not visible to users.

A WritableObservable fires to both lists. Internal observers receive the
Transaction object for synchronous propagation.

## Named Trait

All observables can carry a debug name:

```scala
trait Named:
  protected var maybeDisplayName: js.UndefOr[String]
  def setDisplayName(name: String): this.type
  def displayName: String  // defaults to class + hashcode
```

# Conventions

## Error Handling

- Errors are `Try[A]` values, not thrown exceptions
- User callbacks (map, filter, etc.) are wrapped — thrown exceptions become errors in the stream
- Observer.onNext and Observer.onError must never throw
- Unhandled errors go to `AirstreamError.sendUnhandledError`
- Register error callbacks: `AirstreamError.registerUnhandledErrorCallback(err => ...)`
- A Signal can be in error state: `signal.tryNow() == Failure(error)`

## Naming Conventions

| Method | Meaning |
|--------|---------|
| `now()` | Get current value (throws if error) |
| `tryNow()` | Get current value as Try |
| `signal` | Access the read-only signal of a Var |
| `writer` | Access the write-only observer of a Var |
| `events` | Access the stream from an EventBus |
| `updates` | Stream of signal changes (no initial value) |
| `addObserver` | Subscribe (requires Owner) |
| `foreach` | Shorthand for addObserver with onNext |

## Type Signatures

### Covariance / Contravariance

```scala
Observable[+A]    — covariant (producer)
Signal[+A]        — covariant
EventStream[+A]   — covariant
Observer[-A]      — contravariant (consumer)
Sink[-A]          — contravariant
Var[A]            — invariant (read + write)
```

### Self-typed operators

Operators preserve the concrete type:
- `signal.map(f)` returns `Signal[B]`, not `Observable[B]`
- `stream.filter(p)` returns `EventStream[A]`, not `Observable[A]`

This is achieved via the Self type parameter in `BaseObservable[Self[+_], A]`.

## Lifecycle Rules

1. **Observables are lazy.** No computation happens without an observer.
2. **Ownership is mandatory.** Every `addObserver` requires an implicit Owner.
3. **Subscriptions are monotonic.** Once killed, cannot be restarted.
4. **DynamicOwner for mount/unmount.** Use when lifecycle is not one-shot.
5. **Strict signals for .now() access.** Only `StrictSignal` (from Var) guarantees `.now()` always works.

## Performance Guidelines

1. **Prefer Signal over Stream + startWith** when you need current value semantics
2. **Use split for lists** — avoids re-rendering unchanged items
3. **Use .distinct** on streams that may emit duplicates
4. **Tests on JVM** — Airstream is Scala.js-only but the reactive patterns are testable via abstractions
5. **Avoid deep flatMap chains** — each level adds topoRank depth

## Import Patterns

```scala
import com.raquo.airstream.core.*          // Observable, Signal, EventStream, Observer
import com.raquo.airstream.state.*          // Var, Val
import com.raquo.airstream.ownership.*      // Owner, Subscription
import com.raquo.airstream.eventbus.*       // EventBus
import com.raquo.airstream.combine.*        // combine operators
import com.raquo.airstream.flatten.*        // flatMap, flatten
import com.raquo.airstream.split.*          // split operators
import com.raquo.airstream.timing.*         // delay, throttle, debounce
import com.raquo.airstream.web.*            // fetch, websocket
```

## Key Differences from Other FRP Libraries

| Concept | Airstream | RxJS/RxScala | Cats Effect Streams |
|---------|-----------|--------------|---------------------|
| Memory | Ownership-based | Manual unsubscribe | Resource/Scope |
| Glitch-free | Transaction + topoRank | Not guaranteed | N/A (pull-based) |
| Laziness | Full (start/stop) | Lazy (subscribe) | Pull-based |
| Error model | Try[A] in graph | onError channel | MonadError |
| Backpressure | None (sync push) | Operators | Built-in (pull) |
| Platform | Scala.js only | Multi-platform | JVM/JS |

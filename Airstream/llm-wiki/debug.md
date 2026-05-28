---
id: airstream-debug
title: "Debugging"
category: concept
tags: [debug, debugger, spy, log, breakpoint]
source_files:
  - /p/gh/Airstream/src/main/scala/com/raquo/airstream/debug/Debugger.scala
  - /p/gh/Airstream/src/main/scala/com/raquo/airstream/debug/DebuggableObservable.scala
  - /p/gh/Airstream/src/main/scala/com/raquo/airstream/debug/DebuggerObservable.scala
source_commit: 781abe8
related: [airstream-concepts, airstream-operators]
see_also: [airstream-conventions]
---

# Debugging

Airstream provides a non-intrusive debugging system. Debug operators create
wrapper observables that intercept events for logging, spying, or breakpoints,
then forward everything unchanged to downstream subscribers.

## Debugger Case Class

The core building block. All debug operators ultimately construct a `Debugger`:

```scala
case class Debugger[-A](
  onStart: () => Unit = () => (),
  onStop: () => Unit = () => (),
  onFire: Try[A] => Unit = (_: Try[A]) => (),
  onEvalFromParent: Try[A] => Unit = (_: Try[A]) => ()  // signals only
)
```

- `onFire` -- called on every emitted event or error
- `onStart` / `onStop` -- called on lifecycle transitions
- `onEvalFromParent` -- signal-specific, fires when initial value is evaluated or when re-syncing after restart

## Debug Operators on Observables

All operators return a new observable of the same type. Chain them and use
the result in place of the original.

### Naming

```scala
stream.debugWithName("MyStream").debugLog()
// logs as: MyStream [event]: <value>

// vs setDisplayName which appends |Debug suffix:
stream.setDisplayName("MyStream").debugLog()
// logs as: MyStream|Debug [event]: <value>
```

### Spy (custom callbacks)

```scala
// All events and errors (Try[A])
stream.debugSpy(v => println(s"got: $v"))

// Events only
stream.debugSpyEvents(ev => println(s"event: $ev"))

// Errors only
stream.debugSpyErrors(err => println(s"error: $err"))

// Lifecycle
stream.debugSpyLifecycle(
  startFn = topoRank => println(s"started at rank $topoRank"),
  stopFn = () => println("stopped")
)
stream.debugSpyStarts(rank => println(s"started at $rank"))
stream.debugSpyStops(() => println("stopped"))
```

### Log (println / console.log)

```scala
// Log all events and errors
stream.debugLog()

// Log with condition
stream.debugLog(when = {
  case Success(v) => v > 10
  case _ => true
})

// Log events only (skip errors)
stream.debugLogEvents()

// Log errors only
stream.debugLogErrors()

// Use dom.console.log for JS objects (renders better in devtools)
stream.debugLogEvents(useJsLogger = true)

// Log lifecycle
stream.debugLogLifecycle()
stream.debugLogStarts
stream.debugLogStops
```

Output format: `displayName [action]: value`

### Break (JS debugger)

Triggers `js.special.debugger()` -- pauses execution in browser devtools:

```scala
stream.debugBreak()                          // all events + errors
stream.debugBreakEvents(when = _ == "bug")   // conditional on events
stream.debugBreakErrors()                    // errors only
stream.debugBreakLifecycle                   // start + stop
stream.debugBreakStarts                      // start only
stream.debugBreakStops                       // stop only
```

## Signal-Specific Operators

Signals have additional operators for observing initial value evaluation:

```scala
signal.debugSpyEvalFromParent(v => println(s"init eval: $v"))
signal.debugLogEvalFromParent()
signal.debugBreakEvalFromParent()
```

These fire when `currentValueFromParent` is called: on first start, and on
re-start when re-syncing with the parent's current value.

## Observer Debugging

Observers also support debug operators. They create a wrapper observer that
runs the debug callback then forwards to the original:

```scala
observer.debugWithName("MyObs").debugLog()
observer.debugSpy(v => println(s"observed: $v"))
observer.debugSpyEvents(ev => println(s"event: $ev"))
observer.debugSpyErrors(err => println(s"err: $err"))
observer.debugLog()
observer.debugLogEvents()
observer.debugLogErrors()
observer.debugBreak()
observer.debugBreakEvents()
observer.debugBreakErrors()
```

Note: observer debug methods require explicit type parameters due to
inference limitations.

## Internals

- `DebuggerStream` / `DebuggerSignal` -- wrapper observables that intercept
  fire/start/stop and delegate to the `Debugger` callbacks
- Display name: chained debug wrappers inherit the parent's name instead of
  appending repeated `|Debug` suffixes
- Errors in debug callbacks are caught and sent to `AirstreamError.sendUnhandledError`
  as `DebugError`, so a buggy debugger never crashes the reactive graph

## Practical Tips

```scala
// Chain multiple debuggers:
stream
  .debugWithName("clicks")
  .debugLogEvents()
  .debugSpyStarts(_ => println("someone is listening"))

// Quick inspect with topoRank (no side effects):
val rank: Int = stream.debugTopoRank

// Temporary debugging during development:
val debugStream = stream.debugLog()
// use debugStream everywhere instead of stream, remove when done
```

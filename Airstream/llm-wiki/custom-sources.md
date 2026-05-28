---
id: airstream-custom-sources
title: "Custom Sources"
category: concept
tags: [custom-source, custom-stream, custom-signal, external-integration]
source_files:
  - /p/gh/Airstream/src/main/scala/com/raquo/airstream/custom/CustomSource.scala
  - /p/gh/Airstream/src/main/scala/com/raquo/airstream/custom/CustomStreamSource.scala
  - /p/gh/Airstream/src/main/scala/com/raquo/airstream/custom/CustomSignalSource.scala
source_commit: 781abe8
related: [airstream-streams, airstream-signals, airstream-concepts]
see_also: [airstream-web]
---

# Custom Sources

Custom sources let you bridge external event systems into Airstream's
reactive graph. Use them when you need to wrap a callback-based API,
DOM event, WebSocket, or any push-based source as an EventStream or Signal.

## When to Use

- Wrapping browser APIs not covered by Laminar (e.g. ResizeObserver, IntersectionObserver)
- Integrating third-party JS libraries that use callbacks
- Creating streams from WebSocket messages
- Bridging any push-based external system into Airstream

For most DOM events, Laminar provides built-in bindings. Reach for
custom sources only when no built-in helper exists.

## CustomStreamSource

The primary API is `EventStream.fromCustomSource`:

```scala
EventStream.fromCustomSource[A](
  shouldStart: StartIndex => Boolean = _ => true,
  start: (FireValue[A], FireError, GetStartIndex, GetIsStarted) => Unit,
  stop: StartIndex => Unit
): EventStream[A]
```

### Parameters

| Parameter | Type | Purpose |
|-----------|------|---------|
| `shouldStart` | `StartIndex => Boolean` | Gate whether `start` runs on this activation. `StartIndex` is 1-based, incremented each start. |
| `start` | `(FireValue[A], FireError, GetStartIndex, GetIsStarted) => Unit` | Called when first observer subscribes. Set up your external listener here. |
| `stop` | `StartIndex => Unit` | Called when last observer unsubscribes. Tear down your listener. **Must not throw.** |

### Callback Arguments in `start`

| Callback | Type | Purpose |
|----------|------|---------|
| `fireValue` | `A => Unit` | Emit an event into the stream |
| `fireError` | `Throwable => Unit` | Emit an error into the stream |
| `getStartIndex` | `() => StartIndex` | How many times this source has been started (1-based) |
| `getIsStarted` | `() => Boolean` | Check if still active (useful in async callbacks) |

### Example: Wrapping ResizeObserver

```scala
def resizeStream(element: dom.Element): EventStream[dom.DOMRectReadOnly] = {
  var observer: dom.ResizeObserver = null
  EventStream.fromCustomSource[dom.DOMRectReadOnly](
    start = (fireValue, _, _, _) => {
      observer = new dom.ResizeObserver((entries, _) =>
        entries.foreach(e => fireValue(e.contentRect))
      )
      observer.observe(element)
    },
    stop = _ => {
      observer.disconnect()
      observer = null
    }
  )
}
```

### Example: One-Shot Emit with `shouldStart`

Airstream itself uses `fromCustomSource` for `EventStream.fromValue`:

```scala
EventStream.fromValue(event, emitOnce = true)
// Internally:
EventStream.fromCustomSource[A](
  shouldStart = startIndex => if (emitOnce) startIndex == 1 else true,
  start = (fireEvent, _, _, _) => fireEvent(event),
  stop = _ => ()
)
```

The `shouldStart` gate prevents re-emission when `emitOnce = true` and the
stream is restarted after being stopped.

## CustomSignalSource

The signal variant is `Signal.fromCustomSource`:

```scala
Signal.fromCustomSource[A](
  initial: => Try[A],
  start: (SetCurrentValue[A], GetCurrentValue[A], GetStartIndex, GetIsStarted) => Unit,
  stop: StartIndex => Unit
): Signal[A]
```

### Differences from Stream

- Requires an `initial` value (as `Try[A]`), since signals always have a current value.
- `start` receives `SetCurrentValue` and `GetCurrentValue` instead of `FireValue`/`FireError`.

| Callback | Type | Purpose |
|----------|------|---------|
| `setValue` | `Try[A] => Unit` | Update the signal's current value |
| `getValue` | `() => Try[A]` | Read the signal's current value |

### Example: Wrapping Window Size

```scala
val windowWidth: Signal[Int] = Signal.fromCustomSource[Int](
  initial = Success(dom.window.innerWidth.toInt),
  start = (setValue, _, _, _) => {
    dom.window.addEventListener("resize", (_: dom.Event) =>
      setValue(Success(dom.window.innerWidth.toInt))
    )
  },
  stop = _ => {
    // In production, store the listener reference to remove it here
  }
)
```

## Start/Stop Lifecycle

1. **First observer subscribes** -- `onWillStart()` fires, then `onStart()` runs your `start` callback.
2. **Source is active** -- call `fireValue`/`fireError` (stream) or `setValue` (signal) from external callbacks.
3. **Last observer unsubscribes** -- `onStop()` runs your `stop` callback. Clean up resources here.
4. **Re-subscription** -- `startIndex` increments. Use `shouldStart` (stream) or check `getStartIndex` to control re-activation behavior.

Errors thrown in `start` are caught and emitted as error events in the
observable via `Transaction(fireError(err, _))`.

The `stop` callback **must not throw** -- there is no error recovery path.

## CustomSource.Config

Under the hood, both APIs build a `CustomSource.Config`:

```scala
CustomSource.Config(
  onWillStart: () => Unit,  // pre-start hook (before transaction)
  onStart: () => Unit,      // main start
  onStop: () => Unit        // cleanup
)
```

The config supports a `.when(passes: () => Boolean)` combinator that
conditionally runs the start/stop cycle. `EventStream.fromCustomSource`
uses this internally to implement `shouldStart`:

```scala
Config(onStart = ..., onStop = ...).when(() => shouldStart(getStartIndex()))
```

If `when` returns false, `start` is skipped, and the corresponding `stop`
is also skipped on that cycle.

## Type Aliases

Defined in the `CustomSource` companion object:

```scala
type StartIndex     = Int
type FireValue[A]   = A => Unit
type FireError      = Throwable => Unit
type SetCurrentValue[A] = Try[A] => Unit
type GetCurrentValue[A] = () => Try[A]
type GetStartIndex  = () => StartIndex
type GetIsStarted   = () => Boolean
```

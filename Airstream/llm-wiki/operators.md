# Operators

## Map

```scala
observable.map(a => b)              // Observable[B]
observable.mapTo(value)             // Observable[B] (constant)
observable.mapRecover(tryA => tryB) // recover from errors during map
```

## Filter / Collect

```scala
stream.filter(a => boolean)                   // EventStream[A]
stream.filterNot(a => boolean)                // EventStream[A]
stream.collect { case pattern => value }      // EventStream[B]
stream.collectSome                            // EventStream[A] from EventStream[Option[A]]
```

Signals cannot be filtered (they must always have a value).

## Combine

### Tuple combining

```scala
Signal.combine(s1, s2)            // Signal[(A, B)]
Signal.combine(s1, s2, s3)       // Signal[(A, B, C)]
// up to N

stream.combineWith(s1, s2)        // EventStream[(A, B, C)]
// stream fires trigger; signals provide current values
```

### withCurrentValueOf / sample

```scala
stream.withCurrentValueOf(signal)   // EventStream[(A, B)]
// Emits (streamValue, signal.now()) when stream fires

stream.sample(signal)               // EventStream[B]
// Emits signal.now() when stream fires (drops stream value)
```

### combineWith for streams

```scala
stream1.combineWith(stream2)        // fires when EITHER fires
// Result includes latest values from both (signal-like semantics applied)
```

## Merge

```scala
EventStream.merge(s1, s2, s3)      // EventStream[A]
s1.mergeWith(s2, s3)               // same
```

All parent events forwarded. If multiple fire in same transaction,
each gets its own transaction (no event loss).

## FlatMap / Flatten

### Switch (latest wins)

```scala
signal.flatMapSwitch(a => otherSignal(a))     // Signal[B]
stream.flatMapSwitch(a => otherStream(a))     // EventStream[B]

// When parent emits, subscribe to new inner, unsubscribe from old
```

### Merge (all live)

```scala
stream.flatMapMerge(a => otherStream(a))      // EventStream[B]
// All inner streams stay active, all events forwarded
```

### Flatten

```scala
signalOfSignals.flatten           // Signal[A] (flatMapSwitch semantics)
streamOfStreams.flatten            // EventStream[A] (flatMapSwitch)
streamOfStreams.flattenMerge       // EventStream[A] (flatMapMerge)
```

## Split

Key-based memoized splitting for efficient list rendering:

```scala
signal.splitSeq(key = _.id) { (key, initialValue, valueSignal) =>
  // Called ONCE per unique key
  // valueSignal updates when this key's item changes
  renderItem(key, valueSignal)
}
// Returns Signal[List[Output]]
```

### Split variants

```scala
// Split by index (for ordered collections without stable keys)
signal.splitSeqByIndex { (index, initialValue, valueSignal) => ... }

// Split Option
signal.splitOption(
  (initialValue, valueSignal) => renderSome(valueSignal),
  ifEmpty = renderNone
)

// Split Boolean
signal.splitBoolean(
  whenTrue = (signal) => ...,
  whenFalse = (signal) => ...
)

// Split Either
signal.splitEither(
  left = (initialL, signalL) => ...,
  right = (initialR, signalR) => ...
)

// One-shot split (like splitOption for Signal[A])
signal.splitOne(key = identity) { (key, initial, valueSignal) => ... }
```

### How split memoization works

1. Parent signal emits new list
2. For each item, compute `key(item)`
3. If key was seen before → reuse existing child signal (update its value)
4. If key is new → call `project` once, create new child signal
5. If key disappeared → remove from cache (child signal stops)

Child signals have distinct applied — they only fire when THEIR key's
value changes, not when other items in the list change.

## Distinct

```scala
signal.distinct                              // default equality
signal.distinctBy(a => a.id)                 // by projection
signal.distinctByRef                         // reference equality
stream.distinct                              // same for streams
stream.distinctBy(a => key)
```

## Timing

```scala
stream.delay(ms)                    // delay each event
stream.throttle(ms)                 // max once per interval
stream.throttle(ms, leading = true) // emit first, then throttle
stream.debounce(ms)                 // wait for silence
```

## Take / Drop

```scala
stream.take(n)                      // first n events
stream.drop(n, resetOnStop)         // skip first n
stream.takeUntil(stopStream)        // take until stop fires
stream.dropUntil(startStream)       // drop until start fires
stream.takeWhile(predicate)         // take while true
stream.dropWhile(predicate)         // drop while true
```

## Error Recovery

```scala
observable.recover { case e: MyError => Some(fallback) }
observable.recoverIgnoreErrors       // silently drop errors
observable.recoverToTry              // Observable[Try[A]]
```

## Debug

```scala
observable.debugLog()                        // log all events
observable.debugLog("label")                 // log with label
observable.debugLogEvents                    // log values only
observable.debugLogErrors                    // log errors only
observable.debugSpy(value => sideEffect)     // custom debug
observable.debugBreak()                      // debugger breakpoint
```

## Type Extensions

```scala
// Option
signalOfOption.splitOption(some => ..., none)
streamOfOption.collectSome

// Boolean
signalOfBool.splitBoolean(whenTrue, whenFalse)

// Either
signalOfEither.splitEither(left, right)
```

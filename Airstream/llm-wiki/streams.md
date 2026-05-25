# EventStream

An EventStream has no current value. It fires discrete events to observers.

## EventStream Trait

```scala
trait EventStream[+A] extends Observable[A]:
  // Core operators
  def map[B](project: A => B): EventStream[B]
  def filter(passes: A => Boolean): EventStream[A]
  def collect[B](pf: PartialFunction[A, B]): EventStream[B]
  def delay(ms: Int): EventStream[A]
  def throttle(intervalMs: Int): EventStream[A]
  def debounce(ms: Int): EventStream[A]
  def take(numEvents: Int): EventStream[A]
  def drop(numEvents: Int, resetOnStop: Boolean): EventStream[A]
```

## Key Behaviors

### No Initial Value

When an observer subscribes to a stream, it receives nothing until the
next event fires. Unlike signals, there is no "current state."

### Re-emits Same Values

EventStream does NOT have distinct semantics by default. If the source
fires the same value twice, the stream emits it twice. Use `.distinct`
explicitly if needed.

### Laziness

Like signals, streams are lazy. An `EventStream.map(f)` only evaluates `f`
when someone is observing the mapped stream.

## Creating Streams

```scala
// From EventBus (user-writable source)
val bus = new EventBus[Int]
val stream: EventStream[Int] = bus.events
bus.emit(42)

// From signal changes
val stream: EventStream[Int] = signal.updates

// From other streams
stream.map(_ * 2)
stream.filter(_ > 0)
stream.collect { case x if x > 0 => x.toString }

// Merge multiple streams
EventStream.merge(stream1, stream2, stream3)

// From future/promise
EventStream.fromFuture(myFuture)
EventStream.fromJsPromise(myPromise)

// Periodic
EventStream.periodic(intervalMs = 1000)
```

## WritableStream

```scala
trait WritableStream[A] extends EventStream[A] with WritableObservable[A]:
  protected def fireValue(nextValue: A, transaction: Transaction): Unit =
    // Fire to all external + internal observers in this transaction
  protected def fireError(nextError: Throwable, transaction: Transaction): Unit
```

## Merge

Merge multiple streams into one:

```scala
EventStream.merge(stream1, stream2, stream3): EventStream[A]
// or
stream1.mergeWith(stream2, stream3): EventStream[A]
```

If multiple parents fire in the same transaction, merge fires each value
in a separate transaction (ordered by topoRank of parents).

## Filter / Collect

```scala
stream.filter(x => x > 0)              // only positive values
stream.collect { case Some(x) => x }   // unwrap Options
stream.filterNot(x => x < 0)           // exclude negatives
```

## Delay / Throttle / Debounce

```scala
stream.delay(500)         // delay each event by 500ms
stream.throttle(1000)     // at most one event per 1000ms (first wins)
stream.debounce(300)      // wait 300ms of silence before emitting last value
```

## Take / Drop

```scala
stream.take(5)                          // first 5 events only
stream.drop(3, resetOnStop = false)     // skip first 3 events
stream.takeUntil(stopStream)            // take until another stream fires
stream.dropUntil(startStream)           // drop until another stream fires
```

## withCurrentValueOf / sample

Combine stream events with signal state:

```scala
stream.withCurrentValueOf(signal)       // EventStream[(A, B)]
stream.sample(signal)                   // EventStream[B] (stream triggers, signal provides value)
```

## startWith (convert to Signal)

```scala
stream.startWith(initialValue)          // Signal[A]
stream.startWithNone                    // Signal[Option[A]]
```

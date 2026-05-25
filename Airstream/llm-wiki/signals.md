# Signals

A Signal always has a current value (`Try[A]`). It represents continuous
state that changes over time.

## Signal Trait

```scala
trait Signal[+A] extends Observable[A]:
  def tryNow(): Try[A]           // current value (may evaluate lazily)
  def now(): A                   // current value or throw

  // Derived signals
  def map[B](project: A => B): Signal[B]
  def compose[B](operator: Signal[A] => Signal[B]): Signal[B]
  def composeUpdates[B](operator: EventStream[A] => EventStream[B], initial: => B): Signal[B]
  def scanLeft[B](makeInitial: A => B)(fn: (B, A) => B): Signal[B]
  def updates: EventStream[A]    // stream of changes (no initial)
```

## WritableSignal

Adds value storage and fire semantics:

```scala
trait WritableSignal[A] extends Signal[A] with WritableObservable[A]:
  protected var maybeLastSeenCurrentValue: js.UndefOr[Try[A]]

  protected def setCurrentValue(newValue: Try[A]): Unit
  protected def currentValueFromParent(): Try[A]

  // Lazy evaluation: first access computes from parent and caches
  override protected def tryNow(): Try[A] =
    maybeLastSeenCurrentValue.getOrElse {
      val nextValue = currentValueFromParent()
      setCurrentValue(nextValue)
      nextValue
    }
```

## StrictSignal

A signal that maintains its current value even when not observed:

```scala
trait StrictSignal[+A] extends Signal[A]:
  // Always has a current value (no lazy evaluation)
  // Used for Var.signal, exposed to users for .now() access
```

## Key Behaviors

### Lazy Evaluation

Signal values are computed lazily. A signal only evaluates `currentValueFromParent()`
when:
1. An observer is added (triggering `onWillStart`)
2. `.tryNow()` / `.now()` is called directly on a StrictSignal

### Change Detection

Signals track updates via `lastUpdateId`. A signal only re-evaluates when
its parent's `lastUpdateId` has changed since last check:

```scala
protected var _parentLastUpdateId: Int = -1

override protected def onWillStart(): Unit =
  Protected.maybeWillStart(parent)
  if peekWhetherParentHasUpdated().contains(true) then
    updateCurrentValueFromParent(currentValueFromParent(), ...)
```

### New Observer Semantics

When a new external observer is added to a signal:
- The observer immediately receives the signal's current value
- This happens synchronously during `addObserver`

### Distinct by Default

Signals do NOT re-emit the same value by default (unlike EventStream).
The `.distinct` operator is often implicitly applied in split operations.

## SingleParentSignal

The most common signal implementation base:

```scala
trait SingleParentSignal[I, O] extends WritableSignal[O]:
  protected val parent: Observable[I]

  // Subclass implements this:
  protected def currentValueFromParent(): Try[O]

  // When parent emits, update our value and fire to observers:
  override protected def onTry(nextParentValue: Try[I], transaction: Transaction): Unit
```

Used by: MapSignal, DistinctSignal, SplitChildSignal, SignalFromStream

## Creating Signals

```scala
// From initial value
Val(42)                                    // constant signal
Signal.fromValue(42)                       // same as Val

// From stream + initial
stream.startWith(initial)                  // Signal from EventStream
stream.startWithNone                       // Signal[Option[A]] starting with None

// From Var
val myVar = Var(0)
myVar.signal                               // StrictSignal[Int]

// Derived
signal.map(_ * 2)                          // Signal[Int]
Signal.combine(sig1, sig2)                 // Signal[(A, B)]
signal.flatMapSwitch(a => otherSignal)     // Signal[B] (switches on change)
```

## Signal.combine

Combine multiple signals into a tuple signal:

```scala
Signal.combine(s1, s2)         // Signal[(A, B)]
Signal.combine(s1, s2, s3)    // Signal[(A, B, C)]
// up to Signal.combineN for N signals
```

Fires when ANY input signal updates. All inputs must have values before
the combined signal emits.

## signal.updates

Convert signal changes to a stream (drops the initial value):

```scala
val stream: EventStream[Int] = signal.updates
// Emits only when signal value changes, not on initial subscribe
```

## signal.composeUpdates

Apply a stream operator to a signal's updates while keeping signal semantics:

```scala
signal.composeUpdates(_.throttle(100), signal.now())
// Returns Signal[A] that throttles updates but keeps current value
```

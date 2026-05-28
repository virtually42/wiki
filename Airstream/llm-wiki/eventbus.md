---
id: airstream-eventbus
title: "EventBus"
category: concept
tags: [eventbus, writebus, emit, component-communication]
source_files:
  - /p/gh/Airstream/src/main/scala/com/raquo/airstream/eventbus/EventBus.scala
  - /p/gh/Airstream/src/main/scala/com/raquo/airstream/eventbus/WriteBus.scala
  - /p/gh/Airstream/src/main/scala/com/raquo/airstream/eventbus/EventBusStream.scala
source_commit: 781abe8
related: [airstream-streams, airstream-concepts]
see_also: [airstream-patterns]
---

# EventBus

A writable event stream source. EventBus is the primary way to push events into the Airstream observable graph imperatively. It pairs a `WriteBus` (write side) with an `EventStream` (read side), allowing permission separation -- you can hand out only the writer or only the stream.

## EventBus API

```scala
class EventBus[A] extends EventSource[A] with Sink[A]:
  val writer: WriteBus[A]            // write-only handle (is an Observer[A])
  val events: EventStream[A]        // read-only stream of emitted events
  val stream: EventStream[A]        // alias for events

  def emit(event: A): Unit          // push a value (delegates to writer.onNext)
  def emitTry(event: Try[A]): Unit  // push a Try (delegates to writer.onTry)

  def toObservable: EventStream[A]  // EventSource implementation
  def toObserver: Observer[A]       // Sink implementation
```

### Creating and using an EventBus

```scala
val bus = EventBus[Int]()

// Emit events
bus.emit(42)
bus.emitTry(Success(1))
bus.emitTry(Failure(new Exception("oops")))

// Read events
bus.events.foreach(println)(_)

// Pass writer to code that should only write
def acceptClicks(sink: WriteBus[Int]): Unit =
  sink.onNext(1)
acceptClicks(bus.writer)
```

### Important: events only fire when observed

`WriteBus.onNext` checks `stream.isStarted` before firing. If no one is observing `bus.events`, emitted values are silently dropped.

## WriteBus API

`WriteBus[A]` extends `Observer[A]`. It is the write side of an EventBus.

```scala
class WriteBus[A] extends Observer[A]:
  // Core write methods (from Observer)
  def onNext(nextValue: A): Unit
  def onError(nextError: Throwable): Unit
  def onTry(nextValue: Try[A]): Unit

  // Add a source stream whose events feed into this bus
  def addSource(sourceStream: EventStream[A])(implicit owner: Owner): Subscription

  // Derived write buses (require Owner for lifecycle)
  def contramapWriter[B](project: B => A)(implicit owner: Owner): WriteBus[B]
  def contracomposeWriter[B](operator: EventStream[B] => EventStream[A])(implicit owner: Owner): WriteBus[B]
  def filterWriter(passes: A => Boolean)(implicit owner: Owner): WriteBus[A]
```

### addSource

Pipes all events from an existing stream into the bus. The subscription is tied to an `Owner` for lifecycle management.

```scala
val bus = EventBus[String]()
val clickStream: EventStream[String] = ???

// clickStream events now also appear in bus.events
val sub = bus.writer.addSource(clickStream)(owner)

// Remove the source manually:
sub.kill()
```

### contramapWriter / contracomposeWriter

Create a derived `WriteBus` that transforms values before they reach the parent bus.

```scala
val intBus = EventBus[Int]()
val stringBus: WriteBus[String] = intBus.writer.contramapWriter(_.toInt)(owner)

stringBus.onNext("42")  // intBus receives 42
```

## Static Multi-Bus Emission

Emit into multiple buses in a single transaction. This guarantees all downstream observers see a consistent snapshot.

```scala
val bus1 = EventBus[Int]()
val bus2 = EventBus[String]()

// All emissions happen in one transaction:
EventBus.emit(bus1 -> 1, bus2 -> "hello")
EventBus.emitTry(bus1 -> Success(1), bus2 -> Failure(new Exception("err")))
```

The same API exists on `WriteBus`:

```scala
WriteBus.emit(bus1.writer -> 1, bus2.writer -> "hello")
WriteBus.emitTry(bus1.writer -> Success(1), bus2.writer -> Failure(err))
```

Duplicate bus entries throw an exception -- an observable cannot emit more than one event per transaction.

## EventBusStream (Internal)

`EventBusStream[A]` is the internal `WritableStream` backing every `WriteBus`. It:

- Maintains a `JsArray[EventStream[A]]` of source streams added via `addSource`
- Subscribes to sources when started, unsubscribes when stopped
- Creates a new `Transaction` for each event (unless using shared-transaction batch emit)
- Has `topoRank = 1` (near the top of the topological ordering)

Not part of the public API -- exposed only within the `eventbus` package.

## Patterns

### Component communication

Pass only the `writer` to child components, keep the `events` stream in the parent:

```scala
val actionBus = EventBus[Action]()

// Child only gets write access:
def childComponent(actions: WriteBus[Action]) =
  button(onClick.mapTo(Action.Submit) --> actions)

// Parent observes all actions:
actionBus.events.foreach(handleAction(_))(owner)
```

### Event delegation

Merge multiple event sources into a single bus:

```scala
val bus = EventBus[DomEvent]()

bus.writer.addSource(clickStream)(owner)
bus.writer.addSource(keyStream.map(_.asInstanceOf[DomEvent]))(owner)

bus.events.foreach(handleEvent(_))(owner)
```

### Coordinated state updates

Use `EventBus.emit` to update multiple pieces of state atomically:

```scala
val selectedBus = EventBus[ItemId]()
val detailBus = EventBus[Detail]()

// Both fire in the same transaction:
EventBus.emit(selectedBus -> itemId, detailBus -> detail)
```

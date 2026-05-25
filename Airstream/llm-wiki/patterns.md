# Common Patterns

## Reactive Form State

```scala
case class FormData(name: String, email: String)
val formVar = Var(FormData("", ""))

// Lens into fields
val nameVar = formVar.zoom(_.name)((f, n) => f.copy(name = n))
val emailVar = formVar.zoom(_.email)((f, e) => f.copy(email = e))

// Derived validation (read-only)
val isValid: Signal[Boolean] = formVar.signal.map { form =>
  form.name.nonEmpty && form.email.contains("@")
}
```

## List Rendering with Split

```scala
case class Todo(id: Int, text: String, done: Boolean)
val todosVar = Var(List.empty[Todo])

// Efficient rendering — each todo gets its own signal
todosVar.signal.splitSeq(_.id) { (id, initial, todoSignal) =>
  div(
    text <-- todoSignal.map(_.text),
    cls.toggle("done") <-- todoSignal.map(_.done),
    onClick --> { _ =>
      todosVar.update(_.map(t =>
        if t.id == id then t.copy(done = !t.done) else t
      ))
    }
  )
}
```

## Loading State

```scala
sealed trait LoadState[+A]
case object Loading extends LoadState[Nothing]
case class Loaded[A](value: A) extends LoadState[A]
case class Failed(error: Throwable) extends LoadState[Nothing]

val dataVar = Var[LoadState[Data]](Loading)

// Or use Airstream's built-in status tracking:
val response = EventStream.fromFuture(fetchData())
  .map(Loaded(_))
  .recover { case e => Some(Failed(e)) }
  .startWith(Loading)
```

## EventBus for Component Communication

```scala
val submitBus = new EventBus[FormData]

// Producer (form component)
submitBus.emit(formData)

// Consumer (parent component)
submitBus.events.foreach(data => handleSubmit(data))(owner)
```

## Derived State with Caching

```scala
// signal.map is already cached (won't recompute if not observed)
val expensive: Signal[Result] = input.signal.map(computeExpensive)

// For async derived state:
val asyncResult: Signal[Option[Result]] =
  input.signal
    .flatMapSwitch(input => EventStream.fromFuture(fetchResult(input)))
    .map(Some(_))
    .startWith(None)
```

## Coordinated Multi-Var Updates

```scala
val x = Var(0)
val y = Var(0)
val z = Var(0)

// All update atomically in one transaction:
Var.set(x -> 1, y -> 2, z -> 3)

// Or with updaters:
Var.update(
  x -> (_ + 1),
  y -> (_ * 2)
)
```

## Stream → Signal → Stream Round-Trip

```scala
// Stream with state accumulation
val clicks: EventStream[Unit] = ???
val clickCount: Signal[Int] = clicks.scanLeft(0)((count, _) => count + 1)
val countUpdates: EventStream[Int] = clickCount.updates
```

## Conditional Observation

```scala
// Only observe while condition is true
val active = Var(true)

// Using DynamicOwner
val dynOwner = new DynamicOwner
active.signal.foreach { isActive =>
  if isActive then dynOwner.activate()
  else dynOwner.deactivate()
}(outerOwner)

// Subscriptions under dynOwner live/die with `active`
```

## Error Propagation

```scala
// Errors propagate through the graph like values
val result = input.signal
  .map(parse)           // may throw → becomes error in signal
  .recover {
    case e: ParseError => Some(defaultValue)  // recover
    case _: FatalError => None                // don't recover (propagate)
  }
```

## Avoiding Infinite Loops

```scala
// DANGER: circular dependency
val a = Var(0)
val b = Var(0)
a.signal.foreach(v => b.set(v + 1))(owner)
b.signal.foreach(v => a.set(v + 1))(owner)  // infinite loop!
// Transaction.maxDepth will stop it after 1000 iterations

// SAFE: use unidirectional data flow
val source = Var(0)
val derived = source.signal.map(_ + 1)  // read-only derivation
```

## Testing with ManualOwner

```scala
val owner = new ManualOwner

val myVar = Var(0)
var observed = List.empty[Int]

myVar.signal.foreach(v => observed = observed :+ v)(owner)
// observed == List(0)  (initial value)

myVar.set(1)
// observed == List(0, 1)

owner.killSubscriptions()
myVar.set(2)
// observed == List(0, 1)  (no longer observing)
```

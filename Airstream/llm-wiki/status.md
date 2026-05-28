---
id: airstream-status
title: "Async Status Tracking"
category: concept
tags: [status, pending, resolved, async, loading-state]
source_files:
  - /p/gh/Airstream/src/main/scala/com/raquo/airstream/status/Status.scala
  - /p/gh/Airstream/src/main/scala/com/raquo/airstream/status/AsyncStatusObservable.scala
  - /p/gh/Airstream/src/main/scala/com/raquo/airstream/status/FlatMapStatusObservable.scala
source_commit: 781abe8
related: [airstream-operators, airstream-streams]
see_also: [airstream-patterns, airstream-extensions]
---

# Async Status Tracking

`Status[In, Out]` tracks whether an asynchronous operator has produced its
output for a given input. This is the canonical way to implement loading
indicators and pending-state UI in Airstream.

## Status ADT

```scala
sealed trait Status[+In, +Out]:
  def isResolved: Boolean
  def isPending: Boolean = !isResolved
  def mapInput[In2](project: In => In2): Status[In2, Out]
  def mapOutput[Out2](project: Out => Out2): Status[In, Out2]
  def fold[A](resolved: Resolved[In, Out] => A, pending: Pending[In] => A): A
  def toResolvedOption: Option[Resolved[In, Out]]
  def toPendingOption: Option[Pending[In]]
  def toResolvedInputOption: Option[In]
  def toResolvedOutputOption: Option[Out]
  def toPendingInputOption: Option[In]

case class Pending[+In](input: In) extends Status[In, Nothing]

case class Resolved[+In, +Out](input: In, output: Out, ix: Int)
    extends Status[In, Out]
```

- `Pending(input)` -- input received, waiting for output
- `Resolved(input, output, ix)` -- output received; `ix` is 1-based count of
  how many outputs this input has produced (starts at 1, increments for
  repeated emissions from the same input)

## WithStatus Operators

### delayWithStatus

```scala
val statusS: EventStream[Status[A, A]] = stream.delayWithStatus(ms = 500)
```

Wraps `stream.delay(ms)`. Emits `Pending(input)` immediately on each input,
then `Resolved(input, output, 1)` after the delay.

### throttleWithStatus

```scala
val statusS = stream.throttleWithStatus(ms = 300, leading = true)
```

Wraps `stream.throttle(ms, leading)`. Emits `Pending` for throttled inputs,
`Resolved` when the throttled output fires.

### debounceWithStatus

```scala
val statusS = stream.debounceWithStatus(ms = 300)
```

Wraps `stream.debounce(ms)`. Emits `Pending` on every input keystroke,
`Resolved` once the debounced output fires.

### flatMapWithStatus

Available on all observables (streams and signals):

```scala
val statusS: EventStream[Status[UserId, UserData]] =
  userIdStream.flatMapWithStatus(id => fetchUser(id))
```

Uses `flatMapSwitch` internally -- a new input cancels the previous inner
stream. Emits `Pending(input)` on each input, then `Resolved(input, output, ix)`
for each output from the inner stream.

Shorthand for constant inner stream:

```scala
val statusS = clickStream.flatMapWithStatus(fetchData())
```

## How It Works (AsyncStatusObservable)

```
parent ──map──> inputS ──operator──> outputS
                  │                     │
                  ▼                     ▼
              Pending(in)     Resolved(in, out, ix)
                  │                     │
                  └────── merge ────────┘
                            │
                            ▼
                   Status[In, Out] stream
```

1. Each input resets the output counter `ix` to 0
2. Input is mapped to `Pending(input)` and merged with operator output
3. Operator output is mapped to `Resolved(lastInput, output, ++ix)`
4. Works for both streams and signals (signals use `.changes` then merge)

`FlatMapStatusObservable` works similarly but uses `flatMapSwitch` on the
pending stream instead of applying an operator to a separate input stream.

## Folding on Status

```scala
// Pattern match
statusSignal.map {
  case Pending(input) => s"Loading $input..."
  case Resolved(_, output, _) => s"Got: $output"
}

// fold method
statusSignal.map(_.fold(
  resolved = r => s"Done: ${r.output}",
  pending = p => s"Loading: ${p.input}"
))

// Map just input or output
statusSignal.map(_.mapOutput(_.toString))
statusSignal.map(_.mapInput(_.id))
```

## Patterns

### Loading indicator

```scala
val requestStatus = buttonClickStream.flatMapWithStatus(_ => fetchData())

// In UI:
div(
  child <-- requestStatus.map {
    case Pending(_) => spinner()
    case Resolved(_, data, _) => renderData(data)
  }
)
```

### Disable button while pending

```scala
val isPending: Signal[Boolean] = requestStatus.map(_.isPending).startWith(false)

button(
  disabled <-- isPending,
  "Submit"
)
```

### Debounced search with loading state

```scala
val searchStatus = searchInput
  .events(onInput.mapToValue)
  .debounceWithStatus(ms = 300)

div(
  child <-- searchStatus.map {
    case Pending(_) => div("Searching...")
    case Resolved(query, results, _) => renderResults(query, results)
  }.startWith(div("Type to search"))
)
```

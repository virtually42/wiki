---
id: airstream-extensions
title: "Type Extensions"
category: operator
tags: [option, boolean, either, try, status, tuple, extensions]
source_files:
  - /p/gh/Airstream/src/main/scala/com/raquo/airstream/extensions/
source_commit: 781abe8
related: [airstream-operators, airstream-status]
see_also: [airstream-patterns]
---

# Type Extensions

Implicit extension classes that add type-specific operators to observables
carrying `Option`, `Boolean`, `Either`, `Try`, `Status`, tuples, or nested
observables. Available on both streams and signals unless noted otherwise.

## Option Extensions

### OptionObservable (streams + signals)

```scala
val obs: Observable[Option[User]] = ...

obs.mapSome(_.name)              // Observable[Option[String]]
obs.mapFilterSome(_.isActive)    // Observable[Option[User]]
obs.foldOption("none")(_.name)   // Observable[String]
obs.mapToRight("missing")        // Observable[Either[String, User]]
obs.mapToLeft("present")         // Observable[Either[User, String]]
```

### OptionStream (streams only)

```scala
val stream: EventStream[Option[User]] = ...

stream.collectSome                      // EventStream[User] -- drop Nones
stream.collectSome { case u if u.isActive => u.name }  // with partial function
```

### splitOption (streams, signals, and Vars)

```scala
// With fallback for None:
optionSignal.splitOption(
  project = (initial, signal) => renderUser(initial, signal),
  ifEmpty = renderEmpty()
)  // Signal[Element]

// Without fallback (wraps output in Option):
optionSignal.splitOption(
  (initial, signal) => renderUser(initial, signal)
)  // Signal[Option[Element]]

// On Var[Option[A]] -- project receives Var[A] for two-way binding:
optionVar.splitOption(
  project = (initial, userVar) => renderEditableUser(initial, userVar),
  ifEmpty = renderEmpty()
)  // Signal[Element]
```

`splitOption` uses `split` internally, keyed on `isDefined`. The `project`
callback is re-invoked only when switching between `Some` and `None`.
Consecutive `None` values are deduplicated.

## Boolean Extensions

### BooleanObservable (streams + signals)

```scala
val obs: Observable[Boolean] = ...

obs.invert           // Observable[Boolean] -- logical NOT
obs.not              // alias for invert
obs.foldBoolean(
  whenTrue = "yes",
  whenFalse = "no"
)                    // Observable[String]
```

### splitBoolean (streams + signals)

```scala
boolSignal.splitBoolean(
  whenTrue = signal => div("Active", opacity <-- signal.mapToUnit.mapTo(1.0)),
  whenFalse = signal => div("Inactive")
)  // Signal[Element]
```

Re-invokes the callback only on true/false transitions. The inner `Signal[Unit]`
emits on every consecutive same-value event.

## Either Extensions

### EitherObservable (streams + signals)

```scala
val obs: Observable[Either[Error, User]] = ...

obs.mapRight(_.name)            // Observable[Either[Error, String]]
obs.mapLeft(_.message)          // Observable[Either[String, User]]
obs.foldEither(
  left = _.message,
  right = _.name
)                               // Observable[String]
obs.swap                        // Observable[Either[User, Error]]
obs.mapToOption                 // Observable[Option[User]]   (Right -> Some)
obs.mapLeftToOption             // Observable[Option[Error]]  (Left -> Some)
```

### EitherThrowableObservable (Either[Throwable, B])

```scala
val obs: Observable[Either[Throwable, User]] = ...

obs.recoverLeft(err => defaultUser)  // Observable[User]
obs.throwLeft                        // Observable[User] -- re-throws Left as error
```

### EitherStream (streams only)

```scala
stream.collectLeft                   // EventStream[Error]
stream.collectRight                  // EventStream[User]
stream.collectLeft { case e: NotFoundError => e }   // with partial function
stream.collectRight { case u if u.isAdmin => u }
```

### splitEither (streams + signals)

```scala
eitherSignal.splitEither(
  left = (initialErr, errSignal) => renderError(initialErr, errSignal),
  right = (initialUser, userSignal) => renderUser(initialUser, userSignal)
)  // Signal[Element]
```

Keyed on `isRight`. Re-invokes callback only when switching between
`Left` and `Right`.

## Try Extensions

### TryObservable (streams + signals)

```scala
val obs: Observable[Try[User]] = ...

obs.mapSuccess(_.name)                     // Observable[Try[String]]
obs.mapFailure(err => new WrappedError(err))  // Observable[Try[User]]
obs.foldTry(
  failure = _.getMessage,
  success = _.name
)                                          // Observable[String]
obs.mapToEither                            // Observable[Either[Throwable, User]]
obs.mapToEither(err => err.getMessage)     // Observable[Either[String, User]]
obs.recoverFailure(err => defaultUser)     // Observable[User]
obs.throwFailure                           // Observable[User] -- undoes recoverToTry
```

### TryStream (streams only)

```scala
stream.collectSuccess                      // EventStream[User]
stream.collectFailure                      // EventStream[Throwable]
stream.collectSuccess { case u if u.isActive => u }
```

### splitTry (streams + signals)

```scala
trySignal.splitTry(
  success = (initial, signal) => renderUser(initial, signal),
  failure = (initialErr, errSignal) => renderError(initialErr, errSignal)
)  // Signal[Element]
```

Delegates to `splitEither` internally after converting via `mapToEither`.

## Status Extensions

### StatusObservable (streams + signals)

```scala
val obs: Observable[Status[Query, Results]] = ...

obs.mapOutput(_.items)           // Observable[Status[Query, List[Item]]]
obs.mapInput(_.text)             // Observable[Status[String, Results]]
obs.mapResolved(r => r.output)   // Observable[Either[Pending[Query], Results]]
obs.mapPending(p => p.input)     // Observable[Either[Query, Resolved[Query, Results]]]
obs.foldStatus(
  resolved = r => s"Done: ${r.output}",
  pending = p => s"Loading: ${p.input}"
)                                // Observable[String]
```

### StatusStream (streams only)

```scala
stream.collectOutput             // EventStream[Results]
stream.collectResolved           // EventStream[Resolved[Query, Results]]
stream.collectPending            // EventStream[Pending[Query]]
stream.collectPendingInput       // EventStream[Query]
```

### splitStatus (streams + signals)

```scala
statusSignal.splitStatus(
  resolved = (initial, signal) => renderResults(initial, signal),
  pending = (initial, signal) => renderLoading(initial, signal)
)  // Signal[Element]
```

## Meta / Flatten Extensions

`MetaObservable` provides flatten operators for nested observables
(`Observable[Observable[A]]`):

```scala
val nested: Signal[EventStream[Int]] = ...

nested.flatten              // uses default SwitchingStrategy
nested.flattenSwitch        // explicit switch (cancel previous inner)
nested.flattenMerge         // merge all inner observables
nested.flattenCustom(strategy)  // user-provided FlattenStrategy
```

## Tuple Extensions

`TupleStream2` through `TupleStream9` add `mapN` and `filterN` to streams
of tuples, avoiding manual `_1`, `_2` access:

```scala
val stream: EventStream[(String, Int)] = ...

stream.mapN((name, age) => s"$name is $age")     // EventStream[String]
stream.filterN((name, age) => age > 18)          // EventStream[(String, Int)]
```

Generated for arities 2 through 9. Signals have corresponding `TupleSignal`
extensions.

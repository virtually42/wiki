---
id: airstream-state
title: "Mutable State: Var and Val"
category: concept
tags: [var, val, derived-var, zoom, lens, strict-signal, mutable-state, form-state]
source_files:
  - /p/gh/Airstream/src/main/scala/com/raquo/airstream/state/Var.scala
  - /p/gh/Airstream/src/main/scala/com/raquo/airstream/state/Val.scala
  - /p/gh/Airstream/src/main/scala/com/raquo/airstream/state/SourceVar.scala
  - /p/gh/Airstream/src/main/scala/com/raquo/airstream/state/DerivedVar.scala
  - /p/gh/Airstream/src/main/scala/com/raquo/airstream/state/LazyDerivedVar.scala
  - /p/gh/Airstream/src/main/scala/com/raquo/airstream/state/StrictSignal.scala
source_commit: 781abe8
related: [airstream-signals, airstream-concepts]
see_also: [airstream-patterns]
---

# Mutable State: Var and Val

## Var[A]

A mutable reactive variable. The primary way to create writable state.

```scala
class Var[A]:
  def signal: StrictSignal[A]       // read-only signal of current state
  def now(): A                      // current value (strict)
  def tryNow(): Try[A]             // current value as Try

  // Writing
  def set(value: A): Unit          // set new value (fires in transaction)
  def setTry(value: Try[A]): Unit
  def update(mod: A => A): Unit    // modify current value
  def tryUpdate(mod: Try[A] => Try[A]): Unit

  // Observer-based writing
  def writer: Observer[A]                     // observer that sets value
  def updater[B](mod: (A, B) => A): Observer[B]  // observer that updates

  // Derived vars (lens-like)
  def zoom[B](in: A => B)(out: (A, B) => A): Var[B]        // lazy
  def zoomStrict[B](in: A => B)(out: (A, B) => A)(owner: Owner): Var[B]  // strict
  def bimap[B](getThis: A => B, getParent: B => A): Var[B] // isomorphism
```

### Creating a Var

```scala
val count = Var(0)                        // Var[Int] with initial value 0
val name = Var.fromTry(Success("hello"))  // Var[String] from Try
```

### Writing to a Var

```scala
count.set(42)                             // replace value
count.update(_ + 1)                       // modify in place
count.writer.onNext(99)                   // via observer

// Multiple writes batched in one transaction:
Var.set(count -> 1, name -> "world")
Var.update(count -> (_ + 1), name -> (_ + "!"))
```

### Var.zoom (Derived Vars)

Create a bidirectional lens into part of a Var's state:

```scala
case class Form(name: String, age: Int)
val formVar = Var(Form("", 0))

val nameVar: Var[String] = formVar.zoom(_.name)((form, n) => form.copy(name = n))
val ageVar: Var[Int] = formVar.zoom(_.age)((form, a) => form.copy(age = a))

nameVar.set("Alice")  // updates formVar to Form("Alice", 0)
```

**Lazy vs Strict zoom:**
- `zoom` — creates LazyDerivedVar, only evaluates when observed
- `zoomStrict(owner)` — creates DerivedVar, maintains value eagerly

### Var.updater

Create an Observer that applies a modification function:

```scala
val incrementBy: Observer[Int] = count.updater((current, delta) => current + delta)
incrementBy.onNext(5)  // count becomes count.now() + 5
```

## Val[A]

An immutable constant signal. Never changes value, never fires updates.

```scala
val constant: Val[Int] = Val(42)
constant.now()  // always 42
```

Useful as a "static" signal in APIs that expect Signal[A].

## SourceVar vs DerivedVar

```
SourceVar[A]         — root var, stores its own state
DerivedVar[A, B]     — strict derived var from zoom/bimap, backed by parent var
LazyDerivedVar[A, B] — lazy derived var, evaluates on demand
```

### SourceVar internals

```scala
class SourceVar[A](initial: Try[A]) extends Var[A]:
  private val _varSignal = new VarSignal[A](initial)
  val signal: StrictSignal[A] = _varSignal

  override def set(value: A): Unit =
    val newValue = Success(value)
    Transaction { trx =>
      _varSignal.fireTry(newValue, trx)
    }
```

Every `set`/`update` creates a new Transaction, which propagates the change
synchronously through all downstream signals and streams.

## StrictSignal

A signal that always has an accessible `.now()` value regardless of whether
it's being observed:

```scala
trait StrictSignal[+A] extends Signal[A]:
  // Can always call .now() safely
  // Used for: Var.signal, DerivedVar.signal
```

Regular signals may throw if `.now()` is called when not started.
StrictSignal guarantees the value is always available.

## Patterns

### Form state management

```scala
case class LoginForm(email: String, password: String)
val formVar = Var(LoginForm("", ""))

val emailVar = formVar.zoom(_.email)((f, e) => f.copy(email = e))
val passwordVar = formVar.zoom(_.password)((f, p) => f.copy(password = p))

// In UI components:
input(value <-- emailVar.signal, onInput.mapToValue --> emailVar.writer)
input(value <-- passwordVar.signal, onInput.mapToValue --> passwordVar.writer)
```

### Derived state (read-only)

```scala
val items = Var(List.empty[Item])
val count: Signal[Int] = items.signal.map(_.size)
val isEmpty: Signal[Boolean] = items.signal.map(_.isEmpty)
```

### Coordinated updates

```scala
val x = Var(0)
val y = Var(0)

// Both update in one transaction — observers see both at once:
Var.set(x -> 1, y -> 2)
```

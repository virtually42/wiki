---
id: airstream
title: Airstream Reactive Streams
kind: descriptive
status: active
scope: global
created: 2026-05-28
updated: 2026-05-28
capabilities: [reactive-streams, state-management, ui-data-flow, dom-events]
used_by: []
version_notes: "Airstream as bundled with current Laminar — Observable / Signal / EventStream + ownership model"
---

## Deep Reference

This page is a one-stop orientation for our use of Airstream. For the
**upstream API surface** — every observable type, operator, transaction
rule, and ownership lifecycle detail — read
[[Airstream/llm-wiki/index]]. That wiki is mechanically derived from
`/p/gh/Airstream` and tracks the upstream commit each page was
extracted from.

The relationship between this page (our position) and the Airstream
llm-wiki (upstream knowledge) is documented in
[[syntheses/wiki-layering-and-external-lib-wikis]]; the bridge file
with upstream commit / sections lives at
[[sources/raw/code/airstream]].

Skill available to the agent for focused tasks:
`frontend:airstream-ownership-patterns`.

## Overview

Airstream is the reactive event-streaming library used by Laminar (our
Scala.js UI library) for state management and event flow. It provides
a small, principled set of abstractions:

- `Observable[+A]` — root type, split into `EventStream` (no current
  value) and `Signal` (has current value).
- `Var[A]` / `Val[A]` — writable / constant signal sources.
- `EventBus[A]` / `WriteBus[A]` — writable event-stream sources.
- `Observer[-A]` — consumer of values and errors.
- `Owner` / `Subscription` — explicit subscription lifecycle.
- `Transaction` — glitch-free, topologically ordered propagation.

Airstream was chosen (transitively, via Laminar) for:

- A *single propagation model* covering both push (events) and pull
  (state) without two parallel hierarchies.
- An **explicit ownership model** that ties subscription lifetimes to
  DOM mounts — no manual `unsubscribe` bookkeeping in well-formed code.
- Glitch-free transactions: in a diamond dependency, a downstream
  observable fires exactly once per logical update, not once per path.
- First-class support for splitting collections into memoized child
  signals (`split`), which is the standard pattern for keyed list
  rendering in Laminar.

## Type Hierarchy

```
Observable[+A]
├── EventStream[+A]    — lazy, no current value, fires events
└── Signal[+A]         — lazy, has current value, fires updates

Var[A]                 — writable mutable signal source
Val[A]                 — constant immutable signal
EventBus[A]            — writable event stream source
Observer[-A]           — consumer of values/errors
Owner                  — manages subscription lifecycles
Subscription           — link between observer and observable
```

For the canonical explanation read [[Airstream/llm-wiki/concepts]].

## Core Reading List

The load-bearing pages on the Layer-3 side. Read them in order if
new to Airstream:

| Topic | Layer-3 page |
|-------|--------------|
| Type hierarchy, laziness, Observer | [[Airstream/llm-wiki/concepts]] |
| State-based observables | [[Airstream/llm-wiki/signals]] |
| Event-based observables | [[Airstream/llm-wiki/streams]] |
| Var / Val / DerivedVar | [[Airstream/llm-wiki/state]] |
| EventBus / WriteBus | [[Airstream/llm-wiki/eventbus]] |
| Owner / Subscription / DynamicOwner | [[Airstream/llm-wiki/ownership]] |
| Glitch-free propagation, topological order | [[Airstream/llm-wiki/transactions]] |
| map / filter / combine / flatten / split | [[Airstream/llm-wiki/operators]] |
| Type-specific extensions (Option, Boolean, Either, Try, Status, Tuple) | [[Airstream/llm-wiki/extensions]] |
| Custom sources from external systems | [[Airstream/llm-wiki/custom-sources]] |
| log / spy / break debugging | [[Airstream/llm-wiki/debug]] |
| Async status tracking | [[Airstream/llm-wiki/status]] |
| Fetch / WebSocket / DOM event sources | [[Airstream/llm-wiki/web]] |
| Idioms: form state, list rendering, loading | [[Airstream/llm-wiki/patterns]] |
| Error handling, naming, type signatures | [[Airstream/llm-wiki/conventions]] |

## Ownership — the load-bearing concept

The single most common Airstream pitfall is mishandling subscription
ownership. Two rules cover most cases:

1. Every subscription needs an `Owner` in scope. In Laminar, mount
   contexts provide one automatically (`onMountCallback`,
   `--> observer` on a mounted element).
2. A `Var` is *not* owned, but its `signal` *is* observed by owned
   subscribers. Killing the owner kills the subscription, not the Var.

Full detail at [[Airstream/llm-wiki/ownership]] and in the
`frontend:airstream-ownership-patterns` skill.

## Dependency Coordinates

Airstream is normally pulled in transitively via Laminar. If a module
needs it directly (e.g. a non-Laminar Scala.js library that produces
observables), declare it in `deps/Dependencies.mill` following the
[[tech/decisions/deps-single-file]] convention:

```scala
package build.deps
import mill.*, scalalib.*

private val laminarV    = "17.x.y"  // pin to actual Laminar version
private val airstreamV  = "17.x.y"  // same series as Laminar's bundled Airstream

object Deps:
  val laminar    = mvn"com.raquo::laminar::$laminarV"
  // direct dep only when not already getting it via laminar
  val airstream  = mvn"com.raquo::airstream::$airstreamV"
```

`::` is correct — Airstream is a Scala.js artifact. Airstream is
**Scala.js only**; there is no JVM or Scala Native publish.

## Relation to Functional Domain Design

Airstream sits at the **interpreter / world** boundary: the immutable
domain model (constructors, operators) lives in pure data per
[[tech/patterns/functional-domain-design]]; Airstream is one of the
runtimes the model can be wired into — concretely, the UI runtime
backed by Laminar.

Idiomatic shape: keep the model and its operators total and
side-effect-free; let a thin adapter project `Var[Model] → Signal[View]`
through `map` / `combineWith` / `split`. The model does not import
Airstream; the adapter does.

## Known Issues

- Airstream is **Scala.js only** — do not put Airstream-typed values
  in cross-platform `shared` sources. Keep them in `src-js/`.
- The ownership model is *explicit*: outside of Laminar mount
  contexts you must construct an `Owner` (or `OneTimeOwner`) and
  `kill` it. Forgetting this leaks subscriptions silently.
- `Var.update(f)` reads the current value and writes `f(value)` — it
  is *not* atomic across fibers/async boundaries. In Airstream all
  propagation is single-threaded by design (JS), so this is fine
  for browser code but worth knowing.

## Links

- [Airstream README](https://github.com/raquo/Airstream) — upstream docs
- [[Airstream/llm-wiki/index]] — upstream API reference (Layer 3)
- [[sources/raw/code/airstream]] — bridge file (last observed commit, sections)
- [[syntheses/wiki-layering-and-external-lib-wikis]] — how this page relates to the Airstream llm-wiki
- [[tech/patterns/functional-domain-design]]
- [[tech/decisions/deps-single-file]]

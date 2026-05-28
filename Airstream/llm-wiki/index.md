---
id: airstream-index
title: "Airstream LLM Wiki"
category: index
source_commit: 781abe8
---

# Airstream LLM Wiki

Reactive event streaming library for Scala.js. Provides Observable, Signal,
EventStream, Var, and an ownership-based memory management model.

## Sections

- [concepts.md](concepts.md) — Core abstractions and type hierarchy
- [signals.md](signals.md) — Signal: state-based observable with current value
- [streams.md](streams.md) — EventStream: event-based observable without state
- [state.md](state.md) — Var, Val, DerivedVar: mutable reactive state
- [eventbus.md](eventbus.md) — EventBus, WriteBus: writable event stream source
- [ownership.md](ownership.md) — Owner, Subscription, DynamicOwner lifecycle
- [transactions.md](transactions.md) — Glitch-free propagation and topological ordering
- [operators.md](operators.md) — Map, filter, combine, flatten, split
- [custom-sources.md](custom-sources.md) — Custom stream/signal sources from external systems
- [debug.md](debug.md) — Debugger trait, debug operators (log, spy, break)
- [status.md](status.md) — Async status tracking with Status[In, Out] ADT
- [extensions.md](extensions.md) — Type-specific extensions (Option, Boolean, Either, Try, Status, Tuple)
- [patterns.md](patterns.md) — Common usage patterns and idioms
- [conventions.md](conventions.md) — Error handling, naming, type signatures

## Quick Reference

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

## Package Map

| Package | Purpose |
|---------|---------|
| core/ | Observable, Signal, EventStream, Observer, Transaction |
| state/ | Var, Val, DerivedVar, StrictSignal |
| ownership/ | Owner, Subscription, DynamicOwner |
| custom/ | CustomStreamSource, CustomSignalSource for external integration |
| combine/ | CombineObservable, MergeStream, sample operators |
| flatten/ | SwitchStream, ConcurrentStream, FlattenStrategy |
| split/ | SplitSignal, key-based memoized child signals |
| map/ | MapOps, MapStream, MapSignal |
| distinct/ | Distinct filtering operators |
| timing/ | Delay, throttle, debounce |
| eventbus/ | EventBus, WriteBus |
| extensions/ | Type-specific operators (Boolean, Option, Either, etc.) |
| web/ | Fetch, WebSocket, DOM event sources |
| status/ | Async status tracking |

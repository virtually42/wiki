---
id: source-airstream
type: external-lib
repo: /p/gh/Airstream
origin: https://github.com/raquo/Airstream.git
upstream: https://github.com/raquo/Airstream.git
wiki_branch: llm-wiki
last_observed: 2026-05-24
commit: 0f04f94
wiki_sections:
  - concepts
  - signals
  - streams
  - state
  - ownership
  - transactions
  - operators
  - patterns
  - conventions
---

## Purpose

Reactive event streaming library for Scala.js. Used in Laminar for UI
state management. Provides Observable, Signal, EventStream, Var, and an
ownership-based subscription lifecycle.

## Wiki Branch

How to query: `cd /p/gh/Airstream && git checkout llm-wiki && read llm-wiki/index.md`

Key sections:
- **concepts** — type hierarchy (Observable → Signal/EventStream), Observer, laziness model
- **signals** — state-based observable with current value, WritableSignal, StrictSignal
- **streams** — event-based observable, filter/collect/merge/delay/throttle
- **state** — Var (mutable), Val (constant), zoom/bimap derived vars
- **ownership** — Owner, Subscription, DynamicOwner lifecycle management
- **transactions** — glitch-free propagation, topological ordering, SyncObservable
- **operators** — map, combine, flatMapSwitch, flatMapMerge, split
- **patterns** — form state, list rendering, loading states, testing
- **conventions** — error handling, naming, type signatures, performance

## Refresh Procedure

1. `git fetch origin && git rebase origin/master`
2. Resolve any conflicts in llm-wiki/ (unlikely — upstream never has this folder)
3. Review source changes and update affected llm-wiki/ pages

---
id: kyo
title: Kyo Effect System
kind: descriptive
status: active
scope: global
created: 2026-05-28
updated: 2026-05-28
capabilities: [effects, concurrency, streaming, error-handling, dependency-injection]
used_by: []
version_notes: "1.0-RC1 — Kyo 1.x series with direct syntax and algebraic effect composition"
---

## Deep Reference

This page is a one-stop orientation for our use of Kyo. For the
**upstream API surface** — every effect, data type, module, and
concept — read [[kyo/llm-wiki/index]]. That wiki is mechanically
derived from `/p/gh/kyo` and tracks the upstream commit each page
was extracted from.

The relationship between this page (our position) and the Kyo
llm-wiki (upstream knowledge) is documented in
[[syntheses/wiki-layering-and-external-lib-wikis]]; the bridge file
with upstream commit / sections lives at [[sources/raw/code/kyo]].

Skills available to the agent for focused tasks:
`scala:kyo-effects-sync-async-abort`,
`scala:kyo-fiber-async-concurrency`,
`scala:kyo-channel-hub-queue`,
`scala:kyo-var-emit`,
`scala:kyo-data-env-scope`,
`scala:kyo-process-path`.

## Overview

Kyo is the primary effect system for all our Scala 3 projects. It
provides algebraic effects with a single pending type `A < S` where
`S` is an intersection of effect labels. Effects compose by
intersection at the type level and handlers peel them off one at a
time.

Kyo was chosen over alternatives (Cats Effect, ZIO) for:

- Single pending type instead of nested monad transformers — no
  heap-churn / megamorphism collapse on the JVM (cf.
  [[sources/summaries/throw_away_the_irrelevant_john_de_goes_podcast]]).
- Direct syntax (`direct { ... }`) for sequencing without flatMap noise.
- Explicit effect labels in the type — capabilities are visible, not
  hidden in a polymorphic `M[_]`.
- First-class support for Scala JVM, Scala.js, and Scala Native from a
  single core.
- Foundation/Effects/Applications/Integrations module layering that
  scales from a CLI to an HTTP server to a Wayland compositor.

## Module Layers

```
Foundation:    kyo-data, kyo-kernel
Effects:       kyo-prelude, kyo-core, kyo-combinators, kyo-direct
Applications:  kyo-http, kyo-stm, kyo-actor, kyo-flow, kyo-cache, kyo-schema
Integrations:  kyo-caliban, kyo-cats, kyo-zio, kyo-reactive-streams, kyo-aeron
Scheduler:     kyo-scheduler (standalone, also Scala 2 compatible)
```

For per-module detail, see [[kyo/llm-wiki/modules/index]].

## Core Concepts

The pending type, effect composition, and direct syntax are the load-bearing
ideas. For the canonical explanation read the Layer-3 pages directly:

- [[kyo/llm-wiki/concepts/pending-type]] — the `A < S` shape
- [[kyo/llm-wiki/concepts/effect-composition]] — intersection of labels
- [[kyo/llm-wiki/concepts/effect-widening]] — automatic widening rules
- [[kyo/llm-wiki/concepts/direct-syntax]] — sequencing with `direct { ... }`
- [[kyo/llm-wiki/concepts/algebraic-effects]] — the underlying model
- [[kyo/llm-wiki/concepts/resource-management]] — scope and finalization

## Effects Cheat-Sheet

The set most projects reach for first. Full list at
[[kyo/llm-wiki/effects/index]].

| Effect | Purpose | Layer-3 page |
|--------|---------|--------------|
| `Sync` | Side-effecting code | [[kyo/llm-wiki/effects/sync]] |
| `Abort[E]` | Typed short-circuit / error | [[kyo/llm-wiki/effects/abort]] |
| `Env[R]` | Dependency injection | [[kyo/llm-wiki/effects/env]] |
| `Async` | Fiber-based concurrency | [[kyo/llm-wiki/effects/async]] |
| `Scope` | Resource acquisition / release | [[kyo/llm-wiki/effects/scope]] |
| `Stream[A]` | Pull-based streaming | [[kyo/llm-wiki/effects/stream]] |
| `Var[S]` | Functional mutable state | [[kyo/llm-wiki/effects/var]] |
| `Emit[V]` | Writer-style value emission | [[kyo/llm-wiki/effects/emit]] |
| `Channel`, `Hub`, `Queue` | Fiber communication | [[kyo/llm-wiki/effects/channel]], [[kyo/llm-wiki/effects/hub]], [[kyo/llm-wiki/effects/queue]] |

## Data Types

Kyo ships its own opinionated data types in `kyo-data`. Prefer these
over `Option` / `Either` / `Vector` in Kyo-using code:

- `Maybe[A]` — null-free optional (no `Some(null)` ambiguity)
- `Result[E, A]` — typed success/failure with panic distinction
- `Chunk[A]` — efficient indexed sequence used by `Stream`
- `Duration` — time spans (used by clock/retry/async)
- `Tag[A]` — runtime tag for effect handler dispatch

See [[kyo/llm-wiki/data/index]].

## Dependency Coordinates

Kyo artifacts in `deps/Dependencies.mill` follow the
[[tech/decisions/deps-single-file]] convention:

```scala
package build.deps
import mill.*, scalalib.*

private val kyoV = "1.0-RC1"

object Deps:
  val kyoCore       = mvn"io.getkyo::kyo-core::$kyoV"
  val kyoPrelude    = mvn"io.getkyo::kyo-prelude::$kyoV"
  val kyoCombinators = mvn"io.getkyo::kyo-combinators::$kyoV"
  val kyoDirect     = mvn"io.getkyo::kyo-direct::$kyoV"
  // application-level
  val kyoHttp       = mvn"io.getkyo::kyo-http::$kyoV"
  val kyoSchema     = mvn"io.getkyo::kyo-schema::$kyoV"
```

All Kyo modules cross-publish for JVM, Scala.js, and Scala Native
unless noted otherwise on the specific module's Layer-3 page.

## Conventions

Code style for Kyo-using modules is captured in
[[kyo/llm-wiki/conventions/index]]:

- [[kyo/llm-wiki/conventions/naming]]
- [[kyo/llm-wiki/conventions/types]]
- [[kyo/llm-wiki/conventions/method-signatures]]
- [[kyo/llm-wiki/conventions/inline]]
- [[kyo/llm-wiki/conventions/file-organization]]
- [[kyo/llm-wiki/conventions/testing-conventions]]

## Patterns and Recipes

For task-oriented guidance start at
[[kyo/llm-wiki/patterns/index]] and [[kyo/llm-wiki/recipes/index]].
Most common entry points:

| I want to... | Start here |
|---|---|
| Handle errors | [[kyo/llm-wiki/patterns/error-handling]] |
| Inject dependencies | [[kyo/llm-wiki/patterns/dependency-injection]] |
| Do concurrent work | [[kyo/llm-wiki/patterns/concurrency]] |
| Process streams | [[kyo/llm-wiki/patterns/streaming]] |
| Test effectful code | [[kyo/llm-wiki/patterns/testing]] |
| Build an HTTP server | [[kyo/llm-wiki/recipes/http-server]] |
| Build a CLI app | [[kyo/llm-wiki/recipes/cli-app]] |

## Relation to Functional Domain Design

Kyo is the **interpreter side** of
[[tech/patterns/functional-domain-design]]: an immutable model and
constructors live in pure data, while a Kyo-effectful interpreter
(`A < (Sync & Abort[E] & Env[R])`) executes the program. The
encoding choice (executable vs declarative) is independent of Kyo —
Kyo is the host for both styles.

The De Goes critique of polymorphic `M[_]` with capability type
classes (see
[[sources/summaries/throw_away_the_irrelevant_john_de_goes_podcast]])
applies here: Kyo's concrete pending type with explicit effect
labels sits closer to the *concrete-IO* end of that axis than to
the *polymorphic-MTL* end.

## Known Issues

- `1.0-RC1` is a release candidate; expect minor API shifts before
  `1.0.0`. Pin the version centrally in `deps/Dependencies.mill` so
  bumps are a single edit.
- Direct syntax (`direct { ... }`) requires `kyo-direct` on the
  classpath; it is a separate artifact from `kyo-core`.

## Links

- [Kyo documentation](https://getkyo.io) — upstream docs site
- [[kyo/llm-wiki/index]] — upstream API reference (Layer 3)
- [[sources/raw/code/kyo]] — bridge file (last observed commit, sections)
- [[syntheses/wiki-layering-and-external-lib-wikis]] — how this page relates to the Kyo llm-wiki
- [[tech/patterns/functional-domain-design]]
- [[tech/decisions/deps-single-file]]
- [[sources/summaries/throw_away_the_irrelevant_john_de_goes_podcast]]

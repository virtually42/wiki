# Kyo LLM-Wiki

Query-optimized knowledge base for the Kyo algebraic effect system.

## Quick Lookup

| I want to... | Start here |
|---|---|
| Understand the type system | [concepts/pending-type](concepts/pending-type.md) |
| Handle errors | [effects/abort](effects/abort.md), [patterns/error-handling](patterns/error-handling.md) |
| Inject dependencies | [effects/env](effects/env.md), [patterns/dependency-injection](patterns/dependency-injection.md) |
| Do concurrent work | [effects/async](effects/async.md), [patterns/concurrency](patterns/concurrency.md) |
| Process streams | [effects/stream](effects/stream.md), [patterns/streaming](patterns/streaming.md) |
| Manage resources | [effects/scope](effects/scope.md), [concepts/resource-management](concepts/resource-management.md) |
| Use direct syntax | [concepts/direct-syntax](concepts/direct-syntax.md) |
| Build an HTTP server | [recipes/http-server](recipes/http-server.md), [modules/kyo-http](modules/kyo-http.md) |
| Build a CLI app | [recipes/cli-app](recipes/cli-app.md), [modules/kyo-case-app](modules/kyo-case-app.md) |
| Choose data types | [data/index](data/index.md) (Maybe, Result, Chunk) |
| Follow code conventions | [conventions/index](conventions/index.md) |
| Test effectful code | [patterns/testing](patterns/testing.md), [recipes/effect-testing](recipes/effect-testing.md) |

## Sections

- [concepts/](concepts/index.md) — foundational ideas: pending type, effect composition, direct syntax
- [effects/](effects/index.md) — one page per effect: Abort, Env, Async, Stream, etc.
- [data/](data/index.md) — data types: Maybe, Result, Chunk, Duration, Tag
- [modules/](modules/index.md) — integration modules: kyo-http, kyo-schema, kyo-flow, etc.
- [patterns/](patterns/index.md) — how to combine things: error handling, DI, concurrency
- [conventions/](conventions/index.md) — code style: naming, types, inline, method signatures
- [recipes/](recipes/index.md) — task-oriented guides: build a server, CLI app, stream pipeline

## Module Layers

```
Foundation:    kyo-data, kyo-kernel
Effects:       kyo-prelude, kyo-core, kyo-combinators, kyo-direct
Applications:  kyo-http, kyo-stm, kyo-actor, kyo-flow, kyo-cache, kyo-schema
Integrations:  kyo-caliban, kyo-cats, kyo-zio, kyo-reactive-streams, kyo-aeron
Scheduler:     kyo-scheduler (standalone, also Scala 2 compatible)
```

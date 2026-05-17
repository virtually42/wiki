---
id: compositor-adr-003
title: Effect system and error handling
kind: normative
status: accepted
project: compositor
created: 2026-04-10
updated: 2026-05-15
compliance:
  adopts:
    - tech/decisions/effects-kyo.md
    - tech/patterns/typed-errors.md
  exceptions:
    - page: tech/patterns/immutable-state.md
      rationale: |
        The rendering pipeline uses a mutable frame buffer managed by wlroots.
        Domain-level state (window layout, workspace state) remains immutable.
        Mutation is confined to the rendering boundary.
      risk: low
  deviations: []
  ignores:
    - page: tech/guides/jvm-tuning.md
      rationale: Scala Native target.
    - page: tech/patterns/http-api-versioning.md
      rationale: No HTTP API in the compositor.
supersedes: []
---

# ADR-003: Effect System and Error Handling

## Context

The compositor needs to manage multiple effect types:
- I/O for Wayland protocol communication
- Abort for error handling at subsystem boundaries
- Async for non-blocking event processing
- Resource management for wlroots objects

We need a consistent approach that works with Scala Native and integrates
with the wlroots C bindings.

## Decision

Adopt Kyo as the effect system per [[tech/decisions/effects-kyo]]. Use typed
error boundaries per [[tech/patterns/typed-errors]] at subsystem edges
(input, rendering, IPC, window management).

Each subsystem defines its own error ADT:

```scala
enum InputError:
  case DeviceNotFound(path: String)
  case ProtocolViolation(msg: String)

enum RenderError:
  case BufferAllocationFailed(size: Int)
  case ShaderCompilationFailed(shader: String, error: String)
```

## Consequences

- All subsystem boundaries have typed, exhaustive error handling
- Kyo effects compose across subsystem interactions
- The rendering pipeline's mutable frame buffer is an accepted exception
  to the immutable-state preference (see compliance block)
- C interop errors from wlroots are converted to domain errors at the
  Scala Native binding layer

## Alternatives Considered

### Direct exception handling
Simpler code but loses type safety. Rejected per workspace decision.

### Custom effect encoding
Too much infrastructure code for one project. Kyo provides what we need.

## Links

- [[tech/decisions/effects-kyo]]
- [[tech/patterns/typed-errors]]
- [[projects/compositor/architecture]]

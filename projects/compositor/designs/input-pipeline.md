---
id: compositor-design-input-pipeline
title: Input event processing pipeline design
kind: descriptive
status: draft
project: compositor
created: 2026-05-24
updated: 2026-05-24
related_adrs: []
related_plans:
  - projects/compositor/plans/input-pipeline.md
sources: []
---

## Problem

The compositor needs to process input events (keyboard, mouse, touch, tablet)
from libinput through wlroots and dispatch them to the correct Wayland client.
The pipeline must handle event coalescing, seat management, focus tracking,
and grab semantics — all without GC pauses in the hot path.

## Constraints

- Zero-allocation hot path (Scala Native, no GC pressure)
- Must integrate with wlroots seat and input device abstractions
- Event ordering must be preserved per-device
- Grab semantics (pointer grabs, keyboard grabs) must override normal dispatch
- Must support input method protocols (text-input, input-method)

## Options Explored

### Option A: Single-threaded event loop with arena allocator

Process all input events synchronously in the main compositor loop.
Allocate event structs from a per-frame arena that resets each frame.

Pros: simple, deterministic, no synchronization
Cons: input processing blocks rendering if slow

### Option B: Dedicated input thread with ring buffer

Process input events in a separate thread, communicate to main loop
via a lock-free ring buffer.

Pros: input never blocks rendering
Cons: complexity of cross-thread communication in Scala Native, wlroots
is single-threaded by design

### Option C: Coroutine-based pipeline with Kyo

Model the input pipeline as a Kyo effect chain. Events flow through
composable stages (coalesce -> focus-resolve -> grab-check -> dispatch).

Pros: composable, testable stages; integrates with Kyo effect system
Cons: must ensure zero-allocation in the hot path; Kyo overhead unknown
for Scala Native

## Proposed Approach

Option A with selective adoption of Option C's composability.

The main loop processes input synchronously (Option A) for simplicity and
wlroots compatibility. But the dispatch logic is structured as composable
pure functions (inspired by Option C) that can be tested on JVM without
the compositor running.

Arena allocation handles per-frame event structs. The pipeline stages are:

```
libinput event -> wlr_event -> coalesce -> resolve_focus -> check_grab -> dispatch_to_client
```

Each stage is a pure function `(Event, State) => (Event, State)` that can
be property-tested independently.

## Trade-offs

- **Gain:** simplicity, wlroots compatibility, testable pure core
- **Give up:** async input processing (acceptable — input is fast, rendering is the bottleneck)
- **Risk:** if event processing ever becomes slow (complex input methods), we'll need to revisit

## Open Questions

- What is Kyo's overhead on Scala Native for effect interpretation? Needs benchmarking.
- How do wlroots grabs interact with our focus tracking? Need to study wlr_seat_pointer_grab.
- Should touch and tablet events share the same pipeline or have dedicated paths?

## Decision Record

*Pending — ADRs will be created once the approach is validated with a prototype.*

---
id: compositor-plan-input-pipeline
title: Implement input event processing pipeline
kind: project
status: draft
project: compositor
created: 2026-05-24
updated: 2026-05-24
design_doc: projects/compositor/designs/input-pipeline.md
related_adrs: []
tickets: []
estimated_sessions: 4
---

## Goal

Implement the input event processing pipeline from libinput through to
Wayland client dispatch, with a testable pure core and zero-allocation hot path.

## Prerequisites

- wlroots Scala Native bindings for wlr_seat, wlr_input_device, wlr_keyboard
- Arena allocator implemented (or use Scala Native Zone)
- Basic compositor loop running (can display a window)

## Steps

1. Define event ADT — model wlr input events as Scala case classes for the pure core.
   Dependencies: none.

2. Implement focus resolver — pure function that determines which surface
   receives input based on pointer position and surface stack.
   Dependencies: step 1.

3. Implement grab semantics — pure function that intercepts events when a
   grab is active (pointer grab, keyboard grab).
   Dependencies: step 1, step 2.

4. Implement event coalescing — merge rapid pointer motion events within
   the same frame to reduce dispatch overhead.
   Dependencies: step 1.

5. Wire pipeline to wlroots — connect libinput events to the pure pipeline,
   dispatch results via wlr_seat_*_notify functions.
   Dependencies: steps 1-4.

6. Property tests for pure core — generators for input events, properties
   for focus correctness, grab priority, coalescing invariants.
   Dependencies: steps 1-4.

## Acceptance Criteria

- Keyboard input reaches the focused client correctly
- Pointer motion and clicks reach the correct client based on position
- Pointer grab (e.g., window resize) overrides normal focus dispatch
- No heap allocations in the per-event hot path (verified by profiling)
- Property tests pass for all pipeline stages

## Risks

- wlroots grab API may be more complex than modeled — may need to expand step 3
- Kyo effect overhead on Scala Native unknown — may need to avoid Kyo in the hot path entirely
- Touch/tablet events deferred to a follow-up plan

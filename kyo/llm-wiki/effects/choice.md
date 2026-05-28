---
id: kyo-effect-choice
title: "Choice — Non-Deterministic Branching"
category: effect
layer: prelude
tags: [non-determinism, branching, backtracking, exploration]
source_files:
  - /p/gh/kyo/kyo-prelude/shared/src/main/scala/kyo/Choice.scala
source_commit: 9bab8d00
api_surface: [Choice.eval, Choice.evalSeq, Choice.drop, Choice.dropIf, Choice.run]
related: [kyo-effect-abort, kyo-effect-stream]
see_also: []
platforms: [jvm, js, native]
effect_type: ArrowEffect
suspend_methods: [eval, evalSeq, drop, dropIf]
handle_methods: [run]
pending_type: "Choice"
---

## What It Does

Explores multiple options/pathways in a computation. Useful for decision trees, constraint solving, and backtracking algorithms.

## Key APIs

### Suspending

| Method | Signature | Purpose |
|--------|-----------|---------|
| `Choice.eval(values*)` | `A < Choice` | Branch into multiple values |
| `Choice.evalSeq(seq)` | `A < Choice` | Branch from a sequence |
| `Choice.drop` | `Nothing < Choice` | Discard current branch |
| `Choice.dropIf(cond)` | `Unit < Choice` | Conditional discard |

### Handling

| Method | Signature | Purpose |
|--------|-----------|---------|
| `Choice.run(comp)` | `Seq[A] < S` | Collect all surviving branches |

## Common Patterns

### Filter and transform

```scala
val result: Seq[Int] < Any =
    Choice.run {
        for
            v <- Choice.eval(1, 2, 3, 4)
            _ <- Choice.dropIf(v > 2)
        yield v * 10
    }
// result: Seq(10, 20)
```

### Constraint solving

```scala
val solutions: Seq[(Int, Int)] < Any =
    Choice.run {
        for
            x <- Choice.eval(1, 2, 3)
            y <- Choice.eval(1, 2, 3)
            _ <- Choice.dropIf(x + y != 4)
        yield (x, y)
    }
// solutions: Seq((1,3), (2,2), (3,1))
```

## Gotchas

- `Choice.run` evaluates ALL branches — exponential blowup if unconstrained
- Use `dropIf` early to prune the search space
- `Choice.drop` is the non-determinism equivalent of `Abort.fail`
- Can combine with other effects (Async, Sync) for effectful branching

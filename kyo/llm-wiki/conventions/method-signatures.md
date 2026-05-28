---
id: kyo-convention-method-signatures
title: "Method Signature Conventions"
category: convention
layer: foundation
tags: [signatures, using-clauses, frame, tag, allow-unsafe]
source_files:
  - /p/gh/kyo/CONTRIBUTING.md
  - /p/gh/kyo/AGENTS.md
source_commit: 9bab8d00
api_surface: [Tag, Frame, AllowUnsafe]
related: [kyo-data-tag, kyo-convention-inline]
see_also: []
platforms: [jvm, js, native]
---

## Rule

`using` clauses follow a strict ordering: Tag → Frame → evidence → AllowUnsafe.

## Ordering

### Inline methods (suspend paths)

```scala
inline def myEffect[A](
    value: A
)(using inline Tag[A], inline Frame): A < MyEffect
```

### Non-inline methods (handle paths)

```scala
def handle[A](
    comp: A < (MyEffect & S)
)(using Frame, Tag[A]): A < S
```

### Unsafe methods

```scala
def unsafeRun[A](
    comp: A < Sync
)(using AllowUnsafe): A  // AllowUnsafe always LAST
```

## Frame Requirements

| Needs Frame | No Frame |
|-------------|----------|
| Every effectful method | Pure data accessors: `capacity`, `size` |
| Error-reporting methods | Simple getters |

## Gotchas

- `kyo.System` shadows `java.lang.System` — use fully qualified when needed
- Every effectful method needs `Frame` for source location in errors
- Overloaded methods: all overloads delegate to a canonical implementation
- `Tag` must be `inline` in `inline` methods

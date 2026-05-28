---
id: kyo-data-maybe
title: "Maybe — Allocation-Free Optional"
category: data
layer: foundation
tags: [optional, maybe, absent, present, opaque-type]
source_files:
  - /p/gh/kyo/kyo-data/shared/src/main/scala/kyo/Maybe.scala
source_commit: 9bab8d00
api_surface: [Maybe, Maybe.apply, Maybe.when, Maybe.fromOption, Absent, Present, Maybe.empty]
related: [kyo-data-result]
see_also: [kyo-effect-abort]
platforms: [jvm, js, native]
opaque: true
replaces: "Option"
---

## What It Is

Allocation-free optional value. Opaque type over `Any` — no boxing, no wrapper object.

## When to Use

**Always use `Maybe` instead of `Option` in Kyo code.** Convention enforced.

## Key APIs

| Method | Purpose |
|--------|---------|
| `Maybe(value)` | Create (null-safe — null becomes Absent) |
| `Maybe.when(cond)(value)` | Conditional creation |
| `Maybe.fromOption(opt)` | Convert from Option |
| `.get` | Unwrap (throws if Absent) |
| `.getOrElse(default)` | Unwrap with fallback |
| `.map(f)` | Transform if present |
| `.flatMap(f)` | Chain Maybe operations |
| `.filter(pred)` | Conditional keep |
| `.fold(ifAbsent)(ifPresent)` | Pattern match |
| `.toOption` | Convert to Option (for interop) |
| `.isEmpty` / `.isDefined` | Check state |
| `.orElse(alt)` | Alternative if absent |
| `.zip(other)` | Combine two Maybes |
| `.flatten` | Remove nesting |

## Pattern Matching

```scala
value match
    case Present(v) => s"got $v"
    case Absent     => "nothing"
```

## Performance Characteristics

- **Zero allocation** — opaque type, no wrapper object
- Use `t"..."` interpolation for proper display: `t"value: $maybe"` → `Present(42)`
- `s"..."` interpolation shows raw value: `s"value: $maybe"` → `42` (misleading!)

## Gotchas

- `Maybe` is unboxed — `toString` shows raw value, use `t`-strings or `Render`
- `Maybe(null)` returns `Absent` (null-safe factory)
- Cannot nest transparently with `s`-strings
- For-comprehensions work: `for x <- Maybe(1); y <- Maybe(2) yield x + y`

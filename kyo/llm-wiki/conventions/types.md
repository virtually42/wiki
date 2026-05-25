---
id: kyo-convention-types
title: "Type Conventions"
category: convention
layer: foundation
tags: [types, maybe, result, chunk, kyo-types]
source_files:
  - CONTRIBUTING.md
  - AGENTS.md
source_commit: 9bab8d00
api_surface: []
related: [kyo-data-maybe, kyo-data-result, kyo-data-chunk]
see_also: []
platforms: [jvm, js, native]
---

## Rule

Always use Kyo types over stdlib equivalents in Kyo code.

## Rationale

Kyo types are opaque (zero-allocation), performance-optimized, and integrate with the effect system.

## Type Mapping

| Use this | Not this |
|----------|----------|
| `Maybe` | `Option` |
| `Result` | `Either`, `Try` |
| `Chunk` | `List`, `Vector`, `Seq` |
| `Duration` | `scala.concurrent.duration.Duration` |
| `Text` | `String` (for display/logging) |
| `t"..."` interpolation | `s"..."` (for Kyo values) |

## Display Convention

```scala
// WRONG — opaque types display misleadingly
println(s"value: $maybe")     // "value: 42" (looks like Int!)

// RIGHT — shows wrapper type
println(t"value: $maybe")     // "value: Present(42)"
```

## Exceptions

- API boundaries with external libraries may use stdlib types
- Convert at the boundary: `Maybe.fromOption(opt)`, `result.toEither`

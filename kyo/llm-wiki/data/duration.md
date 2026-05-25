---
id: kyo-data-duration
title: "Duration — Time Representation"
category: data
layer: foundation
tags: [time, duration, nanoseconds, opaque-type]
source_files:
  - kyo-data/shared/src/main/scala/kyo/Duration.scala
source_commit: 9bab8d00
api_surface: [Duration, Duration.fromNanos, Duration.Zero, Duration.Infinity]
related: [kyo-effect-clock]
see_also: []
platforms: [jvm, js, native]
opaque: true
replaces: "scala.concurrent.duration.Duration"
---

## What It Is

Nanosecond-precision duration. Opaque type over Long — zero allocation.

## Key APIs

### Creation

```scala
import kyo.Duration.Units.*
5.seconds; 100.millis; 1.hour; 2.days
Duration.fromNanos(1000000)
Duration.fromUnits(2, Weeks)
```

### Arithmetic & Comparison

`a + b`, `a - b`, `a * n`, `a / n`, `a > b`, `a <= b`

### Conversion

`.toNanos`, `.toMillis`, `.toSeconds`, `.toMinutes`, `.toJava`, `.toScala`

### Special Values

`Duration.Zero`, `Duration.Infinity`

## Gotchas

- Opaque Long — `toString` shows raw nanoseconds, use `.show` or `t`-strings
- Internal representation is nanoseconds
- `Duration.fromJava` / `Duration.fromScala` for interop

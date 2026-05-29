---
id: codec-date-time
title: "Date and Time Codecs"
category: codec
layer: integration
tags: [date, time, java-time, scala-java-time, platform]
source_files:
  - /p/gh/toml-scala/core/src/main/scala/toml/PlatformCodecs.scala
  - /p/gh/toml-scala/core/src/main/scala/toml/PlatformValue.scala
  - /p/gh/toml-scala/core/src/main/scala/toml/PlatformRules.scala
source_commit: 03d4e5f
api_surface:
  - toml.PlatformCodecs
  - toml.PlatformCodecs.localDateCodec
  - toml.PlatformCodecs.localTimeCodec
  - toml.PlatformCodecs.localDateTimeCodec
  - toml.PlatformCodecs.offsetDateTimeCodec
related:
  - codecs/built-in.md
  - data/value.md
see_also:
  - api/parse-as.md
---

# Date and Time Codecs

The four time codecs live on `trait PlatformCodecs`. They are
**not** members of `Codec`'s companion directly — they reach the
implicit scope via `toml.derivation.auto`, which extends
`PlatformCodecs`.

```scala
implicit val localDateCodec:      Codec[LocalDate]
implicit val localTimeCodec:      Codec[LocalTime]
implicit val localDateTimeCodec:  Codec[LocalDateTime]
implicit val offsetDateTimeCodec: Codec[java.time.OffsetDateTime]
```

Each accepts the corresponding `Value.Date` / `Value.Time` /
`Value.DateTime` / `Value.OffsetDateTime` and unwraps the underlying
`java.time` value.

## Importing

To get the date codecs in scope, import `auto`:

```scala
import toml.*
import toml.derivation.auto.*   // Scala 3 (or Scala 2 — same name)
```

`auto` extends `PlatformCodecs` on Scala 2 and re-exports them through
the wider derivation surface on Scala 3.

## TOML Grammar

`PlatformRules` parses:

| TOML | Produces |
|------|----------|
| `1979-05-27` | `Value.Date(LocalDate)` |
| `07:32:00.999999` | `Value.Time(LocalTime)` — nanosecond precision |
| `1979-05-27T07:32:00` | `Value.DateTime(LocalDateTime)` |
| `1979-05-27T07:32:00Z` | `Value.OffsetDateTime(OffsetDateTime)` |
| `1979-05-27T07:32:00-07:00` | `Value.OffsetDateTime(OffsetDateTime)` |

The order of alternatives is
`offsetDateTime | localDateTime | localDate | localTime`, so the most
specific shape wins.

## Platform Dependency

| Platform | java.time source |
|----------|------------------|
| JVM | native `java.time` |
| Scala.js | `io.github.cquiroz::scala-java-time` |
| Scala Native | `io.github.cquiroz::scala-java-time` |

`scala-java-time` is added unconditionally for non-JVM platforms in
`build.sbt` and there is **no opt-out** at the time of writing
(README note (1)).

## Generation Caveat

`Generate.generate(value: Value, …)` does *not* handle the date/time
`Value` cases. Round-tripping a parsed document that contains date
values will fail at the `match`. Treat generation of dates as a gap
and emit them as `Value.Str` if you must.

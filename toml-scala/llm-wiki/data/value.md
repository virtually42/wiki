---
id: data-value
title: "Value ADT"
category: data
layer: core
tags: [value, ast, scalar, container, sealed]
source_files:
  - /p/gh/toml-scala/core/src/main/scala/toml/Value.scala
  - /p/gh/toml-scala/core/src/main/scala/toml/PlatformValue.scala
source_commit: 03d4e5f
api_surface:
  - toml.Value
  - toml.Value.Str
  - toml.Value.Bool
  - toml.Value.Real
  - toml.Value.Num
  - toml.Value.Tbl
  - toml.Value.Arr
  - toml.Value.Date
  - toml.Value.Time
  - toml.Value.DateTime
  - toml.Value.OffsetDateTime
related:
  - data/node.md
  - concepts/ast-model.md
  - codecs/built-in.md
  - codecs/date-time.md
see_also:
  - api/parse.md
---

# `Value`

```scala
package toml
trait Value

object Value extends PlatformValue {
  case class Str(value: String)             extends Value
  case class Bool(value: Boolean)           extends Value
  case class Real(value: Double)            extends Value
  case class Num(value: Long)               extends Value
  case class Tbl(values: Map[String, Value]) extends Value
  case class Arr(values: List[Value])       extends Value
}
```

`PlatformValue` mixes in date/time cases (same on every platform, but
factored to keep the `Value.scala` file pure):

```scala
case class Date(value: LocalDate)                       extends Value
case class Time(value: LocalTime)                       extends Value
case class DateTime(value: LocalDateTime)               extends Value
case class OffsetDateTime(value: java.time.OffsetDateTime) extends Value
```

## Notes

- **Not formally sealed.** The source has `/*sealed*/ trait Value`.
  Match exhaustively at your own risk; treat as closed.
- **Map ordering** is whatever `Map` implementation the parser
  produces. Do not rely on insertion order for `Value.Tbl`.
- **Integers** are `Long`. To decode as `Int` use the implicit
  `Codec[Int]` which truncates via `value.toInt`.
- **`Real`** carries `Double`, including `Double.PositiveInfinity` /
  `Double.NaN` produced by `inf` / `nan` literals.

## Construction

`Value` cases are plain case classes — construct them directly:

```scala
Value.Tbl(Map(
  "name"  -> Value.Str("alice"),
  "age"   -> Value.Num(30),
  "tags"  -> Value.Arr(List(Value.Str("admin"))),
))
```

## Decoding

Decode a `Value` into a Scala type via `Codec[T]`:

```scala
val v: Value = ...
toml.Codec[Int].apply(v, Map.empty, 0) // Either[Parse.Error, Int]
```

For convenience:

```scala
toml.Toml.parseAsValue[Int](v)
```

## Encoding

Encode a `Value` back to TOML text fragment:

```scala
toml.Generate.generate(v)
```

(See [api/generate](../api/generate.md) for limitations.)

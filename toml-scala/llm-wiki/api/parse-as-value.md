---
id: api-parse-as-value
title: "Toml.parseAsValue"
category: api
layer: integration
tags: [parse-as-value, codec, value]
source_files:
  - /p/gh/toml-scala/core/src/main/scala-3/toml/TomlVersionSpecific.scala
  - /p/gh/toml-scala/core/src/main/scala-2/toml/TomlVersionSpecific.scala
source_commit: 03d4e5f
api_surface:
  - toml.Toml.parseAsValue
  - toml.Toml.CodecHelperValue
related:
  - api/parse-as.md
  - codecs/custom.md
see_also:
  - recipes/custom-codec.md
---

# `Toml.parseAsValue`

Decode using a `Codec[T]` **without** requiring a `DefaultParams[T]`.
Use this when `T` is not a product type, or when you want to decode an
arbitrary `Value` (not necessarily a `Value.Tbl`).

```scala
def parseAsValue[T]: CodecHelperValue[T] = new CodecHelperValue[T]
```

`CodecHelperValue[T].apply` overloads:

| Overload | Signature |
|----------|-----------|
| from `Value` | `(value: Value)(using Codec[T])` |
| from string  | `(toml: String, extensions: Set[Extension] = Set())(using Codec[T])` |

Both return `Either[Parse.Error, T]`. Defaults map is always `Map()`
(empty) — this is the key difference from
[`parseAs`](parse-as.md).

## Example: Top-Level Non-Product

```scala
import toml.*

case class Currency(name: String)
implicit val currencyCodec: Codec[Currency] = ... // see recipes/custom-codec

// Decode a Value.Str directly — no Tbl required
toml.Toml.parseAsValue[Currency](Value.Str("BTC"))
```

## Example: Single Field

```scala
val tbl: Value.Tbl = ...
val arr: Value.Arr = tbl.values("xs").asInstanceOf[Value.Arr]
toml.Toml.parseAsValue[List[Int]](arr)
```

## When To Use

- The target `T` does not have synthesizable default parameters.
- You are decoding part of an AST (an array, a scalar, a nested table)
  rather than a whole document.
- You want to forward an explicitly-built `Value` through a codec.

For full document decode into a `case class`, use
[`parseAs`](parse-as.md).

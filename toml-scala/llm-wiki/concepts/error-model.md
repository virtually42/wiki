---
id: concept-error-model
title: "Error Model"
category: concept
layer: core
tags: [error, parse-error, address, either]
source_files:
  - /p/gh/toml-scala/core/src/main/scala/toml/Parse.scala
  - /p/gh/toml-scala/core/src/main/scala/toml/Embed.scala
  - /p/gh/toml-scala/core/src/main/scala/toml/Codec.scala
source_commit: 03d4e5f
api_surface:
  - toml.Parse.Error
  - toml.Parse.Address
  - toml.Parse.Field
  - toml.Parse.Message
related:
  - data/parse-error.md
  - codecs/custom.md
see_also:
  - api/parse.md
---

# Error Model

```scala
package toml
object Parse {
  type Field   = String
  type Address = List[Field]
  type Message = String
  type Error   = (Address, Message)
}
```

All failures across the pipeline use a single type:
`Parse.Error = (List[String], String)`.

- **Address** — a path describing *where* the error occurred:
  - For parse failures (`fastparse`), the address is empty and the
    message is `f.msg`.
  - For embed failures (key redefinition), the address is the
    table-header path plus the offending key.
  - For codec failures (case-class field mismatch), the address is the
    field path; nested codecs prepend their own segment.
  - For array element failures, the address segment is `#N` where `N`
    is the 1-based index (`#1`, `#2`, …).

## Where Each Error Comes From

| Source | Address example | Message example |
|--------|----------------|-----------------|
| FastParse failure | `Nil` | `"Expected …"` (fastparse-generated) |
| `Embed.addPair` redefine | `["table", "key"]` | `"Cannot redefine value"` |
| `Codec[Int]` mismatch | inherited | `"Int expected, Value.Str(\"x\") provided"` |
| `Codec[List[T]]` element | `["#3"]` | inner codec's message |
| `Codec[Map[String, T]]` value | `["key"]` | inner codec's message |
| Derivation unknown field | `["extra"]` | `"Unknown field"` |
| Derivation missing field | inherited | `` "Cannot resolve `field`" `` |
| Array too many elements | inherited | `"Too many elements; remove …"` |

## Composition

Every `Codec[T]` returns `Either[Parse.Error, T]`. Composition is
manual (`flatMap`, `for`) — see
[codecs/built-in](../codecs/built-in.md) for how the list and map
codecs prepend address segments.

## Rendering

The library does not ship a default error renderer. A typical call site
prints both halves:

```scala
toml.Toml.parseAs[Config](text) match {
  case Right(cfg) => cfg
  case Left((addr, msg)) =>
    sys.error(s"TOML decode failed at ${addr.mkString(".")}: $msg")
}
```

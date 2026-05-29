---
id: data-parse-error
title: "Parse.Error"
category: data
layer: core
tags: [error, parse-error, address, either]
source_files:
  - /p/gh/toml-scala/core/src/main/scala/toml/Parse.scala
source_commit: 03d4e5f
api_surface:
  - toml.Parse.Error
  - toml.Parse.Address
  - toml.Parse.Field
  - toml.Parse.Message
related:
  - concepts/error-model.md
see_also:
  - codecs/custom.md
---

# `Parse.Error`

```scala
package toml

object Parse {
  type Field   = String
  type Address = List[Field]
  type Message = String
  type Error   = (Address, Message)
}
```

A tuple of:

- **address** — `List[String]` describing where in the document the
  failure occurred (table path, then field name, then nested array
  index like `#2`).
- **message** — human-readable explanation.

Every `parse`, `parseAs`, `parseAsValue`, and `Codec[T].apply` call
returns `Either[Parse.Error, _]`.

## Address Conventions

| Segment shape | Origin |
|---------------|--------|
| `"key"` | a table key |
| `"#N"` | the N-th (1-based) array element |
| `Nil` | top-level failure (parser, unscoped codec mismatch) |

For the full taxonomy of error sources, see
[concepts/error-model](../concepts/error-model.md).

## Pattern for Reporting

```scala
toml.Toml.parseAs[Config](text) match {
  case Right(cfg)        => cfg
  case Left((Nil,  msg)) => sys.error(s"TOML error: $msg")
  case Left((addr, msg)) => sys.error(s"At ${addr.mkString(".")}: $msg")
}
```

---
id: api-parse-as
title: "Toml.parseAs"
category: api
layer: integration
tags: [parse-as, codec, derivation, case-class]
source_files:
  - /p/gh/toml-scala/core/src/main/scala/toml/Toml.scala
  - /p/gh/toml-scala/core/src/main/scala-3/toml/TomlVersionSpecific.scala
  - /p/gh/toml-scala/core/src/main/scala-2/toml/TomlVersionSpecific.scala
source_commit: 03d4e5f
api_surface:
  - toml.Toml.parseAs
  - toml.Toml.CodecHelperGeneric
related:
  - api/parse.md
  - codecs/built-in.md
  - derivation/scala-3.md
  - derivation/scala-2.md
see_also:
  - recipes/optional-fields.md
  - recipes/default-values.md
  - recipes/table-lists.md
---

# `Toml.parseAs`

Parse TOML text or an existing `Value.Tbl` directly into a typed value.

```scala
def parseAs[T]: CodecHelperGeneric[T] = new CodecHelperGeneric[T]
```

`CodecHelperGeneric[T]` then exposes three overloads via `.apply`:

| Overload | Signature |
|----------|-----------|
| from string + extensions | `(toml: String, extensions: Set[Extension])` |
| from string | `(toml: String)` |
| from existing AST | `(table: Value.Tbl)` |

All return `Either[Parse.Error, T]`.

## Requirements

The summoned implicits depend on the Scala version:

### Scala 3

```scala
(using
  codec: Codec[T],
  D: DefaultParams[T],
)
```

`DefaultParams[T]` is auto-derived for products via the
`derivation.macros.defaultParams` macro. `Codec[T]` is derived from
`import toml.derivation.auto.*` (see
[derivation/scala-3](../derivation/scala-3.md)).

### Scala 2

```scala
(implicit
  generic:       LabelledGeneric.Aux[A, R],
  defaults:      Default.AsRecord.Aux[A, D],
  defaultMapper: util.RecordToMap[D],
  codec:         Codec[R],
)
```

See [derivation/scala-2](../derivation/scala-2.md).

## Example

```scala
import toml.*
import toml.derivation.auto.* // Scala 3 — pulls in derivedProductCodec

case class Table(b: Int)
case class Root(a: Int, table: Table)

val text =
  """a = 1
    |[table]
    |b = 2""".stripMargin

Toml.parseAs[Root](text)
// Right(Root(1, Table(2)))
```

## From an Existing Table

When you already have a `Value.Tbl` (e.g. extracted from a larger
structure), skip re-parsing:

```scala
val sub: Value.Tbl = ...
Toml.parseAs[Table](sub)  // Either[Parse.Error, Table]
```

## See Also

- For decoding **non-product** types (e.g. a `Currency` opaque type) at
  the top level, use [`parseAsValue`](parse-as-value.md), which does
  not require a `DefaultParams`.
- For optional / default-valued fields see
  [recipes/optional-fields](../recipes/optional-fields.md) and
  [recipes/default-values](../recipes/default-values.md).

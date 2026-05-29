---
id: recipe-optional-fields
title: "Optional Fields"
category: recipe
layer: application
tags: [recipe, option, optional, derivation]
source_files:
  - /p/gh/toml-scala/core/src/main/scala-3/toml/derivation/auto.scala
  - /p/gh/toml-scala/core/src/main/scala-2/toml/derivation/auto.scala
  - /p/gh/toml-scala/README.md
source_commit: 03d4e5f
api_surface:
  - toml.derivation.auto.op
related:
  - codecs/built-in.md
  - concepts/derivation-model.md
  - derivation/scala-3.md
  - derivation/scala-2.md
see_also:
  - recipes/default-values.md
---

# Optional Fields

Make a case-class field optional by typing it as `Option[T]`. Missing
keys become `None`; present keys are decoded as `Some(t)`.

## Example

```scala
import toml.*
import toml.derivation.auto.*

case class Table(b: Int)
case class Root(a: Int, table: Option[Table])

Toml.parseAs[Root]("a = 1")
// Right(Root(1, None))

Toml.parseAs[Root]("""
  a = 1
  [table]
  b = 2
""")
// Right(Root(1, Some(Table(2))))
```

## How It Works

`Option[T]` is **not** special-cased in the derivation. Instead the
codec for `Option[T]` overrides `optional` to `true`:

```scala
// scala-3/toml/derivation/auto.scala
implicit def op[A](implicit c: Codec[A]): Codec[Option[A]] = new Codec:
  def apply(value, defaults, index) = c(value, defaults, index).map(Some(_))
  override def optional: Boolean = true
```

When the derivation walk sees a missing key whose codec reports
`optional = true`, it inserts `None` (see
[concepts/derivation-model](../concepts/derivation-model.md)).

## Implications

- A **present** `Option[T]` key with a value of the wrong shape still
  fails with the inner codec's mismatch error — it does **not**
  silently become `None`.
- You can write your own optional-wrapper types by overriding
  `optional` on their codec (see [codecs/custom](../codecs/custom.md)).

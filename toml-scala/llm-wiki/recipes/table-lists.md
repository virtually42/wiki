---
id: recipe-table-lists
title: "Table Lists and Inline-Array Shorthand"
category: recipe
layer: application
tags: [recipe, table-list, array-of-tables, inline]
source_files:
  - /p/gh/toml-scala/core/src/main/scala-3/toml/derivation/DerivedProductCodec.scala
  - /p/gh/toml-scala/core/src/main/scala-2/toml/derivation/auto.scala
  - /p/gh/toml-scala/README.md
source_commit: 03d4e5f
api_surface:
  - toml.Codec.listCodec
related:
  - codecs/built-in.md
  - concepts/derivation-model.md
see_also:
  - api/parse-as.md
---

# Table Lists and Inline-Array Shorthand

Decode an array of TOML tables into a `List[CaseClass]`.

## Inline Tables -> Case Class List

```scala
import toml.*
import toml.derivation.auto.*

case class Point(x: Int, y: Int, z: Int)
case class Root(points: List[Point])

val text =
  """points = [ { x = 1, y = 2, z = 3 },
    |           { x = 7, y = 8, z = 9 },
    |           { x = 2, y = 4, z = 8 } ]
  """.stripMargin

Toml.parseAs[Root](text)
// Right(Root(List(Point(1,2,3), Point(7,8,9), Point(2,4,8))))
```

## Positional Array Shorthand

The derivation also accepts a `Value.Arr` of inner `Value.Arr`s,
treating positional element order as field order. So the same
`case class Point(x: Int, y: Int, z: Int)` accepts:

```toml
points = [ [ 1, 2, 3 ],
           [ 7, 8, 9 ],
           [ 2, 4, 8 ] ]
```

How: in [concepts/derivation-model](../concepts/derivation-model.md),
when the working `Value` is a `Value.Arr`, the derivation walks the
head element through the next field's codec and advances the index.
This treats each inner `Value.Arr` as a positional record over
`Point`'s field list.

## Array of Tables (TOML `[[ … ]]`)

```scala
val text =
  """[[products]]
    |name = "a"
    |price = 1
    |
    |[[products]]
    |name = "b"
    |price = 2""".stripMargin

case class Product(name: String, price: Int)
case class Catalog(products: List[Product])

Toml.parseAs[Catalog](text)
// Right(Catalog(List(Product("a", 1), Product("b", 2))))
```

`Embed.addArrayRow` collects each `[[products]]` block into the
`Value.Arr` at key `"products"` — by the time the codec runs, the
shape is identical to the inline-table case.

## Error Address for Bad Elements

`Codec[List[T]]` prepends `"#N"` (1-based) to inner failures. A
mismatched third point would surface as:

```
Left((List("points", "#3", "x"), "Int expected, ... provided"))
```

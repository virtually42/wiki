---
id: recipe-generate-from-ast
title: "Generate TOML from a Hand-Built AST"
category: recipe
layer: application
tags: [recipe, generate, serialize, ast]
source_files:
  - /p/gh/toml-scala/core/src/main/scala/toml/Generate.scala
  - /p/gh/toml-scala/README.md
source_commit: 03d4e5f
api_surface:
  - toml.Toml.generate
  - toml.Generate.generate
related:
  - api/generate.md
  - data/node.md
see_also:
  - data/value.md
---

# Generate TOML from a Hand-Built AST

There is no `case class -> TOML` derivation. To emit TOML, build a
`Root` of `Node`s by hand and pass it to `Toml.generate`.

## Example (from README)

```scala
import toml.*, Node.*, Value.*

val root = Root(List(Pair("scalaDeps", Arr(List(
  Arr(List(Str("io.monix"),       Str("minitest"),  Str("2.2.2"))),
  Arr(List(Str("org.scalacheck"), Str("scalacheck"), Str("1.14.0"))),
  Arr(List(Str("org.scalatest"),  Str("scalatest"),  Str("3.2.0-SNAP10"))),
)))))

Toml.generate(root)
```

Produces:

```toml
scalaDeps = [
  ["io.monix", "minitest", "2.2.2"],
  ["org.scalacheck", "scalacheck", "1.14.0"],
  ["org.scalatest", "scalatest", "3.2.0-SNAP10"]
]
```

## Building Tables and Array-of-Tables

```scala
import toml.*, Node.*, Value.*

val doc = Root(List(
  NamedTable(List("server"), List(
    "host" -> Str("example.com"),
    "port" -> Num(8080),
  )),
  NamedArray(List("products"), List(
    "name" -> Str("a"),
  )),
  NamedArray(List("products"), List(
    "name" -> Str("b"),
  )),
))

Toml.generate(doc)
```

Output:

```toml
[server]
host = "example.com"
port = 8080

[[products]]
name = "a"

[[products]]
name = "b"
```

## Caveats

- **Dates are not rendered.** `Generate.generate(value: Value, …)`
  does not match `Value.Date` / `Value.Time` / `Value.DateTime` /
  `Value.OffsetDateTime` — using them in a `Root` will throw a
  `MatchError` at runtime. Encode as `Value.Str` if you must.
- **Inline tables only.** A `Value.Tbl` inside a `Node.Pair` is
  rendered as `{ k = v, … }`. To emit a `[header]` section you must
  use `Node.NamedTable`.

---
id: api-parse
title: "Toml.parse"
category: api
layer: core
tags: [parse, entry-point, ast]
source_files:
  - /p/gh/toml-scala/core/src/main/scala/toml/Toml.scala
source_commit: 03d4e5f
api_surface:
  - toml.Toml.parse
related:
  - data/value.md
  - data/extension.md
  - concepts/parse-pipeline.md
see_also:
  - api/parse-as.md
  - api/parse-as-value.md
---

# `Toml.parse`

Parse TOML text into the AST.

```scala
def parse(
    toml: String,
    extensions: Set[Extension] = Set(),
): Either[Parse.Error, Value.Tbl]
```

## Behaviour

- Runs the FastParse grammar (`Rules(extensions).root`).
- On success, runs `Embed.root` to resolve `[a.b]` headers and
  `[[items]]` arrays into a single `Value.Tbl`.
- On parser failure, returns `Left((List(), f.msg))`.
- On embed failure (e.g. redefined key), returns the embed error.

## Example

```scala
import toml.*

val text =
  """a = 1
    |[table]
    |b = 2""".stripMargin

Toml.parse(text)
// Right(Value.Tbl(Map("a" -> Value.Num(1), "table" -> Value.Tbl(Map("b" -> Value.Num(2))))))
```

## With Extensions

```scala
Toml.parse(
  """key = {
    |  a = 23,
    |  b = 42,
    |}""".stripMargin,
  Set(Extension.MultiLineInlineTables),
)
```

See [data/extension](../data/extension.md) for the full extension list.

## When To Use

- You want the raw AST (e.g. you are reading TOML whose schema you do
  not know statically, or you want to walk it manually).
- You want to validate that text is well-formed without forcing a
  particular target type.

For typed decoding, use [`Toml.parseAs[T]`](parse-as.md) instead.

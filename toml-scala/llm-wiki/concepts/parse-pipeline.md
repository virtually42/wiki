---
id: concept-parse-pipeline
title: "Parse Pipeline"
category: concept
layer: core
tags: [parser, fastparse, pipeline, embed]
source_files:
  - /p/gh/toml-scala/core/src/main/scala/toml/Toml.scala
  - /p/gh/toml-scala/core/src/main/scala/toml/Rules.scala
  - /p/gh/toml-scala/core/src/main/scala/toml/Embed.scala
  - /p/gh/toml-scala/core/src/main/scala/toml/PlatformRules.scala
source_commit: 03d4e5f
api_surface:
  - toml.Toml.parse
  - toml.Rules
  - toml.Embed.root
related:
  - concepts/ast-model.md
  - data/extension.md
  - data/parse-error.md
see_also:
  - api/parse.md
  - api/parse-as.md
---

# Parse Pipeline

```
String
  -> fastparse.parse(input, Rules(extensions).root)
       -> Parsed.Success(Root)   |   Parsed.Failure(msg)
  -> Embed.root(Root)
       -> Right(Value.Tbl)       |   Left(Parse.Error)
  -> [optional] Codec[A].apply(value, defaults, 0)
       -> Right(A)               |   Left(Parse.Error)
```

## Stage 1: fastparse Rules

`toml.Rules` (extends `PlatformRules`) is a FastParse grammar. It is
instantiated per call because parser behaviour depends on the
[`Extension`](../data/extension.md) set:

```scala
new Rules(extensions).root(_)
```

Key productions (all `[$: P]`):

| Production | Produces |
|------------|----------|
| `string` | `Value.Str` (basic, literal, multi-line, both) |
| `integer` / `double` | `Value.Num` / `Value.Real` (handles `_`, `inf`, `nan`, signs) |
| `boolean` | `Value.Bool` |
| `array` | `Value.Arr` |
| `inlineTable` | `Value.Tbl` (multi-line variant gated by `MultiLineInlineTables`) |
| `date` (from `PlatformRules`) | `Date` / `Time` / `DateTime` / `OffsetDateTime` |
| `pairNode` / `table` / `tableArray` | `Node.Pair` / `Node.NamedTable` / `Node.NamedArray` |
| `root` | `Root` |

`elem` is the alternation of all scalar / container productions:

```scala
date | string | boolean | double | integer | array | inlineTable
```

The `node` rule selects between `pairNode | table | tableArray`.

## Stage 2: Embed

`Embed.root: Root -> Either[Parse.Error, Value.Tbl]` walks the node
list and merges them into a single table. It enforces:

- **No redefinition** — `addPair` returns
  `Left((stack :+ key) -> "Cannot redefine value")` if a key is set
  twice.
- **Header path resolution** — `updateTable` recurses into nested tables
  on the path (`List("a", "b")` -> descend `a`, then `b`).
- **Array-of-tables** — `addArrayRow` appends to a `Value.Arr` of
  `Value.Tbl` rows when it sees `[[ref]]`.

The error type is `Parse.Error = (List[String], String)` — an
addressable error path plus a message. See
[data/parse-error](../data/parse-error.md).

## Stage 3 (optional): Codec

When you call `parseAs[T]` instead of `parse`, the resulting `Value.Tbl`
is fed to a `Codec[T]`. See [codecs/built-in](../codecs/built-in.md).

## Entry Points

All entry points live on `object Toml`:

| Method | Returns | When to use |
|--------|---------|-------------|
| `parse(s, exts)` | `Either[Parse.Error, Value.Tbl]` | You want the raw AST |
| `parseAs[T](s)` | `Either[Parse.Error, T]` | You want a case class |
| `parseAs[T](tbl)` | `Either[Parse.Error, T]` | You already have a `Value.Tbl` |
| `parseAsValue[T](s)` | `Either[Parse.Error, T]` | Decode without `DefaultParams` plumbing |
| `parseAsValue[T](v)` | `Either[Parse.Error, T]` | Decode an arbitrary `Value` directly |
| `generate(root)` | `String` | Render a `Root` back to TOML |

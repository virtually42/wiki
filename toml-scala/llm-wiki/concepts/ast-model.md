---
id: concept-ast-model
title: "AST Model: Value, Node, Root"
category: concept
layer: core
tags: [ast, value, node, root, model]
source_files:
  - /p/gh/toml-scala/core/src/main/scala/toml/Value.scala
  - /p/gh/toml-scala/core/src/main/scala/toml/Node.scala
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
  - toml.Node
  - toml.Node.Pair
  - toml.Node.NamedTable
  - toml.Node.NamedArray
  - toml.Root
related:
  - data/value.md
  - data/node.md
  - concepts/parse-pipeline.md
see_also:
  - api/parse.md
---

# AST Model

toml-scala uses two layered AST shapes:

1. **`Root` / `Node`** — the syntactic AST as it appears on the page,
   preserving table-header structure (`[a.b.c]`, `[[items]]`).
2. **`Value.Tbl` tree** — the semantic AST where headers have been
   resolved into nested tables.

`Embed.root` is the bridge between them. See
[concepts/parse-pipeline](parse-pipeline.md).

## Value

`Value` is the sum type of all TOML scalars and containers:

| Case | TOML kind |
|------|-----------|
| `Value.Str(String)` | basic / literal / multi-line strings |
| `Value.Bool(Boolean)` | `true` / `false` |
| `Value.Num(Long)` | integers (with `_` underscore separators allowed) |
| `Value.Real(Double)` | floats (incl. `inf`, `nan`) |
| `Value.Tbl(Map[String, Value])` | `{ … }` inline tables and `[header]` tables |
| `Value.Arr(List[Value])` | `[ … ]` arrays |
| `Value.Date(LocalDate)` | `1979-05-27` |
| `Value.Time(LocalTime)` | `07:32:00.999` |
| `Value.DateTime(LocalDateTime)` | `1979-05-27T07:32:00` |
| `Value.OffsetDateTime(OffsetDateTime)` | `1979-05-27T07:32:00Z` |

Date and time cases are defined on the platform mix-in
`PlatformValue`, which is mixed into `object Value`. They use
`java.time` on every platform (on Scala.js / Native via
`scala-java-time`).

> Note: `trait Value` is **not** sealed (the source has `/*sealed*/`
> commented out). Treat it as effectively sealed — adding new cases is
> not part of the public API.

## Node

`Node` represents the *top-level syntactic constructs* before headers
are resolved:

```scala
sealed trait Node
object Node {
  case class Pair(key: String, value: Value) extends Node
  case class NamedTable(ref: List[String], values: List[(String, Value)]) extends Node
  case class NamedArray(ref: List[String], values: List[(String, Value)]) extends Node
}
case class Root(nodes: List[Node])
```

- `Pair` — a top-level `key = value`
- `NamedTable` — a `[a.b.c]` header followed by pairs
- `NamedArray` — a `[[a.b.c]]` header followed by pairs

`ref` is the **already-split path** (`List("a", "b", "c")`).

## Why two ASTs

Header semantics are not local: `[a.b]` must merge into a previously
created `[a]` table, and `[[items]]` appends to an array. Keeping the
syntactic shape (`Node`) lets the parser stay context-free; `Embed`
performs the path merging in a second pass, returning a clean
`Value.Tbl` tree.

`Codec[A]` only ever sees the `Value.Tbl` tree, never `Node`.

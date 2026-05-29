---
id: data-node
title: "Node ADT and Root"
category: data
layer: core
tags: [node, root, syntactic, header, array-of-tables]
source_files:
  - /p/gh/toml-scala/core/src/main/scala/toml/Node.scala
source_commit: 03d4e5f
api_surface:
  - toml.Node
  - toml.Node.Pair
  - toml.Node.NamedTable
  - toml.Node.NamedArray
  - toml.Root
related:
  - data/value.md
  - concepts/ast-model.md
  - concepts/parse-pipeline.md
see_also:
  - api/generate.md
---

# `Node` and `Root`

The **syntactic** AST that the parser emits before `Embed.root`
collapses headers into a nested `Value.Tbl`.

```scala
package toml

sealed trait Node
object Node {
  case class Pair(key: String, value: Value) extends Node
  case class NamedTable(ref: List[String], values: List[(String, Value)]) extends Node
  case class NamedArray(ref: List[String], values: List[(String, Value)]) extends Node
}

case class Root(nodes: List[Node])
```

## Mapping from TOML

```
a = 1                                Node.Pair("a", Value.Num(1))

[server]                             Node.NamedTable(
host = "x"                             ref    = List("server"),
                                       values = List("host" -> Value.Str("x")))

[server.tls]                         Node.NamedTable(
enabled = true                         ref    = List("server", "tls"),
                                       values = List("enabled" -> Value.Bool(true)))

[[products]]                         Node.NamedArray(
name = "a"                             ref    = List("products"),
                                       values = List("name" -> Value.Str("a")))
```

`ref` is **already split** at the parser level — no further dotted-path
parsing is needed by consumers.

## When You See `Node`

- After calling the parser at a lower level than `toml.Toml.parse`
  (which always runs `Embed`).
- When you build a TOML document programmatically for
  [`Toml.generate`](../api/generate.md) — `generate` accepts a `Root`,
  not a `Value`.

For typical use you will **not** see `Node` — the high-level `parse` /
`parseAs` APIs return `Value.Tbl` after embedding.

## Notes

- `Node` *is* `sealed`; pattern matches are exhaustive.
- `Node.NamedTable` and `Node.NamedArray` share the same shape; only
  the syntax (`[…]` vs `[[…]]`) and `Embed` semantics differ.
- `Node.Pair`'s key is the literal TOML key with no dotted-path split
  (top-level dotted keys produce a `Pair` whose key is the dotted
  string only after the parser's `validKey` handles quoting — see
  `Rules.pair`).

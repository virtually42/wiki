---
id: api-generate
title: "Toml.generate"
category: api
layer: core
tags: [generate, render, emit, serialize]
source_files:
  - /p/gh/toml-scala/core/src/main/scala/toml/Toml.scala
  - /p/gh/toml-scala/core/src/main/scala/toml/Generate.scala
source_commit: 03d4e5f
api_surface:
  - toml.Toml.generate
  - toml.Generate.generate
related:
  - data/value.md
  - data/node.md
see_also:
  - concepts/ast-model.md
---

# `Toml.generate`

Render an AST back to TOML text.

```scala
// On Toml
def generate(root: Root): String

// On Generate (lower-level)
def generate(value: Value, level: Int = 0): String
def generate(node: Node): String
def generate(root: Root): String
```

## Output Rules

### Values

- `Value.Str` — JSON-style quoted with `Escape.escapeJavaString`
- `Value.Bool` — `"true"` / `"false"`
- `Value.Num` / `Value.Real` — `.toString`
- `Value.Tbl` — inline form `{ k = v, k = v }`
- `Value.Arr` —
  - If `length > 1` and `level == 0`, multi-line:
    ```
    [
      a,
      b
    ]
    ```
  - Otherwise single-line `[a, b]`
- Date/Time values: not currently emitted by `Generate.generate`
  (`Value` is matched only on the seven non-date cases) — round-tripping
  date values is a gap. Encode them manually or to a `Value.Str` if
  you need to emit them.

### Nodes

- `Node.Pair(k, v)` -> `k = v`
- `Node.NamedTable(ref, vs)` -> `[a.b.c]\nk = v\n…` with `generateRef`
  quoting path segments containing `.`, whitespace, or escape chars.
- `Node.NamedArray(ref, vs)` -> `[[a.b.c]]\n…`

### Root

`Root` nodes are joined with `"\n"`. A trailing newline is inserted
between successive non-pair nodes; pair-to-pair transitions stay on
adjacent lines.

## Example

```scala
import toml.*, Node.*, Value.*

val root = Root(List(Pair("scalaDeps", Arr(List(
  Arr(List(Str("io.monix"), Str("minitest"), Str("2.2.2"))),
  Arr(List(Str("org.scalacheck"), Str("scalacheck"), Str("1.14.0"))),
)))))

Toml.generate(root)
```

Produces:

```toml
scalaDeps = [
  ["io.monix", "minitest", "2.2.2"],
  ["org.scalacheck", "scalacheck", "1.14.0"]
]
```

## Limitations

- No automatic case-class -> `Root` encoder is provided. You must
  build the `Root` yourself.
- Date/time `Value` cases are not currently rendered (will hit a
  non-exhaustive match at runtime).

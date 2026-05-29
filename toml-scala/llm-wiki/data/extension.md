---
id: data-extension
title: "Extension"
category: data
layer: core
tags: [extension, multi-line-inline-tables]
source_files:
  - /p/gh/toml-scala/core/src/main/scala/toml/Rules.scala
source_commit: 03d4e5f
api_surface:
  - toml.Extension
  - toml.Extension.MultiLineInlineTables
related:
  - api/parse.md
  - api/parse-as.md
  - concepts/parse-pipeline.md
---

# `Extension`

Opt-in non-standard TOML grammar features.

```scala
sealed trait Extension
object Extension {
  case object MultiLineInlineTables extends Extension
}
```

## Available Extensions

| Extension | Effect |
|-----------|--------|
| `MultiLineInlineTables` | Allow newlines and trailing commas inside `{ … }` inline tables (see [toml-lang/toml#516](https://github.com/toml-lang/toml/issues/516)) |

## Activation

Pass the set as the second argument to `parse` / `parseAs`:

```scala
toml.Toml.parse(
  """key = {
    |  a = 23,
    |  b = 42,
    |}""".stripMargin,
  Set(Extension.MultiLineInlineTables),
)
```

Default is `Set()` — strict standards mode.

## Implementation Note

`Rules` selects between two parser variants for `inlineTable`:

```scala
def inlineTable[$: P]: P[Value.Tbl] =
  (if (extensions.contains(MultiLineInlineTables))
     P("{" ~ skip   ~ pair.rep(sep = skip   ~ "," ~ skip)   ~ ",".? ~ skip   ~ "}")
   else
     P("{" ~ skipWs ~ pair.rep(sep = skipWs ~ "," ~ skipWs) ~          skipWs ~ "}")
  ).map(p => Value.Tbl(p.toMap))
```

The non-extended path uses `skipWs` (only horizontal whitespace) and
disallows a trailing comma. The extended path uses `skip` (whitespace +
newlines + comments) and allows the trailing comma.

# toml-scala LLM-Wiki

Query-optimized knowledge base for `toml-scala` —
a standards-compliant TOML parser, codec, and generator for Scala 2.12,
2.13, and 3 on JVM / Scala.js / Scala Native.

- **Maven coordinate**: `com.indoorvivants %%(% toml % <version>`
- **Source**: `/p/gh/toml-scala` (fork of upstream)
- **Upstream**: https://github.com/indoorvivants/toml-scala
- **Bridge**: [[sources/raw/code/toml-scala]]

## Quick Lookup

| I want to... | Start here |
|---|---|
| Parse a TOML string to an AST | [api/parse](api/parse.md) |
| Parse a TOML string into a case class | [api/parse-as](api/parse-as.md) |
| Decode a `Value.Tbl` I already have | [api/parse-as-value](api/parse-as-value.md) |
| Render an AST back to TOML text | [api/generate](api/generate.md) |
| Understand the AST | [data/value](data/value.md), [data/node](data/node.md) |
| See the error type | [data/parse-error](data/parse-error.md) |
| Enable multi-line inline tables | [data/extension](data/extension.md) |
| Write a custom codec | [recipes/custom-codec](recipes/custom-codec.md) |
| Use optional case-class fields | [recipes/optional-fields](recipes/optional-fields.md) |
| Use default values on a case class | [recipes/default-values](recipes/default-values.md) |
| Parse a list of inline tables onto a `case class` list | [recipes/table-lists](recipes/table-lists.md) |
| Understand built-in codecs (Int, List, Map…) | [codecs/built-in](codecs/built-in.md) |
| Decode dates / times | [codecs/date-time](codecs/date-time.md) |
| Derive codecs on Scala 3 | [derivation/scala-3](derivation/scala-3.md) |
| Derive codecs on Scala 2 | [derivation/scala-2](derivation/scala-2.md) |
| Understand the parse pipeline | [concepts/parse-pipeline](concepts/parse-pipeline.md) |
| Understand how derivation walks tables | [concepts/derivation-model](concepts/derivation-model.md) |

## Sections

- [concepts/](concepts/index.md) — mental models (AST shape, parse pipeline,
  derivation walk, error addressing)
- [api/](api/index.md) — entry points on `toml.Toml`
- [data/](data/index.md) — `Value`, `Node`, `Root`, `Extension`, `Parse.Error`
- [codecs/](codecs/index.md) — built-in codecs and custom codec authoring
- [derivation/](derivation/index.md) — automatic case-class codecs
  (Scala 2 via Shapeless 2, Scala 3 via Shapeless 3)
- [recipes/](recipes/index.md) — task-oriented examples

## Pipeline Overview

```
TOML text
  -> fastparse Rules        (concepts/parse-pipeline)
  -> Root(List[Node])       (data/node)
  -> Embed.root             (concepts/parse-pipeline, data/value)
  -> Value.Tbl              (data/value)
  -> Codec[A]               (codecs/built-in, codecs/custom)
  -> A                      (your case class)
```

Generation is the reverse: `Root -> Generate.generate -> String`
(see [api/generate](api/generate.md)).

## Cross-Platform Notes

- JVM uses `java.time.*` natively.
- Scala.js / Scala Native depend on
  `io.github.cquiroz::scala-java-time` for date/time support. Cannot
  be opted out of (see [codecs/date-time](codecs/date-time.md)).
- Derivation has two backends:
  - Scala 2.12 / 2.13 uses Shapeless 2 (`com.chuusai::shapeless`)
  - Scala 3 uses Shapeless 3 (`org.typelevel::shapeless3-deriving`)

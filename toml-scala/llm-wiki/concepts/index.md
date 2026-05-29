# Concepts

Mental models for using `toml-scala` effectively.

| Page | Topic |
|------|-------|
| [ast-model](ast-model.md) | The two layered ASTs: `Root`/`Node` (syntactic) vs `Value` (semantic) |
| [parse-pipeline](parse-pipeline.md) | `String -> fastparse Rules -> Root -> Embed -> Value.Tbl -> Codec -> A` |
| [derivation-model](derivation-model.md) | How the Scala 2 / Scala 3 derivations walk a `Value.Tbl` and consume keys |
| [error-model](error-model.md) | `Parse.Error = (Address, Message)`; where each error comes from |

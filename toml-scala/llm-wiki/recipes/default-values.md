---
id: recipe-default-values
title: "Default Values on Case Classes"
category: recipe
layer: application
tags: [recipe, defaults, case-class, derivation]
source_files:
  - /p/gh/toml-scala/core/src/main/scala-3/toml/derivation/ProductDefaults.scala
  - /p/gh/toml-scala/core/src/main/scala-3/toml/derivation/ProductDefaultsMacro.scala
  - /p/gh/toml-scala/core/src/main/scala-2/toml/util/RecordToMap.scala
source_commit: 03d4e5f
api_surface:
  - toml.derivation.DefaultParams
  - toml.derivation.macros.defaultParams
related:
  - concepts/derivation-model.md
  - derivation/scala-3.md
  - derivation/scala-2.md
see_also:
  - recipes/optional-fields.md
---

# Default Values on Case Classes

Give a case-class field a default — missing keys fall back to the
default rather than failing.

## Example

```scala
import toml.*
import toml.derivation.auto.*

case class Server(host: String, port: Int = 8080)

Toml.parseAs[Server]("""host = "example.com"""")
// Right(Server("example.com", 8080))

Toml.parseAs[Server]("""
  host = "example.com"
  port = 9090
""")
// Right(Server("example.com", 9090))
```

## Resolution Order

For a missing field the derivation walks:

1. Is there a registered **default** for this field? Use it.
2. Otherwise, does the field's codec report `optional = true` (e.g.
   `Option[T]`)? Insert `None`.
3. Otherwise, fail: `` Cannot resolve `<field>` ``.

See [concepts/derivation-model](../concepts/derivation-model.md).

## How Defaults Are Collected

### Scala 3

A macro inspects the case class's companion class for synthetic
methods named `$lessinit$greater$default$N` and pairs them with field
names flagged `Flags.HasDefault`:

```scala
// scala-3/toml/derivation/ProductDefaultsMacro.scala
val names =
  for p <- sym.caseFields if p.flags.is(Flags.HasDefault)
  yield p.name
```

`DefaultParams.inst` materialises a `Map[String, Any]` at the call
site of `Toml.parseAs`.

### Scala 2

Shapeless `Default.AsRecord` produces an `HList` of default values.
`util.RecordToMap` flattens that into `Map[String, Any]`. `genericCodec`
in `auto.scala` wires it in.

## Optional vs Default

Both fall through to the same `defaults: Map[String, Any]` plumbing.
The differences:

| | `Option[T]` field | Defaulted field |
|---|---|---|
| Result when key absent | `None` | the default value |
| Result when key present | `Some(t)` if inner codec succeeds | inner codec result directly |
| Inner codec must succeed when present | yes | yes |

You can combine the two: `field: Option[T] = None` works as
expected.

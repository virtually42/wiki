---
id: derivation-scala-2
title: "Codec Derivation (Scala 2)"
category: derivation
layer: integration
tags: [derivation, scala-2, shapeless, hlist, labelled-generic]
source_files:
  - /p/gh/toml-scala/core/src/main/scala-2/toml/derivation/auto.scala
  - /p/gh/toml-scala/core/src/main/scala-2/toml/derivation/syntax.scala
  - /p/gh/toml-scala/core/src/main/scala-2/toml/util/RecordToMap.scala
  - /p/gh/toml-scala/core/src/main/scala-2/toml/TomlVersionSpecific.scala
source_commit: 03d4e5f
api_surface:
  - toml.derivation.auto
  - toml.derivation.LowPriorityCodecs
  - toml.util.RecordToMap
related:
  - derivation/scala-3.md
  - concepts/derivation-model.md
  - codecs/built-in.md
see_also:
  - api/parse-as.md
  - recipes/default-values.md
  - recipes/optional-fields.md
---

# Codec Derivation — Scala 2

Scala 2.12 / 2.13 derivation is built on **Shapeless 2**
(`com.chuusai::shapeless`).

## Import Once

```scala
import toml._
import toml.derivation.auto._
```

`auto` extends `LowPriorityCodecs with PlatformCodecs` and provides:

- `Codec[HNil]` — terminal, fails if the table or array still has
  elements.
- `hconsFromNode[K, V, T]` — required field.
- `hconsFromNodeOpt[K, V, T]` — optional (`Option[V]`) field, given
  lower priority via `LowPriorityCodecs`.
- `genericCodec[A, D, R]` — bridges between a `LabelledGeneric[A]`
  representation and the `HList` codec, threading the defaults through
  `util.RecordToMap`.

## How the Walk Works

For each `hcons`, the witness gives the field name; the codec:

1. If input is a `Value.Tbl` and contains the field name — decode it
   with `Codec[V]`, recurse on `Value.Tbl(pairs - witnessName)`.
2. If input is a `Value.Arr` — decode the head as `V`, recurse on
   `Value.Arr(values.drop(1))` with `index + 1`.
3. For `hconsFromNodeOpt` only: if the field is absent and no default
   is registered, set `None`. If the field is absent but a default
   exists in `defaults`, use the default.
4. For `hconsFromNode`: if the field is absent but a default exists,
   use the default; otherwise fail with `` Cannot resolve `<field>` ``.

`Codec[HNil]` finally checks the residue: any leftover table keys
become `Unknown field`; any leftover array elements become
`Too many elements; remove <head>`.

## Default Parameters

`util.RecordToMap` flattens Shapeless's `Default.AsRecord`
representation into a `Map[String, Any]`:

```scala
implicit def hconsRecordToMap[K <: Symbol, V, T <: HList](implicit
    wit: Witness.Aux[K],
    rtmT: RecordToMap[T],
): RecordToMap[FieldType[K, V] :: T] = ...
```

`genericCodec` applies it once at the top of derivation and passes the
result through the entire codec chain via `Codec.Defaults`.

## CodecHelperGeneric

`Toml.parseAs[T]` summons:

```scala
implicit
  generic:       LabelledGeneric.Aux[A, R],
  defaults:      Default.AsRecord.Aux[A, D],
  defaultMapper: util.RecordToMap[D],
  codec:         Codec[R],
```

`parseAsValue[A]` only needs an inner `Codec[A]` — use it for non
product types or single-value decodes.

## Worked Example

```scala
import toml._
import toml.derivation.auto._

case class Server(host: String, port: Int = 8080)
case class Config(server: Server, debug: Option[Boolean])

Toml.parseAs[Config]("""
  [server]
  host = "example.com"
""")
// Right(Config(Server("example.com", 8080), None))
```

## Implementation Source

The `genericCodec` follows the standard Shapeless 2 recipe; the
`RecordToMap` helper is copied verbatim (with attribution) from
Circe's `circe-generic-extras` (see comment in
`util/RecordToMap.scala`).

---
id: derivation-scala-3
title: "Codec Derivation (Scala 3)"
category: derivation
layer: integration
tags: [derivation, scala-3, shapeless3, macro, default-params]
source_files:
  - /p/gh/toml-scala/core/src/main/scala-3/toml/derivation/auto.scala
  - /p/gh/toml-scala/core/src/main/scala-3/toml/derivation/DerivedProductCodec.scala
  - /p/gh/toml-scala/core/src/main/scala-3/toml/derivation/Context.scala
  - /p/gh/toml-scala/core/src/main/scala-3/toml/derivation/ProductDefaults.scala
  - /p/gh/toml-scala/core/src/main/scala-3/toml/derivation/ProductDefaultsMacro.scala
  - /p/gh/toml-scala/core/src/main/scala-3/toml/derivation/syntax.scala
  - /p/gh/toml-scala/core/src/main/scala-3/toml/TomlVersionSpecific.scala
source_commit: 03d4e5f
api_surface:
  - toml.derivation.auto
  - toml.derivation.auto.derivedProductCodec
  - toml.derivation.auto.op
  - toml.derivation.DerivedProductCodec
  - toml.derivation.DefaultParams
  - toml.derivation.macros.defaultParams
related:
  - derivation/scala-2.md
  - concepts/derivation-model.md
  - codecs/built-in.md
see_also:
  - api/parse-as.md
  - recipes/default-values.md
  - recipes/optional-fields.md
---

# Codec Derivation — Scala 3

Scala 3 derivation is built on **Shapeless 3**
(`org.typelevel::shapeless3-deriving`) plus a small `quoted.*` macro
to extract `case class` default values.

## Import Once

```scala
import toml.*
import toml.derivation.auto.*
```

`auto` provides:

```scala
inline implicit def derivedProductCodec[P](using
    inline codec: DerivedProductCodec[P],
): Codec[P]

implicit def op[A](implicit c: Codec[A]): Codec[Option[A]]
```

`derivedProductCodec` lifts a `DerivedProductCodec[P]` (the actual
typeclass) into the `Codec[P]` slot that `parseAs` / `parseAsValue`
search for. The `inline` propagates so derivation only fires at the
true call site.

## What Gets Derived

`DerivedProductCodec[P]` has a single given:

```scala
given codecGen[P](using
    inst: K0.ProductInstances[Codec, P],
    labelling: Labelling[P],
    d: DefaultParams[P],
): DerivedProductCodec[P]
```

So derivation requires:

1. `P` is a product (case class) — provided by `K0.ProductInstances`.
2. A `Codec[F]` for every field type `F` — found by usual implicit
   search.
3. A `DefaultParams[P]` — auto-derived via the
   `derivation.macros.defaultParams` macro for any product.

## How the Walk Works

`codecGen.apply` calls `inst.unfold(Context(value, elemLabels, index))`
and per-field invokes `unfold[T](defaults, ctx, codec)`. See
[concepts/derivation-model](../concepts/derivation-model.md) for the
full state machine. Summary:

- The working table shrinks as each key is consumed.
- Missing keys fall back to `DefaultParams[P]` -> `optional` -> fail.
- Leftover keys produce `Unknown field` at the end.

## Default Parameters

The macro `derivation.macros.defaultParams[T]` inspects the case
class's companion class for synthetic methods named
`$lessinit$greater$default$N` and pairs them with the names of fields
flagged `Flags.HasDefault`:

```scala
case class Server(host: String, port: Int = 8080)
// macro materialises Map("port" -> 8080)
```

`DefaultParams.inst` wraps the macro in a typeclass and supplies a
`given` for any `P <: Product`.

## CodecHelperGeneric

`Toml.parseAs[T]` returns `CodecHelperGeneric[T]`, whose `apply`
methods require both `Codec[T]` and `DefaultParams[T]`:

```scala
def apply(toml: String)(using
    codec: Codec[T],
    D: DefaultParams[T],
): Either[Parse.Error, T] =
  apply(toml, Set.empty)
```

`parseAsValue` uses `CodecHelperValue[A]` which **does not** require
`DefaultParams` — useful for non-product types.

## Failure Modes

- **No `Codec[F]` for a field** —
  `Codec[F] implicit not defined in scope` (from
  `@implicitNotFound` on `Codec`).
- **Not a product** — Shapeless 3 will fail to find
  `K0.ProductInstances[Codec, P]`.

## Worked Example

```scala
import toml.*
import toml.derivation.auto.*

case class TLS(enabled: Boolean = false)
case class Server(host: String, port: Int = 8080, tls: TLS = TLS())
case class Config(server: Server)

Toml.parseAs[Config]("""
  [server]
  host = "example.com"
""")
// Right(Config(Server("example.com", 8080, TLS(false))))
```

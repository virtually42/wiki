---
id: concept-derivation-model
title: "Derivation Model"
category: concept
layer: integration
tags: [derivation, shapeless, codec, scala-3, scala-2, context]
source_files:
  - /p/gh/toml-scala/core/src/main/scala-3/toml/derivation/DerivedProductCodec.scala
  - /p/gh/toml-scala/core/src/main/scala-3/toml/derivation/Context.scala
  - /p/gh/toml-scala/core/src/main/scala-2/toml/derivation/auto.scala
source_commit: 03d4e5f
api_surface:
  - toml.derivation.DerivedProductCodec
  - toml.derivation.Context
  - toml.derivation.auto
  - toml.derivation.DefaultParams
related:
  - derivation/scala-3.md
  - derivation/scala-2.md
  - codecs/built-in.md
see_also:
  - recipes/optional-fields.md
  - recipes/default-values.md
---

# Derivation Model

Both Scala 2 and Scala 3 implementations of automatic codec derivation
share the same conceptual model, even though the underlying machinery
(Shapeless 2 `HList` vs Shapeless 3 `K0.ProductInstances`) is
different.

## Stateful Walk

Derivation is **stateful**: as each case-class field is resolved, that
field is **removed** from the working `Value.Tbl`. After all fields are
consumed, the table should be empty — any remaining keys are reported
as `Unknown field`.

On Scala 3 the state lives in `Context`:

```scala
private final case class Context(
    tomlValue: Value,        // shrinking working table or array tail
    labels: Seq[String],     // remaining field names to consume
    index: Int,              // current index when reading an array
    error: Parse.Error,      // accumulated error address + message
)
```

On Scala 2 the same shrinking is performed by `hcons` instances over an
`HList`: each step removes a key from the table (`Value.Tbl(pairs -
witnessName)`) and consumes the head of the array.

## Resolution Rules (per field)

For each `case class` field `head` of type `T`:

1. **Table input, key present** — decode with the field's `Codec[T]`
   and recurse on the smaller table.
2. **Table input, key absent**:
   - If there is a **default** for the field (see
     [`DefaultParams`](../derivation/scala-3.md)), use it.
   - Else if the field's `Codec` reports `optional = true` (i.e. it is
     `Option[_]`), insert `None`.
   - Else fail with `Cannot resolve `<key>``.
3. **Array input** — decode the head element as `T`, recurse on the
   tail with `index + 1`.
4. **Anything else** — fail.

Step 3 is what makes
[`points = [ [1, 2, 3] ]`](../recipes/table-lists.md) work as a
shorthand for `points = [ { x = 1, y = 2, z = 3 } ]`.

## Optional fields are codec-level

`Option[A]` is **not** handled by special-casing the field type. Instead,
the codec for `Option[A]` overrides `optional` to `true`:

```scala
// scala-3/toml/derivation/auto.scala
implicit def op[A](implicit c: Codec[A]): Codec[Option[A]] = new Codec:
  def apply(value, defaults, index): Either[Parse.Error, Option[A]] =
    c.apply(value, defaults, index).map(Some(_))
  override def optional: Boolean = true
```

When resolution sees a missing key, it asks the codec
`if codec.optional then ... Some(None)`. This is why custom optional
codecs work transparently.

## Defaults

Scala 3 defaults come from a macro (`derivation.macros.defaultParams`)
that inspects the case class's companion for synthetic
`$lessinit$greater$default$N` methods and pairs them with
`HasDefault` field names. See
[derivation/scala-3](../derivation/scala-3.md).

Scala 2 uses Shapeless's `Default.AsRecord` plus the local
`util.RecordToMap` to materialise the same `Map[String, Any]`.

In both cases the defaults reach the codec via
`Codec.Defaults = Map[String, Any]`.

## Error Accumulation

The `Context.error` (or, on Scala 2, the `Left` carried through
`flatMap`) records the **last failure address**. When the derivation
finishes with leftover keys but a recorded error message, the leftover
keys take precedence (`Unknown field`) unless the error already has a
message — see the closing `match` in `DerivedProductCodec.apply`.

---
id: codec-built-in
title: "Built-in Codecs"
category: codec
layer: integration
tags: [codec, primitive, list, map, implicit]
source_files:
  - /p/gh/toml-scala/core/src/main/scala/toml/Codec.scala
source_commit: 03d4e5f
api_surface:
  - toml.Codec
  - toml.Codec.stringCodec
  - toml.Codec.longCodec
  - toml.Codec.intCodec
  - toml.Codec.doubleCodec
  - toml.Codec.boolCodec
  - toml.Codec.listCodec
  - toml.Codec.tableCodec
related:
  - codecs/date-time.md
  - codecs/custom.md
  - concepts/error-model.md
see_also:
  - api/parse-as.md
  - api/parse-as-value.md
---

# Built-in Codecs

```scala
@implicitNotFound("Codec[${A}] implicit not defined in scope")
trait Codec[A] {
  def apply(value: Value, defaults: Codec.Defaults, index: Int): Either[Parse.Error, A]
  private[toml] def optional: Boolean = false
}

object Codec extends DerivedSyntax {
  type Defaults = Map[String, Any]
  type Index    = Int

  def apply[T](f: (Value, Defaults, Index) => Either[Parse.Error, T]): Codec[T] = ...
}
```

The `Codec` companion ships implicit instances for the common scalar
and container types:

| `Codec[T]` | Accepts | Produces |
|-----------|---------|----------|
| `Codec[String]`  | `Value.Str(s)`  | `s` |
| `Codec[Long]`    | `Value.Num(n)`  | `n` |
| `Codec[Int]`     | `Value.Num(n)`  | `n.toInt` (truncates `Long`) |
| `Codec[Double]`  | `Value.Real(d)` | `d` |
| `Codec[Boolean]` | `Value.Bool(b)` | `b` |
| `Codec[List[T]]` | `Value.Arr(xs)` | List via inner `Codec[T]`, address `"#N"` |
| `Codec[Map[String, T]]` | `Value.Tbl(m)` | Map via inner `Codec[T]`, address `key` |

Date/time codecs (`LocalDate`, `LocalTime`, `LocalDateTime`,
`OffsetDateTime`) live on `PlatformCodecs`, which is mixed into
`toml.derivation.auto`. See [codecs/date-time](date-time.md).

## Codec Signature

The full signature carries two extra arguments beyond `Value`:

- `defaults: Map[String, Any]` — defaults table passed in by the
  derivation machinery so that nested codecs can ask "did the enclosing
  product have a default for me?"
- `index: Int` — the current array index, used to emit `#N` segments in
  error addresses when decoding `List`s.

For top-level user-defined codecs, both are usually ignored — see
[codecs/custom](custom.md).

## Address Forwarding

`Codec[List[T]]` shows the pattern:

```scala
implicit def listCodec[T](implicit codec: Codec[T]): Codec[List[T]] = Codec {
  case (Value.Arr(elems), _, _) =>
    elems.zipWithIndex.foldLeft(...) { case (Right(acc), (cur, idx)) =>
      codec(cur, Map.empty, 0).left
        .map { case (a, m) => (s"#${idx + 1}" +: a, m) }
        ...
    }
  case (value, _, _) => Left((List.empty, s"List expected, $value provided"))
}
```

Each element is decoded; on failure the index segment `"#N"` is
**prepended** to the error address. `Codec[Map[String, T]]` does the
same with the key segment.

## Type Mismatch Errors

The default codecs all return messages of the form
`"<Type> expected, <Value> provided"`. This is the error you see when
field types disagree:

```
Long expected, Value.Str("x") provided
```

## Optionality

`optional` is overridden to `true` only on the codecs for `Option[A]`
(defined in `toml.derivation.auto`). See
[concepts/derivation-model](../concepts/derivation-model.md).

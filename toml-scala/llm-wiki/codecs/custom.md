---
id: codec-custom
title: "Writing Custom Codecs"
category: codec
layer: integration
tags: [codec, custom, implicit, pattern]
source_files:
  - /p/gh/toml-scala/core/src/main/scala/toml/Codec.scala
source_commit: 03d4e5f
api_surface:
  - toml.Codec.apply
related:
  - codecs/built-in.md
  - concepts/error-model.md
see_also:
  - recipes/custom-codec.md
---

# Writing Custom Codecs

`Codec.apply` is the constructor — pass a function of three arguments:

```scala
Codec[T] { (value: Value, defaults: Codec.Defaults, index: Int) =>
  // returns Either[Parse.Error, T]
}
```

For most user-defined types the `defaults` and `index` arguments are
ignored and the function reduces to a pattern match on `value`.

## Skeleton

```scala
import toml.*

case class Currency(name: String)

implicit val currencyCodec: Codec[Currency] = Codec {
  case (Value.Str(s), _, _) =>
    s match {
      case "EUR" => Right(Currency("EUR"))
      case "BTC" => Right(Currency("BTC"))
      case _     => Left((List(), s"Invalid currency: $s"))
    }

  case (value, _, _) =>
    Left((List(), s"Currency expected, $value provided"))
}
```

## Error Address Discipline

When your codec **delegates** to other codecs (typical when decoding a
container or wrapper), preserve the address of any inner failure and
prepend your own segment:

```scala
implicit def wrappedCodec[A](implicit inner: Codec[A]): Codec[Wrap[A]] =
  Codec { (v, d, i) =>
    inner(v, d, i).left.map { case (addr, msg) => ("wrap" +: addr, msg) }
      .map(Wrap(_))
  }
```

For array elements use `"#N"` segments (1-based) to match the
convention of `Codec[List[T]]`.

## Optional Wrapper Codecs

If your codec wraps an inner `T` and should treat "value absent" as a
non-failure, override `optional`:

```scala
implicit def maybeCodec[A](implicit c: Codec[A]): Codec[Maybe[A]] =
  new Codec[Maybe[A]] {
    def apply(value: Value, d: Codec.Defaults, i: Int) =
      c(value, d, i).map(Maybe.some)
    override def optional: Boolean = true
  }
```

This is exactly how `Option[A]` is implemented in
`toml.derivation.auto`.

## Where to Put the Implicit

| Location | Effect |
|----------|--------|
| Companion of `T` | Auto-found by derivation, no import needed |
| `object MyCodecs` | Requires `import MyCodecs.*` at call sites |
| Local `given` / `implicit val` | Scoped to the enclosing block |

For codecs that compose with derived case-class codecs, put them on
the companion or at a place the derivation imports already cover so
the derivation summons them transparently.

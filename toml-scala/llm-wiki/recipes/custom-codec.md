---
id: recipe-custom-codec
title: "Define a Custom Codec"
category: recipe
layer: application
tags: [recipe, codec, custom, currency]
source_files:
  - /p/gh/toml-scala/core/src/main/scala/toml/Codec.scala
  - /p/gh/toml-scala/README.md
source_commit: 03d4e5f
api_surface:
  - toml.Codec.apply
related:
  - codecs/custom.md
  - codecs/built-in.md
see_also:
  - api/parse-as.md
---

# Define a Custom Codec

When the built-in codecs do not cover your domain type, write a
`Codec[T]` and bring it into implicit scope.

## Currency Example (from README)

```scala
import toml.*

case class Currency(name: String)

implicit val currencyCodec: Codec[Currency] = Codec {
  case (Value.Str(value), _, _) =>
    value match {
      case "EUR" => Right(Currency("EUR"))
      case "BTC" => Right(Currency("BTC"))
      case _     => Left((List(), s"Invalid currency: $value"))
    }

  case (value, _, _) =>
    Left((List(), s"Currency expected, $value provided"))
}

case class Root(currency: Currency)

toml.Toml.parseAs[Root]("""currency = "BTC"""")
// Right(Root(Currency("BTC")))
```

## Putting the Codec on the Companion

For a custom codec that you want available everywhere `T` is decoded
(including derived parents), put it on the companion:

```scala
final case class Email(value: String)
object Email {
  implicit val codec: toml.Codec[Email] = toml.Codec {
    case (toml.Value.Str(s), _, _) if s.contains("@") => Right(Email(s))
    case (toml.Value.Str(s), _, _) => Left((List(), s"Invalid email: $s"))
    case (v,                _, _) => Left((List(), s"Email expected, $v provided"))
  }
}
```

Then `Toml.parseAs[Profile]` where `Profile` has an `email: Email`
field will pick it up automatically — no import needed at the call
site.

## Tips

- Match on the **specific** `Value` cases you support; close with a
  catch-all that produces a `<Type> expected, <value> provided`
  message. This matches the convention of the built-in codecs and
  makes errors uniform.
- For error addresses involving children, see
  [codecs/custom](../codecs/custom.md).
- For optional wrappers (your own `Maybe`, `Optional`, etc.), see the
  "Optional Wrapper Codecs" section of
  [codecs/custom](../codecs/custom.md).

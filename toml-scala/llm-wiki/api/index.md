# API

Top-level entry points on `toml.Toml`.

| Page | Method | Returns |
|------|--------|---------|
| [parse](parse.md) | `Toml.parse(text, exts?)` | `Either[Parse.Error, Value.Tbl]` |
| [parse-as](parse-as.md) | `Toml.parseAs[T](text, exts?)` or `(tbl)` | `Either[Parse.Error, T]` (needs `DefaultParams[T]`) |
| [parse-as-value](parse-as-value.md) | `Toml.parseAsValue[T](text \| value, exts?)` | `Either[Parse.Error, T]` (no `DefaultParams` required) |
| [generate](generate.md) | `Toml.generate(root)` | `String` |

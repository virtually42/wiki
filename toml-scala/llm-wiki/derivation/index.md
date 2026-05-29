# Derivation

Automatic `Codec[T]` derivation for case classes.

| Page | Backend |
|------|---------|
| [scala-3](scala-3.md) | Shapeless 3 (`shapeless3-deriving`) + `quoted.*` macro for defaults |
| [scala-2](scala-2.md) | Shapeless 2 (`com.chuusai::shapeless`) + `Default.AsRecord` / `RecordToMap` |

Both backends share the conceptual walk described in
[../concepts/derivation-model](../concepts/derivation-model.md).

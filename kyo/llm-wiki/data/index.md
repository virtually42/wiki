# Data Types

Kyo's core data types — high-performance replacements for stdlib equivalents.

**Convention:** Always use Kyo types in Kyo code — `Maybe` not `Option`, `Result` not `Either`, `Chunk` not `List`.

| Page | Replaces | Summary |
|------|----------|---------|
| [maybe](maybe.md) | `Option` | Allocation-free optional value (opaque type) |
| [result](result.md) | `Either`/`Try` | Three-state outcome: Success, Failure, Panic |
| [chunk](chunk.md) | `List`/`Vector` | O(1) slice/take/drop immutable sequence |
| [duration](duration.md) | `scala.concurrent.duration` | Nanosecond-precision time (opaque Long) |
| [record](record.md) | — | Structural subtyping with intersection types |
| [tag](tag.md) | `ClassTag`/`TypeTag` | Runtime type information for effects |

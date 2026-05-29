# safetensors-scala

Cross-platform SafeTensors binary format reader for Scala 3.
Extracted from the palladium ML framework's
`paladium.ein.safetensors` package and elevated to a self-contained
library with no ML / autodiff dependencies.

**Status:** active — extraction completed 2026-05-29
(safetensors-scala@f3df739, palladium@0c9a7ac).

## Stack

- Language: Scala 3.8.3 (cross-publish)
- Platforms: JVM, Scala.js 1.20.1, Scala Native 0.5.12
- Build: Mill 1.1.2 (Pattern B from [[tech/guides/mill-cross-platform]],
  mirroring `/p/hg/sourceline-manager`)
- Tests: MUnit (17 tests on each platform)
- Runtime dep: `scodec-core 2.3.3` only (pinned to palladium's
  current resolution to avoid eviction)

## Code Location

`/p/hg/safetensors-scala` (initial commit f3df739, 2026-05-29).

Published locally as
`no.virtual-architect::safetensors-scala::0.1.0-SNAPSHOT` on
JVM/JS/Native via `mill safetensors.{jvm,js,native}[3.8.3].publishLocal`.

The upstream package this extracted from lives at
`/p/v42/paladium/paladium/src/paladium/ein/safetensors/` and is now a
thin adapter (`WeightsLoader.scala`) that re-exports upstream types and
wraps upstream calls into palladium's `TensorData[A]` shape.

## Pages

### Designs
- [designs/extract-from-paladium.md](designs/extract-from-paladium.md) — *accepted* — Decoupling strategy, target API surface, Mill layout, tradeoffs.

### Plans
- [plans/extract-from-paladium.md](plans/extract-from-paladium.md) — *completed* — Sequenced migration from in-tree palladium package to standalone `/p/hg` repo.

### ADRs
- [adr/0001-adopt-deps-single-file.md](adr/0001-adopt-deps-single-file.md) — Adopt [[tech/decisions/deps-single-file]] for library coordinates (via dm-generated `deps/Dependencies.mill`, since 2026-05-29 DM-002 migration); narrow platforms-only exception. **Note:** the in-tree predecessor
`/p/hg/safetensors-scala/docs/adr/0001-inline-versions.md` still describes the pre-migration inline-versions state; an optional human-owned in-tree rewrite is tracked in dm DM-008.

### Tickets
*None — extraction completed in a single session against the plan.*

### Syntheses
- [syntheses/library-extraction-via-type-alias-adapter.md](syntheses/library-extraction-via-type-alias-adapter.md) — How `type X = ns.X; val X = ns.X` + `export` + wrap-and-rebind let palladium consume the extracted library with zero caller churn. Candidate for future promotion to [[tech/patterns]] with a second worked example.

### Other
- [log.md](log.md)

## Why Extract?

- The SafeTensors format is an ML-ecosystem standard (HuggingFace) —
  useful far beyond palladium. The Scala ecosystem had no published
  reader.
- The in-palladium surface was narrow: scodec + a hand-rolled JSON
  header parser + four public methods. The only coupling to palladium
  was the `Dim`/`TensorData`/`Ein` shapes used as return types.
- Decoupling moved palladium domain types out of the reader (raw
  `(List[Int], Array[A])` returns) and pushed them into a thin
  in-palladium adapter — preserving every existing caller import
  unchanged.

## Public API (upstream)

```scala
import no.virtual_architect.safetensors.*

val bytes: Array[Byte] = java.nio.file.Files.readAllBytes(path)
val header             = SafeTensors.parseHeader(bytes)

val (shape, data) = SafeTensors.readFloat(bytes, header, "W")
// shape: List[Int], data: Array[Float]

val all: Map[String, (List[Int], Array[Double])] =
  SafeTensors.loadAllDouble(bytes)
```

Naming dimensions is the caller's responsibility — the file carries
shape (authoritative), the caller carries names.
